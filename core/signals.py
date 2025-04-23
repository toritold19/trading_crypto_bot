import pandas as pd

def add_buy_sell_tl_signals(df):
    df["Buy_TL"] = False
    df["Sell_TL"] = False

    last_signal = None

    for i in range(1, len(df)):
        adx = df["ADX"].iloc[i]
        plus_di = df["+DI"].iloc[i]
        minus_di = df["-DI"].iloc[i]
        micro = df["microTrend"].iloc[i]
        macro = df["macroTrend"].iloc[i]
        sz = df["sz"].iloc[i]
        stoch_k = df["stoch_k"].iloc[i]
        stoch_d = df["stoch_d"].iloc[i]

        if pd.isna(adx) or pd.isna(plus_di) or pd.isna(minus_di) or pd.isna(sz) or pd.isna(stoch_k) or pd.isna(stoch_d):
            continue

        # BUY
        if (
            macro and micro and adx > 20 and plus_di > minus_di
            and sz > 0 and sz > df["sz"].iloc[i - 1]
            and stoch_k > stoch_d and stoch_k < 20
        ):
            if last_signal != "BUY":
                df.at[i, "Buy_TL"] = True
                last_signal = "BUY"

        # SELL
        elif (
            not macro and not micro and adx > 20 and minus_di > plus_di
            and sz < 0 and sz < df["sz"].iloc[i - 1]
            and stoch_k < stoch_d and stoch_k > 80
        ):
            if last_signal != "SELL":
                df.at[i, "Sell_TL"] = True
                last_signal = "SELL"

    df["signal_tl"] = "-"
    df.loc[df["Buy_TL"], "signal_tl"] = "BUY"
    df.loc[df["Sell_TL"], "signal_tl"] = "SELL"

    return df
