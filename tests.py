import unittest
from unittest.mock import MagicMock

import sssm
import pandas
import time

from sssm import StockCalculator


class TestsDataSource:

    @staticmethod
    def create_dummy_market_with_trades_from_last_10_minutes():
        market = sssm.StockMarket()

        stock = ["AAA", False, 10, 0, 100]
        market.add_stock(*stock)
        stock[0] = "BBB"
        market.add_stock(*stock)

        timestamp_now = int(time.time())

        trade = ["AAA", timestamp_now, 1, 100, 1]
        market.register_trade(*trade)

        trade[1] = timestamp_now - 60
        trade[3] = 200
        market.register_trade(*trade)

        trade[1] = timestamp_now - 600
        trade[3] = 1000
        market.register_trade(*trade)

        trade[0] = "BBB"
        trade[1] = timestamp_now
        market.register_trade(*trade)

        return market



class StockMarketTests(unittest.TestCase):
    example_trade_entry_1 = ("AAA", 11, 1, 1.5, False)
    example_stock_1 = ("AAA", False, 10, 0, 100)
    example_stock_2 = ("BBB", False, 10, 0, 100)

    def test_registering_trade_appends_to_proper_columns(self):
        market = sssm.StockMarket()
        market.register_trade(*StockMarketTests.example_trade_entry_1)
        self.assertEqual(market.trades.shape[0], 1,
                         "There should be only 1 trade entry, found: {0}".format(len(market.trades)))
        trade_entry = market.trades.iloc[0]
        self.assertEqual(trade_entry["Symbol"], StockMarketTests.example_trade_entry_1[0])
        self.assertEqual(trade_entry["UnixTimestamp"], StockMarketTests.example_trade_entry_1[1])
        self.assertEqual(trade_entry["Quantity"], StockMarketTests.example_trade_entry_1[2])
        self.assertEqual(trade_entry["Price"], StockMarketTests.example_trade_entry_1[3])
        self.assertEqual(trade_entry["IsBuy"], StockMarketTests.example_trade_entry_1[4])

    def test_getting_trades_returns_filtered_dataframe(self):
        market = sssm.StockMarket()
        trade = list(StockMarketTests.example_trade_entry_1)

        market.register_trade(*trade)
        trade[0] = "BBB"
        market.register_trade(*trade)
        market.register_trade(*trade)

        result = market.get_trades("BBB")
        self.assertIsInstance(result, pandas.DataFrame)
        self.assertEqual(result.shape[0], 2)
        self.assertEqual(result.iloc[0]["Symbol"], "BBB")

    def test_adding_a_stock_appends_to_proper_columns(self):
        market = sssm.StockMarket()
        market.add_stock(*StockMarketTests.example_stock_1)

        self.assertEqual(market.stocks.shape[0], 1,
                         "There should be only 1 stock entry, found: {0}".format(len(market.stocks)))
        stock_entry = market.stocks.iloc[0]
        self.assertEqual(stock_entry["Symbol"], StockMarketTests.example_stock_1[0])
        self.assertEqual(stock_entry["IsPreferred"], StockMarketTests.example_stock_1[1])
        self.assertEqual(stock_entry["LastDividend"], StockMarketTests.example_stock_1[2])
        self.assertEqual(stock_entry["FixedDividend"], StockMarketTests.example_stock_1[3])
        self.assertEqual(stock_entry["ParValue"], StockMarketTests.example_stock_1[4])

    def test_adding_existing_stock_raises_key_error(self):
        market = sssm.StockMarket()
        market.add_stock(*StockMarketTests.example_stock_1)
        with self.assertRaises(KeyError):
            market.add_stock(*StockMarketTests.example_stock_1)

    def test_getting_stock_returns_proper_pandas_series_row(self):
        market = sssm.StockMarket()
        market.add_stock(*StockMarketTests.example_stock_1)
        market.add_stock(*StockMarketTests.example_stock_2)

        expected_result = list(StockMarketTests.example_stock_1)
        actual_result = market.get_stock(StockMarketTests.example_stock_1[0])
        self.assertIsInstance(actual_result, pandas.Series)
        self.assertListEqual(expected_result, list(actual_result))

    def test_getting_nonexistent_stock_returns_none(self):
        market = sssm.StockMarket()
        with self.assertRaises(KeyError):
            market.get_stock("AAA")


class StockCalculatorTests(unittest.TestCase):
    def test_common_dividend_yield_is_calculated_correctly(self):
        calc = sssm.StockCalculator()
        self.assertEqual(calc._calculate_common_dividend_yield(100, 20), 5)
        self.assertEqual(calc._calculate_common_dividend_yield(5, 2), 2.5)

    def test_preferred_dividend_yield_is_calculated_correctly(self):
        calc = sssm.StockCalculator()
        self.assertEqual(calc._calculate_preferred_dividend_yield(10, 100, 200), 5)
        self.assertEqual(calc._calculate_preferred_dividend_yield(10, 20, 200), 0.2)

    def test_dividend_returns_none_if_stock_symbol_is_incorrect(self):
        market = sssm.StockMarket()
        calc = sssm.StockCalculator(stock_symbol="NOPE", stock_market=market)
        self.assertIsNone(calc.get_dividend_yield(1))

    def test_dividend_raises_error_if_price_is_not_greater_than_zero(self):
        calc = sssm.StockCalculator(stock_symbol="")
        with self.assertRaises(sssm.StockCalculator.ArgumentError):
            calc.get_dividend_yield(0)

        with self.assertRaises(sssm.StockCalculator.ArgumentError):
            calc.get_dividend_yield(-1)

    def test_pe_ratio_is_calculated_correctly(self):
        calc = sssm.StockCalculator()
        dividend_mock = MagicMock(return_value=2)
        calc.get_dividend_yield = dividend_mock

        self.assertEqual(calc.get_pe_ratio(100), 50)
        calc.get_dividend_yield.assert_called_once()

        self.assertEqual(calc.get_pe_ratio(100, 20), 5)
        calc.get_dividend_yield.assert_called_once()

    def test_volume_weighted_stock_price_is_calculated_correctly(self):
        market = TestsDataSource.create_dummy_market_with_trades_from_last_10_minutes()

        calc = sssm.StockCalculator("AAA", market)
        result = calc.get_volume_weighted_stock_price(time_frame_minutes=5)
        expected = 150
        self.assertEqual(result, expected, "Volume weighted stock price is incorrect")

    def test_volume_weighted_stock_price_returns_zero_if_no_trades_were_made(self):
        market = sssm.StockMarket()
        calc = sssm.StockCalculator("AAA", market)
        self.assertEqual(calc.get_volume_weighted_stock_price(), 0)


class MarketCalculatorTests(unittest.TestCase):
    def test_all_share_index_is_calculated_correctly(self):
        market = TestsDataSource.create_dummy_market_with_trades_from_last_10_minutes()
        market_calc = sssm.MarketCalculator(market)
        expected = 387.2983346207417
        self.assertEqual(market_calc.get_all_share_index(), expected)


if __name__ == '__main__':
    unittest.main()
