"""BURT snapshot python implementation.

A BURT snapshot creates a snapshot (.snap) file from a request (.req) file, the
former of which contains some metadata and PVs with their saved values, and the
latter specifies the PVs to save. This operation involves some caget calls in
order to retrieve the PV values at the moment the snapshot is run.

The .req file may also contain additional specifiers to control the snapshot
and future restore behaviour, such as read-only and write-only entries,
and specifying a certain length of a PV's data to save. See the BURT snapshot
documentation for more information.

A request group .rqg file contains a collection of paths to .req files, and is
used to create bulk snapshots.
"""
import argparse
import getpass
import logging
import os
import pwd
import time

import cothread
from cothread.catools import caget

import burt
from burt.parsers.snap import SnapParser as snap
from burt.utils.file import is_check_file, is_req_file, is_rqg_file, is_snap_file


def take_snapshot(req_files, snap_file, comments=None, keywords=None):
    """Save the PVs and their state to the specified snap file, with metadata.

    If more than one .req file is given as a list or iterable, then the snapshot values
    will be appended to the given snap file one after the other.

    Args:
        req_files (iterable): An iterable of paths to (an) existing .req file(s).
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
            header.

    Returns:
        list: A list of the PV names where something went wrong.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.

    """
    _check_snapshot_params(req_files, snap_file)

    failed_pvs = []

    snap_header = _gen_snap_header(req_files, comments, keywords)
    logging.debug(f"Generated .snap header: {snap_header}")

    snap_footer_entries = []
    for req_file in req_files:
        req_parser = burt.ReqParser(req_file)
        _, pvs = req_parser.parse()
        logging.debug(f"Parsed PVs: {pvs}")

        snapshots, singleton_req_failed_pvs = _read_multi(pvs)
        failed_pvs.append(singleton_req_failed_pvs)
        logging.debug(f"Failed PVs for {req_file}: {singleton_req_failed_pvs}")

        singleton_req_snap_footer = _gen_snap_footer(snapshots)
        snap_footer_entries.append(singleton_req_snap_footer)
        logging.debug(f"Generated .snap footer: {singleton_req_snap_footer}")

    snap_footer = os.linesep.join(snap_footer_entries)

    _write_to_snap_file(snap_header, snap_footer, snap_file)

    return failed_pvs


def take_snapshot_group(rqg_file, snap_file, comments=None, keywords=None, check=True):
    """Perform a BURT snapshot for each request file in the .rqg file.

    Args:
        rqg_file (str): The path to the existing .rqg file.
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
            header.
        check (bool): Whether to inspect .check files or not.

    Raises:
        ValueError: If the rqg file or snap file arguments have an invalid
            extension, or if the  .rqg file does not exist.
        CheckFailedException: If a Burt check failed.

    """
    if not is_rqg_file(rqg_file, True):
        raise ValueError("Invalid .rqg file input.")

    if not is_snap_file(snap_file):
        raise ValueError("Invalid .snap file destination.")

    rqg_parser = burt.RqgParser(rqg_file)
    _, body = rqg_parser.parse()
    logging.debug(f"Parsed .req files: {body}")

    for file_path in body:
        logging.info(f"Processing {file_path}...")

        if check and is_check_file(file_path):
            burt.checks.check(file_path)
        elif is_req_file(file_path):
            take_snapshot(file_path, snap_file, comments, keywords)

        logging.info(f"{file_path} processed.")


def _check_snapshot_params(req_files, snap_file):
    """Check take_snapshot parameters for validity.

    Args:
        req_files: The list of req files.
        snap_file: The destination snap file.

    """
    if not is_snap_file(snap_file):
        raise ValueError("Invalid .snap file destination.")

    if not req_files:
        raise ValueError("Invalid .req file input. Empty list.")

    for req_file in req_files:
        if not is_req_file(req_file, True):
            raise ValueError(f"Invalid .req file input: {req_file}.")


def _gen_snap_header(req_files, comments, keywords):
    """Generate the .snap file BURT header as a string.

    This will precede the list of PVs in the .snap file and will contain
    some meta information such as the current time, user id, etc.

    Args:
        req_files (list): A list of req files to take a snapshot of.
        comments: Optional comments.
        keywords: Optional keywords, with an arbitrary delimiter (or none).

    Returns:
        str: The .snap file BURT header as a string.

    """
    curr_user, current_time, directory, gid, uid = _get_snap_header_system_vals()

    # Carriage returns and newlines from user input can malform the BURT header
    # so write to the snap file as escaped symbols.
    sanitised_keywords = "" if keywords is None else _sanitise_header_line(keywords)
    sanitised_comments = "" if comments is None else _sanitise_header_line(comments)
    logging.debug(f"Keywords: {keywords}")
    logging.debug(f"Comments: {comments}")

    # Always absolute in current burt implementations.
    type = snap.TYPE_DEFAULT_VAL

    header_lines = [
        snap.SNAP_HEADER_START,
        _gen_padded_header_line(snap.TIME_PREFIX, current_time),
        _gen_padded_header_line(snap.LOGINID_PREFIX, curr_user),
        _gen_padded_header_line(snap.UID_PREFIX, str(uid)),
        _gen_padded_header_line(snap.GROUPID_PREFIX, str(gid)),
        _gen_padded_header_line(snap.KEYWORDS_PREFIX, sanitised_keywords),
        _gen_padded_header_line(snap.COMMENTS_PREFIX, sanitised_comments),
        _gen_padded_header_line(snap.TYPE_PREFIX, type),
        _gen_padded_header_line(snap.DIRECTORY_PREFIX, directory),
    ]

    # 1 or more req files will require additional duplicate prefix entries.
    for req_file in req_files:
        header_lines.append(_gen_padded_header_line(snap.REQ_FILE_PREFIX, req_file))

    header_lines.append(snap.SNAP_HEADER_END)

    return os.linesep.join(header_lines)


def _get_snap_header_system_vals():
    """Obtain the required system values for the .snap header.

    Returns:
        str, str, str, int, int: The current user, current time, directory, gid,
        and uid, in the format required for the .snap header.

    """
    # DAY MMM  D hh:mm:ss YYYY format
    current_time = time.ctime()
    logging.debug(f"Current time: {current_time}")

    # Username (Lastname, Initials (Firstname)) format
    username, ugroup = getpass.getuser(), pwd.getpwuid(os.getuid())[4]
    curr_user = username + " (" + ugroup + ")"
    logging.debug(f"Current user: {username}")
    logging.debug(f"Current user group: {ugroup}")

    # Effective user and group ID.
    uid = os.getuid()
    gid = pwd.getpwnam(getpass.getuser()).pw_gid
    logging.debug(f"uid: {uid}")
    logging.debug(f"gid: {gid}")

    # Absolute path to current directory.
    directory = os.getcwd()
    logging.debug(f"Cwd: {directory}")

    return curr_user, current_time, directory, gid, uid


def _sanitise_header_line(header_text):
    """Clear a header line from unwanted characters.

    Args:
        header_text: The header text.

    Returns:
        str: The sanitised header text.

    """
    return header_text.replace("\r", "\\r").replace("\n", "\\n")


def _gen_snap_footer(snap_entries):
    """Generate the .snap file footer as a string.

    This will be the sequence of PVs followed by their reading length and
    current values. This is simply the provided entries concatenated, as the snap
    footer requires no special headers.

    Args:
        snap_entries (List): A list of snap file entries

    Returns:
        str: The .snap file footer as a string.

    """
    return os.linesep.join(snap_entries)


def _gen_padded_header_line(prefix, value):
    """Generate a header line of a .snap file with 11 space alignment padding.

    Args:
        prefix (str): The prefix in the header (e.g. Directory).
        value (str): The value to be displayed next to the prefix, after the colon.

    Returns:
        str: The padded header line.

    """
    left_padding = " " * (11 - len(":") - len(prefix))
    header_line = prefix + ":" + left_padding + str(value)

    return header_line


def _read_multi(pv_entries):
    """Take a snapshot of the PV's current state.

    A snapshot is performed by storing the values as a formatted string, which
    is placed in a .snap file.

    The .snap file PV entries require a 15 width precision number(s) in
    scientific notation.

    Args:
        pv_entries (list(namedtuple(PV))): A list of PV entries in a .req file.

    Returns:
        list(str): The .snap file entries for the PV.
        list(str): PVs for which getting the value failed.

    Raises:
        ValueError: If the save length is invalid.

    """
    ca_readings = caget(
        [pv.name for pv in pv_entries],
        datatype=cothread.catools.DBR_ENUM_STR,
        throw=False,
    )
    logging.debug(f"ca_reading: {ca_readings}")
    logging.debug(f"ca_reading type: {type(ca_readings)}")

    snap_entries = []
    failed_pvs = []

    for ca_reading, pv_entry in zip(ca_readings, pv_entries):
        ca_reading_len = 1
        ca_reading_str = ""

        if hasattr(ca_reading, "ok") and not ca_reading.ok:
            logging.critical(
                f"caget failure: {ca_reading.errorcode}" f", with error: {ca_reading}:"
            )
            failed_pvs.append(pv_entry.name)
            continue

        elif isinstance(ca_reading, cothread.dbr.ca_array):
            ca_reading_len, ca_reading_str = _flatten_ca_array_and_extract_save_len(
                ca_reading, pv_entry
            )

        # A DBR enum, e.g. "DIAD".
        elif isinstance(ca_reading, cothread.dbr.ca_str):
            ca_reading_str = str(ca_reading)

        else:
            ca_reading_str = "{:.15e}".format(ca_reading)

        snapshot_entry = _gen_snapshot_footer_entry(
            ca_reading_len, ca_reading_str, pv_entry
        )
        snap_entries.append(snapshot_entry)

    return snap_entries, failed_pvs


def _flatten_ca_array_and_extract_save_len(ca_reading, pv_entry):
    """Flatten the ca array into a string and obtain the save length if specified.

    Args:
        ca_reading (any): Return value from cothread.
        pv_entry (namedtuple(PV)): A PV entry in a .req file.

    Returns:
        int: The shortest reading length.
        str: The flattened ca array as a string

    Raises:
        ValueError: If the save length is invalid.

    """
    ca_reading_len = len(ca_reading)

    # User specified to save only save_len elements from ca_reading.
    if pv_entry.save_len:

        if pv_entry.save_len > ca_reading_len:
            raise ValueError(
                "Save length value specified in .req " "file exceeds length of PV data."
            )
        else:
            ca_reading_len = pv_entry.save_len

    # Flattening ca_array
    ca_reading_str = " ".join(
        ["{:.15e}".format(reading) for reading in ca_reading[:ca_reading_len]]
    )
    return ca_reading_len, ca_reading_str


def _gen_snapshot_footer_entry(ca_reading_len, ca_reading_str, pv_entry):
    """Generate the final snapshot entry.

    Args:
        ca_reading_len (int): The ca reading length.
        ca_reading_str (str): The ca reading value as a str.
        pv_entry (namedtuple(PV)): A PV entry in a .req file.

    Returns:
        str: The snapshot entry.

    """
    snapshot_entry = ""

    if pv_entry.modifier:
        snapshot_entry += pv_entry.modifier + " "

    snapshot_entry += f"{pv_entry.name} {ca_reading_len} {ca_reading_str}"

    return snapshot_entry


def _write_to_snap_file(snap_header, snap_footer, snap_file):
    """Write to the .snap file, making directories if necessary.

    Args:
        snap_header: The .snap file header.
        snap_footer: The .snap file footer.
        snap_file: The .snap file destination.

    Raises:
        OSError: If the new snap file path is invalid.

    """
    snap_dir = os.path.abspath(os.path.normpath(os.path.dirname(snap_file)))
    os.makedirs(snap_dir, exist_ok=True)

    with open(snap_file, "w") as f:
        f.write(snap_header + snap_footer + os.linesep)


def main():
    """Start command-line interface."""
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "request_file", type=str, help="The path to either a .req or .rqg file."
    )
    cli.add_argument(
        "snap_destination", type=str, help="The path to the destination .snap file."
    )
    cli.add_argument("-c", type=str, help="Optional snapshot comments.")
    cli.add_argument("-k", type=str, help="Optional snapshot keywords.")
    cli.add_argument(
        "-v", help="Enable verbose logging (debug) level.", action="store_true"
    )

    args = cli.parse_args()

    logging.basicConfig()
    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    if is_req_file(args.request_file):
        take_snapshot(
            args.request_file, args.snap_destination, comments=args.c, keywords=args.k
        )

    elif is_rqg_file(args.request_file):
        take_snapshot_group(
            args.request_file, args.snap_destination, comments=args.c, keywords=args.k
        )

    else:
        logging.critical("Invalid request file argument.")
