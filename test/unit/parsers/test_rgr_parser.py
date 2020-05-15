"""Various tests for the rgr parser."""
import pytest

import burt
import test
from burt import RgrParser as rp
from burt.parsers import ParserException


def test_base_case():
    """Run the .rgr parser against mostly blank files."""
    rgr_parser = burt.RgrParser(test.BLANK_RGR)
    assert test.BLANK_RGR == rgr_parser.path

    with pytest.raises(ParserException):
        rgr_parser.parse()


def test_inline_comments():
    """Run the rgr parser against a case with inline comments next to paths."""
    correct_checks = [
        "/home/ops/burt/checkFiles/tune-FFWD.check",
        "/home/ops/burt/checkFiles/fastchic.check",
        "/home/ops/burt/checkFiles/misc.check",
    ]
    correct_snaps = [
        "/home/ops/burt/backupFiles/SR01A-TI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/BS-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-DI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR02A-PC-DDBA/SR-rtf26_190226_164119.snap",
    ]

    rgr_parser = rp(test.INLINE_COMMENTS_RGR)
    header, body = rgr_parser.parse()
    assert test.INLINE_COMMENTS_RGR == rgr_parser.path
    assert "/home/ops/sample.rqg" == header[rp.RQG_PREFIX]
    assert (
        header["Comments"]
        == "LOCO applied for skews only, vertical emittance corrected to"
        " 8pm. Magnets not cycled yet."
    )
    assert 9 == len(body)
    assert correct_checks == body[:3]
    assert correct_snaps == body[3:]


@pytest.mark.parametrize(
    "filename",
    [
        test.MISSING_BOTTOM_HEADER_RGR,
        test.MISSING_TOP_HEADER_RGR,
        test.MISORDERED_HEADER_RGR,
        test.DUPLICATE_HEADERS_RGR,
        test.MALFORMED_HEADER_TYPO_RGR,
        test.MALFORMED_HEADER_PREFIX_TYPO_RGR,
        test.MALFORMED_BODY_RGR,
        test.MALFORMED_BODY_MISORDERED_CHECKS_RGR,
    ],
)
def test_malformed_files(filename):
    """Run the .rgr parser against the malformed .snap files."""
    with pytest.raises(ParserException):
        rgr_parser = rp(filename)
        rgr_parser.parse()


def test_malformed_but_valid_file():
    """Run the .rgr parser against a malformed but valid file."""
    # Entries should still be parsed fine as header is valid, but values could
    # be problematic.
    rgr_parser = rp(test.MALFORMED_HEADER_ENTRIES_RGR)
    rgr_parser.parse()


def normal_case():
    """Run the rgr parser against a typical case."""
    correct_checks = [
        "/home/ops/burt/checkFiles/tune-FFWD.check",
        "/home/ops/burt/checkFiles/fastchic.check",
        "/home/ops/burt/checkFiles/misc.check",
    ]

    correct_snaps = [
        "/home/ops/burt/backupFiles/SR-MP/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-MP-DDBA/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-TI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/BS-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR-DI/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR01A-PC/SR-rtf26_190226_164119.snap",
        "/home/ops/burt/backupFiles/SR02A-PC-DDBA/SR-rtf26_190226_164119.snap",
    ]

    rgr_parser = rp(test.NORMAL_RGR)
    header, body = rgr_parser.parse()
    assert test.INLINE_COMMENTS_RGR == rgr_parser.path
    assert "/home/ops/sample.rqg" == header[rp.RQG_PREFIX]
    assert (
        header["Comments"]
        == "LOCO applied for skews only, vertical emittance corrected to"
        " 8pm. Magnets not cycled yet."
    )
    assert 9 == len(body)
    assert correct_checks == body[:3]
    assert correct_snaps == body[3:]
