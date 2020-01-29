"""Unit tests for the BURT restore functionality."""
import io

import cothread
import mock
import pytest
from cothread.catools import (
    DBR_CHAR,
    DBR_DOUBLE,
    DBR_ENUM,
    DBR_ENUM_STR,
    DBR_FLOAT,
    DBR_LONG,
    DBR_SHORT,
    DBR_STRING,
)

import burt
import test
from burt.parsers import ParserException, SnapParser
from burt.write import snap_entry_to_ca_type

INT_CHANNEL_TYPES = (DBR_SHORT, DBR_LONG)
STR_CHANNEL_TYPES = (DBR_CHAR, DBR_STRING, DBR_ENUM_STR, DBR_ENUM)


class MockCainfo:
    """Mock cainfo struct."""

    def __init__(self, datatype=None, ok=True):
        """Init constructor."""
        self.datatype = datatype
        self.ok = True


def mock_str_io(io_str):
    """Generate a mock io string for testing."""
    return io.StringIO(io_str)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_normal(mock_connect, mock_caput):
    """Run BURT restore against a normal case."""
    # ca_nothings have ok=True by default.
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")] * 4
    mock_connect.return_value = [
        MockCainfo(DBR_DOUBLE),
        MockCainfo(),
        MockCainfo(),
        MockCainfo(DBR_FLOAT),
    ]

    burt.restore(test.ARRAYS_AND_SCALARS_SNAP)
    args, _ = mock_caput.call_args_list[0]
    keys, values = args

    # Pick an integer value such as has caused problems with restoring
    # long PVs. This should now put a float.
    assert list(keys)[3] == "SR01C-DI-COL-02:POS2"
    assert list(values)[3] == 12.0


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_channel_types(mock_connect, mock_caput):
    """Run BURT restore against several channel types."""
    # ca_nothings have ok=True by default.
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")] * 4
    mock_channel_types = [MockCainfo()] * 4
    mock_connect.return_value = mock_channel_types

    # Note: in the ARRAYS_AND_SCALARS_SNAP snap file:
    # [0] is a float array = .259328000000000e+00 3.259328000000000e+00 ...
    # [1] is a float: -3.276854000000000e+00
    # Arrays are always coerced to float, so should not throw.
    for int_channel_type in INT_CHANNEL_TYPES:
        mock_channel_types[0] = MockCainfo(int_channel_type)
        burt.restore(test.ARRAYS_AND_SCALARS_SNAP)

    # Trying to convert float from an int channel type.
    for int_channel_type in INT_CHANNEL_TYPES:
        mock_channel_types[1] = MockCainfo(int_channel_type)
        with pytest.raises(ValueError):
            burt.restore(test.ARRAYS_AND_SCALARS_SNAP)

    # Trying to convert float from a string channel type.
    for str_channel_type in STR_CHANNEL_TYPES:
        mock_channel_types[1] = MockCainfo(str_channel_type)
        burt.restore(test.ARRAYS_AND_SCALARS_SNAP)

    # Enums: "lower voltage", NIL, etc.
    # Trying to convert an enum string from an int channel type.
    for int_channel_type in INT_CHANNEL_TYPES:
        mock_channel_types[0] = MockCainfo(int_channel_type)
        with pytest.raises(ValueError):
            burt.restore(test.ENUM_SNAP)
        mock_channel_types[1] = MockCainfo(int_channel_type)
        with pytest.raises(ValueError):
            burt.restore(test.ENUM_SNAP)
    for str_channel_type in STR_CHANNEL_TYPES:
        mock_channel_types[0] = MockCainfo(str_channel_type)
        mock_channel_types[1] = MockCainfo(str_channel_type)
        burt.restore(test.ENUM_SNAP)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_write_fail(mock_connect, mock_caput):
    """Run BURT restore against a write exception case."""
    mock_caput.side_effect = Exception

    # TODO: discuss if anything special needs to occur on write failure.
    # Probable solution is to not do anything.
    with pytest.raises(Exception):
        burt.restore(test.ARRAYS_AND_SCALARS_WITH_MODS_SNAP)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
@pytest.mark.parametrize(
    "snapfile",
    [
        test.MISSING_BOTTOM_HEADER_SNAP,
        test.MISSING_TOP_HEADER_SNAP,
        test.MISORDERED_BURT_HEADER_SNAP,
        test.DUPLICATE_BURT_HEADERS_SNAP,
        test.MALFORMED_HEADER_TYPO_SNAP,
        test.MALFORMED_BODY_SNAP,
        test.MALFORMED_HEADER_COLONS_SNAP,
    ],
)
def test_restore_bad_snap(mock_connect, mock_caput, snapfile):
    """Run BURT restore against some bad .snap files."""
    with pytest.raises(ParserException):
        burt.restore(snapfile)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_ok_snap(mock_connect, mock_caput):
    """Run BURT restore against ok .snap file."""
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")] * 2
    # Strange entries, but should not raise an exception.
    burt.restore(test.MALFORMED_HEADER_ENTRIES_SNAP)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_bad_file_arguments(mock_connect, mock_caput):
    """Run the burt script against a case where the file arguments are malformed."""
    with pytest.raises(ValueError):
        burt.restore("")
    with pytest.raises(ValueError):
        burt.restore("goodbyeworld")
    with pytest.raises(ValueError):
        burt.restore("helloworld.snap")
    with pytest.raises(ValueError):
        burt.restore_group("")
    with pytest.raises(ValueError):
        burt.restore_group("helloworld")
    with pytest.raises(ValueError):
        burt.restore_group("helloworld.snap")


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_returns_pv_names_if_caput_fails(mock_connect, mock_caput):
    """Checks that the caput error returns are caught as expected."""
    pvs_from_snap = [
        "SR01C-DI-COL-01:POS1",
        "SR01C-DI-COL-01:POS2",
        "SR01C-DI-COL-02:POS1",
        "SR01C-DI-COL-02:POS2",
    ]
    return_values = []
    for pv in pvs_from_snap:
        return_value = cothread.catools.ca_nothing(pv)
        return_value.ok = False
        return_value.errorcode = "dummy"
        return_values.append(return_value)
    mock_caput.return_value = return_values

    mock_connect.return_value = [MockCainfo()] * 4

    failed_pvs = burt.restore(test.ARRAYS_AND_SCALARS_SNAP)

    assert failed_pvs == pvs_from_snap


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_blank_restore(mock_connect, mock_caput):
    """Run burt restore against a blank .snap file."""
    with pytest.raises(ParserException):
        burt.restore(test.BLANK_SNAP)


@mock.patch("burt.write.caput")
@mock.patch("burt.write.connect")
def test_restore_group_normal(mock_connect, mock_caput):
    """Run BURT restore against a normal case."""
    # Just one caput of one PV expected.
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")]
    burt.restore_group(test.NORMAL_ALT_RGR, False)


@pytest.mark.parametrize(
    "entry,datatype,expected",
    [
        (SnapParser.SNAP_PV("a", 1, "2", ""), DBR_LONG, 2),
        (SnapParser.SNAP_PV("a", 1, "2", ""), DBR_FLOAT, 2.0),
        (SnapParser.SNAP_PV("a", 1, "2", ""), DBR_STRING, "2"),
        # Enums are parsed as strings.
        (SnapParser.SNAP_PV("a", 1, "2", ""), DBR_ENUM, "2"),
        # All arrays are parsed to floats.
        (SnapParser.SNAP_PV("a", 2, ["2", "3"], ""), DBR_STRING, [2, 3]),
    ],
)
def test_snap_entry_to_ca_type(entry, datatype, expected):
    """Test conversion of snap entries to specific datatypes."""
    assert snap_entry_to_ca_type(entry, datatype) == expected


@mock.patch("argparse.ArgumentParser")
@mock.patch("burt.utils.file.isfile")
@mock.patch("burt.write.restore")
def test_burt_write_cli_returns_1_if_restore_fails(
    mock_restore, mock_isfile, mock_argument_parser
):
    """Test burt.write.main() returns 1 for a snap file.

    Lots of mocking for this. Note the similarity to the test below.

    """
    mock_restore.return_value = ["FAILED-PV"]
    mock_isfile.return_value = True
    mock_args = mock.MagicMock()
    mock_args.restore_file = "hello.snap"
    mock_argument_parser.return_value.parse_args.return_value = mock_args
    with pytest.raises(SystemExit):
        burt.write.main()


@mock.patch("argparse.ArgumentParser")
@mock.patch("burt.write.is_rgr_file")
@mock.patch("burt.RgrParser")
@mock.patch("burt.write.restore")
def test_burt_write_cli_returns_1_if_restore_group_fails(
    mock_restore, mock_rgr_parser, mock_is_rgr_file, mock_argument_parser
):
    """Test burt.write.main() returns 1 for a snap file.

    Lots of mocking for this. We are checking that if restore() returns a PV
    then the CLI does report a failure.

    Note the similarity to the test above.

    """
    mock_restore.return_value = ["FAILED-PV"]
    mock_rgr_parser.return_value.parse.return_value = "dummy", ["hello.snap"]
    mock_is_rgr_file.return_value = True
    mock_args = mock.MagicMock()
    mock_args.restore_file = "hello.rgr"
    mock_argument_parser.return_value.parse_args.return_value = mock_args
    with pytest.raises(SystemExit):
        burt.write.main()


@mock.patch("argparse.ArgumentParser")
def test_burt_write_cli_returns_1_if_invalid_file(mock_argument_parser):
    """Test burt.write.main() returns 1 for an invalid file.

    Lots of mocking for this. Note the similarity to the test above.

    """
    mock_args = mock.MagicMock()
    mock_args.restore_file = "hello.dummy"
    mock_argument_parser.return_value.parse_args.return_value = mock_args
    with pytest.raises(SystemExit):
        burt.write.main()
