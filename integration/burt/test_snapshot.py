""" Various tests for the main burt module.
"""
import pytest
import test
import integration
import burt
import subprocess
import os
import filecmp

from burt.parsers import ParserException


def test_snapshot_normal():
    """Runs a take snapshot test of a normal .req file that specifies DLS PVs
    with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, integration.TMP_PYBURT_OUT,
                       test_comment,
                       test_keywords)

    assert os.path.isfile(integration.TMP_PYBURT_OUT)
    assert os.stat(integration.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(integration.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 12 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert test.NORMAL_REQ == snap_parser.req_file

    # Known scalar PV
    scalar_pv_snapshot = snap_parser.pv_snapshots[0]
    assert scalar_pv_snapshot.name == "SR01C-DI-COL-01:CENTRE"
    assert len(scalar_pv_snapshot.vals) == 1

    # Known ca array PV
    snapshot_ca_arr_pv = snap_parser.pv_snapshots[1]
    assert snapshot_ca_arr_pv.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_ca_arr_pv.vals) == 936

    # The PVs below have a known specified max save length (see
    # testables/normal.req) and readonly modifiers.
    snapshot_save_length_spec_1 = snap_parser.pv_snapshots[4]
    assert snapshot_save_length_spec_1.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_1.vals) == 5

    snapshot_save_length_spec_2 = snap_parser.pv_snapshots[5]
    assert snapshot_save_length_spec_2.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_2.vals) == 10
    assert snapshot_save_length_spec_2.is_readonly

    snapshot_save_length_spec_3 = snap_parser.pv_snapshots[6]
    assert snapshot_save_length_spec_3.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_save_length_spec_3.vals) == 25
    assert snapshot_save_length_spec_3.is_readonly_notify

    # cleanup
    os.remove(integration.TMP_PYBURT_OUT)


def test_snapshot_group_normal():
    """Runs a take snapshot test of a normal .rqg file that specifies .req
    files which point to DLS PVS with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot_group(test.NORMAL_RQG, integration.TMP_PYBURT_OUT,
                             test_comment,
                             test_keywords)

    assert os.path.isfile(integration.TMP_PYBURT_OUT)
    assert os.stat(integration.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(integration.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 556 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert 13 == len(snap_parser.req_file.split(","))

    # cleanup
    os.remove(integration.TMP_PYBURT_OUT)


def test_snapshot_invalid_save_len():
    """
    Try to save a PV with a length specified that is greater than the PV
    data size. This is a case which would not be  caught by the parser.
    """
    with pytest.raises(ValueError):
        burt.take_snapshot(test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ,
                           test.TMP_PYBURT_OUT)


def test_burt_vanilla_rb():
    """Runs vanilla BURT against pyburt for the rb functionality and checks for differences.
    """
    comment = "Hello World"
    keyword = "little red sally jumped over the fence"

    _vanilla_burtrb(integration.NORMAL_REQ, integration.TMP_BURT_OUT,
                    comment, keyword)

    burt.take_snapshot(integration.NORMAL_REQ, integration.TMP_PYBURT_OUT,
                       comment,
                       keyword)

    assert filecmp.cmp(integration.TMP_BURT_OUT, integration.TMP_PYBURT_OUT)

    # cleanup
    os.remove(integration.TMP_BURT_OUT)
    os.remove(integration.TMP_PYBURT_OUT)


def _vanilla_burtrb(input_req, output_snap, comments, keywords):
    """
    Wrapper for the original burtrb implementation.

    Args:
        input_req (str): input req file(s)
        output_snap (str): output snap file
        comments (comments): comments
        keywords (keywords): keywords
    """
    burt_rb_cmd = \
        "/dls_sw/epics/R3.14.12.3/extensions/bin/linux-x86_64/burtrb -f " \
        + input_req + " -o " \
        + output_snap + " -c " + comments + " -k " + keywords

    # Without shell=True raises an exception on Python 2.7
    process = subprocess.Popen(burt_rb_cmd, shell=True)
    process.wait()
    assert process.returncode == 0
