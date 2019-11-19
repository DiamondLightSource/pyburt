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

import cothread
from cothread.catools import caput

import burt
from burt.utils.file import is_check_file, is_rgr_file, is_snap_file
from burt.utils.logging import configure_root_logger


def restore(snap_file, logfile=None):
    """Restores the state of the PVs in the .snap file.

    This function does nothing for PVs marked with RO or RON specifiers.

    Note that cothread invokes numpy integer conversion for arrays, which must
    be handled separately; each value is converted to a floating point number,
    which is possible as array record types are only supported for DBR_CHAR,
    DBR_SHORT, DBR_LONG, DBR_FLOAT, and DBR_DOUBLE.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        snap_file (str): The path to the .snap file.
        logfile (str): The path to the log file; if empty will just use stdout.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does
        not exist.

    """
    if not is_snap_file(snap_file, True):
        raise ValueError(f"Invalid .snap file {snap_file}.")

    configure_root_logger(log_file_path=logfile)

    snap_parser = burt.SnapParser(snap_file)
    _, body = snap_parser.parse()
    logging.debug(f"Parsed .snap PVs: {body}")

    # Improve performance by putting all at once later on.
    pvs_to_restore = OrderedDict()

    for pv_entry in body:
        if pv_entry.modifier == burt.READONLY_NOTIFY_SPECIFIER:
            # TODO: write to the no write snapshot file
            logging.warning("RON type PVs currently unimplemented.")

        elif pv_entry.modifier != burt.READONLY_SPECIFIER:

            if pv_entry.modifier == burt.WRITEONLY_SPECIFIER:
                # TODO: write the "correct" value, not the saved ones.
                logging.warning("WO type PVs currently unimplemented.")
            else:
                if pv_entry.dtype_len == 1:
                    pvs_to_restore[pv_entry.name] = pv_entry.vals[0]
                else:
                    pvs_to_restore[pv_entry.name] = [
                        float(val) for val in pv_entry.vals
                    ]

    failed_pvs = []
    return_values = caput(pvs_to_restore.keys(), pvs_to_restore.values(), throw=False)
    for pv, return_value in zip(pvs_to_restore.keys(), return_values):
        if not return_value.ok:
            failed_pvs.append(pv)

    return failed_pvs


def restore_group(rgr_file, check=True, logfile=None):
    """Perform BURT restore for each .snap file contained in the .rgr file.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        rgr_file (str): The path to the .rgr file.
        check (bool): Whether to inspect .check files or not.
        logfile (str): The path to the log file; if empty will just use stdout.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the rgr file has an invalid extension, or if it does
        not exist.

    """
    if not is_rgr_file(rgr_file):
        raise ValueError(f"Invalid .rgr file {rgr_file}.")

    configure_root_logger(log_file_path=logfile)

    rgr_parser = burt.RgrParser(rgr_file)
    _, body = rgr_parser.parse()
    logging.debug(f"Parsed .snap files: {body}")

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

    configure_root_logger(log_file_path=args.l)

    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)

    if is_snap_file(args.restore_file):
        failed_pvs = restore(args.restore_file)
    elif is_rgr_file(args.restore_file):
        failed_pvs = restore_group(args.restore_file)
    else:
        logging.critical(f"Invalid restore file argument {args.restore_file}.")
        sys.exit(1)

    if failed_pvs:
        logging.warning(f"Restore failed for the following PVs:")
        for pv in failed_pvs:
            logging.warning(pv)
        sys.exit(1)
