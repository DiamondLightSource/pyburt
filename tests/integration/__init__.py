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
