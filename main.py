import time
from core.fetcher import fetch_ohlcv
from core.analyzer import analyze_dataframe
from utils.logger import setup_logger
from utils.config import get_config
import sys

sys.stdout.reconfigure(encoding='utf-8')

def print_start():
    print(r"""
 /$$$$$$$$                       /$$ /$$                           /$$$$$$$              /$$    
|__  $$__/                      | $$|__/                          | $$__  $$            | $$    
   | $$  /$$$$$$  /$$$$$$   /$$$$$$$ /$$ /$$$$$$$   /$$$$$$       | $$  \ $$  /$$$$$$  /$$$$$$  
   | $$ /$$__  $$|____  $$ /$$__  $$| $$| $$__  $$ /$$__  $$      | $$$$$$$  /$$__  $$|_  $$_/  
   | $$| $$  \__/ /$$$$$$$| $$  | $$| $$| $$  \ $$| $$  \ $$      | $$__  $$| $$  \ $$  | $$    
   | $$| $$      /$$__  $$| $$  | $$| $$| $$  | $$| $$  | $$      | $$  \ $$| $$  | $$  | $$ /$$
   | $$| $$     |  $$$$$$$|  $$$$$$$| $$| $$  | $$|  $$$$$$$      | $$$$$$$/|  $$$$$$/  |  $$$$/
   |__/|__/      \_______/ \_______/|__/|__/  |__/ \____  $$      |_______/  \______/    \___/  
                                                   /$$  \ $$                                    
                                                  |  $$$$$$/                                    
                                                   \______/                                     

═════════════════════════════════════════════════════════════════════════════════════════════════
              Developed by buLL, NMB & GG.G | Crypto Trading Bot v1.0 (ccxt, pandas)                      
═════════════════════════════════════════════════════════════════════════════════════════════════""")
    time.sleep(1.5)

try:
    # === Inicio ===
    print_start()
    log = setup_logger()
    config = get_config()

    # === Configuración desde config.json ===
    symbol = config["symbol"]
    timeframe = config["timeframe"]
    duration_hours = config["duration"]
    exchange_name = config["exchange"]
    timezone_str = config["timezone"]
    analyzer_conf = config.get("analyzer", {})
    dark_mode = analyzer_conf.get("dark_mode", False)

    # === Logs iniciales ===
    log.info(f"EXCHANGE: {exchange_name.upper()}")
    log.info(f"PAR DE TRADING: {symbol}")
    log.info(f"TEMPORALIDAD: {timeframe}")
    log.info(f"DURACION: Ultimas {duration_hours} horas")

    # === Obtener datos OHLCV ===
    df_raw = fetch_ohlcv(
        exchange_name=exchange_name,
        symbol=symbol,
        timeframe=timeframe,
        hours=duration_hours,
        tz_str=timezone_str
    )

    # === Análisis con TL Strategy ===
    df_final = analyze_dataframe(
        df_raw.copy(),
        export_csv=True,
        plot_backtest=True
    )

    # === Mostrar últimas filas con señales TL ===
    print(df_final.tail(10))

except Exception as e:
    print(f"Error: {e}")
    time.sleep(10)
