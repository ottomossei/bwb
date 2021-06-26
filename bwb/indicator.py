import pandas as pd
import numpy as np

def sma(data, day=5):
    return pd.Series(data=data['Close']).rolling(window = day).mean()

def sigma(data, day=5):
    return pd.Series(data=data['Close']).rolling(window = day).std()

def ema(data, day=5):
    return data['Close'].ewm(span=day).mean()

def macd(data, day_short=12, day_long=26, day_span=9):
    # Exponential Moving Average. short & long
    macd = ema(data, day_short) - ema(data, day_long)
    macdsignal = macd.ewm(span=day_span).mean()
    return macd, macdsignal

def ci(data, day, upper_sigma, lower_sigma):
    # Confidence interval
    _sma, _sigma = sma(data, day), sigma(data, day)
    return _sma + _sigma * upper_sigma, _sma + _sigma * lower_sigma