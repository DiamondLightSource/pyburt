"""BURT check file implementation.

A BURT check file specifies PV target values along with set tolerances. If a
check fails, then the BURT snapshot or restore is cancelled.

A check succeeds if |pv-value - target| < tolerance, else it fails.
"""

import logging

from cothread.catools import caget

import burt
from burt.utils.file import is_check_file


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


def check(check_file, logfile=None):
    """Check if the check file conditions are met.

    A check succeeds if |pv-value - target| < tolerance, else it fails.

    Args:
        check_file (str): The path to the .check file.
        logfile (str): The path to the log file; if empty will just use stdout.

    Raises:
        ValueError: If the check file has an invalid extension, or if it does
        not exist.

        CheckFailedException: If the check fails.

    """
    if not is_check_file(check_file, True):
        raise ValueError("Invalid .check file input.")

    if logfile:
        logging.basicConfig(filename=logfile)

    check_parser = burt.CheckParser(check_file)
    _, pvs = check_parser.parse()

    ca_readings = caget([pv.name for pv in pvs], throw=False)

    for pv, ca_reading in zip(pvs, ca_readings):
        if not ca_reading.ok:
            logging.critical(f"Check {check_file} caget failure on {pv.name}")
            raise CheckFailedException(pv, "Caget failure.")

        elif abs(ca_reading - pv.target) > pv.tolerance:
            e = CheckFailedException(pv)
            logging.debug(e)
            logging.critical(f"Check {check_file} failed on {pv.name}")

            raise e

        else:
            logging.debug(f"Check {check_file} passed on {pv.name}.")
