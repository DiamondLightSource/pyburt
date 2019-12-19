"""Parser class which reads the information from a .rqg BURT file."""
from burt.utils.file import is_check_file, is_req_file
from . import BurtParser, ParserException


class RqgParser(BurtParser):
    """Store the information of a .rqg BURT file.

    The format of a .rqg file is:

        <.check file path 1>
        ...
        <.check file path n>
        <.req file path 1>
        ...
        <.req file path n>

    See the testables folder for examples.

    Attributes:
        path (str): The absolute path to a .rqg file.
        _is_req_section (bool): Flag to ensure that .check files are always before
        .req files

    """

    def __init__(self, path):
        """Class constructor.

        Args:
            path (str): The path to the .rgr file.

        """
        super(RqgParser, self).__init__(path)

        self._is_req_section = False

    def read_body_line(self, line) -> str:
        """Check and read a file path in the .rgr file body.

        Returns:
            str: A file path in the .rqg body.

        """
        if not is_req_file(line) and not is_check_file(line):
            raise ParserException(
                "Malformed .rqg file: invalid .req or .check file specified."
            )

        if self._is_req_section and is_check_file(line):
            raise ParserException(
                "Malformed .rqg file: .check files must be ordered before .req files."
            )

        if not self._is_req_section and is_req_file(line):
            self._is_req_section = True

        return line
