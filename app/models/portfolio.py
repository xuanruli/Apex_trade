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
        query = """SELECT stock_symbol, total_shares, cost_basis FROM portfolio WHERE user_id = %s """
        rows = execute_query(query, (self._user_id,))
        for row in rows:
            symbol = row['stock_symbol']
            shares = row['total_shares']
            cost_basis = row['cost_basis']
            self._holdings[symbol] = (shares, cost_basis)

    def update_portfolio(self, symbol, quantity, price, order_type):

        old_shares, old_cost = self._holdings.get(symbol, (0, 0))
        order_cost = quantity * price
        if (old_shares, old_cost) == (0, 0):
            query = """INSERT INTO portfolio (user_id, stock_symbol, total_shares, cost_basis) VALUES (%s, %s, %s, %s)"""
            execute_update(query, (self._user_id, symbol, quantity, order_cost))
            logger.info(f"[PORTFOLIO] - user {self._user_id} {order_type} {quantity} of {symbol} with {price} and this is the new holding cost")
            return True

        if order_type == "buy":
            new_cost = old_cost + order_cost
            new_shares = old_shares + quantity
        elif order_type == "sell":
            old_price = old_cost / old_shares
            new_cost = old_cost - old_price * quantity
            new_shares = old_shares - quantity
            if new_shares == 0:
                query = """DELETE FROM portfolio WHERE user_id = %s AND stock_symbol = %s"""
                execute_update(query, (self._user_id, symbol,))
                return True
        else:
            raise ValueError("incorrect order type")

        query = """UPDATE portfolio SET total_shares = %s, cost_basis = %s WHERE user_id = %s AND stock_symbol = %s"""
        execute_update(query, (new_shares, new_cost, self._user_id, symbol,))

        logger.info(f"[PORTFOLIO] - user {self._user_id} {order_type} {quantity} of {symbol} with {price} and now user new holding cost for {symbol} is {new_cost} and {new_shares} shares")
        return True

    def get_portfolio_summary(self):
        """
        Calculate total market value by multiplying each holding's shares
        by the latest close_price in 'stock_data_hourly'.
        """
        total_value, total_holdings, total_cost = 0.0, 0, 0.0

        for symbol, (shares, cost_basis) in self._holdings.items():
            query = """SELECT close_price FROM stock_data_hourly WHERE stock_symbol = %s ORDER BY closing_date DESC LIMIT 1 """
            row = execute_query(query, (symbol,))
            if row:
                total_value += (row[0]['close_price'] * shares)
            total_holdings += shares
            total_cost += cost_basis
        total_pl_percent = ((total_value - total_cost) / total_cost) * 100 if total_cost else 0.0
        total_pl = (total_value - total_cost)

        logger.info(f"[PORTFOLIO] User {self._user_id}'s total value: {total_value:.2f} with total shares {total_holdings} + total cost {total_cost} + total P&L {total_pl}")
        return {"total_holdings": total_holdings, "total_cost": total_cost, "total_value": total_value, "total_pl": total_pl, "total_pl_percent": total_pl_percent}

    def get_holding_summary(self):
        """
        Returns a summary of the portfolio with current market values.
        """
        portfolio_summary = []

        for symbol, (shares, cost_basis) in self._holdings.items():
            query = """SELECT close_price FROM stock_data_hourly WHERE stock_symbol = %s ORDER BY closing_date DESC LIMIT 1"""
            price_result = execute_query(query, (symbol,))

            if price_result:
                current_price = price_result[0]['close_price']
                avg_cost = cost_basis / shares if shares > 0 else 0
                market_value = current_price * shares
                PL = market_value - cost_basis
                percent_PL = (PL / cost_basis) * 100 if cost_basis > 0 else 0

                portfolio_summary.append({
                    'symbol': symbol,
                    'shares': shares,
                    'avg_cost': avg_cost,
                    'cost_basis': cost_basis,
                    'current_price': current_price,
                    'market_value': market_value,
                    'gain_loss': PL,
                    'percent_change': percent_PL
                })

        return portfolio_summary

    @staticmethod
    def check_portfolio(user_id):
        query = """SELECT COUNT(*) as count FROM portfolio WHERE user_id = %s"""
        result = execute_query(query,(user_id,))
        if result[0]['count'] == 0:
            return False
        return True

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
        query = """ SELECT total_shares, cost_basis FROM portfolio WHERE user_id = %s AND stock_symbol = %s"""
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
        query = """ SELECT * FROM portfolio"""
        result = execute_query(query, ())
        return result

