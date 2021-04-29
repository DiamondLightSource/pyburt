"""Various tests for the check file functionality."""
import mock
import pytest

import burt
from tests import paths
from tests.utils import aug_val


@pytest.mark.parametrize(
    "filename",
    ["", "helloworld.req", "helloworld.chk", "/tmp/no_such_folder/helloworld.check"],
)
def test_bad_file_arguments(filename):
    """Run the check against a case where the file arguments are malformed."""
    with pytest.raises(ValueError):
        burt.check(filename)


@mock.patch("burt.checks.caget")
def test_normal_check(mock_caget):
    """Run the check against a normal case with no failures."""
    # Zero tolerance
    mock_caget.return_value = [aug_val(10)]
    burt.check(paths.NORMAL_CHECK_1)

    # 1E-6 tolerance
    for vai in (0, 1e-6, 1e-7, -1e-7):
        mock_caget.return_value = [aug_val(0)]
        burt.check(paths.NORMAL_CHECK_3)


@mock.patch("burt.checks.caget")
def test_fail_check(mock_caget):
    """Run the check against failure cases."""
    # Zero tolerance
    for val in (9, 0, 11, 9.99, 10.01, -10):
        with pytest.raises(burt.CheckFailedException):
            mock_caget.return_value = [aug_val(val)]
            burt.check(paths.NORMAL_CHECK_1)
    # 1E-6 tolerance
    for val in (1, -1, 10, 1e-5, -1e-5):
        with pytest.raises(burt.CheckFailedException):
            mock_caget.return_value = [aug_val(val)]
            burt.check(paths.NORMAL_CHECK_3)


@mock.patch("burt.checks.caget")
def test_check_fails_if_ok_False(mock_caget):
    """Run the check and simulate caget returning .ok as False."""
    mock_caget.return_value = [aug_val(1, ok=False)]
    with pytest.raises(burt.CheckFailedException):
        burt.check(paths.NORMAL_CHECK_1)
