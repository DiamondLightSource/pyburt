"""Various tests for the main burt module."""
import os

import cothread
import mock
import numpy
import pytest
from cothread.catools import (
    DBR_CHAR,
    DBR_DOUBLE,
    DBR_FLOAT,
    DBR_LONG,
    DBR_SHORT,
    DBR_STRING,
)

import burt
import test
from burt import SnapParser as sp
from burt.read import _flatten_ca_array, _format_ca_reading
from test import aug_val


@mock.patch("burt.read.caget")
def test_blank_snapshot(mock_caget, pyburt_tmpfile):
    """Run the burt snapshot against a blank .req file."""
    mock_caget.return_value = aug_val([0, 0, 0], count=3)

    burt.take_snapshot([test.BLANK_REQ], pyburt_tmpfile)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0


@mock.patch("burt.read.caget")
def test_bad_file_arguments(mock_caget):
    """Run the burt script against a case where the file arguments are malformed."""
    mock_caget.return_value = cothread.catools.ca_nothing
    mock_caget.return_value.ok = False
    mock_caget.return_value.errorcode = "Dummy"

    with pytest.raises(ValueError):
        burt.take_snapshot([""], "")
    with pytest.raises(ValueError):
        burt.take_snapshot(["goodbyeworld"], "helloworld")
    with pytest.raises(ValueError):
        burt.take_snapshot(["goodbyeworld.req"], "helloworld.snap")
    with pytest.raises(ValueError):
        burt.take_snapshot([], "helloworld.snap")
    with pytest.raises(ValueError):
        burt.take_snapshot([test.BLANK_REQ], "helloworld.txt")

    # take_snapshot_group() not currently implemented
    with pytest.raises(NotImplementedError):
        burt.take_snapshot_group(test.BLANK_REQ, "helloworld.snap")
    with pytest.raises(NotImplementedError):
        burt.take_snapshot_group("dummy.rqg", "helloworld.snap")
    with pytest.raises(NotImplementedError):
        burt.take_snapshot_group(test.NORMAL_RQG, "helloworld.sn")


@pytest.mark.parametrize(
    "ca_reading,ca_type,expected_str",
    (
        (0, DBR_CHAR, "\x00"),
        (80, DBR_CHAR, "P"),
        (6666666, DBR_CHAR, "6666666"),  # non existent char code, falls back to str
        ("Dummy", DBR_STRING, "Dummy"),
        ("Dummy Space Word", DBR_STRING, '"Dummy Space Word"'),
        ("", DBR_STRING, "\\0"),
        (123, DBR_SHORT, "123"),
        (123456789, DBR_LONG, "123456789"),
        (1, DBR_FLOAT, "1.000000e+00"),
        (-6.67e7, DBR_FLOAT, "-6.670000e+07"),
        (1, DBR_DOUBLE, "1.000000000000000e+00"),
        (-6.67e13, DBR_DOUBLE, "-6.670000000000000e+13"),
    ),
)
def test_ca_types_snap_formatting(ca_reading, ca_type, expected_str):
    """Check the ca readings are formatted as expected."""
    assert _format_ca_reading(ca_reading, ca_type) == expected_str


@pytest.mark.parametrize(
    "vals,datatype,array_length,requested_length,output",
    [
        ([1, 2], DBR_FLOAT, 2, 2, "1.000000e+00 2.000000e+00"),
        ([1, 2], DBR_FLOAT, 3, 2, "1.000000e+00 2.000000e+00 0.000000e+00"),
        ([1, 2], DBR_DOUBLE, 2, 2, "1.000000000000000e+00 2.000000000000000e+00"),
        ([1], DBR_DOUBLE, 2, 2, "1.000000000000000e+00 0.000000000000000e+00"),
        ([1, 2], DBR_SHORT, 2, 2, "1 2"),
        ([1, 2], DBR_SHORT, 3, 2, "1 2 \\0"),
        ([], DBR_SHORT, 2, 2, "\\0 \\0"),
        ([1, 2], DBR_LONG, 2, 2, "1 2"),
        ([1, 2], DBR_LONG, 3, 2, "1 2 \\0"),
        ([], DBR_LONG, 2, 2, "\\0 \\0"),
        (["a", "b"], DBR_STRING, 2, 2, "a b"),
        (["a", "b"], DBR_STRING, 3, 2, "a b \\0"),
        (["a b", "c d"], DBR_STRING, 2, 2, '"a b" "c d"'),
        (["a b", "c d"], DBR_STRING, 3, 2, '"a b" "c d" \\0'),
        ([97, 98], DBR_CHAR, 2, 2, "a b"),
        ([97, 98], DBR_CHAR, 3, 2, "a b \\0"),
    ],
)
def test_flatten_ca_array(vals, datatype, array_length, requested_length, output):
    """Check formatting arrays for snap files."""
    ca_reading = aug_val(vals, count=array_length, dtype=datatype)
    assert _flatten_ca_array(ca_reading, requested_length) == output


@mock.patch("burt.read.caget")
@mock.patch("burt.read._get_snap_header_system_vals")
def test_simple_snapshot(mock_get_vals, mock_caget, pyburt_tmpfile):
    """Run a simple snapshot."""
    array_return_value = aug_val([1, 2], count=2, dtype=DBR_DOUBLE)
    mock_caget.return_value = [array_return_value]
    mock_get_vals.return_value = ("user", "time", "dir", "group", 100)

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)
    with open(pyburt_tmpfile) as f1:
        with open(test.SIMPLE_SNAP) as f2:
            assert f1.read() == f2.read()


def test_burtinter_req_file_prefix_compatability():
    """Test the header logic from the old burtinter."""
    test_pyburt_header_1 = burt.read._gen_snap_header(
        ["/home/DUMMY.req"], "dummy", "dummy"
    )
    test_pyburt_header_2 = burt.read._gen_snap_header(
        ["/home/DUMMY.req", "/home/DUMMY2.req", "/home/DUMMY3.req"], "dummy", "dummy"
    )

    bad_req_entry_1 = "Req File:  /home/space.req"
    bad_req_entry_2 = "Req File:                  /home/space.req"
    ok_req_entry = "Req File: /home/onespaceonly.req"

    # Req file prefix entry is in the second to last line.
    req_file_prefix_entries = [
        header.split("\n")[-2]
        for header in (test_pyburt_header_1, test_pyburt_header_2)
    ]

    for req_file_prefix_entry in req_file_prefix_entries:
        try:
            _old_req_file_header_burtinter_code(req_file_prefix_entry)
        except IndexError:
            pytest.fail(
                "Old burtinter code detected more than one space in req "
                f"prefix: {req_file_prefix_entry}"
            )

    try:
        _old_req_file_header_burtinter_code(bad_req_entry_1)
        pytest.fail(
            "This test should throw as old burtinter cannot handle more than "
            "one space."
        )
    except IndexError:
        # Expected.
        pass

    try:
        _old_req_file_header_burtinter_code(bad_req_entry_2)
        pytest.fail(
            "This test should throw as old burtinter cannot handle more than "
            "one space."
        )
    except IndexError:
        # Expected.
        pass

    try:
        _old_req_file_header_burtinter_code(ok_req_entry)
    except IndexError:
        pytest.fail("This test should not throw as old burtinter expects one space")


@mock.patch("burt.read.caget")
def test_snapshot_arrays(mock_caget, pyburt_tmpfile):
    """Run a take snapshot test of a normal .req file."""
    # Caget return value is a 12 element list of arrays of 40 elements.
    array_return_value = aug_val([0] * 40, count=40, dtype=DBR_SHORT)
    mock_caget.return_value = [array_return_value for i in range(12)]

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 12 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert header[sp.KEYWORDS_PREFIX]
    assert header[sp.COMMENTS_PREFIX]
    assert header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert test.NORMAL_REQ == header[sp.REQ_FILE_PREFIX]

    assert body[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[0].vals) == 40
    assert body[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[1].vals) == 40
    assert body[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(body[2].vals) == 40
    assert body[3].name == "SR01C-DI-COL-02:GAP"
    assert len(body[3].vals) == 40

    # These PVs have a set save value in the .req file, and the last two have
    # readonly modifiers
    assert body[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[4].vals) == 5
    assert body[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[5].vals) == 10
    assert body[5].modifier == "RO"
    assert body[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[6].vals) == 25
    assert body[6].modifier == "RON"

    # Some readonly modifiers here.
    assert body[7].name == "SR01C-DI-COL-01:POS1"
    assert len(body[7].vals) == 40
    assert body[7].modifier == "RON"
    assert body[8].name == "SR01C-DI-COL-01:POS2"
    assert len(body[8].vals) == 40
    assert body[8].modifier == "RO"
    assert body[9].name == "SR01C-DI-COL-02:POS1"
    assert len(body[9].vals) == 40
    assert body[9].modifier == "RO"
    assert body[10].name == "SR01C-DI-COL-02:POS2"
    assert len(body[10].vals) == 40
    assert body[10].modifier == "RO"
    assert body[11].name == "SR-CS-RING-01:MODE"
    assert len(body[11].vals) == 40


@mock.patch("burt.read.caget")
def test_snapshot_enum(mock_caget, pyburt_tmpfile):
    """Run a take snapshot test of a normal .req file.

    Including a mocked enum, with spaces.
    """
    singleton_return_value = cothread.dbr.ca_str("DIAD")
    singleton_return_value.ok = True
    singleton_return_value.element_count = 1
    singleton_return_value.datatype = DBR_STRING
    mock_caget.return_value = [singleton_return_value for i in range(12)]
    mock_caget.return_value[1] = cothread.dbr.ca_str(".5 fill")
    mock_caget.return_value[1].ok = True
    mock_caget.return_value[1].datatype = DBR_STRING
    mock_caget.return_value[1].element_count = 1
    mock_caget.return_value[2] = cothread.dbr.ca_str("stop filling start beam")
    mock_caget.return_value[2].ok = True
    mock_caget.return_value[2].datatype = DBR_STRING
    mock_caget.return_value[2].element_count = 1

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 12 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert test.NORMAL_REQ == header[sp.REQ_FILE_PREFIX]

    assert body[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[0].vals) == 1
    assert body[0].vals[0] == "DIAD"
    assert body[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[1].vals) == 1
    assert body[1].vals[0] == ".5 fill"
    assert body[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(body[2].vals) == 1
    assert body[2].vals[0] == "stop filling start beam"


@mock.patch("burt.read.caget")
def test_snapshot_scalar(mock_caget, pyburt_tmpfile):
    """Runs a take snapshot test of a normal .req file with a mocked scalar.

    Note that cothread will always return an augmented non scalar value.
    """
    singleton_return_value = test.aug_val(-1e-16)
    mock_caget.return_value = [singleton_return_value for i in range(12)]

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 12 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert test.NORMAL_REQ == header[sp.REQ_FILE_PREFIX]

    assert body[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[0].vals) == 1
    assert body[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[1].vals) == 1
    assert body[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(body[2].vals) == 1
    assert body[3].name == "SR01C-DI-COL-02:GAP"
    assert len(body[3].vals) == 1
    assert body[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[4].vals) == 1
    assert body[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[5].vals) == 1
    assert body[5].modifier == "RO"
    assert body[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[6].vals) == 1
    assert body[6].modifier == "RON"
    assert body[7].name == "SR01C-DI-COL-01:POS1"
    assert len(body[7].vals) == 1
    assert body[7].modifier == "RON"
    assert body[8].name == "SR01C-DI-COL-01:POS2"
    assert len(body[8].vals) == 1
    assert body[8].modifier == "RO"
    assert body[9].name == "SR01C-DI-COL-02:POS1"
    assert len(body[9].vals) == 1
    assert body[9].modifier == "RO"
    assert body[10].name == "SR01C-DI-COL-02:POS2"
    assert len(body[10].vals) == 1
    assert body[10].modifier == "RO"
    assert body[11].name == "SR-CS-RING-01:MODE"
    assert len(body[11].vals) == 1


@mock.patch("burt.read.caget")
def test_snapshot_scalar_failed_pvs_ret(mock_caget, pyburt_tmpfile):
    """Run a take snapshot test of a normal .req file with a mocked scalar.

    Test the failed values for validity.
    """
    singleton_return_value = aug_val("DIAD", dtype=DBR_STRING)
    mock_caget.return_value = [singleton_return_value for i in range(12)]

    # Every PV will fail in test.NORMAL_REQ.
    for mocked in mock_caget.return_value:
        mocked.ok = False
        mocked.errorcode = "Hello Goodbye World!"

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    expected_failed_pvs = [
        "SR01C-DI-COL-01:CENTRE",
        "SR-DI-PICO-01:BUCKETS",
        "SR01C-DI-COL-02:CENTRE",
        "SR01C-DI-COL-02:GAP",
        "SR-DI-PICO-01:BUCKETS",
        "SR-DI-PICO-01:BUCKETS",
        "SR-DI-PICO-01:BUCKETS",
        "SR01C-DI-COL-01:POS1",
        "SR01C-DI-COL-01:POS2",
        "SR01C-DI-COL-02:POS1",
        "SR01C-DI-COL-02:POS2",
        "SR-CS-RING-01:MODE",
    ]

    failed_pvs = burt.take_snapshot(
        [test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords
    )

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0
    assert failed_pvs == expected_failed_pvs

    # cleanup
    os.remove(pyburt_tmpfile)


@mock.patch("burt.read.caget")
def test_snapshot_multiple_reqs(mock_caget, pyburt_tmpfile):
    """Run a take snapshot test of a .req file with multiple req paths."""
    singleton_return_value = test.aug_val(-1e-16)
    mock_caget.return_value = [singleton_return_value for i in range(12)]

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(
        [test.NORMAL_REQ, test.INLINE_COMMENTS_REQ, test.BLANK_REQ],
        pyburt_tmpfile,
        test_comment,
        test_keywords,
    )

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(pyburt_tmpfile)
    header, body = snap_parser.parse()
    assert 15 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert test_keywords == header[sp.KEYWORDS_PREFIX]
    assert test_comment == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert [test.NORMAL_REQ, test.INLINE_COMMENTS_REQ, test.BLANK_REQ] == header[
        sp.REQ_FILE_PREFIX
    ]

    # Req file 1 body
    assert body[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[0].vals) == 1
    assert body[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[1].vals) == 1
    assert body[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(body[2].vals) == 1
    assert body[3].name == "SR01C-DI-COL-02:GAP"
    assert len(body[3].vals) == 1
    assert body[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[4].vals) == 1
    assert body[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[5].vals) == 1
    assert body[5].modifier == "RO"
    assert body[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[6].vals) == 1
    assert body[6].modifier == "RON"
    assert body[7].name == "SR01C-DI-COL-01:POS1"
    assert len(body[7].vals) == 1
    assert body[7].modifier == "RON"
    assert body[8].name == "SR01C-DI-COL-01:POS2"
    assert len(body[8].vals) == 1
    assert body[8].modifier == "RO"
    assert body[9].name == "SR01C-DI-COL-02:POS1"
    assert len(body[9].vals) == 1
    assert body[9].modifier == "RO"
    assert body[10].name == "SR01C-DI-COL-02:POS2"
    assert len(body[10].vals) == 1
    assert body[10].modifier == "RO"
    assert body[11].name == "SR-CS-RING-01:MODE"
    assert len(body[11].vals) == 1

    # Req file 2 body
    assert body[12].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[12].vals) == 1
    assert body[13].name == "SR01C-DI-COL-01:GAP"
    assert len(body[13].vals) == 1
    assert body[14].name == "SR01C-DI-COL-01:LEFT"
    assert len(body[14].vals) == 1

    # Third req file is empty.


@mock.patch("burt.read.caget")
def test_snapshot_newlines_in_args(mock_caget, pyburt_tmpfile):
    """Run a take snapshot test with newlines in user supplied meta data.

    The newlines should appear as is in the .snap file,
    with the help of an extra backslash, and not interpreted.
    """
    # caget return value a 12 element list of arrays of 40 elements.
    array_return_value = aug_val([0] * 40, ok=False, count=40)
    mock_caget.return_value = [array_return_value for i in range(12)]

    test_comment = "\nHello\r\n \nWorld\r\n\r"
    test_keywords = "\r\ncool\n,\r\nsnap,file\n\r\r"

    expected_snap_comment = "\\nHello\\r\\n \\nWorld\\r\\n\\r"
    expected_snap_keywords = "\\r\\ncool\\n,\\r\\nsnap,file\\n\\r\\r"

    burt.take_snapshot([test.NORMAL_REQ], pyburt_tmpfile, test_comment, test_keywords)

    assert os.path.isfile(pyburt_tmpfile)
    assert os.stat(pyburt_tmpfile).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(pyburt_tmpfile)
    header, _ = snap_parser.parse()

    assert expected_snap_comment == header[sp.COMMENTS_PREFIX]
    assert expected_snap_keywords == header[sp.KEYWORDS_PREFIX]


@mock.patch("burt.read.caget")
def test_snapshot_req_file_length_bigger_than_pv(mock_caget, pyburt_tmpfile):
    """Try to save a PV with a length that is greater than the PV data size.

    This is a case which would not be caught by the parser.
    """
    # return value is a 8 element array.
    # The requested save length in the .req file is 9.
    array_return_value = aug_val([0] * 8, count=8)
    mock_caget.return_value = [array_return_value]

    with pytest.raises(ValueError):
        burt.take_snapshot([test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ], pyburt_tmpfile)


@pytest.mark.xfail
def test_snapshot_group(mock_caget):
    """Runs a take snapshot group test of a .rqg file."""
    # TODO: this is a broken test with incorrect behaviour. To be changed when
    #  snapshot groups are implemented.
    assert False


def _old_req_file_header_burtinter_code(snapshotString):
    """Remnant in old burtinter code."""
    # Old code start
    if snapshotString[0:9] == "Req File:":
        requestFileName = snapshotString.split(" ")[2].split("\n")[0]
        fileNameParts = requestFileName.split("/")
        if fileNameParts[1] == "mt":
            fileNameParts[1] = ""
            requestFileName = "/".join(fileNameParts[1:])
    # Old code end
    else:
        pytest.fail(
            f"Last prefix entry is unexpectedly not Req File: {snapshotString}",
            snapshotString,
        )
