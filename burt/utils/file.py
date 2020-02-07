"""BURT file related utility functions."""
from os.path import isfile, splitext

import burt


def is_req_file(filename: str, check_existence: bool = False) -> bool:
    """Check if a given filename refers to a .req file.

    Args:
        filename: The name of the file.
        check_existence: If true, checks also if the file exists.

    Returns:
        True if the file is a .req file, False otherwise.

    """
    return _is_correct_ext(filename, burt.REQ_FILE_EXT, check_existence)


def is_snap_file(filename: str, check_existence: bool = False) -> bool:
    """Check if a given filename refers to a .snap file.

    Args:
        filename: The name of the file.
        check_existence: Check also if the file exists.

    Returns:
        True if the file is a .snap file, False otherwise.

    """
    return _is_correct_ext(
        filename, burt.SNAP_FILE_EXT, check_existence
    ) or _is_correct_ext(filename, burt.PYBURT_SNAP_FILE_EXT, check_existence)


def is_rqg_file(filename: str, check_existence: bool = False) -> bool:
    """Check if a given filename refers to a .rqg file.

    Args:
        filename: The name of the file.
        check_existence: If true, checks also if the file exists.

    Returns:
        True if the file is a .rqg file, False otherwise.

    """
    return _is_correct_ext(filename, burt.RQG_FILE_EXT, check_existence)


def is_rgr_file(filename: str, check_existence: bool = False) -> bool:
    """Check if a given filename refers to a .rgr file.

    Args:
        filename: The name of the file.
        check_existence: If true, checks also if the file exists.

    Returns:
        True if the file is a .rgr file, False otherwise.

    """
    return _is_correct_ext(
        filename, burt.RGR_FILE_EXT, check_existence
    ) or _is_correct_ext(filename, burt.PYBURT_RGR_FILE_EXT, check_existence)


def is_check_file(filename: str, check_existence: bool = False) -> bool:
    """Check if a given filename refers to a .check file.

    Args:
        filename: The name of the file.
        check_existence: If true, checks also if the file exists.

    Returns:
        True if the file is a .check file, False otherwise.

    """
    return _is_correct_ext(filename, burt.CHECK_FILE_EXT, check_existence)


def _is_correct_ext(
    filename: str, correct_ext: str, check_existence: bool = False
) -> bool:
    """Check if a given filename has the expected file extension.

    Args:
        filename: The name of the file.
        correct_ext: The expected file extension.
        check_existence: If true, checks also if the file exists.

    Returns:
        True if the file has the expected file extension, False otherwise.

    """
    if check_existence:
        if not isfile(filename):
            return False

    _, parsed_ext = splitext(filename)
    return parsed_ext == correct_ext
