# -*- coding: utf-8 -*-
# Refer to the following sites
# https://info.monex.co.jp/technical-analysis/indicators/
import pandas as pd
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover
import indicator

class Btest(Backtest):
    def _init__(self):
        super().__init__()

class SMACross(Strategy):
    """
    MA(SMA)
    Simple Moving Average Trading Method
    If the moving average is upward, the market is in an uptrend; if it is sideways, 
    the market is in a faltering phase with no sense of direction; 
    and if it is downward, the market is in a downtrend.
    If the price is above the moving average, it is judged to be a strong market, 
    and if it is below, it is judged to be a weak market.
    """
    def __init__(self, broker, data, params, n1=5, n2=25):
        self._indicators = []
        self._broker: _Broker = broker
        self._data: _Data = data
        self._params = self._check_params(params)
        self.__n1 = n1
        self.__n2 = n2

    @property
    def n1(self):
        return self.__n1

    @n1.setter
    def n1(self, value):
        self.__n1 = value

    @property
    def n2(self):
        return self.__n2

    @n2.setter
    def n2(self, value):
        self.__n2 = value
    
    def get(self):
        sma_short = indicator.sma(self.data, self.n1)
        sma_long = indicator.sma(self.data, self.n2)
        return sma_short, sma_long

    def init(self):
        self.short, self.long = self.I(self.get)
    
    def next(self):
        if crossover(self.short, self.long):
            self.buy()
        elif crossover(self.long, self.short):
            self.position.close()


class MACDCross(Strategy):
    """
    MACD
    Moving Average Convergence ／ Divergence Trading Method
    MACD gives weight to the most recent values, and the weight decreases as the data gets older. 
    Unlike simple moving averages, it avoids the fact that n-day old data and yesterday's data 
    have the same weight, while at the same time n-day old data is not completely dropped.
    """
    def __init__(self, broker, data, params, n1=12, n2=26, ns=9):
        self._indicators = []
        self._broker: _Broker = broker
        self._data: _Data = data
        self._params = self._check_params(params)
        self.__n1 = n1
        self.__n2 = n2
        self.__ns = ns

    @property
    def n1(self):
        return self.__n1

    @n1.setter
    def n1(self, value):
        self.__n1 = value

    @property
    def n2(self):
        return self.__n2

    @n2.setter
    def n2(self, value):
        self.__n2 = value

    @property
    def ns(self):
        return self.__ns

    @ns.setter
    def ns(self, value):
        self.__ns = value
    
    def get(self):
        return indicator.macd(data, self.n1, self.n2, self.ns)

    def init(self):
        self.macd, self.macdsignal = self.I(self.get)
    
    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal, self.macd):
            self.position.close()


class BBCross(Strategy):
    """
    BB
    Bollinger Bands
    If the moving average is upward, the market is in an uptrend; if it is sideways, 
    the market is in a faltering phase with no sense of direction; 
    and if it is downward, the market is in a downtrend.
    If the price is above the moving average, it is judged to be a strong market, 
    and if it is below, it is judged to be a weak market.
    """
    def __init__(self, broker, data, params, d=20, upper_sigma=2, lower_sigma=2):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__d = d
        self.__upper_sigma = upper_sigma
        self.__lower_sigma = lower_sigma

    @property
    def d(self):
        return self.__d

    @d.setter
    def d(self, value):
        self.__d = value

    @property
    def upper_sigma(self):
        return self.__upper_sigma

    @upper_sigma.setter
    def upper_sigma(self, value):
        self.__upper_sigma = value
    
    @property
    def lower_sigma(self):
        return self.__lower_sigma

    @lower_sigma.setter
    def sigma(self, value):
        self.__lower_sigma = value
    
    def get(self):
        return indicator.ci(data, self.d, self.upper_sigma, self.lower_sigma)

    def init(self):
        self.upper, self.lower = self.I(self.get)
    
    def next(self):
        if crossover(self.data['Close'], self.lower):
            self.buy()
        elif crossover(self.upper, self.data['Close']):
            self.position.close()

class DMICross(Strategy):
    """
    DMI
    https://info.monex.co.jp/technical-analysis/indicators/015.html
    Directional Movement Index
    The feature of this indicator is to read the strength or weakness of the market by determining whether the high or low of the day is greater 
    than the high or low of the previous day, ignoring the comparison of closing prices, and to analyze the trend based on the volatility of prices.
    """
    def __init__(self, broker, data, params, d=14):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__d = d

    @property
    def d(self):
        return self.__d

    @d.setter
    def d(self, value):
        self.__d = value
    
    def get(self):
        return indicator.di(data, self.d)

    def init(self):
        self.di_p, self.di_m = self.I(self.get)
    
    def next(self):
        if crossover(self.di_p, self.di_m):
            self.buy()
        elif crossover(self.di_m, self.di_p):
            self.position.close()

if __name__ == "__main__":
    from db import LocalDB
    d = LocalDB()
    data = d.loader('AAPL', '2015/01/01')
    # strategy = MACDCross
    strategy = DMICross
    # strategy = BBCross
    # setter
    # strategy.n1 = 100
    # strategy.n2 = 26
    # strategy.ns = 10

    import time
    start = time.time()
    bt = Btest(
        data = data,
        strategy = strategy,
        cash = 1000,
        commission = 0.00495,
        margin = 1.0,
        trade_on_close = True,
        exclusive_orders = True
        )

    output = bt.run()
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    bt.plot()
    print(output)