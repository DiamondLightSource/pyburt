"""Test fixtures."""
import os

import pytest

from tests import paths


@pytest.fixture
def burt_tmpfile():
    """Temporary file used by Burt."""
    yield paths.TMP_BURT_OUT
    try:
        os.remove(paths.TMP_BURT_OUT)
    except FileNotFoundError:
        pass


@pytest.fixture
def pyburt_tmpfile():
    """Temporary file used by Pyburt."""
    yield paths.TMP_PYBURT_OUT
    try:
        os.remove(paths.TMP_PYBURT_OUT)
    except FileNotFoundError:
        pass


def pytest_sessionstart():
    """Set EPICS environment variables for Python code.

    Note that any soft IOCs use these variables at launch - see
    ioc_manager.py.

    """
    os.environ["EPICS_CA_SERVER_PORT"] = "5064"
    os.environ["EPICS_CA_REPEATER_PORT"] = "5065"
    # os.environ["EPICS_CA_AUTO_ADDR_LIST"] = "NO"
    # os.environ["EPICS_CA_ADDR_LIST"] = "localhost"
