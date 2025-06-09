from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from operator import add
import logging

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

def build_graph(config):
    """Build and return the compiled graph"""
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
            builder.add_node("forecasting", forecasting_node(config))
            builder.add_node("risk", risk_node(config))
            builder.add_node("compliance", compliance_node(config))
            builder.add_node("coordinator", coordinator_node(config))
            builder.add_node("memory_reflection", memory_reflection_node(config))
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

def run():
    """Main execution function"""
    try:
        # Your config setup
        config = {
            # Add your configuration here
            "api_key": "your_api_key",  # Replace with actual config
            # ... other config parameters
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
            "timestamp": "2025-06-10",           # Your timestamp
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

# Alternative simpler version for testing
def build_simple_graph(config):
    """Simplified graph for testing"""
    class SimpleState(TypedDict):
        assets: list[str]
        result: str
    
    def simple_node(state):
        assets = state.get("assets", [])
        return {"result": f"Processed {len(assets)} assets: {', '.join(assets)}"}
    
    builder = StateGraph(SimpleState)
    builder.add_node("process", simple_node)
    builder.set_entry_point("process")
    builder.set_finish_point("process")
    
    return builder.compile()

def test_simple():
    """Test with a simple graph first"""
    try:
        logger.info("Testing simple graph...")
        graph = build_simple_graph({})
        
        if graph is None:
            logger.error("Simple graph is None")
            return
        
        result = graph.invoke({"assets": ["AAPL", "TSLA"], "result": ""})
        logger.info(f"Simple test result: {result}")
        
    except Exception as e:
        logger.error(f"Simple test failed: {e}")

if __name__ == "__main__":
    # First test with simple graph
    test_simple()
    
    # Then run your main function
    run()