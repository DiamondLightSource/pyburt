""" Restore group parser class which stores the information of a .rgr BURT
file."""
from . import *
from burt.pv import PV


class RgrParser:
    """ Stores the information of a .rgr BURT file.

    The format of a .rgr file is:

        --- Start Restore Group header
        Comments: <Comments>
        --- End Restore Group header
        <.check file path 1>
        <.snap file path 1>
        ...
        <.check file path n>
        <.snap file path n>

    See test/testables for examples.

    Attributes:
        path (str): The absolute path to a .rgr file.
        comment (str): The comment stored in a .rgr file.
        snaps (list): A list of paths to the .snap files contained in the .rgr
            file.
        checks (list): A list of paths to the .check files contained in the
        .rgr file.
    """

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The absolute path to the .rgr file.
        """
        self.path = path
        self.comment = ""
        self.snaps = []
        self.checks = []

    def parse(self):
        """Parses the .rgr file located at self.path and stores the information
            in self.snaps and self.checks.
        """
        with open(self.path, 'r') as f:
            file_string = f.read()

            are_rgr_headers_present = \
                (burt.RGR_HEADER_END in file_string) and \
                (burt.RGR_HEADER_START in file_string)

            if not are_rgr_headers_present:
                raise ParserException(
                    "Malformed .rgr header: Missing RGR header.")

            try:
                header, body = [part.strip()
                                for part in
                                file_string.split(burt.RGR_HEADER_END)]
            except ValueError:
                raise ParserException(
                    "Malformed .rgr header: Duplicate RGR headers.")

            header_lines = header.splitlines()
            body_lines = body.splitlines()

            is_rgr_header_malformed = \
                not header_lines or \
                header_lines[0] != burt.RGR_HEADER_START or \
                len(header_lines) != 2  # Just the Comments prefix.

            if is_rgr_header_malformed:
                raise ParserException(
                    "Malformed .rgr header: Top RGR header and/or Comments "
                    "prefix is missing.")

            self._parse_header(header_lines[1])
            self._parse_body(body_lines)

    def _parse_header(self, comment_line):
        """Parses the header portion of a .rgr file.

        Args:
            comment_line (str): The comment line found in a .rgr file.
        """
        self.comment = comment_line.split(":")[1]

    def _parse_body(self, body_lines):
        """Parses the body portion of a .snap file.

        Args:
            body_lines (list): A newline delimited list of lines in a
                .rgr body.
        """
        for line in body_lines:
            if skippable_line(line):
                pass

            else:
                line = clean_line(line)

                if line.endswith(burt.SNAP_FILE_EXT):
                    self.snaps.append(line)
                elif line.endswith(burt.CHECK_FILE_EXT):
                    self.checks.append(line)
                else:
                    raise ParserException("Malformed .rgr file: invalid "
                                          ".snap or .check file "
                                          "specified.")
