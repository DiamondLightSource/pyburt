""" Various tests for the burt modules which require a running IOC (restore).
"""
import pytest
import integration
from burt import pyburt, parser

from pkg_resources import require

require('cothread')
from cothread.catools import caget


def test_restore_integration():
    """Runs burt restore against a .snap file with ca array and scalar pvs.

    This test needs to be run manually after the test IOC is set up and running.
    """
    # CA array PV.
    pyburt.restore(integration.IOC_SNAP_FILE_1)
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert abs(ca_arr[0] - 3.259328000000000e+00) <= 0.2  # Allowed truncation margin
    assert ca_arr[1] == 4
    assert ca_arr[2] == -1

    # Scalar PV.
    pyburt.restore(integration.IOC_SNAP_FILE_2)
    ca_arr = caget(integration.IOC_LOCAL_PV)
    assert ca_arr[0] == 2
