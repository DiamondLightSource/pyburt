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
from collections import OrderedDict

import cothread
from cothread.catools import caget

import burt
from burt.parsers.snap import SnapParser as snap
from burt.utils.file import is_check_file, is_req_file, is_rqg_file, is_snap_file


def take_snapshot(req_files, snap_file, comments=None, keywords=None):
    """Save the PVs and their state to the specified snap file, with metadata.

    If more than one .req file is given as a list or iterable, then the snapshot values
    will be appended to the given snap file.

    Args:
        req_files (str or iterable): A single path/iterable of paths to (an) existing
        .req file(s).
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
            header.

    Returns:
        failed_pvs (list): A list of the PV names where something went wrong.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.

    """
    if not is_snap_file(snap_file):
        raise ValueError("Invalid .snap file destination.")

    if isinstance(req_files, str):
        _check_req_file_validity(req_files)

        failed_pvs = _snapshot_singleton_req(req_files, snap_file, comments, keywords)
    else:
        for req_file in req_files:
            _check_req_file_validity(req_file)

        failed_pvs = _snapshot_multi_req(req_files, snap_file, comments, keywords)

    return failed_pvs


def _snapshot_singleton_req(req_file, snap_file, comments=None, keywords=None):
    """Save the PV states of one .req file onto one .snap file.

    Args:
        req_file (str): A single path to (an) existing .req file(s).
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
            header.

    Returns:
        failed_pvs (list): A list of the PV names where something went wrong.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.

    """
    req_parser = burt.ReqParser(req_file)
    _, pvs = req_parser.parse()
    logging.debug(f"Parsed PVs: {pvs}")

    snap_header = _gen_snap_header(req_file, comments, keywords)
    logging.debug(f"Generated .snap header: {snap_header}")

    snapshots, failed_pvs = _read_multi(pvs)
    snap_footer = _gen_snap_footer(snapshots)
    logging.debug(f"Generated .snap footer: {snap_footer}")

    _write_to_snap_file(snap_header, snap_footer, snap_file)

    return failed_pvs


def _snapshot_multi_req(req_files, snap_file, comments=None, keywords=None):
    """Save the PV states of 2+ .req files appended onto one .snap file.

    Args:
        req_file (iterable): An iterable of paths to existing .req file(s).
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
          header.

    Returns:
        failed_pvs (list): A list of the PV names where something went wrong.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
          extension, or if the  .req file does not exist.

    """
    snap_multi_failed_pvs = []
    snap_multi_footer = ""

    # The header will be the same for all req files, except each one will add an extra
    # Req File prefix.
    snap_multi_header = _gen_snap_header(req_files[0], comments, keywords)
    logging.debug(f"Generated .snap header: {snap_multi_header}")

    first_iteration = True
    for req_file in req_files:
        req_parser = burt.ReqParser(req_file)
        _, pvs = req_parser.parse()
        logging.debug(f"Parsed PVs: {pvs}")

        if first_iteration:
            first_iteration = False
        else:
            extra_req_path_header_entry = _gen_snap_req_header_line(req_file)
            snap_multi_header += extra_req_path_header_entry + os.linesep

        snapshots, failed_pvs = _read_multi(pvs)
        snap_footer = _gen_snap_footer(snapshots)
        logging.debug(f"Generated .snap footer: {snap_footer}")
        snap_multi_footer += snap_footer + os.linesep
        snap_multi_failed_pvs.append(failed_pvs)

    logging.debug(f"Snapshot multi failed pvs: {snap_multi_failed_pvs}")
    logging.debug(f"Snapshot multi header: {snap_multi_header}")
    logging.debug(f"Snapshot multi footer: {snap_multi_footer}")

    _write_to_snap_file(snap_multi_header, snap_multi_footer, snap_file)

    return snap_multi_failed_pvs


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


def _gen_snap_header(req_path, comments, keywords):
    """Generate the .snap file BURT header as a string.

    This will precede the list of PVs in the .snap file and will contain
    some meta information such as the current time, user id, etc.

    Args:
        req_path (str): The path to the .req file.
        comments: Optional comments.
        keywords: Optional keywords, with an arbitrary delimiter (or none).

    Returns:
        str: The .snap file BURT header as a string.

    """
    # DAY MMM  D hh:mm:ss YYYY format
    current_time = time.ctime()

    # Username (Lastname, Initials (Firstname)) format
    username, ugroup = getpass.getuser(), pwd.getpwuid(os.getuid())[4]
    curr_user = username + " (" + ugroup + ")"
    uid = os.getuid()
    gid = pwd.getpwnam(getpass.getuser()).pw_gid

    # Carriage returns and newlines from user input can malform the BURT header
    # so write to the snap file as escaped symbols. This is the behaviour of
    # the old BURT.
    keywords = (
        "" if keywords is None else keywords.replace("\r", "\\r").replace("\n", "\\n")
    )
    comments = (
        "" if comments is None else comments.replace("\r", "\\r").replace("\n", "\\n")
    )

    type = snap.TYPE_DEFAULT_VAL
    directory = os.getcwd()

    req_file = req_path

    logging.debug(f"Current time: {current_time}")
    logging.debug(f"Current user: {username}")
    logging.debug(f"Current user group: {ugroup}")
    logging.debug(f"uid: {uid}")
    logging.debug(f"gid: {gid}")
    logging.debug(f"Keywords: {keywords}")
    logging.debug(f"Comments: {comments}")
    logging.debug(f"Cwd: {directory}")

    header_elements = OrderedDict(
        [
            (snap.SNAP_HEADER_START, ""),
            (snap.TIME_PREFIX, current_time),
            (snap.LOGINID_PREFIX, curr_user),
            (snap.UID_PREFIX, uid),
            (snap.GROUPID_PREFIX, gid),
            (snap.KEYWORDS_PREFIX, keywords),
            (snap.COMMENTS_PREFIX, comments),
            (snap.TYPE_PREFIX, type),
            (snap.DIRECTORY_PREFIX, directory),
            (snap.REQ_FILE_PREFIX, req_file),
            (snap.SNAP_HEADER_END, ""),
        ]
    )

    header = r""
    for prefix in header_elements:
        if (prefix == snap.SNAP_HEADER_START) or (prefix == snap.SNAP_HEADER_END):
            header += prefix + os.linesep

        # 11 space alignment from the left after the prefix for the non special
        # cases.
        else:
            header += (
                _gen_padded_header_line(prefix, header_elements[prefix]) + os.linesep
            )

    return header


def _gen_snap_footer(snap_entries):
    """Generate the .snap file footer as a string.

    This will be the sequence of PVs followed by their reading length and
    current values. This is simply the provided entries concatenated.

    Args:
        snap_entries (List): A list of snap file entries

    Returns:
        str: The .snap file footer as a string.

    """
    return os.linesep.join(snap_entries)


def _gen_padded_header_line(prefix, value):
    """Generate a header line of a .snap file with padding, given the prefix and value.

    Args:
        prefix (str): The prefix in the header (e.g. Directory).
        value (str): The value to be displayed next to the prefix, after the colon.

    Returns:
        str: The padded header line.

    """
    left_padding = " " * (11 - len(":") - len(prefix))
    header_line = prefix + ":" + left_padding + str(value)

    return header_line


def _gen_snap_req_header_line(req_path):
    """Generate a Req File .snap file header entry.

    Needed by the multi req snapshot version which requires duplicate Req File headers.

    Args:
        req_path (str): The path to the .req file.

    Returns:
        str: The generated header entry for a Req File.

    """
    return _gen_padded_header_line(snap.DIRECTORY_PREFIX, req_path)


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

        snapshot_entry = _gen_snapshot_entry(ca_reading_len, ca_reading_str, pv_entry)
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


def _gen_snapshot_entry(ca_reading_len, ca_reading_str, pv_entry):
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


def _check_req_file_validity(req_file):
    """Check if the supplied .req file is valid and exists.

    Args:
        req_file: The .req file to check.

    Raises:
        ValueError: If the request file is invalid.

    """
    if not is_req_file(req_file, True):
        raise ValueError("Invalid .req file input.")


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
