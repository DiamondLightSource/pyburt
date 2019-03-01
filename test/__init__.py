""" Shared globals used by the python tests."""
BLANK_REQ_FILE = "test/testables/blank.req"
BLANK_SNAP_FILE = "test/testables/blank.snap"
REQ_FILE_WITH_INLINE_COMMENTS = "test/testables/req_with_inline_comments.req"
REQ_FILE_1 = "test/testables/test_1.req"
REQ_FILE_2 = "test/testables/test_2.req"
SNAP_FILE_1 = "test/testables/test_1.snap"
SNAP_FILE_2 = "test/testables/test_2.snap"
WRONG_HEADER = "test/testables/wrong_header.snap"
BLANK_HEADER_CONTENTS = "test/testables/only_header.snap"

# Sample PVs to test against
PV_SCALAR_1 = "SR01C-DI-COL-01:POS1"
PV_WITH_CA_ARR = "SR-DI-PICO-01:BUCKETS"

# The local running PV initialized with the test_ioc.py script. Note: it is a PV of a ca array with five float32
# elements.
IOC_LOCAL_PV = "SR-CS-TEST-01:TESTPV"
IOC_SNAP_FILE_1 = "test/testables/test_ioc_restore_1.snap"  # ca array
IOC_SNAP_FILE_2 = "test/testables/test_ioc_restore_2.snap"  # scalar
