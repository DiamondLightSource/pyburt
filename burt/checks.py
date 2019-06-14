"""BURT check file implementation.

A BURT check file specifies PV target values along with set tolerances. If a
check fails, then the BURT snapshot or restore is cancelled.

A check succeeds if |pv-value - target| < tolerance, else it fails.
"""
import burt
import os

from cothread.catools import caget


class CheckFailedException(Exception):
    """Raise when a check unexpectedly fails. Encapsulate failed check info.

    Attributes:
    PV_NAME (str): The name of the failed PV.
    PV_TARGET(float): The target value.
    PV_TOLERANCE The tolerance.

    """
    PV_NAME = ""
    PV_TARGET = 0
    PV_TOLERANCE = 0

    def __init__(self, check_pv, msg=""):
        """Constructor.

        Args:
            check_pv: A CHECK_PV named tuple of the PV which failed the check.
            msg (str): Any other message.
        """
        PV_NAME = check_pv.name
        PV_TARGET = check_pv.target
        PV_TOLERANCE = check_pv.tolerance

        super(CheckFailedException, self).__init__(
            "{} failed with target {} and tolerance {}. {}".format(
                check_pv.name, check_pv.target, check_pv.tolerance, msg))


def check(check_file):
    """Checks if the check file conditions are met.

    A check succeeds if |pv-value - target| < tolerance, else it fails.

    Args:
        check_file (str): The path to the .check file.

    Raises:
        ValueError: If the check file has an invalid extension, or if it does
        not exist.

        CheckFailedException: If the check fails.

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
            raise CheckFailedException(pv_entry)
