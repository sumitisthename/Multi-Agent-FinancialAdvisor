# tools/data_fetcher.py

import requests
import os
from utils.logger import get_logger

logger = get_logger()


def fetch_market_data(assets, date, config):
    # Using Alpha Vantage or Yahoo API as example (mock structure here)
    results = []
    for asset in assets:
        # Simulate fetch
        logger.info(f"Fetching price data for {asset} on {date}")
        results.append(f"Price data for {asset} on {date} (stub)")
    return "\n".join(results)


def fetch_news_data(assets, config):
    news_api_key = os.getenv("NEWS_API_KEY")
    query = " OR ".join(assets)
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}"

    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])[:5]  # Top 5 headlines
        headlines = [f"- {a['title']} ({a['source']['name']})" for a in articles]
        return "\n".join(headlines) if headlines else "No relevant news found."
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return "News fetch error."


def fetch_transaction_data(assets, date, config):
    # Stub function — extend with real transactional logs or simulated examples
    logger.info("Fetching simulated transaction data")
    return [{"asset": a, "volume": 1000, "price": 250 + i * 10} for i, a in enumerate(assets)]
