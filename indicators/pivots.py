import pandas as pd
from utils.config import get_config


def is_pivot_high(series, left=None, right=None, lookback=True):
    config = get_config()
    left = left if left is not None else config.get("pivots", {}).get("left", 1)
    right = right if right is not None else config.get("pivots", {}).get("right", 1)

    result = [False] * len(series)
    max_index = len(series) - right if lookback else len(series)
    for i in range(left, max_index):
        is_high = all(series[i] > series[i - j] for j in range(1, left + 1)) and \
                  all(series[i] > series[i + j] for j in range(1, right + 1))
        result[i] = is_high
    return pd.Series(result, index=series.index)


def is_pivot_low(series, left=None, right=None, lookback=True):
    config = get_config()
    left = left if left is not None else config.get("pivots", {}).get("left", 1)
    right = right if right is not None else config.get("pivots", {}).get("right", 1)

    result = [False] * len(series)
    max_index = len(series) - right if lookback else len(series)
    for i in range(left, max_index):
        is_low = all(series[i] < series[i - j] for j in range(1, left + 1)) and \
                 all(series[i] < series[i + j] for j in range(1, right + 1))
        result[i] = is_low
    return pd.Series(result, index=series.index)
