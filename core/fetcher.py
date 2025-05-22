import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz
from utils.logger import setup_logger

log = setup_logger()

def resample_ohlcv(df, target_tf):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    df_resampled = pd.DataFrame()
    df_resampled['open'] = df['open'].resample(target_tf).first()
    df_resampled['high'] = df['high'].resample(target_tf).max()
    df_resampled['low'] = df['low'].resample(target_tf).min()
    df_resampled['close'] = df['close'].resample(target_tf).last()
    df_resampled['volume'] = df['volume'].resample(target_tf).sum()

    df_resampled.dropna(inplace=True)
    df_resampled.reset_index(inplace=True)
    df_resampled['timestamp'] = df_resampled['timestamp'].astype('int64') // 10**6  # to ms
    return df_resampled

def fetch_ohlcv(exchange_name, symbol, timeframe, hours=None, tz_str="UTC"):
    try:
        if not all([exchange_name, symbol, timeframe]):
            raise ValueError("Faltan argumentos obligatorios: exchange_name, symbol, timeframe")

        exchange = getattr(ccxt, exchange_name)()
        exchange.options["defaultType"] = "spot"

        now_utc = datetime.now(timezone.utc)
        if hours is None:
            hours = 720 if timeframe == "45m" else 48
        since = int((now_utc - timedelta(hours=hours)).timestamp() * 1000)

        log.info(f"Solicitando datos OHLCV desde {exchange_name.upper()} ({symbol}) en temporalidad {timeframe}...")

        base_tf = "15m" if timeframe == "45m" else timeframe
        ohlcv = exchange.fetch_ohlcv(symbol, base_tf, since=since)

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        if df.empty:
            raise ValueError("No se obtuvieron datos desde el exchange.")

        if timeframe == "45m":
            df = resample_ohlcv(df, "45min")

        df["time_utc"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        local_tz = pytz.timezone(tz_str)
        df["time_local"] = df["time_utc"].dt.tz_convert(local_tz)
        df["time"] = df["time_local"].dt.strftime("%Y-%m-%d %H:%M")
        df["date"] = df["time_local"].dt.strftime("%Y-%m-%d")
        df["hour"] = df["time_local"].dt.strftime("%H:%M:%S")

        log.info("Datos OHLCV correctamente obtenidos y convertidos.")
        return df

    except Exception as e:
        log.error(f"[fetch_ohlcv] Error al obtener datos: {e}")
        return pd.DataFrame()
