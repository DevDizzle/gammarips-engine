# 2026-07-08 — Track Record moves to full-life distributions (kill the arbitrary-exit scoreboard)

**Owner call (2026-07-08, approved from mock).** The public `/scorecard` stops leading
with ROI / win-rate under the fixed same-day GIGO bracket and instead shows the
**distribution of what every surfaced contract's premium did from the morning it was
surfaced to the day it expired** — the full opportunity surface, exit left as a free
variable. This is a PRESENTATION policy change (public data exposure), not an
execution-policy change: the live V7.1 trader, tournament, and labels are untouched.

## Why

- The fixed 1-day exit is a **measurement instrument, not a strategy** (Lab-published);
  grading the pool under one arbitrary exit contradicts the product's core claim that
  the edge lives in *how* contracts are traded.
- The whole-pool composite under that exit is negative — as a headline it answers the
  wrong question. The honest, differentiated story is the two-sided distribution: the
  **ceiling** (peak premium return before expiration, strongly right-skewed) and the
  **floor** (hold-to-settlement, mostly ruinous with a fat right tail). The product's
  thesis lives in the gap.
- The blind-buy baseline SURVIVES as prose (one sentence + the landing page's honesty
  section link) — it stays load-bearing for the data-not-advice posture.

## What was built

1. **Substrate — `life_*` column group on `enriched_option_outcomes`**
   (`life_status`, `life_peak_return`, `life_trough_return`, `life_expiry_return`,
   `life_daily_bar_count`, `life_sim_version='LIFE_TO_EXPIRY_V1'`, `life_labeled_at`).
   Anchor = the stored `opp_entry_price` (same 10:00 ET fill as the opp surface, so
   opp/life are one trade at two horizons). Peak/trough = minute-resolution opp
   excursion (days 1–3) ∪ Polygon **daily** bars entry_day+1 → expiration (entry-day
   daily bar excluded: it contains pre-entry prints). Expiry mark = **intrinsic at
   settlement** from `underlying_daily_bars` (not the option's last stale print).
   Labeled only once `recommended_expiration < today ET`. Implemented in
   `forward-paper-trader/main.py` (`_simulate_life_surface`, `_merge_life_rows`,
   `run_label_life_surface`, `POST /label_life_surface` — token-gated like
   `/persist_minute_paths`); daily cron `label-life-surface` 17:10 ET (after the 17:00
   labeler, before the 17:20 pool_outcomes refresh). One-shot history fill:
   `scripts/ledger_and_tracking/backfill_life_surface.py` (imports the deployed
   collector — byte-identical write paths).

2. **Aggregation — `win-tracker /pool_outcomes`** publishes a nested `life` map into
   Firestore `pool_outcomes/current`: N + coverage dates + exclusion counts,
   peak/trough/expiry quantiles, tail shares (touched ≥+40% / ≥+100%), and
   **fixed-edge histogram buckets** (peak: <5 / 5–20 / 20–40 / 40–70 / 70–100 /
   100–200 / 200+ %; expiry: ≤−90 / −90–−50 / −50–0 / 0–50 / 50–100 / 100–200 /
   200+ %). Pool-level aggregates ONLY — per-contract life paths stay in BigQuery
   (MCP-paid depth).

3. **Webapp `/scorecard`** renders the two histograms + distribution stat tiles
   (median peak, touched-+40%, touched-+100%, median drawdown) from `doc.life`;
   the ROI/win-rate tiles are removed from the page.

## Guardrails (carried from the owner-locked rules)

- **No tradeable-ROI headline, no win rate.** Distributions with N, cohort-shaped;
  the floor (hold-to-expiry) is published at equal prominence with the ceiling; peak
  figures are always framed as *potential, not a return anyone earned*.
- **Exclusions documented on-page:** NO_ENTRY (no clean 10:00 fill — the illiquid
  tail, ~28% of expired rows) and not-yet-expired contracts.
- **Pick privacy intact:** the surface is pool-level; nothing exposes the tournament
  pick or per-contract rows.
- Corporate-action edge cases (adjusted contracts) can misprice the intrinsic expiry
  mark for rare rows; peak/trough come from the option's own prints and are unaffected.
  Accepted as research-grade caveat; `life_status` isolates failures.

## Rollout order (data before render)

DDL/schema-ensure → history backfill (~2,300 expired rows) → deploy fpt + scheduler →
deploy win-tracker + refresh doc → webapp PR. `gammarips-review` gated the engine
changes and the webapp change separately.
