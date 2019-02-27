""" Various parsers which read BURT related input/output files and encapsulates the information."""
from . import COMMENT_PREFIX, BURT_HEADER_START, BURT_HEADER_END, BURT_TIME_PREFIX, BURT_LOGINID_PREFIX, \
    BURT_UID_PREFIX, BURT_GROUPID_PREFIX, BURT_KEYWORDS_PREFIX, BURT_COMMENTS_PREFIX, BURT_TYPE_PREFIX, \
    BURT_DIRECTORY_PREFIX, BURT_REQ_FILE_PREFIX, BURT_PREFIX_DELIMITER


class ReqParser:
    """ Stores the information of a .req BURT file.

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
                if line.startswith(COMMENT_PREFIX):
                    pass
                elif line.strip():
                    self.pvs.append(line.strip())


class SnapParser:
    """ Stores the information of a .snap BURT file

    Attributes:
        path (str): The absolute path to the .snap file.
        pv_snapshots (dict): A dict of pvs contained in the .snap file, where a key corresponds to a pv, and the
            corresponding value(s) are the snapshot values of the pv.
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
            for line in f:
                if line.startswith(COMMENT_PREFIX):
                    pass
                elif line.startswith(BURT_HEADER_START):
                    pass
                elif line.startswith(BURT_HEADER_END):
                    pass
                elif line.startswith(BURT_TIME_PREFIX):
                    self.time = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_LOGINID_PREFIX):
                    self.login_id = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_UID_PREFIX):
                    self.u_id = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_GROUPID_PREFIX):
                    self.group_id = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_KEYWORDS_PREFIX):
                    self.keywords = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_COMMENTS_PREFIX):
                    self.comments = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_TYPE_PREFIX):
                    self.type = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_DIRECTORY_PREFIX):
                    self.directory = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.startswith(BURT_REQ_FILE_PREFIX):
                    self.req_file = line.split(BURT_PREFIX_DELIMITER, 1)[1].strip()
                elif line.strip():
                    pv_snapshot = line.split()
                    pv = pv_snapshot.pop(0).strip()
                    snapshot_vals = [val.strip() for val in pv_snapshot]
                    self.pv_snapshots[pv] = snapshot_vals
