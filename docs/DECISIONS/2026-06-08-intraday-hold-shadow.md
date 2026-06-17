# 2026-06-08 — Intraday-hold shadow (day-trade the Tournament pick)

**Status:** built, pending `gammarips-review` + owner deploy go. Research-only; changes NO execution policy.

## Question
Does this signal's edge survive a same-day day-trade? The live strategy enters the Tournament pick at 10:00 ET and holds 3 trading days with a −60%/+80% bracket. Owner asked: what if we just **get in at 10:00 ET and get out flat at 15:45 ET the same day** — no stop, no 3-day hold? (Owner's framing: PDT/day-trade restrictions are no longer a blocker. Noted; irrelevant to a paper research shadow either way — and the live PDT/margin rule should be reconfirmed before any real day-trading.)

This is a **hold-period** experiment, orthogonal to the [top-score selection shadow](2026-06-08-topscore-shadow-tracker.md). Together the two shadows complete a **2×2 matrix** — {Tournament, top-score} × {3-day, intraday} — so we have 4 experiments running:

| | 3-day hold | intraday flat (10:00→15:45) |
|---|---|---|
| **Tournament pick** | live ledger (also mirrored in `paper_shadow_topscore`) | `paper_shadow_intraday` arm=TOURNAMENT |
| **Top-score pick** | `paper_shadow_topscore` arm=TOP_SCORE | `paper_shadow_intraday` arm=TOP_SCORE |

## What it does
Each HAS_PICK day, `forward-paper-trader/main.py:_write_intraday_shadow` records **both** picks day-traded — TOURNAMENT and TOP_SCORE (2 rows/day, `arm` column):
- **Entry:** reuses each pick's already-simulated 10:00 ET fill — the live record's `entry_price` for TOURNAMENT, and the top-score record's `entry_price` (returned by `_write_topscore_shadow`, simulated by the same `_simulate_contract`) for TOP_SCORE. So it NEVER re-simulates entry and never touches the live path. The top-score selection is computed once and shared between the 3-day topscore shadow and this intraday shadow.
- **Exit:** first option print at-or-after **15:45 ET on entry_day** for that pick's contract, marked at the bar close, no slippage (mirrors the live TIMEOUT convention). If the contract stopped printing before 15:45, falls back to the last earlier same-day print and flags `intraday_illiquid=True`.
- `intraday_return_pct = (exit − entry) / entry`. No stop/target.
- Each row also stores that SAME pick's live **3-day** bracket result (`hold_3day_return_pct`, `hold_3day_exit_reason`) plus `same_pick` (top-score ticker == tournament ticker), for self-contained side-by-side and cross views.
- Each arm degrades independently: if the top-score record is unavailable (its shadow skipped/failed), the TOURNAMENT arm still writes.

Written in the same arrears invocation as the live trade (the entry-day bars are long settled by the day-3 exit cron). Best-effort: the whole body is wrapped and can NEVER raise into or alter the live return. Two extra Polygon minute-bar fetches per day (one per arm's contract).

## Why it can't be backtested for free
Unlike the top-score baseline (the labels already carried 3-day option PnL), the intraday question needs **minute-level option bars for entry-day 10:00→15:45**, which the labels don't contain. So this is a **forward shadow** (a historical replay fetching intraday bars is possible later if a faster read is wanted).

## Hard isolation
New table `profitscout-fida8.profit_scout.paper_shadow_intraday` (distinct from `forward_paper_ledger_intraday`, the live MTM table). Written ONLY by `_write_intraday_shadow`. NEVER `forward_paper_ledger` / `current_ledger_stats` / Firestore `todays_pick` / `signal_performance` / webapp / blog. `gammarips.com/scorecard` is unaffected (fed by `forward_paper_ledger` WHERE `policy_version='V6_TOURNAMENT'`). DDL: `scripts/ledger_and_tracking/create_paper_shadow_intraday.py`. Read: `scripts/ledger_and_tracking/shadow_intraday_compare.py`.

## Scope / limits
- Runs on HAS_PICK days; each arm needs its pick's real 10:00 `entry_price` (skips INVALID_LIQUIDITY / unsimulable arms independently).
- Up to two extra Polygon minute-bar fetches per day (one per arm's contract, entry_day only) — on top of the topscore 3-day shadow's fetches. Best-effort, so a cron timeout truncates the shadow, never the live ledger.
- **Decision threshold: N≥15 paired closes** before reading anything into intraday-vs-3day or the tournament-vs-top-score intraday cross.
