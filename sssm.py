import pandas as pd


class StockMarket:
    def __init__(self):
        self.stocks = pd.DataFrame(columns=["Symbol", "IsPreferred", "LastDividend", "FixedDividend", "ParValue"])
        self.trades = pd.DataFrame(columns=["Symbol", "Timestamp", "Quantity", "Price", "IsBuy"])

    def get_stock(self, stock_symbol):
        for _, stock in self.stocks.iterrows():
            if stock["Symbol"] == stock_symbol:
                return stock

    def add_stock(self, symbol, is_preferred, last_dividend, fixed_dividend, par_value):
        for s in self.stocks.Symbol:
            if s == symbol:
                raise KeyError("Stock already entered")
        self.stocks.loc[len(self.stocks)] = [symbol, is_preferred, last_dividend, fixed_dividend, par_value]

    def register_trade(self, stock_symbol, timestamp, quantity, price, is_buy):
        self.trades.loc[len(self.trades)] = [stock_symbol, timestamp, quantity, price, is_buy]


class StockCalculator:
    def __init__(self, stock_symbol, stock_market):
        self.stockSymbol = stock_symbol
        self.stockMarket = stock_market

    def get_dividend_yield(self, price):
        pass

    def get_pe_ratio(self, price):
        pass

    def get_volume_weighted_stock_price(self, time_frame_minutes=5):
        pass





