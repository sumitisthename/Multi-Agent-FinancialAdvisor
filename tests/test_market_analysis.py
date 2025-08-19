import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from agents.market_analysis import market_analysis_node
from config.settings import load_config

# Load .env
load_dotenv()

@pytest.fixture
def dummy_state():
    return {
        "timestamp": "2024-05-01T00:00:00Z",
        "assets": ["AAPL", "GOOGL"],
        "user_query": "Summarize market trend"
    }

@patch('agents.market_analysis.ChatGroq')
@patch('agents.market_analysis.fetch_news_data')
@patch('agents.market_analysis.fetch_market_data')
def test_market_agent_run(mock_fetch_market, mock_fetch_news, MockChatGroq, dummy_state):
    # Create a mock instance of the LLM
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = "This is a mock market summary."
    MockChatGroq.return_value = mock_llm_instance

    # Mock the external data fetcher responses
    mock_fetch_market.return_value = {"AAPL": 150.0, "GOOGL": 2800.0}
    mock_fetch_news.return_value = ["Fake news about AAPL", "Fake news about GOOGL"]

    config = load_config()

    # Run agent
    result_state = market_analysis_node(config)(dummy_state)

    # Check output
    assert "market_summary" in result_state
    assert result_state["market_summary"] == "This is a mock market summary."
    print("\nMarket Summary:", result_state["market_summary"])
