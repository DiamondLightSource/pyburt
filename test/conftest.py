import test

import pytest

import os


@pytest.fixture
def burt_tmpfile():
    """Temporary file used by Burt."""
    yield test.TMP_BURT_OUT
    try:
        os.remove(test.TMP_BURT_OUT)
    except FileNotFoundError:
        pass


@pytest.fixture
def pyburt_tmpfile():
    """Temporary file used by Pyburt."""
    yield test.TMP_PYBURT_OUT
    try:
        os.remove(test.TMP_PYBURT_OUT)
    except FileNotFoundError:
        pass
