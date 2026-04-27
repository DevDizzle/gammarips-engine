# EXEC-PLAN: 90-Day GTM Content Plan — 2026-04-28 → 2026-07-27

**Date:** 2026-04-27
**Owner:** Evan (manual reply windows + final-publish toggles only). Claude services do the drafting.
**Anchor milestone:** V5.3 ledger reaches **30 closed trades** (~end of May 2026, ~Wk 5). All track-record-led copy is gated on that milestone.
**Companion docs:** [`2026-04-24-100-day-gtm-plan.md`](./2026-04-24-100-day-gtm-plan.md), [`2026-04-20-copy-seo-content-overhaul.md`](./2026-04-20-copy-seo-content-overhaul.md), `forward-paper-trader/main.py`, `libs/gammarips_content/`.

This plan is calibrated to one operator who wants the engine to run unattended. Every recommendation reuses an existing service or extends `blog-generator`'s scaffold. No new Cloud Run service beyond a single `content-drafter` (Reddit + email variant).

---

## Section 1 — 90-day calendar

Trade-data milestone gating:
- **Phase 1 — Wk 1–4 (Apr 28 → May 25):** ~0–10 closed trades. Methodology-led, building-in-public, no win-rate claims.
- **Phase 2 — Wk 5–8 (May 26 → Jun 22):** ~10–25 closed trades. Cohort sketches, weekly recaps with ledger snippets, careful "early read" framing.
- **Phase 3 — Wk 9–12 (Jun 23 → Jul 27):** ≥30 closed trades. Track-record-led, paid-tier comparison, scale Reddit + email reach.

| Wk | Phase | Blog (auto Mon 05:00 ET) | Reddit drafts (3/wk) | Email theme (1/wk) | Notes |
|----|-------|--------------------------|----------------------|--------------------|-------|
| 1  | 1 | **Why UOA alone is mostly noise** — kw `unusual options activity false signals`. Links: /how-it-works, /about. Cites: enrichment gate stack (`score>=1`, `spread<=10%`, UOA `>$500K`). | r/options (gate-stack); r/thetagang (skip-day); r/algotrading (deterministic engine). | Welcome v2 — "what to expect 90 days." | Blog-generator first live run. No ledger numbers. |
| 2  | 1 | **The V5.3 bracket: why -60/+80/3-day** — kw `options stop loss bracket`. Links: /pricing, Wk 1. Cites: `docs/DECISIONS/2026-04-17-v5-3-target-80.md`. | r/options (bracket math); r/Daytrading (3-day hold); r/algotrading (paper methodology). | "Reading the engine even with no signal." | First Reddit-drafter run. |
| 3  | 1 | **Paper-trading as data-quality gate** — kw `paper trading validation methodology`. Links: /about, Wk 1, Wk 2. Cites: `forward_paper_ledger` schema, `libs/trace_logger`. | r/options (transparency); r/SecurityAnalysis (process); r/quant (deterministic vs stat-arb). | Engine-mechanics deep-dive. | Schema + trace logging. |
| 4  | 1 | **VIX/VIX3M term-structure as a gate** — kw `VIX term structure options`. Links: /how-it-works, Wk 2. Cites: `signal-notifier` `VIX <= VIX3M`, FRED VIX. | r/options (term structure 101); r/thetagang (vol regime); r/Daytrading (gate explainer). | "Why bearish trades aren't broken" (war-chop regime). | Last pure-methodology week. |
| 5  | 2 | **First 10 closed paper trades** — kw `paper trading results options`. Links: Wk 1–4. Cites: `get_historical_performance` MCP tool (small-N caveat). | r/options (early-read); r/thetagang (first-stop post-mortem); r/algotrading (methodology+sample). | "First 10 trades" recap, ledger snippet, no rate claims. | First Reddit post citing real trades. n=10, not significant. |
| 6  | 2 | **Anatomy of a stop: what -60% looked like** — kw `options stop loss case study`. Links: Wk 2, Wk 5. Cites: closed-loser row from ledger. | r/options (loss post-mortem); r/Daytrading (mechanical stop); r/SecurityAnalysis (audit loser). | Loss-callback newsletter. | Loss-led week reinforces transparency. |
| 7  | 2 | **Why we skip ~40% of days** — kw `selective options trading`. Links: Wk 1, Wk 4. Cites: enrichment hit rate from BQ. | r/options (anti-firehose); r/thetagang (one-trade-a-day); r/investing (FOMO). | Skip-day stats + "no-signal is a signal." | Selectivity is a feature. |
| 8  | 2 | **Cohort sketch: bull vs bear in war-chop regime** — kw `options regime analysis 2026`. Links: Wk 4, Wk 5. Cites: ledger direction split + VIX. | r/options (regime); r/SecurityAnalysis (macro overlay); r/algotrading (cohort+disclaimers). | Mid-May ledger snapshot. | Last "early read" week. Sets up Wk 9. |
| 9  | 3 | **30 trades in: what the ledger says** — kw `paper trading 30 trade sample options`. Links: Wk 5, 6, 8. Cites: `get_historical_performance` (rate, avg R, expectancy). | r/options (30-trade reveal); r/thetagang (expectancy); r/algotrading (full summary). | **30-trade newsletter** — numbers + founder pricing CTA. | First track-record-led post. $39 only. |
| 10 | 3 | **What 30 trades tell us — V5.3 vs V4** — kw `options strategy backtest comparison`. Links: Wk 9, decision doc. Cites: V5.3 vs retired V4. | r/options (strategy iteration); r/algotrading (ledger compare); r/quant (survivorship). | "Why we changed the bracket" — decision trail. | Methodology + numbers. |
| 11 | 3 | **Free vs paid tier: what you actually get** — kw `options signal service review`. Links: /pricing, Wk 9. Cites: `signal-notifier` gates, x-poster cadence. | r/options (pricing transparency); r/thetagang (free/paid split); r/Daytrading (workflow). | Win-back drip starts. $39, no scarcity. | First paid-conversion week. |
| 12 | 3 | **90 days of building in public — what changes for Q3** — kw `options trading transparency report`. Links: Wk 1, Wk 9, /about. Cites: full ledger + roadmap. | r/options (retro); r/SecurityAnalysis (process retro); r/algotrading (`gammarips-mcp` 18-tool surface). | Q3 roadmap newsletter. | Park-mode handoff. |

Working titles only — `blog-generator` planner finalizes per `read_voice_rules()`. Calendar assumptions (V5.3 ~2 trades/wk; 3 Reddit drafts/wk total, not per sub) flagged in Section 6.

---

## Section 2 — Reddit subreddits + posting rules

Discord vs own subreddit (aside): **do not start r/gammarips.** Cold-start failure mode for a small brand — empty subs signal abandonment. If/when community demand exists (Phase 3, post-30-trade), spin up a Discord with a `#signals` channel mirroring x-poster output. Discord wins on discovery (server-list + invites) and on real-time community formation. Re-evaluate at Wk 12.

### Tier 1 — High priority (post weekly)

| Sub | Subs | Best window (ET) | Karma min | Lead with | Never do | GammaRips angle |
|-----|------|------------------|-----------|-----------|----------|-----------------|
| r/options | 1.2M | Tue–Thu 09:00–11:00 | 100 | Concrete mechanic (gate stack, bracket math, term structure). Show numbers. | Link to gammarips.com in body; mention "subscribe"; cherry-pick winners. | Methodology, transparency, deterministic engine. |
| r/thetagang | 230K | Tue–Thu 12:00–14:00 | 50 | Why selective > firehose; loss post-mortems; expectancy framing. | Recommend long-premium without volatility context (sub is short-vol-coded). | Discipline, skip-day rationale, small-account routine. |
| r/algotrading | 270K | Mon–Wed 10:00–13:00 | 100 | Architecture posts, MCP tool surface, BQ schema, paper-trading-as-validation. | Backtest hindsight without OOS framing. | Tooling depth, `gammarips-mcp`, deterministic pipeline. |

### Tier 2 — Medium priority (post bi-weekly Wk 5+)

| Sub | Subs | Best window | Lead with | Never do | Angle |
|-----|------|-------------|-----------|----------|-------|
| r/Daytrading | 2.5M | Tue–Fri 08:00–10:00 | Workflow / one-trade-a-day routine post. | Promo post; "follow my signals." | Working-professional fit — 9 AM push. |
| r/SecurityAnalysis | 320K | Wed–Thu 14:00–17:00 | Process posts, decision trail, methodology rigor. | Promotional copy. | Long-form analysis posts only. |
| r/investing | 2.6M | Tue–Thu 09:00–12:00 | Educational explainers (UOA, term structure). | Anything that reads as a pitch — heavy mod hand. | Education-only, no tier mention. |
| r/quant | 200K | Wed 10:00–13:00 | Sample-size discipline; cohort caveats; explicit OOS framing. | Pretend N=20 is significant. | Honest small-sample posts. |

### Tier 3 — Skip until ≥30 closed trades (Wk 9+) OR skip permanently

| Sub | Why |
|-----|-----|
| r/wallstreetbets | NEVER post until Phase 3 minimum, and even then high-risk. Mod hammer for "signal services." Loss-porn culture incompatible with disciplined-anti-hype voice. |
| r/pennystocks | Audience mismatch. Skip permanently. |
| r/RobinhoodTraders | Audience mismatch + brand drift risk. Skip permanently. |
| r/StockMarket | Low signal/noise mods, frequent removals of methodology posts. Skip Phase 1. Reconsider Wk 9. |

### Universal Reddit rules

1. Never link to gammarips.com in post body — drop URL in a comment 30+ min later if asked. Bio link only.
2. Lead with chart/number, not conclusion. Reddit votes in the first 2 min.
3. 9:1 give:ask ratio.
4. Every post ends with `Paper-trade. Not advice.` (`voice_rules.py:DISCLAIMER_SHORT`).
5. Never use retired aliases. Drafter MUST run `compliance.score_against_rubric()` pre-email.
6. Evan replies within 60 min in the post's first 4 hr — only manual-time burden in the plan.

---

## Section 3 — Reddit-drafter spec (build-ready)

**Service:** `content-drafter` — NOT a new Cloud Run service. Extends the `blog-generator` scaffold with two endpoints. The planner→writer→reviewer loop, voice-rules tool, live-context tool, and rubric scorer are the same primitives a Reddit drafter needs. Forking creates voice drift.

**Endpoints added to `blog-generator/app/fast_api_app.py`:**
- `POST /draft_reddit` — `{"sub","theme","dry_run"}` → returns `{gcs_uri, target_window, post_instructions}`.
- `POST /draft_email` — `{"theme","list"}` → returns Mailgun-template-ready HTML written to GCS.

**Shared with blog-generator (zero duplication):** `read_voice_rules()`, `read_prior_posts()` (Reddit cites blog), `read_live_context()` via `gammarips-mcp.get_historical_performance` (Phase 2+), `score_against_rubric()` extended with per-surface rules (Reddit: no URLs in body, ≤300 words for short posts, lead-with-number check; Email: subject ≤50 chars).

**Per-subreddit voice variance:** New tool `read_subreddit_voice(sub) -> dict` reads `content_config/subreddit_voice/{sub_slug}` (`{lead_style, taboo_phrases, length_range, common_mod_traps}`). Seeded via `scripts/seed_subreddit_voice.py`. Writer injects dict into system prompt — **same writer agent**, contextual prompt only.

**Thu 10:00 ET email to Evan** (Cloud Scheduler `content-drafter-weekly-reddit`):

```
Subject: GammaRips Reddit drafts ready — week of Jun 3

1. r/options — "The V5.3 -60/+80 bracket math"
   Draft: gs://gammarips-content-drafts/reddit/2026-06-03_r-options.md
   Target: Tue Jun 4 10:30 ET
   Copy-paste: open GCS link, copy body, paste into r/options "New post"
   form. Title: <pre-written>. Flair: "Strategy". Crossposting off. Publish,
   then pin first comment from gs://...comment.md within 30 min.
2. r/thetagang — ...   3. r/algotrading — ...

Compliance: PASSED (audit log gs://.../audit.json)  Reviewer: 8.7 / 8.4 / 9.1
```

**Cost:** ~300 LOC in blog-generator app, ~80 LOC Mailgun digest. One scheduler job. ~1 day.

**Hard rules:**
- Drafter MUST NOT auto-post. Email-to-Evan only (mod-relationship + SEC v. Lowe risk).
- Drafts live in GCS, not in the email body — versionable, Evan can edit pre-post.
- A draft that fails `compliance.score_against_rubric()` never ships. Hard fail + Firestore alert.

---

## Section 4 — Email marketing plan

**Stack:** Mailgun (already configured for trial-end pattern). List in Firestore `email_subscribers/{uid}`. Target list = free signups + WhatsApp invitees (one-time import, no re-engagement) + churned trials + blog email-capture (new `<EmailCaptureCard>` on `/blog/[slug]`). Day-1 list ~200–500; Day-90 target 600–1,300.

### Lifecycle emails (priority order)

| Email | Trigger | Ship | Body source |
|-------|---------|------|-------------|
| 1. Welcome v2 | Firebase signup | Wk 1 | Static + dynamic first-name |
| 2. Weekly newsletter | Sun 17:00 ET cron | Wk 1 | `content-drafter` `/draft_email` |
| 3. Trial-ending | 24h before Stripe end | Wk 2 | Static + ledger snapshot (Wk 5+) |
| 4. Win-back | 30d post-cancel | Wk 11 | Static + 30-trade snapshot — needs Phase 3 |

### Weekly newsletter

**Cadence:** Sun 17:00 ET — catches Sunday-night planners; 12-hr gap before Mon blog; avoids Tue/Wed promo glut.

**Template (Mailgun MJML):**

```
Subject: GammaRips weekly — {{week_label}} ({{closed_count}} trades closed)
Preheader: {{one_line_summary}} — paper-trade. Not advice.

## This week's signals       ← get_historical_performance(window="last_week")
## Engine state              ← {{closed_count}} | latest blog link
## What we wrote             ← 150-word excerpt of latest blog_posts/{slug}
## Runners-up we passed on   ← get_enrichment_log(filter="failed_signal_notifier")
## Disclaimer                ← canonical long form
```

**Content reuse:** `content-drafter`'s email writer reads `blog_posts/{latest_slug}`, re-summarizes the intro to 150 words. Same voice, same compliance check.

**CTA in every email:** `$39/mo founder pricing — no seat cap`. NEVER use scarcity copy (500-seat cap superseded 2026-04-24).

---

## Section 5 — "GammaRips finished" — park-mode checklist

Park-mode = the engine trades + writes content unattended; Evan returns when V5.3 ledger crosses 30 closed trades.

### Must be running unattended

| System | Trigger | Failure mode | Monitor |
|--------|---------|--------------|---------|
| `forward-paper-trader` `/` | Cron weekday 10:00 ET | No trade logged | Cloud Run 5xx alert |
| `forward-paper-trader` `/cache_iv` | Daily | Stale IV pricing | Cloud Run logs |
| `enrichment-trigger` | Pub/Sub | No enriched signal | BQ row-count alarm |
| `signal-notifier` | After enrichment | No daily signal email | Mailgun logs + `daily_signals/{date}` |
| `x-poster` 5×/day | Cron | Empty/dupe posts | Cloud Run logs + weekly @gammarips spot-check |
| `blog-generator` Mon 05:00 | Cron | No Mon post | Firestore `blog_posts` write-watch |
| `content-drafter` Thu 10:00 | Cron | No Reddit drafts | Mailgun logs |
| `content-drafter` Sun 17:00 | Cron | No newsletter | Mailgun logs |
| `win-tracker` daily | Cron | Outcomes stale → 30-trade gate breaks | BQ `outcome` null-rate alarm |

### Alerting (build before declaring parked)

- Cloud Monitoring uptime checks on every `/health` endpoint.
- Single alert channel → `evan@gammarips.com`.
- Daily 07:00 ET digest email: yesterday's trades, signal, blog, Reddit, X. Reuses `content-drafter`.
- **30-trade gate watcher** — Cloud Function on BQ insert; emails Evan when `closed_trade_count == 30`. This is the return trigger.

### "You're not done if X"

- 30-trade gate watcher doesn't exist (Evan still checks BQ manually).
- Any service can fail silently — every service must `/health` + log → alert.
- `blog-generator` reviewer iteration-limit fallback (DESIGN_SPEC §1.4) untested.
- Mailgun newsletter test send hasn't verified ≥98% delivery to a small cohort first.
- `compliance.score_against_rubric()` isn't blocking publish on every surface (blog + Reddit + email).
- No kill-switch — add Firestore `engine_state/active=false` flag every scheduled job checks first.

Before walking: update `NEXT_SESSION_PROMPT.md` with the 30-trade gate as return trigger + per-service runbook.

---

## Section 6 — Risk calls

**Plan-level judgment calls (flagged):**
- 3 Reddit drafts/wk is *total*, not per sub — load-bearing for solo-operator capacity.
- Phase 2/3 boundaries assume V5.3 hits 30 trades by end of May. If signal cadence <2/wk, slide right.
- Mailgun reputation not re-verified since trial-end campaign.
- Single `content-drafter` covers Reddit + email + digest. Fork only if complexity forces it; until then, fork = voice drift.

**Blog (`blog-generator`)**
- Reviewer hallucinates ledger numbers in Phase 1 — `read_live_context()` must hard-skip on evergreen posts; verify Wk 1.
- SEO lag — Wk 1 post won't rank until ~Wk 4. Don't measure blog conversion before Wk 6.
- Planner/writer temp drift — lock both at ≤0.4.

**Reddit (`content-drafter`)**
- Mod ban / shadowban risk — weekly posting to same sub with even soft promo gets flagged in ~6 wk. Manual check: incognito view of own post after publish.
- Karma minimums — if Evan's account is under thresholds, comment-only for 2 wk before Wk 1 posting.
- Small-N audience mismatch — r/quant requires `n=X, OOS` framing on every numbers post; reviewer must enforce.

**Email (Mailgun)**
- Reputation regression — never blast 500+ cold WhatsApp invitees at once. Warm with active free signups for 2 wk, then add cohorts of ~100 every 3 days.
- Sun 17:00 ET conflict — A/B test Mon 06:30 ET in Wk 6 if open rates lag.
- First-send unsubscribe spike — expected; if >5%, scorer's `promo_density` flag failed pre-send.

**X (`x-poster`, cross-promo only)**
- Add 3 cross-promo `post_type` values (~30 LOC): Mon 06:30 (blog teaser), Sun 17:30 (newsletter teaser), Wed 10:30 (Reddit teaser).
- Voice drift across surfaces — `libs/gammarips_content/voice_rules.py` must remain the single source; verify all 3 services import the same module.
- `compliance.score_against_rubric()` must wire into content-drafter from day one (already in x-poster + blog-generator).

**Trade-data milestone (load-bearing)**
- If V5.3 has <20 closed trades by Wk 9, do NOT advance to Phase 3. Hold methodology framing and re-plan. One premature track-record post does multi-month credibility damage.
- If trades come in but win rate is bad, the plan doesn't change — losses ship per voice rule. Loss callbacks build credibility faster than victory laps.

---

**Next action:** deploy `blog-generator` per `NEXT_SESSION_PROMPT.md` priority 4, then extend into `content-drafter` per Section 3.
