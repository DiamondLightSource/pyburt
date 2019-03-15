""" Request parser class which stores the information of a .req BURT file."""
from . import *
from burt.pv import PV


class ReqParser:
    """ Stores the information of a .req BURT file.

    The format of a .req file is:

        <Optional RO specifier> <PV 1>
        ...
        # File comments are preceded by a hash sign.
        <Optional RO specifier> <PV N>

    See pyburt/testables for examples.

    Attributes:
        path (str): The absolute path to a .req file.
        pvs (list): A list of PV objects representing pvs contained in a .req
            file.
    """

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The absolute path to the .req file.
        """
        self.path = path
        self.pvs = []

    def parse(self):
        """Parses the .req file located at self.path and stores the information
            in self.pvs.
        """
        with open(self.path, 'r') as f:
            for line in f:
                if skippable_line(line):
                    pass

                else:
                    line = clean_line(line)

                    line_portions = line.split()
                    if len(line_portions) > 3:
                        raise ParserException(
                            "Malformed .req file: Too many elements in line.")

                    is_readonly = line_portions[0].strip(
                    ) == burt.READONLY_SPECIFIER
                    is_readonly_notify = line_portions[0].strip(
                    ) == burt.READONLY_NOTIFY_SPECIFIER

                    save_len_index = None
                    if is_readonly or is_readonly_notify:
                        pv_name = line_portions[1]

                        if len(line_portions) == 3:
                            save_len_index = 2
                    else:
                        pv_name = line_portions[0]

                        if len(line_portions) == 2:
                            save_len_index = 1

                    save_len = None
                    if save_len_index:
                        try:
                            save_len = int(line_portions[save_len_index])
                        except ValueError:
                            raise ParserException(
                                "Malformed .req file: save length "
                                "(third tuple element) must be an "
                                "integer")

                    if save_len and save_len <= 0:
                        raise ParserException(
                            "Malformed .req file: save length "
                            "(third tuple element) must be a "
                            "positive integer")

                    pv = PV(pv_name, is_readonly=is_readonly,
                            is_readonly_notify=is_readonly_notify,
                            save_len=save_len)
                    self.pvs.append(pv)
