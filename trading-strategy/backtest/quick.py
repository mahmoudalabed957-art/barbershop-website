import pandas as pd, sys, engine
tf = sys.argv[1]
df = pd.read_parquet(f"btc_{tf}.parquet")
IS = df[:"2025-12-31"]; OOS = df["2026-01-01":]
for v in (1, 2, 3):
    for name, d in (("2025", IS), ("2026", OOS)):
        print(tf, "V%d" % v, name, engine.stats(engine.run(d, version=v)))
