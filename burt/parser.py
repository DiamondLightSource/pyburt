""" Various parsers which read BURT related input/output files and encapsulates the information."""
import burt
from burt.pv import PV


class ReqParser:
    """ Stores the information of a .req BURT file.

    The format of a .req file is:

        <Optional RO specifier> <PV 1>
        ...
        # File comments are preceded by a hash sign.
        <Optional RO specifier> <PV N>

    See test/testables for examples.

    Attributes:
        path (str): The absolute path to a .req file.
        pvs (list): A list of PV objects representing pvs contained in a .req file.
    """

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The absolute path to the .req file.
        """
        self.path = path
        self.pvs = []

    def parse(self):
        """Parses the .req file located at self.path and stores the information in self.pvs.
        """
        with open(self.path, 'r') as f:
            for line in f:
                is_comment_line = line.startswith(burt.LINE_COMMENT)
                is_blank_line = not line.strip()

                if is_comment_line or is_blank_line:
                    pass

                else:
                    # Slice inline comments.
                    if burt.LINE_COMMENT in line:
                        line = line[:line.find(burt.LINE_COMMENT)]

                    is_readonly = line.strip().startswith(burt.READONLY_SPECIFIER)
                    pv_name = line.split()[1].strip() if is_readonly else line.strip()

                    pv = PV(pv_name, is_readonly=is_readonly)
                    self.pvs.append(pv)


class SnapParser:
    """ Stores the information of a .snap BURT file

    The format of the .snap file is:

        <BURT HEADER>
        <PREFIX 1> <VALUE>
        ...
        <PREFIX N> <VALUE>
        <END BURT HEADER>
        <Optional RO specifier> <PV 1> <CA ARRAY LENGTH> <CA ARRAY or FLOAT>
        ...
        # File comments are preceded by a hash sign.
        <Optional RO specifier> <PV N> <CA ARRAY LENGTH> <CA ARRAY or FLOAT>

    Where <CA ARRAY LENGTH> is 1 if the PV readings are scalar.

    See test/testables for examples.

    Attributes:
        path (str): The absolute path to a .snap file.
        pv_snapshots (list): A list of PV objects representing pvs stored in a .snap file.
        time (str): The time stored in the BURT header.
        login_id (str): The login ID stored in the BURT header.
        u_id (str): The UID stored in the BURT header.
        group_id (str): The group ID stored in the BURT header.
        keywords (str): The keyword line stored in the BURT header.
        comments (str): The comment line stored in the BURT header.
        type (str): The type stored in the BURT header.
        directory (str): The .snap file directory stored in the BURT header.
        req_file (str): The .req file to restore that is stored in the BURT header.
    """

    _HEADER_ATTRIBUTES = {
        burt.TIME_PREFIX: 'time',
        burt.LOGINID_PREFIX: 'login_id',
        burt.UID_PREFIX: 'u_id',
        burt.GROUPID_PREFIX: 'group_id',
        burt.KEYWORDS_PREFIX: 'keywords',
        burt.COMMENTS_PREFIX: 'comments',
        burt.TYPE_PREFIX: 'type',
        burt.DIRECTORY_PREFIX: 'directory',
        burt.REQ_FILE_PREFIX: 'req_file'
    }

    def __init__(self, path):
        """Constructor.

        Args:
            path (str): The absolute path to the .snap file.
        """
        self.path = path
        self.pv_snapshots = []
        self.time = ''
        self.login_id = ''
        self.u_id = ''
        self.group_id = ''
        self.keywords = ''
        self.comments = ''
        self.type = ''
        self.directory = ''
        self.req_file = ''

    def parse(self):
        """Parses the .snap file located at self.path and stores the information in class attributes.
        """
        with open(self.path, 'r') as f:
            file_string = f.read()

            is_bottom_burt_header_present = burt.HEADER_END in file_string
            if not is_bottom_burt_header_present:
                raise ParserException(
                    "Malformed .snap header: Bottom BURT header is missing.")

            header, body = [part.strip() for part in file_string.split(burt.HEADER_END)]
            header_lines = header.splitlines()
            body_lines = body.splitlines()

            is_top_burt_header_present = (header_lines[0] == burt.HEADER_START)
            if not is_top_burt_header_present:
                raise ParserException(
                    "Malformed .snap header: Top BURT header is missing.")
            header_lines = header_lines[1:]

            expected_header_line_count = len(self._HEADER_ATTRIBUTES)
            if len(header_lines) != expected_header_line_count:
                raise ParserException(
                    "Malformed .snap header: Missing prefix/value pairs in BURT header.")

            self._parse_header(header_lines)
            self._parse_body(body_lines)

    def _parse_header(self, header_lines):
        """Parses the header portion of a .snap file.
        """
        for line in header_lines:
            # Ugly wart of .snap files. Directory line doesn't have a colon.
            if burt.COLON in line:
                key, value = (part.strip() for part in line.split(burt.COLON, 1))
            else:
                key, value = (part.strip() for part in line.split(None, 1))
            setattr(self, SnapParser._HEADER_ATTRIBUTES[key], value)

    def _parse_body(self, body_lines):
        """Parses the body portion of a .snap file.
        """
        for line in body_lines:
            is_comment_line = line.startswith(burt.LINE_COMMENT)
            is_blank_line = not line.strip()

            if is_comment_line or is_blank_line:
                pass

            else:
                # Slice inline comments.
                if burt.LINE_COMMENT in line:
                    line = line[:line.find(burt.LINE_COMMENT)]

                pv_snapshot = line.strip().split()
                assert len(pv_snapshot) >= 3

                is_readonly = (pv_snapshot[0].strip() == burt.READONLY_SPECIFIER)
                pv_name_index = 1 if is_readonly else 0
                dtype_index = pv_name_index + 1
                vals_index = dtype_index + 1

                pv_name = pv_snapshot[pv_name_index].strip()
                dtype_len = pv_snapshot[dtype_index].strip()
                vals = pv_snapshot[vals_index:]

                pv = PV(pv_name, vals, is_readonly, int(dtype_len))
                self.pv_snapshots.append(pv)


class ParserException(Exception):
    """ Raised when the parsers run into unexpected malformed formats.
    """
    pass
