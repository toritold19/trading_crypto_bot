
import pandas as pd
from indicators.momentum import calc_sz
from indicators.adx import calculate_adx
from indicators.pivots import is_pivot_low, is_pivot_high

def tl_strategy_signals(close, high, low):
    """
    Genera señales Buy_TL y Sell_TL replicando lógica del Pine Script LPWN.
    Aplica lógica de pivots con desplazamiento para permitir confirmación (right=1).
    """
    df_adx = pd.DataFrame({"high": high, "low": low, "close": close})

    # Indicadores
    sz = calc_sz(close, high, low)
    adx_df = calculate_adx(df_adx)
    adx = adx_df["adx"]

    if len(sz) < 3 or len(adx) < 3:
        return {"sz": float("nan"), "adx": float("nan"), "buy_tl": False, "sell_tl": False}

    sz_now, sz_prev = sz.iloc[-1], sz.iloc[-2]
    adx_now, adx_prev = adx.iloc[-1], adx.iloc[-2]

    # Desplazamiento: pivots detectados 1 barra antes (right=1)
    is_pl_sz = is_pivot_low(sz, left=1, right=1).iloc[-2]
    is_ph_sz = is_pivot_high(sz, left=1, right=1).iloc[-2]
    is_ph_adx = is_pivot_high(adx, left=1, right=1).iloc[-2]

    # Señales BUY
    cond_buy1 = is_pl_sz and adx_now < adx_prev
    cond_buy2 = is_ph_adx and sz_now >= sz_prev and sz_now < 0
    buy_tl = cond_buy1 or cond_buy2

    # Señales SELL
    cond_sell1 = is_ph_sz and adx_now < adx_prev
    cond_sell2 = is_ph_adx and sz_now < sz_prev and sz_now > 0
    sell_tl = cond_sell1 or cond_sell2

    return {
        "sz": float(sz_now),
        "adx": float(adx_now),
        "buy_tl": bool(buy_tl),
        "sell_tl": bool(sell_tl)
    }
