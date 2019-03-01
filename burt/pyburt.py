"""Main BURT module.

Provides methods to save from a .req file to a .snap file, and the reverse. Uses the cothread.catools library to perform
channel access operations.
"""
import burt
import cothread
import os
import errno
import time
import pwd
from pkg_resources import require

require('cothread')
from cothread.catools import caget, caput
from collections import OrderedDict


def _gen_burt_header(req_parser, snap_file, comments, keywords):
    """Generates the .snap file BURT header as a string. This will precede the list of PVs in the .snap file and will
    contain some meta information such as the current time, user id, etc.

    Args:
        req_parser (ReqParser): The .req file parser object which contains the PVs and other necessary information.

    Returns:
        str: The .snap file BURT header as a string.
    """
    header_elements = OrderedDict([
        (burt.HEADER_START, ''),
        (burt.TIME_PREFIX, time.ctime()),
        (burt.LOGINID_PREFIX, os.getlogin()),
        (burt.UID_PREFIX, os.getuid()),
        (burt.GROUPID_PREFIX, pwd.getpwnam(os.getlogin()).pw_gid),
        (burt.KEYWORDS_PREFIX, "" if keywords is None else keywords),
        (burt.COMMENTS_PREFIX, "" if comments is None else comments),
        (burt.TYPE_PREFIX, burt.TYPE_DEFAULT_VAL),
        (burt.DIRECTORY_PREFIX, os.path.dirname(snap_file)),
        (burt.REQ_FILE_PREFIX, req_parser.path),
        (burt.HEADER_END, '')
    ])

    header = ""
    for prefix in header_elements:
        if (prefix == burt.HEADER_START) or (prefix == burt.HEADER_END):
            header += prefix + os.linesep

        # Special case with no colon.
        elif prefix == burt.DIRECTORY_PREFIX:
            header += "{} {}\n".format(prefix, header_elements[prefix])

        # 10 space alignment from the left after the prefix.
        else:
            left_padding = " " * (10 - len(burt.PREFIX_DELIMITER) - len(prefix))
            header += prefix + burt.PREFIX_DELIMITER + left_padding + str(header_elements[prefix]) + os.linesep

    return header


def _gen_snap_footer(req_parser):
    """Generates the .snap file footer as a string. This will be the sequence of PVs followed by their reading length
    and current values.

    Args:
        req_parser (ReqParser): The .req file parser object which contains the PVs and other necessary information.

    Returns:
        str: The .snap file footer as a string.
    """
    footer = ""

    pvs = req_parser.pvs
    for pv in pvs:
        ca_reading = caget(pv)

        # caget returns either a scalar or a ca array, and the pv entry in the .snap file requires the type length.
        ca_reading_len = 1
        ca_reading_str = str(ca_reading)

        if type(ca_reading) is cothread.dbr.ca_array:
            ca_reading_len = len(ca_reading)
            # Raw string format looks like '[ 1 2 \n ... x y \n ]'
            ca_reading_str = ca_reading_str[1:len(ca_reading_str) - 1].replace('\n', ' ')

        footer += "{} {} {}".format(pv, ca_reading_len, ca_reading_str)
        footer += os.linesep

    return footer


def take_snapshot(req_file, snap_file, comments=None, keywords=None):
    """Saves the PVs and their state to the specified snap file, prefaced with the BURT header.

    Args:
        req_file (str): The path to the existing .req file.
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords(str): A delimited string of keywords to append to the BURT header.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid extension, or if the  .req file does not
        exist.
    """
    if (not req_file.endswith(burt.REQ_FILE_EXT)) or (not os.path.isfile(req_file)):
        raise ValueError("Invalid .req file input.")

    if not snap_file.endswith(burt.SNAP_FILE_EXT):
        raise ValueError("Invalid .snap file destination.")

    req_parser = burt.parser.ReqParser(req_file)
    req_parser.parse()

    burt_header = _gen_burt_header(req_parser, snap_file, comments, keywords)
    snap_footer = _gen_snap_footer(req_parser)

    if not os.path.exists(os.path.dirname(snap_file)):
        try:
            os.makedirs(os.path.dirname(snap_file))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(snap_file, "w") as f:
        f.write(burt_header + snap_footer)


def restore(snap_file):
    """Restores the state of the PVs in the .snap file.

    Args:
        snap_file (str): The path to the .snap file.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does not exist.
    """
    if (not snap_file.endswith(burt.SNAP_FILE_EXT)) or (not os.path.isfile(snap_file)):
        raise ValueError("Invalid .snap file.")

    snap_parser = burt.parser.SnapParser(snap_file)
    snap_parser.parse()

    pv_snapshots = snap_parser.pv_snapshots
    for pv in pv_snapshots:
        # Unknown purpose of ca array lengths in a .snap file.
        # ca_arr_len = pv_snapshots[pv][0]
        ca_vals = pv_snapshots[pv][1]
        caput(pv, ca_vals)
