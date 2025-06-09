# config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "ALPHA_VANTAGE_KEY": os.getenv("ALPHA_VANTAGE_KEY"),
        "YAHOO_FINANCE_ENDPOINT": os.getenv("YAHOO_FINANCE_ENDPOINT"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "VECTOR_DB_PATH": os.getenv("VECTOR_DB_PATH"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LOG_FILE": os.getenv("LOG_FILE", "logs/system.log")
    }
