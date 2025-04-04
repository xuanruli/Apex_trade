import unittest
import pandas as pd
from app.services.chart import create_candlestick_chart, create_bar_chart, create_line_chart, convert_dict_to_df
import plotly.graph_objs as go

class TestCharts(unittest.TestCase):
    def setUp(self):
        # Create a simple date range and dummy OHLC and volume data for tests.
        self.dates = pd.date_range(start="2020-01-01", periods=10, freq='D')
        self.data = {
            'open': pd.Series([100 + i for i in range(10)], index=self.dates),
            'high': pd.Series([105 + i for i in range(10)], index=self.dates),
            'low': pd.Series([95 + i for i in range(10)], index=self.dates),
            'close': pd.Series([102 + i for i in range(10)], index=self.dates),
            'volume': pd.Series([100000 + i * 1000 for i in range(10)], index=self.dates)
        }
        self.df = pd.DataFrame(self.data)
        self.symbol = "TEST"

    def test_create_candlestick_chart(self):
        fig = create_candlestick_chart(self.df, self.symbol)
        # Verify that a Plotly figure is returned.
        self.assertIsInstance(fig, go.Figure)
        # Check that the chart title and axis labels are as expected.
        self.assertEqual(fig.layout.title.text, f'{self.symbol} Candlestick Chart')
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'Price')
        # Ensure that the trace type is candlestick.
        self.assertEqual(fig.data[0].to_plotly_json()['type'], 'candlestick')

    def test_create_bar_chart_with_string_volume(self):
        # Create a DataFrame with 'volume' as strings containing commas.
        df_str = self.df.copy()
        df_str['volume'] = df_str['volume'].apply(lambda x: f"{x:,}")
        fig = create_bar_chart(df_str, self.symbol)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(fig.layout.title.text, f'{self.symbol} Trading Volume')
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'volume')
        # Check that the trace type is bar.
        self.assertEqual(fig.data[0].to_plotly_json()['type'], 'bar')

    def test_create_bar_chart_with_numeric_volume(self):
        # Use the numeric volume directly.
        fig = create_bar_chart(self.df, self.symbol)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(fig.layout.title.text, f'{self.symbol} Trading Volume')
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'volume')
        self.assertEqual(fig.data[0].to_plotly_json()['type'], 'bar')

    def test_create_line_chart(self):
        # Prepare a DataFrame with just the 'close' prices.
        df_line = self.df[['close']].copy()
        # Use a short period to force RSI computation over fewer rows.
        fig = create_line_chart(df_line, self.symbol, period=3)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(fig.layout.title.text, f'{self.symbol} Relative Strength Index (RSI)')
        self.assertEqual(fig.layout.xaxis.title.text, 'Date')
        self.assertEqual(fig.layout.yaxis.title.text, 'RSI')
        # Ensure that the trace is a scatter trace with lines.
        trace = fig.data[0]
        self.assertEqual(trace.to_plotly_json()['type'], 'scatter')
        self.assertEqual(trace.to_plotly_json()['mode'], 'lines')
        # Confirm that the function has added the RSI column to the DataFrame.
        self.assertIn('RSI', df_line.columns)

    def test_convert_dict_to_df(self):
        # Create sample input data matching the expected dictionary format.
        data = {
            "2020-01-01": [100, 110, 90, 105, 105, 1000000, 0.0, 1.0],
            "2020-01-02": [105, 115, 95, 110, 110, 1200000, 0.0, 1.0]
        }
        df_converted = convert_dict_to_df(data)
        # Verify that the index is converted to datetime.
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_converted.index))
        # Check that only the expected columns remain.
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        self.assertListEqual(list(df_converted.columns), expected_columns)
        # Verify some values.
        self.assertEqual(df_converted.loc[pd.Timestamp("2020-01-01"), 'open'], 100)
        self.assertEqual(df_converted.loc[pd.Timestamp("2020-01-02"), 'close'], 110)
        self.assertEqual(df_converted.loc[pd.Timestamp("2020-01-01"), 'volume'], 1000000)

if __name__ == '__main__':
    unittest.main()
