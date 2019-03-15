""" Various tests for the burt modules which require a running IOC (restore).
"""
import integration
import subprocess
import os
import filecmp
import burt

from pkg_resources import require

require('cothread')
from cothread.catools import caget


def test_restore_integration():
    """Runs burt restore against a .snap file with ca array and scalar pvs.

    This test needs to be run manually after the test IOC is set up and running.
    """
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


def test_burt_vanilla_rb():
    """Runs vanilla BURT against pyburt for the rb functionality and checks for differences.
    """
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    integration.vanilla_burtrb(integration.NORMAL_REQ,
                               integration.TMP_BURT_OUT, comment, keyword)

    burt.take_snapshot(integration.NORMAL_REQ, integration.TMP_PYBURT_OUT,
                       comment,
                       keyword)

    assert filecmp.cmp(integration.TMP_BURT_OUT, integration.TMP_PYBURT_OUT)

    # cleanup
    os.remove(integration.TMP_BURT_OUT)
    os.remove(integration.TMP_PYBURT_OUT)
