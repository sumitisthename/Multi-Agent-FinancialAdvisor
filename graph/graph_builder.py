from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from operator import add
import logging
from codecarbon import EmissionsTracker
from IPython.display import display,Image
import datetime
from datetime import datetime, timezone # Add timezone here
import os
import sys
from dotenv import load_dotenv

# Set project root as the first entry in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixed GraphState with proper reducers
class GraphState(TypedDict):
    assets: Annotated[list[str], add]  # Use add reducer for lists
    timestamp: str                     # Simple string, no reducer needed
    market_summary: str
    forecast: str
    risk_report: str
    compliance_review: str
    final_decision: str
    reflection_lesson: str
    user_query: str  
    economic_indicators: list[dict]
    evaluation_results: dict

def build_graph(config):
    """Build and return the compiled graph. Raises exceptions if anything fails."""
    import traceback

    logger.info("Starting graph construction...")

    try:
        # Create the StateGraph with our schema
        builder = StateGraph(GraphState)
        logger.info("StateGraph created successfully")

        # Import agent nodes
        from agents.market_analysis import market_analysis_node
        from agents.forecasting_strategy import forecasting_node
        from agents.risk_anomaly import risk_node
        from agents.economic_indicator import economic_indicator_node
        from agents.compliance_monitor import compliance_node
        from agents.coordinator import coordinator_node
        from agents.memory_reflection import memory_reflection_node
        from agents.evaluation import evaluation_node
        logger.info("All agent modules imported successfully")

        # Add nodes
        builder.add_node("market_analysis", market_analysis_node(config))
        builder.add_node("forecasting", forecasting_node(config))
        builder.add_node("risk", risk_node(config))
        builder.add_node("economic_data", economic_indicator_node())
        builder.add_node("compliance", compliance_node(config))
        builder.add_node("coordinator", coordinator_node(config))
        builder.add_node("evaluation", evaluation_node(config))
        builder.add_node("memory_reflection", memory_reflection_node(config))
        logger.info("All nodes added successfully")

        # Set up graph structure
        builder.set_entry_point("economic_data")
        builder.add_edge("economic_data", "market_analysis")
        builder.add_edge("market_analysis", "forecasting")
        builder.add_edge("forecasting", "risk")
        builder.add_edge("risk", "compliance")
        builder.add_edge("compliance", "coordinator")
        builder.add_edge("coordinator", "evaluation")
        builder.add_edge("evaluation", "memory_reflection")
        builder.set_finish_point("memory_reflection")
        logger.info("Graph structure defined successfully")

        # Compile graph
        compiled_graph = builder.compile()
        logger.info("Graph compiled successfully")
        return compiled_graph

    except Exception as e:
        logger.error("Graph construction failed:\n%s", traceback.format_exc())
        # Fail fast
        raise RuntimeError("Graph construction failed. Check logs for details.") from e


def run():
    """Main execution function"""
    try:
        # Your config setup
        config = {
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        }
        
        # Build the graph with debugging
        logger.info("Building graph...")
        graph = build_graph(config)
        
        # Check if graph was created successfully
        if graph is None:
            logger.error("Graph construction returned None - check build_graph function")
            return
        
        logger.info(f"Graph created successfully: {type(graph)}")
        
        # Define initial state
        initial_state = {
            "assets": ["AAPL", "TSLA", "NVDA"],  # Your assets
            "timestamp": datetime.now(timezone.utc).isoformat(),           
            "user_query": " ",
            "market_summary": "",
            "forecast": "",
            "risk_report": "",
            "compliance_review": "",
            "final_decision": "",
            "reflection_lesson": ""
        }
        
        logger.info("Starting graph execution...")
        logger.info(f"Initial state: {initial_state}")
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        
        logger.info("Graph execution completed successfully")
        logger.info(f"Final result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise

def display_graph(graph):
    try:
        display(Image(graph.get_graph().create_png()))
    except Exception as e:
        logger.error(f"Failed to display graph: {e}")

if __name__ == "__main__" and not os.environ.get("STREAMLIT_ENV"):
    run()