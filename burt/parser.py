""" Various parsers which read BURT related input/output files and encapsulates the information."""
import burt


class ReqParser:
    """ Stores the information of a .req BURT file.

    The format of a .req file is:

        <PV 1>
        ...
        # File comments are preceded by a hash sign.
        <PV N>

    Attributes:
        path (str): The absolute path to the .req file.
        pvs (list): A list of pvs contained in the .req file.
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
                if line.startswith(burt.LINE_COMMENT):
                    pass
                elif line.strip():
                    if line.startswith(burt.READONLY_SPECIFIER):
                        line = line[len(burt.READONLY_SPECIFIER):]
                    self.pvs.append(line.strip())


class SnapParser:
    """ Stores the information of a .snap BURT file

    The format of the .snap file is:

        <BURT HEADER>
        <PREFIX 1> <VALUE>
        ...
        <PREFIX N> <VALUE>
        <END BURT HEADER>
        <PV 1> <CA ARRAY LENGTH> <CA ARRAY or FLOAT>
        ...
        # File comments are preceded by a hash sign.
        <PV N> <CA ARRAY LENGTH> <CA ARRAY or FLOAT>

    Where <CA ARRAY LENGTH> is 1 if the PV readings are not represented by a CA array. See test/testables for examples.

    Attributes:
        path (str): The absolute path to the .snap file.
        pv_snapshots (dict): A dict of pvs contained in the .snap file, where a key corresponds to a pv, and the
            corresponding value is a tuple of (CA ARRAY LENGTH, [CA ARRAY or FLOAT])
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
        self.pv_snapshots = {}
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

            if (burt.HEADER_START not in file_string) or (burt.HEADER_END not in file_string):
                raise ParserException(
                    "Malformed .snap header: BURT headers missing: ")

            header, body = [part.strip() for part in file_string.split(burt.HEADER_END)]
            header_lines = header.splitlines()
            body_lines = body.splitlines()

            if header_lines[0] != burt.HEADER_START:
                raise ParserException(
                    "Malformed .snap header. Expected header start: " + burt.HEADER_START + ". Got: " +
                    header_lines[0])

            self._parse_header(header_lines[1:])
            self._parse_body(body_lines)

    def _parse_header(self, header_lines):
        """Parses the header portion of a .snap file.
        """
        for line in header_lines:
            # Ugly wart of .snap files. Directory line doesn't have a colon.
            if burt.PREFIX_DELIMITER in line:
                key, value = (part.strip() for part in line.split(burt.PREFIX_DELIMITER, 1))
            else:
                key, value = (part.strip() for part in line.split(None, 1))
            setattr(self, SnapParser._HEADER_ATTRIBUTES[key], value)

    def _parse_body(self, body_lines):
        """Parses the body portion of a .snap file.
        """
        for line in body_lines:
            if line.startswith(burt.LINE_COMMENT):
                pass

            elif line.strip():
                pv_snapshot = line.split()
                assert len(pv_snapshot) >= 3

                pv_name = pv_snapshot[0]
                ca_arr_len = pv_snapshot[1]
                ca_arr_vals = pv_snapshot[2:]
                self.pv_snapshots[pv_name] = (ca_arr_len, ca_arr_vals)


class ParserException(Exception):
    """ Raised when the parsers run into unexpected malformed formats.
    """
    pass
