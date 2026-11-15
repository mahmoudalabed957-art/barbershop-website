# VP + Delta Scalper (TradingView)

Strategie mit **Volume (RVOL)**, **Volume Profile (POC/VAH/VAL des Vortags)** und
**Footprint-Delta** (angenähert aus Intrabar-Daten). Datei: `VP_Delta_Scalper.pine`
(Pine Script v6). Fünf Versionen sind im Einstellungsmenü wählbar.

> Kein Finanzrat. Einziger vielversprechender Kandidat: **Gold (XAUUSD), V1, 5-Min-Chart** – siehe unten.
> Auf BTC und Nasdaq gab es keinen belastbaren Vorteil.

## Versionen
| Version | Idee |
|---|---|
| V1 Rejection | Preis sticht durch VAL/VAH, schließt zurück in der Value Area, Delta bestätigt oder Absorption → Ziel POC |
| V2 Breakout-Retest | Ausbruch aus der VA mit RVOL + starkem Delta, Retest der Kante → Ziel fester CRV |
| V3 Regime | Open in der VA → V1 (Rotation); Open außerhalb → nur Retests in Trendrichtung |
| V4 80%-Regel | Open außerhalb der VA, 2 Closes zurück in der VA → Ziel gegenüberliegende VA-Seite |
| V5 Fehlausbruch | Hoch über VAH, Close zurück unter VAH mit Verkaufsdelta → Ziel POC (und umgekehrt) |

## Runde 2: Gold und Nasdaq

**Daten:** XAUUSD 1-Min (Jan 2024 – Nov 2026), NAS100 1-Min (Mär – Sep 2026),
CME-Futures GC und NQ mit echtem Börsenvolumen (20. Jan – 15. Apr 2026).
Handelstag = CME-Session ab 18:00 New York. Kosten je Seite: XAUUSD 0,15 $, GC 0,125 Pkt,
NAS100 0,5 Pkt, NQ 0,375 Pkt (1 Tick Slippage + Kommission).

### Gold (XAUUSD) – optimiert auf 2024–2025, geprüft auf 2026
- 1.500 zufällige Einstellungen getestet. Bei V1 und V3 waren 59 % bzw. 70 % aller Einstellungen
  auch 2026 positiv; von den 10 besten aus 2024–25 waren je 8 auch 2026 positiv.
- **Gewählte Einstellung (Standard im Pine Script):** V1 Rejection, 5m, Einstiege 08:00–12:00 NY,
  Stop-Puffer 0,1 ATR, Min. Stop 0,1 %, Min. CRV 2,0, Delta-Ratio 0,1, Min. RVOL 0,8, Zeit-Stop 24 Bars.

| Zeitraum | Trades | Trefferquote | Ø R | PF | Max. DD |
|---|---|---|---|---|---|
| 2024 | 29 | 52 % | +0,55 | 2,04 | −5,5 R |
| 2025 | 64 | 38 % | +0,24 | 1,36 | −6,9 R |
| 2026 (Prüfung) | 54 | 35 % | +0,45 | 1,70 | −10,0 R |
| Gesamt, Kosten ×3 | 147 | 39 % | +0,25 | 1,36 | −11,4 R |

- Jede einzelne Parameter-Variation (±1 Stufe) blieb in beiden Phasen positiv.
- Long besser als Short (PF 1,8 vs. 1,4) – Gold war 2024–26 im starken Aufwärtstrend.
- Ohne die 5 besten Trades bleiben +23,7 R von +55,5 R.
- **Warnung:** Auf **GC-Futures** (gleicher Zeitraum Jan–Apr 2026) gab es nur 6 Trades, alle Verlierer,
  während XAUUSD im selben Zeitraum +18 R machte. Das Ergebnis hängt also stark von den
  Volumendaten der Quelle ab (CFD-Tick-Volumen vs. echtes Futures-Volumen).

### Nasdaq (NAS100 / NQ)
1.000 Einstellungen, optimiert Mär–Jun, geprüft Jul–Sep 2026: nur 15–50 Trades je Phase,
Ergebnisse um null, Top-Einstellungen nur zur Hälfte positiv → **kein belastbarer Vorteil**.

## Runde 1: BTC
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
   (Standard: 0,005 % je Seite für XAUUSD-CFD; bei Futures auf „pro Kontrakt“ umstellen)
4. Für Gold: Symbol XAUUSD (z. B. OANDA), 5-Min-Chart, Zeitzone America/New_York

`backtest/` enthält den Python-Nachbau: `prep.py`/`prep2.py` (Daten), `engine.py`, `sweep.py`/`sweep2.py`
(Optimierung + Prüfung), `robust.py` (Nachbarschaftstest), `mkt.py` (Kosten/Sessions je Markt).
