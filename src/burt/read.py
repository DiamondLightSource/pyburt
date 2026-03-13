"""BURT snapshot python implementation.

A BURT snapshot creates a snapshot (.snap) file from a request (.req) file(s), the
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
import logging
import os
import time
from typing import Any

from cothread.catools import (
    DBR_CHAR,
    DBR_DOUBLE,
    DBR_ENUM_STR,
    DBR_FLOAT,
    DBR_LONG,
    DBR_SHORT,
    DBR_STRING,
    caget,
)

import burt
from burt.config import logconfig
from burt.parsers.snap import SnapParser as Snap
from burt.utils.file import is_req_file, is_rgr_file, is_rqg_file, is_snap_file
from burt.utils.utils import get_user_details

# Scalar pv entries are shown as a 15 width precision number(s) in scientific notation.
SNAP_PRECISION_LONG_PYFORMAT = "{:.15e}"
SNAP_PRECISION_SHORT_PYFORMAT = "{:.6e}"


class InvalidReadingException(Exception):
    """Exception used to denote an incorrect CA reading."""


def take_snapshot(
    req_files: list[str],
    snap_file: str,
    comments: str = None,
    keywords: str = None,
    compat: bool = False,
) -> list[str]:
    """Save the PVs and their state to the specified snap file, with metadata.

    If more than one .req file is given as a list or iterable, then the snapshot values
    will be appended to the given snap file one after the other.

    Args:
        req_files: An iterable of paths to (an) existing .req file(s).
        snap_file: The path to the new .snap file.
        comments: Comments to append to the BURT header.
        keywords: A delimited string of keywords to append to the Burt
            header.
        compat: Whether to ensure output is compatible with Burt

    Returns:
        A list of the PV names where something went wrong.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.

    """
    _check_snapshot_params(req_files, snap_file)

    snap_header = _gen_snap_header(req_files, comments, keywords)
    logging.debug(f"Generated .snap header: {snap_header}")

    all_req_failed_pvs: list[str] = []
    all_req_snap_footer_entries = []

    for req_file in req_files:
        req_parser = burt.ReqParser(req_file)
        _, pvs = req_parser.parse()
        logging.debug(f"Parsed PVs: {pvs}")

        # Use the special DBR_ENUM_STR datatype request, which gets the natural type
        # unless the channel is enum, in which case it gets the string value.
        ca_readings = caget([pv.name for pv in pvs], datatype=DBR_ENUM_STR, throw=False)
        singleton_req_snap_footer, singleton_req_failed_pvs = _gen_snap_footer(
            ca_readings, pvs, compat
        )

        all_req_snap_footer_entries.append(singleton_req_snap_footer)
        logging.debug(f"Generated .snap footer: {singleton_req_snap_footer}")

        all_req_failed_pvs.extend(singleton_req_failed_pvs)
        logging.debug(f"Failed PVs for {req_file}: {singleton_req_failed_pvs}")

    snap_footer = os.linesep.join(all_req_snap_footer_entries)

    _write_to_snap_file(snap_header, snap_footer, snap_file)

    return all_req_failed_pvs


def take_snapshot_group(
    rqg_file: str,
    rgr_file: str,
    comments: str = None,
    keywords: str = None,
    check: bool = True,
) -> list[str]:
    """Perform a BURT snapshot for each request file in the .rqg file.

    Args:
        rqg_file: The path to the existing .rqg file.
        rgr_file: The path to the new .rgr file.
        comments: Comments to append to the BURT header.
        keywords: A delimited string of keywords to append to the BURT
            header.
        check: Whether to inspect .check files or not.

    Returns:
        A list of the PV names where something went wrong.

    Raises:
        ValueError: If the rqg file or snap file arguments have an invalid
            extension, or if the  .rqg file does not exist.
        CheckFailedException: If a Burt check failed.

    """
    # See Git history for a partial implementation.
    # It is unclear how to decide how the all the new snap files are laid out.
    raise NotImplementedError("Not yet implemented.")


def _check_snapshot_params(req_files: list[str], snap_file: str) -> None:
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


def _check_snapshot_group_params(rgr_file, rqg_file):
    """Check take_snapshot_group parameters for validity.

    Args:
        rgr_file: The rgr file.
        rqg_file: The destination rqg file.

    """
    if not is_rqg_file(rqg_file, True):
        raise ValueError("Invalid .rqg file input.")

    if not is_rgr_file(rgr_file):
        raise ValueError("Invalid .rgr file destination.")


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
    curr_user, curr_time, directory, gid, uid = _get_snap_header_system_vals()

    # Carriage returns and newlines from user input can malform the BURT header
    # so write to the snap file as escaped symbols.
    sanitised_keywords = "" if keywords is None else _sanitise_header_line(keywords)
    sanitised_comments = "" if comments is None else _sanitise_header_line(comments)
    logging.debug(f"Keywords: {keywords}")
    logging.debug(f"Comments: {comments}")

    # Always absolute in current burt implementations.
    snap_type = Snap.TYPE_DEFAULT_VAL

    header_lines = [
        Snap.SNAP_HEADER_START,
        _gen_padded_header_line(Snap.TIME_PREFIX, curr_time),
        _gen_padded_header_line(Snap.LOGINID_PREFIX, curr_user),
        _gen_padded_header_line(Snap.UID_PREFIX, str(uid)),
        _gen_padded_header_line(Snap.GROUPID_PREFIX, str(gid)),
        _gen_padded_header_line(Snap.KEYWORDS_PREFIX, sanitised_keywords),
        _gen_padded_header_line(Snap.COMMENTS_PREFIX, sanitised_comments),
        _gen_padded_header_line(Snap.TYPE_PREFIX, snap_type),
        _gen_padded_header_line(Snap.DIRECTORY_PREFIX, directory),
    ]

    # 1 or more req files will require additional duplicate prefix entries.
    for req_file in req_files:
        # NOTE: to keep compatible with the legacy burtinter implementation, no padding
        # just for this header entry!
        header_lines.append(Snap.REQ_FILE_PREFIX + ": " + req_file)

    header_lines.append(Snap.SNAP_HEADER_END)

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

    curr_user, uid, gid = get_user_details()

    logging.debug(f"curr_user: {curr_user}")
    logging.debug(f"uid: {uid}")
    logging.debug(f"gid: {gid}")

    # Absolute path to current directory.
    directory = os.getcwd()
    logging.debug(f"Cwd: {directory}")

    return curr_user, current_time, directory, gid, uid


def _sanitise_header_line(header_text: str) -> str:
    """Clear a header line from unwanted characters.

    Args:
        header_text: The header text.

    Returns:
        str: The sanitised header text.

    """
    return header_text.replace("\r", "\\r").replace("\n", "\\n")


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


def _gen_snap_footer(ca_readings, pv_entries, compat=False):
    """Generate the .snap file BURT footer as a string.

    A snapshot of the PVs in the req file(s) is(are) performed by storing the values
    as a formatted string, which is placed in the bottom of a .snap file.

    Args:
        ca_readings (list(ca_value)): Values returned by caget()
        pv_entries (list(namedtuple(PV))): A list of PV entries in a .req file.
        compat (bool): Ensure output is compatible with Burt

    Returns:
        str: The .snap file footer.
        list(str): PVs for which getting the value failed.

    Raises:
        ValueError: If the save length is invalid.

    """
    logging.debug(f"ca_reading: {ca_readings}")
    logging.debug(f"ca_reading type: {type(ca_readings)}")

    snap_entries = []
    failed_pvs = []

    for ca_reading, pv_entry in zip(ca_readings, pv_entries):
        if ca_reading.element_count > 1 and len(ca_reading) == 0:
            logging.warning(f"Uninitialised array PV {pv_entry.name}.")
            logging.warning(
                "It will not be possible to restore this PV to its uninitialised state."
            )
        try:
            length, ca_reading_str = _ca_val_to_snap_entry(
                ca_reading, pv_entry.save_len, compat
            )
            formatted_snapshot_entry = _format_snap_footer_entry(
                length, ca_reading_str, pv_entry
            )
            snap_entries.append(formatted_snapshot_entry)
        except InvalidReadingException as e:
            logging.warning(f"Problem getting {pv_entry.name}: {e}")
            failed_pvs.append(pv_entry.name)

    return os.linesep.join(snap_entries), failed_pvs


def _ca_val_to_snap_entry(
    ca_reading: Any, requested_save_len: int, compat: bool
) -> tuple[int, str]:
    """Format a reading returned from caget into a string for a snap file.

    Cothread automatically converts a DBR channel access type into its python
    equivalent, and stores it as a type of one of ca_array, ca_str, ca_int, or ca_float.

    Args:
        ca_reading: reading from caget
        requested_save_len: requested length of array to store
        compat: Ensure behaviour is compatible with Burt

    Returns:
        int: actual saved length
        str: formatted string

    """
    save_len = 1
    # Cothread attaches a .ok and .errorcode attribute to each reading. The error
    # if present will be stored in the reading itself.
    try:
        if not ca_reading.ok:
            raise InvalidReadingException(f"Caget failure: {ca_reading.errorcode}.")
    except AttributeError as e:
        raise InvalidReadingException(f"Malformed cothread object: {e}.")

    # If a save length is specified in the .req file, this is used to shorten the
    # cothread array length to the desired value.
    if ca_reading.element_count > 1:
        save_len = _extract_save_len(ca_reading, requested_save_len)
        ca_reading_str = _flatten_ca_array(ca_reading, save_len, compat)

    else:
        ca_reading_str = _format_ca_reading(ca_reading, ca_reading.datatype)

    return save_len, ca_reading_str


def _extract_save_len(ca_reading, requested_length):
    """Check the save length if specified, truncating to the actual value if not.

    Args:
        ca_reading (any): Return value from cothread.
        requested_length (int): length specified in .req file.

    Returns:
        int: The shortest reading length.

    Raises:
        ValueError: If the save length is invalid.

    """
    actual_save_len = ca_reading.element_count

    if requested_length:
        if requested_length > ca_reading.element_count:
            raise ValueError(
                "Save length value specified in .req file exceeds length of PV data."
            )
        else:
            actual_save_len = requested_length

    return actual_save_len


def _flatten_ca_array(ca_reading, requested_length, compat):
    """Flatten the ca array into a string and obtain the save length if specified.

    NOTE: cothread returns a truncated EPICS array, so len(ca_reading) and
    ca_reading.element_count may be misaligned. Handle this by adding in the null chars
    that EPICS adds to empty array elements, to be consistent with old BURT.

    E.g.
    >> l = caget('LI-VA-VLVCC-01:SOFTWARE')
    >> l
    ca_array([4368], dtype=int16)
    >> l.element_count
    3
    >> len(l)
    1
    >> l[0]
    4368
    >> l[1]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    IndexError: index 1 is out of bounds for axis 0 with size 1

    Args:
        ca_reading (any): Return value from cothread.
        requested_length (int): length specified in .req file.
        compat: Ensure behaviour is compatible with Burt

    Returns:
        str: The flattened ca array as a string

    """
    ca_reading_str = " ".join(
        [
            _format_ca_reading(reading, ca_reading.datatype)
            for reading in ca_reading[:requested_length]
        ]
    )

    # Adding EPICS null chars if applicable.
    # Note: Burt represents empty array elements as null zeroes for integer types.
    if len(ca_reading) < ca_reading.element_count:
        # DBR_ENUM and DBR_ENUM_STR are never expected because we caget with
        # DBR_ENUM_STR as a return type request.
        if ca_reading.datatype in (DBR_SHORT, DBR_LONG, DBR_CHAR, DBR_STRING):
            empty_elem_identifier = "\\0"

        # Zero is shown in a snap file to a certain precision for floats and doubles.
        elif ca_reading.datatype == DBR_FLOAT:
            if compat:
                empty_elem_identifier = SNAP_PRECISION_SHORT_PYFORMAT.format(0)
            else:
                empty_elem_identifier = "\\0"
        elif ca_reading.datatype == DBR_DOUBLE:
            if compat:
                empty_elem_identifier = SNAP_PRECISION_LONG_PYFORMAT.format(0)
            else:
                empty_elem_identifier = "\\0"

        else:
            logging.warning(f"Unexpected type: {ca_reading.datatype}.")
            empty_elem_identifier = "\\0"

        # The old BURT appends null characters to the end of arrays in the snap file,
        # if there is a difference between the length of ca_reading (EPICS) vs the
        # actual returned values from cothread. We mimic this behaviour here.
        null_chars_padding = ca_reading_str + " " if ca_reading_str else ""
        ca_reading_str = null_chars_padding + " ".join(
            [empty_elem_identifier] * (ca_reading.element_count - len(ca_reading))
        )

    return ca_reading_str


def _format_ca_reading(ca_reading, datatype=DBR_STRING):
    """Format the cothread value depending on its type.

    Since we have used passed datatype=DBR_ENUM_STR to caget, we expect
    only 6 types to be returned:

     * DBR_DOUBLE
     * DBR_FLOAT
     * DBR_CHAR
     * DBR_SHORT
     * DBR_LONG
     * DBR_STRING (including for an enum channel)

    See http://controls.diamond.ac.uk/downloads/python/cothread/2-14/docs/html
    /catools.html#augmented

    """
    ca_reading_str = ""

    if datatype == DBR_CHAR:
        # Try to convert an ASCII code first, to handle char array case.
        try:
            ca_reading_str = chr(ca_reading)
        except (ValueError, TypeError) as e:
            logging.warning(f"Unable to convert ASCII code to str repr: {e}.")
            ca_reading_str = str(ca_reading)

    elif datatype == DBR_STRING:
        ca_reading_str = str(ca_reading)

        # Empty string case, always output a null char instead to mimic old burt.
        if not ca_reading_str:
            ca_reading_str = "\\0"

        # Enum case, whitespace e.g. "stop filling" in an enum.
        elif " " in ca_reading_str:
            ca_reading_str = f'"{ca_reading_str}"'

    elif datatype in (DBR_SHORT, DBR_LONG):
        ca_reading_str = str(int(ca_reading))

    elif datatype == DBR_FLOAT:
        ca_reading_str = SNAP_PRECISION_SHORT_PYFORMAT.format(ca_reading)

    elif datatype == DBR_DOUBLE:
        ca_reading_str = SNAP_PRECISION_LONG_PYFORMAT.format(ca_reading)

    else:
        logging.warning(f"Unexpected cothread type: {datatype}. Converting to string.")
        ca_reading_str = str(ca_reading)

    return ca_reading_str


def _format_snap_footer_entry(ca_reading_len, ca_reading_str, pv_entry):
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
        f.write(snap_header + os.linesep + snap_footer + os.linesep)


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
    cli.add_argument("-l", type=str, help="Optional backup log file location.")

    args = cli.parse_args()

    logconfig.setup_logging(log_file_path=args.l)

    if "DLS_EPICS_RELEASE" in os.environ:
        # Add graylog if running inside DLS.
        logging.getLogger().addHandler(logconfig.get_graylog_handler())

    if args.l:
        logging.getLogger().addHandler(logconfig.get_logfile_handler(args.l))

    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)

    if is_req_file(args.request_file):
        logging.info(
            "Taking snapshot: %s -> %s", args.request_file, args.snap_destination
        )
        take_snapshot(
            [args.request_file], args.snap_destination, comments=args.c, keywords=args.k
        )

    elif is_rqg_file(args.request_file):
        logging.info(
            "Taking snapshot group: %s -> %s", args.request_file, args.snap_destination
        )
        take_snapshot_group(
            args.request_file, args.snap_destination, comments=args.c, keywords=args.k
        )

    else:
        logging.critical(f"Invalid request file argument {args.request_file}.")
