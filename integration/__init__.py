"""The integration package."""
import subprocess

# Shared test .req files.
NORMAL_REQ = "testables/req/normal.req"

# Shared test .snap files.
ARR_SNAP = "testables/snap/ioc_restore_array.snap"
SCALAR_SNAP = "testables/snap/ioc_restore_scalar.snap"

# The local running PV initialized with the local_ioc.py script.
# Note: it is a PV of containing a ca array datatype with 5 float32 elements.
IOC_LOCAL_PV = "SR-CS-TEST-01:TESTPV"

# Tmp files.
TMP_BURT_OUT = "integration/tmp_burt.snap"
TMP_PYBURT_OUT = "integration/tmp_pyburt.snap"
