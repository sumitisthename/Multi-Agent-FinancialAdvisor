import unittest
from unittest.mock import patch, MagicMock
from agents.market_analysis import market_analysis_node
from agents.forecasting_strategy import forecasting_node
from agents.risk_anomaly import risk_node
from agents.compliance_monitor import compliance_node
from agents.coordinator import coordinator_node
from agents.memory_reflection import memory_reflection_node

class TestAgents(unittest.TestCase):

    def test_market_analysis_node(self):
        with patch('agents.market_analysis.fetch_market_data') as mock_fetch_market_data, \
             patch('agents.market_analysis.fetch_news_data') as mock_fetch_news_data, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_fetch_market_data.return_value = "Market data"
            mock_fetch_news_data.return_value = "News data"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Market summary"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z"
            }

            node = market_analysis_node()
            result = node(state)

            self.assertEqual(result["market_summary"], "Market summary")

    def test_forecasting_node(self):
        with patch('agents.forecasting_strategy.run_forecast_model') as mock_run_forecast_model, \
             patch('agents.forecasting_strategy.log_decision') as mock_log_decision, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_run_forecast_model.return_value = "Forecast data"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Forecast"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z",
                "market_summary": "Market summary"
            }

            node = forecasting_node()
            result = node(state)

            self.assertEqual(result["forecast"], "Forecast")
            mock_log_decision.assert_called_once()

    def test_risk_node(self):
        with patch('agents.risk_anomaly.fetch_transaction_data') as mock_fetch_transaction_data, \
             patch('agents.risk_anomaly.detect_anomalies') as mock_detect_anomalies, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_fetch_transaction_data.return_value = "Transaction data"
            mock_detect_anomalies.return_value = "Anomalies"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Risk report"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z",
                "market_summary": "Market summary",
                "forecast": "Forecast"
            }

            node = risk_node()
            result = node(state)

            self.assertEqual(result["risk_report"], "Risk report")
            self.assertEqual(result["anomalies"], "Anomalies")

    def test_compliance_node(self):
        with patch('agents.compliance_monitor.extract_compliance_rules') as mock_extract_compliance_rules, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_extract_compliance_rules.return_value = "Compliance rules"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Compliance review"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z",
                "market_summary": "Market summary",
                "forecast": "Forecast",
                "risk_report": "Risk report"
            }

            node = compliance_node()
            result = node(state)

            self.assertEqual(result["compliance_review"], "Compliance review")

    def test_coordinator_node(self):
        with patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Final decision"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z",
                "market_summary": "Market summary",
                "forecast": "Forecast",
                "risk_report": "Risk report",
                "compliance_review": "Compliance review"
            }

            node = coordinator_node()
            result = node(state)

            self.assertEqual(result["final_decision"], "Final decision")

    def test_memory_reflection_node(self):
        with patch('agents.memory_reflection.retrieve_recent_memory') as mock_retrieve_recent_memory, \
             patch('agents.memory_reflection.log_decision') as mock_log_decision, \
             patch('langchain_groq.ChatGroq') as mock_chat_groq:

            mock_retrieve_recent_memory.return_value = "Recent memory"

            mock_chat_groq_instance = mock_chat_groq.return_value
            mock_chat_groq_instance.invoke.return_value = "Reflection lesson"

            state = {
                "assets": ["AAPL", "GOOG"],
                "timestamp": "2024-01-01T00:00:00Z",
                "market_summary": "Market summary",
                "forecast": "Forecast",
                "risk_report": "Risk report",
                "compliance_review": "Compliance review",
                "final_decision": "Final decision"
            }

            node = memory_reflection_node()
            result = node(state)

            self.assertEqual(result["reflection_lesson"], "Reflection lesson")
            mock_log_decision.assert_called_once()

if __name__ == '__main__':
    unittest.main()
