"""The test package."""
'''
Shared test .req files.
'''
BLANK_REQ = \
    "testables/req/blank.req"
INLINE_COMMENTS_REQ = \
    "testables/req/inline_comments.req"
MALFORMED_REQ = \
    "testables/req/malformed.req"
MALFORMED_SAVE_LEN_NEG_INT_REQ = \
    "testables/req/malformed_save_len_neg_int.req"
MALFORMED_SAVE_LEN_NON_INT_REQ = \
    "testables/req/malformed_save_len_non_int.req"
MALFORMED_SAVE_LEN_TOO_LARGE_REQ = \
    "testables/req/malformed_save_len_too_large.req"
NORMAL_REQ = \
    "testables/req/normal.req"

'''
Shared test .snap files.
'''
ARRAYS_AND_SCALARS_SNAP = \
    "testables/snap/arrays_and_scalars.snap"
BLANK_SNAP = \
    "testables/snap/blank.snap"
DUPLICATE_BURT_HEADERS_SNAP = \
    "testables/snap/duplicate_burt_headers.snap"
INLINE_COMMENTS_SNAP = \
    "testables/snap/inline_comments.snap"
MALFORMED_BODY_SNAP = \
    "testables/snap/malformed_body.snap"
MALFORMED_HEADER_COLONS_SNAP = \
    "testables/snap/malformed_header_missing_colons.snap"
MALFORMED_HEADER_ENTRIES_SNAP = \
    "testables/snap/malformed_header_strange_entries.snap"
MALFORMED_HEADER_TYPO_SNAP = \
    "testables/snap/malformed_header_typo_prefixes.snap"
MISORDERED_BURT_HEADER_SNAP = \
    "testables/snap/misordered_burt_headers.snap"
MISORDERED_HEADER_PREFIXES_SNAP = \
    "testables/snap/misordered_header_prefixes.snap"
MISSING_BOTTOM_HEADER_SNAP = \
    "testables/snap/missing_bottom_burt_header.snap"
MISSING_TOP_HEADER_SNAP = \
    "testables/snap/missing_top_burt_header.snap"
ONLY_HEADER_SNAP = \
    "testables/snap/only_header.snap"
SCALARS_SNAP = \
    "testables/snap/scalars.snap"

'''
Tmp snap file to be deleted after a test run.
'''
TMP_PYBURT_OUT = "test/tmp.snap"
