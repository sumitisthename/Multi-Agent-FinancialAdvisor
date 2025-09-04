import unittest
import logging
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import os

# For optional IPython inline display (won't fail if IPython not installed)
try:
    from IPython.display import Image, display
except ImportError:
    Image = None
    display = None

# Adjust import path to your actual module
from graph.graph_builder import build_graph
from langchain_core.messages import AIMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.config = {"api_key": "test_api_key"}

    def test_build_graph(self):
        with patch('agents.economic_indicator.os.getenv') as mock_getenv, \
             patch('agents.market_analysis.os.getenv') as mock_getenv_market, \
             patch('agents.forecasting_strategy.os.getenv') as mock_getenv_forecast, \
             patch('agents.risk_anomaly.os.getenv') as mock_getenv_risk, \
             patch('agents.compliance_monitor.os.getenv') as mock_getenv_compliance, \
             patch('agents.coordinator.os.getenv') as mock_getenv_coordinator, \
             patch('agents.memory_reflection.os.getenv') as mock_getenv_memory:
            mock_getenv.return_value = "DUMMY_KEY"
            mock_getenv_market.return_value = "DUMMY_KEY"
            mock_getenv_forecast.return_value = "DUMMY_KEY"
            mock_getenv_risk.return_value = "DUMMY_KEY"
            mock_getenv_compliance.return_value = "DUMMY_KEY"
            mock_getenv_coordinator.return_value = "DUMMY_KEY"
            mock_getenv_memory.return_value = "DUMMY_KEY"

            graph = build_graph(self.config)
            self.assertIsNotNone(graph)
        logger.info(f"Graph object type: {type(graph)}")

    def test_graph_invoke(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "DUMMY_KEY"}):
            # Mock the LLM responses
            with patch('langchain_groq.ChatGroq._generate') as mock_generate:
                from langchain_core.outputs import ChatGeneration, ChatResult
                mock_generation = ChatGeneration(message=AIMessage(content="Mocked LLM response."))
                mock_result = ChatResult(generations=[mock_generation])
                mock_generate.return_value = mock_result

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

        logger.info(f"Graph invoke result: {result}")

        self.assertIsInstance(result, dict)
        self.assertIn("final_decision", result)


if __name__ == "__main__":
    unittest.main()
