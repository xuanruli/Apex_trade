from datetime import datetime
from app.db import execute_query, execute_update
from app.logger import logger


class Transaction:

    def __init__(self, user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date=None, id=None):
        self._id = id
        self._user_id = user_id
        self._stock_symbol = stock_symbol
        self._shares = shares
        self._price_per_share = price_per_share
        self._transaction_type = transaction_type
        self._transaction_date = transaction_date


    def save(self):
        """
        Inserts or updates the transaction record in the DB.

        - If self._id is None, perform an INSERT.
        - Otherwise, perform an UPDATE.
        """
        if self._id is not None:
            # Update existing transaction
            query = """
                UPDATE transactions SET user_id = ?, stock_symbol = ?, shares = ?, price_per_share = ?, transaction_type = ?, transaction_date = ?
                WHERE id = ?
            """
            execute_update(query, (self._user_id, self._stock_symbol, self._shares, self._price_per_share, self._transaction_type, self._transaction_date, self._id))
            logger.info(f"[TRANSACTION] - Updated transaction {self._id}")
        else:
            # Insert a new transaction
            query = """
                INSERT INTO transactions (user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            execute_update(query, (self._user_id, self._stock_symbol, self._shares, self._price_per_share, self._transaction_type, self._transaction_date))
            logger.info(f"[TRANSACTION] - Inserted new transaction for user {self._user_id}")

            # Retrieve the newly assigned ID
            sel_query = """SELECT id FROM transactions WHERE user_id = ? AND stock_symbol = ? ORDER BY id DESC LIMIT 1"""
            result = execute_query(sel_query, (self._user_id, self._stock_symbol))
            if result:
                self._id = result[0]['id']

    @staticmethod
    def get_user_transactions(user_id):
        """
        Retrieve all transactions for the given user, ordered by transaction_date ASC.
        """
        query = """
            SELECT id, user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date
            FROM transactions WHERE user_id = ? ORDER BY transaction_date ASC
        """
        rows = execute_query(query, (user_id,))
        transactions = []
        for row in rows:
            tx = Transaction(
                id=row['id'],
                user_id=row['user_id'],
                stock_symbol=row['stock_symbol'],
                shares=row['shares'],
                price_per_share=row['price_per_share'],
                transaction_type=row['transaction_type'],
                transaction_date=row['transaction_date']
            )
            transactions.append(tx)
        return transactions

    @staticmethod
    def get_transaction_by_id(transaction_id):
        """
        Find a single transaction by its primary key ID.
        """
        query = """
            SELECT
                id,
                user_id,
                stock_symbol,
                shares,
                price_per_share,
                transaction_type,
                transaction_date
            FROM transactions
            WHERE id = ?
        """
        rows = execute_query(query, (transaction_id,))
        if rows:
            row = rows[0]
            return Transaction(
                id=row['id'],
                user_id=row['user_id'],
                stock_symbol=row['stock_symbol'],
                shares=row['shares'],
                price_per_share=row['price_per_share'],
                transaction_type=row['transaction_type'],
                transaction_date=row['transaction_date']
            )
        return None

    @staticmethod
    def get_by_stock_and_user(user_id, stock_symbol):
        """
        Retrieve all transactions for a specific user and stock symbol.
        """
        query = """
            SELECT
                id,
                user_id,
                stock_symbol,
                shares,
                price_per_share,
                transaction_type,
                transaction_date
            FROM transactions
            WHERE user_id = ? AND stock_symbol = ?
            ORDER BY transaction_date ASC
        """
        rows = execute_query(query, (user_id, stock_symbol))
        transactions = []
        for row in rows:
            tx = Transaction(
                id=row['id'],
                user_id=row['user_id'],
                stock_symbol=row['stock_symbol'],
                shares=row['shares'],
                price_per_share=row['price_per_share'],
                transaction_type=row['transaction_type'],
                transaction_date=row['transaction_date']
            )
            transactions.append(tx)
        return transactions

    @staticmethod
    def delete_transaction(transaction_id):
        """
        Delete a transaction by its ID.
        """
        try:
            query = "DELETE FROM transactions WHERE id = ?"
            execute_update(query, (transaction_id,))
            logger.info(f"[TRANSACTION] - Deleted transaction {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"[TRANSACTION] - Error deleting transaction {transaction_id}: {e}")
            return False

    @staticmethod
    def calculate_portfolio_impact(user_id, stock_symbol):
        """
        Calculate the total shares and cost basis for a specific stock in a user's portfolio
        based on all transactions.
        """
        transactions = Transaction.get_by_stock_and_user(user_id, stock_symbol)

        total_shares = 0
        total_cost = 0

        for tx in transactions:
            if tx.transaction_type == 'buy':
                total_shares += tx.shares
                total_cost += tx.shares * tx.price_per_share
            elif tx.transaction_type == 'sell':
                if total_shares >= tx.shares:
                    # Simplified approach: reduce shares proportionally to maintain average cost
                    share_ratio = (total_shares - tx.shares) / total_shares if total_shares > 0 else 0
                    total_cost *= share_ratio
                    total_shares -= tx.shares
                else:
                    # Error case: selling more than owned
                    logger.warning(f"[TRANSACTION] - Attempting to sell more shares than owned: {tx.id}")
                    total_shares = 0
                    total_cost = 0

        # Calculate cost basis (average cost per share)
        cost_basis = total_cost / total_shares if total_shares > 0 else 0

        return (total_shares, cost_basis)

    def to_dict(self):
        """
        Convert transaction object to a dictionary

        :return: Dictionary representation of the transaction
        """
        return {
            'id': self._id,
            'user_id': self._user_id,
            'stock_symbol': self._stock_symbol,
            'shares': self._shares,
            'price_per_share': self._price_per_share,
            'transaction_type': self._transaction_type,
            'transaction_date': self._transaction_date
        }