import pandas as pd
import numpy as np
from utils.config import get_config

def adx(high, low, close, period=None):
    """
    Calcula ADX, +DI y -DI a partir de precios OHLC.
    Usa el valor de 'period' desde config.json si no se especifica.
    """
    config = get_config()
    period = period or config.get("adx", {}).get("period", 14)

    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()
    plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr

    dx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=period).mean()

    return adx, plus_di, minus_di