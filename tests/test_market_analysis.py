from dotenv import load_dotenv
load_dotenv()

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from agents.market_analysis import market_analysis_node
from config.settings import load_config
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage



@pytest.fixture
def dummy_state():
    return {
        "timestamp": "2024-05-01T00:00:00Z",
        "assets": ["AAPL", "GOOGL"],
        "user_query": "Summarize market trend"
    }

def test_market_agent_run(dummy_state):
    with patch.dict(os.environ, {"GROQ_API_KEY": "DUMMY_KEY"}):
        # Mock the LLM response
        with patch('langchain_groq.ChatGroq._generate') as mock_generate:
            from langchain_core.outputs import ChatGeneration, ChatResult
            mock_generation = ChatGeneration(message=AIMessage(content="Market is bullish for AAPL and GOOGL."))
            mock_result = ChatResult(generations=[mock_generation])
            mock_generate.return_value = mock_result

            config = load_config()

            # Run agent
            result_state = market_analysis_node(config)(dummy_state)

            # Check output
            assert "market_summary" in result_state
            assert isinstance(result_state["market_summary"], str)
            print("\nMarket Summary:", result_state["market_summary"])
