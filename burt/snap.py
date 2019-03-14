"""BURT snapshot implementation.

Reads a .req file, stores the requested PV states, and saves the values into a
.snap file.
"""
import burt
import os
import errno
import time
import pwd
import getpass

from collections import OrderedDict


def _gen_burt_header(req_parser, snap_file, comments, keywords):
    """Generates the .snap file BURT header as a string. This will precede the
    list of PVs in the .snap file and will contain some meta information
    such as the current time, user id, etc.

    Args:
        req_parser (ReqParser): The .req file parser object which contains the
        PVs and other necessary information.

    Returns:
        str: The .snap file BURT header as a string.
    """
    # DAY MMM  D hh:mm:ss YYYY format
    current_time = time.ctime()

    # Username (Lastname, Initials (Firstname)) format
    curr_user = getpass.getuser() + " (" + pwd.getpwuid(os.getuid())[4] + ")"

    uid = os.getuid()
    groupid = pwd.getpwnam(getpass.getuser()).pw_gid

    # Carriage returns and newlines malform the BURT header.
    keywords = "" if keywords is None else \
        keywords.replace('\r', '').replace('\n', '')
    comments = "" if comments is None else \
        comments.replace('\r', '').replace('\n', '')

    type = burt.TYPE_DEFAULT_VAL
    directory = os.getcwd()
    req_file = req_parser.path

    header_elements = OrderedDict([
        (burt.HEADER_START, ''),
        (burt.TIME_PREFIX, current_time),
        (burt.LOGINID_PREFIX, curr_user),
        (burt.UID_PREFIX, uid),
        (burt.GROUPID_PREFIX, groupid),
        (burt.KEYWORDS_PREFIX, keywords),
        (burt.COMMENTS_PREFIX, comments),
        (burt.TYPE_PREFIX, type),
        (burt.DIRECTORY_PREFIX, directory),
        (burt.REQ_FILE_PREFIX, req_file),
        (burt.HEADER_END, '')
    ])

    header = ""
    for prefix in header_elements:
        if (prefix == burt.HEADER_START) or (prefix == burt.HEADER_END):
            header += prefix + os.linesep

        # Special case with no colon.
        elif prefix == burt.DIRECTORY_PREFIX:
            header += "{} {}\n".format(prefix, header_elements[prefix])

        # 10 space alignment from the left after the prefix for the non special
        # cases.
        else:
            left_padding = " " * (10 - len(":") - len(prefix))
            header += prefix + ":" + left_padding + str(
                header_elements[prefix]) + os.linesep

    return header


def _gen_snap_footer(req_parser):
    """Generates the .snap file footer as a string. This will be the sequence
    of PVs followed by their reading length and current values.

    Args:
        req_parser (ReqParser): The .req file parser object which contains the
        PVs and other necessary information.

    Returns:
        str: The .snap file footer as a string.
    """
    footer = ""

    pvs = req_parser.pvs

    for pv in pvs:
        snapshot_entry = pv.gen_snapshot_entry()
        footer += snapshot_entry + os.linesep

    return footer


def take_snapshot(req_file, snap_file, comments=None, keywords=None):
    """Saves the PVs and their state to the specified snap file, prefaced with
        the BURT header.

    Args:
        req_file (str): The path to the existing .req file.
        snap_file (str): The path to the new .snap file.
        comments (str): Comments to append to the BURT header.
        keywords(str): A delimited string of keywords to append to the BURT
            header.

    Raises:
        ValueError: If the request file or snap file arguments have an invalid
            extension, or if the  .req file does not exist.
    """
    if (not req_file.endswith(burt.REQ_FILE_EXT)) or (
            not os.path.isfile(req_file)):
        raise ValueError("Invalid .req file input.")

    if not snap_file.endswith(burt.SNAP_FILE_EXT):
        raise ValueError("Invalid .snap file destination.")

    req_parser = burt.ReqParser(req_file)
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
