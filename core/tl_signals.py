import pandas as pd
from indicators.momentum import calc_sz
from indicators.adx import calculate_adx
from indicators.pivots import is_pivot_low, is_pivot_high
from indicators.ma import ma
from utils.config import get_config

def tl_strategy_signals(open_, high, low, close):
    config = get_config()

    sz_delta_min = config.get("tl_signals", {}).get("sz_threshold", 0.0)
    use_trend = config.get("tl_signals", {}).get("use_trend_filter", False)
    trend_ma_type = config.get("tl_signals", {}).get("trend_ma_type", "EMA")
    trend_ma1 = config.get("tl_signals", {}).get("trend_ma1", 100)
    trend_ma2 = config.get("tl_signals", {}).get("trend_ma2", 200)

    # Indicadores
    sz = calc_sz(close, high, low)
    adx_df = calculate_adx(pd.DataFrame({"high": high, "low": low, "close": close}))
    adx = adx_df["adx"]

    if len(sz) < 3 or len(adx) < 3:
        return {"sz": float("nan"), "adx": float("nan"), "buy_tl": False, "sell_tl": False}

    sz_now, sz_prev = sz.iloc[-1], sz.iloc[-2]
    adx_now, adx_prev = adx.iloc[-1], adx.iloc[-2]

    # Pivots desplazados
    is_pl_sz = is_pivot_low(sz, left=1, right=1).iloc[-2]
    is_ph_sz = is_pivot_high(sz, left=1, right=1).iloc[-2]
    is_ph_adx = is_pivot_high(adx, left=1, right=1).iloc[-2]

    # Tendencia
    trend_ok = True
    if use_trend:
        trend_fast = ma(close, trend_ma1, trend_ma_type)
        trend_slow = ma(close, trend_ma2, trend_ma_type)
        trend_ok = trend_fast.iloc[-1] > trend_slow.iloc[-1]

    # Señales BUY
    cond_buy1 = is_pl_sz and adx_now < adx_prev
    cond_buy2 = is_ph_adx and sz_now >= sz_prev and sz_now < 0
    buy_tl = (cond_buy1 or cond_buy2) and abs(sz_now - sz_prev) >= sz_delta_min and trend_ok

    # Señales SELL
    cond_sell1 = is_ph_sz and adx_now < adx_prev
    cond_sell2 = is_ph_adx and sz_now < sz_prev and sz_now > 0
    sell_tl = (cond_sell1 or cond_sell2) and abs(sz_now - sz_prev) >= sz_delta_min and trend_ok

    return {
        "sz": float(sz_now),
        "adx": float(adx_now),
        "buy_tl": bool(buy_tl),
        "sell_tl": bool(sell_tl)
    }
