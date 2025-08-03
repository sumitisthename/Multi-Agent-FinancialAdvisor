# utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import load_config

_config = load_config()

LOG_LEVEL = _config.get("LOG_LEVEL", "INFO")
LOG_FILE = _config.get("LOG_FILE", "logs/system.log")

if not os.path.exists("logs"):
    os.makedirs("logs")


def setup_logger():
    """
    Sets up a rotating file handler and a stream handler for logging.
    """
    logger = logging.getLogger("agent-system")
    logger.setLevel(LOG_LEVEL)

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1024 * 1024 * 5, backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    )

    # Create a stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    )

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_logger():
    """
    Returns the logger instance.
    """
    return logging.getLogger("agent-system")
