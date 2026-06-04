# 2026-06-04 — Pick-pipeline bug-hunt fixes

A multi-agent adversarial audit (every finding re-verified against code + BQ data) surfaced 16 confirmed bugs silently corrupting picks. 13 fixed below; 3 deferred (need a new data source / schema). Trigger: the OKTA $127 untradeable-ghost pick.

## Fixed
| # | Sev | File | Fix |
|---|---|---|---|
| 1 | CRITICAL | `polygon_client.py:_extract_best_price_fields` | **Root cause.** Stopped substituting day LOW/HIGH for missing bid/ask — that produced fake/exactly-0% spreads on ~43% of picks (718/1815 rows = 0.0). Missing quote → bid/ask None → spread NULL, not synthetic. `_best_contract` already drops no-quote contracts, so the chosen contract now carries a REAL spread. |
| 2 | HIGH | `overnight_scanner.py:_score_ticker` | Smart-money divergence flip now resolves **before** the conviction sub-scores (Signals 1-4 read `use_call`). Previously flipped names (institutions fading the tape) were scored on the abandoned side → ~87% fell below MIN_SCORE. Forward-only. |
| 5 | HIGH | `signal-judge/app/agent.py` | `STALE_FIELDS_BLOCKLIST` strips the still-stale `recommended_volume`/`recommended_oi`/V-OI ratios from the judge prompt. `recommended_spread_pct` is NO LONGER blocked — it's real after #1, so the judge weighs it. |
| 6/7/10 | HIGH/MED | `signal-notifier/main.py` | Fallback moneyness band re-applied (was dead code → bypassed `df.iloc[0]` could be deep-ITM); stale docstrings claiming dead gates rewritten to tournament reality; dead `OI_MIN`/`VOL_MIN`/`ACTIVE_DAYS_MIN` removed. |
| 8 | HIGH | `enrichment-trigger.py:fetch_technicals_*` | **Lookahead.** Bar window was `date.today()` (enrichment run date) not `scan_date`; post-open runs leaked the next day's bar into the features. Now bounded to scan_date + defensive `df[date <= scan_date]`. |
| 9/12/13 | MED | `forward-paper-trader/main.py` | Symmetric exit slippage + gap-through; stale-TIMEOUT guard (`STALE_NO_TIMEOUT_PRINT`); late/pre-market fill guard (`late_fill_minutes`, `illiquid_exit`). Removed upward EV bias. New nullable cols. |
| 11 | MED | `signal-judge/app/agent.py` | Empty LLM batch no longer silently drops ≤10 candidates — members re-queue; >50% batch-failure aborts the bracket (consensus carries). |
| 14 | MED | `signal-judge/app/tools.py` | `in_top_5` now a real top-5 (by advancement), not every round-2 survivor. |
| 15 | LOW | `enrichment-trigger.py:compute_risk_fields` | `overnight_score` no longer defaults to a passing `5` (→ 0, fail-safe). |
| 16 | LOW | `overnight_scanner.py:_best_contract` | Greeks store RAW with None preserved — `delta` no longer coerces NULL→0.0; true 0.0 no longer dropped to None. |

**Consequence of #1:** enrichment spread gate loosened `0.08 → 0.30` (it was filtering on FAKE 0% spreads; real spreads are wider; the scanner picks the tightest liquid strike and the judge now sees the real spread). NULL spread fails closed.

## Deferred (need a point-in-time data source / schema — separate pass)
- **#3 OI frozen** — snapshot `open_interest` is prior-session OCC settle (static all session, identical for weeks; 32% of picks OI=0). Used in the scanner's contract scorer (relative OI across strikes is still directionally valid) and the V/OI "unusual" ratio (the divisor is stale). The judge no longer sees OI (#5). True day-of OI needs Polygon flat files.
- **#4 volume frozen** — snapshot `volume` is cumulative session that freezes post-close; a one-night sweep scores "high volume" for nights after. Judge no longer sees it (#5). PIT fix = day-bar (`/v2/aggs`) per scan_date for the recommended contract.
- **#15 full** — propagate NULL + an `under_enriched` flag (needs a schema add) instead of mid-range defaults for rsi/atr/catalyst/reversal.

## Status
Code fixed + py_compile clean. Pending: a confirmation audit pass, then `gammarips-review` for forward-paper-trader + signal-notifier, then deploy of the 5 touched services (overnight-scanner, enrichment-trigger, signal-judge, signal-notifier, forward-paper-trader).
