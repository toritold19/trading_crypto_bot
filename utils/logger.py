import logging
import os
import sys

def setup_logger(name="tradingbot", log_file="logs/bot.log", level=logging.INFO):
    # Crear carpeta de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        # Reconfigurar la salida para usar UTF-8
        console_handler.stream.reconfigure(encoding='utf-8')
        logger.addHandler(console_handler)

        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger