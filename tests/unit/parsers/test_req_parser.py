"""Various tests for the req parser."""
import pytest

import tests
from burt import ReqParser as rp
from burt.parsers import ParserException


def test_base_case():
    """Run the .req parser against mostly blank files."""
    req_parser = rp(tests.BLANK_REQ)
    assert tests.BLANK_REQ == req_parser.path

    _, body = req_parser.parse()
    assert tests.BLANK_REQ == req_parser.path
    assert 0 == len(body)


def test_inline_comments():
    """Run the parser against a case with inline comments next to PVs."""
    correct_pv_list = [
        rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, None),
        rp.REQ_PV("SR01C-DI-COL-01:GAP", None, None),
        rp.REQ_PV("SR01C-DI-COL-01:LEFT", None, None),
    ]

    req_parser = rp(tests.INLINE_COMMENTS_REQ)
    _, body = req_parser.parse()
    assert tests.INLINE_COMMENTS_REQ == req_parser.path
    assert 3 == len(body)
    assert correct_pv_list == body


@pytest.mark.parametrize(
    "filename",
    [
        tests.MALFORMED_REQ,
        tests.MALFORMED_SAVE_LEN_NEG_INT_REQ,
        tests.MALFORMED_SAVE_LEN_NON_INT_REQ,
    ],
)
def test_malformed_files(filename):
    """Run the parser against the malformed .req files."""
    with pytest.raises(ParserException):
        req_parser = rp(filename)
        req_parser.parse()


def test_req_parser_normal():
    """Run the .req parser against a basic case."""
    correct_pv_list = [
        rp.REQ_PV("SR01C-DI-COL-01:CENTRE", None, None),
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
        rp.REQ_PV("SR-CS-RING-01:MODE", None, None),
    ]

    req_parser = rp(tests.NORMAL_REQ)
    assert tests.NORMAL_REQ == req_parser.path

    _, body = req_parser.parse()
    assert tests.NORMAL_REQ == req_parser.path
    assert 12 == len(body)
    assert correct_pv_list == body
