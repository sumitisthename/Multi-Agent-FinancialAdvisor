import unittest
from unittest.mock import patch, MagicMock
import warnings
from tools.economic_data_tool import fetch_gdp_data, fetch_pce_data, fetch_employment_data

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

class TestEconomicDataTool(unittest.TestCase):

    @patch('beaapi.get_data')
    def test_fetch_gdp_data_success(self, mock_get_data):
        """Test fetching GDP data successfully."""
        mock_data = {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "TableName": "T10105",
                            "SeriesCode": "A191RL",
                            "LineNumber": "1",
                            "LineDescription": "Gross domestic product",
                            "TimePeriod": "2023Q1",
                            "METRIC_NAME": "Current-dollar and real GDP",
                            "CL_UNIT": "Level",
                            "UNIT_MULT": "3",
                            "DataValue": "26,813.6"
                        }
                    ]
                }
            }
        }
        mock_get_data.return_value = mock_data
        result = fetch_gdp_data()
        self.assertEqual(result, mock_data)

    @patch('beaapi.get_data')
    def test_fetch_gdp_data_error(self, mock_get_data):
        """Test error handling when fetching GDP data."""
        mock_get_data.side_effect = Exception("API Error")
        result = fetch_gdp_data()
        self.assertEqual(result, {"error": "API Error"})

    @patch('beaapi.get_data')
    def test_fetch_pce_data_success(self, mock_get_data):
        """Test fetching PCE data successfully."""
        mock_data = {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "TableName": "T20304",
                            "SeriesCode": "DPCERG",
                            "LineNumber": "1",
                            "LineDescription": "Personal consumption expenditures",
                            "TimePeriod": "2023Q1",
                            "METRIC_NAME": "Price indexes",
                            "CL_UNIT": "Index numbers, 2017=100",
                            "UNIT_MULT": "0",
                            "DataValue": "119.545"
                        }
                    ]
                }
            }
        }
        mock_get_data.return_value = mock_data
        result = fetch_pce_data()
        self.assertEqual(result, mock_data)

    @patch('beaapi.get_data')
    def test_fetch_pce_data_error(self, mock_get_data):
        """Test error handling when fetching PCE data."""
        mock_get_data.side_effect = Exception("API Error")
        result = fetch_pce_data()
        self.assertEqual(result, {"error": "API Error"})

    @patch('beaapi.get_data')
    def test_fetch_employment_data_success(self, mock_get_data):
        """Test fetching employment data successfully."""
        mock_data = {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "GeoFips": "00000",
                            "GeoName": "United States",
                            "LineCode": "3",
                            "LineDescription": "Full-time and part-time employment",
                            "TimePeriod": "2023",
                            "METRIC_NAME": "Employment",
                            "CL_UNIT": "Number of persons",
                            "UNIT_MULT": "0",
                            "DataValue": "207,649"
                        }
                    ]
                }
            }
        }
        mock_get_data.return_value = mock_data
        result = fetch_employment_data()
        self.assertEqual(result, mock_data)

    @patch('beaapi.get_data')
    def test_fetch_employment_data_error(self, mock_get_data):
        """Test error handling when fetching employment data."""
        mock_get_data.side_effect = Exception("API Error")
        result = fetch_employment_data()
        self.assertEqual(result, {"error": "API Error"})

if __name__ == '__main__':
    unittest.main()
