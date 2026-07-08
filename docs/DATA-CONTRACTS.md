# DATA-CONTRACTS.md

## Purpose
Document the key data objects used by the current forward-trading workflow.

## Enriched signals table — `profitscout-fida8.profit_scout.overnight_signals_enriched`

Primary upstream table for paper-trader execution. Populated by `enrichment-trigger` (Cloud Scheduler `enrichment-trigger-daily`, 05:30 ET Mon-Fri). Enrichment gate: `overnight_score >= 4` (floor, raised from `>= 1` on 2026-06-05) AND directional UOA > $500K (all directions); the pool is then edge-ranked + grounded to the **top-50 BULLISH** names (`thinking_budget=0`). ~50 rows/day. **The spread gate was RETIRED 2026-06-05** — this Polygon plan serves no NBBO quotes, so `recommended_spread_pct` is permanently NULL and cannot be gated on. The enrichment write path is atomic + schema-drift-safe and must **NEVER** use `autodetect` (that mistyped all-NULL columns and broke every load 2026-07-02). See `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`.

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

Active forward paper-trading ledger. Written by `forward-paper-trader/main.py:run_forward_paper_trading` via delete-then-load JSON-L. One row per `scan_date` (one-pick-per-day ledger; the trader simulates ONLY the ticker named in `todays_pick/{scan_date}`). **Mechanics (V7.1 GIGO):** 10:00 ET entry, −30% hard stop, +40% target, same-day hold (`HOLD_DAYS=1`), flat 15:45 ET exit; **no trail** (`USE_TRAIL=False`). On ambiguous bars **TIMEOUT(15:45) > STOP > TARGET** (conservative). Rows are tagged `policy_version = 'V7_1_TILTED_GIGO'` (current cohort start 2026-06-26). **The ledger was truncated at each policy cutover** (V6 launch 2026-06-04 wiped the `V5_4_AGENT_RANKER` rows; the V7.1 relabel 2026-06-22; the live-OI-floor reset 2026-06-25); do NOT mix cohorts across `policy_version`. Populated by Cloud Scheduler `forward-paper-trader-trigger` at 16:30 ET Mon-Fri. The cron resolves `scan_date` such that `exit_day = today` (same-day hold: `exit_day = entry_day`, via `get_canonical_scan_date`).

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
- `exit_reason` values: `TARGET` / `STOP` / `TRAIL` / `TIMEOUT` / `STALE_NO_TIMEOUT_PRINT` (added 2026-06-04 — the exit window had no print, so the position is marked at the last available bar rather than a fresh timeout fill). Under V7.1 the `TIMEOUT` bar is 15:45 ET same-day; **`TRAIL` is retained but inert** (`USE_TRAIL=False`, so no V7.1 row carries it).

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

Daily EOD snapshots of open positions. Pure observability — never feeds back into the trader's decision path. **Effectively dormant under the V7.1 same-day hold** (positions never carry overnight, so there is no open position to mark the evening before exit); retained for schema stability. One row per open position per `snapshot_date`. Written by `forward-paper-trader/main.py:run_mark_to_market` via the `POST /mark_to_market` endpoint (Cloud Scheduler `forward-paper-trader-mtm`, 16:15 ET Mon–Fri — 15 minutes before the realized-exit cron).

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
| `policy_version` | STRING | `"V7_1_TILTED_GIGO"` (current; historical rows carry the cohort label live at write time) |

Idempotent per `snapshot_date`: `DELETE FROM forward_paper_ledger_intraday WHERE snapshot_date = CURRENT_DATE()` before append. Same write pattern as the canonical ledger.

## Research substrate — `profitscout-fida8.profit_scout.enriched_option_outcomes` (added 2026-06-17)

Counterfactual bracket-replay option-PnL labels over the **full** enriched BULLISH pool (~50 rows/day), so a leakage-safe label set accrues ~50x faster than the 1-pick/day ledger. Written by the `/label_enriched_pool` cron via a mechanical replay of `forward-paper-trader/main.py:_simulate_contract` (no LLM). **HARD ISOLATION: research-only** — never read or written by the Scorecard / Firestore / webapp / blog. Partitioned by `entry_day` (DAY), clustered by `ticker`. Schema source of truth: `scripts/ledger_and_tracking/create_enriched_option_outcomes.py`.

### Label definitions (exact mechanics — do NOT infer from `policy_version`)

Each row's label mechanics are stamped in per-row `label_*` semantics tags so horizons never silently mix. The tags are authoritative; the summaries below are the current settings.

- **Same-day GIGO label (`realized_return_pct`)** — the canonical label. Byte-identical to production: **10:00 ET entry, +40% target, −30% stop, flat exit at 15:45 ET, no trail** (V7 GIGO). STOP wins over TARGET on ambiguous bars. Realistic slippage / gap-through-stop; the labeler refuses to simulate an unclosed window (→ NULL). Mechanics stamped in `label_sim_version` / `label_hold_days` / `label_stop_pct` / `label_target_pct`.
- **3-day bracket label (`realized_return_pct_3d`)** — a **parallel, distinct-horizon** arm: **−60% stop, +80% target, HOLD_DAYS=3**. This is the horizon the flagship `mom_60`×delta finding lives on. NEVER pool it with the same-day label. Mechanics stamped in `label_3d_*`. *(LIVE as of 2026-07-02 — columns present + backfilled via `backfill_opportunity_surface.py`; ~2,115 rows carry a 3-day label.)*
- **Opportunity surface (`opp_peak_return` = MFE, `opp_trough_return` = MAE)** — max favorable / max adverse excursion of the option premium over a multi-day window with **NO exit rule**. This is exit-free *profit potential* so any exit rule is derivable offline — it is **NOT a tradeable label** and **NOT a feature**. `opp_status` ∈ {OK, WINDOW_OPEN, NO_BARS, INVALID_LIQUIDITY, NO_POST_ENTRY_BARS, ERROR, DISABLED}. *(LIVE as of 2026-07-02 — backfilled; ~2,994 rows have an `opp_status`, ~2,029 a real MFE/MAE.)*

### Column classification (the leakage boundary)

Every column belongs to exactly one group. The classification is written into the BQ **column descriptions** (machine-readable) by `scripts/ledger_and_tracking/tag_enriched_column_descriptions.py`, prefixed `[feature|label|opportunity|regime_telemetry|identity | as-of <boundary>]`. Adopt the prefix convention going forward: `label_*` = label-semantics tag, `oc_*` = entry-close regime telemetry (realized after the trade), `opp_*` = opportunity-surface excursion.

- **IDENTITY / keys** (known at selection): `scan_date`, `entry_day`, `exit_day` (realized), `ticker`, `direction`, `recommended_contract`, `recommended_strike`, `recommended_expiration`, `recommended_dte`; cohort meta `was_tournament_pick`, `was_topscore_pick`, `pool_size`, `policy_version`, `labeled_at`.
- **FEATURE** (point-in-time, safe as model inputs): the study levers (`recommended_delta`, `risk_reward_ratio`, `atr_normalized_move`, `moneyness_pct`), greeks + contract liquidity (`recommended_gamma/theta/vega/iv/spread_pct/volume/oi`, `volume_oi_ratio`, `contract_score`), flow (`call_dollar_volume`, `put_dollar_volume`), scoring (`overnight_score`, `premium_score`, `is_premium_signal`, `catalyst_score`), scan-time technicals (`underlying_price`, `atr_14`, `rsi_14`), regime feature `vix3m_at_enrich`. Scan-date regime `vix_at_scan` / `spy_trend_at_scan` / `vix_5d_delta_at_scan` and momentum `mom_60` (+ `mom_anchor_date` / `mom_lookback_date` / `mom_lookback_days`) are now LIVE + backfilled point-in-time (2026-07-02, B2/B3). NOTE: the `enriched_features_v1` view still keeps these commented in its `PENDING_FEATURE_ALLOWLIST` — activate them (Phase C) before agents can read them through the view.
- **LABEL** (realized after entry — NEVER a feature): `entry_timestamp/price`, `target_price`, `stop_price`, `trail_trigger_price`, `peak_premium`, `trail_activated`, `trail_stop_at_exit`, `exit_timestamp`, `exit_reason`, `realized_return_pct`, fill-realism (`exit_slippage`, `illiquid_exit`, `late_fill_minutes`), benchmarking (`iv_rank_entry`, `iv_percentile_entry`, `hv_20d_entry`, `underlying_entry/exit_price`, `underlying_return`, `spy_entry/exit_price`, `spy_return_over_window`), the 3-day arm (`realized_return_pct_3d` + `exit_*_3d` + `entry_price_3d` + `peak_premium_3d`), and the `label_*` semantics tags.
- **OPPORTUNITY** (`opp_*`): exit-free MFE/MAE — not a label, not a feature.
- **REGIME_TELEMETRY** (realized entry-close, benchmarking only): `oc_vix_at_close`, `oc_spy_trend_at_close`, `oc_vix_5d_delta_at_close`. **Legacy leak** `VIX_at_entry` / `SPY_trend_state` / `vix_5d_delta_entry` are entry-**close** values realized after the same-day trade — they were mislabeled as features and are being re-homed to `oc_*` (substrate must-fix #2). **Do NOT use them as features.**

### Leakage rule

- A **FEATURE** is known as-of **≤ scan_date** (the real selection point). Entry-window values known **≤ 10:00 ET entry** (e.g. the `*_entry` IV benchmarks) are realized-context, NOT features. **Everything else is an outcome.**
- **Agents / MCP / research MUST query `enriched_features_v1` (never the raw table) for features.** The raw `enriched_option_outcomes` table is for LABEL JOINS ONLY, by a human who understands this rule. dbt equivalent: `features_enriched_option_outcomes` (agent-facing) vs `fct_enriched_option_outcomes` (label-carrying kitchen sink).

### Leakage-safe access surfaces (substrate must-fix #4)

- **`enriched_features_v1`** — VIEW over `enriched_option_outcomes` exposing ONLY the FEATURE + IDENTITY + cohort-meta allowlist above. Created by `scripts/ledger_and_tracking/create_enriched_features_view.py` (gated: dry-run default, `--execute` after `gammarips-review`).
- **`overnight_signals_enriched_safe`** — VIEW over `overnight_signals_enriched` that drops the win-tracker forward-outcome columns (`next_day_pct`, `day2_pct`, `day3_pct`, `peak_return_3d`, `is_win`, `outcome_tier`, the `*_close` forward prices, `performance_updated`) so an agent that wanders upstream can't leak. Created by `scripts/ledger_and_tracking/create_enriched_signals_safe_view.py` (same gating). The base `overnight_signals_enriched` **still carries** those forward-outcome columns (merged in by `win-tracker`) — do not `SELECT *` it for features.

**Known data-quality caveats:** ~145 duplicate rows (a real finding, not a build blocker; `stg_enriched_option_outcomes` dedups to latest by `labeled_at`); ~27.7% of rows are `INVALID_LIQUIDITY` NULL-label (non-random illiquid tail — document the exclusion in any screen); pre-2026-06-11 daily counts are uneven.

## Minute paths — `profitscout-fida8.profit_scout.option_minute_paths` (added 2026-07-07)

Per-minute option-premium OHLCV bars over each enriched-pool candidate's **3-trading-day excursion window** (`[entry_day .. exit_day_3d]`), one row per `(contract, entry_day, ts)` with `bar_date` (ET session) and `day_index` (1–3). This is the first-crossing substrate behind the MCP's `replay_contract` and `estimate_exit_rule`'s exact-resolution + trailing-rule scoring (must-fix #6g / RM-002 / TF-14). Writers: one-shot backfill (`scripts/ledger_and_tracking/backfill_option_minute_paths.py`, executed 2026-07-07) + `forward-paper-trader/minute_paths.py` via `POST /persist_minute_paths` (daily evening cron, reconciles the last 3 scan_dates DELETE-then-LOAD). **LOAD JOBS ONLY with the explicit schema — no streaming (the reconcile DELETE would hit buffers), no autodetect.** Partition `entry_day`, cluster `contract`. Schema source of truth: `scripts/ledger_and_tracking/create_option_minute_paths.py`.

**Classification: REALIZED TAPE — never a feature.** Same class as `opp_*`: research/label substrate for CLOSED windows only. Never joined into `enriched_features_v1` or any as-of ≤ scan_date surface; never read by selection or the live trader. See `docs/DECISIONS/2026-07-07-option-minute-paths.md`.

## Pool-liquidity telemetry — `profitscout-fida8.profit_scout.pool_liquidity_snapshot` (added 2026-07-07)

Interval liquidity re-read of the **current enriched pool** (~50 contracts), one row per `(contract, as_of)`, written every ~10 minutes during RTH (plus one pre-open pass, `is_preopen=true`) by `signal-notifier/pool_liquidity.py` via `POST /refresh_pool_liquidity` (Cloud Scheduler `pool-liquidity-refresh`, `*/10 9-16 * * 1-5` ET). Consumed CACHE-FIRST by the gammarips-mcp `get_contract_snapshot` / `get_pool_liquidity` tools so an agent shortlist refreshes in one call at the ~10:00 ET decision window. See `docs/DECISIONS/2026-07-07-pool-liquidity-snapshot.md`.

**Partition:** `DATE(as_of)` (DAY). **Cluster:** `contract`. Schema source of truth: `scripts/ledger_and_tracking/create_pool_liquidity_snapshot.py`. Write path: `insert_rows_json` against the explicit schema — **never a load job, never autodetect**.

**Classification: TELEMETRY — never a feature.** Every non-identity column is entry-day-live (the 09:15+ tape) keyed by explicit `as_of`. It must NEVER be joined into `overnight_signals_enriched`, `enriched_features_v1`, or any as-of ≤ scan_date surface, and it is never read by the tournament/selection path (which keeps its own C1-walled OI-only fetch, `_fetch_live_oi`).

Key columns: identity (`contract`, `underlying`, `scan_date`, `as_of`, `is_preopen`, `fetch_status` ∈ {ok, polygon_empty, polygon_error}); liquidity read (`open_interest` — refreshes upstream once each morning, `day_volume` — live session, `last_trade_price/_ts`, `day_open/high/low/close`, `day_last_updated`); context (`underlying_price` + `underlying_price_source` ∈ {option_snapshot, day_agg_delayed, prev_close}, `implied_volatility`, `delta/gamma/theta/vega`); provenance (`source`, `is_delayed`). `bid`/`ask`/`mid`/`spread_pct` are **NULL placeholders** pending the RM-001b quote-feed purchase — the MCP omits them from responses while NULL.

## Firestore — `ledger_trades/{scan_date}_{ticker}` (added 2026-06-03)

Per-trade publish of the closed live cohort (current: V7.1) for the public webapp scorecard table (`/scorecard`). Written by `signal-notifier/main.py:compute_and_write_ledger_trades` alongside `cohort_stats/current`, on the same daily cron and the `/refresh_stats` endpoint. **Uses the identical cohort filter and fixed-dollar sizing as `cohort_stats/current`** (`DATE(entry_timestamp) >= LIVE_COHORT_START_DATE` [= 2026-06-26] AND `policy_version = 'V7_1_TILTED_GIGO'` AND `realized_return_pct IS NOT NULL` AND `entry_price > 0`; `n_contracts = GREATEST(1, ROUND(POSITION_SIZE_USD/(entry_price*100)))`), so the table rows and the aggregate tiles can never disagree. Idempotent upsert (`merge=True`) keyed by `{scan_date}_{ticker}`; non-gating, display-only. Read-only consumer; never feeds any execution gate.

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

## Current policy contract (V7.1 Tilted GIGO — V6-tournament selection, same-day GIGO exit, no trader-side gates)

> The ranker is a bracket **TOURNAMENT** (`tournament_v1`, version 7, `gemini-3.1-pro-preview`) on the `signal-judge` Cloud Run service — NOT a single `judge_v6` call. The tournament seeds gated candidates into brackets and writes finalists + the winner row, encoding an ADVANCEMENT proxy in the rubric columns. The `signal_ranker_runs` trace table name is **UNCHANGED**; tournament output is mirrored into the existing `scorer_*`/`picker_*` columns at `*_prompt_version = 7` and `*_model = 'gemini-3.1-pro-preview'`. Cohort labels: `5` = two-stage Scorer→Picker, `6` = `judge_v6` single judge, `7` = tournament. The Firestore `v5_4_*` provenance keys are KEPT (name retained for continuity; do not rename). The ledger `policy_version` label is now `'V7_1_TILTED_GIGO'` (V7.1 changed the trade EXIT to a same-day GIGO bracket, not the picker — the tournament selection and cohort label `7` are unchanged).

All signals that pass the enrichment filter (`overnight_score >= 4 AND directional UOA > $500K`; the spread gate was retired 2026-06-05 → `recommended_spread_pct` is NULL) seed the tournament; the paper trader then ledgers the single daily tournament pick (the full enriched pool is replayed separately into the `enriched_option_outcomes` research substrate). **The `signal-notifier` selection gates were REMOVED in V6 (2026-06-04)** — the `moneyness_pct`, `volume_oi_ratio`, `recommended_dte`, `OI`, and `vol` selection filters no longer run. Only two safety rails remain in `signal-notifier`: **no earnings during the hold window** and the **`VIX <= VIX3M` regime check** (plus the BULLISH-only hard gate, the edge-rank pool cap, and the live-OI liquidity floor). Candidate selection among the survivors is the tournament's job. Premium flags and the former-gate feature columns are still computed and stored for post-hoc discovery. See `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.

## Notes
- `VIX_at_entry`, `vix_5d_delta_entry`, and `SPY_trend_state` are retained as telemetry only. None of them gate execution.
- The `signals_labeled_v1` research table (frozen, `V3_MECHANICS_2026_04_07`) is a backfilled simulation over 1563 historical signals — it is NOT the live forward-paper ledger.
- Always write `policy_version` and `policy_gate` to ledger rows for traceability.
