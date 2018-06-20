import unittest
import sssm
import pandas

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
        self.assertEqual(trade_entry["Timestamp"], StockMarketTests.example_trade_entry_1[1])
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







if __name__ == '__main__':
    unittest.main()
