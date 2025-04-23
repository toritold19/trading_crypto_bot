import pandas as pd
import numpy as np
from utils.config import get_config

CONFIG = get_config()
MA_CONFIG = CONFIG.get("ma", {})

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def ma(ma_type: str, series: pd.Series, period: int) -> pd.Series:
    ma_type = ma_type.upper()

    if period <= 0:
        return pd.Series(np.nan, index=series.index)

    if ma_type == "EMA":
        return ema(series, period)

    elif ma_type == "SMA":
        return series.rolling(window=period).mean()

    elif ma_type == "WMA":
        weights = np.arange(1, period + 1)
        return series.rolling(period).apply(lambda prices: np.dot(prices, weights)/weights.sum(), raw=True)

    elif ma_type == "RMA":
        alpha = 1 / period
        rma = [series.iloc[0]]
        for price in series.iloc[1:]:
            rma.append((1 - alpha) * rma[-1] + alpha * price)
        return pd.Series(rma, index=series.index)

    elif ma_type == "HMA":
        wma_half = ma("WMA", series, period // 2)
        wma_full = ma("WMA", series, period)
        diff = 2 * wma_half - wma_full
        return ma("WMA", diff, int(np.sqrt(period)))

    else:
        raise ValueError(f"Tipo de media móvil no soportado: {ma_type}")

def get_configured_mas(series: pd.Series) -> dict:
    return {
        key: ma(params["type"], series, params["period"])
        for key, params in MA_CONFIG.items()
    }