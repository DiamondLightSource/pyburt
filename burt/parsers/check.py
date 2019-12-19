"""Check parser class which reads the information from a .check BURT file."""
from collections import namedtuple

from burt.parsers import BurtParser, ParserException


class CheckParser(BurtParser):
    """Store the information of a .check BURT file.

    The format of the .check file is:

        <BURT CHECKFILE HEADER>
        <COMMENTS PREFIX>:<VALUE>
        ...
                          <VALUE>
        <END BURT CHECKFILE HEADER>
        <PV 1> <TARGET> <OPTIONAL TOLERANCE>
        ...
        % File comments are preceded by a percent sign.
        <PV N> <TARGET> <OPTIONAL TOLERANCE>

    Where <OPTIONAL TOLERANCE> defaults to 0 if not specified, and
    abs(<PV VALUE> - <TARGET>) < <TOLERANCE> otherwise the check fails.

    See the testables folder for examples.

    Attributes:
        path (str): The path to the .check file.

    """

    CHECK_HEADER_START = "--- Start BURT checkfile header"
    CHECK_HEADER_END = "--- End BURT checkfile header"
    COMMENTS_PREFIX = "Comments"

    CHECK_PV = namedtuple("CHECK_PV", "name target tolerance")

    def __init__(self, path):
        """Class constructor.

        Args:
            path (str): The path to the .snap file.

        """
        super(CheckParser, self).__init__(path)

    def get_header(self):
        """Get the .check file header.

        Returns:
            namedtuple(super.HEADER): The .snap file header.

        """
        return super(CheckParser, self).HEADER(
            self.CHECK_HEADER_START, (self.COMMENTS_PREFIX,), self.CHECK_HEADER_END
        )

    def read_body_line(self, line) -> "CHECK_PV":
        """Store a PV in the .snap body into a namedtuple object.

        Returns:
            namedtuple(SNAP_PV): A namedtuple containing the information in a
                .snap body line.

        """
        pv_snapshot = [segment.strip() for segment in line.split()]

        if len(pv_snapshot) < 2 or len(pv_snapshot) > 3:
            raise ParserException(
                "Malformed .check body: Unexpected number of elements."
            )

        is_tolerance_specified = len(pv_snapshot) == 3

        pv_name = pv_snapshot[0].strip()
        target = pv_snapshot[1]
        tolerance = pv_snapshot[2] if is_tolerance_specified else 0

        try:
            target = float(target)
            tolerance = float(tolerance)
        except ValueError:
            raise ParserException("Malformed .check file: values must be numbers.")

        return self.CHECK_PV(pv_name, target, tolerance)
