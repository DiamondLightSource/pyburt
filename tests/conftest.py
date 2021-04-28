"""Test fixtures."""
import os

import pytest

from tests import paths


@pytest.fixture
def pyburt_tmpfile(tmp_path):
    """Temporary file used by Pyburt."""
    pyburt_out = tmp_path / paths.PYBURT_OUT_FILE
    return pyburt_out


def pytest_sessionstart():
    """Set EPICS environment variables for Python code.

    Note that any soft IOCs use these variables at launch - see
    ioc_manager.py.

    """
    os.environ["EPICS_CA_SERVER_PORT"] = "7064"
    os.environ["EPICS_CA_REPEATER_PORT"] = "7065"
    os.environ["EPICS_CA_AUTO_ADDR_LIST"] = "NO"
    os.environ["EPICS_CA_ADDR_LIST"] = "localhost"
