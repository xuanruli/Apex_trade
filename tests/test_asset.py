import unittest
from unittest.mock import patch
import pandas as pd
from datetime import datetime
from app.models.asset import Asset

class TestAsset(unittest.TestCase):

    def setUp(self):
        self.asset = Asset(symbol='AAPL', name='Apple Inc.')
        self.mock_data = {
            '2025-03-31': [170, 172, 168, 171, 171, 1000000, 0, 1],
            '2025-03-30': [168, 170, 167, 169, 169, 1200000, 0, 1],
            '2025-03-29': [165, 168, 164, 167, 167, 900000, 0, 1]
        }

    @patch('app.models.asset.get_time_series_for_stock')
    def test_get_current_price(self, mock_get_data):
        mock_get_data.return_value = self.mock_data
        current_price = self.asset.get_current_price()
        self.assertEqual(current_price, 171)

    @patch('app.models.asset.get_time_series_for_stock')
    def test_get_historical_data(self, mock_get_data):
        mock_get_data.return_value = self.mock_data
        start_date = '2025-03-30'
        end_date = '2025-03-31'
        df = self.asset.get_historical_data(start_date, end_date)

        # Assert index is datetime and within range
        self.assertIsInstance(df.index, pd.DatetimeIndex)
        self.assertTrue(all((df.index >= pd.to_datetime(start_date)) & 
                            (df.index <= pd.to_datetime(end_date))))

        # Assert data contents
        self.assertEqual(len(df), 2)
        self.assertIn('close', df.columns)
        self.assertEqual(df.loc['2025-03-31']['close'], 171)

    def test_convert_to_df(self):
        df = self.asset.convert_to_df(self.mock_data)

        # Check index type
        self.assertIsInstance(df.index, pd.DatetimeIndex)

        # Check columns
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        self.assertListEqual(list(df.columns), expected_columns)

        # Check values
        self.assertEqual(df.loc[datetime(2025, 3, 31)]['close'], 171)

if __name__ == '__main__':
    unittest.main()
