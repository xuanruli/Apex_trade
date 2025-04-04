from app.db import execute_query, execute_update
from app.logger import logger


class Portfolio:

    def __init__(self, user_id):
        self._user_id = user_id
        self._holdings = {}
        self._load_holdings()

    @property
    def user_id(self):
        return self._user_id

    @property
    def holdings(self):
        return self._holdings

    def _load_holdings(self):
        """
        Load the user's holdings from the 'portfolio' table into self._holdings.
        """
        query = """
            SELECT stock_symbol, total_shares, cost_basis
            FROM portfolio
            WHERE user_id = ?
        """
        rows = execute_query(query, (self._user_id,))
        for row in rows:
            symbol = row['stock_symbol']
            shares = row['total_shares']
            cost_basis = row['cost_basis']
            self._holdings[symbol] = (shares, cost_basis)

    def add_asset(self, symbol, quantity, price):
        """
        Add or update a given asset in the portfolio.
        """
        total_cost = quantity * price
        existing = self._holdings.get(symbol)
        if existing:
            current_shares, current_basis = existing
            new_shares = current_shares + quantity
            new_basis = current_basis + total_cost
            query = """
                UPDATE portfolio
                SET total_shares = ?, cost_basis = ?
                WHERE user_id = ? AND stock_symbol = ?
            """
            execute_update(query, (new_shares, new_basis, self._user_id, symbol))
            self._holdings[symbol] = (new_shares, new_basis)
        else:
            query = """
                INSERT INTO portfolio (user_id, stock_symbol, total_shares, cost_basis)
                VALUES (?, ?, ?, ?)
            """
            execute_update(query, (self._user_id, symbol, quantity, total_cost))
            self._holdings[symbol] = (quantity, total_cost)

        logger.info(f"[PORTFOLIO] User {self._user_id} added {quantity} shares of {symbol} at ${price} each.")

    def remove_asset(self, symbol, quantity, price):
        """
        Remove shares of the given asset from the portfolio.
        """
        existing = self._holdings.get(symbol)
        if not existing:
            logger.info(f"[PORTFOLIO] User {self._user_id} has no holding in {symbol}.")
            return False

        current_shares, current_basis = existing
        if quantity > current_shares:
            logger.info(f"[PORTFOLIO] Not enough {symbol} shares to remove for user {self._user_id}.")
            return False

        new_shares = current_shares - quantity
        if new_shares == 0:
            query = """
                DELETE FROM portfolio
                WHERE user_id = ? AND stock_symbol = ?
            """
            execute_update(query, (self._user_id, symbol))
            del self._holdings[symbol]
            logger.info(f"[PORTFOLIO] User {self._user_id} removed all {symbol}.")
        else:
            # Adjust cost basis proportionally
            ratio = new_shares / current_shares
            new_basis = current_basis * ratio
            query = """
                UPDATE portfolio
                SET total_shares = ?, cost_basis = ?
                WHERE user_id = ? AND stock_symbol = ?
            """
            execute_update(query, (new_shares, new_basis, self._user_id, symbol))
            self._holdings[symbol] = (new_shares, new_basis)
            logger.info(
                f"[PORTFOLIO] User {self._user_id} removed {quantity} shares of {symbol}, new total={new_shares}")

        return True

    def calculate_total_value(self):
        """
        Calculate total market value by multiplying each holding's shares
        by the latest close_price in 'stock_data_daily'.
        """
        total_value = 0.0

        for symbol, (shares, _) in self._holdings.items():
            query = """
                SELECT close_price
                FROM stock_data_daily
                WHERE stock_symbol = ?
                ORDER BY closing_date DESC
                LIMIT 1
            """
            row = execute_query(query, (symbol,))
            if row:
                total_value += (row[0]['close_price'] * shares)

        logger.info(f"[PORTFOLIO] User {self._user_id}'s total value: {total_value:.2f}")
        return total_value

    def get_portfolio_summary(self):
        """
        Returns a summary of the portfolio with current market values.
        """
        portfolio_summary = []

        for symbol, (shares, cost_basis) in self._holdings.items():
            query = """
                SELECT close_price
                FROM stock_data_daily
                WHERE stock_symbol = ?
                ORDER BY closing_date DESC
                LIMIT 1
            """
            price_result = execute_query(query, (symbol,))

            if price_result:
                current_price = price_result[0]['close_price']
                avg_cost = cost_basis / shares if shares > 0 else 0
                market_value = current_price * shares
                gain_loss = market_value - cost_basis
                percent_change = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0

                portfolio_summary.append({
                    'symbol': symbol,
                    'shares': shares,
                    'avg_cost': avg_cost,
                    'cost_basis': cost_basis,
                    'current_price': current_price,
                    'market_value': market_value,
                    'gain_loss': gain_loss,
                    'percent_change': percent_change
                })

        return portfolio_summary

    @staticmethod
    def get_by_user_id(user_id):
        """
        Get a portfolio by user ID.
        """
        return Portfolio(user_id)

    @staticmethod
    def get_holdings_by_symbol(user_id, symbol):
        """
        Get a specific holding from a user's portfolio.
        """
        query = """
            SELECT total_shares, cost_basis
            FROM portfolio
            WHERE user_id = ? AND stock_symbol = ?
        """
        result = execute_query(query, (user_id, symbol))

        if result:
            return (result[0]['total_shares'], result[0]['cost_basis'])
        return None

    @staticmethod
    def get_all_portfolios():
        """
        Get all unique portfolios in the system.

        :return: A list of user_ids that have portfolios
        """
        query = """
            SELECT DISTINCT user_id
            FROM portfolio
        """
        result = execute_query(query, ())
        return [row['user_id'] for row in result]

    def update_from_transactions(self, transactions):
        """
        Rebuild the portfolio based on transaction history.
        This is useful for reconciliation or after deleting transactions.

        :param transactions: List of Transaction objects
        """
        # Clear existing holdings
        clear_query = """
            DELETE FROM portfolio
            WHERE user_id = ?
        """
        execute_update(clear_query, (self._user_id,))

        # Reset holdings dictionary
        self._holdings = {}

        # Process each transaction
        for tx in transactions:
            if tx.transaction_type.lower() == 'buy':
                self.add_asset(tx.stock_symbol, tx.shares, tx.price_per_share)
            elif tx.transaction_type.lower() == 'sell':
                self.remove_asset(tx.stock_symbol, tx.shares, tx.price_per_share)

        logger.info(f"[PORTFOLIO] Updated portfolio for user {self._user_id} from transactions")

    def to_dict(self):
        """
        Convert portfolio to dictionary for JSON serialization

        :return: Dictionary representation of portfolio
        """
        portfolio_dict = {
            'user_id': self._user_id,
            'holdings': {}
        }

        for symbol, (shares, cost_basis) in self._holdings.items():
            portfolio_dict['holdings'][symbol] = {
                'shares': shares,
                'cost_basis': cost_basis,
                'avg_cost': cost_basis / shares if shares > 0 else 0
            }

        return portfolio_dict