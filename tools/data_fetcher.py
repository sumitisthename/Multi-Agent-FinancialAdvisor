# tools/data_fetcher.py
"""
Data fetching tools for the LangGraph multi-agent financial analysis system.
"""
import requests
import os
from utils.logger import get_logger
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()


def fetch_market_data(assets, date):
    """
    Fetches market data for a list of assets.
    """
    results = []
    for asset in assets:
        try:
            logger.info(f"📥 Fetching price data for {asset} on {date}")
            # Fetch daily data for the last 60 days as an example
            df = yf.download(asset, period="60d", interval="1d", progress=False)
            if df.empty:
                logger.warning(f"⚠️ No data found for {asset}")
                results.append(f"No data found for {asset} on {date}")
                continue
            
            results.append(f"Fetched {len(df)} records for {asset} on {date}")
        
        except Exception as e:
            logger.error(f"❌ Failed to fetch data for {asset}: {e}")
            results.append(f"Failed to fetch data for {asset} on {date}")
    
    return "\n".join(results)


def fetch_news_data(assets):
    """
    Fetches news data for a list of assets.
    """
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


def fetch_transaction_data(assets, date):
    """
    Fetches transaction data for a list of assets.
    """
    # Stub function — extend with real transactional logs or simulated examples
    logger.info("Fetching simulated transaction data")
    return [{"asset": a, "volume": 1000, "price": 250 + i * 10} for i, a in enumerate(assets)]
