import unittest
from tools.quant_models import run_forecast_model, detect_anomalies
import datetime

class TestQuantModels(unittest.TestCase):

    def test_run_forecast_model(self):
        assets = ['AAPL', 'GOOGL']
        date = datetime.date.today().strftime("%Y-%m-%d")
        forecast_output = run_forecast_model(assets, date)
        print("\n=== 🔮 Forecast Output ===")
        print(forecast_output)
        self.assertIsInstance(forecast_output, str)

    def test_detect_anomalies(self):
        sample_transactions = [
            {"price": 100, "volume": 20},
            {"price": 102, "volume": 18},
            {"price": 99, "volume": 25},
            {"price": 200, "volume": 2},  # likely anomaly
            {"price": 101, "volume": 22},
        ]
        forecast_output = "Some forecast text"
        anomaly_output = detect_anomalies(sample_transactions, forecast_output)
        print("\n=== ⚠️ Anomaly Detection ===")
        print(anomaly_output)
        self.assertIsInstance(anomaly_output, str)

if __name__ == '__main__':
    unittest.main()
