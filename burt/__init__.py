"""The top-level burt package."""
from pathlib import Path

from burt.checks import CheckFailedException, check
from burt.parsers.check import CheckParser
from burt.parsers.req import ReqParser
from burt.parsers.rgr import RgrParser
from burt.parsers.rqg import RqgParser
from burt.parsers.snap import SnapParser
from burt.read import take_snapshot, take_snapshot_group
from burt.write import restore, restore_group

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


def get_version():
    version_file = Path(__file__).parent / "VERSION"
    with open(version_file) as f:
        return f.read().strip()


__version__ = get_version()
