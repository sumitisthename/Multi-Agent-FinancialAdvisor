"""
Quantitative models for the LangGraph multi-agent financial analysis system.
"""
import itertools
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
from sklearn.metrics import mean_absolute_error, mean_squared_error

import mlflow
from mlflow import log_metric, log_param
import itertools


mlflow.set_tracking_uri("http://localhost:5000")  # or your desired location
mlflow.set_experiment("LangGraph_Quant_Forecasting")

logger = get_logger()

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

def format_float(value):
    return f"{value:.2f}" if pd.notnull(value) else "N/A"

def format_forecast_table(forecast_records):
    """
    Formats forecast records into a readable table.
    """
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
                    status = "[BULLISH] Bullish"
                elif return_pct < -5:
                    status = "[BEARISH] Bearish"
                else:
                    status = "[NEUTRAL] Neutral"
            else:
                status = "[UNKNOWN] Unknown"

            table += f"| {asset} | ${latest} | ${forecasted} | {return_pct:+.2f}% | {status} |\n"
    
    return table

# ARIMA model for forecasting
def run_forecast_model(assets, date):
    """
    Runs a forecast model for a list of assets.
    """
    forecasts = []
    forecast_records = []

    os.makedirs("forecasts", exist_ok=True)
    with mlflow.start_run(run_name=f"Forecast_{date}"):
        mlflow.log_param("date", date)
        mlflow.log_param("assets_count", len(assets))

        for asset in assets:
            try:
                logger.info(f"[INFO] Fetching price data for {asset}")
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
                    p = d = q = range(0, 5)
                    pdq = list(itertools.product(p, d, q))
                    best_aic = float("inf")
                    best_order = None
                    for order in pdq:
                        try:
                            model = ARIMA(price_series, order=order)
                            fitted_model = model.fit()
                            if fitted_model.aic < best_aic:
                                best_aic = fitted_model.aic
                                best_order = order
                        except:
                            continue
                    logger.info(f"Best ARIMA order: {best_order} with AIC: {best_aic}")


                    model = ARIMA(price_series, order=(best_order))
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
                # Log per asset metrics
                mlflow.log_param(f"{asset}_best_order", best_order)
                mlflow.log_metric(f"{asset}_best_aic", best_aic)
                mlflow.log_metric(f"{asset}_expected_return", round(change_pct, 2))
                mlflow.log_metric(f"{asset}_latest_price", round(latest_price, 2))
                mlflow.log_metric(f"{asset}_forecasted_price", round(forecast, 2))

            except Exception as e:
                logger.error(f"[ERROR] Forecasting failed for {asset}:\n{traceback.format_exc()}")
                forecast_records.append({"Asset": asset, "Forecast": "Failed"})

        # Save combined forecast summary
        try:
            forecast_df = pd.DataFrame(forecast_records)
            summary_path = f"forecasts/forecast-{date}.csv"
            forecast_df.to_csv(summary_path, index=False)
            logger.info(f"✅ Forecast summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save forecast CSV: {e}")

        # Return formatted table instead of simple string list
    return format_forecast_table(forecast_records), forecast_records

# Isolation Forest for anomaly detection
def detect_anomalies(transactions, forecast_text):
    """
    Detects anomalies in a list of transactions.
    """
    logger.info("[INFO] Running anomaly detection on transaction data")

    try:
        df = pd.DataFrame(transactions)
        model = IsolationForest(contamination=0.2, random_state=42)
        df['anomaly_score'] = model.fit_predict(df[['price', 'volume']])
        anomalies = df[df['anomaly_score'] == -1].to_dict(orient='records')
        return f"{len(anomalies)} anomalies detected: {anomalies}" if anomalies else "No anomalies."
    except Exception as e:
        logger.error(f"[ERROR]r during anomaly detection: {e}")
        return "Anomaly detection failed."

def run_quant_models(assets, date, transactions, actuals_dict=None):
    """
    Runs a suite of quantitative models.
    """
    logger.info("[INFO] Running quantitative models...")

    # Run forecast model
    forecast_text, forecast_records = run_forecast_model(assets, date)
    logger.info(f"Forecast results:\n{forecast_text}")

    # Run anomaly detection
    anomaly_text = detect_anomalies(transactions, forecast_text)
    logger.info(f"Anomaly detection results:\n{anomaly_text}")
    
    evaluation_results = None
    if actuals_dict:
        evaluation_results = evaluate_forecasts(forecast_records, actuals_dict)
        logger.info(f"Evaluation results:\n{evaluation_results}")

    return {
        "forecast": forecast_text,
        "anomalies": anomaly_text,
        "evaluation": evaluation_results
    }


def evaluate_forecasts(forecast_records, actuals_dict):

    logger.info("[INFO] Evaluating forecast accuracy...")
    evaluation_results = {}

    with mlflow.start_run(run_name="Forecast_Evaluation", nested=True):
        for record in forecast_records:
            asset = record.get("Asset")
            forecasted = record.get("Forecasted Price")
            if asset not in actuals_dict:
                logger.warning(f"No actual price available for {asset}, skipping.")
                continue

            actual_price = actuals_dict[asset]
            predicted_price = forecasted

            # Calculate metrics
            mae = mean_absolute_error([actual_price], [predicted_price])
            mse = mean_squared_error([actual_price], [predicted_price])
            rmse = np.sqrt(mse)

            # Log to MLflow
            mlflow.log_metric(f"{asset}_MAE", mae)
            mlflow.log_metric(f"{asset}_MSE", mse)
            mlflow.log_metric(f"{asset}_RMSE", rmse)

        # Store results
        evaluation_results[asset] = {
            "MAE": round(mae, 4),
            "MSE": round(mse, 4),
            "RMSE": round(rmse, 4),
            "Actual Price": actual_price,
            "Forecasted Price": predicted_price
        }

        logger.info(f"[OK] {asset} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        return evaluation_results


    return {
        "forecast": forecast_text,
        "anomalies": anomaly_text,
        "evaluation": evaluate_forecasts(forecast_records, actuals_dict)
    }