import pandas as pd
from utils.config import get_config

def whale_signal(df: pd.DataFrame, column: str = "close", window: int = None, threshold: float = None) -> pd.DataFrame:
    """
    Calcula señales de Whale y Whale Invert en base al comportamiento del precio sobre una ventana.
    Usa window y threshold desde config.json si no se especifican.

    Args:
        df (pd.DataFrame): DataFrame que contiene al menos la columna de cierre.
        column (str): columna sobre la que hacer el análisis (close o ha_close).
        window (int): cantidad de períodos para el promedio local.
        threshold (float): multiplicador de la desviación estándar.

    Returns:
        pd.DataFrame: con dos nuevas columnas booleanas: is_whale, is_whale_invert.
    """
    config = get_config()
    whale_config = config.get("whale", {})
    window = window or whale_config.get("window", 6)
    threshold = threshold or whale_config.get("threshold", 2.0)

    avg = df[column].rolling(window=window).mean()
    std = df[column].rolling(window=window).std()

    df["is_whale"] = df[column] > (avg + threshold * std)
    df["is_whale_invert"] = df[column] < (avg - threshold * std)

    return df
