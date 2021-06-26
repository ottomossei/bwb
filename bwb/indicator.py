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
    di_p, di_m = di(data, span)
    dx = ((di_p - di_m).abs() / (di_p + di_m) * 100)
    
    # Average Directional Index
    return dx.rolling(span).mean()