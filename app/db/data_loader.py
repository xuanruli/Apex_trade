import datetime as _dt
import time
from typing import Iterable, Mapping, Set

import pandas as pd
import requests
import sqlite3

from app.logger import logger
from .schema import DB_CONFIG
from app.services.alpha_vantage import get_time_series_for_stock, get_stock_info


def fetch_nasdaq_100() -> Set[str]:
    url = "https://www.slickcharts.com/nasdaq100"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    table = pd.read_html(response.text)[0]
    symbols_series = table["Symbol"]
    if not hasattr(symbols_series, "str"):
        symbols_series = pd.Series(symbols_series)
    return set(symbols_series.astype(str).str.strip().str.upper())


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _get_connection():
    if "database" in DB_CONFIG and len(DB_CONFIG) == 1:
        return sqlite3.connect(DB_CONFIG["database"])
    return sqlite3.connect(DB_CONFIG.get("database", ":memory:"))


def store_stocks_in_db(stocks: Iterable[Mapping[str, str]]) -> None:
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        for stock in stocks:
            cursor.execute(
                """
                REPLACE INTO stock_info
                    (symbol, name, exchange, asset_type,
                     ipoDate, delistingDate, status, last_updated)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    stock.get("symbol", ""),
                    stock.get("name", ""),
                    stock.get("exchange", ""),
                    stock.get("assetType", ""),
                    stock.get("ipoDate", ""),
                    stock.get("delistingDate", ""),
                    stock.get("status", ""),
                    _now_iso(),
                ),
            )
        conn.commit()
        logger.info("[TABLE FINISHED COMMIT] - stock_info")
    finally:
        cursor.close()
        conn.close()


def store_time_series_in_db(
    symbol: str,
    time_series_data: Mapping[str, Mapping[str, str]],
    interval: str = "daily",
) -> None:
    if not time_series_data:
        return
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        table_name = f"stock_data_{interval}"
        volume_key = "5. volume" if interval == "hourly" else "6. volume"
        for date, row in time_series_data.items():
            open_p = float(row["1. open"])
            high_p = float(row["2. high"])
            low_p = float(row["3. low"])
            close_p = float(row["4. close"])
            adj_close = float(row.get("5. adjusted close", close_p))
            vol_raw = (
                row.get(volume_key)
                or row.get("6. volume")
                or row.get("5. volume")
                or "0"
            )
            volume = int(str(vol_raw).replace(",", ""))
            cursor.execute(
                f"""
                REPLACE INTO {table_name}
                    (stock_symbol, closing_date, open_price, high_price,
                     low_price, close_price, adj_close_price, volume)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (symbol, date, open_p, high_p, low_p, close_p, adj_close, volume),
            )
        conn.commit()
        logger.info("Stored %s rows in %s", symbol, table_name)
    finally:
        cursor.close()
        conn.close()


def process_all_stocks(delay: float = 0.3) -> None:
    stocks_meta = get_stock_info()
    if stocks_meta:
        store_stocks_in_db(stocks_meta)
    nasdaq_100_symbols = fetch_nasdaq_100()
    intervals = ("daily", "hourly", "monthly")
    for interval in intervals:
        for i, symbol in enumerate(sorted(nasdaq_100_symbols), start=1):
            logger.info("Processing %s (%s /%d)", symbol, interval, i)
            series = get_time_series_for_stock(symbol, interval=interval)
            if series:
                store_time_series_in_db(symbol, series, interval=interval)
                time.sleep(delay)
        logger.info("[TABLE FINISHED COMMIT] - stock_data_%s", interval)
