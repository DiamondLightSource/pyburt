"""Various tests for the rqg parser."""

import pytest

import burt
from burt import RqgParser as rp
from burt.parsers import ParserError
from tests import paths


def test_base_case():
    """Run the .rqg parser against mostly blank files."""
    rgr_parser = burt.RgrParser(paths.BLANK_RQG)
    assert paths.BLANK_RQG == rgr_parser.path

    with pytest.raises(ParserError):
        rgr_parser.parse()


def test_inline_comments():
    """Run the rqg parser against a case with inline comments next to paths."""
    correct_checks = ["/home/ops/burt/checkFiles/tune-FFWD.check"]
    correct_reqs = [
        "/home/ops/burt/requestFiles/LI-RF.req",
        "/home/ops/burt/requestFiles/LI-TI.req",
        "/home/ops/burt/requestFiles/LB-PC.req",
        "/home/ops/burt/requestFiles/LB-DI.req",
        "/home/ops/burt/requestFiles/BR-DI.req",
        "/home/ops/burt/requestFiles/BR-RF.req",
        "/home/ops/burt/requestFiles/BR01C-TI.req",
        "/home/ops/burt/requestFiles/BR02C-TI.req",
        "/home/ops/burt/requestFiles/BR03C-TI.req",
        "/home/ops/burt/requestFiles/BR-PC.req",
        "/home/ops/burt/requestFiles/BR-MP.req",
    ]

    rqg_parser = rp(paths.INLINE_COMMENTS_RQG)
    _, body = rqg_parser.parse()
    assert paths.INLINE_COMMENTS_RQG == rqg_parser.path
    assert 12 == len(body)
    assert correct_checks == body[:1]
    assert correct_reqs == body[1:]


def test_malformed_files():
    """Run the .rqg parser against the malformed .rqg files."""
    with pytest.raises(ParserError):
        rqg_parser = burt.RqgParser(paths.MALFORMED_RQG)
        rqg_parser.parse()

    with pytest.raises(ParserError):
        rqg_parser = burt.RqgParser(paths.MALFORMED_MISORDERED_CHECKS_RQG)
        rqg_parser.parse()


def normal_case():
    """Run the rqg parser against a typical case."""
    correct_checks = [
        "/home/ops/burt/checkFiles/tune-FFWD.check",
        "/home/ops/burt/checkFiles/fastchic.check",
    ]
    correct_reqs = [
        "/home/ops/burt/requestFiles/LI-PC.req",
        "/home/ops/burt/requestFiles/LI-DI.req",
        "/home/ops/burt/requestFiles/LI-RF.req",
        "/home/ops/burt/requestFiles/LI-TI.req",
        "/home/ops/burt/requestFiles/LB-PC.req",
        "/home/ops/burt/requestFiles/LB-DI.req",
        "/home/ops/burt/requestFiles/BR-DI.req",
        "/home/ops/burt/requestFiles/BR-RF.req",
        "/home/ops/burt/requestFiles/BR01C-TI.req",
        "/home/ops/burt/requestFiles/BR02C-TI.req",
        "/home/ops/burt/requestFiles/BR03C-TI.req",
        "/home/ops/burt/requestFiles/BR-PC.req",
        "/home/ops/burt/requestFiles/BR-MP.req",
    ]

    rqg_parser = rp(paths.NORMAL_RQG)
    _, body = rqg_parser.parse()
    assert paths.NORMAL_RQG == rqg_parser.path
    assert 19 == len(body)
    assert correct_checks == body[:2]
    assert correct_reqs == body[2:]
