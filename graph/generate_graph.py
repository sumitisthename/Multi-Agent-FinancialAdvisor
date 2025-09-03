import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def generate_forecast_graph(date):
    """
    Generates and saves graphs for each asset's forecast.
    """
    forecast_file = f"forecasts/forecast-{date}.csv"
    if not os.path.exists(forecast_file):
        print(f"Forecast file not found: {forecast_file}")
        return

    forecast_df = pd.read_csv(forecast_file)

    for index, row in forecast_df.iterrows():
        asset = row['Asset']

        # Find the historical data file for the asset
        asset_files = [f for f in os.listdir("forecasts") if f.startswith(f"assets-{asset}")]
        if not asset_files:
            print(f"No historical data file found for {asset}")
            continue

        # Get the most recent historical data file
        asset_file = max(asset_files, key=lambda f: os.path.getmtime(os.path.join("forecasts", f)))
        historical_df = pd.read_csv(os.path.join("forecasts", asset_file))
        historical_df['Date'] = pd.to_datetime(historical_df['Date'])

        plt.figure(figsize=(12, 6))
        plt.plot(historical_df['Date'], historical_df['Close'], label="Historical Prices")
        plt.plot(historical_df['Date'], historical_df['SMA_10'], label="10-Day SMA")
        plt.plot(historical_df['Date'], historical_df['SMA_30'], label="30-Day SMA")

        # Add forecast data to the plot
        last_date = historical_df['Date'].iloc[-1]
        forecast_date = last_date + timedelta(days=1)

        if 'ARIMA_Forecast' in row and row['ARIMA_Forecast'] != 'N/A' and pd.notna(row['ARIMA_Forecast']):
            forecast_price = float(row['ARIMA_Forecast'])
            plt.plot(forecast_date, forecast_price, 'ro', label='ARIMA Forecast')
        if 'SARIMA_Forecast' in row and row['SARIMA_Forecast'] != 'N/A' and pd.notna(row['SARIMA_Forecast']):
            forecast_price = float(row['SARIMA_Forecast'])
            plt.plot(forecast_date, forecast_price, 'go', label='SARIMA Forecast')
        if 'Prophet_Forecast' in row and row['Prophet_Forecast'] != 'N/A' and pd.notna(row['Prophet_Forecast']):
            forecast_price = float(row['Prophet_Forecast'])
            plt.plot(forecast_date, forecast_price, 'bo', label='Prophet Forecast')
        if 'LSTM_Forecast' in row and row['LSTM_Forecast'] != 'N/A' and pd.notna(row['LSTM_Forecast']):
            forecast_price = float(row['LSTM_Forecast'])
            plt.plot(forecast_date, forecast_price, 'yo', label='LSTM Forecast')

        plt.title(f"Forecast for {asset}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        graph_file = f"forecast_{asset}_{date}.png"
        plt.savefig(graph_file)
        print(f"Graph saved: {graph_file}")
        plt.close()

if __name__ == "__main__":
    today = datetime.today().strftime('%Y-%m-%d')
    generate_forecast_graph(today)
