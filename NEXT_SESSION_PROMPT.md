# Next Session Prompt

**2026-05-28 session — Gemini model migration SHIPPED + verified.** Migrated every text-generation Gemini call `gemini-3-flash-preview` → `gemini-3.5-flash` across the engine. Voluntary quality upgrade — `profitscout-fida8` calls the old model daily so it keeps access past the 2026-06-15 deprecation regardless (NOT a forced migration). **Deployed + verified on 3.5-flash:** `overnight-report-generator` (00016-txd, trace ok), `gammarips-eval` (00006-t8p, judge logs ok + `config.yaml` bug fixed), `x-poster` (00036-kj6, dry-run APPROVE; DRY_RUN restored false), `enrichment-trigger` (00038-6xf — verified by its live 05:30 ET cron: 79 ok grounded calls on 3.5-flash), `signal-ranker` (00010-bmt — verified via `/rank` smoke: `scorer_model=gemini-3.5-flash`). **Untouched (deliberate):** Picker (`gemini-3.1-pro-preview`), x-poster image model (`gemini-3-pro-image-preview`), VAPO (`gemini-2.5-pro`), agent-arena (dead). **Behavioral:** Scorer `temperature=0.2` dropped (response_schema enforces structure); enrichment sampling knobs incl `seed=42` dropped; report temp dropped; **eval judges keep temp=0.0**. `thinking_level` NOT set — deployed `google-genai==1.22.0` rejects the field (caught live by smoke test, a green build hid it); thinking stays at 3.x server default. **Cohort:** segmented by `v5_4_scorer_model` — the 3 pre-migration closed trades (`gemini-3-flash-preview`) are NOT pooled with new-model trades for the 15/30-trade EV gates. `gammarips-review` PASSED. Decision: [`docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md`](docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md). ⚠️ **Working tree has ~23 uncommitted files — commit to sync repo with production.**

---

**Last session wrapped:** 2026-05-27 (Wednesday) — **diagnostic + decision session, no code shipped.** Answered "why only 3 trades on the app," traced the recurring INVALID_LIQUIDITY no-fills to their root cause, backtested a proposed fix, and **rejected it** on the evidence. Operator decision: accept INVALID_LIQUIDITY as a paper-only artifact and leave liquidity gating untouched. Set the go-forward plan: a **15-closed-trade interim checkpoint** (evals + diagnostic GO/NO-GO) ahead of the unchanged formal real-money DoD. Decision file: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md).

**State at handoff time (2026-05-27):**
- `forward_paper_ledger` — **3 closed/counted trades**: OKTA (scan 05-12, BEARISH, TIMEOUT **−1.96%**), HTZ (scan 05-14, BEARISH, TARGET **+80%**), BBY (scan 05-18, BULLISH, TIMEOUT **+15.28%**). Plus 2 `INVALID_LIQUIDITY` no-fills (KBR 05-13, EQIX 05-20) and 2 `SKIPPED` no-candidate days (05-15, 05-19). App tile: **3 trades / +31.8% ROI / 67% win / $1.5K invested**.
- **In flight (deferred reporting — see below):** BLK (scan 05-21, BULLISH) lands **today 05-27 16:30 ET**; ADI (scan 05-22, BULLISH) lands 05-28; scan 05-26 was a no-pick → writes a SKIPPED row on 05-29. ⚠️ BLK's contract showed "no bars" in the MTM log — it may land as another INVALID_LIQUIDITY.
- **Deferred-reporting mechanic (clarified this session):** the trader is NOT real-time. The 16:30 ET cron processes exactly ONE scan_date = `get_canonical_scan_date()` = **today − 3 trading days** (one cohort per day, **no catch-up loop**). So the ledger always trails real-time by ~3 trading days, and a single missed cron permanently drops that scan_date. The "3 trades" is correct given this lag + heavy gating + the 2 INVALID/2 SKIP days + Memorial Day (05-25).
- Production: `forward-paper-trader` `00035-72h` (unchanged since 2026-05-15). `signal-notifier` `00024-xh7` (active-days gate + fixed-$500 sizing). All services healthy.

**Prior sessions:** 2026-05-27 diagnostic + liquidity decision (this session); 2026-05-19 active-days liquidity gate + fixed-$500 sizing; 2026-05-15 trader resurrection + EOD MTM; 2026-05-12 V5.4 pipeline alignment; 2026-05-09 V5.4 promotion; 2026-05-08 V5.4 spec lock.

**Current policy:** V5.4 Agent Ranker — sole live strategy. **Unchanged.** No execution-policy change this session. Decision lock: [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md).

---

## TL;DR for the next session

**Default mode is monitor + park.** Code work is paused while the ledger accumulates closed trades. Return triggers:

1. **15-closed-trade interim checkpoint** (operator plan, set 2026-05-27). When `forward_paper_ledger` reaches **15 closed/counted trades** (distinct scan_date with a realized exit — excludes SKIPPED and INVALID_LIQUIDITY), run the **evals + a diagnostic** as a GO/NO-GO health check. Currently **3/15**. At ~1-2 counted trades/week this lands roughly **mid-to-late July 2026**. This is a checkpoint, NOT the real-money gate.
2. The 30-trade DoD email (`evan@gammarips.com`, subject `[GammaRips] 30-trade gate reached — return trigger active`).
3. The Phase 4 trigger (N ≥ 10 V5.4 closes) — flip `signal-ranker DRY_RUN=false` so per-row Scorer/Picker provenance lands in `signal_ranker_runs`, then build the IC join in `gammarips-eval`. Close at current pace.
4. The "5 consecutive V5.4 losses with no skipped days" rule (`docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md`).
5. The operator surfacing a specific issue.

**Real-money go-live trigger (UNCHANGED — `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`):** all three must fire, PLUS CLAUDE.md's mandatory 30-day OOS + `gammarips-review` audit. The 15-trade checkpoint above does **not** replace this.
- N ≥ 30 closed V5.4 paper trades
- Cohort EV ≥ 0
- ≥ 15 operator-confirmed manual trades match the picker's signal

Until those fire, the system is paper-only. Founder pricing $29/mo continues as the only commercial surface.

**What to put in the 15-trade diagnostic:** cohort EV + win rate; eval/IC health (once Phase 4 lands provenance); fill rate (INVALID_LIQUIDITY %); **and a review of whether the `active_days_20d >= 5` gate should stay** — this session found it may be net-harmful (it would have rejected HTZ, the +80% winner, and did NOT catch EQIX/BLK). See the liquidity decision doc.

---

## What this session did (2026-05-27) — diagnosis only, NO code shipped

1. **"Why only 3 trades?"** — confirmed correct: deferred 3-trading-day reporting lag + heavy upstream gating + 2 INVALID_LIQUIDITY + 2 SKIPPED + Memorial Day. Not a bug.
2. **INVALID_LIQUIDITY root cause** — the contracts V5.4 picks (5–10% OTM, short-DTE, single-name, UOA-spike) are uniformly thin; `recommended_volume` is the scan-day spike that doesn't persist; entry-day fill is near-random. Verified EQIX/BLK printed zero entry-day bars (genuine, not a fetch bug).
3. **Tested a fix (H15: per-day volume floor on the active-days gate) → REJECTED.** Backtest (`backtesting_and_research/2026-05-27_active_day_volume_floor.py`): any floor that rejects EQIX/BLK also rejects OKTA + BBY (real fills), HTZ fails even the current gate, BLK (most trailing activity) never printed, and floor 5 darkens 42% of days. Quote-based fill model blocked (no Polygon NBBO on our tier).
4. **Decision: accept it.** No gate change. INVALID_LIQUIDITY overstates real-world un-fillability (it fires when no one *else* traded; a real buyer crosses the ask). Decision: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md). Research brief updated (H15 resolved). Memory: `project_invalid_liquidity_root_cause`.

**Uncommitted working-tree state (carried from prior sessions, NOT this session's):** `forward-paper-trader/main.py` + `requirements.txt` + `docs/DATA-CONTRACTS.md` + `docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md` (the 05-15 MTM/trader work) and an `enrichment-trigger/main.py` thesis-prompt tweak. These were deployed-from-working-tree but never committed. This session adds: the liquidity decision doc, the INTELLIGENCE_BRIEF H15 entry, and the backtest script/results.

**Locked decisions (don't relitigate):**
- V5.3 is RETIRED. No fallback. signal-ranker uptime is the SLO.
- `LIVE_COHORT_START_DATE = "2026-05-08"`.
- Trader mechanics: entry 10:00 ET, stop −60% initial, trail +30% gain / 25% off peak, target +80%, 3-day hold, exit 15:50 ET day-3. STOP/TRAIL wins on ambiguous bars.
- Composite weights 60/25/15 flow/regime/narrative. `scorer_v5` + `picker_v4`.
- **INVALID_LIQUIDITY accepted as a paper-only artifact (2026-05-27). Do NOT build another trailing-liquidity gate — tested and dead.**
- No real-money trading until the three-part go-live trigger fires (see above).
- No new trader-side gates. Ever.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `signal-notifier` | `00024-xh7` | LIVE V5.4-only fail-closed. `active_days_20d >= 5` gate + fixed-$500 sizing. Cron `30 7 * * 1-5` ET. Refreshes `cohort_stats/current` per run. |
| `signal-ranker` | `00010-bmt` | Scorer fanout (`gemini-3.5-flash` since 2026-05-27) + Picker (`gemini-3.1-pro-preview`). IAM-only. `DRY_RUN=false` (live; table previously mis-stated `true`). |
| `forward-paper-trader` | `00035-72h` | Deferred simulator (today − 3 trading days). Two crons + `/mark_to_market`. |
| `win-tracker` | `00011-5l9` | 30-trade DoD gate. Cron `30 16 * * 1-5` ET. |
| `x-poster` | `00036-kj6` | LIVE, DRY_RUN=false. 5 schedulers active. Text on `gemini-3.5-flash` (2026-05-27). |
| `enrichment-trigger` | `00038-6xf` | gates: score≥1, spread≤8%, UOA>$500K. Thesis on `gemini-3.5-flash` (2026-05-27). |
| `overnight-report-generator` | `00016-txd` | writes `daily_reports/{date}`. On `gemini-3.5-flash` (2026-05-27). |
| `gammarips-eval` | `00006-t8p` | monitoring-only. Rubric IC hookup is Phase 4. Judge on `gemini-3.5-flash` (2026-05-27). |
| `reddit-poster` | `00004-2qd` | LIVE DRY_RUN=true. Reddit creds not wired. |
| `blog-generator` | `00020-npx` | LIVE, DRY_RUN=false. |
| `gammarips-mcp` | `00027-mcl` | 18 tools. |
| `agent-arena` | DEPRECATED 2026-05-04 | service exists; propose deletion if touched. |
| `webapp` (`gammarips-webapp` repo) | Firebase App Hosting auto-deploys main | LIVE V5.4 copy. |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `signal-notifier-job` | 07:30 | signal-notifier | V5.4 pick → `todays_pick` + email + WhatsApp + `cohort_stats/current` refresh. |
| `x-poster-signal-0800` | 08:00 | x-poster `/post {signal}` | Path B anchor. |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | |
| `x-poster-watchlist-0905` | 09:05 | x-poster `/post {watchlist}` | |
| `forward-paper-trader-mtm` | 16:15 | forward-paper-trader `/mark_to_market` | EOD snapshot of open V5.4 positions → `forward_paper_ledger_intraday`. |
| `polygon-iv-cache-daily` | 16:30 | forward-paper-trader `/cache_iv` | |
| `forward-paper-trader-trigger` | 16:30 | forward-paper-trader | Closes the trade whose `exit_day = today` (1 row/fire; today − 3 trading days). |
| `track-signal-performance` | 16:30 | win-tracker | 30-trade DoD gate. |
| `x-poster-callback-1645` | 16:45 | x-poster `/post {callback}` | |
| `backfill-signal-performance` | 17:30 | win-tracker backfill | |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | N≥5 guard. |
| `x-poster-report-0830` | Mon 06:30 | x-poster `/post {report}` | |
| `overnight-scanner-trigger` | 23:00 | overnight-scanner | |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly | |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | |
| `content-drafter-weekly-email` | Sun 17:00 | blog-generator `/draft_email` | operator preview |
| `content-blast-mon-0530` | Mon 05:30 | blog-generator `/blast_latest` | auto-blast (kill via `blast_killswitch/<date>`) |
| `weekly-intel-mon-0700` | Mon 07:00 | blog-generator `/weekly_intel` | |
| `content-drafter-weekly-reddit` | Thu 10:00 | blog-generator `/draft_reddit` | manual-copy drafter |

> **Scheduler hardening (2026-05-20):** 19/22 jobs retry 3× with 30–120s backoff. The 2 trader jobs were skipped pending `gammarips-review`. A single DNS hiccup lost scan_date 2026-05-19 — relevant because the trader has no catch-up loop.

## Firestore schemas relevant to monitoring

| Collection | Schema | Writer | Reader |
|---|---|---|---|
| `todays_pick/{date}` | scan_date, decided_at, has_pick, ticker, direction, contract, score, vix3m_at_enrich, vix_now_at_decision, policy_version, v5_4_run_id, v5_4_justification, v5_4_confidence, v5_4_runner_up | signal-notifier (dual-write under scan_date AND entry_day) | webapp, MCP, x-poster, gamma-bot, `/mark_to_market` |
| `cohort_stats/current` | cohort_start, policy_version, as_of, trades_closed, trades_won, win_rate, total_invested_usd, total_pl_usd, roi_pct | signal-notifier (recomputes from `forward_paper_ledger` once per daily cron) | webapp landing tile |
| `daily_reports/{date}` | scan_date, title, headline, content, bullish_count, bearish_count, total_signals, seoMetadata | overnight-report-generator | x-poster report planner, blog-generator newsletter, webapp `/reports/[date]` |
| `x_posts/{date}_{type}` | scan_date, post_type, text, tweet_id, image_url, iterations, error, dry_run, posted_at | x-poster Publisher | callback / win / loss QRT lookup |
| `blog_posts/{slug}` | slug, title, description, markdown, keywords, cta, reviewer_score, iterations, status, reading_time_min, published_at | blog-generator Publisher | webapp `/blog/[slug]`, newsletter |
| `users` | email, displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId | webapp signups | content-drafter `read_email_audience` |
| `park_watchdog/gate_30_alerted` | one-shot flag (created when V5.4 hits 30 closes) | win-tracker | win-tracker (idempotency) |

## BigQuery tables

| Table | Notes |
|---|---|
| `profit_scout.forward_paper_ledger` | One row per scan_date (V5.4-only). ticker/recommended_contract/direction NULLABLE. 16:30 ET cron writes the exit row for scan_date = today − 3 trading days. |
| `profit_scout.forward_paper_ledger_intraday` | Daily EOD MTM snapshots of open V5.4 positions. Partitioned by `snapshot_date`. 16:15 ET cron. Observability only. |
| `profit_scout.overnight_signals_enriched` | Enrichment output (per-ticker). Gate stack applied. |
| `profit_scout.signal_ranker_runs` | Per-row Scorer/Picker provenance. **Empty until Phase 4 trigger flips `DRY_RUN=false`** (N ≥ 10 closes). |
| `profit_scout.signal_performance` | win-tracker output. Drives the 30-trade DoD gate. |
| `profit_scout.polygon_iv_history` | IV cache. Populated daily at 16:30 ET. |

## What's left to do (as of 2026-05-27)

**Priority 1 — passive monitoring (no action unless something breaks):**
1. Watch BLK (lands 05-27 16:30 ET) and ADI (05-28). If a cron fails, check `gcloud run services logs read forward-paper-trader --project=profitscout-fida8 --region=us-central1 --limit=50`. No catch-up loop, so a missed day is lost.

**Priority 2 — Phase 4 (deferred to ~N≥10 closes, close at current pace):**
2. Flip `signal-ranker DRY_RUN=false`. Per-row Scorer/Picker provenance lands in `signal_ranker_runs`.
3. Build the `signal_ranker_runs ⨝ forward_paper_ledger ON (candidate_ticker, scan_date)` IC join in `gammarips-eval`. Spec: `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#phase-4`.

**Priority 3 — 15-closed-trade interim checkpoint (~mid-to-late July):**
4. Run evals + diagnostic GO/NO-GO. Include the `active_days_20d >= 5` gate review (see liquidity decision doc), cohort EV, fill rate, IC health.

**Priority 4 — pending operator-side items (none blocking):**
5. Reddit creds; GA4 + GSC for `/weekly_intel`; email-list consolidation + unsubscribe; propose `agent-arena` deletion if touched.

**Priority 5 — real-money go-live (deferred until full 3-part trigger fires):**
6. When N ≥ 30 closes AND cohort EV ≥ 0 AND ≥ 15 operator-confirmed matches: open the Alpaca-agent conversation per `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` (subject `[GammaRips] 30-trade gate reached — return trigger active`) when V5.4 closed-trade count (DISTINCT scan_date) ≥ 30. Before that, the **15-closed-trade interim checkpoint** is the first scheduled wake-up for an evals + diagnostic pass.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`** — most recent decision; why liquidity gating is parked.
2. **`docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md`** — the gate this session flagged as possibly net-harmful.
3. **`docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md`** — trader fixes + EOD MTM.
4. **`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`** — V5.4 promotion lock.
5. **`docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`** — real-money go-live trigger (unchanged).
6. `docs/TRADING-STRATEGY.md` — canonical V5.4 execution policy.
7. `docs/DATA-CONTRACTS.md` — BQ + Firestore schemas.
8. `CHEAT-SHEET.md` — operator V5.4 routine.

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## DO NOT do

- Do NOT modify V5.4 trader mechanics. Entry 10:00 ET / stop −60% / trail +30% gain / 25% off peak / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- **Do NOT build another trailing-liquidity gate (volume floor, OI floor, day-before-scan, etc.) — tested and rejected 2026-05-27. INVALID_LIQUIDITY is accepted as paper-only.**
- Do NOT add a V5.3 fallback path to signal-notifier. Fail-closed on signal-ranker error is the SLO.
- Do NOT use FMP in forward-paper-trader. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT add NOT NULL constraints back to `ticker / recommended_contract / direction` on `forward_paper_ledger`.
- Do NOT add execution-side logic to `/mark_to_market`. Observability-only.
- Do NOT treat the 15-trade interim checkpoint as the real-money gate — the full 3-part DoD + 30-day OOS + gammarips-review still applies.
- Do NOT start real-money trading until all three triggers fire.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27.
- Do NOT add a customer-facing chat agent in V1. Bot is sandboxed to `gammarips-mcp`.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record.
- Do NOT add MCP tools without `safe_error` / `clamp` / schema whitelist.
- Do NOT re-add editorial images to x-poster. Text-only.
- Do NOT add the `⚠️ Paper-trade. Not advice.` disclaimer to watchlist/signal/standby/teaser/report posts. Only on realized-P&L recap posts.
- Do NOT name a new ADK service endpoint `/run`. Use `/post`, `/generate`, `/draft_*`, etc.
- Do NOT run any seed/migration script without `PROJECT_ID=profitscout-fida8` prefix.
- Do NOT deploy a new Cloud Run service with a custom service account unless there's a hard isolation requirement.
- Do NOT post the V5.4 paid daily pick on X. Watchlist posts must EXCLUDE the official pick.
- Do NOT broadcast the V5.4 contract on X SIGNAL posts. Path B is anchor-only.
- Do NOT write Reddit posts longer than ~250 chars.
- Do NOT include a multi-row "trades that closed" table in the newsletter — featured-trade-only design (locked 4/30).
- Do NOT flip signal-ranker `DRY_RUN=false` before Phase 4 IC hookup is built.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier / signal-ranker deploys.**

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest additions:
- **2026-05-27** `project_invalid_liquidity_root_cause.md` — INVALID_LIQUIDITY is a thin-contract artifact; trailing-liquidity gating tested and rejected; accepted as paper-only.
- **2026-05-20** `project_first_v5_4_win_and_callback_2026_05_20.md` — HTZ +80% win + callback loop verified.
- **2026-05-20** `project_scheduler_retry_hardening_2026_05_20.md` — 19/22 jobs retry; trader jobs pending review; no catch-up loop.
- **2026-05-15** `project_v5_4_trader_observability_2026_05_15.md` — trader resurrection + EOD MTM.
- **2026-05-12** `project_v5_4_funnel_starvation.md` — picker is starved post-gates; revisit at N ≥ 15.

---

*End of handoff. The engine is rolling: 3 closed trades (+31.8% ROI), BLK + ADI landing this week on the natural 3-day-lag cadence. Liquidity gating is parked by operator decision. Next scheduled wake-up is the 15-closed-trade interim checkpoint (~mid-to-late July) for an evals + diagnostic pass — or earlier if a cron breaks or Phase 4 (N≥10) lands first.*
