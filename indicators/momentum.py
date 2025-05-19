import pandas as pd
import numpy as np
from utils.config import get_config

def calc_sz(close, high, low):
    """
    Calcula el Squeeze Momentum Indicator (SZ) igual a LPWN.
    """
    config = get_config()
    mom_cfg = config.get("momentum", {})
    length = mom_cfg.get("length", 20)  # Por defecto 20

    # 1. Calcular el midpoint
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()
    sma_close = close.rolling(window=length).mean()

    midpoint = ((highest_high + lowest_low) / 2 + sma_close) / 2

    # 2. Calcular diferencia
    val = close - midpoint

    # 3. Aplicar regresión lineal sobre "val" (NO suavizado doble)
    def linreg_slope(series):
        y = series.values
        x = np.arange(len(y))
        if len(y) == 0 or np.std(x) == 0:
            return np.nan
        slope = np.cov(x, y, bias=True)[0, 1] / np.var(x)
        return slope

    sz = val.rolling(window=length).apply(linreg_slope, raw=False)

    return sz