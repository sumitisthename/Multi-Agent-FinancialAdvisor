import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dotenv import load_dotenv
from agents.market_analysis import market_analysis_node
from config.settings import load_config



# Load .env
load_dotenv()

@pytest.fixture
def set_api_key():
    os.environ['GROQ_API_KEY'] = 'test_key'

@pytest.fixture
def dummy_state():
    return {
        "timestamp": "2024-05-01T00:00:00Z",
        "assets": ["AAPL", "GOOGL"],
        "user_query": "Summarize market trend"
    }

def test_market_agent_run(dummy_state, set_api_key):
    config = load_config()

    # Run agent
    result_state = market_analysis_node(config)(dummy_state)

    # Check output
    assert "market_summary" in result_state
    assert isinstance(result_state["market_summary"], str)
    print("\nMarket Summary:", result_state["market_summary"])
