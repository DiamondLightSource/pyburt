"""Snap parser class which reads the information from a .snap BURT file."""
from collections import namedtuple

import burt
from burt.parsers import BurtParser, ParserException


class SnapParser(BurtParser):
    """Store the information of a .snap BURT file.

    The format of the .snap file is:

        <BURT HEADER>
        <PREFIX 1> <VALUE>
        ...
        <PREFIX N> <VALUE>
        <END BURT HEADER>
        <Optional specifier> <PV 1> <DATATYPE LENGTH> <CA ARRAY or other>
        ...
        % File comments are preceded by a percent sign.
        <Optional specifier> <PV N> <DATATYPE LENGTH> <CA ARRAY or other>

    Where <DATATYPE LENGTH> is 1 if the PV readings are scalar.

    See the testables folder for examples.

    Attributes:
        path (str): The path to the .snap file.

    """

    SNAP_HEADER_START = "--- Start BURT header"
    SNAP_HEADER_END = "--- End BURT header"
    TIME_PREFIX = "Time"
    LOGINID_PREFIX = "Login ID"
    UID_PREFIX = "Eff  UID"  # The two spaces are intentional from the old BURT
    GROUPID_PREFIX = "Group ID"
    KEYWORDS_PREFIX = "Keywords"
    COMMENTS_PREFIX = "Comments"
    TYPE_PREFIX = "Type"
    # The Type in a BURT header seems to be always this value (revisit?).
    TYPE_DEFAULT_VAL = "Absolute"
    DIRECTORY_PREFIX = "Directory"
    REQ_FILE_PREFIX = "Req File"

    SNAP_PV = namedtuple("SNAP_PV", "name dtype_len vals modifier")

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The path to the .snap file.

        """
        super(SnapParser, self).__init__(path)

    def get_header(self):
        """Get the .snap file header.

        Returns:
            namedtuple(super.HEADER): The .snap file header.

        """
        return super(SnapParser, self).HEADER(
            self.SNAP_HEADER_START,
            (
                self.TIME_PREFIX,
                self.LOGINID_PREFIX,
                self.UID_PREFIX,
                self.GROUPID_PREFIX,
                self.KEYWORDS_PREFIX,
                self.COMMENTS_PREFIX,
                self.TYPE_PREFIX,
                self.DIRECTORY_PREFIX,
                self.REQ_FILE_PREFIX,
            ),
            self.SNAP_HEADER_END,
        )

    def read_body_line(self, line):
        """Store a PV in the .snap body into a namedtuple object.

        Returns:
            namedtuple(SNAP_PV): A namedtuple containing the information in a
                .snap body line.

        """
        pv_snapshot = [segment.strip() for segment in line.split()]

        if len(pv_snapshot) < 3:
            raise ParserException(
                f"Malformed .snap body {pv_snapshot}: Too few elements for a PV."
            )

        is_modifier_specified = pv_snapshot[0] in (
            burt.READONLY_SPECIFIER,
            burt.READONLY_NOTIFY_SPECIFIER,
            burt.WRITEONLY_SPECIFIER,
        )

        pv_name_index = 1 if is_modifier_specified else 0
        dtype_len_index = pv_name_index + 1
        vals_index = dtype_len_index + 1

        pv_name = pv_snapshot[pv_name_index].strip()
        vals = pv_snapshot[vals_index:]
        modifier = pv_snapshot[0] if is_modifier_specified else None

        dtype_len = pv_snapshot[dtype_len_index]
        try:
            dtype_len = int(dtype_len)
        except ValueError:
            raise ParserException(
                "Malformed .snap file: data type length is a non integer."
            )

        return self.SNAP_PV(pv_name, dtype_len, vals, modifier)
