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
from collections import OrderedDict

import cothread
from cothread.catools import caput

import burt
from burt.utils.file import is_check_file, is_rgr_file, is_snap_file


def restore(snap_file):
    """Restores the state of the PVs in the .snap file.

    This function does nothing for PVs marked with RO or RON specifiers.

    Note that cothread invokes numpy integer conversion for arrays, which must
    be handled separately; each value is converted to a floating point number,
    which is possible as array record types are only supported for DBR_CHAR,
    DBR_SHORT, DBR_LONG, DBR_FLOAT, and DBR_DOUBLE.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        snap_file (str): The path to the .snap file.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does
        not exist.

    """
    if not is_snap_file(snap_file, True):
        raise ValueError("Invalid .snap file.")

    snap_parser = burt.SnapParser(snap_file)
    _, body = snap_parser.parse()
    logging.debug(f"Parsed .snap PVs: {body}")

    # Improve performance by putting all at once later on.
    scalar_pvs_to_restore = OrderedDict()
    array_pvs_to_restore = OrderedDict()

    # TODO: caput return does not behave similarly to caget, and it looks like it
    #  returns the failed values which was being caput-ed. This needs to be changed.
    all_failed_pvs = []
    for pv_entry in body:
        if pv_entry.modifier == burt.READONLY_NOTIFY_SPECIFIER:
            # TODO: write to the no write snapshot file
            print("RON type PVs currently unimplemented.")

        elif pv_entry.modifier != burt.READONLY_SPECIFIER:

            if pv_entry.modifier == burt.WRITEONLY_SPECIFIER:
                # TODO: write the "correct" value, not the saved ones.
                print("WO type PVs currently unimplemented.")
            else:
                if 1 == pv_entry.dtype_len:
                    scalar_pvs_to_restore[pv_entry.name] = pv_entry.vals[0]
                else:
                    array_pvs_to_restore[pv_entry.name] = [
                        float(val) for val in pv_entry.vals
                    ]

    scalar_rets = caput(
        scalar_pvs_to_restore.keys(), scalar_pvs_to_restore.values(), throw=False
    )
    all_failed_pvs = scalar_rets

    array_rets = caput(
        array_pvs_to_restore.keys(), array_pvs_to_restore.values(), throw=False
    )
    if array_rets is not cothread.catools.ca_nothing:
        all_failed_pvs.extend(array_rets)

    _check_caput_rets(all_failed_pvs)

    return all_failed_pvs


def restore_group(rgr_file, check=True):
    """Perform BURT restore for each .snap file contained in the .rgr file.

    Cothread returns cothread.catools.ca_nothing upon a successful caput(s).

    Args:
        rgr_file (str): The path to the .rgr file.
        check (bool): Whether to inspect .check files or not.

    Returns:
        list(str): The list of pvs which failed to be caput-ed to.

    Raises:
        ValueError: If the rgr file has an invalid extension, or if it does
        not exist.

    """
    if not is_rgr_file(rgr_file):
        raise ValueError("Invalid .rgr file.")

    rgr_parser = burt.RgrParser(rgr_file)
    _, body = rgr_parser.parse()
    logging.debug(f"Parsed .snap files: {body}")

    # TODO: caput return does not behave similarly to caget, and it looks like it
    #  returns the failed values which was being caput-ed. This needs to be changed.
    all_failed_pvs = []
    for file_path in body:

        if check and is_check_file(file_path):
            burt.checks.check(file_path)

        elif is_snap_file(file_path):
            failed_pvs = restore(file_path)

            if failed_pvs is not cothread.catools.ca_nothing:
                all_failed_pvs.extend(failed_pvs)

    return all_failed_pvs


def _check_caput_rets(caput_rets):
    """Check caput return codes and log any errors.

    Args:
        caput_rets (list): List of augmented caput return values.

    """
    if caput_rets is not cothread.catools.ca_nothing:
        for caput_ret in caput_rets:
            if not caput_ret.ok:
                logging.critical(
                    f"caput failure: {caput_ret.errorcode}"
                    f", with error: {caput_ret}:"
                )


def main():
    """Start command-line interface."""
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "restore_file", type=str, help="The path to either a .snap or .rgr file."
    )
    cli.add_argument(
        "-v", help="Enable verbose logging (debug) level.", action="store_true"
    )

    args = cli.parse_args()

    logging.basicConfig()
    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    if is_snap_file(args.restore_file):
        restore(args.restore_file)

    elif is_rgr_file(args.restore_file):
        restore_group(args.restore_file)

    else:
        logging.critical("Invalid restore file argument.")
