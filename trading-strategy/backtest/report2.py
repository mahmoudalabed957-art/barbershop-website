import pandas as pd, sys
mk, minn = sys.argv[1], int(sys.argv[2])
r = pd.read_csv(f"sweep_{mk}.csv"); r = r[r.is_n >= minn]
pd.set_option("display.width", 250)
cols = ["tf","sess","min_risk_pct","stop_buf","v1_minrr","v1_dr","v1_rvol_min","bo_rvol","bo_dr","v2_rr","max_bars","arm_bars","is_n","is_avgR","is_PF","oos_n","oos_avgR","oos_PF","oos_maxDD"]
for v in (1,2,3,4,5):
    s = r[r.version == v].sort_values("is_avgR", ascending=False)
    if not len(s): continue
    top = s.head(10)
    print(f"V{v}: {len(s)} Konfig., IS positiv {(s.is_avgR>0).mean()*100:.0f}% | OOS positiv (alle) {(s.oos_avgR>0).mean()*100:.0f}% | Top10-IS -> OOS Ø avgR {top.oos_avgR.mean():.3f}, positiv {(top.oos_avgR>0).sum()}/10")
    print(s.head(3)[cols].to_string(index=False))
