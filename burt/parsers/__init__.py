"""parsers package."""

import burt


class ParserException(Exception):
    """ Raised when the parsers run into unexpected malformed formats.
    """
    pass


def skippable_line(line):
    """Determines if a line should be skipped.

    Args:
        line (str): The line currently being parsed.

    Returns
        bool: If the line should be skipped, or not.
    """
    is_comment_line = line.strip().startswith(burt.INLINE_COMMENT)
    is_blank_line = not line.strip()
    return is_comment_line or is_blank_line


def clean_line(line):
    """Preprocesses the line for parsing.

    Args:
        line (str): The line currently being parsed.

    Returns
        str: The cleaned line.
    """
    if burt.INLINE_COMMENT in line:
        line = line[:line.find(burt.INLINE_COMMENT)]

    return line.strip()
