""" Various tests for the req parser."""
import pytest
import test
import burt
from burt.parsers.exception import ParserException
from burt.parsers.req import ReqParser as rp


def test_base_case():
    """Runs the .req parser against mostly blank files.
    """
    req_parser = burt.ReqParser(test.BLANK_REQ)
    assert test.BLANK_REQ == req_parser.path

    _, body = req_parser.parse()
    assert test.BLANK_REQ == req_parser.path
    assert 0 == len(body)


def test_inline_comments():
    """Runs the parser against a case with inline comments next to
    PVs.
    """
    correct_pv_list = [rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, ""),
                       rp.REQ_PV("SR01C-DI-COL-01:GAP", None, ""),
                       rp.REQ_PV("SR01C-DI-COL-01:LEFT", None, "")]

    req_parser = burt.ReqParser(test.INLINE_COMMENTS_REQ)
    _, body = req_parser.parse()
    assert test.INLINE_COMMENTS_REQ == req_parser.path
    assert 3 == len(body)
    assert correct_pv_list == body


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
    correct_pv_list = [rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, ""),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", None, ""),
                       rp.REQ_PV("SR01C-DI-COL-02:CENTRE", None, ""),
                       rp.REQ_PV("SR01C-DI-COL-02:GAP", None, ""),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 5, ""),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 10, "RO"),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 25, "RON"),
                       rp.REQ_PV("SR01C-DI-COL-01:POS1", None, "RON"),
                       rp.REQ_PV("SR01C-DI-COL-01:POS2", None, "RO"),
                       rp.REQ_PV("SR01C-DI-COL-02:POS1", None, "RO"),
                       rp.REQ_PV("SR01C-DI-COL-02:POS2", None, "RO"),
                       rp.REQ_PV("SR-CS-RING-01:MODE", None, "")]

    req_parser = burt.ReqParser(test.NORMAL_REQ)
    assert test.NORMAL_REQ == req_parser.path

    _, body = req_parser.parse()
    assert test.NORMAL_REQ == req_parser.path
    assert 12 == len(body)
    assert correct_pv_list == body
