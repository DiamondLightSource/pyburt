"""Pyburt package."""

# Various symbols found in .req and .snap files.
LINE_COMMENT = '#'
HEADER_START = "--- Start BURT header"
HEADER_END = "--- End BURT header"
TIME_PREFIX = "Time"
LOGINID_PREFIX = "Login ID"
UID_PREFIX = "Eff  UID"  # The two spaces are intentional from the old BURT
GROUPID_PREFIX = "Group ID"
KEYWORDS_PREFIX = "Keywords"
COMMENTS_PREFIX = "Comments"
TYPE_PREFIX = "Type"
TYPE_DEFAULT_VAL = "Absolute"  # The Type in a BURT header seems to be always this value, may need to revisit.
DIRECTORY_PREFIX = "Directory"
REQ_FILE_PREFIX = "Req File"
PREFIX_DELIMITER = ":"
READONLY_SPECIFIER = "RO"

# .req and .snap file extensions.
REQ_FILE_EXT = '.req'
SNAP_FILE_EXT = '.snap'
