"""Utility functions to setup a standard logging scheme/format for BURT processes."""
import logging
import sys

# E.g.) 2019-11-19 15:16:08,970 - root - WARNING - caget failure SR01C-DI-COL-01:C
DEFAULT_LOG_FORMAT = "%(asctime)-15s - %(name)s - %(levelname)s - %(message)s"


def configure_root_logger(level=logging.INFO, log_file_path=None):
    """Configure the root logger to the BURT defaults.

    Args:
        level (int): The log level, logging.INFO by default.
        log_file_path (str): The path to the log file to write to if applicable.

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Always print log messages to stdout.
    stdout_handler = logging.StreamHandler(sys.stdout)

    handlers = [stdout_handler]

    if log_file_path:
        try:
            log_file_handler = logging.FileHandler(log_file_path, mode="a+")
            handlers.append(log_file_handler)
        except FileNotFoundError as e:
            logging.warning(f"Problem opening BURT logfile: {e}")

    for handler in handlers:
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        root_logger.addHandler(handler)


def add_handler(handler, level=logging.INFO, formatter=None):
    """Add a new handler for the root logger.

    Args:
        handler (logging.Handler): The logging instance to use.
        formatter (logging.Formatter): The formatter to use, otherwise use default.
    """
    if formatter is None:
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

    handler.setLevel(level)
    logging.getLogger().addHandler(handler)
