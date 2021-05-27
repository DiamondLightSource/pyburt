"""Various integration tests for Pyburt snapshots."""
import os

import pytest
from cothread.catools import caput

import burt
import tests.integration.softioc as ioc
from burt import SnapParser as sp
from tests import paths as core_paths
from tests.integration import paths

DOUBLE_ZERO_STR = "0.000000000000000e+00"
FLOAT_ZERO_STR = "0.000000e+00"
NULL_STR = "\\0"
NULL_CHAR = chr(0)


ioc_manager = ioc.create_ioc_manager()


def setup_function(function):
    ioc_manager.start_ioc()


def teardown_function(function):
    ioc_manager.exit_ioc()


@pytest.mark.parametrize(
    "index,null_value",
    [
        (0, NULL_STR),
        (1, DOUBLE_ZERO_STR),
        (2, FLOAT_ZERO_STR),
        (3, NULL_STR),
        (4, NULL_STR),
    ],
)
def test_snapshot_uninitialised_array_compat(index, null_value, pyburt_tmpfile):
    """Run a snapshot against uninitialised arrays."""
    burt.take_snapshot([paths.ARR_REQ], pyburt_tmpfile, compat=True)
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    _, body = snap_parser.parse()
    array_entry = body[index]
    assert all(val == null_value for val in array_entry.vals)


@pytest.mark.parametrize(
    "index,null_value",
    [(0, NULL_STR), (1, NULL_STR), (2, NULL_STR), (3, NULL_STR), (4, NULL_STR)],
)
def test_snapshot_uninitialised_array_no_compat(index, null_value, pyburt_tmpfile):
    """Run a snapshot against uninitialised arrays."""
    burt.take_snapshot([paths.ARR_REQ], pyburt_tmpfile)
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    _, body = snap_parser.parse()
    array_entry = body[index]
    assert all(val == null_value for val in array_entry.vals)


@pytest.mark.parametrize("compat", [True, False])
def test_snapshot_partial_array(pyburt_tmpfile, compat):
    """Run a snapshot against uninitialised arrays.

    Parameterising this fully proved too fiddly.

    """
    # Define the expected compatibility behaviour.
    DOUBLE_NULL = DOUBLE_ZERO_STR if compat else NULL_STR
    FLOAT_NULL = FLOAT_ZERO_STR if compat else NULL_STR

    caput(ioc.LOCAL_PV_ARR_CHAR, [1, 2, 3])
    caput(ioc.LOCAL_PV_ARR_DBL, [1.1, 2.2, 3.3])
    caput(ioc.LOCAL_PV_ARR_FLOAT, [1.1, 2.2, 3.3])
    caput(ioc.LOCAL_PV_ARR_LONG, [1, 2, 3])
    caput(ioc.LOCAL_PV_ARR_STR, ["x", "y", "z"])
    burt.take_snapshot([paths.ARR_REQ], pyburt_tmpfile, compat=compat)
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    _, body = snap_parser.parse()
    char_array_entry = body[5]
    char_expected = ["\x01", "\x02", "\x03"] + [NULL_STR] * 5
    assert char_array_entry.vals == char_expected
    double_array_entry = body[6]
    double_expected = [
        "1.100000000000000e+00",
        "2.200000000000000e+00",
        "3.300000000000000e+00",
    ] + [DOUBLE_NULL] * 5
    assert double_array_entry.vals == double_expected
    float_array_entry = body[7]
    float_expected = ["1.100000e+00", "2.200000e+00", "3.300000e+00"] + [FLOAT_NULL] * 5
    assert float_array_entry.vals == float_expected
    long_array_entry = body[8]
    long_expected = ["1", "2", "3"] + [NULL_STR] * 5
    assert long_array_entry.vals == long_expected
    str_array_entry = body[9]
    str_expected = ["x", "y", "z"] + [NULL_STR] * 5
    assert str_array_entry.vals == str_expected


@pytest.mark.xfail  # Scalar chars are not currently working correctly in Pyburt
def test_snapshot_scalar_char(pyburt_tmpfile):
    """Run a snapshot including scalar chars.

    Pyburt now records the null value as a null character, rather than the digit zero.
    """
    char = "c"
    caput(ioc.LOCAL_PV_CHAR, ord(char))

    burt.take_snapshot([paths.CHAR_REQ], pyburt_tmpfile)

    snap_parser = burt.SnapParser(pyburt_tmpfile)
    _, body = snap_parser.parse()
    char_uninit_entry = body[0]
    char_uninit_expected = NULL_CHAR
    assert char_uninit_entry.vals == [char_uninit_expected]

    char_entry = body[1]
    char_expected = char
    assert char_entry.vals == [char_expected]


def test_snapshot_with_modifiers_and_comments(pyburt_tmpfile):
    """Take a snapshot and check modifiers are applied."""
    float_value = 1.1
    double_array_values = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8]
    float_array_values = double_array_values
    short_values = [1, 2, 3, 4, 5, 6, 7, 8]

    caput(ioc.LOCAL_PV_DBL, float_value)
    caput(ioc.LOCAL_PV_ARR_DBL, double_array_values)
    caput(ioc.LOCAL_PV_ARR_FLOAT, float_array_values)
    caput(ioc.LOCAL_PV_ARR_SHORT, short_values)

    burt.take_snapshot([paths.MODIFIERS_REQ], pyburt_tmpfile)
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    _, body = snap_parser.parse()

    # Scalar value, no modifiers
    float_entry = body[0]
    assert float_entry.name == ioc.LOCAL_PV_DBL
    assert len(float_entry.vals) == 1
    assert float_entry.modifier is None

    # Double array, no modifiers
    double_array_entry = body[1]
    assert double_array_entry.name == ioc.LOCAL_PV_ARR_DBL
    assert len(double_array_entry.vals) == 8
    assert double_array_entry.modifier is None

    # Double array, length specifier of 4
    double_array_reduced = body[2]
    assert double_array_reduced.name == ioc.LOCAL_PV_ARR_DBL
    assert len(double_array_reduced.vals) == 4
    assert double_array_reduced.modifier is None

    # Float array, read-only
    float_array_ro_entry = body[3]
    assert float_array_ro_entry.name == ioc.LOCAL_PV_ARR_FLOAT
    assert len(float_array_ro_entry.vals) == 8
    assert float_array_ro_entry.modifier == "RO"

    # Short array, read-only notify, length specifier of 6
    short_array_ron_entry = body[4]
    assert short_array_ron_entry.name == ioc.LOCAL_PV_ARR_SHORT
    assert len(short_array_ron_entry.vals) == 6
    assert short_array_ron_entry.modifier == "RON"


def test_snapshot_basic(pyburt_tmpfile):
    """Take a snapshot of a basic .req file and check header and body."""
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([paths.BASIC_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 2 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert paths.BASIC_REQ == header[sp.REQ_FILE_PREFIX]

    # Scalar PV
    scalar_pv_snapshot = body[0]
    assert scalar_pv_snapshot.name == ioc.LOCAL_PV_DBL
    assert len(scalar_pv_snapshot.vals) == 1

    # Array PV
    snapshot_arr_pv = body[1]
    assert snapshot_arr_pv.name == ioc.LOCAL_PV_ARR_LONG
    assert len(snapshot_arr_pv.vals) == 8


@pytest.mark.xfail  # take_snapshot_group is not yet implemented
def test_snapshot_group_normal(pyburt_tmpfile):
    """Take a snapshot of a normal .rqg file.

    The .req files point to DLS PVS with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot_group(
        core_paths.NORMAL_RQG, pyburt_tmpfile, test_comment, test_keywords, False
    )

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 6 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]


def test_snapshot_req_file_length_bigger_than_pv(pyburt_tmpfile):
    """Save a PV with a length specified in the .req file that is too big.

    That is, the length in the .req file is bigger than the actual PV's data
    size. This is a case which would not be caught by the parser.
    """
    with pytest.raises(ValueError):
        burt.take_snapshot(
            [core_paths.MALFORMED_SAVE_LEN_TOO_LARGE_REQ], pyburt_tmpfile
        )


@pytest.mark.xfail  # The output is no longer exactly the same.
def test_header_against_burt(pyburt_tmpfile):
    """Compare vanilla BURT header against pyburt snapshots."""
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    burt.take_snapshot([paths.BASIC_REQ], pyburt_tmpfile, comment, keyword)

    snap_parser = burt.SnapParser(pyburt_tmpfile)
    header, _ = snap_parser.parse()

    params = {
        "DATETIME": header[sp.TIME_PREFIX],
        "LOGIN_ID": header[sp.LOGINID_PREFIX],
        "EFF_UID": header[sp.UID_PREFIX],
        "GRP_ID": header[sp.GROUPID_PREFIX],
        "DIRECTORY": os.path.dirname(pyburt_tmpfile),
        "REQ_FILE": paths.BASIC_REQ,
    }

    with open(pyburt_tmpfile, "r") as pyburt_out:
        with open(paths.BURT_TEMPLATED_BASIC_SNAP) as burt_out:
            pyburt_out_header = pyburt_out.read().split(sp.SNAP_HEADER_END)[0]
            burt_out_header = (
                burt_out.read().split(sp.SNAP_HEADER_END)[0].format_map(params)
            )

            assert pyburt_out_header == burt_out_header


def test_various_types_against_burt(pyburt_tmpfile):
    """Test various types against snap file generated by old burt."""
    caput(ioc.LOCAL_PV_SHORT, 4)
    caput(ioc.LOCAL_PV_ARR_SHORT, [3, 4, 13, 19])
    caput(ioc.LOCAL_PV_LONG, 9)
    caput(ioc.LOCAL_PV_ARR_LONG, [124, 623, 8392, 23, 1, -10, 14, 2])
    caput(ioc.LOCAL_PV_DBL, 5.01)
    caput(ioc.LOCAL_PV_ARR_DBL, [3.53, 9.35, 1.23, 1.0, 545.0, 800.0, 111.111, 3.0])
    caput(ioc.LOCAL_PV_FLOAT, 2.0)
    caput(ioc.LOCAL_PV_ARR_FLOAT, [3.53, 9.35, 1.23, 1.0, 545.0, 800.0, 111.111, 3.0])
    caput(ioc.LOCAL_PV_ENUM, "Warning")
    caput(ioc.LOCAL_PV_STR, "dummyString")
    caput(ioc.LOCAL_PV_ARR_STR, ["x", "y", "z", "This", "is", "a", "test", "but"])
    caput(ioc.LOCAL_PV_ARR_CHAR, [72, 101, 108, 108, 111, 32, 73, 0])
    caput(ioc.LOCAL_PV_CHAR, 98)

    burt.take_snapshot([paths.VARIOUS_TYPES_REQ], pyburt_tmpfile)

    # Read into strings to discard time dependent header.
    with open(pyburt_tmpfile, "r") as pyburt_out:
        with open(paths.BURT_VARIOUS_TYPES_SNAP, "r") as burt_out:
            pyburt_out_str = pyburt_out.read().split(sp.SNAP_HEADER_END)[1]
            burt_out_str = burt_out.read().split(sp.SNAP_HEADER_END)[1]

            assert pyburt_out_str.strip() == burt_out_str.strip()
