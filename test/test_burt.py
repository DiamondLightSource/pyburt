""" Various tests for the main burt module.
"""
import pytest
import test
import burt
import cothread
from burt import pyburt, parser
import os

from pkg_resources import require

require('cothread')
from cothread.catools import caget


def test_blank_snapshot():
    """Runs the burt snapshot against a blank .req file.
    """
    tmp_blank_dest = "test/testables/tmp_blank_snap.snap"

    pyburt.take_snapshot(test.BLANK_REQ_FILE, tmp_blank_dest)

    assert os.path.isfile(tmp_blank_dest)
    assert os.stat(tmp_blank_dest).st_size != 0

    # Reverse parsing should have the correct contents for the independent properties, e.g. keywords, directory, etc.
    snap_parser = parser.SnapParser(tmp_blank_dest)
    snap_parser.parse()
    assert 0 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert not snap_parser.keywords
    assert not snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert "test/testables" == snap_parser.directory
    assert test.BLANK_REQ_FILE == snap_parser.req_file
    assert not snap_parser.pv_snapshots

    # cleanup
    os.remove(tmp_blank_dest)


def test_bad_file_arguments():
    """Runs the burt script against a case where the file arguments are malformed.
    """
    with pytest.raises(ValueError):
        pyburt.take_snapshot("", "")
    with pytest.raises(ValueError):
        pyburt.take_snapshot("goodbyeworld", "helloworld")
    with pytest.raises(ValueError):
        pyburt.take_snapshot("goodbyeworld.req", "helloworld.snap")
    with pytest.raises(ValueError):
        pyburt.take_snapshot(test.BLANK_REQ_FILE, "helloworld.txt")
    with pytest.raises(ValueError):
        pyburt.restore("")
    with pytest.raises(ValueError):
        pyburt.restore("goodbyeworld")
    with pytest.raises(ValueError):
        pyburt.restore("helloworld.snap")


def test_snapshot_1_scalars():
    """Runs the burt script against a take snapshot test of a normal .req file with scalar pvs.
    """
    tmp_dest = "test/testables/tmp_snap.snap"
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    pyburt.take_snapshot(test.REQ_FILE_1, tmp_dest, test_comment, test_keywords)

    assert os.path.isfile(tmp_dest)
    assert os.stat(tmp_dest).st_size != 0

    # Reverse parsing should have the correct contents for the independent properties, e.g. keywords, directory, etc.
    snap_parser = parser.SnapParser(tmp_dest)
    snap_parser.parse()
    assert 9 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert "test/testables" == snap_parser.directory
    assert test.REQ_FILE_1 == snap_parser.req_file

    # Known scalar PV
    snapshot_vals = snap_parser.pv_snapshots[test.PV_SCALAR_1]
    assert snapshot_vals[0] == '1'
    assert len(snapshot_vals[1]) == 1

    # cleanup
    os.remove(tmp_dest)


def test_snapshot_1_ca_arr():
    """Runs the burt script against a take snapshot test of a normal .req file with ca array pvs.
    """
    tmp_dest = "test/testables/tmp_snap.snap"
    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    pyburt.take_snapshot(test.REQ_FILE_2, tmp_dest, test_comment, test_keywords)

    assert os.path.isfile(tmp_dest)
    assert os.stat(tmp_dest).st_size != 0

    # Reverse parsing should have the correct contents for the independent properties, e.g. keywords, directory, etc.
    snap_parser = parser.SnapParser(tmp_dest)
    snap_parser.parse()
    assert 3 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert "test/testables" == snap_parser.directory
    assert test.REQ_FILE_2 == snap_parser.req_file

    # Known ca array PV
    snapshot_length_ca_arr_pv = snap_parser.pv_snapshots[test.PV_WITH_CA_ARR][0]
    snapshot_vals_ca_arr_pv = snap_parser.pv_snapshots[test.PV_WITH_CA_ARR][1]
    assert snapshot_length_ca_arr_pv == '936'
    assert len(snapshot_vals_ca_arr_pv) == 936

    # cleanup
    os.remove(tmp_dest)


def test_basic_restore():
    """Runs burt restore against a blank .snap file.
    """
    with pytest.raises(parser.ParserException):
        pyburt.restore(test.BLANK_SNAP_FILE)
