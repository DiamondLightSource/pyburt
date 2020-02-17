"""The integration package."""
import subprocess

# Shared test .req files.
NORMAL_REQ = "testables/req/normal.req"
BCDORBIT_REQ = "/home/ops/burt/requestFiles/bcdorbit.req"

# Shared test .snap files.
ARR_SNAP = "testables/snap/ioc_restore_array.snap"
SCALAR_SNAP = "testables/snap/ioc_restore_scalar.snap"
LONG_SNAP = "testables/snap/ioc_restore_long.snap"
ENUM_SNAP = "testables/snap/ioc_restore_enum.snap"
BCDORBIT_SNAP = "testables/snap/ioc_restore_bcdorbit.snap"

# The local running PVs initialized with the local_ioc.py script.
IOC_LOCAL_PV_FLOAT = "SR-CS-TEST-01:TESTPV_FLOAT"
IOC_LOCAL_PV_ARR_FLOAT = "SR-CS-TEST-01:TESTPV_ARR_FLOAT"

IOC_LOCAL_PV_LONG = "SR-CS-TEST-01:TESTPV_LONG"
IOC_LOCAL_PV_ARR_LONG = "SR-CS-TEST-01:TESTPV_ARR_LONG"

IOC_LOCAL_PV_DBL = "SR-CS-TEST-01:TESTPV_DBL"
IOC_LOCAL_PV_ARR_DBL = "SR-CS-TEST-01:TESTPV_ARR_DBL"

IOC_LOCAL_PV_STR = "SR-CS-TEST-01:TESTPV_STR"
IOC_LOCAL_PV_ENUM_STR = "SR-CS-TEST-01:TESTPV_ENUM_STR"
IOC_LOCAL_PV_ARR_STR = "SR-CS-TEST-01:TESTPV_ARR_STR"

IOC_LOCAL_PV_CHAR = "SR-CS-TEST-01:TESTPV_CHAR"
IOC_LOCAL_PV_ARR_CHAR = "SR-CS-TEST-01:TESTPV_ARR_CHAR"

IOC_LOCAL_PV_SHORT = "SR-CS-TEST-01:TESTPV_SHORT"
IOC_LOCAL_PV_ARR_SHORT = "SR-CS-TEST-01:TESTPV_ARR_SHORT"

# Tmp files.
TMP_BURT_OUT = "integration/tmp_burt.snap"
TMP_PYBURT_OUT = "integration/tmp_pyburt.snap"
