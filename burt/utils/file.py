"""BURT file related utility functions."""
import os
import burt


def is_req_file(filename):
    """Check if a given filename refers to a .req file.

    Args:
        filename: The name of the file.

    Returns:
        True if the file is a .req file, False otherwise.

    """
    return _is_correct_ext(filename, burt.REQ_FILE_EXT)


def is_snap_file(filename):
    """Check if a given filename refers to a .snap file.

    Args:
        filename: The name of the file.

    Returns:
        True if the file is a .snap file, False otherwise.

    """
    return _is_correct_ext(filename, burt.SNAP_FILE_EXT)


def is_rqg_file(filename):
    """Check if a given filename refers to a .rqg file.

    Args:
        filename: The name of the file.

    Returns:
        True if the file is a .rqg file, False otherwise.

    """
    return _is_correct_ext(filename, burt.RQG_FILE_EXT)


def is_rgr_file(filename):
    """Check if a given filename refers to a .rgr file.

    Args:
        filename: The name of the file.

    Returns:
        True if the file is a .rgr file, False otherwise.

    """
    return _is_correct_ext(filename, burt.RGR_FILE_EXT)


def is_check_file(filename):
    """Check if a given filename refers to a .check file.

    Args:
        filename: The name of the file.

    Returns:
        True if the file is a .check file, False otherwise.

    """
    return _is_correct_ext(filename, burt.CHECK_FILE_EXT)


def _is_correct_ext(filename, correct_ext):
    """Check if a given filename has the expected file extension.

    Args:
        filename: The name of the file.
        correct_ext: The expected file extension.

    Returns:
        True if the file has the expected file extension, False otherwise.

    """
    _, parsed_ext = os.path.splitext(filename)
    return parsed_ext == correct_ext
