# tools/quant_models.py

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.logger import get_logger
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
import os
import traceback

logger = get_logger()

def run_forecast_model(assets, date, config):
    forecasts = []
    forecast_records = []

    for asset in assets:
        try:
            logger.info(f"Fetching price data for {asset}")
            df = yf.download(asset, period="60d", interval="1d", auto_adjust=False)
            prices = df['Close'].dropna()

            if len(prices) < 10:
                forecasts.append(f"{asset}: Not enough data to forecast.")
                forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                continue

            # Ensure regular daily frequency
            prices = prices.asfreq('D', method='pad')

            # Fit ARIMA model
            model = ARIMA(prices, order=(3, 1, 2))
            fitted_model = model.fit()
            forecast_value = fitted_model.forecast(steps=1)
            forecast = float(forecast_value.iloc[0])
            latest_price = float(prices.iloc[-1])
            change_pct = ((forecast - latest_price) / latest_price) * 100

            forecasts.append(f"{asset}: expected return {change_pct:+.2f}%")
            forecast_records.append({
                "Asset": asset,
                "Latest Price": round(latest_price, 2),
                "Forecasted Price": round(forecast, 2),
                "Expected Return (%)": round(change_pct, 2)
            })

        except Exception as e:
            logger.error(f"❌ Forecasting failed for {asset}:\n{traceback.format_exc()}")
            forecast_records.append({"Asset": asset, "Forecast": "Failed"})

    # Save to CSV
    try:
        forecast_df = pd.DataFrame(forecast_records)
        os.makedirs("forecasts", exist_ok=True)
        csv_path = f"forecasts/forecast_{date}.csv"
        forecast_df.to_csv(csv_path, index=False)
        logger.info(f"✅ Forecast CSV saved to {csv_path}")
    except Exception as e:
        logger.error(f"Failed to save forecast CSV: {e}")

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