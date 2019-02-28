"""BURT readback script.

The script takes one or more request files (.req) and captures the values of the PVs, writing the value to a snapshot
file (.snap).

Usage:
    $ python burtrb.py -f <input .req file(s)> -o <output .snap file>

Examples:
    $ python burtrb.py -f /home/ops/burt/requestFiles/SR-DI.req -o /home/ops/burt/backupFiles/SR-DI.snap
    $ python burtrb.py -f /home/ops/burt/requestFiles/SR-DI.req -f /home/ops/burt/requestFiles/SR-DI2.req
        -o /home/ops/burt/backupFiles/SR-DI.snap
"""
from pkg_resources import require

require('cothread')
import cothread
from cothread.catools import caget
import argparse
import sys
import burt
from burt import parser
import os.path


def parse_args():
    """Parses the program arguments and checks for errors.

    Returns:
        list: The list of request files. If only one file was specified this will be a singleton list.
        str: The destination snap file.
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', action="append", dest="req_files_src", help="Specify input .req file(s).")
    arg_parser.add_argument('-o', action="store", dest="snap_file_dest", help="Specify output .snap file.")

    args = arg_parser.parse_args()

    return args.req_files_src, args.snap_file_dest


def check_args(req_files, snap_file):
    """Verifies the program arguments.

    Args:
        req_files (list): The path to the .req file(s).
        snap_file (str): The path to the .snap file.

    Raises:
        ValueError: If any of the request files or snap file arguments have an invalid extension, or if a .req file
            does not exist.
    """
    for file_path in req_files:
        if (not file_path.endswith(burt.REQ_FILE_EXT)) or (not os.path.isfile(file_path)):
            raise ValueError("Invalid .req file input.")

    if not snap_file.endswith(burt.SNAP_FILE_EXT):
        raise ValueError("Invalid .snap file destination.")


def reqs_to_snap(req_files, snap_file):
    """Saves the PVs and their state to the specified snap file, prefaced with the BURT header.

    Args:
        req_files (list): The path to the .req file(s).
        snap_file (str): The path to the .snap file.
    """
    # todo
    for req_file in req_files:
        req_parser = parser.ReqParser(req_file)
        req_parser.parse()

        pvs = req_parser.pvs
        for pv in pvs:
            ca_readings = caget(pv)

            ca_readings_len = 0
            if ca_readings is cothread.dbr.ca_array:
                ca_readings_len = len(ca_readings)
            else:
                ca_readings_len = 1

    write_burt_header(req_files, snap_file)
    write_burt_footer(req_files, snap_file)


def write_burt_header(req_files, snap_file):
    """Writes the BURT header from the .req file(s) and the user inputs.

    Args:
        req_files (list): The path to the .req file(s).
        snap_file (str): The path to the .snap file.
    """
    pass


def write_burt_footer(req_files, snap_file):
    """Writes the BURT footer from the .req file(s) and the user inputs.

    Args:
        req_files (list): The path to the .req file(s).
        snap_file (str): The path to the .snap file.
    """


def main():
    """Main function.
    """
    req_files, snap_file = parse_args()
    check_args(req_files, snap_file)
    reqs_to_snap(req_files, snap_file)


if __name__ == "__main__":
    main()
