# -*- coding: utf-8 -*-
import pandas as pd
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover

class Btest(Backtest):
    def _init__(self):
        super().__init__()

"""
Moving Average Convergence ／ Divergence Trading Method
MACD gives weight to the most recent values, and the weight decreases as the data gets older. 
Unlike simple moving averages, it avoids the fact that n-day old data and yesterday's data 
have the same weight, while at the same time n-day old data is not completely dropped.
"""
class MACDCross(Strategy):
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

    @staticmethod
    def calc(close, n1, n2, ns):
        macd = pd.DataFrame()
        macd['close'] = close
        # Exponential Moving Average. short & long
        macd['ema_short'] = macd['close'].ewm(span=n1).mean()
        macd['ema_long'] = macd['close'].ewm(span=n2).mean()
        macd['macd'] = macd['ema_short'] - macd['ema_long']
        macd['macdsignal'] = macd['macd'].ewm(span=ns).mean()
        return macd['macd'], macd['macdsignal']

    def init(self):
        self.macd, self.macdsignal = self.I(self.calc, self.data['Close'], self.n1, self.n2, self.ns)
    
    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal, self.macd):
            self.position.close()