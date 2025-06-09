# utils/logger.py

import logging
import os
from config.settings import load_config

_config = load_config()

LOG_LEVEL = _config.get("LOG_LEVEL", "INFO")
LOG_FILE = _config.get("LOG_FILE", "logs/system.log")

if not os.path.exists("logs"):
    os.makedirs("logs")


def setup_logger():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("agent-system")


def get_logger():
    return logging.getLogger("agent-system")
