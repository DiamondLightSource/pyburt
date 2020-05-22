"""The top-level burt package."""
from pathlib import Path

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

__all__ = [
    "restore",
    "restore_group",
    "take_snapshot",
    "take_snapshot_group",
    "check",
    "CheckFailedException",
    "ReqParser",
    "SnapParser",
    "RgrParser",
    "RqgParser",
    "CheckParser",
]

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


def get_version():
    version_file = Path(__file__).parent / "VERSION"
    with open(version_file) as f:
        return f.read().strip()


__version__ = get_version()
