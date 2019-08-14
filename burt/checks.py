"""BURT check file implementation.

A BURT check file specifies PV target values along with set tolerances. If a
check fails, then the BURT snapshot or restore is cancelled.

A check succeeds if |pv-value - target| < tolerance, else it fails.
"""

import logging
import os

from burt.utils.file import is_check_file
from cothread.catools import ca_nothing, caget

import burt


class CheckFailedException(Exception):
    """Raise when a check unexpectedly fails. Encapsulate failed check info."""

    def __init__(self, check_pv, msg=""):
        """Constructor.

        Args:
            check_pv: A CHECK_PV named tuple of the PV which failed the check.
            msg (str): Any other message.

        """
        super(CheckFailedException, self).__init__(
            f"{check_pv.name} failed with target {check_pv.target} and "
            f"tolerance {check_pv.tolerance}. {msg}"
        )


def check(check_file):
    """Check if the check file conditions are met.

    A check succeeds if |pv-value - target| < tolerance, else it fails.

    Args:
        check_file (str): The path to the .check file.

    Raises:
        ValueError: If the check file has an invalid extension, or if it does
        not exist.

        CheckFailedException: If the check fails.

    """
    if not is_check_file(check_file, True):
        raise ValueError("Invalid .check file input.")

    check_parser = burt.CheckParser(check_file)
    _, body = check_parser.parse()

    # Each entry is a CHECK_PV named tuple
    for pv_entry in body:
        try:
            current_pv_val = caget(pv_entry.name)

            if abs(current_pv_val - pv_entry.target) > pv_entry.tolerance:
                e = CheckFailedException(pv_entry)
                logging.debug(e)
                msg = f"Check {check_file} failed on {pv_entry.name}"
                logging.critical(msg)

                raise e
        except ca_nothing as e:
            raise CheckFailedException(pv_entry, str(e))
