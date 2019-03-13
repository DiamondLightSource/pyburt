""" Various tests for the main burt module.
"""
import pytest
import test
import burt
from burt import parser
import os


def test_blank_snapshot():
    """Runs the burt snapshot against a blank .req file.
    """
    burt.take_snapshot(test.BLANK_REQ, test.TMP_BURT_OUT)

    assert os.path.isfile(test.TMP_BURT_OUT)
    assert os.stat(test.TMP_BURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent properties, e.g. keywords, directory, etc.
    snap_parser = parser.SnapParser(test.TMP_BURT_OUT)
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
    os.remove(test.TMP_BURT_OUT)


def test_bad_file_arguments():
    """Runs the burt script against a case where the file arguments are malformed.
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


def test_snapshot_1_normal():
    """Runs the burt script against a take snapshot test of a normal .req file with scalars and ca array pvs.
    """
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_BURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_BURT_OUT)
    assert os.stat(test.TMP_BURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent properties, e.g. keywords, directory, etc.
    snap_parser = parser.SnapParser(test.TMP_BURT_OUT)
    snap_parser.parse()
    assert 10 == len(snap_parser.pv_snapshots)
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
    assert len(scalar_pv_snapshot.vals) == 1

    # Known ca array PV
    snapshot_ca_arr_pv = snap_parser.pv_snapshots[1]
    assert snapshot_ca_arr_pv.name == "SR-DI-PICO-01:BUCKETS"
    assert len(snapshot_ca_arr_pv.vals) == 936
    assert len(snapshot_ca_arr_pv.vals) == 936

    # cleanup
    os.remove(test.TMP_BURT_OUT)


def test_blank_restore():
    """Runs burt restore against a blank .snap file.
    """
    with pytest.raises(parser.ParserException):
        burt.restore(test.BLANK_SNAP)
