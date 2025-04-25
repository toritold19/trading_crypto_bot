import pandas as pd
from utils.config import get_config
from indicators.ma import ma

def calculate_adx(df):
    config = get_config()
    di_length = config.get("adx", {}).get("di_length", 14)
    adx_smoothing = config.get("adx", {}).get("adx_smoothing", 14)
    ma_type = config.get("adx", {}).get("ma_type", "WMA")

    high = df['high']
    low = df['low']
    close = df['close']

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = (high - low).abs()
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = ma(tr, di_length, ma_type)
    plus_di = 100 * ma(plus_dm, di_length, ma_type) / atr
    minus_di = 100 * ma(minus_dm, di_length, ma_type) / atr

    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx = ma(ma(dx, adx_smoothing, ma_type), adx_smoothing, ma_type)  # doble suavizado

    return pd.DataFrame({"adx": adx, "+di": plus_di, "-di": minus_di})