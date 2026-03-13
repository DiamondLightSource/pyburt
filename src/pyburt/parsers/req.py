"""Request parser class which reads the information from a .req BURT file."""

from collections import namedtuple

from burt import consts
from burt.parsers import BurtParser, ParserException


class ReqParser(BurtParser):
    """Store the information of a .req BURT file.

    The format of a .req file is:

        <Optional prefix> <PV 1> <Optional save length>
        ...
        % File comments are preceded by a percentage sign.
        <Optional prefix> <PV N> <Optional save length>

    See the tests/resources folder for examples.

    Attributes:
        path (str): The path to the .req file.

    """

    REQ_PV = namedtuple("REQ_PV", "name save_len modifier")

    def __init__(self, path):
        """Class constructor.

        Args:
            path (str): The path to the .req file.

        """
        super().__init__(path)

    def read_body_line(self, line) -> "REQ_PV":
        """Store a PV entry in the .req file into a namedtuple object.

        Args:
            line: The line being parsed in a .req file.

        Returns:
            namedtuple(REQ_PV): A namedtuple containing the information in a
                .req body line.

        """
        pv_entry = [segment.strip() for segment in line.split()]

        if len(pv_entry) > 3:
            raise ParserException("Malformed .req file: Too many elements in line.")

        pv_name, save_len_index, modifier = ReqParser._extract_elements(pv_entry)

        save_len = ReqParser._extract_save_len(pv_entry, save_len_index)

        return self.REQ_PV(pv_name, save_len, modifier)

    @staticmethod
    def _extract_elements(pv_entry):
        """Retrieve the segments of a PV in a .req file.

        Args:
            pv_entry: The body line as a space delimited list.

        Returns:
            str, int, str: The name of the PV, the position of the save length,
                and the PV modifier, if specified.

        """
        is_modifier_specified = pv_entry[0] in (
            consts.READONLY_SPECIFIER,
            consts.READONLY_NOTIFY_SPECIFIER,
            consts.WRITEONLY_SPECIFIER,
        )

        save_len_index = None
        if is_modifier_specified:
            modifier = pv_entry[0]
            pv_name = pv_entry[1]
            if len(pv_entry) == 3:
                save_len_index = 2
        else:
            modifier = None
            pv_name = pv_entry[0]
            if len(pv_entry) == 2:
                save_len_index = 1

        return pv_name, save_len_index, modifier

    @staticmethod
    def _extract_save_len(pv_entry, save_len_index):
        """Retrieve the save length from the PV segments in a .req file.

        Args:
            pv_entry: The body line as a space delimited list.
            save_len_index: The position of the save length in the .req file,
                or None if there is no save length specified.

        Returns:
            int: The save length for the PV.

        Raises:
            ValueError: If the save length is an invalid number.
            ParserException: If the BURT file is malformed.

        """
        save_len = None

        if save_len_index:
            try:
                save_len = int(pv_entry[save_len_index])
            except ValueError:
                raise ParserException(
                    "Malformed .req file: save length (third tuple element)"
                    "must be an integer"
                )

        if save_len and save_len <= 0:
            raise ParserException(
                "Malformed .req file: save length (third tuple element) must"
                "be a positive integer"
            )

        return save_len
