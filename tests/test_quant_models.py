import sys
import os
import pandas as pd
import warnings

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



# Suppress specific known warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


from tools.quant_models import run_forecast_model, detect_anomalies

def test_run_forecast_model():
    config = {}
    assets = ["AAPL", "TSLA", "NVDA"]
    date = "2025-06-13"

    output = run_forecast_model(assets, date, config)
    print("\n=== Forecast Model Output ===")
    print(output)

    csv_path = f"./forecasts/forecast_{date}.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print("\n=== Forecast CSV Data ===")
        print(df.head())
    else:
        print("\n⚠️ CSV not found.")

def test_detect_anomalies():
    sample_transactions = [
        {"asset": "AAPL", "price": 250, "volume": 1000},
        {"asset": "AAPL", "price": 300, "volume": 500},
        {"asset": "AAPL", "price": 50, "volume": 10000},  # likely anomaly
    ]
    config = {}
    forecast_text = "AAPL: expected return +3.2%"

    result = detect_anomalies(sample_transactions, forecast_text, config)
    print("\n=== Anomaly Detection Result ===")
    print(result)
if __name__ == "__main__":
    test_run_forecast_model()
    test_detect_anomalies()