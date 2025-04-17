import unittest
from unittest.mock import patch, MagicMock
from app.services import alpha_vantage as av


class TestAlphaVantage(unittest.TestCase):

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_company_overview(self, mock_get):
        mock_get.return_value.json.return_value = {'Symbol': 'AAPL'}
        result = av.get_company_overview('AAPL')
        self.assertEqual(result['Symbol'], 'AAPL')

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_global_quote(self, mock_get):
        mock_get.return_value.json.return_value = {'Global Quote': {'05. price': '150.00'}}
        result = av.get_global_quote('AAPL')
        self.assertEqual(result['05. price'], '150.00')

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_news(self, mock_get):
        mock_get.return_value.json.return_value = {
            'feed': [{'title': 'Headline 1'}, {'title': 'Headline 2'}]
        }
        result = av.get_news('AAPL')
        self.assertIn('feed', result)

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_time_series_for_stock_daily(self, mock_get):
        mock_get.return_value.json.return_value = {
            "Time Series (Daily)": {
                "2024-04-01": {
                    "1. open": "100", "2. high": "110", "3. low": "90",
                    "4. close": "105", "5. adjusted close": "104.5", "6. volume": "1000000"
                }
            }
        }
        result = av.get_time_series_for_stock('AAPL', interval='daily')
        self.assertIn("2024-04-01", result)

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_rsi_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "Technical Analysis: RSI": {
                "2024-04-01": {"RSI": "45.67"}
            }
        }
        result = av.get_rsi("AAPL")
        self.assertEqual(result["2024-04-01"], 45.67)

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_stock_quote_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "Global Quote": {
                "01. symbol": "AAPL",
                "02. open": "170",
                "03. high": "175",
                "04. low": "169",
                "05. price": "173",
                "06. volume": "120000",
                "07. latest trading day": "2024-04-10",
                "08. previous close": "171",
                "09. change": "2",
                "10. change percent": "1.17%"
            }
        }
        result = av.get_stock_quote("AAPL")
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["price"], 173.0)

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_stock_info(self, mock_get):
        mock_csv = "symbol,name,exchange,assetType,ipoDate,delistingDate,status\nAAPL,Apple Inc.,NASDAQ,Equity,1980-12-12,,Active"
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_csv
        result = av.get_stock_info()
        self.assertEqual(result[0]["symbol"], "AAPL")

    @patch('app.services.alpha_vantage.requests.get')
    def test_get_overview(self, mock_get):
        mock_get.return_value.json.return_value = {"Name": "Apple Inc.", "Symbol": "AAPL"}
        result = av.get_overview("AAPL")
        self.assertEqual(result["Name"], "Apple Inc.")


if __name__ == '__main__':
    unittest.main()
