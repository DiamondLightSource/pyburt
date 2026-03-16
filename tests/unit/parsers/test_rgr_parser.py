"""Various tests for the rgr parser."""

import pytest

import burt
from burt import RgrParser as rp  # noqa: N813
from burt.parsers import ParserError
from tests import paths


def test_base_case():
    """Run the .rgr parser against mostly blank files."""
    rgr_parser = burt.RgrParser(paths.BLANK_RGR)
    assert paths.BLANK_RGR == rgr_parser.path

    with pytest.raises(ParserError):
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

    rgr_parser = rp(paths.INLINE_COMMENTS_RGR)
    header, body = rgr_parser.parse()
    assert paths.INLINE_COMMENTS_RGR == rgr_parser.path
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
        paths.MISSING_BOTTOM_HEADER_RGR,
        paths.MISSING_TOP_HEADER_RGR,
        paths.MISORDERED_HEADER_RGR,
        paths.DUPLICATE_HEADERS_RGR,
        paths.MALFORMED_HEADER_TYPO_RGR,
        paths.MALFORMED_HEADER_PREFIX_TYPO_RGR,
        paths.MALFORMED_BODY_RGR,
        paths.MALFORMED_BODY_MISORDERED_CHECKS_RGR,
    ],
)
def test_malformed_files(filename):
    """Run the .rgr parser against the malformed .snap files."""
    with pytest.raises(ParserError):
        rgr_parser = rp(filename)
        rgr_parser.parse()


def test_malformed_but_valid_file():
    """Run the .rgr parser against a malformed but valid file."""
    # Entries should still be parsed fine as header is valid, but values could
    # be problematic.
    rgr_parser = rp(paths.MALFORMED_HEADER_ENTRIES_RGR)
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

    rgr_parser = rp(paths.NORMAL_RGR)
    header, body = rgr_parser.parse()
    assert paths.INLINE_COMMENTS_RGR == rgr_parser.path
    assert "/home/ops/sample.rqg" == header[rp.RQG_PREFIX]
    assert (
        header["Comments"]
        == "LOCO applied for skews only, vertical emittance corrected to"
        " 8pm. Magnets not cycled yet."
    )
    assert 9 == len(body)
    assert correct_checks == body[:3]
    assert correct_snaps == body[3:]
