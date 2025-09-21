import yfinance as yf
import pandas as pd

class DataIngestor:
    """
    Handles the ingestion of real-time market data.
    """
    def __init__(self, assets: list[str]):
        self.assets = assets

    def fetch_live_data(self) -> pd.DataFrame:
        """
        Fetches the latest market data for the specified assets.

        Returns:
            pd.DataFrame: A DataFrame containing the latest tick data.
        """
        # In a real-world scenario, this would connect to a live data feed (e.g., WebSocket).
        # For this example, we'll use yfinance to get recent data.
        data = yf.download(self.assets, period="1d", interval="1m")
        return data.tail(1)

if __name__ == '__main__':
    # Example usage
    ingestor = DataIngestor(assets=["AAPL", "TSLA"])
    latest_data = ingestor.fetch_live_data()
    print("Latest data:")
    print(latest_data)
