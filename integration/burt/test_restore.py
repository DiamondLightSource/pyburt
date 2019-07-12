""" Various tests for the burt modules which require a running IOC (restore).
"""
import integration
import burt
import subprocess
import test
import time
from random import randint

from pkg_resources import require

require("cothread")
from cothread.catools import caget, caput


def test_restore():
    """Runs burt restore against a .snap file with ca array and scalar pvs.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV, randint(1, 100))

    # CA array PV.
    burt.restore(integration.ARR_SNAP)
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1

    # Scalar PV.
    burt.restore(integration.SCALAR_SNAP)
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert ca_arr[0] == 2


def test_restore_long():
    """Runs burt restore against a .snap file with a long datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV_LONG, randint(1, 100))

    # CA long PV.
    burt.restore(integration.LONG_SNAP)


def test_restore_enum():
    """Runs burt restore against a .snap file with an enum datatype.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV, randint(1, 100))

    # CA long PV.
    burt.restore(integration.ENUM_SNAP)


def test_restore_group():
    """Runs burt restore group against a normal case.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV, randint(1, 100))

    burt.restore_group(test.NORMAL_ALT_RGR, False)

    # CA array PV.
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert abs(ca_arr[0] - 3.259328000000000e00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1


def test_speed_restore():
    """Speed comparison between different restore schemes."""
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    t0 = time.time()
    burt.restore(
        integration.BCDORBIT_SNAP
    )
    t1 = time.time()
    tend = t1 - t0
    print(f"test_speed_restore_1:{tend}")

    t0 = time.time()
    _vanilla_burtwb(
        integration.BCDORBIT_SNAP
    )
    t1 = time.time()
    tend = t1 - t0
    print(f"test_speed_restore_burt_vanilla:{tend}")


def _vanilla_burtwb(input_snap):
    """
    Wrapper for the original burtwb implementation.

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
