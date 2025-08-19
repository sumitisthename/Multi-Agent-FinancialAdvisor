import unittest
import logging
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

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

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.config = {"api_key": "test_api_key"}

    def test_build_graph(self):
        graph = build_graph(self.config)
        self.assertIsNotNone(graph)
        logger.info(f"Graph object type: {type(graph)}")

    @patch('tools.data_fetcher.fetch_news_data')
    @patch('tools.data_fetcher.fetch_market_data')
    @patch('agents.memory_reflection.ChatGroq')
    @patch('agents.evaluation.ChatGroq')
    @patch('agents.coordinator.ChatGroq')
    @patch('agents.compliance_monitor.ChatGroq')
    @patch('agents.risk_anomaly.ChatGroq')
    @patch('agents.forecasting_strategy.ChatGroq')
    @patch('agents.market_analysis.ChatGroq')
    @patch('agents.economic_indicator.ChatGroq')
    def test_graph_invoke(self, mock_econ_cg, mock_market_cg, mock_forecast_cg, mock_risk_cg, mock_compliance_cg, mock_coord_cg, mock_eval_cg, mock_mem_cg, mock_fetch_market, mock_fetch_news):
        # Mock the LLM to return different values for each call
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.side_effect = [
            "Mock economic indicator",
            "Mock market summary",
            "Mock forecast",
            "Mock risk report",
            "Mock compliance review",
            "Mock final decision",
            '{"fcd": 1, "fgr": 1, "fdf": 0, "ecs": 0.1}', # eval
            "Mock reflection"
        ]

        # Point all ChatGroq mocks to the same instance
        mock_econ_cg.return_value = mock_llm_instance
        mock_market_cg.return_value = mock_llm_instance
        mock_forecast_cg.return_value = mock_llm_instance
        mock_risk_cg.return_value = mock_llm_instance
        mock_compliance_cg.return_value = mock_llm_instance
        mock_coord_cg.return_value = mock_llm_instance
        mock_eval_cg.return_value = mock_llm_instance
        mock_mem_cg.return_value = mock_llm_instance

        # Mock data fetchers
        mock_fetch_market.return_value = {"AAPL": 150.0}
        mock_fetch_news.return_value = ["Fake news"]

        graph = build_graph(self.config)
        self.assertIsNotNone(graph)

        initial_state = {
            "assets": ["AAPL", "TSLA"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_summary": "",
            "forecast": "",
            "risk_report": "",
            "compliance_review": "",
            "final_decision": "",
            "reflection_lesson": "",
            "user_query": "What is the market forecast?",
            "economic_indicators": []
        }

        result = graph.invoke(initial_state)

        logger.info(f"Graph invoke result: {result}")

        self.assertIsInstance(result, dict)
        self.assertIn("final_decision", result)
        # The coordinator node is the one that sets the final_decision
        # The mock for the coordinator is the 6th in the side_effect list
        self.assertEqual(result['final_decision'], "Mock final decision")

    def test_graph_visualization_saved(self):
        graph = build_graph(self.config)
        self.assertIsNotNone(graph)

        filename = "test_graph_visualization.png"
        saved_file = save_graph_visualization(graph, filename)
        self.assertIsNotNone(saved_file)
        self.assertTrue(saved_file.endswith(".png"))

if __name__ == "__main__":
    unittest.main()
