import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.logger import get_logger
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
import os
import traceback
from datetime import datetime

logger = get_logger()

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

def format_forecast_table(forecast_records):
    """Format forecast records into a readable table"""
    if not forecast_records:
        return "No forecast data available."
    
    # Create markdown table
    table = "| Asset | Latest Price | Forecasted Price | Expected Return (%) | Status |\n"
    table += "|-------|--------------|------------------|--------------------|---------|\n"
    
    for record in forecast_records:
        asset = record.get("Asset", "N/A")
        
        if "Forecast" in record:  # Error cases
            status = record["Forecast"]
            table += f"| {asset} | - | - | - | {status} |\n"
        else:  # Successful forecasts
            latest = record.get("Latest Price", "N/A")
            forecasted = record.get("Forecasted Price", "N/A")
            return_pct = record.get("Expected Return (%)", "N/A")
            
            # Add color indicators
            if isinstance(return_pct, (int, float)):
                if return_pct > 0:
                    status = "📈 Bullish"
                elif return_pct < -5:
                    status = "📉 Bearish"
                else:
                    status = "📊 Neutral"
            else:
                status = "❓ Unknown"
            
            table += f"| {asset} | ${latest} | ${forecasted} | {return_pct:+.2f}% | {status} |\n"
    
    return table

def run_forecast_model(assets, date, config):
    forecasts = []
    forecast_records = []

    assets = config.get("assets", assets)  # allow dynamic override

    os.makedirs("forecasts", exist_ok=True)

    for asset in assets:
        try:
            logger.info(f"📥 Fetching price data for {asset}")
            df = yf.download(asset, period="60d", interval="1d", auto_adjust=False)

            # Save raw asset prices
            df = df.reset_index()  # 'Date' column from index
            df['timestamp'] = pd.Timestamp.now()
            safe_date = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            asset_csv_path = f"forecasts/assets-{asset}-{safe_date}.csv"
            df.to_csv(asset_csv_path, index=False)
            logger.info(f"✅ Asset CSV saved: {asset_csv_path}")
            logger.debug(df.head(6))

            # Forecast logic
            prices = df[['Date', 'Close']].dropna()
            if len(prices) < 10:
                forecasts.append(f"{asset}: Not enough data to forecast.")
                forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                continue

            prices.set_index('Date', inplace=True)
            prices.index = pd.to_datetime(prices.index)
            price_series = prices['Close'].asfreq('D', method='pad')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = ARIMA(price_series, order=(3, 1, 2))
                fitted_model = model.fit()
                forecast_value = fitted_model.forecast(steps=1)

            forecast = float(forecast_value.iloc[0])
            latest_price = float(price_series.iloc[-1].item())
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

    # Save combined forecast summary
    try:
        forecast_df = pd.DataFrame(forecast_records)
        summary_path = f"forecasts/forecast-{date}.csv"
        forecast_df.to_csv(summary_path, index=False)
        logger.info(f"✅ Forecast summary saved to {summary_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save forecast CSV: {e}")

    # Return formatted table instead of simple string list
    return format_forecast_table(forecast_records)


def detect_anomalies(transactions, forecast_text, config):
    logger.info("📊 Running anomaly detection on transaction data")

    try:
        df = pd.DataFrame(transactions)
        model = IsolationForest(contamination=0.2, random_state=42)
        df['anomaly_score'] = model.fit_predict(df[['price', 'volume']])
        anomalies = df[df['anomaly_score'] == -1].to_dict(orient='records')
        return f"{len(anomalies)} anomalies detected: {anomalies}" if anomalies else "No anomalies."
    except Exception as e:
        logger.error(f"❌ Error during anomaly detection: {e}")
        return "Anomaly detection failed."

def run_quant_models(assets, date, transactions, config):
    logger.info("🔍 Running quantitative models...")

    # Run forecast model
    forecast_text = run_forecast_model(assets, date, config)
    logger.info(f"Forecast results:\n{forecast_text}")

    # Run anomaly detection
    anomaly_text = detect_anomalies(transactions, forecast_text, config)
    logger.info(f"Anomaly detection results:\n{anomaly_text}")

    return {
        "forecast": forecast_text,
        "anomalies": anomaly_text
    }