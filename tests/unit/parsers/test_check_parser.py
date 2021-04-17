"""Various tests for the check parser."""
import pytest

from tests import paths
from burt import CheckParser as cp
from burt.parsers import ParserException


def test_base_case():
    """Run the .req parser against mostly blank files."""
    check_parser = cp(paths.BLANK_REQ)
    assert paths.BLANK_REQ == check_parser.path

    with pytest.raises(ParserException):
        check_parser.parse()


def test_multiline_comments():
    """Run the parser against a case with multi line comments in the header."""
    check_parser = cp(paths.MULTI_LINE_COMMENT_CHECK)
    with pytest.raises(ParserException):
        check_parser.parse()


def test_malformed_files():
    """Run the parser against the malformed .check files."""
    with pytest.raises(ParserException):
        check_parser = cp(paths.BAD_PREFIX_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(paths.BAD_VALUES_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(paths.EXCESS_VALUES_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(paths.EXTRA_PREFIX_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(paths.MISSING_TARGET_CHECK)
        check_parser.parse()


def test_non_floats():
    """Run the parser against cases with non parseable numbers."""
    with pytest.raises(ParserException):
        check_parser = cp(paths.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL a")

    with pytest.raises(ParserException):
        check_parser = cp(paths.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL blabla dummy")

    with pytest.raises(ParserException):
        check_parser = cp(paths.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL blabla dummy dummy2")

    # Should not throw an ex.
    check_parser = cp(paths.NORMAL_CHECK_1)
    check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL 0 1")


def test_check_parser_normal_1():
    """Run the .check parser against a basic case."""
    correct_pv_list = [cp.CHECK_PV("SR-DI-DCCT-01:SIGNAL", 10, 0)]

    check_parser = cp(paths.NORMAL_CHECK_1)
    assert paths.NORMAL_CHECK_1 == check_parser.path

    header, body = check_parser.parse()
    assert "Beam current should be 10mA" == header[cp.COMMENTS_PREFIX]
    assert paths.NORMAL_CHECK_1 == check_parser.path
    assert 1 == len(body)
    assert correct_pv_list == body


def test_check_parser_normal_2():
    """Run the .check parser against a basic case."""
    correct_pv_list = [
        cp.CHECK_PV("SR01A-PC-Q1D-01:OFFSET1.VAL", 0, 0),
        cp.CHECK_PV("SR01A-PC-Q2D-02:OFFSET1.VAL", 2, 1),
        cp.CHECK_PV("SR01A-PC-Q3D-03:OFFSET1.VAL", 1, 5),
        cp.CHECK_PV("SR01A-PC-Q3B-08:OFFSET1.VAL", 1, 4),
        cp.CHECK_PV("SR01A-PC-Q2B-09:OFFSET1.VAL", 2, 3),
        cp.CHECK_PV("SR01A-PC-Q1B-10:OFFSET1.VAL", 6, 0),
        cp.CHECK_PV("SR03A-PC-Q1B-01:OFFSET1.VAL", 5, 2),
        cp.CHECK_PV("SR03A-PC-Q2B-02:OFFSET1.VAL", 0, 0),
    ]

    check_parser = cp(paths.NORMAL_CHECK_2)
    assert paths.NORMAL_CHECK_2 == check_parser.path

    header, body = check_parser.parse()
    assert (
        "Aggregate to Set points for backup / zero set points for "
        "restore." == header[cp.COMMENTS_PREFIX]
    )
    assert paths.NORMAL_CHECK_2 == check_parser.path
    assert 8 == len(body)
    assert correct_pv_list == body


def test_check_parser_normal_3():
    """Run the .check parser against a basic case."""
    correct_pv_list = [
        cp.CHECK_PV("SR09A-PC-FCHIC-01:SETI", 0, 1e-6),
        cp.CHECK_PV("SR09A-PC-FCHIC-02:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-03:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-04:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-05:SETI", 0, 1e-6),
    ]

    check_parser = cp(paths.NORMAL_CHECK_3)
    assert paths.NORMAL_CHECK_3 == check_parser.path

    header, body = check_parser.parse()
    assert "check setpoints on fast chicane are zero." == header[cp.COMMENTS_PREFIX]
    assert paths.NORMAL_CHECK_3 == check_parser.path
    assert 5 == len(body)
    assert correct_pv_list == body
