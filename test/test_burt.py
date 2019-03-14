""" Various tests for the main burt module.
"""
import pytest
import test
import burt
import os

from burt.parsers import ParserException


def test_blank_snapshot():
    """Runs the burt snapshot against a blank .req file.
    """
    burt.take_snapshot(test.BLANK_REQ, test.TMP_PYBURT_OUT)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 0 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert not snap_parser.keywords
    assert not snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert test.BLANK_REQ == snap_parser.req_file
    assert not snap_parser.pv_snapshots

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


def test_bad_file_arguments():
    """Runs the burt script against a case where the file arguments are
    malformed.
    """
    with pytest.raises(ValueError):
        burt.take_snapshot("", "")
    with pytest.raises(ValueError):
        burt.take_snapshot("goodbyeworld", "helloworld")
    with pytest.raises(ValueError):
        burt.take_snapshot("goodbyeworld.req", "helloworld.snap")
    with pytest.raises(ValueError):
        burt.take_snapshot(test.BLANK_REQ, "helloworld.txt")
    with pytest.raises(ValueError):
        burt.restore("")
    with pytest.raises(ValueError):
        burt.restore("goodbyeworld")
    with pytest.raises(ValueError):
        burt.restore("helloworld.snap")


def test_snapshot_normal():
    """Runs a take snapshot test of a normal .req file with scalars and ca
    array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
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
    os.remove(test.TMP_PYBURT_OUT)


def test_snapshot_newlines_in_args():
    """Runs a take snapshot test with the problematic case of newlines in user
    supplied meta data. The newlines should be stripped.
    """
    test_comment = "\nHello\t\n \nWorld\r\n\t"
    test_keywords = "\t\ncool\n,\r\nsnap,file\n\t\r"

    expected_snap_comment = "Hello\t World"
    expected_snap_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()

    assert expected_snap_comment == snap_parser.comments
    assert expected_snap_keywords == snap_parser.keywords

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


def test_snapshot_invalid_save_len():
    """
    Try to save a PV with a length specified that is greater than the PV
    data size. This is a case which would not be  caught by the parser.
    """
    with pytest.raises(ValueError):
        burt.take_snapshot(test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ,
                           test.TMP_PYBURT_OUT)


def test_blank_restore():
    """Runs burt restore against a blank .snap file.
    """
    with pytest.raises(ParserException):
        burt.restore(test.BLANK_SNAP)
