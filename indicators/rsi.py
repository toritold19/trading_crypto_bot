import pandas as pd
from utils.config import get_config

def calculate_rsi(series, length=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1/length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/length, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def is_rsi_outside_dead_zone(rsi_series):
    config = get_config()
    use_deadzone = config.get("rsi", {}).get("use_deadzone", True)
    dead_min = config.get("rsi", {}).get("dead_min", 45)
    dead_max = config.get("rsi", {}).get("dead_max", 55)

    if not use_deadzone:
        return pd.Series([True] * len(rsi_series), index=rsi_series.index)

    outside = (rsi_series < dead_min) | (rsi_series > dead_max)
    return outside
