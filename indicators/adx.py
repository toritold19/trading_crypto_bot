
import pandas as pd
from utils.config import get_config

def calculate_adx(df):
    config = get_config()
    di_len = config.get("adx", {}).get("di_length", 14)
    adx_smoothing = config.get("adx", {}).get("adx_smoothing", 14)

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # DI+ / DI-
    up = high.diff()
    down = -low.diff()

    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)

    # True Range
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.ewm(span=di_len, adjust=False).mean()

    plus_di = 100 * (plus_dm.ewm(span=di_len, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(span=di_len, adjust=False).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 1)) * 100
    adx = dx.ewm(span=adx_smoothing, adjust=False).mean()

    return pd.DataFrame({
        "adx": adx,
        "+di": plus_di,
        "-di": minus_di
    })

def apply_adx(df):
    adx_df = calculate_adx(df)
    return pd.concat([df, adx_df], axis=1)
