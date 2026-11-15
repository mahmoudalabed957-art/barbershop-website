"""NQ/Gold-Daten laden. Handelstag = CME-Session ab 18:00 New York (wie timeframe.change('D') in TradingView)."""
import pandas as pd, numpy as np, glob
from prep import resample
def delta_tv(df):
    d = np.sign(df.close - df.open); d2 = np.sign(df.close - df.close.shift())
    d = d.where(d != 0, d2).replace(0, np.nan).ffill().fillna(1)
    df["delta"] = d * df.volume; return df
def load(path_or_glob, tcol="datetime", naive_utc=True):
    files = sorted(glob.glob(path_or_glob))
    df = pd.concat([pd.read_csv(f) for f in files])
    t = pd.to_datetime(df[tcol], utc=True) if naive_utc else pd.to_datetime(df[tcol])
    df = df[["open","high","low","close","volume"]].set_index(t).sort_index()
    df = df[~df.index.duplicated()]; df = df[df.volume > 0]
    return delta_tv(df)
def finish(m1, name):
    for tf in ("3min", "5min"):
        r = resample(m1, tf)
        ny = r.index.tz_convert("America/New_York")
        r["day"] = (ny + pd.Timedelta(hours=6)).normalize().tz_localize(None)
        r["hr"] = ny.hour + ny.minute / 60
        r.to_parquet(f"{name}_{tf}.parquet")
    print(name, m1.index[0], m1.index[-1], len(m1))
D = "/home/user/data/"
finish(load(D + "Gold-XAUUSD-1m-2020-2025-Historical-Data/XAUUSD/1m/*/*/*.csv", "datetime_utc"), "xau")
finish(load(D + "nas/NAS100_1m.csv"), "nas")
finish(load(D + "cme/NQ/NQ_1min_*.csv"), "nq")
finish(load(D + "cme/GC/GC_1min_*.csv"), "gc")
