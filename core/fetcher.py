# core/fetcher.py

import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz
from utils.logger import setup_logger

log = setup_logger()

def fetch_ohlcv(exchange_name, symbol, timeframe, hours, tz_str="UTC"):
    try:
        # Validación básica
        if not all([exchange_name, symbol, timeframe, hours]):
            raise ValueError("Faltan argumentos obligatorios: exchange_name, symbol, timeframe, hours")

        exchange = getattr(ccxt, exchange_name)()
        exchange.options["defaultType"] = "spot"

        now_utc = datetime.now(timezone.utc)
        since = int((now_utc - timedelta(hours=hours)).timestamp() * 1000)

        log.info(f"Solicitando datos OHLCV desde {exchange_name.upper()} ({symbol}) en temporalidad {timeframe}...")

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        if df.empty:
            raise ValueError("No se obtuvieron datos desde el exchange.")

        # Timestamps
        df["time_utc"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        local_tz = pytz.timezone(tz_str)
        df["time"] = df["time_utc"].dt.tz_convert(local_tz)
        df["date"] = df["time"].dt.date
        df["hour"] = df["time"].dt.time

        log.info("Datos OHLCV correctamente obtenidos y convertidos.")
        return df

    except Exception as e:
        log.error(f"[fetch_ohlcv] Error al obtener datos: {e}")
        return pd.DataFrame()
