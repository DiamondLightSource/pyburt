"""BURT check file implementation.

A BURT check file specifies PV target values along with set tolerances. If a
check fails, then the BURT snapshot or restore is cancelled.

A check succeeds if |pv-value - target| < tolerance, else it fails.
"""
import burt
import os

from cothread.catools import caget


def check(check_file):
    """Checks if the check file conditions are met.

    A check succeeds if |pv-value - target| < tolerance, else it fails.

    Args:
        check_file (str): The path to the .check file.

    Returns:
        bool: True if the check succeeds, false otherwise.

    Raises:
        ValueError: If the check file has an invalid extension, or if it does
        not exist.

    """
    if (not check_file.endswith(burt.CHECK_FILE_EXT)) or (
            not os.path.isfile(check_file)):
        raise ValueError("Invalid .check file input.")

    check_parser = burt.CheckParser(check_file)
    _, body = check_parser.parse()

    # Each entry is a CHECK_PV named tuple
    for pv_entry in body:
        current_pv_val = caget(pv_entry.name)

        if abs(current_pv_val - pv_entry.target) > pv_entry.tolerance:
            return False

    return True
