"""Test fixtures."""
import os

import pytest

import tests


@pytest.fixture
def burt_tmpfile():
    """Temporary file used by Burt."""
    yield tests.TMP_BURT_OUT
    try:
        os.remove(tests.TMP_BURT_OUT)
    except FileNotFoundError:
        pass


@pytest.fixture
def pyburt_tmpfile():
    """Temporary file used by Pyburt."""
    yield tests.TMP_PYBURT_OUT
    try:
        os.remove(tests.TMP_PYBURT_OUT)
    except FileNotFoundError:
        pass
