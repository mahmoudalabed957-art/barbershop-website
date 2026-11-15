import pandas as pd, engine
r = pd.read_csv("sweep_is45.csv"); r = r[r.is_n >= 30].sort_values("is_avgR", ascending=False)
D = {tf: pd.read_parquet(f"btc_{tf}.parquet")["2026-01-01":] for tf in ("3min","5min")}
cols = ["version","min_risk_pct","stop_buf","v1_minrr","v1_dr","v1_rvol_min","bo_rvol","bo_dr","v2_rr","max_bars","arm_bars"]
for v in (4,5):
    for _, row in r[r.version==v].head(4).iterrows():
        p = {k: row[k] for k in cols}; p["version"]=int(p["version"]); p["max_bars"]=int(p["max_bars"]); p["arm_bars"]=int(p["arm_bars"])
        print(v, row.tf, "IS avgR", row.is_avgR, "| OOS", engine.stats(engine.run(D[row.tf], **p)))
