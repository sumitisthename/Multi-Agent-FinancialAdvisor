"""
Builds the LangGraph workflow for the multi-agent financial analysis system.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from operator import add
import logging
from codecarbon import EmissionsTracker
from IPython.display import display,Image
import datetime
from datetime import datetime, timezone # Add timezone here
import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixed GraphState with proper reducers
class GraphState(TypedDict):
    """
    Represents the state of the LangGraph.
    """
    assets: Annotated[list[str], add]  # Use add reducer for lists
    timestamp: str                     # Simple string, no reducer needed
    market_summary: str
    forecast: str
    risk_report: str
    compliance_review: str
    final_decision: str
    reflection_lesson: str
    user_query: str  

def build_graph(config):
    """
    Builds and compiles the LangGraph workflow.
    """
    try:
        logger.info("Starting graph construction...")
        
        # Create the StateGraph with our schema
        builder = StateGraph(GraphState)
        logger.info("StateGraph created successfully")
        
        # Import your agent nodes with error handling
        try:
            from agents.market_analysis import market_analysis_node
            from agents.forecasting_strategy import forecasting_node
            from agents.risk_anomaly import risk_node
            from agents.compliance_monitor import compliance_node
            from agents.coordinator import coordinator_node
            from agents.memory_reflection import memory_reflection_node
            logger.info("All agent modules imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import agent modules: {e}")
            raise
        
        # Add nodes to the graph
        try:
            builder.add_node("market_analysis", market_analysis_node(config))
            builder.add_node("forecasting", forecasting_node())
            builder.add_node("risk", risk_node())
            builder.add_node("compliance", compliance_node())
            builder.add_node("coordinator", coordinator_node())
            builder.add_node("memory_reflection", memory_reflection_node())
            logger.info("All nodes added successfully")
        except Exception as e:
            logger.error(f"Failed to add nodes: {e}")
            raise
        
        # Set up the graph structure
        try:
            builder.set_entry_point("market_analysis")
            
            # Use sequential execution to avoid parallel state updates
            builder.add_edge("market_analysis", "forecasting")
            builder.add_edge("forecasting", "risk")
            builder.add_edge("risk", "compliance")
            builder.add_edge("compliance", "coordinator")
            builder.add_edge("coordinator", "memory_reflection")
            
            builder.set_finish_point("memory_reflection")
            logger.info("Graph structure defined successfully")
        except Exception as e:
            logger.error(f"Failed to set up graph structure: {e}")
            raise
        
        # Compile the graph
        try:
            compiled_graph = builder.compile()
            logger.info("Graph compiled successfully")
            return compiled_graph
        except Exception as e:
            logger.error(f"Failed to compile graph: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Graph construction failed: {e}")
        return None

def display_graph(graph):
    """
    Displays the graph.
    """
    try:
        display(Image(graph.get_graph().create_png()))
    except Exception as e:
        logger.error(f"Failed to display graph: {e}")
        raise