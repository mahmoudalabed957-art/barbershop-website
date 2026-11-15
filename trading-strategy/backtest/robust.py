"""Nachbarschaftstest: jeden Parameter einzeln eine Stufe variieren -> bleibt es positiv?"""
import pandas as pd, engine, sys, json
from mkt import M, BASE
mk, split, chk = sys.argv[1], sys.argv[2], sys.argv[3]
base = json.loads(sys.argv[4]); tf = base.pop("tf")
d = pd.read_parquet(f"{mk}_{tf}.parquet"); c = pd.read_parquet(f"{chk}_{tf}.parquet")
def ev(p):
    P = {**BASE, **M[mk], **p}
    a = engine.stats(engine.run(d[:split], **P)); b = engine.stats(engine.run(d[split:].iloc[1:], **P))
    C = engine.stats(engine.run(c, **{**BASE, **M[chk], **p}))
    return f"IS {a['n']:3d} {a['avgR']:+.3f} PF {a['PF']:.2f} | OOS {b['n']:3d} {b['avgR']:+.3f} PF {b['PF']:.2f} DD {b['maxDD']} | {chk} {C.get('n',0):3d} {C.get('avgR',0):+.3f} PF {C.get('PF',0)}"
print("BASIS            ", ev(base))
VAR = dict(min_risk_pct=[0.05, 0.15], stop_buf=[0.3], v1_minrr=[1.5, 2.5], v1_dr=[0.05, 0.2], v1_rvol_min=[1.0, 1.2],
           v1_absorb_rvol=[1.2, 2.0], v1_closepos=[0.4, 0.6], max_bars=[36, 48], rows=[70, 150], bo_rvol=[1.2, 2.0])
for k, vs in VAR.items():
    for v in vs: print(f"{k}={v:<10}", ev({**base, k: v}))
