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
import errno
import getpass
import logging
import os
import pwd
import time
from collections import OrderedDict

import cothread
from cothread.catools import caget

import burt
import burt.utils.file as utils
from burt.parsers.snap import SnapParser as snap


def take_snapshot(req_file, snap_file, comments=None, keywords=None):
    """Save the PVs and their state to the specified snap file, with metadata.

    Args:
        req_file (str): The path to the existing .req file.
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords (str): A delimited string of keywords to append to the BURT
            header.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.

    """
    if (not req_file.endswith(burt.REQ_FILE_EXT)) or (not os.path.isfile(req_file)):
        raise ValueError("Invalid .req file input.")

    if not snap_file.endswith(burt.SNAP_FILE_EXT):
        raise ValueError("Invalid .snap file destination.")

    req_parser = burt.ReqParser(req_file)
    _, body = req_parser.parse()
    logging.debug(f"Parsed PVs: {body}")

    snap_header = _gen_snap_header(req_file, comments, keywords)
    logging.debug(f"Generated .snap header: {snap_header}")

    snap_footer = _gen_snap_footer(body)
    logging.debug(f"Generated .snap footer: {snap_footer}")

    _write_to_snap_file(snap_header, snap_footer, snap_file)


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

    """
    if (not rqg_file.endswith(burt.RQG_FILE_EXT)) or (not os.path.isfile(rqg_file)):
        raise ValueError("Invalid .rqg file input.")

    if not snap_file.endswith(burt.SNAP_FILE_EXT):
        raise ValueError("Invalid .snap file destination.")

    rqg_parser = burt.RqgParser(rqg_file)
    _, body = rqg_parser.parse()
    logging.debug(f"Parsed .req files: {body}")

    for file_path in body:
        if file_path.endswith(burt.CHECK_FILE_EXT) and check:
            burt.checks.check(file_path)

        elif file_path.endswith(burt.REQ_FILE_EXT):
            take_snapshot(file_path, snap_file, comments, keywords)


def _write_to_snap_file(snap_header, snap_footer, snap_file):
    """Write to the .snap file, making directories if necessary.

    Args:
        snap_header: The .snap file header.
        snap_footer: The .snap file footer.
        snap_file: The .snap file destination.

    Raises:
        OSError: If the new snap file path is invalid.

    """
    if not os.path.exists(os.path.dirname(snap_file)):
        try:
            os.makedirs(os.path.dirname(snap_file))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

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
    logging.debug(f"Current time: {current_time}")

    # Username (Lastname, Initials (Firstname)) format
    username, ugroup = getpass.getuser(), pwd.getpwuid(os.getuid())[4]
    logging.debug(f"Current user: {username}")
    logging.debug(f"Current user group: {ugroup}")
    curr_user = username + " (" + ugroup + ")"

    uid = os.getuid()
    logging.debug(f"uid: {uid}")

    gid = pwd.getpwnam(getpass.getuser()).pw_gid
    logging.debug(f"gid: {gid}")

    # Carriage returns and newlines from user input can malform the BURT header
    # so write to the snap file as escaped symbols. This is the behaviour of
    # the old BURT.
    keywords = (
        "" if keywords is None else keywords.replace("\r", "\\r").replace("\n", "\\n")
    )
    logging.debug(f"Keywords: {keywords}")

    comments = (
        "" if comments is None else comments.replace("\r", "\\r").replace("\n", "\\n")
    )
    logging.debug(f"Comments: {comments}")

    type = snap.TYPE_DEFAULT_VAL

    directory = os.getcwd()
    logging.debug(f"Cwd: {directory}")

    req_file = req_path

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

        # Special case with no colon.
        elif prefix == snap.DIRECTORY_PREFIX:
            header += f"{prefix} {header_elements[prefix]}\n"

        # 10 space alignment from the left after the prefix for the non special
        # cases.
        else:
            left_padding = " " * (10 - len(":") - len(prefix))
            header += (
                prefix + ":" + left_padding + str(header_elements[prefix]) + os.linesep
            )

    return header


def _gen_snap_footer(pvs):
    """Generate the .snap file footer as a string.

    This will be the sequence of PVs followed by their reading length and
    current values. A snapshot of the PV's current state is taken, which is performed
    by storing the values as a formatted string, which is stored in a .snap file. PV
    entries require a 15 width precision number(s) in scientific notation.

    Args:
        pvs (List): A list of PV named tuple objects.

    Returns:
        str: The .snap file footer as a string.

    """
    snapshots = _read_multi(pvs)
    return os.linesep.join(snapshots)


def _read_multi(pv_entries):
    """Take a snapshot of the PV's current state.

    A snapshot is performed by storing the values as a formatted string, which
    is placed in a .snap file.

    The .snap file PV entries require a 15 width precision number(s) in
    scientific notation.

    Args:
        pv_entries (list(namedtuple(PV))): A list of PV entries in a .req file.

    Returns:
        str: The .snap file entries for the PV.

    Raises:
        ValueError: If the save length is invalid.

    """
    ca_readings = caget(
        [pv.name for pv in pv_entries], datatype=cothread.catools.DBR_ENUM_STR
    )
    logging.debug(f"ca_reading: {ca_readings}")
    logging.debug(f"ca_reading type: {type(ca_readings)}")

    snap_entries = []

    for i in range(len(pv_entries)):
        ca_reading_len = 1
        ca_reading_str = ""

        if isinstance(ca_readings[i], cothread.dbr.ca_array):
            ca_reading_len, ca_reading_str = _flatten_ca_array_and_extract_save_len(
                ca_readings[i], pv_entries[i]
            )

        # A DBR enum, e.g. "DIAD".
        elif isinstance(ca_readings[i], cothread.dbr.ca_str):
            ca_reading_str = str(ca_readings[i])

        else:
            ca_reading_str = "{:.15e}".format(ca_readings[i])

        snapshot_entry = _gen_snapshot_entry(
            ca_reading_len, ca_reading_str, pv_entries[i]
        )
        snap_entries.append(snapshot_entry)

    return snap_entries


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

    args = cli.parse_args()

    if utils.is_req_file(args.request_file):
        take_snapshot(
            args.request_file, args.snap_destination, comments=args.c, keywords=args.k
        )

    elif utils.is_rqg_file(args.request_file):
        take_snapshot_group(
            args.request_file, args.snap_destination, comments=args.c, keywords=args.k
        )

    else:
        logging.critical("Invalid request file argument.")
