import sys
import os
import pytest
from dotenv import load_dotenv
import pandas as pd

# Ensure root path is set before imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.forecasting_strategy import forecasting_node

load_dotenv()

@pytest.fixture
def sample_state():
    return {
        "assets": ["AAPL", "TSLA", "NVDA"],
        "timestamp": "2025-06-13",
        "market_summary": "Tech stocks are showing upward movement after earnings reports."
    }

def test_forecasting_node_outputs_forecast(sample_state):
    config = {}
    node = forecasting_node(config)
    result = node(sample_state)

    # ✅ Check structure
    assert "forecast" in result
    forecast_str = result["forecast"]
    assert isinstance(forecast_str, str)
    assert len(forecast_str.strip()) > 0

    print("\n=== Forecast Output ===")
    print(forecast_str)

    # ✅ Check CSV was written
    expected_path = f"forecasts/forecast_{sample_state['timestamp']}.csv"
    assert os.path.exists(expected_path), f"Expected forecast CSV not found: {expected_path}"

    # ✅ Optionally inspect content
    df = pd.read_csv(expected_path)
    print("\n=== CSV Forecast ===")
    print(df.head())

    assert not df.empty
    assert "Asset" in df.columns
    assert "Forecasted Price" in df.columns or "Forecast" in df.columns
