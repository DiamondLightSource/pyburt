""" Unit tests for the BURT restore functionality."""
import test
import pytest
import burt
import mock
import cothread
from burt.parsers import ParserException


@mock.patch("burt.write.caput")
def test_restore_normal(mock_caput):
    """ Runs BURT restore against a normal case.
    """
    # ca_nothings have ok=True by default.
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")] * 4
    burt.restore(test.ARRAYS_AND_SCALARS_SNAP)


@mock.patch("burt.write.caput")
def test_restore_write_fail(mock_caput):
    """ Runs BURT restore against a write exception case.
    """
    mock_caput.side_effect = Exception

    # TODO: discuss if anything special needs to occur on write failure.
    # Probable solution is to not do anything.
    with pytest.raises(Exception):
        burt.restore(test.ARRAYS_AND_SCALARS_WITH_MODS_SNAP)


@mock.patch("burt.write.caput")
def test_restore_bad_snap(mock_caput):
    """ Runs BURT restore against some bad .snap files.
    """

    with pytest.raises(ParserException):
        burt.restore(test.MISSING_BOTTOM_HEADER_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.MISSING_TOP_HEADER_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.MISORDERED_BURT_HEADER_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.DUPLICATE_BURT_HEADERS_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.MALFORMED_HEADER_TYPO_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.MALFORMED_BODY_SNAP)

    with pytest.raises(ParserException):
        burt.restore(test.MALFORMED_HEADER_COLONS_SNAP)

    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")] * 2
    # Strange entries, but should not raise an exception.
    burt.restore(test.MALFORMED_HEADER_ENTRIES_SNAP)


@mock.patch("burt.write.caput")
def test_bad_file_arguments(mock_caput):
    """Runs the burt script against a case where the file arguments are
    malformed.
    """
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
def test_restore_returns_pv_names_if_caput_fails(mock_caput):
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

    failed_pvs = burt.restore(test.ARRAYS_AND_SCALARS_SNAP)

    assert failed_pvs == pvs_from_snap


@mock.patch("burt.write.caput")
def test_blank_restore(mock_caput):
    """Runs burt restore against a blank .snap file.
    """
    with pytest.raises(ParserException):
        burt.restore(test.BLANK_SNAP)


@mock.patch("burt.write.caput")
def test_restore_group_normal(mock_caput):
    """ Runs BURT restore against a normal case.
    """
    # Just one caput of one PV expected.
    mock_caput.return_value = [cothread.catools.ca_nothing("dummy")]
    burt.restore_group(test.NORMAL_ALT_RGR, False)


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
