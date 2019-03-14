"""burt package."""

# Various symbols found in .req and .snap files.
HEADER_START = "--- Start BURT header"
HEADER_END = "--- End BURT header"
TIME_PREFIX = "Time"
LOGINID_PREFIX = "Login ID"
UID_PREFIX = "Eff  UID"  # The two spaces are intentional from the old BURT
GROUPID_PREFIX = "Group ID"
KEYWORDS_PREFIX = "Keywords"
COMMENTS_PREFIX = "Comments"
TYPE_PREFIX = "Type"
# The Type in a BURT header seems to be always this value, may need to revisit.
TYPE_DEFAULT_VAL = "Absolute"
DIRECTORY_PREFIX = "Directory"
REQ_FILE_PREFIX = "Req File"
READONLY_SPECIFIER = "RO"
READONLY_NOTIFY_SPECIFIER = "RON"
INLINE_COMMENT = "%"

# .req and .snap file extensions.
REQ_FILE_EXT = '.req'
SNAP_FILE_EXT = '.snap'

# Place after globals as imported modules below make use of globals
# defined above.
from burt.restore import restore
from burt.snap import take_snapshot
from burt.parsers.req_parser import ReqParser
from burt.parsers.snap_parser import SnapParser
