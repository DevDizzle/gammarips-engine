# DATA-CONTRACTS.md

## Purpose
Document the key data objects used by the current forward-trading workflow.

## Enriched signals table — `profitscout-fida8.profit_scout.overnight_signals_enriched`

Primary upstream table for paper-trader execution. Populated by `enrichment-trigger` (Cloud Scheduler `enrichment-trigger-daily`, 05:30 ET Mon-Fri). Enrichment gate: `overnight_score >= 1`, `recommended_spread_pct <= 0.30`, and directional UOA > $500K. ~70 tickers/day. (Spread cap loosened `0.08 → 0.30` on 2026-06-04 once `recommended_spread_pct` became the REAL quoted spread — see field-quality notes below and `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.)

**Field-quality caveats (2026-06-04 bug-hunt — read before any analysis on this table):**
- `recommended_spread_pct` is now the REAL quoted bid/ask spread: `NULL` when no live quote was available at scan time, a real fraction otherwise. Historically (~43% of older rows) it was a fake day-range/0% placeholder. Treat pre-2026-06-04 spread values as unreliable. See `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.
- `recommended_oi` and `recommended_volume` are still SESSION-FROZEN snapshots — `recommended_oi` is prior-session open interest, `recommended_volume` is the cumulative-frozen scan-session volume. Do NOT treat them as fresh, point-in-time per-`scan_date` values. The PIT fix is deferred.

All premium flags (`premium_hedge`, `premium_high_rr`, `premium_bull_flow`, `premium_bear_flow`, `premium_high_atr`, `premium_score`) are still computed and stored — they are features for post-hoc discovery, not gates.

Expected fields used by policy logic include:
- `scan_date`
- `ticker`
- `recommended_contract`
- `direction`
- `premium_score`
- `is_premium_signal`
- `recommended_volume`
- `recommended_oi`
- `recommended_dte`
- `recommended_spread_pct`
- `implied_volatility` / `recommended_iv` if available
- any market context fields needed for telemetry

**Quality-gate feature columns (added 2026-04-17, NULLABLE):**
- `volume_oi_ratio` — `recommended_volume / NULLIF(recommended_oi, 0)` at focal strike. **No longer a gate** (removed 2026-06-02; selection-gate teardown completed in V6). Retained as a descriptive feature only. Note: derived from session-frozen `recommended_volume`/`recommended_oi` (see field-quality caveats above).
- `moneyness_pct` — `abs(recommended_strike - underlying_price) / underlying_price`. **No longer a selection gate** (notifier moneyness band removed 2026-06-04 with the V6 selection-gate teardown). Retained as a descriptive/cohort feature. Falls back to Polygon scan_date close when `underlying_price` is missing.
- `vix3m_at_enrich` — FRED `VXVCLS` close at or before `scan_date`. Notifier still enforces the `VIX <= VIX3M` regime safety rail (skip day if backwardated). Fail-closed on NULL.

**Metadata columns (added 2026-06-03, NULLABLE, NON-GATING):**
- `sector` / `industry` — SIC-mapped at scan time in `overnight_scanner.py` (per-ticker Polygon detail endpoint), already present on the raw `overnight_signals` table; now carried through to the enriched table and the Firestore doc. **Read by no gate, WHERE, or ranking** — purely descriptive. Consumed only by the webapp's same-sector related-signals ranking and available for post-hoc cohort analysis. `None` on Polygon detail failures. See `docs/DECISIONS/2026-06-03-sector-persistence-and-webapp-internal-linking.md`.

Schema is ensured idempotently via `ALTER TABLE ADD COLUMN IF NOT EXISTS` on every enrichment run. Old rows retain NULL and are automatically excluded by the notifier's fail-closed filter.

## Forward ledger — `profitscout-fida8.profit_scout.forward_paper_ledger`

Active forward paper-trading ledger. Written by `forward-paper-trader/main.py:run_forward_paper_trading` via delete-then-load JSON-L. One row per `scan_date` (one-pick-per-day ledger; the trader simulates ONLY the ticker named in `todays_pick/{scan_date}`). **Mechanics (unchanged in V6):** 10:00 ET entry, −60% initial stop, trail at +30% gain / 25% off peak, +80% target, 3-day hold, 15:50 ET exit; STOP/TRAIL wins over TARGET on ambiguous bars. Rows are tagged `policy_version = 'V6_TOURNAMENT'`. **The ledger was truncated 2026-06-04** on the V6 cutover (prior `V5_4_AGENT_RANKER` rows wiped); do NOT mix V6 rows with the retired V5.4 cohort. Populated by Cloud Scheduler `forward-paper-trader-trigger` at 16:30 ET Mon-Fri. The cron resolves `scan_date` such that `exit_day = today` (walks back `HOLD_DAYS=3` trading days from today via `get_canonical_scan_date`).

**Skip rows are first-class.** When the picker abstains (`todays_pick/{scan_date}.has_pick = false`), the trader writes one ledger row with `is_skipped=true`, `skip_reason=<reason>`, and `ticker/recommended_contract/direction` all NULL. Those three columns are NULLABLE (relaxed 2026-05-15 — see `docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md`).

### Columns

**Identity:**
- `scan_date`, `ticker`, `recommended_contract`, `direction`
- `is_premium_signal`, `premium_score`

**Policy metadata:**
- `policy_version`, `policy_gate`
- `is_skipped`, `skip_reason`

**Recommended contract fields (from `overnight_signals_enriched`):**
- `recommended_dte`, `recommended_volume`, `recommended_oi`, `recommended_spread_pct`

**Regime context:**
- `VIX_at_entry` — daily VIX close on entry day. Sourced from FRED (`VIXCLS`). Telemetry only.
- `SPY_trend_state` — `"BULLISH"` or `"BEARISH"`, based on SPY close > 10-day SMA on entry day. Sourced from Polygon daily bars.
- `vix_5d_delta_entry` — VIX 5-trading-day change at entry. Positive = rising vol regime.

**Execution:**
- `entry_timestamp`, `entry_price`, `target_price`, `stop_price`
- `exit_timestamp`, `exit_reason`, `realized_return_pct`
- `exit_reason` values: `TARGET` / `STOP` / `TRAIL` / `TIMEOUT` / `STALE_NO_TIMEOUT_PRINT` (added 2026-06-04 — the 15:50 ET exit window had no print, so the position is marked at the last available bar rather than a fresh timeout fill).

**Liquidity/fill quality (added 2026-06-04, all NULLABLE):**
- `exit_slippage` — FLOAT64. Modeled slippage applied at exit; `NULL` on clean fills.
- `illiquid_exit` — BOOL. `TRUE` when the exit had to be reconstructed from a stale/illiquid book. **Exclude `illiquid_exit = TRUE` rows from EV / IC computations** — those exits are not faithfully tradeable.
- `late_fill_minutes` — FLOAT64. Minutes between the intended exit stamp and the bar actually used; `NULL` when the fill was on-time.

**Benchmarking (all FLOAT64 nullable):**
- `underlying_entry_price` — stock price at `entry_timestamp`. Polygon minute bar, at-or-after the entry stamp.
- `underlying_exit_price` — stock price at `exit_timestamp`. Polygon minute bar, at-or-before the exit stamp.
- `underlying_return` — `(underlying_exit_price / underlying_entry_price - 1) * direction_sign`. Signed so that a winning directional bet on the stock is positive.
- `spy_entry_price` — SPY price at `entry_timestamp`. Cached per `(entry_day, timeout_day)` window per trader invocation.
- `spy_exit_price` — SPY price at `exit_timestamp`.
- `spy_return_over_window` — `(spy_exit_price / spy_entry_price - 1)`. Unsigned. The noise floor for each trade.
- `hv_20d_entry` — 20-day annualized realized volatility on the underlying, computed from the trailing Polygon daily bars at entry.
- `iv_rank_entry` — queried at trade time from `polygon_iv_history` (trailing 252 trading days of ATM 30d IV on the underlying). `NULL` when the cache has fewer than 20 observations for the ticker.
- `iv_percentile_entry` — same source, complement metric.

## IV cache table — `profitscout-fida8.profit_scout.polygon_iv_history`

One row per (ticker, as_of_date). Populated daily by `forward-paper-trader/main.py:run_iv_cache_update` via the `POST /cache_iv` endpoint (Cloud Scheduler `polygon-iv-cache-daily`, 16:30 ET Mon-Fri). Watchlist = tickers seen in `overnight_signals_enriched` in the trailing 30 days.

**Clustering:** `ticker`. **Partition:** `as_of_date` (DAY).

| Column | Type | Notes |
|---|---|---|
| `ticker` | STRING REQUIRED | Underlying symbol |
| `as_of_date` | DATE REQUIRED | Snapshot date (ET close) |
| `atm_iv_30d` | FLOAT | Implied volatility of the ATM call whose expiration is closest to 30 DTE. NULL if no usable contract. |
| `dte_used` | INT64 | Actual DTE of the contract sampled (typically 28–35) |
| `strike_used` | FLOAT | Strike of the sampled contract |
| `underlying_px` | FLOAT | Underlying stock price at snapshot time |
| `contract_symbol` | STRING | Polygon contract symbol (e.g. `O:AAPL260508C00260000`) |
| `source` | STRING | `"polygon_snapshot"` |
| `fetched_at` | TIMESTAMP REQUIRED | When the row was written |

Idempotent per `as_of_date`: the endpoint issues `DELETE FROM polygon_iv_history WHERE as_of_date = CURRENT_DATE()` before appending, so re-triggering on the same day does not double-write.

## Intraday mark-to-market — `profitscout-fida8.profit_scout.forward_paper_ledger_intraday` (added 2026-05-15)

Daily EOD snapshots of open V5.4 positions. Pure observability — never feeds back into the trader's decision path. One row per open position per `snapshot_date`. Written by `forward-paper-trader/main.py:run_mark_to_market` via the `POST /mark_to_market` endpoint (Cloud Scheduler `forward-paper-trader-mtm`, 16:15 ET Mon–Fri — 15 minutes before the realized-exit cron).

**Partition:** `snapshot_date` (DAY). All non-key columns NULLABLE.

| Column | Type | Notes |
|---|---|---|
| `scan_date` | DATE REQUIRED | The pick's scan_date — FK to `forward_paper_ledger.scan_date` once the trade closes |
| `ticker` | STRING REQUIRED | Denormalized for filter speed |
| `direction` | STRING | `BULLISH` / `BEARISH` |
| `recommended_contract` | STRING | Polygon option ID (e.g. `O:HTZ260612P00005500`) |
| `entry_day` | DATE | First trading day after scan_date |
| `exit_day` | DATE | `entry_day + (HOLD_DAYS-1)` trading days |
| `snapshot_date` | DATE REQUIRED | The date this snapshot represents (today in ET when the cron fires) |
| `snapshot_ts` | TIMESTAMP REQUIRED | Exact write time |
| `trading_day_idx` | INT64 | 1, 2, or 3 — which trading day of the hold this snapshot covers (1 on entry_day, 3 on exit_day) |
| `entry_price` | FLOAT | Reconstructed entry: 10:00 ET entry-day bar close × 1.02 (mirrors trader slippage) |
| `current_mid` | FLOAT | Most recent option close in the bars-from-entry-to-today window |
| `peak_mid` | FLOAT | Max bar high over the same window |
| `unrealized_return_pct` | FLOAT | `(current_mid − entry_price) / entry_price` |
| `trail_armed` | BOOL | `peak_mid >= entry_price × 1.30` (i.e., trail trigger has been hit) |
| `underlying_close` | FLOAT | Reserved; currently NULL |
| `policy_version` | STRING | `"V5_4_AGENT_RANKER"` |

Idempotent per `snapshot_date`: `DELETE FROM forward_paper_ledger_intraday WHERE snapshot_date = CURRENT_DATE()` before append. Same write pattern as the canonical ledger.

## Firestore — `ledger_trades/{scan_date}_{ticker}` (added 2026-06-03)

Per-trade publish of the closed V5.4 cohort for the public webapp scorecard table (`/scorecard`). Written by `signal-notifier/main.py:compute_and_write_ledger_trades` alongside `cohort_stats/current`, on the same daily cron and the `/refresh_stats` endpoint. **Uses the identical cohort filter and fixed-dollar sizing as `cohort_stats/current`** (`DATE(entry_timestamp) >= LIVE_COHORT_START_DATE` AND `policy_version = 'V5_4_AGENT_RANKER'` AND `realized_return_pct IS NOT NULL` AND `entry_price > 0`; `n_contracts = GREATEST(1, ROUND(POSITION_SIZE_USD/(entry_price*100)))`), so the table rows and the aggregate tiles can never disagree. Idempotent upsert (`merge=True`) keyed by `{scan_date}_{ticker}`; non-gating, display-only. Read-only consumer; never feeds any execution gate.

### Fields
- `scan_date`, `ticker`, `direction` (`BULLISH`/`BEARISH`)
- `recommended_contract` (raw OCC) + parsed `option_type` (`CALL`/`PUT`/null), `strike` (float/null), `expiration` (ISO/null), `dte` (int/null) — parsed via `_parse_occ_contract`; null on malformed symbols
- `entry_date`, `entry_price`, `exit_date`, `hold_days`, `exit_reason` (`TARGET`/`STOP`/`TIMEOUT`/`TRAIL`)
- `return_pct` (decimal; ×100 for %), `capital_usd`, `pl_usd` (sized P&L — the per-trade summand of the tile total), `policy_gate`, `policy_version`, `as_of` (server ts)

## Firestore — `x_posts/{scan_date}_{post_type}` (added 2026-04-24)

Audit log + idempotency store for `x-poster` (Cloud Run service). One doc per published or rejected X post. Doc id pattern: `2026-04-24_signal`, `2026-04-24_standby`, `2026-04-24_teaser`, `2026-04-24_callback`, `2026-04-24_scorecard`. Scorecard thread tweets get suffixed: `..._scorecard_0`, `_1`, `_2`.

### Fields
- `scan_date` (str, YYYY-MM-DD ET)
- `post_type` (str, one of `signal|standby|teaser|report|callback|scorecard`)
- `text` (str, the canonicalized tweet body)
- `tweet_id` (str|None, X API tweet id; `dry_run_*` in DRY_RUN mode)
- `image_url` (str|None, GCS URL of generated image; currently None — bytes pass directly to Tweepy media_upload)
- `iterations` (int, how many LoopAgent iterations the writer needed)
- `error` (str|None, populated on rejected/failed posts)
- `dry_run` (bool, true if DRY_RUN env was set)
- `posted_at` (timestamp, server time)
- `thread_tweet_index` (int|None, set only for scorecard thread members)

Used by win/loss callback posts to look up the original signal post's `tweet_id` for quote-retweet via `firestore_helpers.fetch_original_tweet_id()`.

## Firestore — `blog_posts/{slug}` (added 2026-04-24, blog-generator)

Output collection for `blog-generator` ADK service. Webapp `/blog/[slug]` route renders directly from these docs. Slug is the URL-safe hyphenated title (e.g. `why-uoa-is-mostly-noise`).

### Fields
- `slug` (str)
- `title` (str)
- `description` (str, meta description)
- `markdown` (str, full post body)
- `keywords` (list[str])
- `cta` (str, CTA target — `webapp_visit` | `pro_trial` | `starter_trial`)
- `published_at` (timestamp)
- `reviewer_score` (float, holistic LLM review score)
- `iterations` (int, LoopAgent iterations used)
- `status` (str, `published` | `rejected` | `draft`)
- `reading_time_min` (int)

## Firestore — `blog_schedule/current` + `blog_config/voice_rules` (added 2026-04-24, blog-generator)

`blog_schedule/current` — single doc holding the 13-row 90-day schedule. Each row: `{slug, week_num, title_candidate, persona, keywords, cta, type, cross_channel, status}`. `status` flips `pending` → `publishing` → `published` (atomic via Firestore transaction).

`blog_config/voice_rules` — rendered output of `gammarips_content.voice_rules.render_for_prompt()`. Seeded once via `blog-generator/scripts/seed_schedule.py`.

## GCS — `gs://gammarips-x-media/` (added 2026-04-24)

| Path | Purpose |
|---|---|
| `brand_logo.jpg` | Brand mark — PIL-composited at 12% width on bottom-right of every generated image. 400×400 JPG. **Source of truth for the brand mark.** |
| `brand_ref_card.png` | Deprecated 2026-04-24. Was the webapp og-image; carried `/arena` multi-agent debate visuals which we gated noindex 2026-04-22. No longer used by image-gen pipeline. |
| `preview/` | First-round AI-generated brand cards (REJECTED by Evan as off-brand). Archive only. |
| `preview_v2/` | Second-round themed-editorial previews (signal_app, signal_nvda, teaser, standby + manual_nvda_test). Used by Evan to eyeball image-gen output before flipping DRY_RUN=false. |
| `_archive/` | Misc snapshots. |

## Current policy contract (V6 Tournament — no trader-side gates)

> The ranker is a bracket **TOURNAMENT** (`tournament_v1`, version 7, `gemini-3.1-pro-preview`) on the `signal-judge` Cloud Run service — NOT a single `judge_v6` call. The tournament seeds gated candidates into brackets and writes finalists + the winner row, encoding an ADVANCEMENT proxy in the rubric columns. The `signal_ranker_runs` trace table name is **UNCHANGED**; tournament output is mirrored into the existing `scorer_*`/`picker_*` columns at `*_prompt_version = 7` and `*_model = 'gemini-3.1-pro-preview'`. Cohort labels: `5` = two-stage Scorer→Picker, `6` = `judge_v6` single judge, `7` = tournament. The Firestore `v5_4_*` provenance keys are KEPT (name retained for continuity; do not rename). The ledger `policy_version` label is now `'V6_TOURNAMENT'`.

All signals that pass the enrichment filter (`overnight_score >= 1 AND recommended_spread_pct <= 0.30 AND directional UOA > $500K`) are simulated by the paper trader. **The `signal-notifier` selection gates were REMOVED in V6 (2026-06-04)** — the `moneyness_pct`, `volume_oi_ratio`, `recommended_dte`, `OI`, and `vol` selection filters no longer run. Only two safety rails remain in `signal-notifier`: **no earnings during the hold window** and the **`VIX <= VIX3M` regime check**. Candidate selection among the survivors is the tournament's job. Premium flags and the former-gate feature columns are still computed and stored for post-hoc discovery. See `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.

## Notes
- `VIX_at_entry`, `vix_5d_delta_entry`, and `SPY_trend_state` are retained as telemetry only. None of them gate execution.
- The `signals_labeled_v1` research table (frozen, `V3_MECHANICS_2026_04_07`) is a backfilled simulation over 1563 historical signals — it is NOT the live forward-paper ledger.
- Always write `policy_version` and `policy_gate` to ledger rows for traceability.
