from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from operator import add
import logging
from codecarbon import EmissionsTracker
from datetime import datetime, timezone
import os

# For Mermaid visualization
from IPython.display import Image, display

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Updated GraphState with economic_indicators
class GraphState(TypedDict):
    assets: Annotated[list[str], add]
    timestamp: str
    market_summary: str
    forecast: str
    risk_report: str
    compliance_review: str
    final_decision: str
    reflection_lesson: str
    user_query: str
    economic_indicators: list[dict]

def save_graph_visualization(graph, filename="graph_visualization.png"):
    try:
        mermaid_png = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(mermaid_png)
        print(f"✅ Graph visualization saved as '{filename}'")
        try:
            display(Image(mermaid_png))
        except:
            print("💡 To view the image inline, run this in Jupyter or IPython")
        return filename
    except Exception as e:
        logger.error(f"Failed to save graph visualization: {e}")
        return None

def test_graph():
    try:
        logger.info("Testing updated graph...")
        
        # Empty config or add real config as needed
        config = {"api_key": "your_api_key"}
        
        from graph_builder import build_graph  # Adjust import path accordingly
        
        graph = build_graph(config)
        if graph is None:
            logger.error("Graph build returned None")
            return
        
        print("📊 Saving graph visualization...")
        save_graph_visualization(graph, "updated_graph.png")
        
        # Define a realistic initial state with new field
        initial_state = {
            "assets": ["AAPL", "TSLA", "NVDA"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_query": "What is the market outlook?",
            "market_summary": "",
            "forecast": "",
            "risk_report": "",
            "compliance_review": "",
            "final_decision": "",
            "reflection_lesson": "",
            "economic_indicators": []
        }
        
        tracker = EmissionsTracker(project_name="graph_test_run", output_file="emissions.csv")
        tracker.start()
        
        result = graph.invoke(initial_state)
        
        emissions = tracker.stop()
        logger.info(f"Estimated CO₂ emissions: {emissions:.6f} kg")
        logger.info(f"Graph execution result: {result}")
        
    except Exception as e:
        logger.error(f"Test graph failed: {e}")

if __name__ == "__main__":
    test_graph()
