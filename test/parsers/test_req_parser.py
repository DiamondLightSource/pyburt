""" Various tests for the parser classes."""
import pytest
import test
import burt
from burt.parsers import ParserException
from burt.pv import PV


def test_base_case_parsers():
    """Runs the .req parser against mostly blank files.
    """

    req_parser = burt.ReqParser(test.BLANK_REQ)
    assert test.BLANK_REQ == req_parser.path
    assert not req_parser.pvs

    req_parser.parse()
    assert test.BLANK_REQ == req_parser.path
    assert 0 == len(req_parser.pvs)

    snap_parser = burt.SnapParser(test.BLANK_SNAP)
    assert test.BLANK_SNAP == snap_parser.path
    assert not snap_parser.pv_snapshots
    assert "" == snap_parser.time
    assert "" == snap_parser.login_id
    assert "" == snap_parser.u_id
    assert "" == snap_parser.group_id
    assert "" == snap_parser.keywords
    assert "" == snap_parser.comments
    assert "" == snap_parser.type
    assert "" == snap_parser.directory
    assert "" == snap_parser.req_file

    with pytest.raises(ParserException):
        snap_parser.parse()


def test_inline_comments():
    """Runs the parsers against a problematic case with inline comments next to PVs.
    """

    correct_pv_list_req = [PV("SR01C-DI-COL-01:CENTRE"),
                           PV("SR01C-DI-COL-01:GAP"),
                           PV("SR01C-DI-COL-01:LEFT")]

    correct_pv_snapshots = [
        PV("SR01C-DI-COL-01:POS1", ["3.259328000000000e+00"]),
        PV("SR01C-DI-COL-01:POS2", ["-3.276854000000000e+00", "333"]),
        PV("SR01C-DI-COL-02:POS1", ["-1.200000000000000e+01"]),
        PV("SR01C-DI-COL-03:POS3", ["666"])]

    req_parser = burt.ReqParser(test.INLINE_COMMENTS_REQ)
    req_parser.parse()
    assert test.INLINE_COMMENTS_REQ == req_parser.path
    assert 3 == len(req_parser.pvs)
    assert correct_pv_list_req == req_parser.pvs

    snap_parser = burt.SnapParser(test.INLINE_COMMENTS_SNAP)
    snap_parser.parse()
    assert test.INLINE_COMMENTS_SNAP == snap_parser.path
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


def test_malformed_files():
    """Runs the .snap parser against the malformed .snap files.
    """
    with pytest.raises(ParserException):
        req_parser = burt.ReqParser(test.MALFORMED_REQ)
        req_parser.parse()

    with pytest.raises(ParserException):
        req_parser = burt.ReqParser(test.MALFORMED_SAVE_LEN_NEG_INT_REQ)
        req_parser.parse()

    with pytest.raises(ParserException):
        req_parser = burt.ReqParser(test.MALFORMED_SAVE_LEN_NON_INT_REQ)
        req_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MISSING_BOTTOM_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MISSING_TOP_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MISORDERED_BURT_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.ONLY_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.DUPLICATE_BURT_HEADERS_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MALFORMED_HEADER_TYPO_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MALFORMED_BODY_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = burt.SnapParser(test.MALFORMED_HEADER_COLONS_SNAP)
        snap_parser.parse()

    # Entries should still be parsed fine as header is valid, but values could be problematic.
    snap_parser = burt.SnapParser(test.MALFORMED_HEADER_ENTRIES_SNAP)
    snap_parser.parse()


def test_req_parser_normal():
    """Runs the .req parser against a basic case.
    """
    correct_pv_list = [PV("SR01C-DI-COL-01:CENTRE"),
                       PV("SR-DI-PICO-01:BUCKETS"),
                       PV("SR01C-DI-COL-02:CENTRE"),
                       PV("SR01C-DI-COL-02:GAP"),
                       PV("SR-DI-PICO-01:BUCKETS", save_len=5),
                       PV("SR-DI-PICO-01:BUCKETS", is_readonly=True,
                          save_len=10),
                       PV("SR-DI-PICO-01:BUCKETS", is_readonly_notify=True,
                          save_len=25),
                       PV("SR01C-DI-COL-01:POS1", is_readonly_notify=True),
                       PV("SR01C-DI-COL-01:POS2", is_readonly=True),
                       PV("SR01C-DI-COL-02:POS1", is_readonly=True),
                       PV("SR01C-DI-COL-02:POS2", is_readonly=True),
                       PV("SR-CS-RING-01:MODE")]
    req_parser = burt.ReqParser(test.NORMAL_REQ)
    assert test.NORMAL_REQ == req_parser.path
    assert not req_parser.pvs

    req_parser.parse()
    assert test.NORMAL_REQ == req_parser.path
    assert 12 == len(req_parser.pvs)
    assert correct_pv_list == req_parser.pvs


def test_snap_parser_scalars():
    """Runs the .snap parser against a basic case with only PV scalars.
    """
    correct_pv_snapshots = [
        PV("SR01C-DI-COL-01:POS1", ["3.259328000000000e+00"]),
        PV("SR01C-DI-COL-01:POS2", ["-3.276854000000000e+00"]),
        PV("SR01C-DI-COL-02:POS1", ["-1.200000000000000e+01"]),
        PV("SR01C-DI-COL-02:POS2", ["1.200000000000000e+01"])]

    snap_parser = burt.SnapParser(test.SCALARS_SNAP)
    assert test.SCALARS_SNAP == snap_parser.path
    assert not snap_parser.pv_snapshots
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
    assert test.SCALARS_SNAP == snap_parser.path
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
        PV("SR01C-DI-COL-01:POS1",
           ["3.259328000000000e+00", "3.259328000000000e+00",
            "3.259328000000000e+00"]),
        PV("SR01C-DI-COL-01:POS2", ["-3.276854000000000e+00"]),
        PV("SR01C-DI-COL-02:POS1",
           ["-1.200000000000000e+01", "-1.200000000000000e+01"]),
        PV("SR01C-DI-COL-02:POS2", ["1.200000000000000e+01"])]

    snap_parser = burt.SnapParser(test.ARRAYS_AND_SCALARS_SNAP)
    snap_parser.parse()

    assert test.ARRAYS_AND_SCALARS_SNAP == snap_parser.path
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
