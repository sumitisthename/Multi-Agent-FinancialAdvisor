# memory/memory_store.py

import os
import json
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()

MEMORY_LOG_PATH = "./memory/logs.json"


def log_decision(state, lesson, config):
    logger.info("Logging decision and lesson to memory")

    entry = {
        "timestamp": state["timestamp"],
        "assets": state["assets"],
        "decision": state.get("final_decision", ""),
        "lesson": lesson
    }

    try:
        if os.path.exists(MEMORY_LOG_PATH):
            with open(MEMORY_LOG_PATH, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(entry)

        with open(MEMORY_LOG_PATH, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write to memory log: {e}")


def retrieve_recent_memory(config, limit=5):
    try:
        if os.path.exists(MEMORY_LOG_PATH):
            with open(MEMORY_LOG_PATH, "r") as f:
                logs = json.load(f)
            recent = logs[-limit:]
            return "\n".join([f"{l['timestamp']}: {l['lesson']}" for l in recent])
        else:
            return "No memory available."
    except Exception as e:
        logger.error(f"Failed to read memory log: {e}")
        return "Memory fetch error."
