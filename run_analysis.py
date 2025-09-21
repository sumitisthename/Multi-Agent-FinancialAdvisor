import json
from datetime import datetime
from graph.graph_builder import build_graph
from config.settings import load_config

def load_decisions(log_file: str = "logs/real_time_decisions.json"):
    """
    Loads trading decisions from a log file.
    """
    decisions = []
    with open(log_file, "r") as f:
        for line in f:
            decisions.append(json.loads(line))
    return decisions

def main():
    """
    Runs the high-level analysis on the real-time decisions.
    """
    config = load_config()
    graph = build_graph(config) # We still need the graph for the nodes

    # Load the decisions from the real-time trader
    decisions = load_decisions()
    if not decisions:
        print("No decisions to analyze.")
        return

    # We'll run the analysis on the most recent decision
    last_decision = decisions[-1]

    # Create a state object that mimics the old LangGraph state
    initial_state = {
        "assets": [last_decision["asset"]],
        "timestamp": last_decision["timestamp"],
        "market_summary": "Market data from real-time feed.", # Placeholder
        "forecast": f"Forecast leading to {last_decision['decision']} decision.", # Placeholder
        "risk_report": "Risk analysis from real-time agent.", # Placeholder
        "compliance_review": "Compliance check from real-time agent.", # Placeholder
        "final_decision": last_decision["decision"],
        "user_query": "",
        "economic_indicators": [],
        "evaluation_results": {},
        "reflection_lesson": ""
    }

    # Get the coordinator and memory reflection nodes from the graph
    coordinator_node_func = graph.nodes["coordinator"]
    memory_reflection_node_func = graph.nodes["memory_reflection"]

    # Run the coordinator
    print("Running Coordinator...")
    coordinator_result_state = coordinator_node_func.invoke(initial_state)
    print("Coordinator Result:", coordinator_result_state.get("final_decision"))

    # Run memory reflection
    print("\nRunning Memory Reflection...")
    reflection_result_state = memory_reflection_node_func.invoke(coordinator_result_state)
    print("Reflection Lesson:", reflection_result_state.get("reflection_lesson"))

if __name__ == "__main__":
    main()
