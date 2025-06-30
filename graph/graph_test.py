from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from operator import add
import logging
from codecarbon import EmissionsTracker
import datetime
import os

# For Mermaid visualization
from IPython.display import Image, display
import base64

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

def save_graph_visualization(graph, filename="graph_visualization.png"):
    """Save the LangGraph Mermaid diagram as PNG"""
    try:
        # Generate the Mermaid PNG
        mermaid_png = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open(filename, "wb") as f:
            f.write(mermaid_png)
        
        print(f"✅ Graph visualization saved as '{filename}'")
        
        # Optional: Display in IPython if available
        try:
            display(Image(mermaid_png))
        except:
            print("💡 To view the image inline, run this in Jupyter or IPython")
        
        return filename
        
    except Exception as e:
        logger.error(f"Failed to save graph visualization: {e}")
        return None

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
            # Create dummy nodes for testing
            logger.warning("Creating dummy nodes for testing...")
            
            def dummy_node(name):
                def node_func(state):
                    print(f"🔄 Running {name}...")
                    return state
                return node_func
            
            market_analysis_node = lambda config: dummy_node("Market Analysis")
            forecasting_node = lambda config: dummy_node("Forecasting")
            risk_node = lambda config: dummy_node("Risk Analysis")
            compliance_node = lambda config: dummy_node("Compliance")
            coordinator_node = lambda config: dummy_node("Coordinator")
            memory_reflection_node = lambda config: dummy_node("Memory Reflection")
        
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
        
        # Save the graph visualization
        print("📊 Creating and saving graph visualization...")
        save_graph_visualization(graph, "my_financial_graph.png")
        
        # Define initial state
        initial_state = {
            "assets": ["AAPL", "TSLA", "NVDA"],  # Your assets
            "timestamp": datetime.datetime.utcnow().isoformat(),           
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
        
        # Start emissions tracking
        tracker = EmissionsTracker(project_name="graph_cli_run", output_file="emissions.csv")
        tracker.start()
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        
        # Stop emissions tracking
        emissions = tracker.stop()
        logger.info(f"Estimated CO₂ emissions: {emissions:.6f} kg")
        
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
        
        # Save simple graph visualization
        print("📊 Creating simple graph visualization...")
        save_graph_visualization(graph, "simple_graph.png")
        
        initial_state = {"assets": ["TEST"], "result": ""}
        
        tracker = EmissionsTracker(project_name="graph_cli_run", output_file="emissions.csv")
        tracker.start()

        result = graph.invoke(initial_state)

        emissions = tracker.stop()
        logger.info(f"Estimated CO₂ emissions: {emissions:.6f} kg")
        logger.info(f"Simple test result: {result}")
        
    except Exception as e:
        logger.error(f"Simple test failed: {e}")

# Standalone function to visualize any existing graph
def visualize_existing_graph():
    """If you already have a graph object, use this to visualize it"""
    try:
        # Build a quick graph for demonstration
        config = {}
        graph = build_graph(config)
        
        if graph:
            # Method 1: Save as PNG
            save_graph_visualization(graph, "langgraph_diagram.png")
            
            # Method 2: Get raw Mermaid code (if you want to see the code)
            mermaid_code = graph.get_graph().draw_mermaid()
            print("\n📝 Mermaid code:")
            print(mermaid_code)
            
            # Method 3: If you're in IPython/Jupyter, display inline
            try:
                mermaid_png = graph.get_graph().draw_mermaid_png()
                display(Image(mermaid_png))
            except:
                print("💡 Run in IPython/Jupyter to see inline display")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test the visualization first
    print("🚀 Testing graph visualization...")
    visualize_existing_graph()
    
    # First test with simple graph
    test_simple()
    
    # Then run your main function
    run()