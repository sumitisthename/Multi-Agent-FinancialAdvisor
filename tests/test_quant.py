# tests/test_quant_models.py

from tools.quant_models import run_forecast_model, detect_anomalies
import datetime

assets = ['AAPL', 'GOOGL']
date = datetime.date.today().strftime("%Y-%m-%d")
config = {}

print("\n=== 🔮 Forecast Output ===")
forecast_output = run_forecast_model(assets, date, config)
print(forecast_output)

print("\n=== ⚠️ Anomaly Detection ===")
sample_transactions = [
    {"price": 100, "volume": 20},
    {"price": 102, "volume": 18},
    {"price": 99, "volume": 25},
    {"price": 200, "volume": 2},  # likely anomaly
    {"price": 101, "volume": 22},
]
anomaly_output = detect_anomalies(sample_transactions, forecast_output, config)
print(anomaly_output)
