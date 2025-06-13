import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import os
import traceback

assets = ["AAPL", "TSLA", "NVDA"]
date = "2025-06-13"
forecast_records = []

for asset in assets:
    try:
        print(f"\nFetching data for {asset}...")
        df = yf.download(asset, period="60d", interval="1d", auto_adjust=False)
        prices = df['Close'].dropna()
        print(prices.tail())

        if len(prices) < 10:
            print(f"{asset}: Not enough data to forecast.")
            forecast_records.append({"Asset": asset, "Forecast": "Not enough data"})
            continue

        # ✅ Ensure regular frequency with forward fill
        prices = prices.asfreq('D', method='pad')

        model = ARIMA(prices, order=(3, 1, 2))
        fitted_model = model.fit()
        forecast_value = fitted_model.forecast(steps=1)
        print(f"Raw forecast output for {asset}: {forecast_value}")

        forecast = float(forecast_value.iloc[0])
        latest_price = float(prices.iloc[-1])
        change_pct = ((forecast - latest_price) / latest_price) * 100

        forecast_records.append({
            "Asset": asset,
            "Latest Price": round(latest_price, 2),
            "Forecasted Price": round(forecast, 2),
            "Expected Return (%)": round(change_pct, 2)
        })

    except Exception as e:
        print(f"❌ Exception while processing {asset}:\n{traceback.format_exc()}")
        forecast_records.append({"Asset": asset, "Forecast": "Failed"})

# Save to CSV
df = pd.DataFrame(forecast_records)
os.makedirs("forecasts", exist_ok=True)
csv_path = f"forecasts/debug_forecast_{date}.csv"
df.to_csv(csv_path, index=False)

print(f"\n✅ Saved CSV to {csv_path}")
print(df)
