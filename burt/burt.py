"""BURT module.

Provides methods to save from a .req file to a .snap file, and the reverse. Uses the cothread.catools library to perform
channel access operations.
"""
from pkg_resources import require

require('cothread')
import cothread
from cothread.catools import caget, caput
import burt
from burt import parser
import os
import errno
import time
import pwd


def _gen_burt_header(req_parser, snap_file, comments, keywords):
    """Generates the .snap file BURT header as a string. This will precede the list of PVs in the .snap file and will
    contain some meta information such as the current time, user id, etc.

    Args:
        req_parser (ReqParser): The .req file parser object which contains the PVs and other necessary information.

    Returns:
        str: The .snap file BURT header as a string.
    """
    header = ""

    curr_time = time.ctime()
    username = os.getlogin()
    uid = os.getuid()
    group_id = pwd.getpwnam(username).pw_gid
    keywords = "" if comments is None else comments
    comments = "" if keywords is None else keywords
    type = burt.TYPE_DEFAULT_VAL
    directory = os.path.dirname(snap_file)
    req_file = req_parser.path

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
        if ca_reading is cothread.dbr.ca_array:
            ca_reading_len = len(ca_reading)

        footer += "{} {} {}".format(pv, ca_reading_len, ca_reading)
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

    req_parser = parser.ReqParser(req_file)
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
        f.write(burt_header + os.linesep + snap_footer)


def restore(snap_file):
    """Restores the state of the PVs in the .snap file.

    Args:
        snap_file (str): The path to the .snap file.

    Raises:
        ValueError: If the snap file has an invalid extension, or if it does not exist.
    """
    if (not snap_file.endswith(burt.SNAP_FILE_EXT)) or (not os.path.isfile(snap_file)):
        raise ValueError("Invalid .snap file .")

    snap_parser = parser.SnapParser(snap_file)
    snap_parser.parse()

    pv_snapshots = snap_parser.pv_snapshots
    for pv in pv_snapshots:
        # Unknown purpose of ca array lengths in a .snap file.
        # ca_arr_len = pv_snapshots[pv][0]
        ca_vals = pv_snapshots[pv][1]
        caput(pv, ca_vals)
