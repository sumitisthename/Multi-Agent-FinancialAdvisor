import yfinance as yf
import pandas as pd
import numpy as np
from tools.quant_models import evaluate_and_select_model
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger()

def run_backtest(asset, start_date, end_date):
    """
    Runs a backtest for a given asset over a specified period.
    """
    logger.info(f"Running backtest for {asset} from {start_date} to {end_date}")

    # Fetch historical data
    df = yf.download(asset, start=start_date, end=end_date, interval="1d")

    # Backtesting logic
    results = []
    portfolio_value = 100000  # Starting with $100,000

    # Loop through the data, starting from the first day we have enough data to train
    # For LSTM, we need at least 61 days of data for the first training run.
    # We will use a 1-year training window.
    for i in range(252, len(df) - 1): # 252 trading days in a year, -1 to avoid index out of bounds

        train_start_date = df.index[i-252]
        train_end_date = df.index[i]

        train_data = df['Close'][train_start_date:train_end_date]

        if len(train_data) < 61:
            continue

        logger.info(f"Backtesting for date: {train_end_date}")

        model_evaluations = evaluate_and_select_model(train_data)
        best_model = min(model_evaluations, key=lambda x: x['score'])

        forecast = best_model['forecast']
        current_price = train_data.iloc[-1]

        # Trading strategy
        signal = 0 # 0 for hold, 1 for buy, -1 for sell
        if forecast > current_price:
            signal = 1
        elif forecast < current_price:
            signal = -1

        # Calculate return for the next day
        next_day_price = df['Close'].iloc[i+1]
        daily_return = signal * (next_day_price - current_price) / current_price
        portfolio_value *= (1 + daily_return)

        results.append({
            "date": train_end_date,
            "chosen_model": best_model['model'],
            "forecast": forecast,
            "actual_price": current_price,
            "next_day_price": next_day_price,
            "signal": signal,
            "daily_return": daily_return,
            "portfolio_value": portfolio_value,
            "model_evaluations": model_evaluations
        })

    results_df = pd.DataFrame(results)

    # --- Output Results ---
    print("\n--- Backtest Results ---")

    # 1. Total Return
    total_return = (results_df['portfolio_value'].iloc[-1] / results_df['portfolio_value'].iloc[0]) - 1
    print(f"Total Return: {total_return:.2%}")

    # 2. Sharpe Ratio
    daily_returns = results_df['daily_return']
    sharpe_ratio = np.sqrt(252) * (daily_returns.mean() / daily_returns.std())
    print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")

    # 3. Model Selection Frequency
    print("\n--- Model Selection ---")
    model_selection_counts = results_df['chosen_model'].value_counts()
    print(model_selection_counts)

    # 4. Model Performance Analysis
    print("\n--- Model Performance ---")
    model_performance = []
    for model_name in ["ARIMA", "SARIMA", "Prophet", "LSTM"]:
        model_results = []
        for index, row in results_df.iterrows():
            for eval_result in row['model_evaluations']:
                if eval_result['model'] == model_name:
                    model_results.append(eval_result)

        model_df = pd.DataFrame(model_results)
        avg_mape = model_df['mape'].mean()
        avg_emissions = model_df['emissions'].mean()

        model_performance.append({
            "model": model_name,
            "avg_mape": avg_mape,
            "avg_emissions": avg_emissions
        })

    model_performance_df = pd.DataFrame(model_performance)
    print(model_performance_df)

    logger.info("Backtest complete.")

if __name__ == "__main__":
    ASSET = "AAPL"
    START_DATE = "2022-01-01"
    END_DATE = "2023-01-01"
    run_backtest(ASSET, START_DATE, END_DATE)
