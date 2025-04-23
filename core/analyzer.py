from indicators.ema import get_configured_mas
from indicators.heikin_ashi import heikin_ashi
from indicators.adx import adx
from indicators.whale import whale_signal
from indicators.momentum import squeeze_momentum
from indicators.stoch_rsi import stoch_rsi
from core.signals import add_buy_sell_tl_signals
from utils.logger import setup_logger
from utils.config import get_config
import pandas as pd
import os
from datetime import datetime

log = setup_logger()
CONFIG = get_config()

def analyze_dataframe(df, export_csv=False, csv_filename=None):
    candle_type = CONFIG.get("analyzer", {}).get("candle_type", "heikin_ashi")
    if candle_type == "heikin_ashi":
        df = heikin_ashi(df)
        price_col = "ha_close"
        tipo = "heikin"
    else:
        price_col = "close"
        tipo = "tradicional"

    # EMAs desde config
    mas = get_configured_mas(df[price_col])
    for name, values in mas.items():
        df[name] = values

    # Tendencias macro y micro
    df["macroTrend"] = df.get("MA3", pd.Series([False]*len(df))) >= df.get("MA4", pd.Series([False]*len(df)))
    df["microTrend"] = df.get("MA1", pd.Series([False]*len(df))) >= df.get("MA2", pd.Series([False]*len(df)))
    df["macroTrendLabel"] = df["macroTrend"].apply(lambda x: "UP" if x else "DOWN")
    df["microTrendLabel"] = df["microTrend"].apply(lambda x: "UP" if x else "DOWN")

    # ADX y +DI / -DI (usa config internamente)
    df["ADX"], df["+DI"], df["-DI"] = adx(df["high"], df["low"], df[price_col])

    # Whale unificada (usa config internamente)
    whale_df = whale_signal(df.copy(), column=price_col)
    whale_df["whale"] = whale_df["is_whale"].shift(1).fillna(False).map(lambda x: "TOP" if x else None)
    whale_df["whale"] = whale_df["whale"].combine_first(
        whale_df["is_whale_invert"].shift(1).fillna(False).map(lambda x: "BOTTOM" if x else None)
    )
    df["whale"] = whale_df["whale"].fillna("-")

    # Momentum (squeeze)
    df["sz"] = squeeze_momentum(df)

    # Stoch RSI
    df["stoch_k"], df["stoch_d"] = stoch_rsi(df)

    # Señales Buy/Sell TL usando lógica centralizada
    df = add_buy_sell_tl_signals(df)

    if export_csv:
        export_dir = "core/exports"
        os.makedirs(export_dir, exist_ok=True)
        if not csv_filename:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"analysis_{tipo}_{fecha}.csv"
        filepath = os.path.join(export_dir, csv_filename)
        df.to_csv(filepath, index=False)
        log.info(f"DataFrame exportado como {filepath}")

    return df

def print_analysis_table(df, tipo="Tradicional"):
    log.info("="*22 + f" {tipo.upper()} " + "="*22)
    log.info("+------------+----------+-----------+----------------+----------------+-----------+-----------+-----------+------------+--------------+")
    log.info("|   Fecha    |  Hora    |  Cierre   | Macro Trend    | Micro Trend    |   ADX     |   +DI     |   -DI     | Señal TL   | Whale        |")
    log.info("+------------+----------+-----------+----------------+----------------+-----------+-----------+-----------+------------+--------------+")

    tail_size = CONFIG.get("analyzer", {}).get("analyze_rows", 5)
    df_tail = df.tail(tail_size)
    for _, row in df_tail.iterrows():
        fecha = row['date']
        hora = row['hour']
        close = row['ha_close'] if "ha_close" in row else row['close']
        close = f"{close:.2f}"
        macro = row['macroTrendLabel']
        micro = row['microTrendLabel']
        adx_val = f"{row['ADX']:.2f}"
        plus_di = f"{row['+DI']:.2f}"
        minus_di = f"{row['-DI']:.2f}"
        signal = row['signal_tl'].upper() if 'signal_tl' in row and pd.notna(row['signal_tl']) else "-"
        whale_flag = row.get("whale", "-")

        log.info(f"| {fecha} | {hora} | {close:>9} | {macro:^14} | {micro:^14} | {adx_val:>9} | {plus_di:>9} | {minus_di:>9} | {signal:^10} | {whale_flag:^12} |")

    log.info("+------------+----------+-----------+----------------+----------------+-----------+-----------+-----------+------------+--------------+")