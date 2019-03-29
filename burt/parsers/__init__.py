"""parsers package."""
from abc import ABCMeta, abstractmethod
from collections import namedtuple

# Global inline comment prefix.
INLINE_COMMENT = "%"


class BurtParser:
    """ Abstract class that reads from BURT files; the information is stored by
    the appropriate subclass(es).

    Attributes:
        path (str): The path to the .* BURT file.
    """
    __metaclass__ = ABCMeta

    HEADER = namedtuple('HEADER', 'start_label prefixes end_label')

    def __init__(self, path):
        """ Constructor.

        Args:
            path (str): The path to the .* BURT file.
        """
        self.path = path

    @abstractmethod
    def read_body_line(self, line):
        """ Stores a line in the body as a namedtuple/tuple or other object.

        Every BURT parser has a unique format for the body; this method must
        be overridden to return either a namedtuple, a normal tuple, or some
        other object which encapsulates the information in a line.

        Args:
            line(str): The line being parsed.

        Returns:
            namedtuple or tuple or other: Contains the line information.

        Raises:
            ParserException: If the BURT file is malformed.
        """
        pass

    def get_header(self):
        """ Gets the header elements, specified as a namedtuple HEADER
        object. If there is no header, this shall return an empty tuple, by
        default.

        Returns:
            namedtuple(HEADER): The start, prefix, and end entries in the
                header, or an empty tuple if there is no header (default).
        """
        return ()

    def parse(self):
        """ Parses the .* BURT file located at self.path.

        Returns:
            dict, tuple(namedtuple) or tuple(namedtuple): The contents of
            either both the header and body as a dict, and a tuple of
            namedtuple objects, respectively, or just the body, if the
            header does not exist.
        """
        with open(self.path, 'r') as f:
            file_contents = f.read()

            if self.get_header():
                header_lines, body_lines = self._extract_header_and_body(
                    file_contents)
                header_vals = self.parse_header(header_lines)
            else:
                body_lines = file_contents.splitlines()
                header_vals = {}

            body_vals = self.parse_body(body_lines)

            return header_vals, body_vals if header_vals else body_vals

    def parse_header(self, header_lines):
        """ Parses the header portion of a .* BURT file.

        Args:
            header_lines (list): A newline delimited list of lines in a .*
                BURT header.
        """
        prefix_to_val = {}
        for line in header_lines:
            # Ugly wart of .snap files: directory line doesn't have a colon.
            if ":" in line:
                key, value = (part.strip() for part in line.split(":", 1))
            else:
                key, value = (part.strip() for part in line.split(None, 1))

            if key not in self.get_header().prefixes:
                raise ParserException("Unexpected BURT header prefix.")
            else:
                prefix_to_val[key] = value

        return prefix_to_val

    def parse_body(self, body_lines):
        """ Parses the body portion of a .* BURT file.

        Args:
            body_lines (list): A newline delimited list of lines in a
                .* BURT body.

        Returns:
            list (namedtuple or tuple): Contains the child class defined
            tuple objects storing the information of the parsed body.
        """
        body_objs = []
        for line in body_lines:

            if BurtParser._skippable_line(line):
                pass
            else:
                line = BurtParser._clean_line(line)

                # Child class defined object in the body.
                body_object = self.read_body_line(line)
                body_objs.append(body_object)

        return body_objs

    def _extract_header_and_body(self, file_contents):
        """
        Helper method to get the contents from a BURT file with both a header
        and a footer.

        Args:
            file_contents (str): The contents of the BURT file as a str.

        Returns:
            str: The newline delimited lines in the BURT header.
            str: The newline delimited lines in the BURT footer.

        Raises:
            ParserException: If the BURT file is malformed.
        """
        if not (self.get_header().start_label in file_contents) and \
                (self.get_header().end_label in file_contents):
            raise ParserException("Malformed BURT header.")

        try:
            header, body = [part.strip() for part in
                            file_contents.split(
                                self.get_header().end_label)]
        except ValueError:
            raise ParserException(
                "Duplicated BURT headers.")

        header_lines = header.splitlines()[1:]
        body_lines = body.splitlines()

        if len(header_lines) != len(self.get_header().prefixes):
            raise ParserException(
                "Missing or duplicate prefixes in BURT header.")

        return header_lines, body_lines

    @staticmethod
    def _skippable_line(line):
        """ Determines if a line should be skipped.

        Args:
            line (str): The line currently being parsed.

        Returns
            bool: If the line should be skipped, or not.
        """
        is_comment_line = line.strip().startswith(INLINE_COMMENT)
        is_blank_line = not line.strip()

        return is_comment_line or is_blank_line

    @staticmethod
    def _clean_line(line):
        """ Preprocesses the line for parsing.

        Args:
            line (str): The line currently being parsed.

        Returns
            str: The cleaned line.
        """
        cleaned_line = line
        if INLINE_COMMENT in line:
            cleaned_line = line[:line.find(INLINE_COMMENT)]

        return cleaned_line.strip()


class ParserException(Exception):
    """ Raised when the parsers run into unexpected malformed formats.
    """
    pass
