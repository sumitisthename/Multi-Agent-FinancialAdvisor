import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from tools.quant_models import get_numerical_forecast
from utils.logger import get_logger
import warnings
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import os
import json
from codecarbon import EmissionsTracker

# Suppress yfinance and other warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logger = get_logger()

def get_actual_price(asset, date_str):
    """
    Fetches the actual closing price for a given asset on a specific date.
    """
    try:
        date = pd.to_datetime(date_str)
        data = yf.download(asset, start=date, end=date + timedelta(days=1), interval="1d", progress=False)
        if not data.empty:
            return float(data['Close'].iloc[0])
    except Exception as e:
        logger.error(f"Could not fetch actual price for {asset} on {date_str}: {e}")
    return None

def calculate_metrics(df):
    """
    Calculates and returns a dictionary of performance metrics.
    """
    if df.empty:
        return {}

    # Forecast Accuracy Metrics
    rmse = np.sqrt(mean_squared_error(df['Actual_Price'], df['Forecasted_Price']))
    mape = mean_absolute_percentage_error(df['Actual_Price'], df['Forecasted_Price'])

    # Directional Accuracy
    df['Predicted_Direction'] = np.where(df['Forecasted_Price'] > df['Latest_Price_at_Forecast'], 1, -1)
    df['Actual_Direction'] = np.where(df['Actual_Price'] > df['Latest_Price_at_Forecast'], 1, -1)
    directional_accuracy = (df['Predicted_Direction'] == df['Actual_Direction']).mean()

    # Simulated Strategy Returns
    df['Strategy_Return'] = np.where(
        df['Predicted_Direction'] == 1,
        (df['Actual_Price'] / df['Latest_Price_at_Forecast']) - 1,
        (df['Latest_Price_at_Forecast'] / df['Actual_Price']) - 1
    )
    df['Strategy_Return'].fillna(0, inplace=True)

    # P&L and Sharpe Ratio
    cumulative_return = (1 + df['Strategy_Return']).cumprod()
    total_return_pct = (cumulative_return.iloc[-1] - 1) * 100

    if df['Strategy_Return'].std() > 0:
        sharpe_ratio = (df['Strategy_Return'].mean() / df['Strategy_Return'].std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    metrics = {
        "RMSE": rmse,
        "MAPE": mape,
        "Directional_Accuracy": directional_accuracy,
        "Total_Return_pct": total_return_pct,
        "Sharpe_Ratio": sharpe_ratio
    }
    return metrics

def run_backtest(assets, days_to_backtest, model_type):
    """
    Runs the backtest for a given list of assets over a specified number of days.
    """
    logger.info(f"Starting backtest for model '{model_type}'...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_backtest)

    all_results = []

    for i in range(days_to_backtest):
        current_date = start_date + timedelta(days=i)
        current_date_str = current_date.isoformat()

        forecast_records = get_numerical_forecast(
            assets,
            current_date_str,
            model_type=model_type,
            save_intermediate_files=False
        )

        for record in forecast_records:
            if "Forecasted Price" in record:
                asset = record["Asset"]
                forecasted_price = record["Forecasted Price"]
                latest_price = record["Latest Price"]
                forecast_date = record["Forecast Date"]

                actual_price = get_actual_price(asset, forecast_date)

                if actual_price is not None:
                    all_results.append({
                        "Asset": asset,
                        "Date_of_Forecast": current_date.strftime('%Y-%m-%d'),
                        "Forecast_for_Date": forecast_date,
                        "Latest_Price_at_Forecast": latest_price,
                        "Forecasted_Price": forecasted_price,
                        "Actual_Price": actual_price,
                        "Model": model_type
                    })

    return pd.DataFrame(all_results)


if __name__ == "__main__":
    ASSETS_TO_TEST = ["SPY", "AAPL"]
    DAYS_TO_RUN = 30
    MODELS_TO_TEST = ['arima', 'moving_average']

    os.makedirs("results", exist_ok=True)

    all_model_results = {}

    for model in MODELS_TO_TEST:
        print(f"\n--- Running Backtest for Model: {model} ---")

        tracker = EmissionsTracker(project_name=f"backtest_{model}", output_file="emissions.csv")
        tracker.start()

        backtest_df = run_backtest(ASSETS_TO_TEST, DAYS_TO_RUN, model_type=model)

        emissions_kg = tracker.stop()
        print(f"Emissions for {model} model: {emissions_kg:.6f} kg CO2eq")

        if not backtest_df.empty:
            model_metrics = {}
            for asset in ASSETS_TO_TEST:
                asset_df = backtest_df[backtest_df['Asset'] == asset].copy()
                if not asset_df.empty:
                    metrics = calculate_metrics(asset_df)
                    model_metrics[asset] = metrics

            all_model_results[model] = {
                "performance_metrics": model_metrics,
                "aggregated_emissions_kg": emissions_kg
            }

            # Save raw data for this model
            raw_data_path = f"results/backtest_raw_data_{model}.csv"
            backtest_df.to_csv(raw_data_path, index=False)
            print(f"Full backtest data for {model} saved to {raw_data_path}")

    # Save the final comparative summary
    summary_path = "results/performance_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(all_model_results, f, indent=4)
    print(f"\nComparative performance summary saved to {summary_path}")

    # Also print summary to console
    print("\n--- Comparative Performance Metrics Summary ---")
    print(json.dumps(all_model_results, indent=4))
