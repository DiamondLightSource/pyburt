"""Modified logconfig.py from dls_ade."""
import getpass
import logging.config
import os

GRAYLOG_HOST = "graylog2.diamond.ac.uk"
GRAYLOG_PORT = 12201

DEFAULT_LOG_FORMAT = (
    "%(asctime)5s - %(filename)s:%(lineno)d - %(name)s - %("
    "levelname)5s - %(message)s"
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
        },
        "logfile_handler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "extended",
            "filename": "",
            "mode": "a+",
            "delay": True,
        },
        "graylog_handler": {
            "class": "pygelf.GelfUdpHandler",
            "level": "INFO",
            "host": GRAYLOG_HOST,
            "port": GRAYLOG_PORT,
            "debug": True,
            "include_extra_fields": True,
            "username": getpass.getuser(),
            "pid": os.getpid(),
            "package": __package__,
            "application": "pyburt",
        },
    },
    "loggers": {
        "console_entry": {
            "level": "INFO",
            "handlers": ["graylog_handler"],
            "propagate": True,
        },
        "console_entry_with_logfile": {
            "level": "INFO",
            "handlers": ["graylog_handler", "logfile_handler"],
            "propagate": True,
        },
    },
    "root": {
        # Set the level here to be the default minimum level of log record to be
        # produced
        # If you set a handler to level DEBUG you will need to set either this level, or
        # the level of one of the loggers above to DEBUG or you won't see any DEBUG
        # messages
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging(default_level=logging.INFO, log_file_path=None):
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
                DEFAULT_CONFIG["handlers"]["logfile_handler"].update(
                    {"filename": log_file_path}
                )
            except KeyError:
                pass

        logging.config.dictConfig(DEFAULT_CONFIG)

    except Exception as e:
        logging.basicConfig(level=default_level)
        logging.warning(f"Logging configuration failed to load: {str(e)}")
