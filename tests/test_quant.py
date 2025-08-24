import os
import sys

# 1️⃣ Add project root to sys.path BEFORE any imports from your project
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now project imports work
from tools.quant_models import run_forecast_model, detect_anomalies

# Standard imports
import unittest
import datetime
import warnings
import yfinance as yf
import pandas as pd
from sklearn.exceptions import ConvergenceWarning

# Optional: import only if exists
try:
    from tools.quant_models import evaluate_forecasts
    HAS_EVAL = True
except ImportError:
    HAS_EVAL = False

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestQuantModels(unittest.TestCase):

    def test_run_forecast_model(self):
        assets = ['AAPL', 'GOOGL']
        date = datetime.date.today().strftime("%Y-%m-%d")
        forecast_output = run_forecast_model(assets, date, config={})
        print("\n=== 🔮 Forecast Output ===")
        print(forecast_output)
        self.assertIsInstance(forecast_output, str)

    def test_detect_anomalies(self):
        transactions = [
            {"price": 100, "volume": 20},
            {"price": 102, "volume": 18},
            {"price": 99, "volume": 25},
            {"price": 200, "volume": 2},  # anomaly
            {"price": 101, "volume": 22},
        ]
        forecast_output = "Forecasted data"
        result = detect_anomalies(transactions, forecast_output, config={})
        print("\n=== ⚠️ Anomaly Detection ===")
        print(result)
        self.assertIsInstance(result, str)

    @unittest.skipUnless(HAS_EVAL, "evaluate_forecasts not implemented in this version")
    def test_evaluate_forecasts(self):
        assets = ['AAPL']
        date = datetime.date.today().strftime("%Y-%m-%d")
        run_forecast_model(assets, date, config={})

        forecast_df = pd.read_csv(f"forecasts/forecast-{date}.csv")
        forecast_records = forecast_df.to_dict(orient="records")

        actual_prices = {}
        for asset in assets:
            data = yf.download(asset, period="1d", interval="1d")
            if not data.empty:
                actual_prices[asset] = round(data["Close"].iloc[0], 2)
            else:
                self.fail(f"Failed to fetch actual price for {asset}")

        results = evaluate_forecasts(forecast_records, actual_prices)
        print("\n=== 📏 Evaluation Metrics ===")
        print(results)
        self.assertIsInstance(results, dict)
        self.assertIn('AAPL', results)


if __name__ == '__main__':
    unittest.main()
