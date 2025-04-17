import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.models.transaction import Transaction


class TestTransaction(unittest.TestCase):

    @patch('app.models.transaction.execute_query')
    @patch('app.models.transaction.execute_update')
    def test_save_insert(self, mock_update, mock_query):
        # Simulate INSERT behavior
        mock_query.return_value = [{'id': 42}]
        tx = Transaction(user_id=1, stock_symbol='AAPL', shares=10, price_per_share=100, transaction_type='buy', transaction_date='2023-01-01')
        tx.save()
        self.assertEqual(tx._id, 42)
        self.assertTrue(mock_update.called)

    @patch('app.models.transaction.execute_update')
    def test_save_update(self, mock_update):
        tx = Transaction(id=5, user_id=1, stock_symbol='AAPL', shares=10, price_per_share=100, transaction_type='buy', transaction_date='2023-01-01')
        tx.save()
        mock_update.assert_called_once()

    @patch('app.models.transaction.execute_query')
    def test_get_user_transactions(self, mock_query):
        mock_query.return_value = [
            {
                'id': 1,
                'user_id': 1,
                'stock_symbol': 'AAPL',
                'shares': 10,
                'price_per_share': 100,
                'transaction_type': 'buy',
                'transaction_date': '2023-01-01'
            }
        ]
        transactions = Transaction.get_user_transactions(1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]._stock_symbol, 'AAPL')

    @patch('app.models.transaction.execute_query')
    def test_get_transaction_by_id(self, mock_query):
        mock_query.return_value = [{
            'id': 1,
            'user_id': 1,
            'stock_symbol': 'TSLA',
            'shares': 5,
            'price_per_share': 200,
            'transaction_type': 'sell',
            'transaction_date': '2023-02-02'
        }]
        tx = Transaction.get_transaction_by_id(1)
        self.assertIsNotNone(tx)
        self.assertEqual(tx._stock_symbol, 'TSLA')

    @patch('app.models.transaction.execute_query')
    def test_get_by_stock_and_user(self, mock_query):
        mock_query.return_value = [
            {
                'id': 3,
                'user_id': 1,
                'stock_symbol': 'MSFT',
                'shares': 7,
                'price_per_share': 120,
                'transaction_type': 'buy',
                'transaction_date': '2023-03-03'
            }
        ]
        txs = Transaction.get_by_stock_and_user(1, 'MSFT')
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0]._shares, 7)

    @patch('app.models.transaction.execute_update')
    def test_delete_transaction(self, mock_update):
        result = Transaction.delete_transaction(10)
        self.assertTrue(result)
        mock_update.assert_called_once()

    @patch('app.models.transaction.execute_query')
    def test_calculate_portfolio_impact(self, mock_query):
        mock_query.return_value = [
            {
                'id': 1,
                'user_id': 1,
                'stock_symbol': 'AAPL',
                'shares': 10,
                'price_per_share': 100,
                'transaction_type': 'buy',
                'transaction_date': '2023-01-01'
            },
            {
                'id': 2,
                'user_id': 1,
                'stock_symbol': 'AAPL',
                'shares': 5,
                'price_per_share': 110,
                'transaction_type': 'sell',
                'transaction_date': '2023-01-02'
            }
        ]
        shares, cost_basis = Transaction.calculate_portfolio_impact(1, 'AAPL')
        self.assertEqual(shares, 5)
        self.assertTrue(cost_basis > 0)

    def test_to_dict(self):
        tx = Transaction(id=99, user_id=2, stock_symbol='GOOG', shares=15, price_per_share=1500, transaction_type='buy', transaction_date='2023-05-01')
        tx_dict = tx.to_dict()
        self.assertEqual(tx_dict['id'], 99)
        self.assertEqual(tx_dict['stock_symbol'], 'GOOG')
        self.assertEqual(tx_dict['shares'], 15)


if __name__ == '__main__':
    unittest.main()
