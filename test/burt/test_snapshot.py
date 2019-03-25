""" Various tests for the main burt module.
"""
import pytest
import test
import mock
import burt
import cothread
import os
import numpy

from burt.parsers import ParserException


@mock.patch('burt.pv.caget')
def test_blank_snapshot(mock_caget):
    """Runs the burt snapshot against a blank .req file.
    """
    mock_caget.return_value = cothread.catools.ca_nothing

    burt.take_snapshot(test.BLANK_REQ, test.TMP_PYBURT_OUT)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
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
        burt.restore("")
    with pytest.raises(ValueError):
        burt.restore("goodbyeworld")
    with pytest.raises(ValueError):
        burt.restore("helloworld.snap")


@mock.patch('burt.pv.caget')
def test_snapshot_arrays(mock_caget):
    """Runs a take snapshot test of a normal .req file with a mocked ca array
    return value.
    """
    # Flattened ndarray is a 40 element list.
    mock_caget.return_value = \
        cothread.dbr.ca_array(numpy.array([1, 1, 40])).flatten()

    test_comment = "Hello World"
    test_keywords = "cool,snap,file"

    burt.take_snapshot(test.NORMAL_REQ, test.TMP_PYBURT_OUT, test_comment,
                       test_keywords)

    assert os.path.isfile(test.TMP_PYBURT_OUT)
    assert os.stat(test.TMP_PYBURT_OUT).st_size != 0

    # Reverse parsing should have the correct contents for the independent
    # properties, e.g. keywords, directory, etc.
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 12 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert test.NORMAL_REQ == snap_parser.req_file

    assert snap_parser.pv_snapshots[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(snap_parser.pv_snapshots[0].vals) == 40
    assert snap_parser.pv_snapshots[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[1].vals) == 40
    assert snap_parser.pv_snapshots[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(snap_parser.pv_snapshots[2].vals) == 40
    assert snap_parser.pv_snapshots[3].name == "SR01C-DI-COL-02:GAP"
    assert len(snap_parser.pv_snapshots[3].vals) == 40

    # These PVs have a set save value in the .req file, and the last two have
    # readonly modifiers
    assert snap_parser.pv_snapshots[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[4].vals) == 5
    assert snap_parser.pv_snapshots[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[5].vals) == 10
    assert snap_parser.pv_snapshots[5].is_readonly
    assert snap_parser.pv_snapshots[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[6].vals) == 25
    assert snap_parser.pv_snapshots[6].is_readonly_notify

    # Some readonly modifiers here.
    assert snap_parser.pv_snapshots[7].name == "SR01C-DI-COL-01:POS1"
    assert len(snap_parser.pv_snapshots[7].vals) == 40
    assert snap_parser.pv_snapshots[7].is_readonly_notify
    assert snap_parser.pv_snapshots[8].name == "SR01C-DI-COL-01:POS2"
    assert len(snap_parser.pv_snapshots[8].vals) == 40
    assert snap_parser.pv_snapshots[8].is_readonly
    assert snap_parser.pv_snapshots[9].name == "SR01C-DI-COL-02:POS1"
    assert len(snap_parser.pv_snapshots[9].vals) == 40
    assert snap_parser.pv_snapshots[9].is_readonly
    assert snap_parser.pv_snapshots[10].name == "SR01C-DI-COL-02:POS2"
    assert len(snap_parser.pv_snapshots[10].vals) == 40
    assert snap_parser.pv_snapshots[10].is_readonly
    assert snap_parser.pv_snapshots[11].name == "SR-CS-RING-01:MODE"
    assert len(snap_parser.pv_snapshots[11].vals) == 40

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
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
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 12 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert test.NORMAL_REQ == snap_parser.req_file

    assert snap_parser.pv_snapshots[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(snap_parser.pv_snapshots[0].vals) == 1
    assert snap_parser.pv_snapshots[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[1].vals) == 1
    assert snap_parser.pv_snapshots[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(snap_parser.pv_snapshots[2].vals) == 1
    assert snap_parser.pv_snapshots[3].name == "SR01C-DI-COL-02:GAP"
    assert len(snap_parser.pv_snapshots[3].vals) == 1
    assert snap_parser.pv_snapshots[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[4].vals) == 1
    assert snap_parser.pv_snapshots[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[5].vals) == 1
    assert snap_parser.pv_snapshots[5].is_readonly
    assert snap_parser.pv_snapshots[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[6].vals) == 1
    assert snap_parser.pv_snapshots[6].is_readonly_notify

    # Some readonly modifiers here.
    assert snap_parser.pv_snapshots[7].name == "SR01C-DI-COL-01:POS1"
    assert len(snap_parser.pv_snapshots[7].vals) == 1
    assert snap_parser.pv_snapshots[7].is_readonly_notify
    assert snap_parser.pv_snapshots[8].name == "SR01C-DI-COL-01:POS2"
    assert len(snap_parser.pv_snapshots[8].vals) == 1
    assert snap_parser.pv_snapshots[8].is_readonly
    assert snap_parser.pv_snapshots[9].name == "SR01C-DI-COL-02:POS1"
    assert len(snap_parser.pv_snapshots[9].vals) == 1
    assert snap_parser.pv_snapshots[9].is_readonly
    assert snap_parser.pv_snapshots[10].name == "SR01C-DI-COL-02:POS2"
    assert len(snap_parser.pv_snapshots[10].vals) == 1
    assert snap_parser.pv_snapshots[10].is_readonly
    assert snap_parser.pv_snapshots[11].name == "SR-CS-RING-01:MODE"
    assert len(snap_parser.pv_snapshots[11].vals) == 1

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
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
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 12 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert test_keywords == snap_parser.keywords
    assert test_comment == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert test.NORMAL_REQ == snap_parser.req_file

    assert snap_parser.pv_snapshots[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(snap_parser.pv_snapshots[0].vals) == 1
    assert snap_parser.pv_snapshots[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[1].vals) == 1
    assert snap_parser.pv_snapshots[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(snap_parser.pv_snapshots[2].vals) == 1
    assert snap_parser.pv_snapshots[3].name == "SR01C-DI-COL-02:GAP"
    assert len(snap_parser.pv_snapshots[3].vals) == 1
    assert snap_parser.pv_snapshots[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[4].vals) == 1
    assert snap_parser.pv_snapshots[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[5].vals) == 1
    assert snap_parser.pv_snapshots[5].is_readonly
    assert snap_parser.pv_snapshots[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[6].vals) == 1
    assert snap_parser.pv_snapshots[6].is_readonly_notify
    assert snap_parser.pv_snapshots[7].name == "SR01C-DI-COL-01:POS1"
    assert len(snap_parser.pv_snapshots[7].vals) == 1
    assert snap_parser.pv_snapshots[7].is_readonly_notify
    assert snap_parser.pv_snapshots[8].name == "SR01C-DI-COL-01:POS2"
    assert len(snap_parser.pv_snapshots[8].vals) == 1
    assert snap_parser.pv_snapshots[8].is_readonly
    assert snap_parser.pv_snapshots[9].name == "SR01C-DI-COL-02:POS1"
    assert len(snap_parser.pv_snapshots[9].vals) == 1
    assert snap_parser.pv_snapshots[9].is_readonly
    assert snap_parser.pv_snapshots[10].name == "SR01C-DI-COL-02:POS2"
    assert len(snap_parser.pv_snapshots[10].vals) == 1
    assert snap_parser.pv_snapshots[10].is_readonly
    assert snap_parser.pv_snapshots[11].name == "SR-CS-RING-01:MODE"
    assert len(snap_parser.pv_snapshots[11].vals) == 1

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
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
    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()

    assert expected_snap_comment == snap_parser.comments
    assert expected_snap_keywords == snap_parser.keywords

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
def test_snapshot_invalid_save_len(mock_caget):
    """
    Try to save a PV with a length specified that is greater than the PV
    data size. This is a case which would not be caught by the parser.
    """
    # Flattened ndarray is a 936 element list (mimics SR-DI-PICO-01:BUCKETS).
    # The requested save length in the .req file is 937.
    mock_caget.return_value = \
        cothread.dbr.ca_array(numpy.array([1, 1, 936])).flatten()

    with pytest.raises(ValueError):
        burt.take_snapshot(test.MALFORMED_SAVE_LEN_TOO_LARGE_REQ,
                           test.TMP_PYBURT_OUT)


@mock.patch('burt.pv.caget')
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

    snap_parser = burt.SnapParser(test.TMP_PYBURT_OUT)
    snap_parser.parse()
    assert 24 == len(snap_parser.pv_snapshots)
    assert snap_parser.time
    assert snap_parser.login_id
    assert snap_parser.u_id
    assert snap_parser.group_id
    assert "" == snap_parser.keywords
    assert "" == snap_parser.comments
    assert burt.TYPE_DEFAULT_VAL == snap_parser.type
    assert os.getcwd() == snap_parser.directory
    assert "testables/req/normal.req,testables/req/normal.req" == \
           snap_parser.req_file

    assert snap_parser.pv_snapshots[0].name == "SR01C-DI-COL-01:CENTRE"
    assert len(snap_parser.pv_snapshots[0].vals) == 40
    assert snap_parser.pv_snapshots[1].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[1].vals) == 40
    assert snap_parser.pv_snapshots[2].name == "SR01C-DI-COL-02:CENTRE"
    assert len(snap_parser.pv_snapshots[2].vals) == 40
    assert snap_parser.pv_snapshots[3].name == "SR01C-DI-COL-02:GAP"
    assert len(snap_parser.pv_snapshots[3].vals) == 40

    # These PVs have a set save value in the .req file, and the last two have
    # readonly modifiers
    assert snap_parser.pv_snapshots[4].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[4].vals) == 5
    assert snap_parser.pv_snapshots[5].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[5].vals) == 10
    assert snap_parser.pv_snapshots[5].is_readonly
    assert snap_parser.pv_snapshots[6].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[6].vals) == 25
    assert snap_parser.pv_snapshots[6].is_readonly_notify

    # Some readonly modifiers here.
    assert snap_parser.pv_snapshots[7].name == "SR01C-DI-COL-01:POS1"
    assert len(snap_parser.pv_snapshots[7].vals) == 40
    assert snap_parser.pv_snapshots[7].is_readonly_notify
    assert snap_parser.pv_snapshots[8].name == "SR01C-DI-COL-01:POS2"
    assert len(snap_parser.pv_snapshots[8].vals) == 40
    assert snap_parser.pv_snapshots[8].is_readonly
    assert snap_parser.pv_snapshots[9].name == "SR01C-DI-COL-02:POS1"
    assert len(snap_parser.pv_snapshots[9].vals) == 40
    assert snap_parser.pv_snapshots[9].is_readonly
    assert snap_parser.pv_snapshots[10].name == "SR01C-DI-COL-02:POS2"
    assert len(snap_parser.pv_snapshots[10].vals) == 40
    assert snap_parser.pv_snapshots[10].is_readonly
    assert snap_parser.pv_snapshots[11].name == "SR-CS-RING-01:MODE"
    assert len(snap_parser.pv_snapshots[11].vals) == 40

    assert snap_parser.pv_snapshots[12].name == "SR01C-DI-COL-01:CENTRE"
    assert len(snap_parser.pv_snapshots[12].vals) == 40
    assert snap_parser.pv_snapshots[13].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[13].vals) == 40
    assert snap_parser.pv_snapshots[14].name == "SR01C-DI-COL-02:CENTRE"
    assert len(snap_parser.pv_snapshots[14].vals) == 40
    assert snap_parser.pv_snapshots[15].name == "SR01C-DI-COL-02:GAP"
    assert len(snap_parser.pv_snapshots[15].vals) == 40

    # These PVs have a set save value in the .req file, and the last two have
    # readonly modifiers
    assert snap_parser.pv_snapshots[16].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[16].vals) == 5
    assert snap_parser.pv_snapshots[17].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[17].vals) == 10
    assert snap_parser.pv_snapshots[17].is_readonly
    assert snap_parser.pv_snapshots[18].name == "SR-DI-PICO-01:BUCKETS"
    assert len(snap_parser.pv_snapshots[18].vals) == 25
    assert snap_parser.pv_snapshots[18].is_readonly_notify

    # Some readonly modifiers here.
    assert snap_parser.pv_snapshots[19].name == "SR01C-DI-COL-01:POS1"
    assert len(snap_parser.pv_snapshots[19].vals) == 40
    assert snap_parser.pv_snapshots[19].is_readonly_notify
    assert snap_parser.pv_snapshots[20].name == "SR01C-DI-COL-01:POS2"
    assert len(snap_parser.pv_snapshots[20].vals) == 40
    assert snap_parser.pv_snapshots[20].is_readonly
    assert snap_parser.pv_snapshots[21].name == "SR01C-DI-COL-02:POS1"
    assert len(snap_parser.pv_snapshots[21].vals) == 40
    assert snap_parser.pv_snapshots[21].is_readonly
    assert snap_parser.pv_snapshots[22].name == "SR01C-DI-COL-02:POS2"
    assert len(snap_parser.pv_snapshots[22].vals) == 40
    assert snap_parser.pv_snapshots[22].is_readonly
    assert snap_parser.pv_snapshots[23].name == "SR-CS-RING-01:MODE"
    assert len(snap_parser.pv_snapshots[23].vals) == 40

    # cleanup
    os.remove(test.TMP_PYBURT_OUT)
