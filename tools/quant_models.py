# tools/quant_models.py

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.logger import get_logger

logger = get_logger()


def run_forecast_model(assets, date, config):
    logger.info("Running basic forecast model")
    
    # Mock forecast output (can replace with ARIMA, LSTM, etc.)
    forecasts = []
    for i, asset in enumerate(assets):
        change = round(np.random.uniform(-0.05, 0.1), 3)
        forecasts.append(f"{asset}: expected return +{change*100:.2f}%")

    return "\n".join(forecasts)


def detect_anomalies(transactions, forecast_text, config):
    logger.info("Running anomaly detection on transaction data")

    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    try:
        model = IsolationForest(contamination=0.2, random_state=42)
        df['anomaly_score'] = model.fit_predict(df[['price', 'volume']])

        anomalies = df[df['anomaly_score'] == -1].to_dict(orient='records')
        return f"{len(anomalies)} anomalies detected: {anomalies}" if anomalies else "No anomalies."
    except Exception as e:
        logger.error(f"Error during anomaly detection: {e}")
        return "Anomaly detection failed."