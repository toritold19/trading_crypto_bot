import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from utils.config import get_config
from utils.logger import setup_logger
from core.tl_signals import tl_strategy_signals
from indicators.heikin_ashi import apply_heikin_ashi
import os
from datetime import datetime
from matplotlib.patches import Rectangle

log = setup_logger()
CONFIG = get_config()


def analyze_dataframe(df, export_csv=False, csv_filename=None, execute_signals=False, plot_backtest=False, dark_mode=False):
    tipo = CONFIG.get("analyzer", {}).get("candle_type", "tradicional")

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

    for i in range(len(df)):
        if i < 25:
            for key in ["sz", "sz_prev", "adx", "adx_prev", "is_pl_sz", "is_ph_sz", "is_ph_adx", "rsi", "rsi_ok", "Buy_TL", "Sell_TL"]:
                df.at[i, key] = None
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
                res = {key: float('nan') for key in ["sz", "sz_prev", "adx", "adx_prev", "is_pl_sz", "is_ph_sz", "is_ph_adx", "rsi", "rsi_ok", "buy_tl", "sell_tl"]}

            df.at[i, "sz"] = res["sz"]
            df.at[i, "sz_prev"] = res["sz_prev"]
            df.at[i, "adx"] = max(res["adx"], 0)
            df.at[i, "adx_prev"] = max(res["adx_prev"], 0)
            df.at[i, "is_pl_sz"] = res["is_pl_sz"]
            df.at[i, "is_ph_sz"] = res["is_ph_sz"]
            df.at[i, "is_ph_adx"] = res["is_ph_adx"]
            df.at[i, "rsi"] = res["rsi"]
            df.at[i, "rsi_ok"] = res["rsi_ok"]
            df.at[i, "Buy_TL"] = res["buy_tl"]
            df.at[i, "Sell_TL"] = res["sell_tl"]

    df["signal_tl"] = df.apply(lambda row: "BUY" if row.get("Buy_TL") else "SELL" if row.get("Sell_TL") else "-", axis=1)

    if export_csv:
        export_dir = "core/exports"
        os.makedirs(export_dir, exist_ok=True)
        if not csv_filename:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"analysis_{fecha}.csv"
        export_path = os.path.join(export_dir, csv_filename)
        df.to_csv(export_path, index=False)
        log.info(f"Archivo exportado: {export_path}")

    if plot_backtest:
        plot_signals(df, c_open, c_close, c_high, c_low, dark_mode)

    return df


def plot_signals(df, c_open, c_close, c_high, c_low, dark_mode=False):
    df["time"] = pd.to_datetime(df["time"])
    if dark_mode:
        plt.style.use("dark_background")

    fig, axs = plt.subplots(4, 1, figsize=(18, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})

    # Mejora velas
    width = 0.0007 * len(df)  # Más delgado
    candle_color_up = "#26a69a"
    candle_color_down = "#ef5350"

    for idx, row in df.iterrows():
        color = candle_color_up if row[c_close] >= row[c_open] else candle_color_down
        axs[0].plot([row["time"], row["time"]], [row[c_low], row[c_high]],
                    color='white' if dark_mode else 'black', linewidth=0.7)
        rect = Rectangle(
            (mdates.date2num(row["time"]) - width / 2, min(row[c_open], row[c_close])),
            width, max(abs(row[c_close] - row[c_open]), 0.0001),
            color=color, zorder=2
        )
        axs[0].add_patch(rect)

    for i, row in df.iterrows():
        if row["Buy_TL"]:
            axs[0].plot(row["time"], row[c_close], marker="^", color="green", markersize=10)
            axs[0].text(row["time"], row[c_close] + 15, "BUY", color="red", fontsize=9, weight="bold", ha="center")
            axs[0].text(row["time"], row[c_close] + 9, row["time"].strftime("%H:%M"), color="gray", fontsize=8, ha="center")
        elif row["Sell_TL"]:
            axs[0].plot(row["time"], row[c_close], marker="v", color="red", markersize=10)
            axs[0].text(row["time"], row[c_close] + 15, "SELL", color="red", fontsize=9, weight="bold", ha="center")
            axs[0].text(row["time"], row[c_close] + 9, row["time"].strftime("%H:%M"), color="gray", fontsize=8, ha="center")

    axs[0].set_ylabel("Precio")
    axs[0].set_title("ETH/USDT - Heikin Ashi + Señales TL (15m)")
    axs[0].grid(True, linestyle="--", alpha=0.3)

    axs[1].plot(df["time"], df["rsi"], label="RSI", color="blue")
    axs[1].axhspan(45, 55, color="red", alpha=0.2, label="Zona Muerta RSI")
    axs[1].set_ylabel("RSI")
    axs[1].set_yticks(range(0, 101, 10))
    axs[1].legend()
    axs[1].grid(True, linestyle="--", alpha=0.3)

    axs[2].plot(df["time"], df["adx"], label="ADX", color="orange")
    axs[2].set_ylabel("ADX")
    axs[2].set_yticks(range(0, 101, 10))
    axs[2].legend()
    axs[2].grid(True, linestyle="--", alpha=0.3)

    axs[3].plot(df["time"], df["sz"], label="SZ", color="purple")
    axs[3].set_ylabel("SZ")
    axs[3].legend()
    axs[3].grid(True, linestyle="--", alpha=0.3)

    axs[-1].xaxis.set_major_locator(mdates.HourLocator(byhour=[3, 6, 9, 12, 15, 18, 21]))
    axs[-1].xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
    axs[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))

    plt.tight_layout()
    plt.show()
