import sqlite3
from app.logger import logger
DB_PATH = 'db/apex_data.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS stock_info")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_info (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                exchange TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                ipoDate TEXT,
                delistingDate TEXT,
                status TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        logger.info("[TABLE CREATE] - stock_info")

        cursor.execute("DROP TABLE IF EXISTS stock_data_daily")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data_daily (
                stock_symbol TEXT NOT NULL,
                closing_date TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                adj_close_price REAL NOT NULL,
                volume INTEGER NOT NULL,
                PRIMARY KEY (stock_symbol, closing_date)
            )
        """)
        logger.info("[TABLE CREATE] - stock_data_daily")

        cursor.execute("DROP TABLE IF EXISTS stock_data_monthly")
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data_monthly (
                        stock_symbol TEXT NOT NULL,
                        closing_date TEXT NOT NULL,
                        open_price REAL NOT NULL,
                        high_price REAL NOT NULL,
                        low_price REAL NOT NULL,
                        close_price REAL NOT NULL,
                        adj_close_price REAL NOT NULL,
                        volume INTEGER NOT NULL,
                        PRIMARY KEY (stock_symbol, closing_date)
                    )
                """)
        logger.info("[TABLE CREATE] - stock_data_monthly")

        cursor.execute("DROP TABLE IF EXISTS stock_data_hourly")
        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS stock_data_hourly (
                                stock_symbol TEXT NOT NULL,
                                closing_date TEXT NOT NULL,
                                open_price REAL NOT NULL,
                                high_price REAL NOT NULL,
                                low_price REAL NOT NULL,
                                close_price REAL NOT NULL,
                                adj_close_price REAL NOT NULL,
                                volume INTEGER NOT NULL,
                                PRIMARY KEY (stock_symbol, closing_date)
                            )
                        """)
        logger.info("[TABLE CREATE] - stock_data_monthly")

        # account
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       email TEXT UNIQUE NOT NULL,
                       firstname TEXT,
                       lastname TEXT,
                       password_hash TEXT
                   )
               """)
        logger.info("[TABLE CREATE] - user")

        # portfolio table
        cursor.execute("DROP TABLE IF EXISTS portfolio")
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS portfolio (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       stock_symbol TEXT NOT NULL,
                       total_shares REAL NOT NULL,
                       cost_basis REAL NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES users(id),
                       FOREIGN KEY (stock_symbol) REFERENCES stock_info(symbol),
                       UNIQUE(user_id, stock_symbol)
                   )
               """)
        logger.info("[TABLE CREATE] - portfolio")

        # transaction table
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS transactions (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       stock_symbol TEXT NOT NULL,
                       shares REAL NOT NULL,
                       price_per_share REAL NOT NULL,
                       transaction_type TEXT NOT NULL,
                       transaction_date TEXT NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES users(id),
                       FOREIGN KEY (stock_symbol) REFERENCES stock_info(symbol)
                   )
               """)
        logger.info("[TABLE CREATE] - transactions")

        conn.commit()
    finally:
        conn.close()
