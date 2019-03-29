""" Various tests for the req parser."""
import pytest
import test
from burt.parsers import ParserException
from burt import ReqParser as rp


def test_base_case():
    """Runs the .req parser against mostly blank files.
    """
    req_parser = rp(test.BLANK_REQ)
    assert test.BLANK_REQ == req_parser.path

    _, body = req_parser.parse()
    assert test.BLANK_REQ == req_parser.path
    assert 0 == len(body)


def test_inline_comments():
    """Runs the parser against a case with inline comments next to
    PVs.
    """
    correct_pv_list = [rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, None),
                       rp.REQ_PV("SR01C-DI-COL-01:GAP", None, None),
                       rp.REQ_PV("SR01C-DI-COL-01:LEFT", None, None)]

    req_parser = rp(test.INLINE_COMMENTS_REQ)
    _, body = req_parser.parse()
    assert test.INLINE_COMMENTS_REQ == req_parser.path
    assert 3 == len(body)
    assert correct_pv_list == body


def test_malformed_files():
    """Runs the parser against the malformed .req files.
    """
    with pytest.raises(ParserException):
        req_parser = rp(test.MALFORMED_REQ)
        req_parser.parse()

    with pytest.raises(ParserException):
        req_parser = rp(test.MALFORMED_SAVE_LEN_NEG_INT_REQ)
        req_parser.parse()

    with pytest.raises(ParserException):
        req_parser = rp(test.MALFORMED_SAVE_LEN_NON_INT_REQ)
        req_parser.parse()


def test_req_parser_normal():
    """Runs the .req parser against a basic case.
    """
    correct_pv_list = [rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, None),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", None, None),
                       rp.REQ_PV("SR01C-DI-COL-02:CENTRE", None, None),
                       rp.REQ_PV("SR01C-DI-COL-02:GAP", None, None),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 5, None),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 10, "RO"),
                       rp.REQ_PV("SR-DI-PICO-01:BUCKETS", 25, "RON"),
                       rp.REQ_PV("SR01C-DI-COL-01:POS1", None, "RON"),
                       rp.REQ_PV("SR01C-DI-COL-01:POS2", None, "RO"),
                       rp.REQ_PV("SR01C-DI-COL-02:POS1", None, "RO"),
                       rp.REQ_PV("SR01C-DI-COL-02:POS2", None, "RO"),
                       rp.REQ_PV("SR-CS-RING-01:MODE", None, None)]

    req_parser = rp(test.NORMAL_REQ)
    assert test.NORMAL_REQ == req_parser.path

    _, body = req_parser.parse()
    assert test.NORMAL_REQ == req_parser.path
    assert 12 == len(body)
    assert correct_pv_list == body
