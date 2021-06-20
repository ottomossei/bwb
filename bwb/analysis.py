# -*- coding: utf-8 -*-
import pandas_datareader.data as web
import datetime
import pandas as pd
from backtesting import Backtest, Strategy 
from backtesting.lib import crossover
import matplotlib.pyplot as plt


"""
Moving Average Convergence ／ Divergence Trading Method
MACD gives weight to the most recent values, and the weight decreases as the data gets older. 
Unlike simple moving averages, it avoids the fact that n-day old data and yesterday's data 
have the same weight, while at the same time n-day old data is not completely dropped.
"""
def calc_macd(close, n1, n2, ns):
    macd = pd.DataFrame()
    macd['close'] = close

    # Exponential Moving Average. short & long
    macd['ema_short'] = macd['close'].ewm(span=n1).mean()
    macd['ema_long'] = macd['close'].ewm(span=n2).mean()
    macd['macd'] = macd['ema_short'] - macd['ema_long']
    macd['macdsignal'] = macd['macd'].ewm(span=ns).mean()
    return macd['macd'], macd['macdsignal']
    
def plot_macd(macd, macdsignal):
    fig, (ax1, ax2) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[3, 1]})
    ax1.plot(pd.to_datetime(data.index.values), data['Close'])
    ax2.plot(pd.to_datetime(data.index.values), macd)
    ax2.plot(pd.to_datetime(data.index.values), macdsignal)
    fig.tight_layout()
    plt.show()


class MACDCross(Strategy):
    n1 = 12
    n2 = 26
    ns = 9

    def init(self):
        self.macd, self.macdsignal = self.I(calc_macd, self.data['Close'], self.n1, self.n2, self.ns)
    
    def next(self):
        if crossover(self.macd, self.macdsignal):
            self.buy()
        elif crossover(self.macdsignal, self.macd):
            self.position.close()

if __name__ == "__main__":
    # get Apple's stock price
    start = datetime.date(2019,1,1)
    end = datetime.date.today()
    data = web.DataReader('AAPL', 'yahoo', start, end)

    # Setting backtest
    bt = Backtest(
        data,
        MACDCross,
        cash=1000,
        commission=0.00495,
        margin=1.0,
        trade_on_close=True,
        exclusive_orders=True
    )

    output = bt.run()
    bt.plot()
    print(output)

    """
    # Drawing with matplotlib
    macd, macdsignal = calc_macd(data['Close'], 12, 26, 9)
    plot_macd(macd, macdsignal)
    """
