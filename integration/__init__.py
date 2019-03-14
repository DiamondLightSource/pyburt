"""The integration package."""
import subprocess

'''
Shared test .req files.
'''
NORMAL_REQ = "integration/testables/req/normal.req"

'''
Shared test .snap files.
'''
ARR_SNAP = "integration/testables/snap/test_ioc_restore_1.snap"
SCALAR_SNAP = "integration/testables/snap/test_ioc_restore_2.snap"

'''
The local running PV initialized with the test_ioc.py script.

Note: it is a PV of containing a ca array datatype with five float32 elements.
'''
IOC_LOCAL_PV = "SR-CS-TEST-01:TESTPV"

'''
Tmp files.
'''
TMP_BURT_OUT = "integration/testables/tmp_burt.snap"
TMP_PYBURT_OUT = "integration/testables/tmp_pyburt.snap"


def vanilla_burtrb(input_req, output_snap, comments, keywords):
    """
    Wrapper for the original burtrb implementation.

    Args:
        input_req (str): input req file(s)
        output_snap (str): output snap file
        comments (comments): comments
        keywords (keywords): keywords
    """
    burt_rb_cmd = \
        "/dls_sw/epics/R3.14.12.3/extensions/bin/linux-x86_64/burtrb -f " \
        + input_req + " -o " \
        + output_snap + " -c " + comments + " -k " + keywords

    # Without shell=True raises an exception on Python 2.7
    process = subprocess.Popen(burt_rb_cmd, shell=True)
    process.wait()
    assert process.returncode == 0
