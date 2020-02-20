"""Various tests for the snap parser."""
import pytest

import burt
import test
from burt import SnapParser as sp
from burt.parsers import ParserException


def test_base_case():
    """Run the .snap parser against mostly blank files."""
    snap_parser = burt.SnapParser(test.BLANK_SNAP)
    assert test.BLANK_SNAP == snap_parser.path

    with pytest.raises(ParserException):
        snap_parser.parse()


def test_inline_comments():
    """Run the snap parser against a case with inline comments next to PVs."""
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


@pytest.mark.parametrize(
    "invalid_snap_file",
    [
        test.MISSING_BOTTOM_HEADER_SNAP,
        test.MISSING_TOP_HEADER_SNAP,
        test.MISORDERED_BURT_HEADER_SNAP,
        test.DUPLICATE_BURT_HEADERS_SNAP,
        test.MALFORMED_HEADER_BURT_TYPO_SNAP,
        test.MALFORMED_HEADER_TYPO_SNAP,
        test.MALFORMED_BODY_SNAP,
        test.MALFORMED_HEADER_COLONS_SNAP,
        test.MALFORMED_FOOTER_PREFIX_SNAP,
        test.MALFORMED_FOOTER_NON_INT_LENGTH_SNAP,
    ],
)
def test_malformed_snap_files(invalid_snap_file):
    """Run the .snap parser against the malformed .snap files."""
    with pytest.raises(ParserException):
        snap_parser = sp(invalid_snap_file)
        snap_parser.parse()


def test_acceptably_malformed_snap_file():
    """Run the .snap parser against a malformed .snap file that is still valid."""
    # Entries should still be parsed fine as header is valid, but values could
    # be problematic.
    snap_parser = sp(test.MALFORMED_HEADER_ENTRIES_SNAP)
    snap_parser.parse()


def test_snap_parser_scalars():
    """Run the .snap parser against a basic case with only PV scalars."""
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
    """Run the .snap parser against a case with multiple req paths in the header."""
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


@pytest.mark.parametrize(
    "line,length,parsed_value",
    [
        (
            "PV:NAME 3 3.259328000000000e+00 3.259328000000000e+00 3.259328000000000e+00",
            3,
            ["3.259328000000000e+00", "3.259328000000000e+00", "3.259328000000000e+00"],
        ),
        ("PV:NAME 1 -3.276854000000000e+00", 1, ["-3.276854000000000e+00"]),
    ],
)
def test_snap_parser_ca_arr(line, length, parsed_value):
    """Run the .snap parser against a case with ca arrays."""
    snap_parser = sp("file")
    snap_pv = snap_parser.read_body_line(line)
    assert snap_pv.name == "PV:NAME"
    assert snap_pv.dtype_len == length
    assert snap_pv.vals == parsed_value


@pytest.mark.parametrize(
    "line,parsed_value,modifier",
    [
        ("RO PV:NAME 1 NIL", ["NIL"], "RO"),
        ('WO PV:NAME 1 "lower voltage"', ["lower voltage"], "WO"),
        ('PV:NAME 1 "no voltage"', ["no voltage"], None),
        ("RON PV:NAME 1 1.200000000000000e+0", ["1.200000000000000e+0"], "RON"),
    ],
)
def test_snap_parser_with_modifiers(line, parsed_value, modifier):
    """Run the .snap parser against a case with optional modifiers."""
    snap_parser = sp("file")
    snap_pv = snap_parser.read_body_line(line)
    assert snap_pv.name == "PV:NAME"
    assert snap_pv.modifier == modifier
    assert snap_pv.vals == parsed_value


@pytest.mark.parametrize(
    "line,parsed_value",
    [
        ("PV:NAME 1 NIL", "NIL"),
        ('PV:NAME 1 "lower voltage"', "lower voltage"),
        ('PV:NAME 1 "no voltage"', "no voltage"),
        ('PV:NAME 1 "lower voltage no voltage"', "lower voltage no voltage"),
    ],
)
def test_snap_parser_enums(line, parsed_value):
    """Run the .snap parser against a case with enums."""
    parser = sp("file")
    snap_pv = parser.read_body_line(line)
    assert snap_pv.name == "PV:NAME"
    assert snap_pv.dtype_len == 1
    assert snap_pv.vals == [parsed_value]


@pytest.mark.parametrize(
    "line,parsed_value",
    [
        ("PV:NAME 1 a b", ["a", "b"]),
        ('PV:NAME 1 a "b c"', ["a", "b c"]),
        ("PV:NAME 1 a \\0", ["a", "\\0"]),
        ('PV:NAME 1 a "b c" \\0', ["a", "b c", "\\0"]),
    ],
)
def test_snap_parser_string_arrays(line, parsed_value):
    """Run the .snap parser against a case with enums."""
    parser = sp("file")
    snap_pv = parser.read_body_line(line)
    assert snap_pv.name == "PV:NAME"
    assert snap_pv.dtype_len == 1
    assert snap_pv.vals == parsed_value
