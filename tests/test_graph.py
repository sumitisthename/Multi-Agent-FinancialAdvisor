import unittest
import logging
from datetime import datetime, timezone

# For optional IPython inline display (won't fail if IPython not installed)
try:
    from IPython.display import Image, display
except ImportError:
    Image = None
    display = None

# Adjust import path to your actual module
from graph.graph_builder import build_graph  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_graph_visualization(graph, filename="test_graph_visualization.png"):
    try:
        mermaid_png = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(mermaid_png)
        logger.info(f"Graph visualization saved as '{filename}'")
        if display and Image:
            display(Image(mermaid_png))
        return filename
    except Exception as e:
        logger.error(f"Failed to save graph visualization: {e}")
        return None

import os

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.config = {"api_key": "test_api_key"}
        os.environ['GROQ_API_KEY'] = 'test_key'

    def test_build_graph(self):
        graph = build_graph(self.config)
        self.assertIsNotNone(graph)
        logger.info(f"Graph object type: {type(graph)}")

    def test_get_analysis_nodes(self):
        graph = build_graph(self.config)
        self.assertIsNotNone(graph)
        self.assertIn("coordinator", graph.nodes)
        self.assertIn("memory_reflection", graph.nodes)

    def test_graph_visualization_saved(self):
        graph = build_graph(self.config)
        self.assertIsNotNone(graph)

        filename = "test_graph_visualization.png"
        saved_file = save_graph_visualization(graph, filename)
        self.assertIsNotNone(saved_file)
        self.assertTrue(saved_file.endswith(".png"))

if __name__ == "__main__":
    unittest.main()
