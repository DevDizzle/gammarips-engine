# Next Session Prompt

**Last session wrapped:** 2026-05-04 — **marketing surfaces actually go live + analytics intel cron wired.** Fixed silent x-poster failure (watchlist missing from FastAPI literal → 422 every 09:05 ET since 4/30). Email moved off "no drafts" — added `/blast_latest` with kill-switch and idempotency, scheduled Mon 05:30 ET auto-blast. X cleanup: teaser deleted, report demoted to weekly Mon 06:30 ET. New `reddit-poster` service skeleton (DRY_RUN, trade_idea + pnl_receipt only — addresses "AI slop" complaints). New `/weekly_intel` Mon 07:00 ET cron with GA4/GSC stubs (degrade to "unavailable" until creds land). **Open user actions remain — see "User to-do (2026-05-04)" section below.**

**Prior session (2026-04-30):** content machine first wave — all 4 surfaces went LIVE but with operator-only email and Reddit-as-draft. Park condition was set. Today's session is the unblock pass.
**Current policy:** V5.3 "Target 80" — execution unchanged.
**V5.4 direction (experimental, NOT live):** agent-driven dynamic criteria. See memory `project_v5_4_dynamic_criteria.md`.

---

## TL;DR for the next session

1. **Park is active.** Win-tracker emails `evan@gammarips.com` when V5.3 hits 30 closed trades — that's the return signal. Until then, sessions should focus on (a) silent-breakage fixes if you spot any, and (b) operating the content cadence.
2. **No new features without strong reason.** All 4 surfaces are intentionally stable.
3. **Read first:** [`docs/DECISIONS/2026-04-30-content-machine-live.md`](docs/DECISIONS/2026-04-30-content-machine-live.md) — full diff of what shipped today, including every revision tag, every cron, every rubric tweak.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `x-poster` | `00023-bw6` | LIVE, DRY_RUN=false. **Watchlist literal fix 5/4** — `watchlist` added to FastAPI `PostRequest.post_type` (was 422-ing every 09:05 ET since 4/30). |
| `blog-generator` | `00019-bwk` | LIVE, DRY_RUN=false. **NEW `/blast_latest`** auto-blast endpoint (kill-switch via `blast_killswitch/<date>`, idempotent on `blast_history/<date>`). **NEW `/weekly_intel`** GA4+GSC+ledger intel report (GA4/GSC degrade gracefully when env vars unset). |
| `reddit-poster` | NOT YET DEPLOYED | Service skeleton built 5/4 in `/reddit-poster/`. DRY_RUN=true default. Two post types only: `trade_idea`, `pnl_receipt`. Blocked on user creating Reddit script app + 4 Secret Manager entries. |
| `signal-notifier` | `00009-cd5` (verify on next deploy) | LIVE. Paid-only Mailgun fan-out. Dual-writes `todays_pick/{scan,entry}`. |
| `win-tracker` | `00010-rkn` | LIVE. **30-trade gate watcher armed.** One-shot email to `evan@gammarips.com` when V5.3 ledger crosses 30 closed trades. Idempotent via Firestore `park_watchdog/gate_30_alerted`. |
| `gammarips-mcp` | `00027-mcl` | 18 tools. Sole sandboxed-bot attack surface. |
| `forward-paper-trader` | unchanged | V5.3 ledger active. Trader runs brackets on every enrichment signal (no trader-side filter). |
| `enrichment-trigger` | unchanged | gates: score≥1, spread≤10%, UOA>$500K. |
| `agent-arena`, `overnight-report-generator`, `gammarips-eval` | unchanged | overnight-report-generator writes `daily_reports/{date}` (NOT `overnight_reports/`). |
| `webapp` | latest | `/blog/[slug]` renders Firestore `blog_posts/{slug}`. `/reports/[date]` renders `daily_reports/{date}`. **Templates may differ visually — Evan flagged 4/30 they should match. Webapp-side work, not in this repo.** |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `agent-arena-trigger` | 06:00 | agent-arena | |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | writes `daily_reports/{date}` |
| **`x-poster-report-0830`** | **Mon 06:30** | x-poster `/post {report}` | **demoted from daily 5/4** |
| `signal-notifier-job` | 09:00 | signal-notifier | dual-writes pick |
| **`x-poster-signal-0905`** | **09:05** | **x-poster `/post {watchlist}`** | **fixed 5/4** (literal gap) |
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

## x-poster post types — current canonical (2026-04-30)

| Type | Disclaimer | URL allowed | Notes |
|---|---|---|---|
| `watchlist` | none | none | NEW 4/30 — replaces `signal`. 3 tickers ranked by call+put dollar volume, exclude paid pick. |
| `signal` | none | none | Retained as code path. Cron `x-poster-signal-0905` no longer sends this payload. |
| `standby` | none | none | |
| `teaser` | none | none | |
| `report` | none | `gammarips.com/reports/<date>` (one only) | |
| `win` | `⚠️ Paper-trade. Not advice.` | none | QRTs originating watchlist post via `find_originating_post_for_ticker` |
| `loss` | `⚠️ Paper-trade. Not advice.` | none | NEUTRAL single, no QRT |
| `callback` | `⚠️ Paper-trade. Not advice.` | none | restricts to publicly-posted tickers |
| `scorecard` | `⚠️ Paper-trade. Not advice.` | none | restricts to publicly-posted tickers (lookback 10 days) |

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

## User to-do (2026-05-04)

These are blocked on the user, not on Claude. Each is single-shot.

1. **Today's blast** (`2026-05-03_newsletter.html`) — when ready, fire:
   ```
   curl -X POST https://blog-generator-406581297632.us-central1.run.app/blast_latest \
     -H "Content-Type: application/json" -d '{"audience":"all","dry_run":false}'
   ```
   Goes to 212 users. Confirmed dry-run today returned `audience_count=212, sent=1` (operator preview). After this fires once, future Mondays auto-blast at 05:30 ET. Set `blast_killswitch/2026-05-03 {aborted:true}` if you change your mind before firing.

2. **Reddit auto-poster — give Claude the creds** so I can deploy:
   - Create Reddit script app at https://www.reddit.com/prefs/apps (type: script).
   - Add 4 secrets to Secret Manager:
     ```
     gcloud secrets create REDDIT_CLIENT_ID --replication-policy=automatic --project=profitscout-fida8
     printf "%s" "<value>" | gcloud secrets versions add REDDIT_CLIENT_ID --data-file=- --project=profitscout-fida8
     # repeat for REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
     ```
   - Create draft bucket: `gsutil mb -p profitscout-fida8 -l us-central1 gs://gammarips-reddit-drafts`
   - Tell Claude when done — I'll deploy `reddit-poster`, smoke-test in DRY_RUN, then schedule.

3. **GA4 + GSC analytics access** — needed for `/weekly_intel` to actually have traffic data:
   - Find GA4 property ID at analytics.google.com → Admin → Property Settings (numeric, ~9 digits).
   - Confirm GSC verified property URL (`https://gammarips.com/` or `sc-domain:gammarips.com`).
   - In GA4: Admin → Property Access Management → add `406581297632-compute@developer.gserviceaccount.com` as **Viewer**.
   - In GSC: Settings → Users and permissions → add same SA email as **Restricted user**.
   - Tell Claude the property ID + site URL → I'll redeploy with env vars and the next Mon 07:00 cron will have real traffic data.

4. **Reddit scope confirmation** — I built the service for `trade_idea` + `pnl_receipt` only. Subreddits default to r/options, r/thetagang, r/algotrading. Confirm or change before deploy.

5. **X-poster cleanup confirmation** — I deleted `teaser-1230` and demoted `report-0830` to Mon 06:30 ET only. Reverse with one gcloud command if you disagree.

6. **Decision points the reddit-poster build agent flagged** (need a yes/no):
   - Catalyst field name in `todays_pick/{date}` doc — is it `catalyst`, `headline`, or `top_bullets`?
   - `peak_return` vs `realized_return_pct` — which is the right sort key for "highest close in last 24h"?
   - Char budget: trade_idea 400-1500, pnl_receipt 200-700 — too long?

## Outstanding gaps (post-park work)

1. **Email list consolidation** — `users` collection (212 docs, all `isSubscribed=false` style) vs any unmerged form-capture path. Identify before scaling beyond 1 blast/week.
2. **Unsubscribe link in newsletter** — CAN-SPAM hardening before any third blast.
3. **Featured trade — restrict to publicly-posted tickers?** Currently picks top winner from any V5.3-bracket close. Tradeoff: smaller pool, more honest.
4. **Webapp `/blog/[slug]` should render visually like `/reports/[date]`** (Evan 4/30). Webapp template work, not in this repo.
5. **Watchlist first-fire verification** — Mon 5/4 09:05 ET fire MISSED today (422 since 4/30 — fixed mid-day 5/4). Tomorrow 5/5 09:05 ET is the first real test of the fix.
6. **Mon 5/4 first auto-blog** — slug `why-uoa-is-mostly-noise`. Verify Firestore `blog_posts/why-uoa-is-mostly-noise` lands and webapp renders cleanly.
7. **Mailgun spam-folder retraining** — 4/28 V5.3 SNDK pick email landed in Gmail spam (marked not-spam manually). Critical now that auto-blast fires Mondays — watch deliverability.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` with subject `[GammaRips] 30-trade gate reached — return trigger active` when V5.3 closed-trade count ≥ 30. Estimated arrival: end of May / early June 2026 at the current ~1-2 trades/week public-pick pace.

When the email lands, the 90-day plan Wk 9-12 sequence kicks in: 30-trade-in-the-books blog post, paid-funnel hard via newsletter, x-poster cadence shifts to recap-led mode.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-04-30-content-machine-live.md`** — what shipped 4/30 (this is the load-bearing context for the next session).
2. `CHEAT-SHEET.md` — operator V5.3 trading routine.
3. `docs/DECISIONS/2026-04-28-blog-gen-prod-text-only-x.md` — text-only x-poster + dual-write pick + first blog deploy.
4. `docs/EXEC-PLANS/2026-04-27-90-day-content-plan.md` — 90-day GTM plan (Apr 28 → Jul 27 2026).
5. `docs/ARCHITECTURE.md` — service map + data flow.
6. `gammarips-mcp/SECURITY.md` — trust model. Read before adding any MCP tool.

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

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest 4/30 additions:
- `feedback_default_compute_sa.md` — Cloud Run services use the default compute SA, not custom isolation SAs.
- `project_finished_definition.md` — flipped from "1 of 4 shipped" to "all 4 LIVE 2026-04-30".

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

*End of handoff. The content machine runs itself. Wake me when the gate fires.*
