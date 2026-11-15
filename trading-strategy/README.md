# VP + Delta Scalper (TradingView)

Strategie mit **Volume (RVOL)**, **Volume Profile (POC/VAH/VAL des Vortags)** und
**Footprint-Delta** (angenähert aus Intrabar-Daten). Datei: `VP_Delta_Scalper.pine`
(Pine Script v6). Fünf Versionen sind im Einstellungsmenü wählbar.

> Kein Finanzrat. Kein getestetes Setup war nach Gebühren in der Prüfphase profitabel.

## Versionen
| Version | Idee |
|---|---|
| V1 Rejection | Preis sticht durch VAL/VAH, schließt zurück in der Value Area, Delta bestätigt oder Absorption → Ziel POC |
| V2 Breakout-Retest | Ausbruch aus der VA mit RVOL + starkem Delta, Retest der Kante → Ziel fester CRV |
| V3 Regime | Open in der VA → V1 (Rotation); Open außerhalb → nur Retests in Trendrichtung |
| V4 80%-Regel | Open außerhalb der VA, 2 Closes zurück in der VA → Ziel gegenüberliegende VA-Seite |
| V5 Fehlausbruch | Hoch über VAH, Close zurück unter VAH mit Verkaufsdelta → Ziel POC (und umgekehrt) |

## Test
- Daten: Binance BTCUSDT 1-Min, Jan 2025 – Sep 2026, Chart 3m und 5m, Delta aus 1m-Kerzen
  (gleiche Methode wie TradingViews `requestUpAndDownVolume`)
- Optimiert nur auf 2025 (~900 Zufalls-Kombinationen), geprüft auf 2026 (nicht gesehen)
- Kosten: 0,04 % Gebühr + 0,01 % Slippage je Seite; Ergebnisse in R (1R = Risiko pro Trade)

### Standard-Parameter (5m, enge Stops)
| Version | 2025 Trades / Ø R / PF | 2026 Trades / Ø R / PF |
|---|---|---|
| V1 | 245 / −0,40 / 0,61 | 137 / −0,39 / 0,62 |
| V2 | 145 / −0,40 / 0,58 | 94 / −0,57 / 0,46 |
| V3 | 353 / −0,47 / 0,53 | 210 / −0,61 / 0,41 |
Ohne Gebühren lagen V1/V2 bei PF 1,16/1,20 → die Gebühren fressen den kleinen Vorteil.

### Beste 2025-Einstellung je Version → Prüfung 2026
| Version | 2025 Ø R (PF) | 2026 Trades / Ø R / PF |
|---|---|---|
| V1 (3m) | +0,03 (1,04) | 51 / −0,25 / 0,59 |
| V2 (5m) | +0,14 (1,19) | 43 / −0,41 / 0,57 |
| V3 (3m) | −0,01 (0,99) | 49 / −0,44 / 0,40 |
| V4 (3m) | +0,01 (1,02) | 13 / −0,34 / 0,52 |
| V5 (5m) | +0,10 (1,27) | 15 / −0,02 / 0,93 |

**Fazit:** Kein robuster Vorteil auf BTC mit diesen Kosten. Die positiven 2025-Werte sind
Überoptimierung (wenige Trades, brechen 2026 ein).

## Grenzen
- Delta ist eine Annäherung aus 1m-Kerzen, **kein echter Bid/Ask-Footprint**. Echtes Tick-Delta
  (z. B. Futures mit Footprint-Daten) kann andere Ergebnisse liefern.
- Nur BTC getestet. Auf ES/NQ-Futures sind die Kosten relativ zur Bewegung deutlich kleiner.
- Pine und Python weichen leicht ab (Pine prüft CRV am Signal-Close, Python am nächsten Open).

## Nutzung in TradingView
1. Pine Editor → Inhalt von `VP_Delta_Scalper.pine` einfügen → „Zum Chart hinzufügen“
2. Chart 3m oder 5m (Intrabar-Zeiteinheit muss kleiner als der Chart sein)
3. Version wählen, im Strategy Tester Gebühren/Slippage an deinen Broker anpassen

`backtest/` enthält den Python-Nachbau (`prep.py`, `engine.py`, `sweep.py`, `oos.py`).
