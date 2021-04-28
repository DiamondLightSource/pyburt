# Shared test .req files.
BLANK_REQ = "tests/resources/req/blank.req"
INLINE_COMMENTS_REQ = "tests/resources/req/inline_comments.req"
NORMAL_REQ = "tests/resources/req/normal.req"
TYPES_REQ = "tests/resources/req/types.req"

MALFORMED_REQ = "tests/resources/req/malformed.req"
MALFORMED_SAVE_LEN_NEG_INT_REQ = "tests/resources/req/malformed_save_len_neg_int.req"
MALFORMED_SAVE_LEN_NON_INT_REQ = "tests/resources/req/malformed_save_len_non_int.req"
MALFORMED_SAVE_LEN_TOO_LARGE_REQ = (
    "tests/resources/req/malformed_save_len_too_large.req"
)

# Shared test .snap files.
SIMPLE_SNAP = "tests/resources/snap/simple.snap"
ENUM_SNAP = "tests/resources/snap/enum_with_spaces.snap"
ARRAYS_AND_SCALARS_SNAP = "tests/resources/snap/arrays_and_scalars.snap"
ARRAYS_AND_SCALARS_WITH_MODS_SNAP = (
    "tests/resources/snap/arrays_and_scalars_with_mods.snap"
)
BLANK_SNAP = "tests/resources/snap/blank.snap"
SCALARS_SNAP = "tests/resources/snap/scalars.snap"
INLINE_COMMENTS_SNAP = "tests/resources/snap/inline_comments.snap"
MULTIPLE_REQ_PATHS_SNAP = "tests/resources/snap/multiple_req_paths.snap"
LONG_SNAP = "tests/resources/snap/ioc_restore_long.snap"
CONTROL_ROOM_TYPES_SNAP = "tests/resources/snap/types.controlroom.snap"

DUPLICATE_BURT_HEADERS_SNAP = "tests/resources/snap/duplicate_burt_headers.snap"
MALFORMED_BODY_SNAP = "tests/resources/snap/malformed_body.snap"
MALFORMED_HEADER_COLONS_SNAP = (
    "tests/resources/snap/malformed_header_missing_colons.snap"
)
MALFORMED_HEADER_ENTRIES_SNAP = (
    "tests/resources/snap/malformed_header_strange_entries.snap"
)
MALFORMED_HEADER_BURT_TYPO_SNAP = "tests/resources/snap/malformed_header_burt_typo.snap"
MALFORMED_HEADER_TYPO_SNAP = "tests/resources/snap/malformed_header_typo_prefixes.snap"
MALFORMED_FOOTER_PREFIX_SNAP = (
    "tests/resources/snap/malformed_footer_unknown_prefix.snap"
)
MALFORMED_FOOTER_NON_INT_LENGTH_SNAP = (
    "tests/resources/snap/malformed_footer_non_int_length.snap"
)
MISORDERED_BURT_HEADER_SNAP = "tests/resources/snap/misordered_burt_headers.snap"
MISORDERED_HEADER_PREFIXES_SNAP = "tests/resources/snap/misordered_header_prefixes.snap"
MISSING_BOTTOM_HEADER_SNAP = "tests/resources/snap/missing_bottom_burt_header.snap"
MISSING_TOP_HEADER_SNAP = "tests/resources/snap/missing_top_burt_header.snap"
ONLY_HEADER_SNAP = "tests/resources/snap/only_header.snap"

# Shared test .rgr files.
BLANK_RGR = "tests/resources/rgr/blank.rgr"
INLINE_COMMENTS_RGR = "tests/resources/rgr/inline_comments.rgr"
NORMAL_RGR = "tests/resources/rgr/normal.rgr"
NORMAL_ALT_RGR = "tests/resources/rgr/normal_alt.rgr"

DUPLICATE_HEADERS_RGR = "tests/resources/rgr/duplicate_rgr_headers.rgr"
MALFORMED_BODY_RGR = "tests/resources/rgr/malformed_body.rgr"
MALFORMED_BODY_MISORDERED_CHECKS_RGR = (
    "tests/resources/rgr/malformed_body_misordered_checks.rgr"
)
MALFORMED_HEADER_ENTRIES_RGR = (
    "tests/resources/rgr/malformed_header_strange_entries.rgr"
)
MALFORMED_HEADER_TYPO_RGR = "tests/resources/rgr/malformed_header_typo.rgr"
MALFORMED_HEADER_PREFIX_TYPO_RGR = (
    "tests/resources/rgr/malformed_header_typo_prefixes.rgr"
)
MISORDERED_HEADER_RGR = "tests/resources/rgr/misordered_headers.rgr"
MISSING_BOTTOM_HEADER_RGR = "tests/resources/rgr/missing_bottom_rgr_header.rgr"
MISSING_TOP_HEADER_RGR = "tests/resources/rgr/missing_top_rgr_header.rgr"
ONLY_HEADER_RGR = "tests/resources/rgr/only_header.rgr"

# Shared test .rqg files.
BLANK_RQG = "tests/resources/rqg/blank.rqg"
INLINE_COMMENTS_RQG = "tests/resources/rqg/inline_comments.rqg"
NORMAL_RQG = "tests/resources/rqg/normal.rqg"
NORMAL_ALT_RQG = "tests/resources/rqg/normal_alt.rqg"
MALFORMED_RQG = "tests/resources/rqg/malformed.rqg"
MALFORMED_MISORDERED_CHECKS_RQG = "tests/resources/rqg/malformed_misordered_checks.rqg"

# Shared test .check files.
BAD_PREFIX_CHECK = "tests/resources/check/bad_prefix.check"
BAD_VALUES_CHECK = "tests/resources/check/bad_values.check"
EXCESS_VALUES_CHECK = "tests/resources/check/excess_values.check"
EXTRA_PREFIX_CHECK = "tests/resources/check/extra_prefix.check"
MISSING_TARGET_CHECK = "tests/resources/check/missing_target.check"
MULTI_LINE_COMMENT_CHECK = "tests/resources/check/multi_line_comment.check"
NEG_TOLERANCE_CHECK = "tests/resources/check/neg_tolerance.check"
NORMAL_CHECK_1 = "tests/resources/check/normal_1.check"
NORMAL_CHECK_2 = "tests/resources/check/normal_2.check"
NORMAL_CHECK_3 = "tests/resources/check/normal_3.check"


# Tmp snap file to be deleted after a test run.
PYBURT_OUT_FILE = "tmp_pyburt.snap"
