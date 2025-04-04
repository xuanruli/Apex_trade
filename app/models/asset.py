import pandas as pd
from app.services.alpha_vantage import get_time_series_for_stock

class Asset:
    def __init__(self, symbol: str, name: str):
        """
        Initializes a new Asset instance.
        Args:
            symbol (str): The ticker symbol of the asset (e.g., 'AAPL' for Apple Inc.).
            name (str): The full name of the asset (e.g., 'Apple Inc.').
        """

        self.symbol = symbol
        self.name = name

    def get_current_price(self):
        """
        Retrieves the current price of the asset.
        This method fetches the time series data for the stock associated with the asset's symbol,
        converts the data into a DataFrame, and returns the most recent closing price.
        Returns:
            float: The most recent closing price of the asset.
        Raises:
            Exception: If there is an issue fetching or processing the time series data.
        """

        data = get_time_series_for_stock(symbol=self.symbol)
        df = self.convert_to_df(data)
        return df.iloc[-1]['close']

    def get_historical_data(self, start_date: str, end_date: str):
        """
        Retrieves historical stock data for the asset within the specified date range.
        Args:
            start_date (str): The start date for the historical data in 'YYYY-MM-DD' format.
            end_date (str): The end date for the historical data in 'YYYY-MM-DD' format.
        Returns:
            pandas.DataFrame: A DataFrame containing the historical stock data filtered by the specified date range.
                              The DataFrame is indexed by date and contains relevant stock data for the asset.
        Raises:
            KeyError: If the specified date range is not found in the data.
            ValueError: If the date format is invalid or the date range is incorrect.
        """
        
        data = get_time_series_for_stock(symbol=self.symbol)
        df = self.convert_to_df(data)
        filtered_df = df.loc[start_date:end_date]
        return filtered_df

    def convert_to_df(self, data: dict):
        """
        Converts a dictionary of financial data into a pandas DataFrame.
        Args:
            data (dict): A dictionary where keys are date strings and values are lists 
                         containing financial data in the following order:
                         ['open', 'high', 'low', 'close', 'adjusted close', 'volume', 
                         'dividend amount', 'split coefficient'].
        Returns:
            pandas.DataFrame: A DataFrame containing the financial data with columns 
                              ['open', 'high', 'low', 'close', 'volume'] and the index 
                              converted to datetime objects.
        """

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = ['open', 'high', 'low', 'close', 'adjusted close', 'volume', 'dividend amount', 'split coefficient']
        df.index = pd.to_datetime(df.index)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.sort_index()
        return df