"""Various tests for the check file functionality."""
import cothread
import mock
import pytest

import burt
import test


@mock.patch("burt.checks.caget")
def test_bad_file_arguments(mock_caget):
    """Run the check against a case where the file arguments are malformed."""
    mock_caget.return_value = cothread.catools.ca_nothing

    with pytest.raises(ValueError):
        burt.check("")
    with pytest.raises(ValueError):
        burt.check("helloworld.req")
    with pytest.raises(ValueError):
        burt.check("helloworld.chk")
    with pytest.raises(ValueError):
        burt.check("/tmp/no_such_folder/helloworld.check")


@mock.patch("burt.checks.caget")
def test_normal_check(mock_caget):
    """Runs the check against a normal case with no failures."""
    # Zero tolerance
    mock_caget.return_value = [10]
    burt.check(test.NORMAL_CHECK_1)

    # 1E-6 tolerance
    mock_caget.return_value = [0]
    burt.check(test.NORMAL_CHECK_3)
    mock_caget.return_value = [1e-6]
    burt.check(test.NORMAL_CHECK_3)
    mock_caget.return_value = [1e-7]
    burt.check(test.NORMAL_CHECK_3)
    mock_caget.return_value = [-1e-7]
    burt.check(test.NORMAL_CHECK_3)


@mock.patch("burt.checks.caget")
def test_fail_check(mock_caget):
    """Runs the check against failure cases."""
    # Zero tolerance
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [9]
        burt.check(test.NORMAL_CHECK_1)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [0]
        burt.check(test.NORMAL_CHECK_1)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [11]
        burt.check(test.NORMAL_CHECK_1)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [9.99]
        burt.check(test.NORMAL_CHECK_1)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [10.01]
        burt.check(test.NORMAL_CHECK_1)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [-10]
        burt.check(test.NORMAL_CHECK_1)

    # 1E-6 tolerance
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [1]
        burt.check(test.NORMAL_CHECK_3)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [-1]
        burt.check(test.NORMAL_CHECK_3)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [10]
        burt.check(test.NORMAL_CHECK_3)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [1e-5]
        burt.check(test.NORMAL_CHECK_3)
    with pytest.raises(burt.CheckFailedException):
        mock_caget.return_value = [-1e-5]
        burt.check(test.NORMAL_CHECK_3)
