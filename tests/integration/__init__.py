"""The integration test package."""

# Shared test .req files.
NORMAL_REQ = "tests/resources/req/normal.req"
ARR_REQ = "tests/resources/req/array.req"

# Shared test .snap files.
ARR_SNAP = "tests/resources/snap/ioc_restore_array.snap"
SCALAR_SNAP = "tests/resources/snap/ioc_restore_scalar.snap"
LONG_SNAP = "tests/resources/snap/ioc_restore_long.snap"
ENUM_SNAP = "tests/resources/snap/ioc_restore_enum.snap"
STRING_SNAP = "tests/resources/snap/ioc_restore_string.snap"
CONTROL_ROOM_LOCAL_IOC_TYPES_SNAP = (
    "tests/resources/snap/ioc_restore_control_room_types.snap"
)
NULL_ARRAY_SNAP = "tests/resources/snap/null_arrays.snap"
PARTIAL_ARRAY_SNAP = "tests/resources/snap/partial_arrays.snap"

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
