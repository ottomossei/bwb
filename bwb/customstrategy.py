import backtesting
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

try:
    from . import indicator
    from .basicstrategy import Btest
except:
    import indicator
    from basicstrategy import Btest





def base_params():
    """
    ▼ macd()
    概要：
        MACDの計算で、MACDとMACDシグナルを出力する。
    引数：
        day_short(int:12)   短期EMA計算の期間
        day_long(int:26)    長期EMA計算の期間
        span(int:9)         MACDシグナルの計算期間
    """
    return {
        'macd':{
            'day_short':12,
            'day_long':26,
            'span':9,
            }
        }

class CustomStrategy(Strategy):
    """
    """
    def __init__(self, broker, data, params, custom_params={}):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.today = 0
        if custom_params == {}:
            self.__custom_params = base_params()
        else:
            self.custom_params = custom_params
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def custom_params(self):
        return self.__custom_params

    @custom_params.setter
    def custom_params(self, value):
        self.__custom_params = value

    def next(self):
        self.today += 1