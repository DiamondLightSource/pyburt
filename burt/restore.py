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
import burt
import os
from pkg_resources import require

require('cothread')

from cothread.catools import caput


def do_restore(snap_file):
    """Restores the state of the PVs in the .snap file.

    This function does nothing for PVs marked with RO or RON specifiers.

    Args:
        snap_file (str): The path to the .snap file.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does
        not exist.

    """
    if (not snap_file.endswith(burt.SNAP_FILE_EXT)) or (
            not os.path.isfile(snap_file)):
        raise ValueError("Invalid .snap file.")

    snap_parser = burt.SnapParser(snap_file)
    _, body = snap_parser.parse()

    for pv_entry in body:
        if pv_entry.modifier not in (burt.READONLY_NOTIFY_SPECIFIER,
                                     burt.READONLY_SPECIFIER):

            if pv_entry.modifier == burt.WRITEONLY_SPECIFIER:
                # TODO: write the "correct" value, not the saved ones.
                pass
            else:
                caput(pv_entry.name, pv_entry.vals)

        if pv_entry == burt.READONLY_NOTIFY_SPECIFIER:
            # TODO: write to the no write snapshot file
            pass


def do_restore_group(rgr_file):
    """Perform BURT restore for each .snap file contained in the .rgr file.

    Args:
        rgr_file (str): The path to the .rgr file.

    Raises:
        ValueError: If the rgr file has an invalid extension, or if it does
        not exist.

    """
    if (not rgr_file.endswith(burt.RGR_FILE_EXT)) or (
            not os.path.isfile(rgr_file)):
        raise ValueError("Invalid .rgr file.")

    rgr_parser = burt.RgrParser(rgr_file)
    _, body = rgr_parser.parse()

    for file_path in body:
        # Ignore .check files as pyburt does not need to deal with them.
        if file_path.endswith(burt.SNAP_FILE_EXT):
            do_restore(file_path)
