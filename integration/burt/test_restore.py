""" Various tests for the burt modules which require a running IOC (restore).
"""
import integration
import burt
import test
from random import randint

from pkg_resources import require

require('cothread')
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
    assert abs(
        ca_arr[0] - 3.259328000000000e+00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1

    # Scalar PV.
    burt.restore(integration.SCALAR_SNAP)
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert ca_arr[0] == 2


def test_restore_group():
    """Runs burt restore group against a normal case.

    A caget on the test IOC is performed to check that the restore changed the
    value to as specified in the .snap file.
    """
    # Randomize IOC start value.
    caput(integration.IOC_LOCAL_PV, randint(1, 100))

    burt.restore_group(test.NORMAL_ALT_RGR)

    # CA array PV.
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert abs(
        ca_arr[0] - 3.259328000000000e+00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1
