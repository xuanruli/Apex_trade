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

    @property
    def transaction_type(self):
        return self._transaction_type

    @property
    def shares(self):
        return self._shares

    @property
    def price_per_share(self):
        return self._price_per_share

    def save(self):
        """
        Inserts or updates the transaction record in the DB.

        - If self._id is None, perform an INSERT.
        - Otherwise, perform an UPDATE.
        """
        if self._id is not None:
            # Update existing transaction
            query = """
                UPDATE transactions SET user_id = %s, stock_symbol = %s, shares = %s, price_per_share = %s, transaction_type = %s, transaction_date = %s
                WHERE id = %s
            """
            execute_update(query, (self._user_id, self._stock_symbol, self._shares, self._price_per_share, self._transaction_type, self._transaction_date, self._id))
            logger.info(f"[TRANSACTION] - Updated transaction {self._id}")
        else:
            # Insert a new transaction
            query = """
                INSERT INTO transactions (user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_update(query, (self._user_id, self._stock_symbol, self._shares, self._price_per_share, self._transaction_type, self._transaction_date))
            logger.info(f"[TRANSACTION] - Inserted new transaction for user {self._user_id}")

            # Retrieve the newly assigned ID
            sel_query = """SELECT id FROM transactions WHERE user_id = %s AND stock_symbol = %s ORDER BY id DESC LIMIT 1"""
            result = execute_query(sel_query, (self._user_id, self._stock_symbol))
            if result:
                self._id = result[0]['id']

    @staticmethod
    def get_all_transactions(user_id):
        """
        Retrieve all transactions for the given user, ordered by transaction_date ASC.
        """
        query = """
            SELECT id, user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date
            FROM transactions WHERE user_id = %s ORDER BY transaction_date ASC
        """
        rows = execute_query(query, (user_id,))
        transactions = []
        for row in rows:
            quantity, price = row['shares'], row['price_per_share']
            total = row['shares'] * row['price_per_share']
            tx = {
                "stock_symbol": row['stock_symbol'],
                "shares": quantity,
                "price": price,
                "transaction_type": row['transaction_type'],
                "transaction_date": row['transaction_date'],
                "total": -total if row['transaction_type'] == "buy" else total
            }
            transactions.append(tx)
        return transactions

    @staticmethod
    def get_all_user_transactions():
        query = """ SELECT * FROM transactions"""
        result = execute_query(query, ())
        return result

    @staticmethod
    def get_transaction_by_id(transaction_id):
        """
        Find a single transaction by its primary key ID.
        """
        query = """SELECT id, user_id, stock_symbol, shares, price_per_share, transaction_type, transaction_date FROM transactions WHERE id = %s"""
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
            WHERE user_id = %s AND stock_symbol = %s
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
