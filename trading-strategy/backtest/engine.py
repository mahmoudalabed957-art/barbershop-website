"""Backtest-Engine, bildet die Pine-Strategie 1:1 nach.
Signal am Bar-Close, Einstieg am Open des nächsten Bars (TradingView-Standard).
Stop & Ziel intrabar; wenn beide im selben Bar möglich -> Stop zuerst (konservativ)."""
import numpy as np, pandas as pd

DEF = dict(
    version=1, rows=100, va_pct=0.70,
    sess_start=7, sess_end=20,          # UTC-Stunden für Einstiege
    rvol_len=20, atr_len=14,
    # V1 Rejection
    v1_dr=0.15, v1_absorb_rvol=1.5, v1_rvol_min=1.0, v1_minrr=1.5, v1_closepos=0.5,
    # V2 Breakout+Retest
    bo_rvol=1.5, bo_dr=0.25, arm_bars=12, retest_buf=0.1, v2_rr=2.0,
    stop_buf=0.1, min_risk_pct=0.10, max_bars=36,
    max_trades_day=4, day_loss_r=-2.0,
    fee=0.0004, slip=0.0001, cost_abs=0.0, flat_after=2,
)

def profiles(df, days, rows, va_pct):
    """POC/VAH/VAL je UTC-Tag; Volumen jedes Bars gleichmäßig über seine Range verteilt."""
    out = {}
    for day, g in df.groupby(days):
        lo, hi = g.low.min(), g.high.max()
        step = (hi - lo) / rows if hi > lo else 1.0
        vol = np.zeros(rows)
        for l, h, v in zip(g.low.values, g.high.values, g.volume.values):
            a = min(int((l - lo) / step), rows - 1); b = min(int((h - lo) / step), rows - 1)
            vol[a:b + 1] += v / (b - a + 1)
        p = int(vol.argmax()); up = dn = p; acc = vol[p]; tot = vol.sum()
        while acc < va_pct * tot and (up < rows - 1 or dn > 0):
            vu = vol[up + 1] if up < rows - 1 else -1
            vd = vol[dn - 1] if dn > 0 else -1
            if vu >= vd: up += 1; acc += vu
            else: dn -= 1; acc += vd
        out[day] = (lo + (p + .5) * step, lo + (up + 1) * step, lo + dn * step)
    return out

def run(df, **kw):
    P = {**DEF, **kw}
    days = pd.DatetimeIndex(df["day"]) if "day" in df else df.index.floor("D")
    prof = profiles(df, days, P["rows"], P["va_pct"])
    ud = days.unique()
    prev = {ud[i]: prof[ud[i - 1]] for i in range(1, len(ud))}
    o, h, l, c, v, dl = (df[k].values for k in ("open", "high", "low", "close", "volume", "delta"))
    hour = df["hr"].values if "hr" in df else df.index.hour.values
    rvol = (df.volume / df.volume.rolling(P["rvol_len"]).mean()).values
    dr = np.where(v > 0, dl / np.where(v > 0, v, 1), 0)
    tr = np.maximum(df.high - df.low, np.maximum((df.high - df.close.shift()).abs(), (df.low - df.close.shift()).abs()))
    atr = tr.ewm(alpha=1 / P["atr_len"], adjust=False).mean().values
    rng = h - l; cpos = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), .5)
    dv = days.values
    trades = []; pos = None; pending = None
    armL = armS = -10**9; reentL = [False]; reentS = [False]; day_n = 0; day_r = 0.0; cur_day = None; day_open_loc = 0
    for i in range(1, len(df)):
        d = dv[i]
        if d != cur_day:
            cur_day = d; reentL = [False]; reentS = [False]; day_n = 0; day_r = 0.0; armL = armS = -10**9
            lv = prev.get(days[i])
            if lv: day_open_loc = 1 if o[i] > lv[1] else (-1 if o[i] < lv[2] else 0)
        lv = prev.get(days[i])
        # 1) pending Einstieg am Open
        if pending is not None and pos is None:
            dirn, stop, tgt_kind, tgt, rr = pending; e = o[i]
            risk = (e - stop) * dirn
            ok = risk > 0 and risk / e * 100 >= P["min_risk_pct"]
            if ok and tgt_kind == "level":
                ok = (tgt - e) * dirn >= rr * risk
            elif ok:
                tgt = e + dirn * rr * risk
            if ok:
                pos = dict(dir=dirn, entry=e, stop=stop, tgt=tgt, risk=risk, i0=i, t=df.index[i], day=dv[i]); day_n += 1
        pending = None
        # 2) Position managen
        if pos is not None:
            dirn = pos["dir"]; ex = None
            hit_stop = l[i] <= pos["stop"] if dirn > 0 else h[i] >= pos["stop"]
            hit_tgt = h[i] >= pos["tgt"] if dirn > 0 else l[i] <= pos["tgt"]
            if hit_stop: ex = pos["stop"] if (o[i] - pos["stop"]) * dirn > 0 else o[i]
            elif hit_tgt: ex = pos["tgt"] if (pos["tgt"] - o[i]) * dirn > 0 else o[i]
            elif i - pos["i0"] >= P["max_bars"] or hour[i] >= P["sess_end"] + P["flat_after"] or dv[i] != pos["day"]:
                ex = c[i]
            if ex is not None:
                cost = (pos["entry"] + ex) * (P["fee"] + P["slip"]) + 2 * P["cost_abs"]
                r = ((ex - pos["entry"]) * dirn - cost) / pos["risk"]
                trades.append(dict(t=pos["t"], dir=dirn, r=r, bars=i - pos["i0"], ver=pos.get("v")))
                day_r += r; pos = None
            continue
        if lv is None or np.isnan(rvol[i]): continue
        poc, vah, val = lv
        # Breakout-Arming (V2/V3)
        if c[i] > vah and c[i - 1] <= vah and rvol[i] >= P["bo_rvol"] and dr[i] >= P["bo_dr"]: armL = i
        if c[i] < val and c[i - 1] >= val and rvol[i] >= P["bo_rvol"] and dr[i] <= -P["bo_dr"]: armS = i
        if not (P["sess_start"] <= hour[i] < P["sess_end"]): continue
        if day_n >= P["max_trades_day"] or day_r <= P["day_loss_r"]: continue
        ver = P["version"]
        sig = None
        # --- V1: Rejection an VAL/VAH mit Delta-Bestätigung oder Absorption
        def v1():
            if rvol[i] < P["v1_rvol_min"]: return None
            if l[i] <= val < c[i] < poc and cpos[i] >= P["v1_closepos"] and \
               (dr[i] >= P["v1_dr"] or (dr[i] < 0 and rvol[i] >= P["v1_absorb_rvol"])):
                return (1, l[i] - P["stop_buf"] * atr[i], "level", poc, P["v1_minrr"])
            if h[i] >= vah > c[i] > poc and cpos[i] <= 1 - P["v1_closepos"] and \
               (dr[i] <= -P["v1_dr"] or (dr[i] > 0 and rvol[i] >= P["v1_absorb_rvol"])):
                return (-1, h[i] + P["stop_buf"] * atr[i], "level", poc, P["v1_minrr"])
        # --- V2: Retest nach Ausbruch
        def v2(allowL=True, allowS=True, forceL=False, forceS=False):
            buf = P["retest_buf"] * atr[i]
            if allowL and (forceL or 0 < i - armL <= P["arm_bars"]) and l[i] <= vah + buf and c[i] > vah and dr[i] > 0:
                return (1, min(l[i], vah) - P["stop_buf"] * atr[i], "rr", None, P["v2_rr"])
            if allowS and (forceS or 0 < i - armS <= P["arm_bars"]) and h[i] >= val - buf and c[i] < val and dr[i] < 0:
                return (-1, max(h[i], val) + P["stop_buf"] * atr[i], "rr", None, P["v2_rr"])
        # --- V4: 80%-Regel (Open außerhalb VA, 2 Closes zurück in VA -> Ziel andere VA-Seite)
        def v4():
            if day_open_loc == -1 and c[i] > val and c[i-1] > val and not reentL[0] and dr[i] > 0:
                reentL[0] = True
                return (1, min(l[i], l[i-1]) - P["stop_buf"] * atr[i], "level", vah, P["v1_minrr"])
            if day_open_loc == 1 and c[i] < vah and c[i-1] < vah and not reentS[0] and dr[i] < 0:
                reentS[0] = True
                return (-1, max(h[i], h[i-1]) + P["stop_buf"] * atr[i], "level", val, P["v1_minrr"])
        # --- V5: Fehlausbruch: Hoch über VAH (in letzten N Bars), Close zurück unter VAH, Delta negativ
        def v5():
            lb = max(0, i - P["arm_bars"])
            if h[lb:i+1].max() > vah and c[i] < vah and c[i-1] >= vah and dr[i] <= -P["v1_dr"] and rvol[i] >= P["v1_rvol_min"]:
                return (-1, h[lb:i+1].max() + P["stop_buf"] * atr[i], "level", poc, P["v1_minrr"])
            if l[lb:i+1].min() < val and c[i] > val and c[i-1] <= val and dr[i] >= P["v1_dr"] and rvol[i] >= P["v1_rvol_min"]:
                return (1, l[lb:i+1].min() - P["stop_buf"] * atr[i], "level", poc, P["v1_minrr"])
        if ver == 1: sig = v1()
        elif ver == 4: sig = v4()
        elif ver == 5: sig = v5()
        elif ver == 2: sig = v2()
        elif ver == 3:   # Regime nach Eröffnungslage (Dalton): innen -> Rotation, außen -> Trend
            if day_open_loc == 0: sig = v1() or v2()
            elif day_open_loc == 1: sig = v2(True, False, forceL=True)
            else: sig = v2(False, True, forceS=True)
        if sig: pending = sig
    return pd.DataFrame(trades)

def stats(t):
    if len(t) == 0: return dict(n=0)
    r = t.r.values; eq = np.cumsum(r); dd = (eq - np.maximum.accumulate(np.r_[0, eq])[1:]).min()
    w = r[r > 0].sum(); ls = -r[r < 0].sum()
    return dict(n=len(r), win=round((r > 0).mean() * 100, 1), avgR=round(r.mean(), 3),
                totR=round(r.sum(), 1), PF=round(w / ls, 2) if ls else np.inf, maxDD=round(dd, 1))
