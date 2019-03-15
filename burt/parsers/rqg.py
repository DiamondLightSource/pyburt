""" Request group parser class which stores the information of a .rqg BURT
file."""
from . import *
from burt.pv import PV


class RqgParser:
    """ Stores the information of a .rqg BURT file.

    The format of a .rqg file is:

        <.req file path 1>
        ...
        <.req file path n>

    See pyburt/testables for examples.

    Attributes:
        path (str): The absolute path to a .rqg file.
        reqs (list): A list of paths to the .req files contained in the .rqg
            file.
    """

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The absolute path to the .rqg file.
        """
        self.path = path
        self.reqs = []

    def parse(self):
        """Parses the .rqg file located at self.path and stores the information
            in self.reqs.
        """
        with open(self.path, 'r') as f:
            for line in f:
                if skippable_line(line):
                    pass

                else:
                    line = clean_line(line)

                    if not line.endswith(burt.REQ_FILE_EXT):
                        raise ParserException("Malformed .rqg file: invalid "
                                              ".req file specified.")

                    self.reqs.append(line)
