"""BURT restore python implementation.

A BURT restore triggers a revert of the PVs specified in a .snap file to the
snapshot values that are in a .snap file. This involves channel access
put operations.

A restore group .rgr file is just a collection of paths to .snap files, and
is used for bulk restore operations.
"""
import burt
import os


def restore(snap_file):
    """ Restores the state of the PVs in the .snap file, if not specified as
        read only.

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
    snap_parser.parse()

    pv_snapshots = snap_parser.pv_snapshots
    for pv in pv_snapshots:
        pv.restore_values()


def restore_group(rgr_file):
    """ Performs BURT restore for each .snap file contained in the .rgr file.

    Args:
        rgr_file (str): The path to the .rgr file.
    """
    if (not rgr_file.endswith(burt.RGR_FILE_EXT)) or (
            not os.path.isfile(rgr_file)):
        raise ValueError("Invalid .rgr file.")

    rgr_parser = burt.RgrParser(rgr_file)
    rgr_parser.parse()

    # Ignore .check files as pyburt does not need to deal with them.
    for snap_file in rgr_parser.snaps:
        restore(snap_file)
