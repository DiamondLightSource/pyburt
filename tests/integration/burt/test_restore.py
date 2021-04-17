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
from tests import paths
from tests import integration
from tests.integration.softioc import create_ioc_manager


ioc_manager = create_ioc_manager()


def setup_module(module):
    ioc_manager.start_ioc()


def teardown_module(module):
    ioc_manager.exit_ioc()


def test_restore():
    """Runs burt restore against a .snap file with ca array and scalar pvs.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_ARR_FLOAT, randint(1, 100))

    # CA array PV.
    burt.restore(integration.ARR_SNAP)
    ca_arr = caget(integration.IOC_LOCAL_PV_ARR_DBL)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1

    # Scalar PV.
    burt.restore(integration.SCALAR_SNAP)
    ca_long = caget(integration.IOC_LOCAL_PV_LONG)
    assert ca_long == 2


def test_restore_long():
    """Runs burt restore against a .snap file with a long datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_LONG, randint(1, 100))

    # CA long PV.
    burt.restore(integration.LONG_SNAP)

    # Before fixing #34 this value would incorrectly read 1.
    new_val = caget(integration.IOC_LOCAL_PV_LONG)
    assert new_val == 14


def test_restore_string():
    """Runs burt restore against a .snap file with a str datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_STR, "dummyEnumStr")
    burt.restore(integration.STRING_SNAP)

    assert caget(integration.IOC_LOCAL_PV_STR) == "DIAD"


def test_restore_enum():
    """Runs burt restore against a .snap file with an enum str datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_ENUM, "OK")
    burt.restore(integration.ENUM_SNAP)
    # Gets the numeric value.
    assert caget(integration.IOC_LOCAL_PV_ENUM) == 1


@pytest.mark.parametrize(
    "pv,set_value,expected",
    [
        (integration.IOC_LOCAL_PV_ARR_CHAR, [1, 2, 3], 0),
        (integration.IOC_LOCAL_PV_ARR_DBL, [1, 2, 3], 0),
        (integration.IOC_LOCAL_PV_ARR_FLOAT, [1, 2, 3], 0),
        (integration.IOC_LOCAL_PV_ARR_LONG, [1, 2, 3], 0),
        (integration.IOC_LOCAL_PV_ARR_STR, ["1", "2", "3"], ""),
    ],
)
def test_restore_null_arrays(pv, set_value, expected):
    """Check that all nulls in a snap file are restored.

    Zeros for numeric types and empty string for string types.

    """
    # Ensure IOC start value is not zeros.
    caput(pv, set_value)
    assert not numpy.all(caget(pv) == expected)
    burt.restore(integration.NULL_ARRAY_SNAP)
    assert numpy.all(caget(pv) == expected)


@pytest.mark.parametrize(
    "pv,expected",
    [
        (integration.IOC_LOCAL_PV_ARR_CHAR, [120, 33, 70, 32]),
        (integration.IOC_LOCAL_PV_ARR_DBL, [-12.3, 0]),
        (integration.IOC_LOCAL_PV_ARR_FLOAT, [0.432, -1.1]),
        (integration.IOC_LOCAL_PV_ARR_LONG, [1, 2, 3]),
    ],
)
def test_restore_partial_numeric_arrays(pv, expected):
    """Check that partial arrays in a snap file are restored."""
    # Ensure IOC start value is not zeros.
    caput(pv, [0])
    assert not numpy.all(caget(pv) == expected)
    burt.restore(integration.PARTIAL_ARRAY_SNAP)

    val = caget(pv)
    numpy.testing.assert_allclose(val, expected)


def test_restore_partial_string_array():
    """Check that partial string arrays in a snap file are restored."""
    # Ensure IOC start value is not zeros.
    pv = integration.IOC_LOCAL_PV_ARR_STR
    caput(pv, ["hello", "world"])
    burt.restore(integration.PARTIAL_ARRAY_SNAP)

    val = caget(pv)
    assert len(val) == 2
    assert val[0] == "three"
    assert val[1] == "blind mice"


def test_restore_group():
    """Runs burt restore group against a normal case.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_ARR_FLOAT, randint(1, 100))

    burt.restore_group(paths.NORMAL_ALT_RGR, False)

    # CA array PV.
    ca_arr = caget(integration.IOC_LOCAL_PV_ARR_DBL)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1


def test_various_types_restore():
    """Check that restoring for various types works properly.

    No test for a scalar short because I can't find a way of creating
    one in a soft IOC, other than an array of length one.
    """
    # Randomize IOC start values.
    caput(integration.IOC_LOCAL_PV_FLOAT, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_ARR_FLOAT, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_LONG, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_ARR_LONG, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_DBL, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_ARR_DBL, randint(1, 100))
    caput(integration.IOC_LOCAL_PV_STR, "dummy")
    caput(integration.IOC_LOCAL_PV_ARR_STR, ["dummy", "rummy"])
    # Scalar short only available in a waveform in a soft IOC.
    caput(integration.IOC_LOCAL_PV_ARR_SHORT, randint(1, 100))
    # Ignored cases
    caput(integration.IOC_LOCAL_PV_ARR_CHAR, "dummy")

    # Execute the restore.
    burt.restore(integration.CONTROL_ROOM_LOCAL_IOC_TYPES_SNAP)

    pv_long = caget(integration.IOC_LOCAL_PV_LONG)
    pv_double = caget(integration.IOC_LOCAL_PV_DBL)
    pv_arr_double = caget(integration.IOC_LOCAL_PV_ARR_DBL)
    pv_arr_float = caget(integration.IOC_LOCAL_PV_ARR_FLOAT)
    pv_str = caget(integration.IOC_LOCAL_PV_STR)
    pv_arr_str = caget(integration.IOC_LOCAL_PV_ARR_STR)
    pv_arr_char = caget(integration.IOC_LOCAL_PV_ARR_CHAR)
    pv_arr_short = caget(integration.IOC_LOCAL_PV_ARR_SHORT)

    # Note the curious format in the snap file for this PV.
    for a, b in itertools.zip_longest(pv_arr_char, "Hi Lo!"):
        print(f"{a} {b}")
        assert a == ord(b)

    assert pv_long == 200
    assert pv_double == -2.900000000000000e01
    assert pv_arr_double[0] == 3.003617499404633e-02
    assert pv_arr_double[1] == 3.457100664366716e-02
    # Near equality
    assert abs(pv_arr_float[0] - 3.800000e-01) <= 1e-05  # arbitrary
    assert abs(pv_arr_float[1] - 3.800000e-01) <= 1e-05  # arbitrary
    assert pv_arr_short[0] == 4368
    assert pv_str == ""
    assert pv_arr_str[0] == "dummy"
    assert pv_arr_str[1] == "rummy"


def _vanilla_burtwb(input_snap):
    """Run the original burtwb implementation.

    Args:
        input_snap (str): input snap file
    """
    burt_rb_cmd = (
        f"/dls_sw/epics/R3.14.12.3/extensions/bin/linux-x86_64/burtwb -f {input_snap}"
    )

    # Without shell=True raises an exception on Python 2.7
    process = subprocess.Popen(burt_rb_cmd, shell=True)
    process.wait()
    assert process.returncode == 0
