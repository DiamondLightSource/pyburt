"""Parser class which reads the information from a .rgr BURT file."""
import burt
from . import BurtParser, ParserException
from burt.parsers.snap import SnapParser


class RgrParser(BurtParser):
    """Store the information of a .rgr BURT file.

    The format of a .rgr file is:

        <RGR HEADER>
        <COMMENTS PREFIX> <VALUE>
        <END RGR HEADER>
        <.check file path 1>
        <.snap file path 1>
        ...
        <.check file path n>
        <.snap file path n>

    See the testables folder for examples.

    Attributes:
        path (str): The path to the .rgr file.

    """

    RGR_HEADER_START = "--- Start Restore Group header"
    RGR_HEADER_END = "--- End Restore Group header"

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The path to the .rgr file.

        """
        super(RgrParser, self).__init__(path)

    def get_header(self):
        """Get the .rgr file header.

        Returns:
            namedtuple(super.HEADER): The .rgr file header.

        """
        return super(RgrParser, self).HEADER(self.RGR_HEADER_START,
                                             (SnapParser.COMMENTS_PREFIX,),
                                             self.RGR_HEADER_END)

    def read_body_line(self, line):
        """Check and read a file path in the .rgr file body.

        Returns:
            str: A file path in the body.

        """
        if not line.endswith(burt.SNAP_FILE_EXT) and not line.endswith(
                burt.CHECK_FILE_EXT):
            raise ParserException("Malformed .rgr file: invalid .snap or"
                                  ".check file specified.")

        return line
