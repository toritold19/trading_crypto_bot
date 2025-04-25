
import numpy as np
import pandas as pd
from utils.config import get_config

def calc_sz(close, high, low):
    config = get_config()
    length = config.get("momentum", {}).get("length", 20)

    centro = (high.rolling(length).max() + low.rolling(length).min()) / 2
    media = close.rolling(length).mean()
    sz_raw = close - ((centro + media) / 2)

    # Resetear índice para evitar errores con np.polyfit
    sz_raw = sz_raw.reset_index(drop=True)
    x = np.arange(len(sz_raw))
    sz = pd.Series(index=sz_raw.index, dtype='float64')

    for i in range(length, len(sz_raw)):
        y = sz_raw.iloc[i - length:i]
        if y.isna().any():
            continue
        coef = np.polyfit(x[i - length:i], y, 1)[0]
        sz.iloc[i] = coef

    return sz
