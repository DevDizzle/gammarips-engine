Status: active
Type: finding
Tag: fragile-conditional
Exit-context: ONLY 3-day hold × |delta| 0.20–0.46. ZERO edge under same-day GIGO.
Source: docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md; INTELLIGENCE_BRIEF 2026-06-19; FINDINGS_LEDGER §momentum
Date: 2026-07-17

# 60-day momentum lever — the ".1 Tilt", real but fragile and exit-conditional

`BULLISH & mom_60 ≥ +0.35` was the first lever to clear the +4.11% bullish baseline AND
survive an out-of-sample split: ~+11.4%/55.9% win, marginal **+8.4pp (CI clears zero)**,
stable in both walk-forward halves (+16.9% → +7.5%). Term structure is pure momentum at all
horizons {20,60,126,189,252} with NO reversal; the tradeable horizon is the 1–3 month rip,
NOT literal year-over-year (252d collapses OOS).

SHIPPED as a **soft edge-rank pre-rank tilt** in `enrichment-trigger` (rev `00045-f89`,
`gammarips-review` PASS, `MOMENTUM_TILT` kill switch, N≥15 lock) — this is the ".1 Tilted"
in [[v7-1-tilted-gigo-live-policy]]. **BUT it has ZERO edge under the live same-day GIGO
exit** ([[v7-gigo-same-day-exit]]); the effect lives on a multi-day hold, and it decayed
+16% → +1.7% on the newest slice. Treat as **proposer-only / fragile**: never load-bearing
for a same-day trade; a forward 3-day label arm is accruing confirmation.
