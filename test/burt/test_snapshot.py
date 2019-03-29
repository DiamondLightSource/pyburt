""" Various tests for the main burt module.
"""
import pytest
import test
import mock
import burt
import cothread
import os
import numpy
from burt import SnapParser as sp


@mock.patch('burt.snapshot.caget')
def test_blank_snapshot(mock_caget):
    """Runs the burt snapshot against a blank .req file.
    """
    mock_caget.return_value = cothread.catools.ca_nothing

    burt.take_snapshot(test.BLANK_REQ, test.TMP_PYBURT_OUT)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_bad_file_arguments(mock_caget):
    """Runs the burt script against a case where the file arguments are
    malformed.
    """
    mock_caget.return_value = cothread.catools.ca_nothing

    with pytest.raises(ValueError):
        burt.take_snapshot("", "")
    with pytest.raises(ValueError):
        burt.take_snapshot("goodbyeworld", "helloworld")
    with pytest.raises(ValueError):
        burt.take_snapshot("goodbyeworld.req", "helloworld.snap")
    with pytest.raises(ValueError):
        burt.take_snapshot(test.BLANK_REQ, "helloworld.txt")
    with pytest.raises(ValueError):
        burt.do_restore("")
    with pytest.raises(ValueError):
        burt.do_restore("goodbyeworld")
    with pytest.raises(ValueError):
        burt.do_restore("helloworld.snap")


@mock.patch('burt.snapshot.caget')
def test_snapshot_arrays(mock_caget):
    """Runs a take snapshot test of a normal .req file with a mocked ca array
    return value.
    """
    # Flattened ndarray is a 40 element list.
    mock_caget.return_value = cothread.dbr.ca_array(
        numpy.array([1, 1, 40])
    ).flatten()

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(test.TMP_PYBURT_OUT)
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

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_snapshot_enum(mock_caget):
    """Runs a take snapshot test of a normal .req file with a mocked enum
    return value.
    """
    mock_caget.return_value = cothread.dbr.ca_str("DIAD")

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(test.TMP_PYBURT_OUT)
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

    # Some readonly modifiers here.
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

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_snapshot_scalar(mock_caget):
    """Runs a take snapshot test of a normal .req file with a mocked scalar
    return value.
    """
    mock_caget.return_value = -1e-16

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(test.TMP_PYBURT_OUT)
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

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_snapshot_newlines_in_args(mock_caget):
    """Runs a take snapshot test with the problematic case of newlines in user
    supplied meta data. The newlines should appear as is in the .snap file,
    with the help of an extra backslash, and not interpreted.
    """
    mock_ret = cothread.dbr.ca_array(numpy.array([1, 1, 40])).flatten()
    mock_caget.return_value = mock_ret

    test_comment = "\nHello\r\n \nWorld\r\n\r"
    test_keywords = "\r\ncool\n,\r\nsnap,file\n\r\r"

    expected_snap_comment = "\\nHello\\r\\n \\nWorld\\r\\n\\r"
    expected_snap_keywords = "\\r\\ncool\\n,\\r\\nsnap,file\\n\\r\\r"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = sp(test.TMP_PYBURT_OUT)
    header, _ = snap_parser.parse()

    assert expected_snap_comment == header[sp.COMMENTS_PREFIX]
    assert expected_snap_keywords == header[sp.KEYWORDS_PREFIX]

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_snapshot_invalid_save_len(mock_caget):
    """
    Try to save a PV with a length specified that is greater than the PV
    data size. This is a case which would not be caught by the parser.
    """
    # Flattened ndarray is a 936 element list (mimics SR-DI-PICO-01:BUCKETS).
    # The requested save length in the .req file is 937.
    mock_caget.return_value = cothread.dbr.ca_array(
        numpy.array([1, 1, 936])
    ).flatten()

    with pytest.raises(ValueError):
        burt.take_snapshot(test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ,
                           test.TMP_PYBURT_OUT)


@mock.patch('burt.snapshot.caget')
def test_snapshot_group_arrays(mock_caget):
    """Runs a take snapshot group test of a .rqg file with mocked ca array
    return values. The request group file specifies a .req file twice, so
    the contents of the snap file should consist of the header, plus the
    .req pvs twice.
    """
    mock_ret = cothread.dbr.ca_array(numpy.array([1, 1, 40])).flatten()
    mock_caget.return_value = mock_ret

    burt.take_snapshot_group(test.NORMAL_ALT_RQG, test.TMP_PYBURT_OUT)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    snap_parser = sp(test.TMP_PYBURT_OUT)
    header, body = snap_parser.parse()
    assert 24 == len(body)
    assert header[sp.TIME_PREFIX]
    assert header[sp.LOGINID_PREFIX]
    assert header[sp.UID_PREFIX]
    assert header[sp.GROUPID_PREFIX]
    assert "" == header[sp.KEYWORDS_PREFIX]
    assert "" == header[sp.COMMENTS_PREFIX]
    assert sp.TYPE_DEFAULT_VAL == header[sp.TYPE_PREFIX]
    assert os.getcwd() == header[sp.DIRECTORY_PREFIX]
    assert "testables/req/normal.req,testables/req/normal.req" == header[
        sp.REQ_FILE_PREFIX]

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

    assert body[12].name == "SR01C-DI-COL-01:CENTRE"
    assert len(body[12].vals) == 40
    assert body[13].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[13].vals) == 40
    assert body[14].name == "SR01C-DI-COL-02:CENTRE"
    assert len(body[14].vals) == 40
    assert body[15].name == "SR01C-DI-COL-02:GAP"
    assert len(body[15].vals) == 40

    # These PVs have a set save value in the .req file, and the last two have
    # readonly modifiers
    assert body[16].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[16].vals) == 5
    assert body[17].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[17].vals) == 10
    assert body[17].modifier == "RO"
    assert body[18].name == "SR-DI-PICO-01:BUCKETS"
    assert len(body[18].vals) == 25
    assert body[18].modifier == "RON"

    # Some readonly modifiers here.
    assert body[19].name == "SR01C-DI-COL-01:POS1"
    assert len(body[19].vals) == 40
    assert body[19].modifier == "RON"
    assert body[20].name == "SR01C-DI-COL-01:POS2"
    assert len(body[20].vals) == 40
    assert body[20].modifier == "RO"
    assert body[21].name == "SR01C-DI-COL-02:POS1"
    assert len(body[21].vals) == 40
    assert body[21].modifier == "RO"
    assert body[22].name == "SR01C-DI-COL-02:POS2"
    assert len(body[22].vals) == 40
    assert body[22].modifier == "RO"
    assert body[23].name == "SR-CS-RING-01:MODE"
    assert len(body[23].vals) == 40

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)
