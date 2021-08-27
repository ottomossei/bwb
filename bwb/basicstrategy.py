# -*- coding: utf-8 -*-
# Refer to the following sites
from datetime import date
import backtesting
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover

try:
    from . import indicator
except:
    import indicator

class ObjectStrategy(Strategy):
    @property
    def candle(self):
        return self.__candle

    @candle.setter
    def candle(self, value):
        self.__candle = value

    @property
    def indicator_params(self):
        return self.__indicator_params

    @indicator_params.setter
    def indicator_params(self, value):
        self.__indicator_params = value


class Btest(Backtest):
    def __init__(self, strategy, cash = 1000, commission = 0.00495, margin = 1.0, trade_on_close = True, exclusive_orders = True):
        data = strategy.candle
        super().__init__(data=data, strategy=strategy, cash=cash, commission=commission, margin=margin, trade_on_close=trade_on_close, exclusive_orders=exclusive_orders)
        
    def htmlsaver(self, path, results: pd.Series = None, filename=None, plot_width=None,
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
                filename=path,
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


class SMACross(ObjectStrategy):
    """
    MA(SMA)
    Simple Moving Average Trading Method
    If the moving average is upward, the market is in an uptrend; if it is sideways, 
    the market is in a faltering phase with no sense of direction; 
    and if it is downward, the market is in a downtrend.
    If the price is above the moving average, it is judged to be a strong market, 
    and if it is below, it is judged to be a weak market.
    """
    def base_indicator_params():
        return {
            'n1':np.array([5, 25, 75, 100, 200]),
            'n2':np.array([5, 25, 75, 100, 200])
            }
    
    def get(self):
        sma_short = indicator.sma(self.data, self.indicator_params['n1'])
        sma_long = indicator.sma(self.data, self.indicator_params['n2'])
        return sma_short, sma_long

    def init(self):
        self.short, self.long = self.I(self.get)
    
    def next(self):
        if crossover(self.short, self.long):
            self.buy()
        elif crossover(self.long, self.short):
            self.position.close()


class MACDCross(ObjectStrategy):
    """
    MACD
    Moving Average Convergence ／ Divergence Trading Method
    MACD gives weight to the most recent values, and the weight decreases as the data gets older. 
    Unlike simple moving averages, it avoids the fact that n-day old data and yesterday's data 
    have the same weight, while at the same time n-day old data is not completely dropped.
    """
    def base_indicator_params():
        return {
            'n1':np.array([6, 12, 18]),
            'n2':np.array([13, 26, 39]),
            'ns':np.array([5, 9, 15]),
            }
    
    def get(self):
        return indicator.macd(self.candle, self.indicator_params['n1'], self.indicator_params['n2'], self.indicator_params['ns'])

    def init(self):
        self.macd, self.macdsignal = self.I(self.get)
    
    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal, self.macd):
            self.position.close()


class BBCross(ObjectStrategy):
    """
    BB
    Bollinger Bands
    If the moving average is upward, the market is in an uptrend; if it is sideways, 
    the market is in a faltering phase with no sense of direction; 
    and if it is downward, the market is in a downtrend.
    If the price is above the moving average, it is judged to be a strong market, 
    and if it is below, it is judged to be a weak market.
    """
    def base_indicator_params():
        return {
            'd':np.array([9, 10, 20, 21, 50, 75, 100]),
            'upper_sigma':np.array([1, 2, 3]),
            'lower_sigma':np.array([1, 2, 3]),
            }
    
    def get(self):
        return indicator.ci(self.candle, self.indicator_params['d'], self.indicator_params['upper_sigma'], self.indicator_params['lower_sigma'])

    def init(self):
        self.upper, self.lower = self.I(self.get)
    
    def next(self):
        if crossover(self.data['Close'], self.lower):
            self.buy()
        elif crossover(self.upper, self.data['Close']):
            self.position.close()


class DMICross(ObjectStrategy):
    """
    DMI
    https://info.monex.co.jp/technical-analysis/indicators/015.html
    Stop And Reverse Point
    Parabolic is a technical indicator that displays a parabolic line at the top or bottom of a chart, 
    and is mainly useful when looking for trend turning points in the market.
    """
    def base_indicator_params():
        return {
            'd':np.array([7, 14, 21, 28, 35])
            }
    
    def get(self):
        return indicator.di(self.candle, self.indicator_params['d'])

    def init(self):
        self.di_p, self.di_m = self.I(self.get)
    
    def next(self):
        if crossover(self.di_p, self.di_m):
            self.buy()
        elif crossover(self.di_m, self.di_p):
            self.position.close()


class SARCross(ObjectStrategy):
    """
    SAR
    https://info.monex.co.jp/technical-analysis/indicators/021.html
    Directional Movement Index
    The feature of this indicator is to read the strength or weakness of the market by determining whether the high or low of the day is greater 
    than the high or low of the previous day, ignoring the comparison of closing prices, and to analyze the trend based on the volatility of prices.
    """
    def base_indicator_params():
        return {
            'init_af':np.array([0.01, 0.02, 0.05, 0.1]),
            'maxaf':np.array([0.1, 0.15, 0.2, 0.25])
            }

    def get(self):
        return indicator.sar(self.candle, self.indicator_params['init_af'], self.indicator_params['maxaf'])

    def init(self):
        self.sar, _, __ = self.I(self.get)
        
    def next(self):
        if crossover(self.data['Close'], self.sar):
            self.buy()
        elif crossover(self.sar, self.data['Close']):
            self.position.close()


class RSICross(ObjectStrategy):
    """
    RSI
    https://info.monex.co.jp/technical-analysis/indicators/005.html
    Relative Strength Index
    An indicator to determine how much the exchange rate has increased relative to the overall change in the exchange rate.
    """
    def base_indicator_params():
        return {
            'd':np.array([9, 14, 22, 42, 52]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }

    def get(self):
        return indicator.rsi(self.candle, self.indicator_params['d'])

    def init(self):
        self.rsi = self.I(self.get)
    
    def next(self):
        if crossover(self.indicator_params['buy_ratio'], self.rsi):
            self.buy()
        elif crossover(self.rsi, self.indicator_params['sell_ratio']):
            self.position.close()


class StochasticsCross(ObjectStrategy):
    """
    Stochastics
    https://info.monex.co.jp/technical-analysis/indicators/006.html
    Relative Strength Index
    Like RSI, it is an analytical method for determining overbought and oversold market conditions.
    """
    def base_indicator_params():
        return {
            'maxmin_span':np.array([5, 9, 14, 21, 30]),
            'k_span':np.array([2, 3, 4, 5]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }

    def get(self):
        return indicator.slow_s(self.candle, self.indicator_params['maxmin_span'], self.indicator_params['k_span'])

    def init(self):
        self.slow_per_k, self.slow_per_d = self.I(self.get)
    
    def next(self):
        if (crossover(self.indicator_params['buy_ratio'], self.slow_per_d) and (crossover(self.slow_per_k, self.slow_per_d))):
            self.buy()
        elif (crossover(self.slow_per_d, self.indicator_params['sell_ratio']) and (crossover(self.slow_per_d, self.slow_per_k))):
            self.position.close()


class PsychologicalCross(ObjectStrategy):
    """
    Psychological line
    https://info.monex.co.jp/technical-analysis/indicators/007.html
    The psychological line is an indicator that quantifies the "psychology of investors," and its calculation formula is simple and easy to understand.
    It is mainly effective in determining the strength and weakness of the market, and determining where to buy and sell.
    """
    def base_indicator_params():
        return {
            'span':np.array([5, 12, 19]),
            'buy_ratio':np.array([10, 15, 20, 25, 30, 35]),
            'sell_ratio':np.array([65, 70, 75, 80, 85, 90])
            }
    
    def get(self):
        return indicator.psyco(self.candle, self.indicator_params['span'])

    def init(self):
        self.psyco = self.I(self.get)
    
    def next(self):
        if self.indicator_params['buy_ratio'] > self.psyco:
            self.buy()
        elif self.psyco > self.indicator_params['sell_ratio']:
            self.position.close()


class RCICross(ObjectStrategy):
    """
    RCI
    https://info.monex.co.jp/technical-analysis/indicators/017.html
    Rank Correlation Index
    RCI is one of the indicators that quantify the psychology of investors to time their trades.
    It ranks the date and price respectively, and focuses on how much correlation there is between each.
    """
    def base_indicator_params():
        return {
            'span':np.array([7, 8, 9, 21, 23, 26, 42, 45, 48, 52]),
            'buy_ratio':np.array([-100, -90, -80, -70]),
            'sell_ratio':np.array([70, 80, 90, 100])
            }

    def get(self):
        return indicator.rci(self.candle, self.indicator_params['span'])

    def init(self):
        self.rci = self.I(self.get)
    
    def next(self):
        if crossover(self.indicator_params['buy_ratio'], self.rci):
            self.buy()
        elif crossover(self.rci, self.indicator_params['sell_ratio']):
            self.position.close()


class MAERCross(ObjectStrategy):
    """
    MAER
    https://info.monex.co.jp/technical-analysis/indicators/019.html
    Moving Average Estrangement Rate
    MAER is the percentage of the current price that is away from the moving average.
    """
    def base_indicator_params():
        return {
            'span':np.array([5, 25, 75, 100, 200]),
            'buy_ratio':np.array([-5, -6, -7, -8, -9, -10]),
            'sell_ratio':np.array([5, 6, 7, 8, 9, 10])
            }

    def get(self):
        return indicator.maer(self.candle, self.indicator_params['span'])

    def init(self):
        self.maer = self.I(self.get)
    
    def next(self):
        if crossover(self.indicator_params['buy_ratio'], self.maer):
            self.buy()
        elif crossover(self.maer, self.indicator_params['sell_ratio']):
            self.position.close()