# -*- coding: utf-8 -*-
# Refer to the following sites
from datetime import date
import backtesting
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover
import indicator

class Btest(Backtest):
    def _init__(self):
        super().__init__()
    
    def plot(self, issue, results: pd.Series = None, filename=None, plot_width=None,
             plot_equity=True, plot_return=True, plot_pl=True,
             plot_volume=True, plot_drawdown=True,
             smooth_equity=False, relative_equity=True,
             superimpose = True,
             resample=True, reverse_indicators=False,
             show_legend=True, open_browser=False):
             backtesting._plotting.plot(
                results=self._results,
                df=self._data,
                indicators=self._results._strategy._indicators,
                filename='./LocalDB/' + issue + '/BestStrategy',
                plot_width=plot_width,
                plot_equity=plot_equity,
                plot_return=plot_return,
                plot_pl=plot_pl,
                plot_volume=plot_volume,
                plot_drawdown=plot_drawdown,
                smooth_equity=smooth_equity,
                relative_equity=relative_equity,
                superimpose=superimpose,
                resample=resample,
                reverse_indicators=reverse_indicators,
                show_legend=show_legend,
                open_browser=open_browser)
    

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
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__n1 = n1
        self.__n2 = n2
    
    def base_params():
        return {
            'n1':np.array([5, 25, 75, 100, 200]),
            'n2':np.array([5, 25, 75, 100, 200])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

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
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__n1 = n1
        self.__n2 = n2
        self.__ns = ns
    
    def base_params():
        return {
            'n1':np.array([6, 12, 18]),
            'n2':np.array([13, 26, 39]),
            'ns':np.array([5, 9, 15]),
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

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
        return indicator.macd(self.candle, self.n1, self.n2, self.ns)

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

    def base_params():
        return {
            'd':np.array([9, 10, 20, 21, 50, 75, 100]),
            'upper_sigma':np.array([1, 2, 3]),
            'lower_sigma':np.array([1, 2, 3]),
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

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
        return indicator.ci(self.candle, self.d, self.upper_sigma, self.lower_sigma)

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
    Stop And Reverse Point
    Parabolic is a technical indicator that displays a parabolic line at the top or bottom of a chart, 
    and is mainly useful when looking for trend turning points in the market.
    """
    def __init__(self, broker, data, params, d=14):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__d = d
    
    def base_params():
        return {
            'd':np.array([7, 14, 21, 28, 35])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def d(self):
        return self.__d

    @d.setter
    def d(self, value):
        self.__d = value
    
    def get(self):
        return indicator.di(self.candle, self.d)

    def init(self):
        self.di_p, self.di_m = self.I(self.get)
    
    def next(self):
        if crossover(self.di_p, self.di_m):
            self.buy()
        elif crossover(self.di_m, self.di_p):
            self.position.close()


class SARCross(Strategy):
    """
    SAR
    https://info.monex.co.jp/technical-analysis/indicators/021.html
    Directional Movement Index
    The feature of this indicator is to read the strength or weakness of the market by determining whether the high or low of the day is greater 
    than the high or low of the previous day, ignoring the comparison of closing prices, and to analyze the trend based on the volatility of prices.
    """
    def __init__(self, broker, data, params, af=0.02, maxaf=0.2):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__init_af = af
        self.__maxaf = maxaf
    
    def base_params():
        return {
            'af':np.array([0.01, 0.02, 0.05, 0.1]),
            'maxaf':np.array([0.1, 0.15, 0.2, 0.25])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def init_af(self):
        return self.__init_af

    @init_af.setter
    def init_af(self, value):
        self.__init_af = value

    @property
    def maxaf(self):
        return self.__maxaf

    @maxaf.setter
    def maxaf(self, value):
        self.__maxaf = value

    def get(self):
        return indicator.sar(self.candle, self.init_af, self.maxaf)

    def init(self):
        self.sar, _, __ = self.I(self.get)
        
    def next(self):
        if crossover(self.data['Close'], self.sar):
            self.buy()
        elif crossover(self.sar, self.data['Close']):
            self.position.close()


class RSICross(Strategy):
    """
    RSI
    https://info.monex.co.jp/technical-analysis/indicators/005.html
    Relative Strength Index
    An indicator to determine how much the exchange rate has increased relative to the overall change in the exchange rate.
    """
    def __init__(self, broker, data, params, d=14, buy_ratio=30, sell_ratio=80):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__d = d
        self.__buy_ratio = buy_ratio
        self.__sell_ratio = sell_ratio
    
    def base_params():
        return {
            'd':np.array([9, 14, 22, 42, 52]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def d(self):
        return self.__d

    @d.setter
    def d(self, value):
        self.__d = value

    @property
    def buy_ratio(self):
        return self.__buy_ratio

    @buy_ratio.setter
    def buy_ratio(self, value):
        self.__buy_ratio = value
    
    @property
    def sell_ratio(self):
        return self.__sell_ratio

    @sell_ratio.setter
    def sell_ratio(self, value):
        self.__sell_ratio = value

    def get(self):
        return indicator.rsi(self.candle, self.d)

    def init(self):
        self.rsi = self.I(self.get)
    
    def next(self):
        if crossover(self.buy_ratio, self.rsi):
            self.buy()
        elif crossover(self.rsi, self.sell_ratio):
            self.position.close()


class StochasticsCross(Strategy):
    """
    Stochastics
    https://info.monex.co.jp/technical-analysis/indicators/006.html
    Relative Strength Index
    Like RSI, it is an analytical method for determining overbought and oversold market conditions.
    """
    def __init__(self, broker, data, params, maxmin_span=9, k_span=3, buy_ratio=20, sell_ratio=80):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__maxmin_span = maxmin_span
        self.__k_span = k_span
        self.__buy_ratio = buy_ratio
        self.__sell_ratio = sell_ratio
    
    def base_params():
        return {
            'maxmin_span':np.array([5, 9, 14, 21, 30]),
            'k_span':np.array([2, 3, 4, 5]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def maxmin_span(self):
        return self.__maxmin_span

    @maxmin_span.setter
    def maxmin_span(self, value):
        self.__maxmin_span = value
    
    @property
    def k_span(self):
        return self.__k_span

    @k_span.setter
    def k_span(self, value):
        self.__k_span = value
    
    @property
    def buy_ratio(self):
        return self.__buy_ratio

    @buy_ratio.setter
    def buy_ratio(self, value):
        self.__buy_ratio = value
    
    @property
    def sell_ratio(self):
        return self.__sell_ratio

    @sell_ratio.setter
    def sell_ratio(self, value):
        self.__sell_ratio = value

    def get(self):
        return indicator.slow_s(self.candle, self.maxmin_span, self.k_span)

    def init(self):
        self.slow_per_k, self.slow_per_d = self.I(self.get)
    
    def next(self):
        if (crossover(self.buy_ratio, self.slow_per_d) and (crossover(self.slow_per_k, self.slow_per_d))):
            self.buy()
        elif (crossover(self.slow_per_d, self.sell_ratio) and (crossover(self.slow_per_d, self.slow_per_k))):
            self.position.close()


class PsychologicalCross(Strategy):
    """
    Psychological line
    https://info.monex.co.jp/technical-analysis/indicators/007.html
    The psychological line is an indicator that quantifies the "psychology of investors," and its calculation formula is simple and easy to understand.
    It is mainly effective in determining the strength and weakness of the market, and determining where to buy and sell.
    """
    def __init__(self, broker, data, params, span=12, buy_ratio=25, sell_ratio=75):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__span = span
        self.__buy_ratio = buy_ratio
        self.__sell_ratio = sell_ratio
    
    def base_params():
        return {
            'span':np.array([5, 12, 19]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }
    
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def span(self):
        return self.__span

    @span.setter
    def span(self, value):
        self.__span = value

    @property
    def buy_ratio(self):
        return self.__buy_ratio

    @buy_ratio.setter
    def buy_ratio(self, value):
        self.__buy_ratio = value
    
    @property
    def sell_ratio(self):
        return self.__sell_ratio

    @sell_ratio.setter
    def sell_ratio(self, value):
        self.__sell_ratio = value
    
    def get(self):
        return indicator.psyco(self.candle, self.span)

    def init(self):
        self.psyco = self.I(self.get)
    
    def next(self):
        if 25 > self.psyco:
            self.buy()
        elif self.psyco > 75:
            self.position.close()


class RCICross(Strategy):
    """
    RCI
    https://info.monex.co.jp/technical-analysis/indicators/017.html
    Rank Correlation Index
    RCI is one of the indicators that quantify the psychology of investors to time their trades.
    It ranks the date and price respectively, and focuses on how much correlation there is between each.
    """
    def __init__(self, broker, data, params, span=9, buy_ratio=-100, sell_ratio=100):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__span = span
        self.__buy_ratio = buy_ratio
        self.__sell_ratio = sell_ratio
    
    def base_params():
        return {
            'span':np.array([7, 8, 9, 21, 23, 26, 42, 45, 48, 52]),
            'buy_ratio':np.array([-100, -90, -80, -70]),
            'sell_ratio':np.array([70, 80, 90, 100])
            }

    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def span(self):
        return self.__span

    @span.setter
    def span(self, value):
        self.__span = value

    @property
    def buy_ratio(self):
        return self.__buy_ratio

    @buy_ratio.setter
    def buy_ratio(self, value):
        self.__buy_ratio = value
    
    @property
    def sell_ratio(self):
        return self.__sell_ratio

    @sell_ratio.setter
    def sell_ratio(self, value):
        self.__sell_ratio = value

    def get(self):
        return indicator.rci(self.candle, self.span)

    def init(self):
        self.rci = self.I(self.get)
    
    def next(self):
        if crossover(self.buy_ratio, self.rci):
            self.buy()
        elif crossover(self.rci, self.sell_ratio):
            self.position.close()


class MAERCross(Strategy):
    """
    MAER
    https://info.monex.co.jp/technical-analysis/indicators/019.html
    Moving Average Estrangement Rate
    MAER is the percentage of the current price that is away from the moving average.
    """
    def __init__(self, broker, data, params, span=25, buy_ratio=-8, sell_ratio=5):
        self._indicators = []
        self._broker = broker
        self._data = data
        self._params = self._check_params(params)
        self.__span = span
        self.__buy_ratio = buy_ratio
        self.__sell_ratio = sell_ratio
    
    def base_params():
        return {
            'span':np.array([5, 25, 75, 100, 200]),
            'buy_ratio':np.array([-5, -6, -7, -8, -9, -10]),
            'sell_ratio':np.array([5, 6, 7, 8, 9, 10])
            }

    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def span(self):
        return self.__span

    @span.setter
    def span(self, value):
        self.__span = value

    @property
    def buy_ratio(self):
        return self.__buy_ratio

    @buy_ratio.setter
    def buy_ratio(self, value):
        self.__buy_ratio = value
    
    @property
    def sell_ratio(self):
        return self.__sell_ratio

    @sell_ratio.setter
    def sell_ratio(self, value):
        self.__sell_ratio = value

    def get(self):
        return indicator.maer(self.candle, self.span)

    def init(self):
        self.maer = self.I(self.get)
    
    def next(self):
        if crossover(self.buy_ratio, self.maer):
            self.buy()
        elif crossover(self.maer, self.sell_ratio):
            self.position.close()