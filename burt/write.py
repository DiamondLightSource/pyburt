"""BURT restore python implementation.

A BURT restore triggers a revert of the PVs specified in a .snap file to the
snapshot values that are in the .snap file. A .snap file contains some meta
data and a list of PVs with their values at the the time of the BURT
snapshot (retrieved via caget operations). Additional specifiers may also exist
which modifies the restore behaviour, such as read-only and write-only PVs.
See the BURT restore documentation for more information.

Restoring the PV values involves channel access put operations; thus the
restore operation may fail if it is run by a user with insufficient write
privileges to the target PVs.

A restore group .rgr file is just a collection of paths to .snap files,
and some .check files which verifies certain preconditions prior to the
restore operation proceeding. It is used for bulk restoring of PVs.
"""
import argparse
import logging
import sys
from collections import OrderedDict
from typing import Any, Dict, List, Union

import cothread
from cothread.catools import caput, connect
from cothread.catools import (
    DBR_CHAR,
    DBR_DOUBLE,
    DBR_ENUM,
    DBR_ENUM_STR,
    DBR_FLOAT,
    DBR_LONG,
    DBR_SHORT,
    DBR_STRING,
)

import burt
from burt.config import logconfig
from burt.parsers.snap import SnapParser
from burt.utils.file import is_check_file, is_rgr_file, is_snap_file

CaValue = Union[str, int, float, List[float]]


def restore(snap_file: str, _logger=logging.getLogger()) -> List[str]:
    """Restores the state of the PVs in the .snap file.

    This function does nothing for PVs marked with RO or RON specifiers.

    Note that cothread invokes numpy integer conversion for arrays, which must
    be handled separately; each value is converted to a floating point number,
    which is possible as array record types are only supported for DBR_CHAR,
    DBR_SHORT, DBR_LONG, DBR_FLOAT, and DBR_DOUBLE.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        snap_file (str): The path to the .snap file.
        _logger (logging.Logger): Internal logger, do not override.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does
        not exist.

    """
    if not is_snap_file(snap_file, True):
        raise ValueError(f"Invalid .snap file {snap_file}.")

    pvs = _get_pvs_in_snap(snap_file, _logger)

    # Improve performance by putting all at once later on.
    pvs_to_restore: Dict[str, Any] = OrderedDict()

    # Obtain for the channel type prior to the put for each pv, so we can put the
    # correct type.
    ca_infos = connect([pv_entry.name for pv_entry in pvs], cainfo=True, throw=False)

    pvs_to_restore = OrderedDict()

    for pv_entry, ca_info in zip(pvs, ca_infos):
        if _is_write_instr(pv_entry, _logger):
            if not ca_info.ok:
                _logger.warning(f"PV invalid, skipping: {ca_info}")
            else:
                pvs_to_restore[pv_entry.name] = _snap_entry_to_ca_type(
                    pv_entry, ca_info.datatype
                )
                _logger.debug(f"Restoring PVs: {pvs_to_restore}.")

    failed_pvs = []
    return_values = caput(pvs_to_restore.keys(), pvs_to_restore.values(), throw=False)

    for pv, return_value in zip(pvs_to_restore.keys(), return_values):
        if not return_value.ok:
            failed_pvs.append(pv)

    return failed_pvs


def restore_group(
        rgr_file: str, check: bool = True, _logger=logging.getLogger()
) -> List[str]:
    """Perform BURT restore for each .snap file contained in the .rgr file.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        rgr_file (str): The path to the .rgr file.
        check (bool): Whether to inspect .check files or not.
        _logger (logging.Logger): Internal logger, do not specify.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the rgr file has an invalid extension, or if it does
        not exist.

    """
    if not is_rgr_file(rgr_file):
        raise ValueError(f"Invalid .rgr file {rgr_file}.")

    rgr_parser = burt.RgrParser(rgr_file)
    _, body = rgr_parser.parse()
    _logger.debug(f"Parsed .snap files: {body}")

    all_failed_pvs = []
    for file_path in body:

        if check and is_check_file(file_path):
            burt.checks.check(file_path)

        elif is_snap_file(file_path):
            failed_pvs = restore(file_path)

            if failed_pvs is not cothread.catools.ca_nothing:
                all_failed_pvs.extend(failed_pvs)

    return all_failed_pvs


def main():
    """Start command-line interface."""
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "restore_file", type=str, help="The path to either a .snap or .rgr file."
    )
    cli.add_argument(
        "-v", help="Enable verbose logging (debug) level.", action="store_true"
    )
    cli.add_argument("-l", type=str, help="Optional restore log file location.")

    args = cli.parse_args()

    logconfig.setup_logging(log_file_path=args.l)

    if args.l:
        restore_logger = logging.getLogger("console_entry_with_logfile")
    else:
        restore_logger = logging.getLogger("console_entry")

    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)

    if is_snap_file(args.restore_file):
        failed_pvs = restore(args.restore_file, restore_logger)
    elif is_rgr_file(args.restore_file):
        failed_pvs = restore_group(args.restore_file, _logger=restore_logger)
    else:
        logging.critical(f"Invalid restore file argument {args.restore_file}.")
        sys.exit(1)

    if failed_pvs:
        logging.warning(f"Restore failed for the following PVs:")
        for pv in failed_pvs:
            logging.warning(pv)
        sys.exit(1)


def _is_write_instr(pv_entry: SnapParser.SNAP_PV, _logger) -> bool:
    """Check pv modifier prefix for write/no write instructions.

    Args:
        pv_entry: PV currently being checked.
        _logger: Internal logger, do not override.

    Returns:
        True if writing to PV, False if flagged otherwise.
    """
    ret = True

    if pv_entry.modifier == burt.READONLY_NOTIFY_SPECIFIER:
        # TODO: write to the no write snapshot file
        _logger.warning("RON type PVs currently unimplemented.")
        ret = False

    elif pv_entry.modifier == burt.READONLY_SPECIFIER:
        _logger.debug(f"Readonly PV {pv_entry.name}. Skipping write.")
        ret = False

    elif pv_entry.modifier == burt.WRITEONLY_SPECIFIER:
        # TODO: write the "correct" value, not the saved ones.
        _logger.warning("WO type PVs currently unimplemented.")
        ret = True

    return ret


def _get_pvs_in_snap(snap_file, _logger):
    """Parse and extract the PV entries in a snap file."""
    snap_parser = SnapParser(snap_file)
    _, body = snap_parser.parse()
    _logger.debug(f"Parsed .snap PVs: {body}")
    return body


def _snap_entry_to_ca_type(pv_entry: SnapParser.SNAP_PV, datatype: int) -> CaValue:
    """Coerce the correct ca type from the channel type."""
    # Non CA array case.
    if pv_entry.dtype_len == 1:

        if datatype in (DBR_CHAR, DBR_STRING, DBR_ENUM_STR):
            if pv_entry.vals[0] == "\\0":
                return ""
            else:
                return str(pv_entry.vals[0])

        elif datatype in (DBR_SHORT, DBR_LONG, DBR_ENUM):
            # Problematic case where the channel type is an int type, but stored value
            # is float. Python cannot convert a str float representation to an int,
            # without converting to an int first.
            try:
                return int(pv_entry.vals[0])
            except ValueError as e:
                logging.warning(
                    f"Unable to convert: {pv_entry.vals[0]}, to int type,"
                    f"given channel type: {datatype}. Converting to float value "
                    f"first: {e}."
                )
                fl_val = float(pv_entry.vals[0])
                return int(fl_val)

        elif datatype in (DBR_FLOAT, DBR_DOUBLE):
            return float(pv_entry.vals[0])

        # Fall back on older technique wth trying to convert by force.
        else:
            logging.warning(f"Unexpected channel type: {datatype}.")
            try:
                return float(pv_entry.vals[0])
            except ValueError as e:
                logging.warning(f"Unable to convert to float type: {e}.")
                return pv_entry.vals[0]

    # Arrays are always coerced as floats.
    # TODO: handle arrays of chars and other types.
    else:
        return [float(val) for val in pv_entry.vals]
