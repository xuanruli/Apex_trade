import mysql.connector
from app.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': 'apex_data_mysql'
}

def setup_database():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS stock_info")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_info (
                symbol VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                exchange VARCHAR(255) NOT NULL,
                asset_type VARCHAR(255) NOT NULL,
                ipoDate VARCHAR(255),
                delistingDate VARCHAR(255),
                status VARCHAR(255) NOT NULL,
                last_updated VARCHAR(255) NOT NULL
            )
        """)
        logger.info("[TABLE CREATE] - stock_info")

        cursor.execute("DROP TABLE IF EXISTS stock_data_daily")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data_daily (
                stock_symbol VARCHAR(255) NOT NULL,
                closing_date DATE NOT NULL,
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
                        stock_symbol VARCHAR(255) NOT NULL,
                        closing_date DATE NOT NULL,
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
                                stock_symbol VARCHAR(255) NOT NULL,
                                closing_date DATE NOT NULL,
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

        # portfolio table
        cursor.execute("DROP TABLE IF EXISTS portfolio")
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS portfolio (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       user_id INT NOT NULL,
                       stock_symbol VARCHAR(255) NOT NULL,
                       total_shares REAL NOT NULL,
                       cost_basis REAL NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES users(id),
                       UNIQUE(user_id, stock_symbol)
                   )
               """)
        logger.info("[TABLE CREATE] - portfolio")

        # transaction table
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS transactions (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       user_id INT NOT NULL,
                       stock_symbol VARCHAR(255) NOT NULL,
                       shares REAL NOT NULL,
                       price_per_share REAL NOT NULL,
                       transaction_type VARCHAR(255) NOT NULL,
                       transaction_date DATE,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                   )
               """)
        logger.info("[TABLE CREATE] - transactions")

        # account
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("""
                           CREATE TABLE IF NOT EXISTS users (
                               id INT AUTO_INCREMENT PRIMARY KEY,
                               username VARCHAR(255) UNIQUE NOT NULL,
                               email VARCHAR(255) UNIQUE NOT NULL,
                               firstname VARCHAR(255),
                               lastname VARCHAR(255),
                               password_hash VARCHAR(255)
                           )
                       """)
        logger.info("[TABLE CREATE] - user")

        conn.commit()
    finally:
        conn.close()


