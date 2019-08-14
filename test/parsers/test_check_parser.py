""" Various tests for the check parser."""
import pytest
import test
from burt.parsers import ParserException
from burt import CheckParser as cp


def test_base_case():
    """Runs the .req parser against mostly blank files.
    """
    check_parser = cp(test.BLANK_REQ)
    assert test.BLANK_REQ == check_parser.path

    with pytest.raises(ParserException):
        check_parser.parse()


def test_multiline_comments():
    """Runs the parser against a case with multi line comments in the header.
    """
    correct_pv_list = [cp.CHECK_PV("SR-DI-EBPM-01:BCD_LIMIT", 20, 0)]

    check_parser = cp(test.MULTI_LINE_COMMENT_CHECK)
    with pytest.raises(ParserException):
        check_parser.parse()


def test_malformed_files():
    """Runs the parser against the malformed .check files.
    """
    with pytest.raises(ParserException):
        check_parser = cp(test.BAD_PREFIX_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(test.BAD_VALUES_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(test.EXCESS_VALUES_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(test.EXTRA_PREFIX_CHECK)
        check_parser.parse()

    with pytest.raises(ParserException):
        check_parser = cp(test.MISSING_TARGET_CHECK)
        check_parser.parse()


def test_non_floats():
    """Runs the parser against cases with non parseable numbers.
    """
    with pytest.raises(ParserException):
        check_parser = cp(test.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL a")

    with pytest.raises(ParserException):
        check_parser = cp(test.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL blabla dummy")

    with pytest.raises(ParserException):
        check_parser = cp(test.NORMAL_CHECK_1)
        check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL blabla dummy dummy2")

    # Should not throw an ex.
    check_parser = cp(test.NORMAL_CHECK_1)
    check_parser.read_body_line("SR-DI-DCCT-01:SIGNAL 0 1")


def test_check_parser_normal_1():
    """Runs the .check parser against a basic case.
    """
    correct_pv_list = [cp.CHECK_PV("SR-DI-DCCT-01:SIGNAL", 10, 0)]

    check_parser = cp(test.NORMAL_CHECK_1)
    assert test.NORMAL_CHECK_1 == check_parser.path

    header, body = check_parser.parse()
    assert "Beam current should be 10mA" == header[cp.COMMENTS_PREFIX]
    assert test.NORMAL_CHECK_1 == check_parser.path
    assert 1 == len(body)
    assert correct_pv_list == body


def test_check_parser_normal_2():
    """Runs the .check parser against a basic case.
    """
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

    check_parser = cp(test.NORMAL_CHECK_2)
    assert test.NORMAL_CHECK_2 == check_parser.path

    header, body = check_parser.parse()
    assert (
            "Aggregate to Set points for backup / zero set points for "
            "restore." == header[cp.COMMENTS_PREFIX]
    )
    assert test.NORMAL_CHECK_2 == check_parser.path
    assert 8 == len(body)
    assert correct_pv_list == body


def test_check_parser_normal_3():
    """Runs the .check parser against a basic case.
    """
    correct_pv_list = [
        cp.CHECK_PV("SR09A-PC-FCHIC-01:SETI", 0, 1e-6),
        cp.CHECK_PV("SR09A-PC-FCHIC-02:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-03:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-04:SETI", 0, 1e-6),
        cp.CHECK_PV("SR10S-PC-FCHIC-05:SETI", 0, 1e-6),
    ]

    check_parser = cp(test.NORMAL_CHECK_3)
    assert test.NORMAL_CHECK_3 == check_parser.path

    header, body = check_parser.parse()
    assert "check setpoints on fast chicane are zero." == header[cp.COMMENTS_PREFIX]
    assert test.NORMAL_CHECK_3 == check_parser.path
    assert 5 == len(body)
    assert correct_pv_list == body
