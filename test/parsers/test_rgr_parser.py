""" Various tests for the rgr parser."""
import pytest
import test
import burt
from burt.parsers import ParserException


def test_base_case():
    """Runs the .rgr parser against mostly blank files.
    """
    rgr_parser = burt.RgrParser(test.BLANK_RGR)
    assert test.BLANK_RGR == rgr_parser.path
    assert "" == rgr_parser.comments
    assert not rgr_parser.snaps
    assert not rgr_parser.checks

    with pytest.raises(ParserException):
        rgr_parser.parse()


def test_inline_comments():
    """Runs the rgr parser against a case with inline comments next to paths.
    """

    correct_checks = ["/home/ops/burt/checkFiles/tune-FFWD.check",
                      "/home/ops/burt/checkFiles/fastchic.check",
                      "/home/ops/burt/checkFiles/misc.check"]

    correct_snaps = [
        "/home/ops/burt/backupFiles/SR01A-TI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/BS-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-DI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR02A-PC-DDBA/SR-rtf26_190226_164119.snap"]

    rgr_parser = burt.RgrParser(test.INLINE_COMMENTS_RGR)
    rgr_parser.parse()
    assert test.INLINE_COMMENTS_RGR == rgr_parser.path
    assert rgr_parser.comments == \
           "LOCO applied for skews only, vertical emittance corrected to" \
           " 8pm. Magnets not cycled yet."
    assert 3 == len(rgr_parser.checks)
    assert 6 == len(rgr_parser.snaps)
    assert correct_checks == rgr_parser.checks
    assert correct_snaps == rgr_parser.snaps


def test_malformed_files():
    """Runs the .rgr parser against the malformed .snap files.
    """
    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MISSING_BOTTOM_HEADER_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MISSING_TOP_HEADER_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MISORDERED_HEADER_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.ONLY_HEADER_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.DUPLICATE_HEADERS_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MALFORMED_HEADER_TYPO_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MALFORMED_HEADER_PREFIX_TYPO_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MALFORMED_BODY_RGR)
        rgr_parser.parse()

    with pytest.raises(ParserException):
        rgr_parser = burt.RgrParser(test.MALFORMED_HEADER_COLONS_RGR)
        rgr_parser.parse()

    # Entries should still be parsed fine as header is valid, but values could
    # be problematic.
    rgr_parser = burt.RgrParser(test.MALFORMED_HEADER_ENTRIES_RGR)
    rgr_parser.parse()


def normal_case():
    """Runs the rgr parser against a typical case.
    """

    correct_checks = ["/home/ops/burt/checkFiles/tune-FFWD.check",
                      "/home/ops/burt/checkFiles/fastchic.check",
                      "/home/ops/burt/checkFiles/misc.check"]

    correct_snaps = [
        "/home/ops/burt/backupFiles/SR-MP/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-MP-DDBA/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-TI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/BS-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-DI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR02A-PC-DDBA/SR-rtf26_190226_164119.snap"]

    rgr_parser = burt.RgrParser(test.NORMAL_RGR)
    rgr_parser.parse()
    assert test.INLINE_COMMENTS_RGR == rgr_parser.path
    assert rgr_parser.comments == \
           "LOCO applied for skews only, vertical emittance corrected to" \
           " 8pm. Magnets not cycled yet."
    assert 3 == len(rgr_parser.checks)
    assert 8 == len(rgr_parser.snaps)
    assert correct_checks == rgr_parser.checks
    assert correct_snaps == rgr_parser.snaps
