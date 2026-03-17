import numpy
from cothread.catools import (
    DBR_CHAR,
    DBR_DOUBLE,
    DBR_FLOAT,
    DBR_LONG,
    DBR_SHORT,
    DBR_STRING,
)


def aug_val(val, ok=True, count=1, dtype=DBR_FLOAT):
    """Create a dummy augmented value as returned by cothread.

    Note that an augmented value may have a shorter length
    than the length of the array that it came from, so count
    may not match len(val).

    Args:
        val: value to return
        ok: ok attribute of returned value
        count: length of simulated PV array
        dtype: cothread DBR type

    """

    # noqa D202  https://github.com/PyCQA/pydocstyle/pull/395
    class AugFloat(float):
        ok = True
        element_count = 1
        datatype = DBR_FLOAT

    class AugInt(int):
        ok = True
        element_count = 1
        datatype = DBR_LONG

    class AugStr(str):
        ok = True
        element_count = 1
        datatype = DBR_STRING

    class AugArray(numpy.ndarray):
        ok = True
        element_count = 1
        datatype = DBR_FLOAT

    if count > 1:
        if dtype in (DBR_STRING, DBR_CHAR):
            npdtype = object
        else:
            npdtype = numpy.float64
        f = AugArray([len(val)], dtype=npdtype)
        for i, v in enumerate(val):
            f[i] = v
    elif dtype in (DBR_DOUBLE, DBR_FLOAT):
        f = AugFloat(val)
    elif dtype in (DBR_SHORT, DBR_LONG):
        f = AugInt(val)
    elif dtype == DBR_STRING:
        f = AugStr(val)
    else:
        f = AugFloat(val)

    f.ok = ok
    f.element_count = count
    f.datatype = dtype

    return f
