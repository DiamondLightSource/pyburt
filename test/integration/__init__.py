"""The integration test package."""

# Shared test .req files.
NORMAL_REQ = "testables/req/normal.req"
BCDORBIT_REQ = "/home/ops/burt/requestFiles/bcdorbit.req"

# Shared test .snap files.
ARR_SNAP = "testables/snap/ioc_restore_array.snap"
SCALAR_SNAP = "testables/snap/ioc_restore_scalar.snap"
LONG_SNAP = "testables/snap/ioc_restore_long.snap"
ENUM_SNAP = "testables/snap/ioc_restore_enum.snap"
STRING_SNAP = "testables/snap/ioc_restore_string.snap"
BCDORBIT_SNAP = "testables/snap/ioc_restore_bcdorbit.snap"
CONTROL_ROOM_LOCAL_IOC_TYPES_SNAP = "testables/snap/ioc_restore_control_room_types.snap"

# The local running PVs initialized with the local_ioc.py script.
IOC_LOCAL_PV_FLOAT = "SR-CS-SOFT-01:AI"
IOC_LOCAL_PV_ARR_FLOAT = "SR-CS-SOFT-01:FLOAT_ARR"

IOC_LOCAL_PV_LONG = "SR-CS-SOFT-01:LONGIN"
IOC_LOCAL_PV_ARR_LONG = "SR-CS-SOFT-01:LONG_ARR"

IOC_LOCAL_PV_DBL = "SR-CS-SOFT-01:AI"
IOC_LOCAL_PV_ARR_DBL = "SR-CS-SOFT-01:DOUBLE_ARR"

IOC_LOCAL_PV_STR = "SR-CS-SOFT-01:STRINGIN"
IOC_LOCAL_PV_ARR_STR = "SR-CS-SOFT-01:STRING_ARR"

IOC_LOCAL_PV_ENUM = "SR-CS-SOFT-01:MBBI"

IOC_LOCAL_PV_CHAR = "SR-CS-SOFT-01:TESTPV_CHAR"
IOC_LOCAL_PV_ARR_CHAR = "SR-CS-SOFT-01:CHAR_ARR"

IOC_LOCAL_PV_SHORT = "SR-CS-SOFT-01:TESTPV_SHORT"
IOC_LOCAL_PV_ARR_SHORT = "SR-CS-SOFT-01:SHORT_ARR"
