""" Request group parser class which reads the information from a .rqg BURT
file."""
import burt
from . import *
from overrides import overrides


class RqgParser(BurtParser):
    """ Stores the information of a .rqg BURT file.

    The format of a .rqg file is:

        <.req file path 1>
        <.check file path 1>
        ...
        <.req file path n>
        <.check file path n>

    See the testables folder for examples.

    Attributes:
        path (str): The absolute path to a .rqg file.
    """

    def __init__(self, path):
        """ Constructor.

        Args:
            path (str): The path to the .rgr file.
        """
        super(RqgParser, self).__init__(path)

    @overrides
    def read_body_line(self, line):
        if not line.endswith(burt.REQ_FILE_EXT) or not line.endswith(
                burt.CHECK_FILE_EXT):
            raise ParserException("Malformed .rgr file: invalid .req or"
                                  ".check file specified.")

        return line
