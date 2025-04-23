import pandas as pd

def stoch_rsi(df, rsi_period=14, k_period=3, d_period=3):
    """
    Calcula el Stochastic RSI (con %K y %D).
    """
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    stoch_k = ((rsi - rsi.rolling(window=rsi_period).min()) /
               (rsi.rolling(window=rsi_period).max() - rsi.rolling(window=rsi_period).min())) * 100
    stoch_d = stoch_k.rolling(window=d_period).mean()

    return stoch_k.fillna(0), stoch_d.fillna(0)
