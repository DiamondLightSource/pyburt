"""integration package."""
# The local running PV initialized with the test_ioc.py script. Note: it is a PV of a ca array with five float32
# elements.
IOC_LOCAL_PV = "SR-CS-TEST-01:TESTPV"

# Shared test files
IOC_SNAP_FILE_1 = "integration/testables/test_ioc_restore_1.snap"  # ca array
IOC_SNAP_FILE_2 = "integration/testables/test_ioc_restore_2.snap"  # scalar
NORMAL_REQ = "integration/testables/normal.req"
