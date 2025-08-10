import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import os
import re
import numpy as np
import json

# Add project root to path to allow imports from other modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.graph_builder import build_graph
from config.settings import load_config
from utils.logger import get_logger

# Suppress yfinance and other warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logger = get_logger()

def parse_decision(decision_text):
    """
    Parses the natural language decision from the coordinator to extract a trading signal.
    """
    if not isinstance(decision_text, str):
        return "NO_SIGNAL"

    decision_text = decision_text.upper()
    if "BUY" in decision_text:
        return "BUY"
    elif "SELL" in decision_text:
        return "SELL"
    elif "HOLD" in decision_text or "TAKE NO ACTION" in decision_text:
        return "HOLD"
    return "NO_SIGNAL"

def get_next_day_return(asset, trade_date):
    """
    Fetches the return for a simple open-to-close trade on the next trading day.
    """
    try:
        data = yf.download(asset, start=trade_date, end=trade_date + timedelta(days=4), interval="1d", progress=False)
        if not data.empty and len(data) > 1:
            next_day_open = data['Open'].iloc[1]
            next_day_close = data['Close'].iloc[1]
            if next_day_open > 0:
                return (next_day_close / next_day_open) - 1
    except Exception as e:
        logger.error(f"Could not calculate next day return for {asset} on {trade_date}: {e}")
    return 0.0

def calculate_agent_performance(df):
    """
    Calculates performance metrics for the agentic strategy.
    """
    if df.empty:
        return {}

    trade_df = df[df['Signal'].isin(['BUY', 'SELL'])].copy()

    if trade_df.empty:
        return {"Total_Trades": 0, "Win_Rate": 0, "Total_Return_pct": 0, "Sharpe_Ratio": 0}

    win_rate = (trade_df['Return'] > 0).mean()
    total_trades = len(trade_df)

    df['Cumulative_Return'] = (1 + df['Return']).cumprod()
    total_return_pct = (df['Cumulative_Return'].iloc[-1] - 1) * 100

    if trade_df['Return'].std() > 0:
        sharpe_ratio = (trade_df['Return'].mean() / trade_df['Return'].std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    return {
        "Total_Return_pct": total_return_pct,
        "Sharpe_Ratio": sharpe_ratio,
        "Win_Rate": win_rate,
        "Total_Trades": total_trades
    }

def run_agent_backtest(assets, days_to_backtest):
    """
    Runs the agent-based backtest.
    """
    logger.info(f"Starting AGENT backtest for assets: {assets} over the last {days_to_backtest} days.")

    config = load_config()
    graph = build_graph(config)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_backtest)

    results = []

    for i in range(days_to_backtest):
        current_date = start_date + timedelta(days=i)
        if current_date.weekday() >= 5:
            continue

        current_date_str = current_date.isoformat()

        initial_state = {"assets": assets, "timestamp": current_date_str}

        try:
            graph_result = graph.invoke(initial_state)
            final_decision_text = graph_result.get("final_decision", "")
            parsed_signal = parse_decision(final_decision_text)

            daily_return = 0.0
            if parsed_signal in ["BUY", "SELL"]:
                day_return = get_next_day_return(assets[0], current_date)
                if parsed_signal == "BUY":
                    daily_return = day_return
                elif parsed_signal == "SELL":
                    daily_return = -day_return

            results.append({
                "Date": current_date.strftime('%Y-%m-%d'),
                "Asset": assets[0],
                "Signal": parsed_signal,
                "Return": daily_return
            })

        except Exception as e:
            logger.error(f"  Graph invocation failed for date {current_date_str}: {e}")
            results.append({ "Date": current_date.strftime('%Y-%m-%d'), "Asset": assets[0], "Signal": "ERROR", "Return": 0.0 })

    return pd.DataFrame(results)


if __name__ == "__main__":
    ASSETS_TO_TEST = ["SPY"]
    DAYS_TO_RUN = 10

    os.makedirs("results", exist_ok=True)

    # Run the agent-based backtest
    agent_results_df = run_agent_backtest(ASSETS_TO_TEST, DAYS_TO_RUN)

    agent_performance = {}
    if not agent_results_df.empty:
        agent_performance = calculate_agent_performance(agent_results_df)

    # Load numerical model performance
    try:
        with open("results/performance_summary.json", 'r') as f:
            numerical_performance = json.load(f)
    except FileNotFoundError:
        print("Could not find numerical performance summary. Run `backtest.py` first.")
        numerical_performance = {}

    # Combine all results
    final_comparison = {
        "agent_strategy": agent_performance,
        "numerical_strategies": numerical_performance
    }

    # Save final comparison report
    comparison_path = "results/strategy_comparison.json"
    with open(comparison_path, 'w') as f:
        json.dump(final_comparison, f, indent=4)

    print(f"Final strategy comparison report saved to {comparison_path}")

    print("\n--- Strategy Comparison Summary ---")
    print(json.dumps(final_comparison, indent=4))
