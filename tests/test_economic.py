import unittest
import warnings
import sys
import os
from tools.economic_data_tool import fetch_economic_indicator

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

class TestEconomicIndicatorAPI(unittest.TestCase):

    def test_fetch_gdp_us(self):
        """Test fetching GDP (current US$) for the US."""
        result = fetch_economic_indicator("NY.GDP.MKTP.CD", "US")

        print("\n=== 🇺🇸 GDP (US) ===")
        print(result)

        self.assertIsInstance(result, dict)
        self.assertIn("indicator", result)
        self.assertEqual(result["indicator"], "NY.GDP.MKTP.CD")
        self.assertEqual(result["country"], "United States")

    def test_fetch_inflation_india(self):
        """Test fetching inflation rate for India."""
        result = fetch_economic_indicator("FP.CPI.TOTL.ZG", "IN")

        print("\n=== 🇮🇳 Inflation (India) ===")
        print(result)

        self.assertIsInstance(result, dict)
        self.assertIn("indicator", result)
        self.assertEqual(result["indicator"], "FP.CPI.TOTL.ZG")
        self.assertEqual(result["country"], "India")

    def test_invalid_indicator(self):
        """Test behavior with an invalid indicator."""
        result = fetch_economic_indicator("INVALID.INDICATOR", "US")

        print("\n=== ❌ Invalid Indicator ===")
        print(result)

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_invalid_country(self):
        """Test behavior with an invalid country code."""
        result = fetch_economic_indicator("NY.GDP.MKTP.CD", "XX")

        print("\n=== ❌ Invalid Country Code ===")
        print(result)

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
