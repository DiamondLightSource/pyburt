"""Modified logconfig.py from dls_ade."""
import getpass
import logging
import logging.config
import logging.handlers
import os
import sys

import pygelf

GRAYLOG_HOST = "graylog2.diamond.ac.uk"
GRAYLOG_PORT = 12201

DEFAULT_LOG_FORMAT = (
    "%(asctime)5s - %(filename)s:%(lineno)d - %(" "levelname)5s - %(message)s"
)

DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"extended": {"format": DEFAULT_LOG_FORMAT}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "extended",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


def get_graylog_handler():
    handler = pygelf.GelfUdpHandler(
        GRAYLOG_HOST,
        GRAYLOG_PORT,
        debug=True,
        include_extra_fields=True,
        _username=getpass.getuser(),
        _package=__package__,
        _pid=os.getpid(),
        _application_name="pyburt",
    )
    handler.setLevel(logging.DEBUG)
    return handler


def get_logfile_handler(log_file_path: str):
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    handler = logging.FileHandler(log_file_path, "a+")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler


def setup_logging(default_level: int = logging.INFO, log_file_path: str = None):
    """Set logging configuration.

    Call this only once from the application main() function or __main__ module!

    This will configure the python logging module based on a logging configuration
    in the following order of priority:

       1. Log configuration file found in the environment variable specified in the
       `env_key` argument.
       2. Log configuration file found in the `default_log_config` argument.
       3. Default log configuration found in the `logconfig.default_config` dict.
       4. If all of the above fails: basicConfig is called with the `default_level`
       argument.

    Args:
        default_level (int): logging level to set as default. Ignored if a log
            configuration is found elsewhere.
        log_file_path (str): path to optional logfile.

    Returns: None

    """
    try:
        if log_file_path is not None:
            try:
                # Mypy inner dicts issue, see:
                # https://stackoverflow.com/questions/54786574/
                DEFAULT_CONFIG["handlers"]["logfile_handler"].update(  # type: ignore
                    {"filename": log_file_path}
                )
            except KeyError:
                pass

        logging.config.dictConfig(DEFAULT_CONFIG)

    except Exception as e:
        logging.basicConfig(level=default_level)
        tb = sys.exc_info()[2]
        logging.warning(
            f"Logging configuration failed to load: {str(e.with_traceback(tb))}"
        )
