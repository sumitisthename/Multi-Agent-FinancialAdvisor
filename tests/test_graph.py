import unittest
from unittest.mock import patch
from graph.graph_builder import build_graph

class TestGraph(unittest.TestCase):

    def test_graph_execution(self):
        with patch('agents.market_analysis.fetch_market_data') as mock_fetch_market_data, \
             patch('agents.market_analysis.fetch_news_data') as mock_fetch_news_data, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq, \
             patch('agents.forecasting_strategy.run_forecast_model') as mock_run_forecast_model, \
             patch('agents.forecasting_strategy.log_decision') as mock_log_decision, \
             patch('agents.risk_anomaly.fetch_transaction_data') as mock_fetch_transaction_data, \
             patch('agents.risk_anomaly.detect_anomalies') as mock_detect_anomalies, \
             patch('agents.compliance_monitor.extract_compliance_rules') as mock_extract_compliance_rules, \
             patch('agents.memory_reflection.retrieve_recent_memory') as mock_retrieve_recent_memory, \
             patch('agents.memory_reflection.log_decision') as mock_memory_log_decision:

            # Mock return values
            mock_fetch_market_data.return_value = "Market data"
            mock_fetch_news_data.return_value = "News data"
            mock_run_forecast_model.return_value = "Forecast data"
            mock_fetch_transaction_data.return_value = "Transaction data"
            mock_detect_anomalies.return_value = "Anomalies"
            mock_extract_compliance_rules.return_value = "Compliance rules"
            mock_retrieve_recent_memory.return_value = "Recent memory"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.side_effect = [
                "Market summary",
                "Forecast",
                "Risk report",
                "Compliance review",
                "Final decision",
                "Reflection lesson"
            ]

            # Build the graph
            graph = build_graph()

            # Define the initial state
            initial_state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z"
            }

            # Invoke the graph
            result = graph.invoke(initial_state)

            # Assert the final state
            self.assertEqual(result["market_summary"], "Market summary")
            self.assertEqual(result["forecast"], "Forecast")
            self.assertEqual(result["risk_report"], "Risk report")
            self.assertEqual(result["compliance_review"], "Compliance review")
            self.assertEqual(result["final_decision"], "Final decision")
            self.assertEqual(result["reflection_lesson"], "Reflection lesson")

if __name__ == '__main__':
    unittest.main()
