# -*- coding: utf-8 -*-
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

# Universal log format for the project
default_logger_format = "[%(asctime)s - %(name)s - %(levelname)s: %(message)s]"


def get_timed_rotating_file_logger(
    logger_name: str,
    log_file: str,
    when: str = "midnight",
    interval: int = 1,
    backup: int = 5,
    logger_format: str = default_logger_format,
) -> logging.Logger:
    """
    Utility Function to write to a Timed Rotating File Handler

    Parameters
    ----------
    logger_name : str
        Name of the logger
    log_file : str
        Log File Path
    when : str
        Specifies the type of interval
        (e.g., "midnight", "S", "M", "H", "D", "W0"-"W6")
        Default - "midnight"
    interval : int
        The interval for rotating the log file.
        Default - 1
    backup : int
        Number of backup files to keep
        Default - 5

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(logger_name)

    # Create an empty log file if it doesn"t exist
    if not os.path.exists(log_file):
        open(log_file, "w+").close()

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = TimedRotatingFileHandler(
            filename=log_file, when=when, interval=interval, backupCount=backup
        )
        file_formatter = logging.Formatter(logger_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(logger_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
