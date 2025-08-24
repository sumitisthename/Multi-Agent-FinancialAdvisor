import glob
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


def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def format_forecast_table(forecast_records):
    """Format forecast records into a readable table"""
    if not forecast_records:
        return "No forecast data available."

    # Markdown table header
    table = "| Asset | Latest Price | Forecasted Price | Expected Return (%) | MAPE (%) | Status |\n"
    table += "|-------|--------------|------------------|--------------------|----------|---------|\n"

    for record in forecast_records:
        asset = record.get("Asset", "N/A")

        if "Forecast" in record:  # Error or no-data cases
            status = record["Forecast"]
            table += f"| {asset} | - | - | - | - | {status} |\n"
        else:
            latest = record.get("Latest Price", "N/A")
            forecasted = record.get("Forecasted Price", "N/A")
            return_pct = record.get("Expected Return (%)", "N/A")
            mape = record.get("MAPE", "N/A")

            # Simple status check (using text instead of emojis)
            if isinstance(return_pct, (int, float)):
                if return_pct > 0:
                    status = "BULLISH"
                elif return_pct < -5:
                    status = "BEARISH"
                else:
                    status = "NEUTRAL"
            else:
                status = "UNKNOWN"

            table += f"| {asset} | ${latest} | ${forecasted} | {return_pct:+.2f}% | {mape:.2f} | {status} |\n"

    return table


def run_forecast_model(assets, date, config):
    """Run forecasting model on financial assets"""
    forecasts = []
    forecast_records = []
    all_mapes = []

    assets = config.get("assets", assets)  # allow dynamic override

    os.makedirs("forecasts", exist_ok=True)

    # Clean old forecast files
    files = glob.glob("forecasts/*")
    for f in files:
        try:
            os.remove(f)
            logger.info(f"[SUCCESS] Deleted old forecast file: {f}")
        except Exception as e:
            logger.warning(f"[ERROR] Could not delete file {f}: {e}")

    for asset in assets:
        try:
            logger.info(f"Fetching price data for {asset}")
            df = yf.download(asset, period="60d", interval="1d", auto_adjust=False)

            if df.empty:
                logger.warning(f"No data available for {asset}")
                forecast_records.append({"Asset": asset, "Forecast": "No data available"})
                continue

            df = df.reset_index()
            df['timestamp'] = pd.Timestamp.now()

            # Windows-compatible filename (replace colons with hyphens)
            safe_date = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            asset_csv_path = f"forecasts/assets-{asset.replace(':', '-')}-{safe_date}.csv"
            df.to_csv(asset_csv_path, index=False)
            logger.info(f"Asset CSV saved: {asset_csv_path}")

            # Forecast logic
            prices = df[['Date', 'Close']].dropna()
            if len(prices) < 20:  # Need enough data for train/test split
                forecasts.append(f"{asset}: Not enough data to forecast.")
                forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                continue

            prices.set_index('Date', inplace=True)
            prices.index = pd.to_datetime(prices.index)
            price_series = prices['Close'].asfreq('D', method='pad')

            # Train/test split for MAPE calculation
            train_size = int(len(price_series) * 0.9)
            train, test = price_series[0:train_size], price_series[train_size:]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = ARIMA(train, order=(3, 1, 2))
                fitted_model = model.fit()

                # Forecast for the test period to calculate MAPE
                test_forecast = fitted_model.forecast(steps=len(test))
                mape = calculate_mape(test.values, test_forecast.values)
                all_mapes.append(mape)

                # Full model forecast
                full_model = ARIMA(price_series, order=(3, 1, 2))
                fitted_full_model = full_model.fit()
                forecast_value = fitted_full_model.forecast(steps=1)

            forecast = float(forecast_value.iloc[0])
            latest_price = float(price_series.iloc[-1].item())
            change_pct = ((forecast - latest_price) / latest_price) * 100

            forecasts.append(f"{asset}: expected return {change_pct:+.2f}% (MAPE: {mape:.2f}%)")
            forecast_records.append({
                "Asset": asset,
                "Latest Price": round(latest_price, 2),
                "Forecasted Price": round(forecast, 2),
                "Expected Return (%)": round(change_pct, 2),
                "MAPE": mape
            })

        except Exception as e:
            logger.error(f"Forecasting failed for {asset}: {str(e)}")
            forecast_records.append({"Asset": asset, "Forecast": "Failed"})

    # Save combined forecast summary with Windows-compatible filename
    try:
        forecast_df = pd.DataFrame(forecast_records)
        # Replace colons and other invalid characters in the date string
        safe_date = date.replace(':', '-').replace('T', '_')
        summary_path = f"forecasts/forecast-{safe_date}.csv"
        forecast_df.to_csv(summary_path, index=False)
        logger.info(f"Forecast summary saved to {summary_path}")
    except Exception as e:
        logger.error(f"Failed to save forecast CSV: {str(e)}")

    # Return both the formatted table and the average MAPE
    avg_mape = np.mean(all_mapes) if all_mapes else 0
    return format_forecast_table(forecast_records), avg_mape


def detect_anomalies(transactions, forecast_text, config):
    """Detect anomalies in transaction data"""
    logger.info("Running anomaly detection on transaction data")

    try:
        df = pd.DataFrame(transactions)

        # Use available numeric columns instead of hardcoding
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return "No numeric features available for anomaly detection."

        features_df = df[numeric_cols].fillna(0)

        model = IsolationForest(contamination=0.2, random_state=42)
        df['anomaly_score'] = model.fit_predict(features_df)

        anomalies = df[df['anomaly_score'] == -1].to_dict(orient='records')
        return f"{len(anomalies)} anomalies detected: {anomalies}" if anomalies else "No anomalies."

    except Exception as e:
        logger.error(f"Error during anomaly detection: {str(e)}")
        return "Anomaly detection failed."


def run_quant_models(assets, date, transactions, config):
    """Run quantitative models including forecasting and anomaly detection"""
    logger.info("Running quantitative models...")

    forecast_text, avg_mape = run_forecast_model(assets, date, config)
    logger.info(f"Forecast results:\n{forecast_text}")
    logger.info(f"Average MAPE: {avg_mape:.2f}%")

    anomaly_text = detect_anomalies(transactions, forecast_text, config)
    logger.info(f"Anomaly detection results:\n{anomaly_text}")

    return {
        "forecast": forecast_text,
        "anomalies": anomaly_text,
        "mape": avg_mape
    }