import pandas as pd
from utils.config import get_config
from indicators.ma import ma

def calc_sz(close, high, low):
    """
    Calcula el Squeeze Momentum Indicator con suavizado doble como en LPWN.
    """
    config = get_config()
    mom_cfg = config.get("momentum", {})
    length = mom_cfg.get("length", 20)
    ma_type = mom_cfg.get("type", "WMA")  # default WMA según LPWN

    avg_price = (high + low + close) / 3
    val = close - avg_price

    sz = ma(ma(val, 4, ma_type), 4, ma_type)  # doble suavizado con WMA por defecto
    return sz