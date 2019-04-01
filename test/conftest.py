import sys
import types
import mock
import numpy


def pytest_sessionstart():
    """Create a dummy cothread module."""

    class ca_nothing(Exception):
        """A minimal mock of the cothread ca_nothing exception class."""

        def __init__(self, name, errorcode=True):
            self.ok = errorcode
            self.name = name

    class ca_array(numpy.ndarray):
        """A minimal mock of the cothread ca_array class."""
        pass

    class ca_str(str):
        """A minimal mock of the cothread ca_str class."""
        pass

    cothread = types.ModuleType('cothread')
    catools = types.ModuleType('catools')
    dbr = types.ModuleType('dbr')

    catools.caget = mock.MagicMock()
    catools.caput = mock.MagicMock()
    catools.ca_nothing = ca_nothing
    catools.DBR_ENUM_STR = mock.MagicMock()
    dbr.ca_array = ca_array
    dbr.ca_str = ca_str

    cothread.catools = catools
    cothread.dbr = dbr

    sys.modules['cothread'] = cothread
    sys.modules['cothread.catools'] = catools
