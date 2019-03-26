""" Various tests for the req parser."""
import pytest
import test
import burt
from burt.parsers import ParserException
from burt.pv import PV


def test_base_case():
    """Runs the .req parser against mostly blank files.
    """
    req_parser = burt.ReqParser(test.BLANK_REQ)
    assert test.BLANK_REQ == req_parser.path
    assert not req_parser.pvs

    req_parser.parse()
    assert test.BLANK_REQ == req_parser.path
    assert 0 == len(req_parser.pvs)


def test_inline_comments():
    """Runs the parser against a case with inline comments next to
    PVs.
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


def test_malformed_files():
    """Runs the parser against the malformed .req files.
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
