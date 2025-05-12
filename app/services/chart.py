import pandas as pd
import plotly.graph_objs as go
from app.services.alpha_vantage import get_time_series_for_stock, get_news, get_global_quote, get_overview
from plotly.io import to_html
from datetime import timedelta, datetime
from flask import session, request

def create_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create a candlestick chart using OHLC data.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing 'Open', 'High', 'Low', 'Close' columns.
    symbol (str): Stock symbol.

    Returns:
    fig (plotly.graph_objs._figure.Figure): Plotly figure object.
    """
    # create ohlc fig
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])
    fig.update_layout(title=f'{symbol.upper()} Candlestick Chart', xaxis_title='Date', yaxis_title='Price')

    # gridlines
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray',
        rangebreaks=[
            dict(bounds=["sat", "mon"])
        ]
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    return fig

def create_bar_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create a bar chart for trading volume.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing 'Volume' column.
    symbol (str): Stock symbol.

    Returns:
    fig (plotly.graph_objs._figure.Figure): Plotly figure object.
    """
    # convert to float
    if df['volume'].dtype == 'object':
        df['volume'] = df['volume'].str.replace(',', '').astype(float)

    # create figure
    fig = go.Figure(data=[go.Bar(x=df.index, y=df['volume'])])
    fig.update_layout(title=f'{symbol.upper()} Trading Volume', xaxis_title='Date', yaxis_title='volume')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig

def create_line_chart(df, symbol: str, period: int = 14):
    """
    Calculate RSI (Relative Strength Index) and create a line chart.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'Close' price column.
    symbol (str): Symbol of the financial asset.
    period (int): Period to calculate RSI.

    Returns:
    fig (plotly.graph_objs._figure.Figure): Plotly figure object.
    """
    # convert to float
    df['close'] = df['close'].astype(float)

    # calculate rsi
    delta = df['close'].diff(1)
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # line fig
    fig = go.Figure(data=[go.Scatter(x=df.index, y=df['RSI'], mode='lines')])

    # labels
    fig.update_layout(title=f'{symbol.upper()} Relative Strength Index (RSI)', xaxis_title='Date', yaxis_title='RSI')

    # gridlines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig

def convert_dict_to_df(data: dict) -> pd.DataFrame:
    """convert dict from get_time_series_for_stock to DataFrame compatible with chart functions.

    Args:
        data (dict): input dict from get_time_series_for_stock

    Returns:
        pd.DataFrame: converted DataFrame
    """
    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = ['open', 'high', 'low', 'close', 'adjusted close', 'volume', 'dividend amount', 'split coefficient']
    df.index = pd.to_datetime(df.index)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df

def load_asset_page():
    symbol = request.args.get('symbol') or session.get('symbol', "AAPL")
    session['symbol'] = symbol

    news = get_news(symbol=symbol)
    global_quote = get_global_quote(symbol=symbol)
    overview = get_overview(symbol=symbol)

    stock = {
        'Name': overview['Name'],
        'Symbol': overview['Symbol'],
        'Exchange': overview['Exchange'],
        'Price': global_quote['05. price'],
        'WeekHigh': overview['52WeekHigh'],
        'WeekLow': overview['52WeekLow'],
        'Sector': overview['Sector'],
        'Industry': overview['Industry'],
        'MarketCap': overview['MarketCapitalization'],
        'PERatio': overview['PERatio'],
        'EPS': overview['EPS'],
        'Dividend': overview['DividendPerShare'],
        'DividendYield': overview['DividendYield']
    }

    titles, urls = [], []
    for i in range(3):
        titles.append(news['feed'][i]['title'])
        urls.append(news['feed'][i]['url'])

    # Get time series data and create charts
    data = get_time_series_for_stock(symbol)
    df = convert_dict_to_df(data)

    five_years_ago = (datetime.now() - timedelta(days=365 * 5)).date()
    default_start = five_years_ago.isoformat()
    default_end = df.index[0].date().isoformat()

    start_date = request.args.get('start_date') or session.get('start_date', default_start)
    end_date = request.args.get('end_date') or session.get('end_date', default_end)

    session['start_date'] = start_date
    session['end_date'] = end_date

    if start_date and end_date:
        try:
            df = df[(df.index >= start_date) & (df.index <= end_date)]
        except Exception as e:
            print(f"Error filtering by date: {e}")

    # Create charts and convert them to HTML
    candlestick_chart = to_html(create_candlestick_chart(df, symbol), full_html=False)
    line_chart = to_html(create_line_chart(df, symbol), full_html=False)
    bar_chart = to_html(create_bar_chart(df, symbol), full_html=False)

    return stock, candlestick_chart, line_chart, bar_chart, titles, urls, start_date, end_date
