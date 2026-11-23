"""
Logging configuration for OS Simulator.
Provides unified console and file logging with timestamps and log levels.
"""

import logging
import os
from typing import Optional

LOGGER_NAME = "SimOS"

def setup_logger(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console formatter (clean, readable)
    c_format = logging.Formatter("[%(levelname)s] %(message)s")
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File formatter (detailed with timestamp and module)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        f_format = logging.Formatter("%(asctime)s - [%(name)s] [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s")
        f_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    return logger

def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        return setup_logger(log_file="logs/sim_os.log", level=logging.INFO)
    return logger
