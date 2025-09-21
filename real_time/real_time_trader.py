import time
import json
from datetime import datetime
from real_time.data_ingestor import DataIngestor
from real_time.live_state import LiveState
from real_time.trading_agent import TradingAgent

def log_decision(asset: str, decision: str, log_file: str = "logs/real_time_decisions.json"):
    """
    Logs a trading decision to a file.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "asset": asset,
        "decision": decision
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    """
    The main loop for the real-time trading system.
    """
    assets = ["AAPL", "TSLA"]  # Example assets

    data_ingestor = DataIngestor(assets)
    live_state = LiveState()
    trading_agent = TradingAgent(live_state)

    print("Starting real-time trading loop...")

    try:
        while True:
            # 1. Fetch live data
            new_data = data_ingestor.fetch_live_data()

            if not new_data.empty:
                # 2. Update live state
                live_state.update_market_data(new_data)
                print(f"Updated market data at {live_state.timestamp}")

                # 3. Make trading decisions for each asset
                for asset in assets:
                    decision = trading_agent.make_decision(asset)
                    print(f"Decision for {asset}: {decision}")
                    log_decision(asset, decision)

            # Sleep for a short interval (e.g., 60 seconds for 1-minute data)
            time.sleep(60)

    except KeyboardInterrupt:
        print("Stopping real-time trading loop.")

if __name__ == "__main__":
    main()
