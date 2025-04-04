import requests
import sqlite3
import time
from app.logger import logger
import os
from app.services.alpha_vantage import get_time_series_for_stock, get_stock_info

app_root = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(app_root, 'db/apex_data.db')


def fetch_nasdaq_100():
    """Web scraping to get NASDAQ-100 symbols"""
    url = "https://www.slickcharts.com/nasdaq100"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    import pandas as pd
    tables = pd.read_html(response.text)[0]['Symbol']
    return set(tables)

def store_stocks_in_db(stocks):
    """store stock information in stock_info table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        import datetime
        now = datetime.datetime.now().isoformat()

        for stock in stocks:
            cursor.execute("""
                INSERT OR REPLACE INTO stock_info 
                (symbol, name, exchange, asset_type, ipoDate, delistingDate, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock.get('symbol', ''),
                stock.get('name', ''),
                stock.get('exchange', ''),
                stock.get('assetType', ''),
                stock.get('ipoDate', ''),
                stock.get('delistingDate', ''),
                stock.get('status\r', ''),
                now
            ))
        conn.commit()
        logger.info("[TABLE FINISHED COMMIT] - stock_info")

    except Exception as e:
        print(f"store stock data fail: {str(e)}")
    finally:
        conn.close()


def store_time_series_in_db(symbol, time_series_data, interval='daily'):
    """store all time series into stock_data table"""
    if not time_series_data:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for date, daily_data in time_series_data.items():
            adj_close = float(daily_data['4. close']) if interval == "hourly" else float(daily_data.get('5. adjusted close'))
            volume = int(daily_data['5. volume'], 0) if interval == "hourly" else int(daily_data['6. volume'], 0)
            cursor.execute(f"""
                INSERT OR REPLACE INTO stock_data_{interval}
                (stock_symbol, closing_date, open_price, high_price, low_price, close_price, adj_close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                date,
                float(daily_data['1. open']),
                float(daily_data['2. high']),
                float(daily_data['3. low']),
                float(daily_data['4. close']),
                adj_close,
                volume
            ))

        conn.commit()

        print(f"store {symbol} successfully")
    except Exception as e:
        print(f"store {symbol} fail: {str(e)}")
    finally:
        conn.close()


def process_all_stocks(delay=0.3):
    """"""
    stocks = get_stock_info()
    if stocks:
        store_stocks_in_db(stocks)

    # get nasdaq_100_stock
    nasdaq_100_stock = fetch_nasdaq_100()

    # iterate list for three types of data
    interval_list = ['daily', 'hourly', 'monthly']
    for interval in interval_list:
        for i, symbol in enumerate(nasdaq_100_stock):
            print(f"ready to deal with {interval}'s {i+1}th stock: {symbol}")
            time_series = get_time_series_for_stock(symbol, interval=interval)
            if time_series:
                store_time_series_in_db(symbol, time_series, interval=interval)
                print(f"wait {delay} second for API limit")
                time.sleep(delay)
        logger.info(f"[TABLE FINISHED COMMIT] - stock_data{interval}")

