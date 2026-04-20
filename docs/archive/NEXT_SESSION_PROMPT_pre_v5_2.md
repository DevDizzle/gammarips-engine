# Next Session Prompt — Pick Up Cold

> **Last updated: 2026-04-16. V4 is the only active strategy. V3 is retired.**

---

## Current state

V4 ("whale following") has been live since 2026-04-12. V3 scheduler jobs should be paused; V3 services are idle but deployed. All forward data collection runs through V4.

### V4 infrastructure

| Component | Service / Table | URL / Schedule |
|---|---|---|
| Enrichment service | `enrichment-trigger` | `https://enrichment-trigger-406581297632.us-central1.run.app` |
| Trader service | `forward-paper-trader` | `https://forward-paper-trader-406581297632.us-central1.run.app` |
| Enriched table | `overnight_signals_enriched` | — |
| Ledger table | `forward_paper_ledger` | — |
| Enrichment cron | `enrichment-trigger-daily` | 05:30 ET Mon-Fri |
| Trader cron | `forward-paper-trader-trigger` | 16:30 ET Mon-Fri |
| IV cache cron | `polygon-iv-cache-v4-daily` | 16:30 ET Mon-Fri |

### V4 policy

- **Enrichment filter:** `overnight_score >= 1 AND spread <= 10% AND directional UOA > $500K`
- **Trader filter:** None — all enriched signals execute
- **Bracket:** +40% target / -25% stop / 2-day hold / 15:00 ET entry
- **Premium flags:** Computed and stored as features, not gates

### Key tables

- `forward_paper_ledger` — active V4 ledger
- `overnight_signals_enriched` — V4 enriched signals
- `polygon_iv_history` — shared IV cache (both V3 and V4 wrote here)
- `signals_labeled_v1` — frozen research table (do not modify)

---

## What to do on pickup

### Step 1 — Verify V4 is running

```sql
-- How many V4 trades since launch?
SELECT COUNT(*) AS n_trades, MIN(entry_day) AS first, MAX(entry_day) AS last
FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY');
```

Expected: trades accumulating daily since 2026-04-14 (first automated run). If no rows, check Cloud Run logs for `forward-paper-trader`.

### Step 2 — Check trade volume

```sql
-- Daily trade counts
SELECT entry_day, COUNT(*) AS n
FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
GROUP BY entry_day ORDER BY entry_day;
```

Expected: 20-50+ trades/day with the loose gates. If significantly lower, investigate enrichment output.

### Step 3 — Run stats snapshot

```bash
python scripts/ledger_and_tracking/current_ledger_stats.py
```

Report the numbers. Track but don't panic on short-term returns — the point is data collection, not optimizing return yet.

### Step 4 — Count toward N >= 500

```sql
SELECT COUNT(*) AS total_trades, 500 - COUNT(*) AS trades_remaining
FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY');
```

If N >= 500: run Phase 2 feature importance (XGBoost/SHAP). See `docs/TRADING-STRATEGY.md` for the full methodology.
If N < 500: continue accumulating. No ML, no gate changes. Estimate time to N=500 based on daily trade rate.

---

## Hard constraints

- **Do not add execution gates.** V4's value is unfiltered data. Filters come from Phase 2 discovery.
- **Do not run ML until N >= 500.** Feature importance on small samples is noise.
- **Do not backfill.** Hedge flag can't be replicated without real-time news. Forward-only.
- **Do not rip Gemini out of enrichment.** Premium flags are features for discovery.
- **Do not treat bearish dominance as a flaw.** It reflects regime.
- **Invoke `gammarips-review` before any deploy.**

---

## Pickup prompt

> Read `NEXT_SESSION_PROMPT.md`, then run the health checks (Steps 1-4). Report numbers before deciding anything. No gate changes, no ML until N >= 500. If something is broken, fix infrastructure only.
