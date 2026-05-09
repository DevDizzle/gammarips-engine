# Next Session Prompt

**Last session wrapped:** 2026-05-09 (Saturday) — **V5.4 promotion COMPLETE and LIVE end-to-end.** Engine services redeployed (`signal-notifier-00020-rqq`, `forward-paper-trader-00031-2bv`, `win-tracker-00011-5l9`); webapp pushed to `main` (`512fb567`) and Firebase App Hosting auto-deployed; Firestore `cohort_stats/current` patched to V5.4. V5.3 is fully retired. Ledger empty post-truncate. **Park-mode is active again** — return trigger is the V5.4 30-trade DoD email.

**State at handoff time:**
- `forward_paper_ledger` — empty (TRUNCATED 2026-05-08; first V5.4 row lands Mon 5/11 16:30 ET).
- All execution-chain services serving V5.4 code. Webapp shows `GammaRips · V5.4 Live` + `Cohort since May 8, 2026`.
- `cohort_stats/current` Firestore doc: `cohort_start=2026-05-08`, `policy_version=V5_4_AGENT_RANKER`, all stats 0. Will self-rewrite on first signal-notifier cron.
- `park_watchdog/gate_30_alerted` doc never existed (V5.3 never reached 30 closes). Watchdog naturally re-armed.
- Engine git: clean except for `.claude/scheduled_tasks.lock` (untracked runtime artifact). Two commits: `3e83caf` (V5.4 promotion) + `8eec742` (content copy sweep).
- Webapp git: clean except for `public/og-image.png.bak` (untracked backup). One commit: `512fb567`.

**Prior sessions:** 2026-05-09 V5.4 promotion deployed; 2026-05-08 V5.4 spec LOCKED + Phases 0-3 built + V5.3 retired same day; 2026-05-07 receipt-only content strategy + NVAX trade #1 (subsequently truncated); 2026-05-06 lit-audit deploys + cohort_stats live-stats panel; 2026-04-30 content surfaces live; 2026-04-17 V5.3 adopted (now retired).
**Current policy:** V5.4 Agent Ranker — sole live strategy. Decision lock: [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md). Promotion EXEC-PLAN: [`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`](docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md).
**V5.4 build status:** Phases 0-3 LIVE in production. Phase 4 (gammarips-eval rubric IC + flip signal-ranker `DRY_RUN=false`) NOT YET BUILT — defer until N≥10 V5.4 closes (~2-3 weeks at 1-2 picks/week).

---

## TL;DR for the next session

**Default mode is monitor + park.** Code work is paused until either (a) the 30-trade DoD email fires, (b) Phase 4 trigger (N≥10 closes), or (c) the operator surfaces a specific issue.

**Mon 2026-05-11 07:30 ET — first live V5.4 cron fire.** What to verify:

1. `todays_pick/{scan_date}` Firestore doc has `policy_version="V5_4_AGENT_RANKER"` + `v5_4_run_id` + `v5_4_justification` + `v5_4_confidence` + `v5_4_runner_up`. (Or `has_pick=false` + a `skip_reason` like `v5_4_unavailable` / `earnings_overlap_all_candidates` — both are correct outcomes.)
2. Operator + paid-sub emails BOTH show the V5.4 pick + Picker justification block (single email path; no operator-only V5.4 callout — that's gone).
3. WhatsApp message via openclaw mirrors the email pick (or the standby copy on a no-pick day).
4. `cohort_stats/current` Firestore doc gets rewritten by signal-notifier with the same V5.4 cohort metadata.
5. Mon 16:30 ET — `forward_paper_ledger` gets ~80 rows tagged `V5_4_AGENT_RANKER` (broad-research dataset). The "official pick" is the row whose `(scan_date, ticker)` matches `todays_pick/{scan_date}`.
6. Webapp banner, x-poster `signal` post (08:00 ET), gamma-bot, MCP all read `todays_pick` and reflect V5.4 automatically — no per-reader code change needed.

**If first cron fails closed (signal-ranker error):**
- `todays_pick/{scan_date}` is written with `has_pick=false, skip_reason="v5_4_unavailable"`. NO email fires. NO trade is executed by the trader (broad-research rows still simulate, but the "official pick" JOIN finds nothing).
- This is the documented intended behavior — fail-closed is the SLO. Investigate signal-ranker logs (`gcloud run services logs read signal-ranker --project=profitscout-fida8 --region=us-central1 --limit=100`).

**Hold window:** Mon 5/11 entry → Thu 5/14 exit (3 trading days, 15:50 ET). First close lands 5/14 EOD; first `signal_performance` write 5/14 16:30 ET via win-tracker.

**Phase 4 trigger (deferred ~2 weeks):**
- Flip `signal-ranker DRY_RUN=false` so `signal_ranker_runs` populates per-row Scorer/Picker provenance.
- Build IC join: `signal_ranker_runs ⨝ forward_paper_ledger ON (candidate_ticker, entry_day)` to compute Scorer rubric → realized return correlation.
- Hookup lives in `gammarips-eval`. Original spec in [`docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#phase-4`](docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md).

**Locked decisions (don't relitigate):**
- V5.3 is RETIRED. **No fallback.** signal-ranker uptime is the SLO.
- Full TRUNCATE TABLE was performed (246 rows wiped). `LIVE_COHORT_START_DATE = "2026-05-08"`.
- Subscribers get V5.4 from the first post-deploy cron — single email path.
- Trader mechanics unchanged from V5.3: entry 10:00 ET, stop −60%, target +80%, 3-day hold, exit 15:50 ET day-3, stop wins on ambiguous bars.
- Composite weights: 60/25/15 flow/regime/narrative. `scorer_v3` has HEDGING `flow_conviction` ≤4 hard cap. `picker_v2` outputs enum confidence + prose-only Scorer input.

**Known follow-ups (NOT blockers):**
- `todays_pick_history` BQ table — optional add-on so cohort_stats / win-tracker can JOIN cleanly instead of using `COUNT(DISTINCT scan_date)` heuristic. Spec in EXEC-PLAN Phase 2.
- Stale `todays_v5_4_pick/{2026-05-04, 2026-05-07}` Firestore docs — collection retired; clean up if desired.
- DESIGN_SPEC files in `x-poster/` + `blog-generator/` still have V5.3 lineage references — historical, not user-facing, leave.
- `docs/LAUNCH-DAY-2026-04-21.md` — historical launch doc, leave.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `signal-notifier` | `00020-rqq` | LIVE V5.4-only fail-closed flow. Single email path (operator + paid subs same content). `SIGNAL_RANKER_URL` env var live. 300s timeout on `/rank`. Cron `30 7 * * 1-5` ET. |
| `signal-ranker` | `00004-5nt` | ADK Scorer fanout (`gemini-3-flash-preview`, scorer_v3 — HEDGING ≤4) + Picker (`gemini-3.1-pro-preview`, picker_v2 — enum confidence). IAM-only. POST `/rank` returns pick + runner-up + justification + confidence. `DRY_RUN=true` (Phase 4 flips this). Hard leakage guard `assert_no_leakage` rejects post-scan fields. |
| `forward-paper-trader` | `00031-2bv` | `POLICY_VERSION="V5_4_AGENT_RANKER"`. Sidecar removed. Firestore dep dropped. Trader mechanics unchanged. Cron `30 16 * * 1-5` ET + IV cache `30 16 * * 1-5` ET. |
| `win-tracker` | `00011-5l9` | 30-trade DoD gate filters on `V5_4_AGENT_RANKER` + `COUNT(DISTINCT scan_date)` heuristic. Idempotent via `park_watchdog/gate_30_alerted`. Cron `30 16 * * 1-5` ET. |
| `x-poster` | `00031-c2b` | LIVE, DRY_RUN=false. Reads `todays_pick` (auto-V5.4). Path B `signal` post = anchor (ticker + direction + score, withholds contract). 5 schedulers active. |
| `enrichment-trigger` | unchanged | gates: score≥1, **spread≤8%** (5/6 lit-audit H11), UOA>$500K. VIX/VIX3M cache made date-aware in 5/9 promotion sweep. |
| `overnight-report-generator` | unchanged | writes `daily_reports/{date}`. |
| `gammarips-eval` | unchanged | monitoring-only. Rubric IC hookup is Phase 4. |
| `reddit-poster` | `00004-2qd` | LIVE 5/7 DRY_RUN=true. Drafts to `gs://gammarips-reddit-drafts/{date}/`. Reddit creds NOT wired. |
| `blog-generator` | `00019-bwk` | LIVE, DRY_RUN=false. Auto-blast Mon 05:30 ET (kill via `blast_killswitch/<date>`). |
| `gammarips-mcp` | `00027-mcl` | 18 tools. Sole sandboxed-bot attack surface. |
| `agent-arena` | DEPRECATED 2026-05-04 | service still exists; propose deletion if touched. |
| `webapp` (`gammarips-webapp` repo) | main `512fb567` | LIVE V5.4 copy. Firebase App Hosting auto-deploys main. |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `agent-arena-trigger` | 06:00 | agent-arena | PAUSED |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `signal-notifier-job` | **07:30** | signal-notifier | V5.4 pick → `todays_pick` + email + WhatsApp. Fail-closed on signal-ranker error. |
| `x-poster-signal-0800` | 08:00 | x-poster `/post {signal}` | Path B anchor; reads `todays_pick`. |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | writes `daily_reports/{date}` |
| `x-poster-watchlist-0905` | 09:05 | x-poster `/post {watchlist}` | excludes the official pick |
| `polygon-iv-cache-daily` | 16:30 | forward-paper-trader `/cache_iv` | |
| `forward-paper-trader-trigger` | 16:30 | forward-paper-trader | writes ~80 V5.4-tagged rows |
| `track-signal-performance` | 16:30 | win-tracker | 30-trade DoD gate |
| `x-poster-callback-1645` | 16:45 | x-poster `/post {callback}` | restricts to posted tickers |
| `backfill-signal-performance` | 17:30 | win-tracker backfill | |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | |
| `x-poster-report-0830` | Mon 06:30 | x-poster `/post {report}` | |
| `overnight-scanner-trigger` | 23:00 | overnight-scanner | |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly | |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | |
| `content-drafter-weekly-email` | Sun 17:00 | blog-generator `/draft_email` | operator preview |
| `content-blast-mon-0530` | Mon 05:30 | blog-generator `/blast_latest` | auto-blast (kill via `blast_killswitch/<date>`) |
| `weekly-intel-mon-0700` | Mon 07:00 | blog-generator `/weekly_intel` | GA4+GSC+ledger intel email |
| `content-drafter-weekly-reddit` | Thu 10:00 | blog-generator `/draft_reddit` | manual-copy drafter |

## Email strategy (canonical) — REVISED 2026-05-04

Newsletter auto-blasts. Operator has a ~12.5h kill window between Sun preview and Mon fan-out.

| Path | Trigger | Recipient |
|---|---|---|
| `/draft_email` Sun 17:00 ET cron | Auto | **Evan only** — operator preview |
| `/blast_latest` Mon 05:30 ET cron | Auto | All ~212 users (audience filter: `isAnonymous=False AND email IS NOT NULL`) |
| `/blast_email` | Manual `curl` (fallback) | Per-call audience selector |
| Daily V5.4 pick (signal-notifier) | Auto weekday 07:30 ET | Operator + paid subs (single email path) |
| Stripe transactional | Per-event | Triggering user |

**Operator kill workflow** (between Sun preview and Mon blast):

```
gcloud firestore documents set blast_killswitch/<DATE> \
  --data='{"aborted": true, "reason": "..."}' --project=profitscout-fida8
```

`/blast_latest` honors the kill, emails operator confirming, and writes `blast_history/<DATE>` with status `killed`. Idempotent: a second cron retry skips with `already_blasted`.

**CAN-SPAM caveat:** the ~212 users registered for the webapp; there's no explicit `email_consent` field. Adding "unsubscribe" link to the newsletter template is on the to-do list before scaling beyond V0.

Cadence target: 1 newsletter blast per week max.

## Newsletter design contract (Evan locked 2026-04-30)

- Subject line auto-FOMO: "$<ticker> closed +X% — did you catch it?"
- "This week" section: 2-3 sentences synthesizing real `daily_reports` headlines from the past 7 days.
- "Featured trade this week" callout:
  - Single biggest winner from V5.4 ledger past 7 days. Skipped if no winners.
  - Return percentage wraps in `<span style="color: #16a34a; font-weight: 700;">+80%</span>` — green for ALL winners regardless of BULLISH/BEARISH direction.
  - FOMO copy: "Did you catch this trade? Paid subscribers get our curated daily pick at 07:30 AM ET — straight to inbox, no chart-watching required."
  - Paper-trade disclosure as small italic line directly under.
- "What we wrote" — 120-word excerpt of latest `blog_posts/{slug}` + link to `gammarips.com/blog/<slug>`. Skipped if no published post.
- Disclaimer at footer (canonical long form).
- CTA: "Founder pricing $29/mo with code FOUNDER29 (or $39/mo without)." Links to `gammarips.com/pricing`.
- **Anti-hallucination rule:** writer ONLY mentions tickers that appear verbatim in the data blocks fed in (`recent_reports`, `recent_closes`). NO $SPY/$QQQ/$IWM/$DIA filler.

## x-poster post types — current canonical (2026-05-07)

| Type | Disclaimer | URL allowed | Notes |
|---|---|---|---|
| `signal` | none | `https://gammarips.com` (root) | Path B 5/7 — anchors ticker + direction + score, withholds contract. Anchors enable receipt-style QRTs from `win`/`loss`/`callback` later. Fired by `x-poster-signal-0800` cron. |
| `watchlist` | none | none | 3 tickers ranked by call+put dollar volume; excludes official pick. Fired by `x-poster-watchlist-0905` cron. |
| `standby` | none | none | Fires when no V5.4 pick today (gate-cleared empty or fail-closed). |
| `teaser` | none | none | Runner-ups bench post (rarely scheduled). |
| `report` | none | `gammarips.com/reports/<date>` (one only) | Weekly Mon 06:30 ET only. |
| `win` | `⚠️ Paper-trade. Not advice.` | none | QRTs originating SIGNAL anchor via `find_originating_post_for_ticker`. |
| `loss` | `⚠️ Paper-trade. Not advice.` | none | NEUTRAL single, no QRT. |
| `callback` | `⚠️ Paper-trade. Not advice.` | none | Restricts to publicly-posted tickers. |
| `scorecard` | `⚠️ Paper-trade. Not advice.` | none | Restricts to publicly-posted tickers (lookback 10 days). |

## Firestore schemas relevant to content

| Collection | Schema | Writer | Reader |
|---|---|---|---|
| `todays_pick/{date}` | scan_date, decided_at, has_pick, ticker, direction, contract, score, vix3m_at_enrich, vix_now_at_decision, **policy_version, v5_4_run_id, v5_4_justification, v5_4_confidence, v5_4_runner_up** | signal-notifier (dual-write under scan_date AND entry_day) | webapp banner, MCP, x-poster watchlist planner (for exclusion lookup), gamma-bot |
| `cohort_stats/current` | cohort_start, policy_version, as_of, trades_closed, trades_won, win_rate, total_invested_usd, total_pl_usd, roi_pct | signal-notifier (cohort recompute) | webapp landing tile |
| `daily_reports/{date}` | scan_date, title, headline, content, bullish_count, bearish_count, total_signals, seoMetadata | overnight-report-generator | x-poster report planner, blog-generator newsletter, webapp `/reports/[date]` |
| `x_posts/{date}_{type}` | scan_date, post_type, text, tweet_id, image_url, iterations, error, dry_run, posted_at | x-poster Publisher | callback ticker-restrict lookup, win/loss QRT lookup |
| `blog_posts/{slug}` | slug, title, description, markdown, keywords, cta, reviewer_score, iterations, status, reading_time_min, published_at | blog-generator Publisher | webapp `/blog/[slug]`, newsletter "What we wrote" excerpt |
| `blog_schedule/current` | version, rows[] (13-row 90-day plan) | seed script | blog-generator planner |
| `blog_config/voice_rules` | rendered, retired_aliases, banned_phrases, disclaimer_long, disclaimer_short | seed script | blog-generator (also imports gammarips_content) |
| `users` | email, displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId | webapp signups | content-drafter `read_email_audience` |
| `park_watchdog/gate_30_alerted` | one-shot flag (currently does not exist; created when V5.4 hits 30 closes) | win-tracker | win-tracker (idempotency) |

## What's left to do (as of 2026-05-09)

**Priority 1 — first-cron verification (Mon 2026-05-11):**
1. **07:30 ET** — V5.4 first auto-fire. See TL;DR step 1-4 for the pass/fail criteria.
2. **08:00 ET** — x-poster `signal` post; verify Path B anchor renders cleanly with V5.4 pick.
3. **16:30 ET** — trader writes V5.4 ledger rows; win-tracker writes nothing yet (no closes).
4. **5/14 EOD** — first V5.4 trade closes (entry 5/11 + 3 trading days). `signal_performance/{ticker,scan_date}` doc lands. Cohort tile increments.

**Priority 2 — Phase 4 prep (deferred ~2 weeks):**
5. Once N≥10 V5.4 closes: flip `signal-ranker DRY_RUN=false`. Add `signal_ranker_runs ⨝ forward_paper_ledger` IC join in gammarips-eval. Original spec in `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#phase-4`.

**Priority 3 — pending operator-side items (none blocking):**
6. Reddit creds (only needed to flip reddit-poster DRY_RUN→false). Manual cross-posting from GCS drafts works without these.
7. GA4 + GSC analytics access for `/weekly_intel` to populate with real traffic.
8. FMP key rotation (free-tier, hygiene not crisis).
9. Email list consolidation + unsubscribe link before any further newsletter blast (CAN-SPAM hardening).
10. Mailgun spam-folder watch — prior SNDK pick landed in Gmail spam; deliverability monitoring.
11. `agent-arena` Cloud Run service still exists post-deprecation; propose deletion if touched.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` with subject `[GammaRips] 30-trade gate reached — return trigger active` when V5.4 closed-trade count (DISTINCT scan_date) ≥ 30. Estimated arrival: late June / early July 2026 at the current ~1-2 trades/week public-pick pace.

When the email lands: pull aggregate stats from `forward_paper_ledger`, publish 30-trade-in-the-books blog post, open paid funnel hard via newsletter to ~212 users, shift @gammarips X cadence into recap-led mode.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`** — V5.4 promotion lock, fully executed.
2. **`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`** — promotion deploy spec (now executed).
3. `docs/TRADING-STRATEGY.md` — canonical V5.4 execution policy.
4. `docs/ARCHITECTURE.md` — service map + data flow.
5. `CHEAT-SHEET.md` — operator V5.4 routine.
6. `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md` — original V5.4 build (Phases 0-3 LIVE, Phase 4 deferred).
7. `gammarips-mcp/SECURITY.md` — trust model. Read before adding any MCP tool.

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## Definition of "GammaRips finished" (Evan's stated intent — ALL 4 LIVE on V5.4)

| Surface | Status |
|---|---|
| **`x-poster`** — @gammarips X publisher, 5 schedulers | ✅ LIVE. Reads `todays_pick` (auto-V5.4). Watchlist 09:05 (excludes pick); callback / scorecard restrict to posted tickers. |
| **`blog-generator`** — auto-publish weekly to Firestore + render on `/blog` | ✅ LIVE. Mon 05:00 ET schedule. |
| **`reddit-drafter`** — Thu 10:00 ET, GCS markdown drafts | ✅ LIVE (same blog-generator service). Drafter NEVER auto-posts. |
| **Email-marketing** — Sun 17:00 ET preview, Mon 05:30 ET auto-blast | ✅ LIVE. Newsletter design locked 4/30. |

Park condition active. Return when V5.4 30-trade gate fires.

---

## DO NOT do

- Do NOT modify V5.4 trader mechanics. Entry 10:00 ET / stop −60% / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT add a V5.3 fallback path to signal-notifier. Fail-closed on signal-ranker error is the SLO; signal-ranker uptime matters.
- Do NOT use FMP in forward-paper-trader. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27 (openclaw push is operator-side notification, not paid delivery).
- Do NOT add a customer-facing chat agent in V1. The bot is sandboxed to `gammarips-mcp` and routes group `@gamma` mentions only.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record. Founder pricing $29/mo with FOUNDER29 (or $39 base) is the only commercial surface.
- Do NOT add MCP tools without `safe_error` / `clamp` / schema whitelist.
- Do NOT publish real-money track record until V5.4 has ≥30 closed trades.
- Do NOT re-add editorial images to x-poster. Text-only is the editorial decision (2026-04-28).
- Do NOT add the `⚠️ Paper-trade. Not advice.` disclaimer to watchlist/signal/standby/teaser/report posts. Disclaimer is only for realized-P&L recap posts.
- Do NOT name a new ADK service endpoint `/run`. ADK reserves it. Use `/post`, `/generate`, `/draft_*`, etc.
- Do NOT run any seed/migration script without `PROJECT_ID=profitscout-fida8` prefix. Shell has `PROJECT_ID=profitscout-lx6bb` set; missing prefix writes to wrong project.
- Do NOT deploy a new Cloud Run service with a custom service account unless there's a hard isolation requirement. Use the default compute SA `406581297632-compute@developer.gserviceaccount.com` — it inherits Vertex AI / logging / Firestore / GCS via project Editor.
- Do NOT post the V5.4 paid daily pick on X. Watchlist posts must EXCLUDE the official pick (already enforced by planner instruction; don't unenforce).
- Do NOT broadcast the V5.4 contract (strike / expiration / mid / DTE / V/OI) on X SIGNAL posts. Path B is anchor-only. The contract is the paid product.
- Do NOT write Reddit posts longer than ~250 chars. Trades + receipts only, distraction-frame voice, no methodology, no literature citations.
- Do NOT include a multi-row "trades that closed" table in the newsletter — Evan locked 4/30 on featured-trade-only design.
- Do NOT flip signal-ranker `DRY_RUN=false` before Phase 4 IC hookup is built. The Scorer/Picker provenance writes only matter once gammarips-eval can join them to ledger outcomes.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier / signal-ranker deploys.** Not needed for x-poster / blog-generator / mcp / content-drafter / overnight-report-generator.

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest additions:
- **2026-05-09** `project_v5_4_live.md` — V5.4 promotion COMPLETE; engine + webapp + Firestore aligned; first cron Mon 5/11 07:30 ET.
- **2026-05-08** `project_v5_4_dynamic_criteria.md` — V5.4 spec lock (60/25/15 weights, scorer_v3, picker_v2).
- **2026-05-07** `feedback_reddit_short_distraction.md` — Reddit posts must be short distraction-frame.
- **2026-05-06** `project_v5_3_lit_audit_2026_05_06.md` — H11 + H12 deployed (these gates carry forward to V5.4 as upstream filters).
- **2026-04-30** `feedback_default_compute_sa.md` — Cloud Run uses default compute SA.
- **2026-04-30** `project_finished_definition.md` — all 4 surfaces LIVE.

---

*End of handoff. V5.4 is wired, deployed, and waiting for Mon 5/11 07:30 ET to fire. Park-mode is active. Wake me when the 30-trade gate email fires (`evan@gammarips.com`), or earlier if Mon's first cron shows unexpected behavior.*
