Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: compares 3-day +80/−60 bracket vs same-day GIGO on 1,375 fills (846 BULLISH), 2% slippage/side
Source: docs/DECISIONS/2026-06-17-v7-intraday-bracket.md; backtesting_and_research/exit_velocity_sweep.py
Date: 2026-07-17

# The exit lever is SAME-DAY, not the target magnitude

The exit-velocity sweep re-replayed the 1,375 FILLED fills under a grid of exit policies on
the same cached minute bars, charging 2% slippage per side, with day-level bootstrap CIs
(~33 effective scan-dates). Findings:
- Every H1 target from +30% to "let it ride" lands ~**+2.4–2.8%/trade** — the lever is the
  **same-day exit itself**, not the target size. A small target with a 2–3 day hold is the
  WORST policy.
- Same-day is per-trade ~tied with the 3-day hold but frees capital ~2.5× faster →
  **~3× return-per-capital-day** (+2.64% vs +0.82%) and **halves the disaster tail**
  (−34% vs −61%).
- −30% stop beats −40% on the tail; target magnitude within H1 is noise.

HONEST LIMIT: the per-trade improvement is NOT significant at the day level (CIs include 0,
single regime) — the case rests on **velocity + tail reduction**, not higher per-trade EV.
This is the evidence base for [[v7-gigo-same-day-exit]].
