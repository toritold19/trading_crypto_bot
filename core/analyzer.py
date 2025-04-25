import pandas as pd
from utils.config import get_config
from utils.logger import setup_logger
from core.tl_signals import tl_strategy_signals
from indicators.heikin_ashi import apply_heikin_ashi
import os
from datetime import datetime

log = setup_logger()
CONFIG = get_config()

def analyze_dataframe(df, export_csv=False, csv_filename=None, execute_signals=False):
    tipo = CONFIG.get("analyzer", {}).get("candle_type", "tradicional")

    # Aplicar Heikin Ashi si corresponde
    if tipo == "heikin_ashi":
        df = apply_heikin_ashi(df)
        c_open = "ha_open"
        c_close = "ha_close"
        c_high = "ha_high"
        c_low = "ha_low"
    else:
        c_open = "open"
        c_close = "close"
        c_high = "high"
        c_low = "low"

    # Señales TL Strategy
    sz_list = []
    adx_list = []
    buy_list = []
    sell_list = []

    for i in range(len(df)):
        if i < 25:
            sz_list.append(None)
            adx_list.append(None)
            buy_list.append(False)
            sell_list.append(False)
        else:
            window_df = df.iloc[:i+1]
            try:
                res = tl_strategy_signals(
                    open_=window_df[c_open],
                    close=window_df[c_close],
                    high=window_df[c_high],
                    low=window_df[c_low]
                )
            except Exception as e:
                log.warning(f"Error en signals para índice {i}: {e}")
                res = {"sz": float("nan"), "adx": float("nan"), "buy_tl": False, "sell_tl": False}

            sz_list.append(res['sz'])
            adx_list.append(res['adx'])
            buy_list.append(res['buy_tl'])
            sell_list.append(res['sell_tl'])

    df["sz"] = sz_list
    df["adx"] = adx_list
    df["Buy_TL"] = buy_list
    df["Sell_TL"] = sell_list

    # Señal resumen final TL
    df["signal_tl"] = df.apply(lambda row: "BUY" if row.get("Buy_TL") else "SELL" if row.get("Sell_TL") else "-", axis=1)

    if execute_signals:
        if res.get("buy_tl"):
            log.info("Ejecutando acción de COMPRA...")
        elif res.get("sell_tl"):
            log.info("Ejecutando acción de VENTA...")

    if export_csv:
        export_dir = "core/exports"
        os.makedirs(export_dir, exist_ok=True)
        if not csv_filename:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"analysis_{fecha}.csv"
        export_path = os.path.join(export_dir, csv_filename)
        df.to_csv(export_path, index=False)
        log.info(f"Archivo exportado: {export_path}")

    return df
