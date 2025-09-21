import pandas as pd
from datetime import datetime

class LiveState:
    """
    Maintains the live state of the trading system.
    """
    def __init__(self):
        self.market_data = pd.DataFrame()
        self.positions = {}  # E.g., {"AAPL": 10, "TSLA": -5}
        self.open_orders = []  # A list of open orders
        self.timestamp = None

    def update_market_data(self, new_data: pd.DataFrame):
        """
        Updates the market data with the latest tick.
        """
        self.market_data = pd.concat([self.market_data, new_data]).tail(1000)  # Keep last 1000 ticks
        self.timestamp = datetime.now()

    def get_latest_price(self, asset: str):
        """
        Gets the latest price for a given asset.
        """
        if not self.market_data.empty and asset in self.market_data.columns.get_level_values(1):
             return self.market_data['Close'][asset].iloc[-1]
        return None

    def get_position(self, asset: str) -> int:
        """
        Gets the current position for a given asset.
        """
        return self.positions.get(asset, 0)

if __name__ == '__main__':
    # Example usage
    live_state = LiveState()

    # Simulate a market data update
    data = {
        ('Close', 'AAPL'): [150.0],
        ('Close', 'TSLA'): [300.0]
    }
    index = [pd.to_datetime("2025-09-20 15:00:00")]
    new_data = pd.DataFrame(data, index=index)
    new_data.columns = pd.MultiIndex.from_tuples(new_data.columns)

    live_state.update_market_data(new_data)

    print(f"Latest AAPL price: {live_state.get_latest_price('AAPL')}")
    print(f"Current TSLA position: {live_state.get_position('TSLA')}")
    print(f"State timestamp: {live_state.timestamp}")
