import pandas as pd
import numpy as np

def sma(data, day=5):
    return pd.Series(data=data['Close']).rolling(window = day).mean()

def sigma(data, day=5):
    return pd.Series(data=data['Close']).rolling(window = day).std()

def ema(data, day=5):
    # Exponential Moving Average.
    return data['Close'].ewm(span=day).mean()

def macd(data, day_short=12, day_long=26, span=9):
    macd = ema(data, day_short) - ema(data, day_long)
    macdsignal = macd.ewm(span=span).mean()
    return macd, macdsignal

def ci(data, day=20, upper_sigma=2, lower_sigma=2):
    # Confidence interval
    _sma, _sigma = sma(data, day), sigma(data, day)
    return _sma + _sigma * upper_sigma, _sma - _sigma * lower_sigma

def di(data, span=14):
    # Direction Movement (±DM)
    dm_p = data['High'] - data['High'].shift(1)
    dm_m = data['Low'].shift(1) - data['Low']
    dm_p.loc[dm_p<0] = 0
    dm_m.loc[dm_m<0] = 0
    dm_p.loc[dm_p-dm_m <= 0] = 0
    dm_m.loc[dm_p-dm_m >= 0] = 0
    # True Range (TR)
    _tr = tr(data)
    # Direction Indicator (±DI)
    return dm_p.rolling(span).sum()/_tr.rolling(span).sum() * 100, dm_m.rolling(span).sum()/_tr.rolling(span).sum() * 100

def tr(data):
    # True Range (TR)
    a = (data['High'] - data['Low']).abs()
    b = (data['High'] - data['Close'].shift(1)).abs()
    c = (data['Low'] - data['Close'].shift(1)).abs()
    return pd.concat([a, b, c], axis=1).max(axis=1)

def adx(data, span=14):
    # Direction Indicator (±DI)
    di_p, di_m = di(data, span)
    # Directional Index (DX)
    dx = ((di_p - di_m).abs() / (di_p + di_m) * 100)
    # Average Directional Index
    return dx.rolling(span).mean()

def sar(data, iaf=0.02, maxaf=0.2):
    # Refer to https://github.com/soshika/stock_marketing/blob/master/indicators/parabolicSAR.py
    # Stop And Reverse Point
    # AF(Acceleration Factor), EP(Extreme Price)
    length = len(data)
    high = list(data['High'])
    low = list(data['Low'])
    close = list(data['Close'])
    psar = close[0:len(close)]
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]
    for i in range(2,length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
        reverse = False
        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf
        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]
        if bull:
            psarbull[i] = psar[i]
        else:
            psarbear[i] = psar[i]
    return pd.Series(data=psar, index=data.index), pd.Series(data=psarbear, index=data.index), pd.Series(data=psarbull, index=data.index)

def rsi(data, span):
    # Relative Strength Index
    diff = data['Close'].diff()
    up, down = diff.copy(), diff.copy()
    up[up <= 0] = 0
    down[down > 0] = 0
    up_sma = up.rolling(window=span).sum().abs()
    down_sma = down.rolling(window=span).sum().abs()
    return 1.0 - (1.0 / (1.0 + (up_sma / down_sma)))