import unittest
from unittest.mock import patch, MagicMock, call
from app.db import data_loader


class TestDataLoader(unittest.TestCase):

    @patch('app.db.data_loader.requests.get')
    @patch('pandas.read_html')
    def test_fetch_nasdaq_100(self, mock_read_html, mock_get):
        mock_read_html.return_value = [ {'Symbol': ['AAPL', 'GOOG', 'MSFT']} ]
        result = data_loader.fetch_nasdaq_100()
        self.assertIn('AAPL', result)
        self.assertEqual(len(result), 3)

    @patch('app.db.data_loader.sqlite3.connect')
    def test_store_stocks_in_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        sample_stock = [{
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'exchange': 'NASDAQ',
            'assetType': 'Equity',
            'ipoDate': '1980-12-12',
            'delistingDate': '',
            'status\r': 'Active'
        }]

        data_loader.store_stocks_in_db(sample_stock)

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.db.data_loader.sqlite3.connect')
    def test_store_time_series_in_db(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        sample_series = {
            "2024-04-01": {
                "1. open": "100.0",
                "2. high": "110.0",
                "3. low": "95.0",
                "4. close": "105.0",
                "5. adjusted close": "104.5",
                "6. volume": "1000000"
            }
        }

        data_loader.store_time_series_in_db("AAPL", sample_series, interval='daily')
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('app.db.data_loader.time.sleep')
    @patch('app.db.data_loader.store_time_series_in_db')
    @patch('app.db.data_loader.fetch_nasdaq_100')
    @patch('app.db.data_loader.store_stocks_in_db')
    @patch('app.db.data_loader.get_time_series_for_stock')
    @patch('app.db.data_loader.get_stock_info')
    def test_process_all_stocks(
        self,
        mock_get_stock_info,
        mock_get_time_series,
        mock_store_stocks,
        mock_fetch_nasdaq,
        mock_store_time_series,
        mock_sleep
    ):
        mock_get_stock_info.return_value = [{'symbol': 'AAPL'}]
        mock_fetch_nasdaq.return_value = {'AAPL'}
        mock_get_time_series.return_value = {
            "2024-04-01": {
                "1. open": "100.0",
                "2. high": "110.0",
                "3. low": "95.0",
                "4. close": "105.0",
                "5. adjusted close": "104.5",
                "6. volume": "1000000"
            }
        }

        data_loader.process_all_stocks(delay=0)

        self.assertEqual(mock_store_stocks.call_count, 1)
        self.assertEqual(mock_fetch_nasdaq.call_count, 1)
        self.assertEqual(mock_get_time_series.call_count, 3)  # one for each interval
        self.assertEqual(mock_store_time_series.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 3)


if __name__ == '__main__':
    unittest.main()
