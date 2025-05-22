# core/tl_signals.py

import pandas as pd
from indicators.momentum import calc_sz
from indicators.adx import calculate_adx
from indicators.pivots import is_pivot_low, is_pivot_high
from indicators.rsi import calculate_rsi, is_rsi_outside_dead_zone
from utils.config import get_config

def tl_strategy_signals(open_, high, low, close, position_active=False):
    config = get_config()

    pivot_left = config.get("pivots", {}).get("left", 1)
    pivot_right = config.get("pivots", {}).get("right", 1)
    key_level = config.get("adx", {}).get("key_level", 23)
    rsi_length = config.get("rsi", {}).get("length", 14)

    sz = calc_sz(close, high, low)
    adx_df = calculate_adx(pd.DataFrame({"high": high, "low": low, "close": close}))
    adx = adx_df["adx"]

    rsi_series = calculate_rsi(close, length=rsi_length)
    rsi_ok_series = is_rsi_outside_dead_zone(rsi_series)

    if len(sz) < 3 or len(adx) < 3:
        return {
            "sz": float("nan"), "sz_prev": float("nan"),
            "adx": float("nan"), "adx_prev": float("nan"),
            "is_pl_sz": False, "is_ph_sz": False, "is_ph_adx": False,
            "rsi": float("nan"), "rsi_ok": False,
            "buy_tl": False, "sell_tl": False
        }

    sz_now, sz_prev = sz.iloc[-1], sz.iloc[-2]
    adx_now, adx_prev = adx.iloc[-1], adx.iloc[-2]

    is_pl_sz = is_pivot_low(sz, left=pivot_left, right=pivot_right).iloc[-2]
    is_ph_sz = is_pivot_high(sz, left=pivot_left, right=pivot_right).iloc[-2]
    is_ph_adx = is_pivot_high(adx, left=pivot_left, right=pivot_right).iloc[-2]

    strong_trend = adx_now > key_level
    rsi_ok = rsi_ok_series.iloc[-1]

    cond_buy1 = is_pl_sz and adx_now < adx_prev
    cond_buy2 = is_ph_adx and sz_now >= sz_prev and sz_now < 0
    buy_tl = (cond_buy1 or cond_buy2) and strong_trend and rsi_ok and not position_active

    cond_sell1 = is_ph_sz and adx_now < adx_prev
    cond_sell2 = is_ph_adx and sz_now < sz_prev and sz_now > 0
    sell_tl = (cond_sell1 or cond_sell2) and strong_trend and rsi_ok

    return {
        "sz": float(sz_now), "sz_prev": float(sz_prev),
        "adx": float(adx_now), "adx_prev": float(adx_prev),
        "is_pl_sz": is_pl_sz, "is_ph_sz": is_ph_sz, "is_ph_adx": is_ph_adx,
        "rsi": float(rsi_series.iloc[-1]), "rsi_ok": rsi_ok,
        "buy_tl": buy_tl, "sell_tl": sell_tl
    }