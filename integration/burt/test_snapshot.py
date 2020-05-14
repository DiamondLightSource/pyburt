""" Various tests for the main burt module.
"""
import pytest
import test
import integration
import burt
import subprocess
import os
import filecmp
import time

from burt import SnapParser as sp

NOT_DLS = "DLS_EPICS_RELEASE" not in os.environ


@pytest.fixture
def burt_tmpfile():
    yield integration.TMP_BURT_OUT
    try:
        os.remove(integration.TMP_BURT_OUT)
    except FileNotFoundError:
        pass


@pytest.fixture
def pyburt_tmpfile():
    yield integration.TMP_PYBURT_OUT
    try:
        os.remove(integration.TMP_PYBURT_OUT)
    except FileNotFoundError:
        pass


@pytest.mark.skipif(NOT_DLS, reason="Run only inside DLS")
def test_snapshot_normal(pyburt_tmpfile):
    """Runs a take snapshot test of a normal .req file that specifies DLS PVs
    with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 12 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert test.NORMAL_REQ == header[sp.REQ_FILE_PREFIX]

    # Known scalar PV
    scalar_pv_snapshot = body[0]
    assert scalar_pv_snapshot.name == "SR01C-DI-COL-01:CENTRE"
    assert len(scalar_pv_snapshot.vals) == 1

    # Known ca array PV
    snapshot_ca_arr_pv = body[1]
    assert snapshot_ca_arr_pv.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_ca_arr_pv.vals) == 936

    # The PVs below have a known specified max save length (see
    # testables/normal.req) and readonly modifiers.
    snapshot_save_length_spec_1 = body[4]
    assert snapshot_save_length_spec_1.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_1.vals) == 5

    snapshot_save_length_spec_2 = body[5]
    assert snapshot_save_length_spec_2.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_2.vals) == 10
    assert snapshot_save_length_spec_2.modifier == "RO"

    snapshot_save_length_spec_3 = body[6]
    assert snapshot_save_length_spec_3.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_3.vals) == 25
    assert snapshot_save_length_spec_3.modifier == "RON"


@pytest.mark.xfail  # take_snapshot_group is not yet implemented
def test_snapshot_group_normal(pyburt_tmpfile):
    """Runs a take snapshot test of a normal .rqg file that specifies .req
    files which point to DLS PVS with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot_group(
        test.NORMAL_RQG, pyburt_tmpfile, test_comment, test_keywords, False
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
    """
    Try to save a PV with a length specified in the .req file that is greater
    than the actual PV's data size. This is a case which would not be caught by the parser.
    """
    with pytest.raises(ValueError):
        burt.take_snapshot([test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ], pyburt_tmpfile)


@pytest.mark.xfail  # The output is no long exactly the Ysame.
def test_burt_vanilla_rb(burt_tmpfile, pyburt_tmpfile):
    """Runs vanilla BURT against pyburt for the rb functionality and checks for
    differences.
    """
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    _vanilla_burtrb(integration.NORMAL_REQ, burt_tmpfile, comment, keyword)

    burt.take_snapshot([integration.NORMAL_REQ], pyburt_tmpfile, comment, keyword)

    assert filecmp.cmp(burt_tmpfile, pyburt_tmpfile, shallow=False)


@pytest.mark.skipif(NOT_DLS, reason="Run only inside DLS")
def test_speed_snapshot(pyburt_tmpfile):
    """Speed comparison between different snapshot schemes."""
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    t0 = time.time()
    burt.take_snapshot(
        [integration.BCDORBIT_REQ], pyburt_tmpfile, test_comment, test_keywords
    )
    t1 = time.time()
    tend = t1 - t0
    print(f"test_speed_snapshot_pyburt_1:{tend}")

    t0 = time.time()
    burt.take_snapshot(
        [integration.BCDORBIT_REQ], pyburt_tmpfile, test_comment, test_keywords
    )
    t1 = time.time()
    tend = t1 - t0
    print(f"test_speed_snapshot_pyburt_2:{tend}")

    t0 = time.time()
    _vanilla_burtrb(
        "/home/ops/burt/requestFiles/bcdorbit.req",
        pyburt_tmpfile,
        test_comment,
        test_keywords,
    )
    t1 = time.time()
    tend = t1 - t0
    print(f"test_speed_snapshot_burt_vanilla:{tend}")


@pytest.mark.skipif(NOT_DLS, reason="Run only inside DLS")
def test_various_types_against_burt(pyburt_tmpfile):
    """Test edge case types against old burt.

    Requires the following DLS PVs to be active:

    % Scalar long
    SR-RF-LLRF-30:T-MOTOR.SREV
    % Array long
    LI-VA-FVALV-01:GETRAWILK
    % Scalar double
    SR-RF-RFPGU-34:SETPHASE
    % Array double
    SR-CS-FILL-01:FITGUNCHGE
    % Array float
    BR-RF-LLRF-01:AM:WAVE
    % Scalar enum
    SR-RF-IOC-31:BURT:OK
    % Scalar string
    SR-RF-IOT-34:SERIAL
    % Scalar char
    BR01C-PC-EVR-02:LINAC-PRE
    % Array char
    CS-CS-MSTAT-01:MESS01
    % Scalar short
    LI-TI-EVG-01:LINAC-PRE
    % Array short
    LI-VA-VLVCC-01:SOFTWARE

    """
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    burt.take_snapshot([test.TYPES_REQ], pyburt_tmpfile, comment, keyword)

    # Read into strings to discard time dependent header.
    with open(pyburt_tmpfile, "r") as pyburt_out:
        with open(test.CONTROL_ROOM_TYPES_SNAP, "r") as burt_out:
            pyburt_out_str = pyburt_out.read().split(sp.SNAP_HEADER_END)[1]
            burt_out_str = burt_out.read().split(sp.SNAP_HEADER_END)[1]

            # Some of the str type PV's can change their case, so this test is
            # a bit brittle. E.g. CS-CS-MSTAT-01:MESS01 can have a lower case b or
            # capital case B for "User beam time".
            assert pyburt_out_str.strip().lower() == burt_out_str.strip().lower()


def test_speed_snapshot_group():
    """Speed comparison between different snapshot group schemes"""
    pass


def _vanilla_burtrb(input_req, output_snap, comments, keywords):
    """
    Wrapper for the original burtrb implementation.

    Args:
        input_req (str): input req file(s)
        output_snap (str): output snap file
        comments (comments): comments
        keywords (keywords): keywords
    """
    burt_rb_cmd = (
        "/dls_sw/epics/R3.14.12.3/extensions/bin/linux-x86_64/burtrb -f "
        + input_req
        + " -o "
        + output_snap
        + " -c "
        + comments
        + " -k "
        + keywords
    )

    # Without shell=True raises an exception on Python 2.7
    process = subprocess.Popen(burt_rb_cmd, shell=True)
    process.wait()
    assert process.returncode == 0
