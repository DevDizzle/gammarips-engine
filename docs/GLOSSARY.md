# GammaRips Glossary — Services & Tables

Plain-English reference. Not schemas. Use this to remember what each thing is for.

## Services (Cloud Run)

| Service | What it does | Why it exists |
|---|---|---|
| `overnight-scanner` | Pulls raw options activity data from Polygon each evening. Detects unusual options activity (UOA) — large directional call/put volume, spread quality, technicals. | Ingests the raw universe. You'd see ~500 tickers mentioned per night. |
| `enrichment-trigger` | Filters scanner output to signals with `overnight_score >= 4 AND directional UOA > $500k` (all directions), then edge-ranks + grounds only the **top-50 BULLISH** names (`thinking_budget=0`). Adds features: premium flags, technicals, V/OI ratio, moneyness %, VIX3M, `mom_60`. | Turns raw noise into tradeable candidates. Score floor raised 1 → 4 on 2026-06-05; the spread gate was RETIRED 2026-06-05 (this Polygon plan serves no NBBO quotes, so `recommended_spread_pct` is permanently NULL). |
| `signal-notifier` | Applies the two SAFETY rails (VIX ≤ VIX3M regime gate, no earnings during hold window), hard-gates to BULLISH, edge-ranks + caps the pool, re-fetches **live OI** and drops dead contracts (`OI_FLOOR`), calls `signal-judge` for the bracket-tournament pick, emails you the **top 1** at **~09:45 ET**. Also writes `cohort_stats/current` (public-stats panel) and the canonical `todays_pick/{scan_date}` doc. | Your inbox is the signal. One pick per day or nothing. The per-candidate selection gates were all REMOVED in V6 (2026-06-04); cron moved 09:00 → 07:30 ET (2026-05-06), then 07:30 → ~09:45 ET (2026-06-25) with the live-OI floor. |
| `signal-judge` | The V6 ranker (renamed from `signal-ranker` 2026-06-04). A randomized bracket **tournament** (`tournament_v1`, `gemini-3.1-pro-preview`) over ALL enriched signals — 3 brackets × (batches ≤10 → top-2 advance → 94→20→4→1) → consensus pick (+ runner-up + confidence). Simple prompt + daily report + per-contract JSON; no memory/rubric/weights. Writes `signal_ranker_runs` (table name unchanged). | The one high-stakes daily decision. Evolved Scorer+Picker → judge_v6 → tournament across 2026-06-04. Fail-closed — no fallback. |
| `forward-paper-trader` | Simulates V7.1 "GIGO" execution (10:00 ET entry, +40% target, −30% stop, same-day hold, flat 15:45 ET, no trail) on the daily tournament pick (one row per `scan_date`). Writes to `forward_paper_ledger`. | Paper P&L baseline. Runs in parallel with your real trades so we can compare mechanical execution vs your discretion. |
| `win-tracker` | For every enriched signal, tracks the underlying STOCK's 3-day peak price movement. Writes to `signal_performance`. Posts "strong" wins to X/Twitter. | Answers "did the direction call work?" independent of whether the option trade worked. |
| `agent-arena` | Multi-LLM debate service. **DEPRECATED 2026-05-04 — dead, not run.** Writes to (frozen) `agent_arena_*` tables. | No longer part of any loop. If touched, propose deletion, not enhancement. |
| `overnight-report-generator` | Uses Gemini to write an editorial summary of each night's scan for the webapp. | User-facing narrative layer. Not part of the trading loop. |
| `gammarips-eval` | Evaluates LLM quality against labeled outcomes. Writes to `llm_eval_results_v1`. | Monitoring only. Non-gating. |
| `gammarips-mcp`, `gammarips-webapp` | The public-facing web surface. | Consumer-facing UI for the research. |
| `x-poster` | ADK multi-agent publisher for `@gammarips` X account. 5 schedulers/day (report, signal/standby, teaser, callback, scorecard). Text-only since 2026-04-28. Disclaimer only on win/loss/callback/scorecard. | The brand voice on X. Win/loss callbacks are the realized-P&L credibility loop. |
| `blog-generator` | ADK multi-agent weekly blog publisher. Mon 05:00 ET cron → `POST /generate` → `blog_posts/{slug}` in Firestore → webapp renders. 13-row schedule per the 90-day plan. | Long-form SEO + cornerstone content. The blog is the hub; X / Reddit / email are spokes. |
| `content-drafter` (planned) | Extends `blog-generator` with `/draft_reddit` + `/draft_email` endpoints. Drafts to GCS, digest emails to Evan. Never auto-posts to Reddit; can blast email to Firestore `users` collection (211 entries) on approval. | Reddit + email surfaces of the 4-surface ship-and-park plan. |

## BigQuery tables (`profitscout-fida8.profit_scout.*`)

| Table | What's in it | Who writes it | Why you care |
|---|---|---|---|
| `overnight_signals` | Raw scanner output — every ticker the scanner flagged, before filtering. | `overnight-scanner` | Full universe. You probably never query this directly. |
| `overnight_signals_enriched` | Filtered + feature-added signals. ~50 rows/day (top-N BULLISH grounded) passing the enrichment gate. Has all the features the notifier and trader use (premium flags, technicals, V/OI, moneyness, VIX3M, `mom_60`). | `enrichment-trigger` | This is the table the notifier reads to decide what to email you. |
| `signal_performance` | Stock-level 3-day outcomes: peak move %, tier bucket (strong/solid/directional/no_decision/loss), `is_final` flag. 2,664 rows since Feb 18. | `win-tracker` | Answers "did the signal pick the right direction?" Use for directional accuracy analysis. |
| `signals_labeled_v1` | **FROZEN research dataset.** 2,162 option-level simulated trades (Feb 18 – Apr 6) with entry, target, stop, exit, realized return. Built by `scripts/research/` (frozen). | One-shot research script (do not rebuild) | Historical validation backbone. Do not modify. Read-only use only. |
| `forward_paper_ledger` | Paper P&L for the daily pick (one row per `scan_date`). Tagged by `policy_version` — current rows are `V7_1_TILTED_GIGO` (cohort start 2026-06-26); prior cohorts were truncated at each policy cutover. | `forward-paper-trader` | Your live paper scoreboard. Compare cohort EV here to your real P&L to see if discretion adds value. |
| `polygon_iv_history` | Daily ATM-30D implied volatility snapshot per ticker in the scan universe. | `forward-paper-trader` `/cache_iv` endpoint (daily 16:30 ET) | Backfills `iv_rank_entry`/`iv_percentile_entry` on ledger rows. |
| `agent_arena_consensus`, `agent_arena_picks`, `agent_arena_rounds` | Multi-LLM debate artifacts. | `agent-arena` | Research/monitoring only. Not in the trading loop. |
| `llm_eval_results_v1`, `llm_traces_v1` | LLM evaluation output and prompt/response traces. | `gammarips-eval`, shared `libs/trace_logger` | Observability into LLM quality. Not in the trading loop. |
| `temp_perf_updates` | Staging table for win-tracker perf updates. | `win-tracker` internal | Ignore. |

## Firestore collections (`profitscout-fida8` `(default)` database)

| Collection | What's in it | Who writes it | Why you care |
|---|---|---|---|
| `todays_pick/{date}` | One doc per scan_date AND per entry_day (dual-write since 2026-04-28). Fields: `ticker`, `direction`, `recommended_contract`, `score`, `vix3m_at_enrich`, `policy_version`. | `signal-notifier` (writes both keys) | Source of truth for "today's GammaRips pick" across webapp, gamma-bot, MCP, x-poster. |
| `overnight_reports/{date}` | Daily overnight editorial brief (markdown). | `overnight-report-generator` | x-poster `report` planner reads this; if missing the report cron skips. |
| `x_posts/{date}_{type}` | Logged tweet record: text, tweet_id, image_url, iterations, error, dry_run, posted_at. | x-poster Publisher | Win/loss QRT lookup uses this to find the original signal tweet. |
| `blog_schedule/current` | 13-row 90-day plan. Each row: `slug`, `week_num`, `title_candidate`, `persona`, `keywords`, `cta` (webapp_visit / starter_trial / pro_trial), `type`, `cross_channel`, `status` (pending / published). | `scripts/seed_schedule.py` (run with `PROJECT_ID=profitscout-fida8`) | blog-generator planner + future content-drafter cross-channel coordination. |
| `blog_config/voice_rules` | Snapshotted voice rules + retired aliases + banned phrases + disclaimer strings. | seed script | Backup source for voice rules in case the lib version drifts. |
| `blog_posts/{slug}` | Published blog markdown + metadata: title, description, keywords, cta, reviewer_score, iterations, status (published / rejected / dry_run), reading_time_min, published_at. | blog-generator Publisher (only on `dry_run=False AND APPROVE AND rubric.passed`) | Webapp `/blog/[slug]` renders directly from this. |
| `users` | Webapp signups. 211 docs (2026-04-28). All have `email`. Other fields: displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId. | webapp signup flow | Email blast audience for content-drafter `/draft_email`. |
| `email_subscribers` | Legacy (2 docs). | (unused) | Not used by current pipeline. |
| `eval_reports/{iso_week}` | Weekly LLM eval markdown digest. | gammarips-eval | Monitoring. |

## Governance

| Term | What it means |
|---|---|
| `policy_version` | Tag on every ledger row identifying which strategy produced it. Current rows get `V7_1_TILTED_GIGO`; prior cohorts (V5.3/V5.4/V6/V7) were truncated at each cutover. **Never reuse a label across strategies** — keeps the cohorts clean. |
| `policy_gate` | Describes the filter applied. Current rows carry `ENRICHMENT_ONLY_NO_TRADER_GATE` — meaning the trader applies no filters, all gates live upstream. |
| `scan_date` | The date the scanner ran (overnight). Signals for `scan_date = X` are traded on `X+1 trading day`. |
| `enriched_at` | Timestamp the enrichment step completed. For a `scan_date` of Monday, `enriched_at` is typically Tuesday 05:30 ET. |
| Frozen files | `scripts/research/*` and `signals_labeled_v1` are immutable for reproducibility. Everything else can evolve. |
| Phase 2 backlog | Sweep/block detection, aggressor side, GEX, regime-conditional sizing — all deferred until the current cohort hits 30 closes. |

## Subagents (Claude Code)

| Agent | Role |
|---|---|
| `gammarips-engineer` | Implementation. Code changes, deploys, BQ schema. |
| `gammarips-researcher` | Read-only research. Cohort analysis, hypothesis testing. Does not edit code. |
| `gammarips-review` | Read-only auditor. **Must run before any deploy.** Checks lookahead, leakage, unsafe execution. |

## Read-first docs

| File | Read when |
|---|---|
| `CHEAT-SHEET.md` (root) | You want to know what to do today. |
| `docs/TRADING-STRATEGY.md` | You want the canonical policy spec. |
| `docs/DECISIONS/2026-04-17-v5-3-target-80.md` | You want the V5.3 → V5.4 lineage. |
| `docs/GLOSSARY.md` (this file) | You forgot what a service or table is for. |
| `docs/ARCHITECTURE.md` | You're touching code and need the data-flow map. |
| `docs/DATA-CONTRACTS.md` | You need the actual BQ schemas. |
| `docs/archive/*` | Historical only. Not authoritative. |
