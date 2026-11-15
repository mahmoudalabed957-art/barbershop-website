import pandas as pd, engine, numpy as np
df = pd.read_parquet("btc_5min.parquet")[:"2025-12-31"]
for v in (1,2,3):
    print("V%d gross" % v, engine.stats(engine.run(df, version=v, fee=0, slip=0)))
    print("V%d maker 0.02" % v, engine.stats(engine.run(df, version=v, fee=0.0002, slip=0)))
