import requests
import logging

logger = logging.getLogger(__name__)

def fetch_economic_indicator(indicator_id="NY.GDP.MKTP.CD", country_code="US"):
    """
    Fetches the most recent value of a given economic indicator from the World Bank API.
    - Default indicator: GDP (current US$)
    - Default country: United States (US)

    World Bank Indicator Examples:
    - NY.GDP.MKTP.CD → GDP (current US$)
    - FP.CPI.TOTL.ZG → Inflation, consumer prices (annual %)
    - SL.UEM.TOTL.ZS → Unemployment (% of total labor force)
    """
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&per_page=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if len(data) < 2 or not data[1]:
            logger.warning(f"No data found for indicator {indicator_id}")
            return {"error": "No data available."}

        record = data[1][0]
        return {
            "indicator": record.get("indicator", {}).get("id"),
            "indicator_name": record.get("indicator", {}).get("value"),
            "country": record.get("country", {}).get("value"),
            "date": record.get("date"),
            "value": record.get("value")
        }
    except Exception as e:
        logger.error(f"Failed to fetch indicator {indicator_id} from World Bank: {e}")
        return {"error": str(e)}