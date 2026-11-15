"""Lädt BTCUSDT 1m (Binance), berechnet Intrabar-Delta wie TradingView
(ta.requestUpAndDownVolume) und resampled auf Chart-Zeiteinheit."""
import pandas as pd, numpy as np, sys
SRC = "/home/user/alessiostomeo/btc-cycle-data/binance/1min/BTCUSDT_binance_1min_{}.csv.gz"

def load_1m():
    df = pd.concat([pd.read_csv(SRC.format(y), usecols=[0,1,2,3,4,5]) for y in (2025, 2026)])
    df["t"] = pd.to_datetime(df["datetime_utc"], utc=True)
    df = df.drop(columns="datetime_utc").set_index("t").sort_index()
    df = df[~df.index.duplicated()]
    # TradingView-Logik: close>open -> Kaufvolumen, close<open -> Verkauf,
    # sonst Vergleich mit vorherigem Close, sonst Richtung des Vorbars
    d = np.sign(df.close - df.open)
    d2 = np.sign(df.close - df.close.shift())
    d = d.where(d != 0, d2).replace(0, np.nan).ffill().fillna(1)
    df["delta"] = d * df.volume
    return df

def resample(df, tf):
    r = df.resample(tf, label="left", closed="left").agg(
        open=("open","first"), high=("high","max"), low=("low","min"),
        close=("close","last"), volume=("volume","sum"), delta=("delta","sum")).dropna()
    return r

if __name__ == "__main__":
    m1 = load_1m()
    print(m1.index[0], m1.index[-1], len(m1))
    for tf in ("3min", "5min"):
        resample(m1, tf).to_parquet(f"btc_{tf}.parquet")
    m1.to_parquet("btc_1min.parquet")
