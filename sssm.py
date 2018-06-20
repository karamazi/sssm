import pandas as pd
import time
import numpy as np

class StockMarket:
    def __init__(self):
        self.stocks = pd.DataFrame(columns=["Symbol", "IsPreferred", "LastDividend", "FixedDividend", "ParValue"])
        self.trades = pd.DataFrame(columns=["Symbol", "UnixTimestamp", "Quantity", "Price", "IsBuy"])

    def get_stock(self, stock_symbol):
        for _, stock in self.stocks.iterrows():
            if stock["Symbol"] == stock_symbol:
                return stock
        raise KeyError("Stock symbol not found in data")

    def add_stock(self, symbol, is_preferred, last_dividend, fixed_dividend, par_value):
        for s in self.stocks.Symbol:
            if s == symbol:
                raise KeyError("Stock already entered")
        self.stocks.loc[len(self.stocks)] = [symbol, is_preferred, last_dividend, fixed_dividend, par_value]

    def register_trade(self, stock_symbol, timestamp, quantity, price, is_buy):
        self.trades.loc[len(self.trades)] = [stock_symbol, timestamp, quantity, price, is_buy]

    def get_trades(self, stock_symbol):
        return self.trades[self.trades.Symbol == stock_symbol]


class StockCalculator:

    class ArgumentError(Exception):
        pass

    def __init__(self, stock_symbol=None, stock_market=None):
        self.stockSymbol = stock_symbol
        self.stockMarket = stock_market

    def get_dividend_yield(self, price):
        if price <= 0:
            raise StockCalculator.ArgumentError("Price has to be greater than 0")

        try:
            stock = self.stockMarket.get_stock(self.stockSymbol)
        except KeyError:
            return None

        if stock["IsPreferred"]:
            return self._calculate_common_dividend_yield(stock["LastDividend"], price)
        return

    def _calculate_common_dividend_yield(self, last_dividend, price):
        return float(last_dividend)/price

    def _calculate_preferred_dividend_yield(self, fixed_dividend, par_value, price):
        return (fixed_dividend * par_value)/100 * par_value/price

    def get_pe_ratio(self, price, dividend=None):
        if not dividend:
            dividend = self.get_dividend_yield(price)
        return price/dividend

    def get_volume_weighted_stock_price(self, time_frame_minutes=5):
        trades = self.stockMarket.get_trades(self.stockSymbol)
        time_start = int(time.time()) - time_frame_minutes * 60
        last_trades = trades[trades.UnixTimestamp > time_start]

        total_volume = 0
        weight = 0

        for _, trade in last_trades.iterrows():
            total_volume += trade["Quantity"] * trade["Price"]
            weight += trade["Quantity"]

        if weight == 0:
            return 0

        return total_volume/weight


class MarketCalculator:
    def __init__(self, market):
        self.market = market

    def get_all_share_index(self, time_frame_minutes=5):
        volume_weighted_stock_prices = []
        stock_calculator = StockCalculator(stock_market=self.market, stock_symbol="")
        for _, stock in self.market.stocks.iterrows():
            stock_calculator.stockSymbol = stock["Symbol"]
            vwsp = stock_calculator.get_volume_weighted_stock_price(time_frame_minutes)
            volume_weighted_stock_prices.append(vwsp)

        return self._calculate_geometric_mean(volume_weighted_stock_prices)

    def _calculate_geometric_mean(self, array):
        np_array = np.array(array)
        return np_array.prod() ** (1.0/len(np_array))

