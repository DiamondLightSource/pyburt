"""Various tests for the utils file."""
import burt.utils.file as f


def test_file_normal():
    """Run file util tests against normal cases."""
    assert f.is_rgr_file("sample.rgr")
    assert f.is_rgr_file("/utils/sample.rgr")
    assert f.is_snap_file("sample.snap")
    assert f.is_snap_file("/utils/sample.snap")
    assert f.is_rqg_file("sample.rqg")
    assert f.is_rqg_file("/utils/sample.rqg")
    assert f.is_req_file("sample.req")
    assert f.is_req_file("/utils/sample.req")
    assert f.is_check_file("sample.check")
    assert f.is_check_file("/utils/sample.check")


def test_file_fail():
    """Run file util tests against malformed cases."""
    assert not f.is_rgr_file("sample.rg")
    assert not f.is_rgr_file("/utils/sample.req")
    assert not f.is_snap_file("sample.snp")
    assert not f.is_snap_file("/utils/sample")
    assert not f.is_rqg_file("sample.rg")
    assert not f.is_rqg_file("/utils/sample.rq")
    assert not f.is_req_file("sample.r")
    assert not f.is_req_file("/utils/sample.rq")
    assert not f.is_check_file("sample.chec")
    assert not f.is_check_file("/utils/sample.ceck")
