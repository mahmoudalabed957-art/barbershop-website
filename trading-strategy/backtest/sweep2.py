"""Zufalls-Sweep auf In-Sample, danach Top-Konfigurationen Out-of-Sample.
Aufruf: python3 sweep2.py <markt> <IS-Ende> <N> [check-markt]"""
import pandas as pd, numpy as np, engine, random, sys
from multiprocessing import Pool
from mkt import M, BASE
mk, split, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); chk = sys.argv[4] if len(sys.argv) > 4 else None
random.seed(7)
DATA = {tf: pd.read_parquet(f"{mk}_{tf}.parquet") for tf in ("3min", "5min")}
SESS = {"nas": [(9.5, 11.0), (9.5, 12.0), (9.5, 15.5)], "nq": [(9.5, 11.0), (9.5, 12.0), (9.5, 15.5)],
        "xau": [(3.0, 12.0), (8.0, 12.0), (3.0, 16.0)], "gc": [(3.0, 12.0), (8.0, 12.0), (3.0, 16.0)]}[mk]
GRID = dict(tf=["3min", "5min"], version=[1, 2, 3, 4, 5], sess=list(range(len(SESS))),
            min_risk_pct=[0.05, 0.1, 0.15, 0.25], stop_buf=[0.1, 0.3, 0.5], v1_minrr=[1.0, 1.5, 2.0],
            v1_dr=[0.1, 0.2, 0.3], v1_rvol_min=[0.8, 1.2], bo_rvol=[1.2, 1.5, 2.0], bo_dr=[0.15, 0.3],
            v2_rr=[1.5, 2, 3], max_bars=[24, 48], arm_bars=[6, 12, 24])
def params(c):
    p = {k: v for k, v in c.items() if k not in ("tf", "sess")}
    s0, s1 = SESS[c["sess"]]
    return {**BASE, **M[mk], **p, "sess_start": s0, "sess_end": s1}
def one(c):
    d = DATA[c["tf"]]; p = params(c)
    a = engine.stats(engine.run(d[:split], **p)); b = engine.stats(engine.run(d[split:].iloc[1:], **p))
    return {**c, **{"is_" + k: v for k, v in a.items()}, **{"oos_" + k: v for k, v in b.items()}}
if __name__ == "__main__":
    keys = list(GRID)
    combos = [dict(zip(keys, [random.choice(GRID[k]) for k in keys])) for _ in range(N)]
    with Pool() as pool: res = pd.DataFrame(pool.map(one, combos))
    res.to_csv(f"sweep_{mk}.csv", index=False)
