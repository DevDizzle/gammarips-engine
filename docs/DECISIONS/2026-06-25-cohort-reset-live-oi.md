# 2026-06-25 — Cohort reset for the live-OI floor regime (ledger truncate + cohort floor → 06-26)

Owner-directed. Same shape as the [2026-06-22 V7.1 reset](2026-06-22-v7-1-tilted-gigo-cohort-reset.md),
pulled forward so the public scorecard starts clean on the **live-OI liquidity
floor** selection regime (shipped 2026-06-25, see
[`2026-06-25-live-oi-liquidity-floor.md`](2026-06-25-live-oi-liquidity-floor.md)).

## What changed
- **`forward_paper_ledger` TRUNCATED** (3 rows). Dumped first to
  `.scratch/forward_paper_ledger_pre_2026-06-26_reset.json`:
  - `TTWO` (scan 06-18 / entry 06-22) — STOP, −31.77% (was already floor-excluded under the 06-23 cohort)
  - `VICR` (scan 06-22 / entry 06-23) — TIMEOUT, −7.18% (the lone trade the scorecard was showing)
  - `AFL`  (scan 06-23 / entry 06-24) — `INVALID_LIQUIDITY`, NULL (the illiquid pick that helped motivate the floor)
- **`LIVE_COHORT_START_DATE` `2026-06-23` → `2026-06-26`** (`signal-notifier/main.py:94`).
- **`policy_version` UNCHANGED — stays `V7_1_TILTED_GIGO`.** The live-OI floor is a
  *selection-quality* change, not new trader mechanics (entry 10:00 / +40% / −30% /
  flat 15:45 are all unchanged), so no relabel — consistent with not relabeling for
  the edge-rank cap or the momentum tilt.

## Why 06-26 is the right floor (entry-based)
The cohort floor is `WHERE DATE(entry_timestamp) >= LIVE_COHORT_START_DATE`
(`signal-notifier/main.py:1575,1668`) — **entry day, not scan_date**. So `06-26`:
- **EXCLUDES** today's `BBWI` (scan 06-24 / entry 06-25) — the last pick made under the
  OLD pipeline (07:30 cron, no live-OI floor). Its row writes at the 16:30 ET trade cron
  *today* as a **floor-excluded** ledger row (entry 06-25 < 06-26) — present in the table,
  absent from the scorecard. Cosmetic; purge later if desired (same as the 06-22 TTWO precedent).
- **INCLUDES** the first live-OI-floor pick: tomorrow's 09:45 ET run (scan 06-25 / entry 06-26).

## Scope — only signal-notifier redeployed
`LIVE_COHORT_START_DATE` lives in exactly one place (`signal-notifier/main.py:94`); the
other four services (forward-paper-trader, win-tracker, x-poster, blog-generator) filter on
`policy_version` only, which is unchanged → **no redeploy needed**. (Contrast the 06-22 reset,
which relabeled `policy_version` and therefore touched all five.)

## Steps executed
1. Dump → `TRUNCATE TABLE profitscout-fida8.profit_scout.forward_paper_ledger` (verified 0 rows).
2. `signal-notifier/main.py:94` → `2026-06-26`; `cd signal-notifier && bash deploy.sh`.
3. `POST /refresh_stats` → `cohort_stats/current` = `V7_1_TILTED_GIGO` / cohort_start `2026-06-26` / 0 trades.
4. Verified live at https://gammarips.com/scorecard (webapp reads `cohort_stats` dynamically).

Reversible: the 3 dumped rows can be reloaded; `LIVE_COHORT_START_DATE` is a one-line revert.
