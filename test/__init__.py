"""The test package."""

# Shared test .req files.
BLANK_REQ = "testables/req/blank.req"
INLINE_COMMENTS_REQ = "testables/req/inline_comments.req"
NORMAL_REQ = "testables/req/normal.req"

MALFORMED_REQ = "testables/req/malformed.req"
MALFORMED_SAVE_LEN_NEG_INT_REQ = "testables/req/malformed_save_len_neg_int.req"
MALFORMED_SAVE_LEN_NON_INT_REQ = "testables/req/malformed_save_len_non_int.req"
MALFORMED_SAVE_LEN_TOO_LARGE_REQ = "testables/req/malformed_save_len_too_large.req"

# Shared test .snap files.
ARRAYS_AND_SCALARS_SNAP = "testables/snap/arrays_and_scalars.snap"
BLANK_SNAP = "testables/snap/blank.snap"
SCALARS_SNAP = "testables/snap/scalars.snap"
INLINE_COMMENTS_SNAP = "testables/snap/inline_comments.snap"
MODIFIERS_SNAP = "testables/snap/modifiers.snap"
MULTIPLE_REQ_PATHS_SNAP = "testables/snap/multiple_req_paths.snap"

DUPLICATE_BURT_HEADERS_SNAP = "testables/snap/duplicate_burt_headers.snap"
MALFORMED_BODY_SNAP = "testables/snap/malformed_body.snap"
MALFORMED_HEADER_COLONS_SNAP = "testables/snap/malformed_header_missing_colons.snap"
MALFORMED_HEADER_ENTRIES_SNAP = "testables/snap/malformed_header_strange_entries.snap"
MALFORMED_HEADER_BURT_TYPO_SNAP = "testables/snap/malformed_header_burt_typo.snap"
MALFORMED_HEADER_TYPO_SNAP = "testables/snap/malformed_header_typo_prefixes.snap"
MALFORMED_FOOTER_PREFIX_SNAP = "testables/snap/malformed_footer_unknown_prefix.snap"
MALFORMED_FOOTER_NON_INT_LENGTH_SNAP = (
    "testables/snap/malformed_footer_non_int_length.snap"
)
MISORDERED_BURT_HEADER_SNAP = "testables/snap/misordered_burt_headers.snap"
MISORDERED_HEADER_PREFIXES_SNAP = "testables/snap/misordered_header_prefixes.snap"
MISSING_BOTTOM_HEADER_SNAP = "testables/snap/missing_bottom_burt_header.snap"
MISSING_TOP_HEADER_SNAP = "testables/snap/missing_top_burt_header.snap"
ONLY_HEADER_SNAP = "testables/snap/only_header.snap"

# Shared test .rgr files.
BLANK_RGR = "testables/rgr/blank.rgr"
INLINE_COMMENTS_RGR = "testables/rgr/inline_comments.rgr"
NORMAL_RGR = "testables/rgr/normal.rgr"
NORMAL_ALT_RGR = "testables/rgr/normal_alt.rgr"

DUPLICATE_HEADERS_RGR = "testables/rgr/duplicate_rgr_headers.rgr"
MALFORMED_BODY_RGR = "testables/rgr/malformed_body.rgr"
MALFORMED_BODY_MISORDERED_CHECKS_RGR = (
    "testables/rgr/malformed_body_misordered_checks.rgr"
)
MALFORMED_HEADER_ENTRIES_RGR = "testables/rgr/malformed_header_strange_entries.rgr"
MALFORMED_HEADER_TYPO_RGR = "testables/rgr/malformed_header_typo.rgr"
MALFORMED_HEADER_PREFIX_TYPO_RGR = "testables/rgr/malformed_header_typo_prefixes.rgr"
MISORDERED_HEADER_RGR = "testables/rgr/misordered_headers.rgr"
MISSING_BOTTOM_HEADER_RGR = "testables/rgr/missing_bottom_rgr_header.rgr"
MISSING_TOP_HEADER_RGR = "testables/rgr/missing_top_rgr_header.rgr"
ONLY_HEADER_RGR = "testables/rgr/only_header.rgr"

# Shared test .rqg files.
BLANK_RQG = "testables/rqg/blank.rqg"
INLINE_COMMENTS_RQG = "testables/rqg/inline_comments.rqg"
NORMAL_RQG = "testables/rqg/normal.rqg"
NORMAL_ALT_RQG = "testables/rqg/normal_alt.rqg"
MALFORMED_RQG = "testables/rqg/malformed.rqg"
MALFORMED_MISORDERED_CHECKS_RQG = "testables/rqg/malformed_misordered_checks.rqg"

# Shared test .check files.
BAD_PREFIX_CHECK = "testables/check/bad_prefix.check"
BAD_VALUES_CHECK = "testables/check/bad_values.check"
EXCESS_VALUES_CHECK = "testables/check/excess_values.check"
EXTRA_PREFIX_CHECK = "testables/check/extra_prefix.check"
MISSING_TARGET_CHECK = "testables/check/missing_target.check"
MULTI_LINE_COMMENT_CHECK = "testables/check/multi_line_comment.check"
NEG_TOLERANCE_CHECK = "testables/check/neg_tolerance.check"
NORMAL_CHECK_1 = "testables/check/normal_1.check"
NORMAL_CHECK_2 = "testables/check/normal_2.check"
NORMAL_CHECK_3 = "testables/check/normal_3.check"

# Tmp snap file to be deleted after a test run.
TMP_PYBURT_OUT = "test/tmp.snap"
