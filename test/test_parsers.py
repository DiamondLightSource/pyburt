""" Various tests for the parser classes."""
import pytest
import test
import burt
from burt import parser
from burt.pv import PV


def test_base_case_req_parser():
    """Runs the .req parser against mostly blank files.
    """
    req_parser = parser.ReqParser(test.BLANK_REQ_FILE)
    assert test.BLANK_REQ_FILE == req_parser.path
    assert 0 == len(req_parser.pvs)

    req_parser.parse()
    assert test.BLANK_REQ_FILE == req_parser.path
    assert 0 == len(req_parser.pvs)


def test_basic_case_1_req_parser():
    """Runs the .req parser against a basic case.
    """
    correct_pv_list = [PV("SR01C-DI-COL-01:CENTRE"), PV("SR01C-DI-COL-01:GAP"), PV("SR01C-DI-COL-02:CENTRE"),
                       PV("SR01C-DI-COL-02:GAP"),
                       PV("SR01C-DI-COL-01:POS1"), PV("SR01C-DI-COL-01:POS2"), PV("SR01C-DI-COL-02:POS1"),
                       PV("SR01C-DI-COL-02:POS2"), PV("SR-CS-RING-01:MODE")]
    req_parser = parser.ReqParser(test.REQ_FILE_1)
    assert test.REQ_FILE_1 == req_parser.path
    assert 0 == len(req_parser.pvs)

    req_parser.parse()
    assert test.REQ_FILE_1 == req_parser.path
    assert 9 == len(req_parser.pvs)

    assert correct_pv_list == req_parser.pvs


def test_inline_comment():
    """Runs the parsers against a problematic case with inline comments next to PVs.
    """
    correct_pv_list = [PV("SR01C-DI-COL-01:CENTRE"), PV("SR01C-DI-COL-01:GAP"), PV("SR01C-DI-COL-02:CENTRE")]

    req_parser = parser.ReqParser(test.REQ_FILE_WITH_INLINE_COMMENTS)
    req_parser.parse()

    assert test.REQ_FILE_WITH_INLINE_COMMENTS == req_parser.path
    assert 3 == len(req_parser.pvs)
    assert correct_pv_list == req_parser.pvs


def test_base_case_snap_parser():
    """Runs the .snap parser against mostly blank files.
    """
    snap_parser = parser.SnapParser(test.BLANK_SNAP_FILE)
    assert test.BLANK_SNAP_FILE == snap_parser.path
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


def test_snap_parser_scalars():
    """Runs the .snap parser against a basic case with only PV scalars.
    """
    correct_pv_snapshots = [PV("SR01C-DI-COL-01:POS1", ["3.259328000000000e+00"], dtype_len=1),
                            PV("SR01C-DI-COL-01:POS2", ["-3.276854000000000e+00"], dtype_len=1),
                            PV("SR01C-DI-COL-02:POS1", ["-1.200000000000000e+01"], dtype_len=1),
                            PV("SR01C-DI-COL-02:POS2", ["1.200000000000000e+01"], dtype_len=1)]
    snap_parser = parser.SnapParser(test.SNAP_FILE_1)
    assert test.SNAP_FILE_1 == snap_parser.path
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
    assert test.SNAP_FILE_1 == snap_parser.path
    assert 4 == len(snap_parser.pv_snapshots)
    assert "Tue Sep 21 15:07:59 2010" == snap_parser.time
    assert "ops-cc83 (Chris Christou)" == snap_parser.login_id
    assert "37245" == snap_parser.u_id
    assert "37245" == snap_parser.group_id
    assert "hello world" == snap_parser.keywords
    assert r"Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to" \
           r" peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4" == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert "/home/ops/burt/backupFiles" == snap_parser.directory
    assert "/home/ops/burt/requestFiles/SR-DI.req" == snap_parser.req_file
    assert correct_pv_snapshots == snap_parser.pv_snapshots


def test_snap_parser_ca_arr():
    """Runs the .snap parser against a case with ca arrays.
    """
    correct_pv_snapshots = [
        PV("SR01C-DI-COL-01:POS1", ["3.259328000000000e+00", "3.259328000000000e+00", "3.259328000000000e+00"],
           dtype_len=3),
        PV("SR01C-DI-COL-01:POS2", ["-3.276854000000000e+00"], dtype_len=1),
        PV("SR01C-DI-COL-02:POS1", ["-1.200000000000000e+01", "-1.200000000000000e+01"], dtype_len=2),
        PV("SR01C-DI-COL-02:POS2", ["1.200000000000000e+01"], dtype_len=1)]

    snap_parser = parser.SnapParser(test.SNAP_FILE_2)

    snap_parser.parse()
    assert test.SNAP_FILE_2 == snap_parser.path
    assert 4 == len(snap_parser.pv_snapshots)
    assert "Tue Sep 21 15:07:59 2010" == snap_parser.time
    assert "ops-cc83 (Chris Christou)" == snap_parser.login_id
    assert "37245" == snap_parser.u_id
    assert "37245" == snap_parser.group_id
    assert "hello world" == snap_parser.keywords
    assert r"Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to" \
           r" peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4" == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert "/home/ops/burt/backupFiles" == snap_parser.directory
    assert "/home/ops/burt/requestFiles/SR-DI.req" == snap_parser.req_file
    assert correct_pv_snapshots == snap_parser.pv_snapshots


def test_incorrect_snap_header():
    """Runs the .snap parser against a case with a missing BURT header.
    """
    with pytest.raises(parser.ParserException):
        snap_parser = parser.SnapParser(test.WRONG_HEADER)
        snap_parser.parse()


def test_blank_snap_header():
    """Runs the .snap parser against a case where there are no header contents.
    """
    with pytest.raises(parser.ParserException):
        snap_parser = parser.SnapParser(test.BLANK_HEADER_CONTENTS)
        snap_parser.parse()
