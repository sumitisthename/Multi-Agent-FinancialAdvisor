# main.py (updated with test scenario)

from graph.graph_builder import build_graph
from config.settings import load_config
from utils.logger import setup_logger


def run():
    config = load_config()
    logger = setup_logger()

    logger.info("Starting LangGraph Multi-Agent Financial System Test Run...")

    # Build LangGraph workflow
    graph = build_graph(config)

    # Test scenario input
    initial_state = {
        "assets": ["AAPL", "TSLA", "NVDA"],
        "timestamp": "2025-06-10",
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
