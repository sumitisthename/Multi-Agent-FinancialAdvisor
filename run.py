"""
Main entry point for the LangGraph multi-agent financial analysis system.
"""
from config.settings import load_config
from utils.logger import setup_logger
from dotenv import load_dotenv
from datetime import datetime
import os
from graph.graph_builder import build_graph


from dotenv import load_dotenv
load_dotenv()

import os
print("[DEBUG] Using GROQ Key:", os.getenv("GROQ_API_KEY"))



def run():
    """
    Initializes and runs the LangGraph financial analysis system.
    """
    config = load_config()
    logger = setup_logger()

    logger.info("Starting LangGraph Multi-Agent Financial System Test Run...")

    # Build LangGraph workflow
    graph = build_graph()

    # Test scenario input
    initial_state = {
        "assets": ["AAPL", "TSLA", "NVDA"],
        "timestamp": datetime.utcnow().isoformat(),
        "memory": None
    }

    # Run the graph for a single cycle
    result = graph.invoke(initial_state)

    print("\n======= FINAL DECISION =======")
    print(result.get("final_decision", "No decision produced"))

    print("\n======= REFLECTION LESSON =======")
    print(result.get("reflection_lesson", "No reflection produced"))


if __name__ == "__main__":
    run()
