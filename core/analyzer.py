import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.config import get_config
from utils.logger import setup_logger
from core.tl_signals import tl_strategy_signals
from indicators.heikin_ashi import apply_heikin_ashi

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

    position_open = False
    entry_price = None
    df["trade_return_pct"] = None

    for i in range(len(df)):
        if i < 25:
            for key in ["sz", "sz_prev", "adx", "adx_prev", "is_pl_sz", "is_ph_sz", "is_ph_adx", "rsi", "rsi_ok", "Buy_TL", "Sell_TL"]:
                df.at[i, key] = None
        else:
            window_df = df.iloc[:i+1]
            try:
                position_active = df["Buy_TL"].iloc[:i].sum() > df["Sell_TL"].iloc[:i].sum()
                res = tl_strategy_signals(
                    open_=window_df[c_open],
                    close=window_df[c_close],
                    high=window_df[c_high],
                    low=window_df[c_low],
                    position_active=position_active
                )
            except Exception as e:
                log.warning(f"Error en signals para índice {i}: {e}")
                res = {key: float('nan') for key in ["sz", "sz_prev", "adx", "adx_prev", "is_pl_sz", "is_ph_sz", "is_ph_adx", "rsi", "rsi_ok", "buy_tl", "sell_tl"]}

            df.at[i, "sz"] = res["sz"]
            df.at[i, "sz_prev"] = res["sz_prev"]
            df.at[i, "adx"] = max(res["adx"] or 0, 0)
            df.at[i, "adx_prev"] = max(res["adx_prev"] or 0, 0)
            df.at[i, "is_pl_sz"] = res["is_pl_sz"]
            df.at[i, "is_ph_sz"] = res["is_ph_sz"]
            df.at[i, "is_ph_adx"] = res["is_ph_adx"]
            df.at[i, "rsi"] = res["rsi"]
            df.at[i, "rsi_ok"] = res["rsi_ok"]
            df.at[i, "Buy_TL"] = res["buy_tl"]
            df.at[i, "Sell_TL"] = res["sell_tl"]

            # Simular operación para rendimiento
            if res["buy_tl"] and not position_open:
                entry_price = df.at[i, c_close]
                position_open = True

                # Recalcular en la misma vela si también hay señal de salida
                if res["sell_tl"]:
                    exit_price = df.at[i, c_close]
                    trade_return = ((exit_price - entry_price) / entry_price) * 100
                    df.at[i, "trade_return_pct"] = round(trade_return, 2)
                    position_open = False
                    entry_price = None

            elif res["sell_tl"] and position_open and entry_price:
                exit_price = df.at[i, c_close]
                trade_return = ((exit_price - entry_price) / entry_price) * 100
                df.at[i, "trade_return_pct"] = round(trade_return, 2)
                position_open = False
                entry_price = None

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
        required_cols = ["rsi", "adx", "sz", c_open, c_close, c_high, c_low]
        df_plot = df.dropna(subset=required_cols).copy()
        if not df_plot.empty:
            plot_signals_plotly(df_plot, c_open, c_close, c_high, c_low, dark_mode=True)

        return df

def plot_signals_plotly(df, c_open="open", c_close="close", c_high="high", c_low="low", dark_mode=False):
    df_plot = df.dropna(subset=[c_open, c_high, c_low, c_close, "rsi", "adx"]).copy()
    df_plot["time"] = pd.to_datetime(df_plot["time"])

    # Tema visual
    if dark_mode:
        template = "plotly_dark"
        inc_color = "#00ff00"
        dec_color = "#ff3333"
        rsi_color = "#1e90ff"
        adx_color = "orange"
    else:
        template = "plotly_white"
        inc_color = "green"
        dec_color = "red"
        rsi_color = "blue"
        adx_color = "orange"

    # Crear subplots (3 filas)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Velas + Señales", "RSI", "ADX")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df_plot["time"],
        open=df_plot[c_open],
        high=df_plot[c_high],
        low=df_plot[c_low],
        close=df_plot[c_close],
        name="Velas",
        increasing_line_color=inc_color,
        decreasing_line_color=dec_color
    ), row=1, col=1)

    # Señales de compra
    buy_signals = df_plot[df_plot["Buy_TL"] == True]
    fig.add_trace(go.Scatter(
        x=buy_signals["time"],
        y=buy_signals[c_close],
        mode="markers+text",
        marker=dict(color="lime", size=10, symbol="triangle-up"),
        text=["BUY"] * len(buy_signals),
        textposition="top center",
        name="BUY Signals"
    ), row=1, col=1)

    # Señales de venta
    sell_signals = df_plot[df_plot["Sell_TL"] == True]
    fig.add_trace(go.Scatter(
        x=sell_signals["time"],
        y=sell_signals[c_close],
        mode="markers+text",
        marker=dict(color="red", size=10, symbol="triangle-down"),
        text=["SELL"] * len(sell_signals),
        textposition="bottom center",
        name="SELL Signals"
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df_plot["time"],
        y=df_plot["rsi"],
        name="RSI",
        line=dict(color=rsi_color, width=2)
    ), row=2, col=1)

    # ADX
    fig.add_trace(go.Scatter(
        x=df_plot["time"],
        y=df_plot["adx"],
        name="ADX",
        line=dict(color=adx_color, width=2)
    ), row=3, col=1)

    # Layout final
    fig.update_layout(
        height=900,
        template=template,
        title="ETH/USDT - Señales TL + Indicadores (Plotly)",
        showlegend=True,
        xaxis=dict(title="Fecha/Hora"),
        yaxis=dict(title="Precio"),
        yaxis2=dict(title="RSI"),
        yaxis3=dict(title="ADX"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.show()
