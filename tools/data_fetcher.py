# tools/data_fetcher.py
"""
Data fetching tools for the LangGraph multi-agent financial analysis system.
"""
import uuid
import requests
import os
from utils.logger import get_logger
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
import inspect

load_dotenv()

logger = get_logger()

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_market_data(assets, date):
    """
    Fetches market data for a list of assets.
    """
    logger.info(f"🔄 fetch_market_data() called - ID: {uuid.uuid4()}")
    caller = inspect.stack()[1].function
    timestamp = date
    logger.info(f"📥 Fetching price data for {assets} on {timestamp} (called by {caller})")

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
    Fetches news data for a list of assets and saves citations to a JSON file.
    """
    news_api_key = os.getenv("NEWS_API_KEY")
    query = " OR ".join(assets)
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])[:5]

        citations = []
        for article in articles:
            citation = {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "author": article.get("author"),
                "publishedAt": article.get("publishedAt"),
                "url": article.get("url"),
                "description": article.get("description")
            }
            citations.append(citation)

        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("news_data", exist_ok=True)
        filename = os.path.join("news_data", f"news_citations_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(citations, f, indent=4)

        # Return a readable version for display
        headlines = [f"- {c['title']} ({c['source']})" for c in citations]
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
