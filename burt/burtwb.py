"""BURT writeback script.

The script takes a .snap file(s) and restores the PV values stored in them.

Usage:
    $ python burtwb.py -f <input .snap file(s)>

Examples:
    $ python burtwb.py -f /home/ops/burt/backupFiles/SR-DI.snap
    $ python burtwb.py -f /home/ops/burt/backupFiles/SR-DI.snap -f /home/ops/burt/backupFiles/SR-DI2.snap
"""
from pkg_resources import require

require('cothread')
import cothread
import burt
from cothread.catools import caput
from cothread.pv import PV_array
from burt import parser


def restore_snap_files(snap_files):
    """Restores the PVs in the .snap file to the values that are stored in the file.

    Args:
        snap_files (list): The path to the .snap files.
    """
    for snap_file in snap_files:
        snap_parser = parser.SnapParser(snap_file)
        snap_parser.parse()

        pv_snapshots = snap_parser.pv_snapshots
        for pv in pv_snapshots:
            ca_arr_len = pv_snapshots[pv][0]
            ca_vals = pv_snapshots[pv][1]
            caput(pv, ca_vals)


def main():
    """Main function.
    """
    snap_files = []
    restore_snap_files(snap_files)


if __name__ == "__main__":
    main()
