import unittest
from unittest.mock import patch, MagicMock
from app.models.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    @patch('app.models.portfolio.execute_query')
    def test_load_holdings(self, mock_query):
        mock_query.return_value = [
            {'stock_symbol': 'AAPL', 'total_shares': 10, 'cost_basis': 1500},
            {'stock_symbol': 'TSLA', 'total_shares': 5, 'cost_basis': 3000},
        ]
        p = Portfolio(user_id=1)
        self.assertEqual(p.holdings['AAPL'], (10, 1500))
        self.assertEqual(p.holdings['TSLA'], (5, 3000))

    @patch('app.models.portfolio.execute_update')
    @patch('app.models.portfolio.execute_query')
    def test_add_asset_new(self, mock_query, mock_update):
        mock_query.return_value = []
        p = Portfolio(user_id=2)
        p._holdings = {}  # Simulate no holdings
        p.add_asset('GOOGL', 4, 500)
        self.assertIn('GOOGL', p.holdings)
        self.assertEqual(p.holdings['GOOGL'], (4, 2000))

    @patch('app.models.portfolio.execute_update')
    @patch('app.models.portfolio.execute_query')
    def test_add_asset_existing(self, mock_query, mock_update):
        mock_query.return_value = []
        p = Portfolio(user_id=3)
        p._holdings = {'MSFT': (3, 600)}
        p.add_asset('MSFT', 2, 250)
        self.assertEqual(p.holdings['MSFT'], (5, 1100))

    @patch('app.models.portfolio.execute_update')
    @patch('app.models.portfolio.execute_query')
    def test_remove_asset_partial(self, mock_query, mock_update):
        mock_query.return_value = []
        p = Portfolio(user_id=4)
        p._holdings = {'AMZN': (10, 2000)}
        result = p.remove_asset('AMZN', 4, 300)
        self.assertTrue(result)
        self.assertEqual(p.holdings['AMZN'][0], 6)

    @patch('app.models.portfolio.execute_update')
    @patch('app.models.portfolio.execute_query')
    def test_remove_asset_all(self, mock_query, mock_update):
        mock_query.return_value = []
        p = Portfolio(user_id=5)
        p._holdings = {'NFLX': (2, 600)}
        result = p.remove_asset('NFLX', 2, 300)
        self.assertTrue(result)
        self.assertNotIn('NFLX', p.holdings)

    @patch('app.models.portfolio.execute_query')
    def test_calculate_total_value(self, mock_query):
        # First call for _load_holdings
        mock_query.side_effect = [
            [{'stock_symbol': 'AAPL', 'total_shares': 3, 'cost_basis': 900},
            {'stock_symbol': 'TSLA', 'total_shares': 1, 'cost_basis': 800}],
            [{'close_price': 300}],  # for AAPL
            [{'close_price': 800}],  # for TSLA
        ]
        p = Portfolio(user_id=6)
        value = p.calculate_total_value()
        self.assertEqual(value, 3 * 300 + 1 * 800)

    @patch('app.models.portfolio.execute_query')
    def test_get_portfolio_summary(self, mock_query):
        # First for _load_holdings
        mock_query.side_effect = [
            [{'stock_symbol': 'AAPL', 'total_shares': 5, 'cost_basis': 400}],
            [{'close_price': 100}],  # AAPL
        ]
        p = Portfolio(user_id=7)
        summary = p.get_portfolio_summary()
        self.assertEqual(summary[0]['symbol'], 'AAPL')
        self.assertEqual(summary[0]['market_value'], 500)
        self.assertAlmostEqual(summary[0]['gain_loss'], 100)

    @patch('app.models.portfolio.execute_query')
    def test_get_holdings_by_symbol(self, mock_query):
        mock_query.return_value = [{'total_shares': 3, 'cost_basis': 450}]
        result = Portfolio.get_holdings_by_symbol(8, 'GOOG')
        self.assertEqual(result, (3, 450))

    @patch('app.models.portfolio.execute_query')
    def test_get_all_portfolios(self, mock_query):
        mock_query.return_value = [{'user_id': 1}, {'user_id': 2}]
        result = Portfolio.get_all_portfolios()
        self.assertEqual(result, [1, 2])


if __name__ == '__main__':
    unittest.main()
