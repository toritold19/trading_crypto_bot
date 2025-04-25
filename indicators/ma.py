# indicators/ma.py
import pandas as pd
import numpy as np


def sma(series, length):
    return series.rolling(window=length).mean()


def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()


def wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def rma(series, length):
    alpha = 1 / length
    return series.ewm(alpha=alpha, adjust=False).mean()


def ma(series, length, ma_type="SMA"):
    if ma_type == "SMA":
        return sma(series, length)
    elif ma_type == "EMA":
        return ema(series, length)
    elif ma_type == "WMA":
        return wma(series, length)
    elif ma_type == "RMA":
        return rma(series, length)
    else:
        raise ValueError(f"Unsupported MA type: {ma_type}")