""" Various tests for the burt modules which require a running IOC (restore).
"""
import pytest
import integration
import subprocess
import os
import filecmp
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


def test_burt_vanilla_rb():
    """Runs vanilla BURT against pyburt for the rb functionality and checks for differences.
    """
    burt_tmp_out = "integration/testables/tmp_burt.snap"
    pyburt_tmp_out = "integration/testables/tmp_pyburt.snap"
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    burt_rb_cmd = \
        "/dls_sw/epics/R3.14.12.3/extensions/bin/linux-x86_64/burtrb -f " + integration.NORMAL_REQ + " -o " + \
        burt_tmp_out + " -c " + comment + " -k " + keyword

    # Without shell=True raises an exception on Python 2.7
    process = subprocess.Popen(burt_rb_cmd, shell=True)
    process.wait()
    print("BURT process return code: " + str(process.returncode))

    pyburt.take_snapshot(integration.NORMAL_REQ, pyburt_tmp_out, comment, keyword)

    assert filecmp.cmp(burt_tmp_out, pyburt_tmp_out)

    # cleanup
    os.remove(burt_tmp_out)
    os.remove(pyburt_tmp_out)
