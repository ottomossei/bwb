# -*- coding: utf-8 -*-
# Refer to the following sites
# https://info.monex.co.jp/technical-analysis/indicators/
import pandas as pd
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover

class Btest(Backtest):
    def _init__(self):
        super().__init__()

"""
MA(SMA)
Simple Moving Average Trading Method
If the moving average is upward, the market is in an uptrend; if it is sideways, 
the market is in a faltering phase with no sense of direction; 
and if it is downward, the market is in a downtrend.
If the price is above the moving average, it is judged to be a strong market, 
and if it is below, it is judged to be a weak market.
"""
class SMACross(Strategy):
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

    @staticmethod
    def calc(close, n1, n2):
        sma = pd.DataFrame()
        sma['close'] = close
        # Simple Moving Average. short, middle, long
        sma['sma_short'] = sma['close'].rolling(window = n1).mean()
        sma['sma_long'] = sma['close'].rolling(window = n2).mean()
        return sma
    
    def get(self, close, n1, n2):
        sma = self.calc(close, n1, n2)
        return sma['sma_short'], sma['sma_long']

    def init(self):
        self.short, self.long = self.I(self.get, self.data['Close'], self.n1, self.n2)
    
    def next(self):
        if crossover(self.short, self.long):
            self.buy()
        elif crossover(self.long, self.short):
            self.position.close()


"""
MACD
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
        return macd
    
    def get(self, close, n1, n2, ns):
        macd = self.calc(close, n1, n2, ns)
        return macd['macd'], macd['macdsignal']

    def init(self):
        self.macd, self.macdsignal = self.I(self.get, self.data['Close'], self.n1, self.n2, self.ns)
    
    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal, self.macd):
            self.position.close()


if __name__ == "__main__":
    from db import LocalDB
    d = LocalDB()
    data = d.loader('AAPL', '2015/01/01')
    strategy = MACDCross
    # setter
    strategy.n1 = 100
    strategy.n2 = 26
    strategy.ns = 10

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
    bt.plot()
    print(output)

    """
    # Calculate only MACD with variables independent of the strategy
    macd = strategy.calc(data['Close'], 12, 26, 9)
    print(macd)
    """