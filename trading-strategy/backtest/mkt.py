"""Markt-Einstellungen: Kosten je Seite in Punkten, Session in New-York-Zeit."""
# NQ: 1 Tick Slippage (0,25) + ~2,5$ Kommission/Seite (=0,125 Pkt) ; NAS100-CFD: ~1 Pkt Spread
# Gold GC: 1 Tick (0,1) + ~2,5$/Seite (=0,025) ; XAUUSD-CFD: ~0,25$ Spread
M = {
  "nas": dict(cost_abs=0.5,   sess_start=9.5, sess_end=12.0, flat_after=1),
  "nq":  dict(cost_abs=0.375, sess_start=9.5, sess_end=12.0, flat_after=1),
  "xau": dict(cost_abs=0.15,  sess_start=3.0, sess_end=12.0, flat_after=1),
  "gc":  dict(cost_abs=0.125, sess_start=3.0, sess_end=12.0, flat_after=1),
}
BASE = dict(fee=0.0, slip=0.0)
