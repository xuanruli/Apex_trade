import requests
import os
from dotenv import load_dotenv
load_dotenv()

app_root = os.path.dirname(os.path.dirname(__file__))
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'
DB_PATH = os.path.join(app_root, 'db/apex_data.db')

def get_company_overview(symbol):
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()

def get_global_quote(symbol):
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()['Global Quote']
    return data

def get_news(symbol):
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'limit': 5
    }
    response = requests.get(BASE_URL, params=params).json()
    if "feed" in response:
        response["feed"] = response["feed"]
    return response


def get_stock_history():
    """get all stock data with alpha vantage API Listing Status, store with list(dict), not limited to nasdaq 100"""
    params = {
        'function': 'LISTING_STATUS',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(f"{BASE_URL}", params=params)
        if response.status_code == 200:
            # parse csv file
            lines = response.text.strip().split('\n')
            headers = lines[0].split(',')

            stocks = []
            for i in range(1, len(lines)):
                values = lines[i].split(',')
                stock = dict(zip(headers, values))
                stocks.append(stock)

            return stocks
        else:
            print(f"API request status fail")
            return []
    except Exception as e:
        print(f"API request fail: {str(e)}")
        return []

def get_time_series_for_stock(symbol, interval="daily"):
    """get time series, based on interval to determine it's daily, hourly or monthly data, add weekly if necessary"""
    function_map = {
        "daily": "TIME_SERIES_DAILY_ADJUSTED",
        "hourly": "TIME_SERIES_INTRADAY",
        "monthly": "TIME_SERIES_MONTHLY_ADJUSTED"
    }
    if interval not in function_map:
        raise ValueError("interval has to be 'daily', or 'monthly'")

    params = {
        'function': function_map[interval],
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'full'
    }
    if interval == "hourly":
        params['interval'] = "60min"

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        key_map = {
            "daily": "Time Series (Daily)",
            "hourly": "Time Series (60min)",
            "monthly": "Monthly Adjusted Time Series"
        }

        if key_map[interval] in data:
            time_series = data[key_map[interval]]

            from datetime import datetime
            filtered_time_series = {}
            for date_str, values in time_series.items():
                date_format = "%Y-%m-%d" if interval != "hourly" else "%Y-%m-%d %H:%M:%S"
                date_obj = datetime.strptime(date_str, date_format)
                if date_obj.weekday() < 5:
                    filtered_time_series[date_str] = values

            dates = sorted(filtered_time_series.keys(), reverse=True)
            sorted_time_series = {date: filtered_time_series[date] for date in dates}
            return sorted_time_series
        else:
            print(f"error: {data}")
            return None
    except Exception as e:
        print(f"fetching {symbol} data error: {str(e)}")
        return None

def get_stock_info():
    """get all stock data with alpha vantage API Listing Status, store with list(dict), not limited to nasdaq 100"""
    params = {
        'function': 'LISTING_STATUS',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    try:
        response = requests.get(f"{BASE_URL}", params=params)
        if response.status_code == 200:
            # parse csv file
            lines = response.text.strip().split('\n')
            headers = lines[0].split(',')

            stocks = []
            for i in range(1, len(lines)):
                values = lines[i].split(',')
                stock = dict(zip(headers, values))
                stocks.append(stock)

            return stocks
        else:
            print(f"API request status fail")
            return []
    except Exception as e:
        print(f"API request fail: {str(e)}")
        return []


def get_rsi(symbol, interval="daily", time_period=14, series_type="close"):
    # untested, return: dict
    params = {
        "function": "RSI",
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "Technical Analysis: RSI" in data:
            return {date: float(values["RSI"]) for date, values in data["Technical Analysis: RSI"].items()}
        else:
            print(f"error: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def get_stock_quote(symbol):
    """
    get realtime quote
    untested, return : dict
    """
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "Global Quote" in data:
            return {
                "symbol": data["Global Quote"].get("01. symbol"),
                "open": float(data["Global Quote"].get("02. open", 0)),
                "high": float(data["Global Quote"].get("03. high", 0)),
                "low": float(data["Global Quote"].get("04. low", 0)),
                "price": float(data["Global Quote"].get("05. price", 0)),
                "volume": int(data["Global Quote"].get("06. volume", 0)),
                "latest_trading_day": data["Global Quote"].get("07. latest trading day"),
                "previous_close": float(data["Global Quote"].get("08. previous close", 0)),
                "change": float(data["Global Quote"].get("09. change", 0)),
                "change_percent": data["Global Quote"].get("10. change percent")
            }
        else:
            print(f"Error: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def get_overview(symbol: str):
    """
    Get company overview from Alpha Vantage API.
    Args:
        symbol (str): The stock symbol of the company.
    Returns:
        dict: A dictionary containing the company overview data.
    """
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()