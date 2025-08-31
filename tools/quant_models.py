import glob
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.logger import get_logger
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from codecarbon import EmissionsTracker
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

    # Markdown table header
    table = "| Asset | Latest Price | ARIMA | SARIMA | Prophet | LSTM | SMA_10 | SMA_30 | EMA_10 | EMA_30 | Status |\n"
    table += "|-------|--------------|-------|--------|---------|------|--------|--------|--------|--------|---------|\n"

    for record in forecast_records:
        asset = record.get("Asset", "N/A")

        if "Forecast" in record:  # Error or no-data cases
            status = record["Forecast"]
            table += f"| {asset} | - | - | - | - | - | - | - | - | - | {status} |\n"
        else:
            latest = record.get("Latest Price", "N/A")
            arima_forecast = record.get("ARIMA_Forecast", "N/A")
            sarima_forecast = record.get("SARIMA_Forecast", "N/A")
            prophet_forecast = record.get("Prophet_Forecast", "N/A")
            lstm_forecast = record.get("LSTM_Forecast", "N/A")
            sma10 = record.get("SMA_10", "-")
            sma30 = record.get("SMA_30", "-")
            ema10 = record.get("EMA_10", "-")
            ema30 = record.get("EMA_30", "-")

            # Simple status based on the first forecast model (ARIMA)
            if arima_forecast > latest:
                status = "📈 Bullish"
            else:
                status = "📉 Bearish"

            table += f"| {asset} | ${latest} | ${arima_forecast} | ${sarima_forecast} | ${prophet_forecast} | ${lstm_forecast} | {sma10} | {sma30} | {ema10} | {ema30} | {status} |\n"

    return table


def evaluate_and_select_model(price_series):
    """
    Evaluates different forecasting models based on performance and emissions,
    and selects the best one.
    """
    models = ["ARIMA", "SARIMA", "Prophet", "LSTM"]
    results = []

    for model_name in models:
        tracker = EmissionsTracker(output_file="emissions.csv", log_level="error")
        tracker.start()

        forecast = None

        train_series = price_series[:-1]
        test_value = price_series[-1]

        try:
            if model_name == "ARIMA":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ARIMA(train_series, order=(5, 1, 0))
                    fitted_model = model.fit()
                    forecast = fitted_model.forecast(steps=1).iloc[0]

            elif model_name == "SARIMA":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = SARIMAX(train_series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
                    fitted_model = model.fit(disp=False)
                    forecast = fitted_model.forecast(steps=1).iloc[0]

            elif model_name == "Prophet":
                prophet_df = train_series.reset_index()
                prophet_df.columns = ['ds', 'y']
                model = Prophet()
                model.fit(prophet_df)
                future = model.make_future_dataframe(periods=1)
                forecast_df = model.predict(future)
                forecast = forecast_df['yhat'].iloc[-1]

            elif model_name == "LSTM":
                scaler = MinMaxScaler(feature_range=(0, 1))
                scaled_data = scaler.fit_transform(train_series.values.reshape(-1,1))

                x_train, y_train = [], []
                for i in range(60, len(scaled_data)):
                    x_train.append(scaled_data[i-60:i, 0])
                    y_train.append(scaled_data[i, 0])

                x_train, y_train = np.array(x_train), np.array(y_train)
                x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

                lstm_model = Sequential()
                lstm_model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
                lstm_model.add(LSTM(50, return_sequences=False))
                lstm_model.add(Dense(25))
                lstm_model.add(Dense(1))
                lstm_model.compile(optimizer='adam', loss='mean_squared_error')
                lstm_model.fit(x_train, y_train, batch_size=1, epochs=1)

                last_60_days = scaler.transform(price_series.values[-61:-1].reshape(-1,1))
                x_test = np.array([last_60_days])
                x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

                pred_price = lstm_model.predict(x_test)
                forecast = scaler.inverse_transform(pred_price)[0][0]

            emissions = tracker.stop()

            mape = np.mean(np.abs((test_value - forecast) / test_value)) * 100

            # Simple scoring: lower is better. We want low MAPE and low emissions.
            # Weights can be adjusted based on priority.
            score = (0.7 * mape) + (0.3 * emissions * 1000)

            results.append({
                "model": model_name,
                "forecast": forecast,
                "mape": mape,
                "emissions": emissions,
                "score": score
            })

        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")
            emissions = tracker.stop()
            results.append({
                "model": model_name,
                "forecast": None,
                "mape": None,
                "emissions": emissions,
                "score": float('inf') # Penalize failed models
            })

    return results


def run_forecast_model(assets, date, config):
    forecast_records = []

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
            logger.info(f"📥 Fetching price data for {asset}")
            df = yf.download(asset, period="1y", interval="1d", auto_adjust=False)

            df = df.reset_index()
            df['timestamp'] = pd.Timestamp.now()

            # Moving averages
            df['SMA_10'] = df['Close'].rolling(window=10).mean()
            df['SMA_30'] = df['Close'].rolling(window=30).mean()
            df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
            df['EMA_30'] = df['Close'].ewm(span=30, adjust=False).mean()

            safe_date = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            asset_csv_path = f"forecasts/assets-{asset}-{safe_date}.csv"
            df.to_csv(asset_csv_path, index=False)
            logger.info(f"✅ Asset CSV saved: {asset_csv_path}")

            # Forecast logic
            prices = df[['Date', 'Close']].dropna()
            if len(prices) < 61: # Needs at least 61 days for LSTM
                forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
                continue

            prices.set_index('Date', inplace=True)
            prices.index = pd.to_datetime(prices.index)
            price_series = prices['Close'].asfreq('D', method='pad')

            latest_price = float(price_series.iloc[-1].item())

            model_evaluations = evaluate_and_select_model(price_series)
            best_model = min(model_evaluations, key=lambda x: x['score'])

            logger.info(f"Best model for {asset}: {best_model['model']}")

            record = {
                "Asset": asset,
                "Latest Price": round(latest_price, 2),
                "SMA_10": round(df['SMA_10'].iloc[-1], 2) if not pd.isna(df['SMA_10'].iloc[-1]) else None,
                "SMA_30": round(df['SMA_30'].iloc[-1], 2) if not pd.isna(df['SMA_30'].iloc[-1]) else None,
                "EMA_10": round(df['EMA_10'].iloc[-1], 2) if not pd.isna(df['EMA_10'].iloc[-1]) else None,
                "EMA_30": round(df['EMA_30'].iloc[-1], 2) if not pd.isna(df['EMA_30'].iloc[-1]) else None,
                "model_evaluations": model_evaluations
            }

            for model_eval in model_evaluations:
                record[f"{model_eval['model']}_Forecast"] = round(model_eval['forecast'], 2) if model_eval['forecast'] is not None else 'N/A'

            forecast_records.append(record)

        except Exception as e:
            logger.error(f"❌ Forecasting failed for {asset}:\n{traceback.format_exc()}")
            forecast_records.append({"Asset": asset, "Forecast": "Failed"})

    # Save combined forecast summary
    try:
        # This part needs to be handled carefully because of the nested list
        summary_df = pd.DataFrame(forecast_records)
        summary_path = f"forecasts/forecast-{date}.csv"
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"✅ Forecast summary saved to {summary_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save forecast CSV: {e}")

    return forecast_records


def detect_anomalies(transactions, forecast_text, config):
    logger.info("📊 Running anomaly detection on transaction data")

    try:
        df = pd.DataFrame(transactions)

        # Integrate moving averages into anomaly detection
        if 'price' in df.columns:
            df['SMA_10'] = df['price'].rolling(window=10).mean()
            df['SMA_30'] = df['price'].rolling(window=30).mean()
            df['price_vs_sma10'] = df['price'] - df['SMA_10']
            df['price_vs_sma30'] = df['price'] - df['SMA_30']

        features = ['price', 'volume']
        if 'price_vs_sma10' in df.columns:
            features += ['price_vs_sma10', 'price_vs_sma30']

        features_df = df[features].fillna(0)

        model = IsolationForest(contamination=0.2, random_state=42)
        df['anomaly_score'] = model.fit_predict(features_df)

        anomalies = df[df['anomaly_score'] == -1].to_dict(orient='records')
        return f"{len(anomalies)} anomalies detected: {anomalies}" if anomalies else "No anomalies."

    except Exception as e:
        logger.error(f"❌ Error during anomaly detection: {e}")
        return "Anomaly detection failed."


def run_quant_models(assets, date, transactions, config):
    logger.info("🔍 Running quantitative models...")

    forecast_text = run_forecast_model(assets, date, config)
    logger.info(f"Forecast results:\n{forecast_text}")

    anomaly_text = detect_anomalies(transactions, forecast_text, config)
    logger.info(f"Anomaly detection results:\n{anomaly_text}")

    return {
        "forecast": forecast_text,
        "anomalies": anomaly_text
    }
