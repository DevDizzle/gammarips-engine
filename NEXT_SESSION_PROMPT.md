# Next Session Prompt

**Last session wrapped:** 2026-05-08 (Friday late) — **V5.4 promotion code DONE across both repos. UNCOMMITTED + UNDEPLOYED.** This session executed the entire promotion code rewrite. The only steps left are: review diff → commit → deploy → Monday 5/11 07:30 ET first-cron verify. Cron is weekday-only (`30 7 * * 1-5`), so Sat 5/9 + Sun 5/10 are no-cron days — comfortable window to ship without operator-email duplication risk.

**State at handoff time:**
- `forward_paper_ledger` TRUNCATED (246 V5.3 rows wiped earlier in session) — empty.
- gammarips-engine repo: 28 files modified, 4 new files (decision doc, exec plan, V5.4 BQ DDL script, signal-ranker service tree). All UNCOMMITTED.
- gammarips-webapp repo: 20 files modified. All UNCOMMITTED. Firebase App Hosting auto-deploys on `main` push.
- No services redeployed since session 2 (`signal-notifier-00019-gsw`, `signal-ranker-00004-5nt`, `forward-paper-trader-00030-8ct`). Tomorrow morning's wiring goes live ONLY if the next session redeploys.

**Prior sessions:** 2026-05-08 (early) V5.4 spec LOCKED + Phases 0/1/2/2.5/3 built + deployed as DRY_RUN shadow; 2026-05-07 receipt-only content strategy + NVAX trade #1 of post-lit-audit cohort; 2026-05-06 lit-audit deploys + ledger truncation + cohort_stats live-stats panel; 2026-04-30 content surfaces live; 2026-04-17 V5.3 adopted (now retired).
**Current policy:** V5.4 Agent Ranker is the only active strategy; V5.3 retired same day. Decision lock: [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md). Promotion EXEC-PLAN: [`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`](docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md).
**V5.4 build status:** Phases 0/1/2/2.5/3 LIVE in production. Promotion code DONE but undeployed. Phase 4 (gammarips-eval rubric IC) NOT YET BUILT — defer until ≥10 V5.4 closes.

---

## TL;DR for the next session

**Primary task: review → commit → deploy the V5.4 promotion before Monday 5/11 07:30 ET.**

The code rewrite is finished across both repos. What's left is the safety net + push.

1. **Verify the diff is sane** — `git diff` in each repo. Spot-check `signal-notifier/main.py` (V5.4-only flow with fail-closed), `forward-paper-trader/main.py` (POLICY_VERSION → V5_4_AGENT_RANKER, sidecar removed), `win-tracker/main.py` (gate switched to V5_4_AGENT_RANKER + COUNT(DISTINCT scan_date) heuristic), webapp landing/faq/pricing.
2. **Pre-deploy: invoke `gammarips-review`** on the gammarips-engine diff. Mandatory per CLAUDE.md G-Stack rules (signal-notifier + trader changes are strategy-touching). Specifically test: V5.4 fail-closed paths (no V5.3 fallback drift), no zombie code referencing the retired V5.4 sidecar / shadow block, win-tracker gate semantics (won't fire spuriously on day 1 with the DISTINCT scan_date heuristic).
3. **Commit** in 2-3 atomic commits — engine: (a) decision + exec-plan + scripts (already had `?? signal-ranker/`), (b) signal-notifier + trader + win-tracker rewrites, (c) docs + content services + voice_rules sweep. Webapp: one commit.
4. **Deploy** in this order:
   - `signal-notifier` (`cd signal-notifier && bash deploy.sh`) — biggest blast radius, lands first so trader has the right Firestore handoff.
   - `forward-paper-trader` (`cd forward-paper-trader && bash deploy.sh`) — POLICY_VERSION change.
   - `win-tracker` (`cd win-tracker && bash deploy.sh`) — gate switch.
   - `x-poster` + `blog-generator` + `reddit-poster` — copy changes only; redeploy not strictly needed unless you want them on the new code immediately. Defer if low-priority.
   - Webapp: push to `main` → Firebase App Hosting auto-deploys.
5. **Reset park_watchdog flag** so the gate fires when V5.4 hits 30 closes:
   `gcloud firestore documents delete park_watchdog/gate_30_alerted --project=profitscout-fida8` (or set `{alerted: false}`).
6. **Mon 5/11 07:30 ET first-cron verify:**
   - `todays_pick/2026-05-08` (or whatever scan_date) Firestore doc has V5.4 pick + `policy_version: "V5_4_AGENT_RANKER"` + `v5_4_run_id` + `v5_4_justification` + `v5_4_confidence`.
   - Operator + paid subscriber emails BOTH show the V5.4 pick + "Why we picked it" justification block (single email path).
   - 16:30 ET trader writes ~80 rows tagged `V5_4_AGENT_RANKER` to `forward_paper_ledger`.
   - Webapp banner, x-poster signal post, gamma-bot, MCP all read `todays_pick` and reflect V5.4 automatically.
7. **Phase 4 (deferred 2 weeks)** — gammarips-eval rubric IC. Flip `signal-ranker DRY_RUN=false` so `signal_ranker_runs` populates the per-row provenance trace. Build the IC join `signal_ranker_runs ⨝ forward_paper_ledger ON (candidate_ticker, entry_day)`. Wait until N≥10 V5.4 closes.

**Locked decisions (don't relitigate):**
- V5.3 is RETIRED. **No fallback.** signal-ranker uptime is the SLO.
- Full TRUNCATE TABLE was performed (246 rows wiped). LIVE_COHORT_START_DATE = "2026-05-08".
- Subscribers get V5.4 from the first post-deploy cron — single email path.
- All other V5.4 spec inherited: 60/25/15 weighted sum, scorer_v3 (HEDGING ≤4 hard cap), picker_v2 (enum confidence, prose-only Scorer input).

**Live revisions (services are the OLD code at handoff time — promotion deploys this weekend):**
- `signal-notifier-00019-gsw` — V5.3 + V5.4 dual-path. Promotion deploy replaces with V5.4-only.
- `signal-ranker-00004-5nt` — Scorer + Picker, IAM-only, DRY_RUN=true. No change in promotion. Flip DRY_RUN in Phase 4.
- `forward-paper-trader-00030-8ct` — V5.4 sidecar. Promotion deploy retags POLICY_VERSION + removes sidecar.

**Cron weekend gap (no operator-email duplicate risk):**
- Sat 5/9 — `1-5` weekday cron does NOT fire.
- Sun 5/10 — does NOT fire.
- Mon 5/11 07:30 ET — first auto-fire after promotion deploy.

**Known follow-ups (NOT blockers for Monday):**
- `todays_pick_history` BQ table — optional Phase 2 add-on so cohort_stats / win-tracker can JOIN cleanly instead of relying on `COUNT(DISTINCT scan_date)` heuristic.
- Stale `todays_v5_4_pick/{2026-05-04, 2026-05-07}` Firestore docs from earlier tests — collection retired; clean up if desired.
- DESIGN_SPEC files in `x-poster/` + `blog-generator/` still have V5.3 lineage references — historical, not user-facing, leave.
- `docs/LAUNCH-DAY-2026-04-21.md` — historical launch doc, leave.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `x-poster` | `00031-c2b` | LIVE, DRY_RUN=false. **5/7: SIGNAL post = Path B anchor** (withholds contract, drives subs via gammarips.com URL). URL whitelist extended to allow `https://gammarips.com` root. |
| `signal-notifier` | `00019-gsw` | LIVE. **5/8: V5.4 shadow path wired** — calls `signal-ranker /rank` after V5.3 SQL pick, writes `todays_v5_4_pick/{scan_date}` Firestore, includes V5.4 block in operator email only (paid subs unchanged). 5/7: FMP earnings calendar migrated to `/stable/earnings-calendar`. |
| `signal-ranker` | `00004-5nt` | **NEW 5/8.** ADK Scorer fanout (`gemini-3-flash-preview`, scorer_v3) + Picker (`gemini-3.1-pro-preview`, picker_v2). IAM-only invokers. POST `/rank` returns pick + runner-up + justification + confidence. DRY_RUN=true (no `signal_ranker_runs` writes yet). |
| `forward-paper-trader` | `00030-8ct` | LIVE. **5/8: V5.4 sidecar added** — reads `todays_v5_4_pick/{target_date}` after V5.3 simulation, mirrors picked-ticker's V5.3 row to `forward_paper_ledger` with `policy_version=V5_4_AGENT_RANKER`. V5.3 mechanics (entry 10:00, stop -60%, target +80%, 3-day hold) unchanged. |
| `reddit-poster` | `00004-2qd` | **LIVE 5/7, DRY_RUN=true.** Templates rewritten to distraction-frame (~230 chars, no methodology, no citations). Drafts to `gs://gammarips-reddit-drafts/{date}/` for manual cross-posting. Reddit creds NOT wired (DRY_RUN doesn't need them). |
| `blog-generator` | `00019-bwk` | LIVE, DRY_RUN=false. `/blast_latest` auto-blast (kill-switch via `blast_killswitch/<date>`). `/weekly_intel` GA4+GSC+ledger intel (GA4/GSC degrade until creds land). |
| `win-tracker` | `00010-rkn` | LIVE. **30-trade gate watcher armed.** One-shot email to `evan@gammarips.com` when V5.3 ledger crosses 30 closed trades. Idempotent via `park_watchdog/gate_30_alerted`. |
| `gammarips-mcp` | `00027-mcl` | 18 tools. Sole sandboxed-bot attack surface. |
| `forward-paper-trader` | unchanged | V5.3 ledger active. **NVAX is trade #1**, entered 10:00 ET 5/7, exits 5/12. |
| `enrichment-trigger` | unchanged | gates: score≥1, **spread≤8%** (5/6 lit-audit H11), UOA>$500K. |
| `overnight-report-generator`, `gammarips-eval` | unchanged | overnight-report-generator writes `daily_reports/{date}`. |
| `agent-arena` | DEPRECATED 2026-05-04 | Memory `project_agent_arena_dead.md` — no eval, no fixes, propose deletion if touched. |
| `webapp` (gammarips-webapp repo) | main `5d736023` | LIVE. Hero/footer/title copy fixed 5/7 (`9 AM` → `7:30 AM ET`). PR #3 merged. Firebase App Hosting auto-deploys main. |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `agent-arena-trigger` | 06:00 | agent-arena | |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | writes `daily_reports/{date}` |
| **`x-poster-report-0830`** | **Mon 06:30** | x-poster `/post {report}` | **demoted from daily 5/4** |
| `signal-notifier-job` | 07:30 | signal-notifier | dual-writes pick (moved earlier from 09:00 per 5/6 cron decision) |
| **`x-poster-signal-0800`** (NEW 5/7) | **08:00** | **x-poster `/post {signal}`** | **Path B anchor**, fires 30 min after signal-notifier so `todays_pick` is locked. Replaces the misnamed `x-poster-signal-0905` job. |
| **`x-poster-watchlist-0905`** (NEW 5/7) | **09:05** | **x-poster `/post {watchlist}`** | Daily flow magnets (3 high-$-vol setups, NOT the V5.3 pick). Same time as before; preserved behavior. |
| ~~`x-poster-signal-0905`~~ | — | — | **DELETED 5/7** (was misnamed — body said watchlist; replaced by the two jobs above) |
| ~~`x-poster-teaser-1230`~~ | — | — | **DELETED 5/4** (engagement bait, no signal value) |
| `polygon-iv-cache-daily` | 16:30 | forward-paper-trader `/cache_iv` | |
| `forward-paper-trader-trigger` | 16:30 | forward-paper-trader | |
| `track-signal-performance` | 16:30 | win-tracker | 30-trade gate |
| `backfill-signal-performance` | 17:30 | win-tracker backfill | |
| `x-poster-callback-1645` | 16:45 | x-poster `/post {callback}` | restricts to posted tickers |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | first real fire 5/8 |
| `overnight-scanner-trigger` | 23:00 | overnight-scanner | |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly | |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | first auto-fire 5/4 |
| **`content-drafter-weekly-email`** | **Sun 17:00** | **blog-generator `/draft_email`** | **operator preview** |
| **`content-blast-mon-0530`** | **Mon 05:30** | **blog-generator `/blast_latest`** | **NEW 5/4 — auto-blast (kill via `blast_killswitch/<date>`)** |
| **`weekly-intel-mon-0700`** | **Mon 07:00** | **blog-generator `/weekly_intel`** | **NEW 5/4 — GA4+GSC+ledger intel email** |
| **`content-drafter-weekly-reddit`** | **Thu 10:00** | **blog-generator `/draft_reddit`** | **manual-copy drafter, separate from auto reddit-poster** |

## Email strategy (canonical) — REVISED 2026-05-04

Newsletter now auto-blasts. Operator has a ~12.5h kill window between Sun preview and Mon fan-out.

| Path | Trigger | Recipient |
|---|---|---|
| `/draft_email` Sun 17:00 ET cron | Auto | **Evan only** — operator preview |
| **`/blast_latest` Mon 05:30 ET cron** | **Auto** | **All 212 users** (audience filter: `isAnonymous=False AND email IS NOT NULL`) |
| `/blast_email` | Manual `curl` (fallback) | Per-call audience selector |
| Daily V5.3 pick (signal-notifier) | Auto weekday 09:00 ET | Paid subs only |
| Stripe transactional | Per-event | Triggering user |

**Operator kill workflow** (between Sun preview and Mon blast):

```
gcloud firestore documents set blast_killswitch/<DATE> \
  --data='{"aborted": true, "reason": "..."}' --project=profitscout-fida8
```

`/blast_latest` honors the kill, emails operator confirming, and writes `blast_history/<DATE>` with status `killed`. Idempotent: a second cron retry skips with `already_blasted`.

**CAN-SPAM caveat:** the 212 users registered for the webapp; there's no explicit `email_consent` field. Adding "unsubscribe" link to the newsletter template is on the to-do list before scaling beyond V0.

Cadence target: 1 newsletter blast per week max.

## Newsletter design contract (Evan locked 2026-04-30)

- Subject line auto-FOMO: "$<ticker> closed +X% — did you catch it?"
- "This week" section: 2-3 sentences synthesizing real `daily_reports` headlines from the past 7 days.
- "Featured trade this week" callout:
  - Single biggest winner from V5.3 ledger past 7 days. Skipped if no winners.
  - **Return percentage wraps in `<span style="color: #16a34a; font-weight: 700;">+80%</span>` — green for ALL winners regardless of BULLISH/BEARISH direction.**
  - FOMO copy: "Did you catch this trade? Paid subscribers get our curated daily V5.3 pick at 09:00 AM ET — straight to inbox, no chart-watching required."
  - Paper-trade disclosure as small italic line directly under.
- "What we wrote" — 120-word excerpt of latest `blog_posts/{slug}` + link to `gammarips.com/blog/<slug>`. Skipped if no published post.
- Disclaimer at footer (canonical long form).
- CTA: "Founder pricing $29/mo with code FOUNDER29 (or $39/mo without)." Links to `gammarips.com/pricing`.
- **Anti-hallucination rule:** writer ONLY mentions tickers that appear verbatim in the data blocks fed in (`recent_reports`, `recent_closes`). NO $SPY/$QQQ/$IWM/$DIA filler.

## x-poster post types — current canonical (2026-05-07)

| Type | Disclaimer | URL allowed | Notes |
|---|---|---|---|
| `signal` | none | `https://gammarips.com` (root) | **Path B 5/7** — anchors ticker + direction + score, withholds contract. Anchors enable receipt-style QRTs from `win`/`loss`/`callback` later. Fired by `x-poster-signal-0800` cron. |
| `watchlist` | none | none | 3 tickers ranked by call+put dollar volume; excludes paid pick. Fired by `x-poster-watchlist-0905` cron. |
| `standby` | none | none | Fires when no V5.3 pick today (gate-cleared empty or fail-closed). |
| `teaser` | none | none | Runner-ups bench post (rarely scheduled). |
| `report` | none | `gammarips.com/reports/<date>` (one only) | Weekly Mon 06:30 ET only. |
| `win` | `⚠️ Paper-trade. Not advice.` | none | QRTs originating SIGNAL anchor via `find_originating_post_for_ticker`. **NVAX 5/12 close = first real test of this loop.** |
| `loss` | `⚠️ Paper-trade. Not advice.` | none | NEUTRAL single, no QRT. |
| `callback` | `⚠️ Paper-trade. Not advice.` | none | Restricts to publicly-posted tickers. |
| `scorecard` | `⚠️ Paper-trade. Not advice.` | none | Restricts to publicly-posted tickers (lookback 10 days). First fire Fri 5/8 17:00 ET. |

## Firestore schemas relevant to content

| Collection | Schema | Writer | Reader |
|---|---|---|---|
| `todays_pick/{date}` | scan_date, decided_at, has_pick, ticker, direction, contract, score, vix3m_at_enrich, vix_now_at_decision, policy_version | signal-notifier (dual-write under scan_date AND entry_day) | webapp banner, MCP, x-poster watchlist planner (for exclusion lookup), gamma-bot |
| `daily_reports/{date}` | scan_date, title, headline, content, bullish_count, bearish_count, total_signals, seoMetadata | overnight-report-generator | x-poster report planner, blog-generator newsletter, webapp `/reports/[date]` |
| `x_posts/{date}_{type}` | scan_date, post_type, text, tweet_id, image_url, iterations, error, dry_run, posted_at | x-poster Publisher | callback ticker-restrict lookup, win/loss QRT lookup |
| `blog_posts/{slug}` | slug, title, description, markdown, keywords, cta, reviewer_score, iterations, status, reading_time_min, published_at | blog-generator Publisher | webapp `/blog/[slug]`, newsletter "What we wrote" excerpt |
| `blog_schedule/current` | version, rows[] (13-row 90-day plan) | seed script | blog-generator planner |
| `blog_config/voice_rules` | rendered, retired_aliases, banned_phrases, disclaimer_long, disclaimer_short | seed script | blog-generator (also imports gammarips_content) |
| `users` | email, displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId. **211 docs, all have email.** | webapp signups | content-drafter `read_email_audience` |
| `park_watchdog/gate_30_alerted` | one-shot flag | win-tracker | win-tracker (idempotency) |

## What's left to do (as of 2026-05-07)

**Priority 1 — validation (next ~5 days, no code work):**

1. **5/8 (Fri) 08:00 ET** — first auto-fire of `x-poster-signal-0800` against tomorrow's pick (or standby). Verify Path B template renders cleanly with whatever signal-notifier writes. If pick is empty, verify graceful STANDBY fallback.
2. **5/8 (Fri) 17:00 ET** — first auto-fire of `x-poster-scorecard-fri-1700`. Cohort has 1 trade in flight (NVAX), 0 closed. Should gracefully no-op via `no_scorecard_trades` skip.
3. **5/12 (Mon)** — **NVAX exits, the receipt loop gets its first real test:**
   - X: `x-poster-callback-1645` fires; `find_originating_post_for_ticker("NVAX")` should return `2052419298035900592` (the manually-planted anchor); win/loss callback QRTs it.
   - Reddit: trigger `reddit-poster /post {pnl_receipt}` manually; draft lands in `gs://gammarips-reddit-drafts/2026-05-12/pnl_receipt_options.md` with cohort tally `1/1.` or `0/1.` depending on outcome.
   - Forward-paper-trader writes `signal_performance/{NVAX,2026-05-07}` (cohort_stats/current updates).

**Priority 2 — pending user-side actions (optional, none blocking):**

4. **Reddit creds (only needed to flip DRY_RUN→false)** — manual cross-posting from GCS drafts works now without these. Create when ready:
   - Reddit script app at https://www.reddit.com/prefs/apps
   - 4 secrets: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`
   - Re-add `--set-secrets` line to `reddit-poster/deploy.sh` (currently commented out with NOTE)
5. **GA4 + GSC analytics access** for `/weekly_intel` to populate with real traffic (GA4 property ID + GSC verified URL + grant Viewer to default compute SA).
6. **FMP key rotation** — leaked in Cloud Logging URL between ~11:30–14:30 UTC 5/7 (free-tier key, hygiene not crisis).
7. **Email list consolidation + unsubscribe link** before any third newsletter blast (CAN-SPAM hardening).
8. **Mailgun spam-folder watch** — 4/28 SNDK pick landed in Gmail spam; deliverability monitoring matters now that auto-blast fires Mondays.

**Priority 3 — cleanup (low-value, defer):**

9. `agent-arena` is dead — Cloud Run service still exists. Propose deletion if touched.
10. `blog-generator` was previously blocked on dangling-state-ref fix; verify before next blog cron fires Mon.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` with subject `[GammaRips] 30-trade gate reached — return trigger active` when V5.3 closed-trade count ≥ 30. Estimated arrival: end of May / early June 2026 at the current ~1-2 trades/week public-pick pace.

When the email lands, the 90-day plan Wk 9-12 sequence kicks in: 30-trade-in-the-books blog post, paid-funnel hard via newsletter, x-poster cadence shifts to recap-led mode.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-05-07-receipt-content-strategy.md`** — what shipped 5/7 (Path B + Reddit distraction-frame + FMP migration). Most recent load-bearing context.
2. **`docs/DECISIONS/2026-04-30-content-machine-live.md`** — first wave of content surfaces.
3. `CHEAT-SHEET.md` — operator V5.3 trading routine (unchanged).
4. `docs/DECISIONS/2026-04-28-blog-gen-prod-text-only-x.md` — text-only x-poster + dual-write pick + first blog deploy.
5. `docs/EXEC-PLANS/2026-04-27-90-day-content-plan.md` — 90-day GTM plan.
6. `docs/ARCHITECTURE.md` — service map + data flow.
7. `gammarips-mcp/SECURITY.md` — trust model. Read before adding any MCP tool.

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## Definition of "GammaRips finished" (Evan's stated intent — ALL 4 NOW LIVE)

| Surface | Status |
|---|---|
| **`x-poster`** — @gammarips X publisher, 5 schedulers | ✅ LIVE (rev `00022-jpb`). Watchlist 09:05 (replaces signal); callback / scorecard restrict to posted tickers. |
| **`blog-generator`** — auto-publish weekly to Firestore + render on `/blog` | ✅ LIVE (rev `00017-zw6`). First scheduled fire **Mon 2026-05-04 05:00 ET** for `why-uoa-is-mostly-noise`. |
| **`reddit-drafter`** — Thu 10:00 ET, 3 GCS markdown drafts → email Evan | ✅ LIVE (same blog-generator service). Drafter NEVER auto-posts. Tier-1 subs: r/options, r/thetagang, r/algotrading. |
| **Email-marketing** — Sun 17:00 ET cron → `/draft_email` operator preview; manual `/blast_email` for user list | ✅ LIVE. Newsletter design locked 4/30 with featured-trade FOMO + green win color + FOUNDER29 coupon. |

Park condition active. Return when 30-trade gate fires.

---

## DO NOT do

- Do NOT modify V5.3 execution policy. Entry 10:00 ET / stop −60% / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT use FMP. Retired 2026-04-08 from forward-paper-trader.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27.
- Do NOT add a customer-facing chat agent in V1. The bot is sandboxed to `gammarips-mcp` and routes group `@gamma` mentions only.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record. Founder pricing $29/mo with FOUNDER29 (or $39 base) is the only commercial surface.
- Do NOT add MCP tools without `safe_error` / `clamp` / schema whitelist.
- Do NOT publish real-money track record until V5.3 has ≥30 closed trades.
- Do NOT re-add editorial images to x-poster. Text-only is the editorial decision (2026-04-28).
- Do NOT add the `⚠️ Paper-trade. Not advice.` disclaimer to watchlist/signal/standby/teaser/report posts. Disclaimer is only for realized-P&L recap posts.
- Do NOT name a new ADK service endpoint `/run`. ADK reserves it. Use `/post`, `/generate`, `/draft_*`, etc.
- Do NOT run any seed/migration script without `PROJECT_ID=profitscout-fida8` prefix. Shell has `PROJECT_ID=profitscout-lx6bb` set; missing prefix writes to wrong project.
- Do NOT deploy a new Cloud Run service with a custom service account unless there's a hard isolation requirement. Use the default compute SA `406581297632-compute@developer.gserviceaccount.com` — it inherits Vertex AI / logging / Firestore / GCS via project Editor.
- Do NOT post the V5.3 paid daily pick on X. Watchlist posts must EXCLUDE the paid pick (already enforced by planner instruction; don't unenforce).
- Do NOT broadcast the V5.3 contract (strike / expiration / mid / DTE / V/OI) on X SIGNAL posts. Path B 5/7 is anchor-only (ticker + direction + score, withhold the rest). The contract is the paid product.
- Do NOT write Reddit posts longer than ~250 chars. Trades + receipts only, distraction-frame voice, no methodology, no literature citations. See `feedback_reddit_short_distraction.md`.
- Do NOT include the multi-row "V5.3 trades that closed" table in the newsletter — Evan locked 4/30 on featured-trade-only design.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier deploys.** Not needed for x-poster / blog-generator / mcp / content-drafter.

No content-strategist agent exists yet. Per 2026-04-28 discussion: don't spawn one until ~Wk 5 of the 90-day plan, after enough cross-channel output exists to audit for cohesion.

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest additions:
- **2026-05-07** `feedback_reddit_short_distraction.md` — Reddit posts must be short distraction-frame, max ~250 chars; no literature citations or gate walkthroughs. Long posts get karma-killed.
- **2026-05-06** `project_v5_3_lit_audit_2026_05_06.md` — H11 + H12 deployed, H13 deferred (breaks RH routine).
- **2026-04-30** `feedback_default_compute_sa.md` — Cloud Run services use default compute SA.
- **2026-04-30** `project_finished_definition.md` — all 4 surfaces LIVE.

Earlier (still load-bearing):
- `project_no_disclaimer_no_images.md` — text-only x-poster, disclaimer scope rule.
- `project_todays_pick_dual_write.md` — `signal-notifier` writes both keys.
- `feedback_adk_route_reserved.md` — ADK claims `/run`; use `/post`, `/generate`, etc.
- `feedback_seed_script_project_env.md` — shell `PROJECT_ID=profitscout-lx6bb` traps seed scripts.
- `project_email_only_delivery.md` — WhatsApp deprecated.
- `project_mcp_hardened.md` — MCP attack surface contract.
- `feedback_no_own_subreddit.md` — Discord, not r/gammarips.
- `feedback_simplicity.md` — minimum-knob plans.
- `project_founder_pricing.md` — $29/mo with FOUNDER29 coupon (no S), uncapped.
- `project_capital_constraint.md` — user can't trade picks personally.

---

*End of handoff. The trade → anchor → receipt loop is wired. Now it runs and the SEO + receipt cadence builds traction. Wake me when the 30-trade gate fires (`evan@gammarips.com` will get the email), or earlier if NVAX 5/12 close shows the receipt loop didn't fire as expected.*
