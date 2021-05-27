"""Various integration tests for Pyburt restore which require a running IOC."""
import itertools
import os
import subprocess
import time
from random import randint

import numpy
import pytest
from cothread.catools import caget, caput

import burt
from tests import paths as core_paths
from tests.integration import paths
import tests.integration.softioc as ioc


NULL_CHAR = chr(0)


ioc_manager = ioc.create_ioc_manager()


def setup_function(function):
    ioc_manager.start_ioc()


def teardown_function(function):
    ioc_manager.exit_ioc()


def test_restore():
    """Runs burt restore against a .snap file with ca array and scalar pvs.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(ioc.LOCAL_PV_ARR_FLOAT, randint(1, 100))

    # CA array PV.
    burt.restore(paths.ARR_SNAP)
    ca_arr = caget(ioc.LOCAL_PV_ARR_DBL)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1

    # Scalar PV.
    burt.restore(paths.SCALAR_SNAP)
    ca_long = caget(ioc.LOCAL_PV_LONG)
    assert ca_long == 2


def test_restore_long():
    """Runs burt restore against a .snap file with a long datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(ioc.LOCAL_PV_LONG, randint(1, 100))

    # CA long PV.
    burt.restore(paths.LONG_SNAP)

    # Before fixing #34 this value would incorrectly read 1.
    new_val = caget(ioc.LOCAL_PV_LONG)
    assert new_val == 14


def test_restore_string():
    """Runs burt restore against a .snap file with a str datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(ioc.LOCAL_PV_STR, "dummyEnumStr")
    burt.restore(paths.STRING_SNAP)

    assert caget(ioc.LOCAL_PV_STR) == "DIAD"


def test_restore_enum():
    """Runs burt restore against a .snap file with an enum str datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(ioc.LOCAL_PV_ENUM, "OK")
    burt.restore(paths.ENUM_SNAP)
    # Gets the numeric value.
    assert caget(ioc.LOCAL_PV_ENUM) == 1


@pytest.mark.parametrize(
    "pv,set_value,expected",
    [
        (ioc.LOCAL_PV_ARR_CHAR, [1, 2, 3], 0),
        (ioc.LOCAL_PV_ARR_DBL, [1, 2, 3], 0),
        (ioc.LOCAL_PV_ARR_FLOAT, [1, 2, 3], 0),
        (ioc.LOCAL_PV_ARR_LONG, [1, 2, 3], 0),
        (ioc.LOCAL_PV_ARR_STR, ["1", "2", "3"], ""),
    ],
)
def test_restore_null_arrays(pv, set_value, expected):
    """Check that all nulls in a snap file are restored.

    Zeros for numeric types and empty string for string types.

    """
    # Ensure IOC start value is not zeros.
    caput(pv, set_value)
    assert not numpy.all(caget(pv) == expected)
    burt.restore(paths.NULL_ARRAY_SNAP)
    assert numpy.all(caget(pv) == expected)


@pytest.mark.parametrize(
    "pv,expected",
    [
        (ioc.LOCAL_PV_ARR_CHAR, [120, 33, 70, 32]),
        (ioc.LOCAL_PV_ARR_DBL, [-12.3, 0]),
        (ioc.LOCAL_PV_ARR_FLOAT, [0.432, -1.1]),
        (ioc.LOCAL_PV_ARR_LONG, [1, 2, 3]),
    ],
)
def test_restore_partial_numeric_arrays(pv, expected):
    """Check that partial arrays in a snap file are restored."""
    # Ensure IOC start value is not zeros.
    caput(pv, [0])
    assert not numpy.all(caget(pv) == expected)
    burt.restore(paths.PARTIAL_ARRAY_SNAP)

    val = caget(pv)
    numpy.testing.assert_allclose(val, expected)


def test_restore_partial_string_array():
    """Check that partial string arrays in a snap file are restored."""
    # Ensure IOC start value is not zeros.
    pv = ioc.LOCAL_PV_ARR_STR
    caput(pv, ["hello", "world"])
    burt.restore(paths.PARTIAL_ARRAY_SNAP)

    val = caget(pv)
    assert len(val) == 2
    assert val[0] == "three"
    assert val[1] == "blind mice"


@pytest.mark.xfail  # Restoration of null char is currently broken in Pyburt
def test_restore_scalar_char(pyburt_tmpfile):
    """Run a snapshot including scalar chars.

    Scalar chars could not be restored properly in vanilla burt. Pyburt now records the
    null value as a null character, rather than the digit zero, to prevent this.

    We specifically test with a value of 48 (the digit zero) to test this case.
    """
    char = "c"
    caput(ioc.LOCAL_PV_CHAR, ord(char))

    burt.restore(paths.CHAR_SNAP)
    ca_char_uninit = caget(ioc.LOCAL_PV_CHAR_UNINIT)
    ca_char = caget(ioc.LOCAL_PV_CHAR)
    assert ca_char_uninit == ord(NULL_CHAR)
    assert ca_char == ord("0")


def test_restore_group():
    """Runs burt restore group against a normal case.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(ioc.LOCAL_PV_ARR_FLOAT, randint(1, 100))

    burt.restore_group(core_paths.NORMAL_ALT_RGR, False)

    # CA array PV.
    ca_arr = caget(ioc.LOCAL_PV_ARR_DBL)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1


def test_various_types_restore():
    """Check that restoring for various types works properly.

    No test for a scalar short because I can't find a way of creating
    one in a soft IOC, other than an array of length one.
    """
    # Randomize IOC start values.
    caput(ioc.LOCAL_PV_FLOAT, randint(1, 100))
    caput(ioc.LOCAL_PV_ARR_FLOAT, randint(1, 100))
    caput(ioc.LOCAL_PV_LONG, randint(1, 100))
    caput(ioc.LOCAL_PV_ARR_LONG, randint(1, 100))
    caput(ioc.LOCAL_PV_DBL, randint(1, 100))
    caput(ioc.LOCAL_PV_ARR_DBL, randint(1, 100))
    caput(ioc.LOCAL_PV_STR, "dummy")
    caput(ioc.LOCAL_PV_ARR_STR, ["dummy", "rummy"])
    caput(ioc.LOCAL_PV_SHORT, randint(1, 100))
    caput(ioc.LOCAL_PV_ARR_SHORT, randint(1, 100))
    # Ignored case: See test_restore_scalar_char
    # caput(ioc.LOCAL_PV_CHAR, ord('c'))
    caput(ioc.LOCAL_PV_ARR_CHAR, "dummy")

    # Execute the restore.
    burt.restore(paths.VARIOUS_TYPES_ALT_SNAP)

    pv_float = caget(ioc.LOCAL_PV_FLOAT)
    pv_arr_float = caget(ioc.LOCAL_PV_ARR_FLOAT)
    pv_long = caget(ioc.LOCAL_PV_LONG)
    pv_arr_long = caget(ioc.LOCAL_PV_ARR_LONG)
    pv_double = caget(ioc.LOCAL_PV_DBL)
    pv_arr_double = caget(ioc.LOCAL_PV_ARR_DBL)
    pv_str = caget(ioc.LOCAL_PV_STR)
    pv_arr_str = caget(ioc.LOCAL_PV_ARR_STR)
    pv_short = caget(ioc.LOCAL_PV_SHORT)
    pv_arr_short = caget(ioc.LOCAL_PV_ARR_SHORT)
    # pv_char = caget(ioc.LOCAL_PV_CHAR)
    pv_arr_char = caget(ioc.LOCAL_PV_ARR_CHAR)

    # Note the curious format in the snap file for this PV.
    for a, b in itertools.zip_longest(pv_arr_char, "Hi Lo!"):
        print(f"{a} {b}")
        assert a == ord(b)

    assert abs(pv_float + 7.900000e01) <= 1e-05  # arbitrary
    assert abs(pv_arr_float[0] - 3.800000e-01) <= 1e-05  # arbitrary
    assert abs(pv_arr_float[1] - 3.800000e-01) <= 1e-05  # arbitrary
    assert pv_long == 200
    assert pv_arr_long[0] == 65535
    assert pv_double == -2.900000000000000e01
    assert pv_arr_double[0] == 3.003617499404633e-02
    assert pv_arr_double[1] == 3.457100664366716e-02

    # Near equality
    assert pv_str == ""
    assert pv_arr_str[0] == "dummy"
    assert pv_arr_str[1] == "rummy"
    assert pv_short == 858
    assert pv_arr_short[0] == 4368
