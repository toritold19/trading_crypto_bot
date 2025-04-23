import pandas as pd

def squeeze_momentum(df, length=20):
    """
    Calcula el Squeeze Momentum similar a LazyBear.
    """
    highest_high = df['high'].rolling(window=length).max()
    lowest_low = df['low'].rolling(window=length).min()
    sma = df['close'].rolling(window=length).mean()
    avg = (highest_high + lowest_low) / 2
    linreg = (df['close'] - ((avg + sma) / 2)).rolling(window=length).apply(
        lambda x: pd.Series(x).dot(range(length)) / (length * (length - 1) / 2), raw=True
    )
    return linreg.fillna(0)