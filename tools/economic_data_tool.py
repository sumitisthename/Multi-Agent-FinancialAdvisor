import beaapi
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_bea_api_key():
    """
    Get the BEA API key from the environment variables.
    """
    bea_api_key = os.getenv("BEA_API_KEY")
    if not bea_api_key:
        raise ValueError("BEA_API_KEY environment variable not set.")
    return bea_api_key

def fetch_gdp_data():
    """
    Fetches the latest GDP data from the BEA API.
    Note: The table and parameters are currently hardcoded. This could be improved in the future
    to allow for more flexibility.
    """
    try:
        bea_api_key = get_bea_api_key()
        gdp_data = beaapi.get_data(
            bea_api_key,
            'NIPA',
            TableName='T10105',
            Frequency='Q',
            Year='X'
        )
        return gdp_data
    except Exception as e:
        logger.error(f"Failed to fetch GDP data from BEA: {e}")
        return {"error": str(e)}

def fetch_pce_data():
    """
    Fetches the latest PCE price index data from the BEA API.
    Note: The table and parameters are currently hardcoded. This could be improved in the future
    to allow for more flexibility.
    """
    try:
        bea_api_key = get_bea_api_key()
        pce_data = beaapi.get_data(
            bea_api_key,
            'NIPA',
            TableName='T20304',
            Frequency='Q',
            Year='X'
        )
        return pce_data
    except Exception as e:
        logger.error(f"Failed to fetch PCE data from BEA: {e}")
        return {"error": str(e)}

def fetch_employment_data():
    """
    Fetches the latest employment data from the BEA API.
    Note: The table and parameters are currently hardcoded. This could be improved in the future
    to allow for more flexibility.
    """
    try:
        bea_api_key = get_bea_api_key()
        employment_data = beaapi.get_data(
            bea_api_key,
            'Regional',
            TableName='SAINC4',
            GeoFips='STATE',
            LineCode='3' # Full-time and part-time employment
        )
        return employment_data
    except Exception as e:
        logger.error(f"Failed to fetch employment data from BEA: {e}")
        return {"error": str(e)}
