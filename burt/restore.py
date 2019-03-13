"""BURT restore implementation.

Provides methods to save from a .req file to a .snap file, and the reverse.
Uses the cothread.catools library to perform channel access operations.
"""
import burt
import os

from burt.parser import SnapParser


def restore(snap_file):
    """Restores the state of the PVs in the .snap file, if not specified as
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

    snap_parser = SnapParser(snap_file)
    snap_parser.parse()

    pv_snapshots = snap_parser.pv_snapshots
    for pv in pv_snapshots:
        pv.restore()
