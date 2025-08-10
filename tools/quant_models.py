import glob  # Correct import for glob module
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
        
        if "Forecast" in record and "Latest Price" not in record:  # Error cases
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

def get_numerical_forecast(assets, end_date_str, model_type='arima', save_intermediate_files=False):
    """
    Runs a forecast for a list of assets up to a given end date using the specified model.
    
    Args:
        assets (list[str]): List of asset tickers.
        end_date_str (str): The end date for historical data (ISO format).
        model_type (str): The type of model to use ('arima' or 'moving_average').
        save_intermediate_files (bool): If True, saves raw asset data to CSV.

    Returns:
        list[dict]: A list of dictionaries, each containing forecast results for an asset.
    """
    forecast_records = []
    end_date = pd.to_datetime(end_date_str)

    for asset in assets:
        try:
            logger.info(f"📥 Fetching price data for {asset} up to {end_date.date()}")
            df = yf.download(asset, end=end_date, period="60d", interval="1d", auto_adjust=False)

            if save_intermediate_files:
                df_reset = df.reset_index()
                df_reset['timestamp'] = pd.Timestamp.now()
                safe_date = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                asset_csv_path = f"forecasts/assets-{asset}-{safe_date}.csv"
                df_reset.to_csv(asset_csv_path, index=False)
                logger.info(f"✅ Asset CSV saved: {asset_csv_path}")

            prices = df[['Close']].dropna()
            if len(prices) < 10:
                logger.warning(f"({model_type}) {asset}: Not enough data to forecast ({len(prices)} data points).")
                forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                continue

            price_series = prices['Close'].asfreq('D', method='pad')
            forecast = 0.0

            if model_type == 'arima':
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ARIMA(price_series, order=(3, 1, 2))
                    fitted_model = model.fit()
                    forecast_value = fitted_model.forecast(steps=1)
                forecast = float(forecast_value.iloc[0])

            elif model_type == 'moving_average':
                window_size = 5
                if len(price_series) >= window_size:
                    moving_average = price_series.rolling(window=window_size).mean()
                    forecast = float(moving_average.iloc[-1])
                else:
                    logger.warning(f"({model_type}) {asset}: Not enough data for window size {window_size}.")
                    forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                    continue

            else:
                raise ValueError(f"Unknown model_type: {model_type}")

            latest_price = float(price_series.iloc[-1])
            change_pct = ((forecast - latest_price) / latest_price) * 100

            forecast_date = price_series.index[-1] + pd.Timedelta(days=1)

            forecast_records.append({
                "Asset": asset,
                "Latest Price": round(latest_price, 2),
                "Forecasted Price": round(forecast, 2),
                "Expected Return (%)": round(change_pct, 2),
                "Forecast Date": forecast_date.strftime('%Y-%m-%d'),
                "Model": model_type
            })

        except Exception as e:
            logger.error(f"❌ Forecasting failed for {asset} with model {model_type}:\n{traceback.format_exc()}")
            forecast_records.append({"Asset": asset, "Forecast": "Failed", "Model": model_type})

    return forecast_records

def run_forecast_model(assets, date, config):
    """
    Original function to run forecast, now refactored to use get_numerical_forecast.
    It saves results to CSV and returns a formatted table for the agents.
    """
    assets = config.get("assets", assets)  # allow dynamic override

    os.makedirs("forecasts", exist_ok=True)

    # Clean up old forecast files
    files = glob.glob("forecasts/*")
    for f in files:
        try:
            os.remove(f)
            logger.info(f"[SUCCESS] Deleted old forecast file: {f}")
        except Exception as e:
            logger.warning(f"[ERROR] Could not delete file {f}: {e}")

    # Get numerical data, allowing intermediate files to be saved as before
    forecast_records = get_numerical_forecast(assets, date, save_intermediate_files=True)

    # Save combined forecast summary
    if forecast_records:
        try:
            forecast_df = pd.DataFrame(forecast_records)
            # Use a safe filename based on the run date
            safe_date_str = pd.to_datetime(date).strftime("%Y-%m-%d")
            summary_path = f"forecasts/forecast-{safe_date_str}.csv"
            forecast_df.to_csv(summary_path, index=False)
            logger.info(f"✅ Forecast summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save forecast CSV: {e}")

    # Return formatted table for compatibility with other agents
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
