import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

def generate_forecast_plotly(date):
    """
    Generates and returns a list of Plotly figures for each asset's forecast.
    """
    forecast_file = f"forecasts/forecast-{date}.csv"
    if not os.path.exists(forecast_file):
        print(f"Forecast file not found: {forecast_file}")
        return []

    forecast_df = pd.read_csv(forecast_file)
    figures = []

    for index, row in forecast_df.iterrows():
        asset = row['Asset']

        asset_files = [f for f in os.listdir("forecasts") if f.startswith(f"assets-{asset}")]
        if not asset_files:
            print(f"No historical data file found for {asset}")
            continue

        asset_file = max(asset_files, key=lambda f: os.path.getmtime(os.path.join("forecasts", f)))
        historical_df = pd.read_csv(os.path.join("forecasts", asset_file))
        historical_df['Date'] = pd.to_datetime(historical_df['Date'])

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=historical_df['Date'], y=historical_df['Close'], mode='lines', name='Historical Prices'))
        fig.add_trace(go.Scatter(x=historical_df['Date'], y=historical_df['SMA_10'], mode='lines', name='10-Day SMA'))
        fig.add_trace(go.Scatter(x=historical_df['Date'], y=historical_df['SMA_30'], mode='lines', name='30-Day SMA'))

        last_date = historical_df['Date'].iloc[-1]
        forecast_date = last_date + timedelta(days=1)

        forecasts = {
            'ARIMA': row.get('ARIMA_Forecast'),
            'SARIMA': row.get('SARIMA_Forecast'),
            'Prophet': row.get('Prophet_Forecast'),
            'LSTM': row.get('LSTM_Forecast')
        }

        for model, forecast in forecasts.items():
            if forecast and forecast != 'N/A' and pd.notna(forecast):
                fig.add_trace(go.Scatter(x=[forecast_date], y=[float(forecast)], mode='markers', name=f'{model} Forecast', marker=dict(size=10)))

        fig.update_layout(
            title=f"Forecast for {asset}",
            xaxis_title="Date",
            yaxis_title="Price",
            legend_title="Legend",
            template="plotly_white"
        )
        figures.append((asset, fig))

    return figures

def generate_forecast_graph(date):
    """
    Generates and saves graphs for each asset's forecast.
    """
    figures = generate_forecast_plotly(date)
    for asset, fig in figures:
        graph_file = f"forecast_{asset}_{date}.html"
        fig.write_html(graph_file)
        print(f"Graph saved: {graph_file}")

if __name__ == "__main__":
    today = datetime.today().strftime('%Y-%m-%d')
    generate_forecast_graph(today)
