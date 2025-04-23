import time
from core.fetcher import fetch_ohlcv
from core.analyzer import analyze_dataframe, print_analysis_table
from utils.logger import setup_logger
from utils.config import get_config

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

# === Logs iniciales ===
log.info(f"EXCHANGE: {exchange_name.upper()}")
log.info(f"PAR DE TRADING: {symbol}")
log.info(f"TEMPORALIDAD: {timeframe}")
log.info(f"DURACIÓN: Últimas {duration_hours} horas")

# === Obtener datos OHLCV ===
df_raw = fetch_ohlcv(
    exchange_name=exchange_name,
    symbol=symbol,
    timeframe=timeframe,
    hours=duration_hours,
    tz_str=timezone_str
)

# === Análisis según config.json (heikin/tradicional, CSV, etc.) ===
df_final = analyze_dataframe(df_raw.copy(), export_csv=True)
print_analysis_table(df_final, tipo=config["analyzer"].get("candle_type", "Tradicional"))