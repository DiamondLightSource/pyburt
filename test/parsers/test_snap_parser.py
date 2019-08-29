""" Various tests for the snap parser."""
import pytest
import test
import burt
from burt import SnapParser as sp
from burt.parsers import ParserException


def test_base_case():
    """Runs the .snap parser against mostly blank files.
    """
    snap_parser = burt.SnapParser(test.BLANK_SNAP)
    assert test.BLANK_SNAP == snap_parser.path

    with pytest.raises(ParserException):
        snap_parser.parse()


def test_inline_comments():
    """Runs the snap parser against a case with inline comments next to PVs.
    """
    correct_pv_snapshots = [
        sp.SNAP_PV("SR01C-DI-COL-01:POS1", 1, ["3.259328000000000e+00"], None),
        sp.SNAP_PV("SR01C-DI-COL-01:POS2", 2, ["-3.276854000000000e+00", "333"], None),
        sp.SNAP_PV("SR01C-DI-COL-02:POS1", 1, ["-1.200000000000000e+01"], None),
        sp.SNAP_PV("SR01C-DI-COL-03:POS3", 1, ["666"], None),
    ]

    snap_parser = sp(test.INLINE_COMMENTS_SNAP)
    header, body = snap_parser.parse()
    assert test.INLINE_COMMENTS_SNAP == snap_parser.path
    assert 4 == len(body)
    assert "Tue Sep 21 15:07:59 2010" == header[sp.TIME_PREFIX]
    assert "ops-cc83 (Chris Christou)" == header[sp.LOGINID_PREFIX]
    assert "37245" == header[sp.UID_PREFIX]
    assert "37245" == header[sp.GROUPID_PREFIX]
    assert "hello world" == header[sp.KEYWORDS_PREFIX]
    assert (
        r"Nominal optics\nInjection efficiency with IDs closed to 5mm"
        r" is 80%\nResidual kick less than 1mm peak to"
        r" peak\nOnly changed injection magnets\nRF phasing 94/180"
        r" voltage 0.8/1.4" == header[sp.COMMENTS_PREFIX]
    )
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert "/home/ops/burt/backupFiles" == header[sp.DIRECTORY_PREFIX]
    assert "/home/ops/burt/requestFiles/SR-DI.req" == header[sp.REQ_FILE_PREFIX]
    assert correct_pv_snapshots == body


def test_malformed_files():
    """Runs the .snap parser against the malformed .snap files.
    """
    with pytest.raises(ParserException):
        snap_parser = sp(test.MISSING_BOTTOM_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MISSING_TOP_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MISORDERED_BURT_HEADER_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.DUPLICATE_BURT_HEADERS_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_HEADER_BURT_TYPO_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_HEADER_TYPO_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_BODY_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_HEADER_COLONS_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_FOOTER_PREFIX_SNAP)
        snap_parser.parse()

    with pytest.raises(ParserException):
        snap_parser = sp(test.MALFORMED_FOOTER_NON_INT_LENGTH_SNAP)
        snap_parser.parse()

    # Entries should still be parsed fine as header is valid, but values could
    # be problematic.
    snap_parser = sp(test.MALFORMED_HEADER_ENTRIES_SNAP)
    snap_parser.parse()


def test_snap_parser_scalars():
    """Runs the .snap parser against a basic case with only PV scalars.
    """
    correct_pv_snapshots = [
        sp.SNAP_PV("SR01C-DI-COL-01:POS1", 1, ["3.259328000000000e+00"], None),
        sp.SNAP_PV("SR01C-DI-COL-01:POS2", 1, ["-3.276854000000000e+00"], None),
        sp.SNAP_PV("SR01C-DI-COL-02:POS1", 1, ["-1.200000000000000e+01"], None),
        sp.SNAP_PV("SR01C-DI-COL-02:POS2", 1, ["1.200000000000000e+01"], None),
    ]

    snap_parser = sp(test.SCALARS_SNAP)
    header, body = snap_parser.parse()

    assert test.SCALARS_SNAP == snap_parser.path
    assert 4 == len(body)
    assert "Tue Sep 21 15:07:59 2010" == header[sp.TIME_PREFIX]
    assert "ops-cc83 (Chris Christou)" == header[sp.LOGINID_PREFIX]
    assert "37245" == header[sp.UID_PREFIX]
    assert "37245" == header[sp.GROUPID_PREFIX]
    assert "hello world" == header[sp.KEYWORDS_PREFIX]
    assert (
        r"Nominal optics\nInjection efficiency with IDs closed to 5mm"
        r" is 80%\nResidual kick less than 1mm peak to"
        r" peak\nOnly changed injection magnets\nRF phasing 94/180"
        r" voltage 0.8/1.4" == header[sp.COMMENTS_PREFIX]
    )
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert "/home/ops/burt/backupFiles" == header[sp.DIRECTORY_PREFIX]
    assert "/home/ops/burt/requestFiles/SR-DI.req" == header[sp.REQ_FILE_PREFIX]
    assert correct_pv_snapshots == body


def test_snap_parser_multiple_req_paths():
    """Runs the .snap parser against a case with multiple req paths in the header.
    """
    snap_parser = sp(test.MULTIPLE_REQ_PATHS_SNAP)
    header, body = snap_parser.parse()

    assert test.MULTIPLE_REQ_PATHS_SNAP == snap_parser.path
    assert [
        "/home/ops/burt/requestFiles/SR-DI.req",
        "/home/ops/burt/requestFiles/SR-DI2.req",
        "/home/ops/burt/requestFiles/SR-DI3.req",
        "/home/ops/burt/requestFiles/SR-DI4.req",
        "/home/ops/burt/requestFiles/SR-DI5.req",
    ] == header[sp.REQ_FILE_PREFIX]


def test_snap_parser_ca_arr():
    """Runs the .snap parser against a case with ca arrays.
    """
    correct_pv_snapshots = [
        sp.SNAP_PV(
            "SR01C-DI-COL-01:POS1",
            3,
            ["3.259328000000000e+00", "3.259328000000000e+00", "3.259328000000000e+00"],
            None,
        ),
        sp.SNAP_PV("SR01C-DI-COL-01:POS2", 1, ["-3.276854000000000e+00"], None),
        sp.SNAP_PV(
            "SR01C-DI-COL-02:POS1",
            2,
            ["-1.200000000000000e+01", "-1.200000000000000e+01"],
            None,
        ),
        sp.SNAP_PV("SR01C-DI-COL-02:POS2", 1, ["1.200000000000000e+01"], None),
    ]

    snap_parser = sp(test.ARRAYS_AND_SCALARS_SNAP)
    header, body = snap_parser.parse()

    assert test.ARRAYS_AND_SCALARS_SNAP == snap_parser.path
    assert 4 == len(body)
    assert "Tue Sep 21 15:07:59 2010" == header[sp.TIME_PREFIX]
    assert "ops-cc83 (Chris Christou)" == header[sp.LOGINID_PREFIX]
    assert "37245" == header[sp.UID_PREFIX]
    assert "37245" == header[sp.GROUPID_PREFIX]
    assert "hello world" == header[sp.KEYWORDS_PREFIX]
    assert (
        r"Nominal optics\nInjection efficiency with IDs closed to 5mm"
        r" is 80%\nResidual kick less than 1mm peak to"
        r" peak\nOnly changed injection magnets\nRF phasing 94/180"
        r" voltage 0.8/1.4" == header[sp.COMMENTS_PREFIX]
    )
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert "/home/ops/burt/backupFiles" == header[sp.DIRECTORY_PREFIX]
    assert "/home/ops/burt/requestFiles/SR-DI.req" == header[sp.REQ_FILE_PREFIX]
    assert correct_pv_snapshots == body


def test_snap_parser_with_modifiers():
    """Runs the .snap parser against a case with optional modifiers.
    """
    correct_pv_snapshots = [
        sp.SNAP_PV(
            "SR01C-DI-COL-01:POS1",
            3,
            ["3.259328000000000e+00", "3.259328000000000e+00", "3.259328000000000e+00"],
            "RO",
        ),
        sp.SNAP_PV("SR01C-DI-COL-01:POS2", 1, ["-3.276854000000000e+00"], "WO"),
        sp.SNAP_PV(
            "SR01C-DI-COL-02:POS1",
            2,
            ["-1.200000000000000e+01", "-1.200000000000000e+01"],
            None,
        ),
        sp.SNAP_PV("SR01C-DI-COL-02:POS2", 1, ["1.200000000000000e+01"], "RON"),
    ]

    snap_parser = sp(test.MODIFIERS_SNAP)
    header, body = snap_parser.parse()

    assert test.MODIFIERS_SNAP == snap_parser.path
    assert 4 == len(body)
    assert "Tue Sep 21 15:07:59 2010" == header[sp.TIME_PREFIX]
    assert "ops-cc83 (Chris Christou)" == header[sp.LOGINID_PREFIX]
    assert "37245" == header[sp.UID_PREFIX]
    assert "37245" == header[sp.GROUPID_PREFIX]
    assert "hello world" == header[sp.KEYWORDS_PREFIX]
    assert (
        r"Nominal optics\nInjection efficiency with IDs closed to 5mm"
        r" is 80%\nResidual kick less than 1mm peak to"
        r" peak\nOnly changed injection magnets\nRF phasing 94/180"
        r" voltage 0.8/1.4" == header[sp.COMMENTS_PREFIX]
    )
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert "/home/ops/burt/backupFiles" == header[sp.DIRECTORY_PREFIX]
    assert "/home/ops/burt/requestFiles/SR-DI.req" == header[sp.REQ_FILE_PREFIX]
    assert correct_pv_snapshots == body
