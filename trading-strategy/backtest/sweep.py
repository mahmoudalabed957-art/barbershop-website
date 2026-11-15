import pandas as pd, numpy as np, engine, itertools, random, sys, json
from multiprocessing import Pool
random.seed(1)
DATA = {tf: pd.read_parquet(f"btc_{tf}.parquet") for tf in ("3min","5min")}
GRID = dict(tf=["3min","5min"], version=[4,5], min_risk_pct=[0.2,0.3,0.4,0.6],
            stop_buf=[0.1,0.3,0.5], v1_minrr=[1.0,1.5,2.0], v1_dr=[0.1,0.2,0.3],
            v1_rvol_min=[0.8,1.2], bo_rvol=[1.2,1.5,2.0], bo_dr=[0.15,0.3],
            v2_rr=[1.5,2,3], max_bars=[24,48], arm_bars=[6,12,24])
def one(p):
    tf = p.pop("tf"); d = DATA[tf]
    a = engine.stats(engine.run(d[:"2025-12-31"], **p))
    return dict(tf=tf, **p, **{"is_"+k: v for k, v in a.items()})
if __name__ == "__main__":
    keys = list(GRID); combos = [dict(zip(keys, [random.choice(GRID[k]) for k in keys])) for _ in range(int(sys.argv[1]))]
    with Pool() as pool: res = pool.map(one, combos)
    pd.DataFrame(res).to_csv("sweep_is45.csv", index=False)
