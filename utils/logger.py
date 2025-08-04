import logging
import os
import sys
from config.settings import load_config

# Load configuration
_config = load_config()

LOG_LEVEL = _config.get("LOG_LEVEL", "INFO").upper()
LOG_FILE = _config.get("LOG_FILE", "logs/system.log")

# Ensure logs directory exists
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))


def setup_logger(name="multi_agent_app"):
    """Sets up a logger with both file and stream handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # Stream handler (for console/Streamlit)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # File handler (for logs/system.log)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name="multi_agent_app"):
    return logging.getLogger(name)
