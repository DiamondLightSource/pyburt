"""burt package."""

# Possible PV prefixes.
READONLY_SPECIFIER = "RO"
READONLY_NOTIFY_SPECIFIER = "RON"
WRITEONLY_SPECIFIER = "WO"

# BURT file extensions.
REQ_FILE_EXT = ".req"
SNAP_FILE_EXT = ".snap"
PYBURT_SNAP_FILE_EXT = ".pyburt.snap"
RQG_FILE_EXT = ".rqg"
RGR_FILE_EXT = ".rgr"
PYBURT_RGR_FILE_EXT = ".pyburt.rgr"
CHECK_FILE_EXT = ".check"

# Ignore PEP8 warning as imports below require globals above.
from burt.write import restore  # noqa
from burt.write import restore_group  # noqa
from burt.read import take_snapshot  # noqa
from burt.read import take_snapshot_group  # noqa
from burt.checks import check  # noqa
from burt.checks import CheckFailedException  # noqa
from burt.parsers.req import ReqParser  # noqa
from burt.parsers.snap import SnapParser  # noqa
from burt.parsers.rgr import RgrParser  # noqa
from burt.parsers.rqg import RqgParser  # noqa
from burt.parsers.check import CheckParser  # noqa
