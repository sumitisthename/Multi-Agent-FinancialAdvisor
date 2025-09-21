import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from real_time.data_ingestor import DataIngestor
from real_time.live_state import LiveState
from real_time.trading_agent import TradingAgent

class TestRealTimeComponents(unittest.TestCase):

    def test_data_ingestor(self):
        with patch('yfinance.download') as mock_download:
            # Mock the return value of yfinance.download
            mock_data = {
                ('Close', 'AAPL'): [150.0],
                ('Close', 'TSLA'): [300.0]
            }
            index = [pd.to_datetime("2025-09-20 15:00:00")]
            mock_df = pd.DataFrame(mock_data, index=index)
            mock_df.columns = pd.MultiIndex.from_tuples(mock_df.columns)
            mock_download.return_value = mock_df

            ingestor = DataIngestor(assets=["AAPL", "TSLA"])
            latest_data = ingestor.fetch_live_data()

            self.assertIsNotNone(latest_data)
            self.assertEqual(latest_data.shape[0], 1)
            self.assertIn(('Close', 'AAPL'), latest_data.columns)

    def test_live_state(self):
        live_state = LiveState()
        self.assertTrue(live_state.market_data.empty)

        data = {
            ('Close', 'AAPL'): [150.0],
        }
        index = [pd.to_datetime("2025-09-20 15:00:00")]
        new_data = pd.DataFrame(data, index=index)
        new_data.columns = pd.MultiIndex.from_tuples(new_data.columns)

        live_state.update_market_data(new_data)
        self.assertEqual(live_state.get_latest_price('AAPL'), 150.0)
        self.assertIsNotNone(live_state.timestamp)

    @patch('real_time.trading_agent.run_forecast_model')
    @patch('real_time.trading_agent.detect_anomalies')
    def test_trading_agent_buy_decision(self, mock_detect_anomalies, mock_run_forecast):
        # Mock the external dependencies
        mock_run_forecast.return_value = "Forecast: Positive trend"
        mock_detect_anomalies.return_value = []

        live_state = LiveState()
        trading_agent = TradingAgent(live_state)

        decision = trading_agent.make_decision("AAPL")
        self.assertEqual(decision, "BUY")

    @patch('real_time.trading_agent.run_forecast_model')
    @patch('real_time.trading_agent.detect_anomalies')
    def test_trading_agent_sell_decision(self, mock_detect_anomalies, mock_run_forecast):
        # Mock the external dependencies
        mock_run_forecast.return_value = "Forecast: Negative trend"
        mock_detect_anomalies.return_value = []

        live_state = LiveState()
        trading_agent = TradingAgent(live_state)

        decision = trading_agent.make_decision("TSLA")
        self.assertEqual(decision, "SELL")

    @patch('real_time.trading_agent.run_forecast_model')
    @patch('real_time.trading_agent.detect_anomalies')
    def test_trading_agent_hold_decision_on_anomaly(self, mock_detect_anomalies, mock_run_forecast):
        # Mock the external dependencies
        mock_run_forecast.return_value = "Forecast: Positive trend"
        mock_detect_anomalies.return_value = ["High Volatility"]

        live_state = LiveState()
        trading_agent = TradingAgent(live_state)

        decision = trading_agent.make_decision("AAPL")
        self.assertEqual(decision, "HOLD")

if __name__ == '__main__':
    unittest.main()
