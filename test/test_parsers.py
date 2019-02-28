""" Various tests for the parser classes."""

import burt
from burt import parser
from . import BLANK_REQ_FILE, BLANK_SNAP_FILE, REQ_FILE_1, SNAP_FILE_1
import pytest


def test_base_case_req_parser():
    """Runs the .req parser against mostly blank files.
    """
    req_parser = parser.ReqParser(BLANK_REQ_FILE)
    assert BLANK_REQ_FILE == req_parser.path
    assert 0 == len(req_parser.pvs)

    req_parser.parse()
    assert BLANK_REQ_FILE == req_parser.path
    assert 0 == len(req_parser.pvs)


def test_basic_case_1_req_parser():
    """Runs the .req parser against a basic case.
    """
    correct_pv_list = ["SR01C-DI-COL-01:CENTRE", "SR01C-DI-COL-01:GAP", "SR01C-DI-COL-02:CENTRE", "SR01C-DI-COL-02:GAP",
                       "RO SR01C-DI-COL-01:POS1", "RO SR01C-DI-COL-01:POS2", "RO SR01C-DI-COL-02:POS1",
                       "RO SR01C-DI-COL-02:POS2", "SR-CS-RING-01:MODE"]
    req_parser = parser.ReqParser(REQ_FILE_1)
    assert REQ_FILE_1 == req_parser.path
    assert 0 == len(req_parser.pvs)

    req_parser.parse()
    assert REQ_FILE_1 == req_parser.path
    assert 9 == len(req_parser.pvs)
    assert correct_pv_list == req_parser.pvs


def test_base_case_snap_parser():
    """Runs the .snap parser against mostly blank files.
    """
    snap_parser = parser.SnapParser(BLANK_SNAP_FILE)
    assert BLANK_SNAP_FILE == snap_parser.path
    assert 0 == len(snap_parser.pv_snapshots)
    assert "" == snap_parser.time
    assert "" == snap_parser.login_id
    assert "" == snap_parser.u_id
    assert "" == snap_parser.group_id
    assert "" == snap_parser.keywords
    assert "" == snap_parser.comments
    assert "" == snap_parser.type
    assert "" == snap_parser.directory
    assert "" == snap_parser.req_file

    with pytest.raises(parser.ParserException):
        snap_parser.parse()


def test_basic_case_1_snap_parser():
    """Runs the .snap parser against a basic case.
    """
    correct_pv_snapshots = {"SR01C-DI-COL-01:POS1": ["1", "3.259328000000000e+00"],
                            "SR01C-DI-COL-01:POS2": ["1", "-3.276854000000000e+00"],
                            "SR01C-DI-COL-02:POS1": ["1", "-1.200000000000000e+01"],
                            "SR01C-DI-COL-02:POS2": ["1", "1.200000000000000e+01"]}
    snap_parser = parser.SnapParser(SNAP_FILE_1)
    assert SNAP_FILE_1 == snap_parser.path
    assert 0 == len(snap_parser.pv_snapshots)
    assert "" == snap_parser.time
    assert "" == snap_parser.login_id
    assert "" == snap_parser.u_id
    assert "" == snap_parser.group_id
    assert "" == snap_parser.keywords
    assert "" == snap_parser.comments
    assert "" == snap_parser.type
    assert "" == snap_parser.directory
    assert "" == snap_parser.req_file

    snap_parser.parse()
    assert SNAP_FILE_1 == snap_parser.path
    assert 4 == len(snap_parser.pv_snapshots)
    assert "Tue Sep 21 15:07:59 2010" == snap_parser.time
    assert "ops-cc83 (Chris Christou)" == snap_parser.login_id
    assert "37245" == snap_parser.u_id
    assert "37245" == snap_parser.group_id
    assert "hello world" == snap_parser.keywords
    assert r"Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to" \
           r" peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4" == snap_parser.comments
    assert "Absolute" == snap_parser.type
    assert "/home/ops/burt/backupFiles" == snap_parser.directory
    assert "/home/ops/burt/requestFiles/SR-DI.req" == snap_parser.req_file
    assert correct_pv_snapshots == snap_parser.pv_snapshots
