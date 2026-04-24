# 2026-04-24 — x-poster + blog-generator ADK services + shared content lib

**Decision type:** New services (infra, code). No execution-policy changes.
**Scope:** `x-poster/` (new), `blog-generator/` (new), `libs/gammarips_content/` (new), `win-tracker/` (X posting removed), `gammarips-webapp/` (GA4 ID swap + dead cron delete — not yet pushed).
**Deployed:** `x-poster-00016-js8` (DRY_RUN=true). `blog-generator` scaffolded, not deployed. Engine commit `031110ec` local-only (not pushed).
**Reviewer:** Claude (primary) + Evan (direction + eyeball). 11 subagents spawned across the session (3 deploy/smoke agents for x-poster alone).

---

## Context

Prior session wrapped 2026-04-22 with paid tier live on gammarips-webapp + SSR crawlable. This session shifted focus from webapp to **distribution** — the engine-side automation that turns every overnight signal + closed trade + morning report into a @gammarips X post. Side-goal: stand up the parallel blog-generator infrastructure using the same ADK pattern so a single weekly cron can auto-publish to the webapp blog.

Coming into the session, x-poster did not exist. win-tracker had dormant X posting code (`post_win_to_x()`) that never ran because credentials were never mounted to its Cloud Run service. The webapp had stale GA4 measurement ID pointing at a long-deprecated "ProfitScout" stream, plus 4 scheduler entries in `apphosting.yaml` firing 404s at deleted cron handlers for 4 days.

## What shipped

### New service: `x-poster/`

ADK multi-agent pipeline for @gammarips X publishing. Cloud Run service, one `POST /post` endpoint, Cloud Scheduler routes 5 different `post_type` payloads to the same endpoint.

**Architecture:**
```
SequentialAgent
├── LoopAgent (max 3 iterations)
│   ├── Planner    — calls 6 fetch_* tools to gather data
│   ├── Writer     — renders the premium template for the post_type
│   ├── Reviewer   — structured APPROVE/REVISE (Pydantic)
│   └── EscalationChecker — escalate=True on APPROVE
└── Publisher      — image gen → X post → Firestore log
```

7 post types defined in writer instruction + compliance rubric:

| Type | Trigger (Cloud Scheduler) | Template anchor | Image |
|---|---|---|---|
| signal | Mon–Fri 09:05 ET | `🔥 GammaRips Signal — <scan_date>` | YES |
| standby | (fallback when signal has no pick) | `🛑 GammaRips Standby — <scan_date>` | YES |
| teaser | Mon–Fri 12:30 ET | `📡 Overnight flow — <scan_date>` | YES |
| report | Mon–Fri 08:30 ET | `📝 Overnight Brief — <scan_date>` | YES |
| win | Mon–Fri 16:00 ET (QRT of original) | `✅ CALLED IT — ...` | optional |
| loss | Mon–Fri 16:00 ET (neutral single, no QRT) | `❌ STOPPED OUT — ...` | none |
| scorecard | Fri 17:00 ET (3-tweet thread) | `📊 Week ending <scan_date>` | YES tweet 1 |

**Signal template matches Evan's premium WhatsApp format pixel-for-pixel** (verified on real data 2026-04-23 $APP):
```
🔥 GammaRips Signal — 2026-04-23

$APP BEARISH (Score: 6)
📕 PUT $425 | Exp: May 15
💰 Mid: $26.93 (~$2,693/contract) | 6.42% OTM
📊 V/OI: 7.33 | DTE: 21 | V5_3_TARGET_80

Entry Routine:
• 10:00 AM ET — Buy 1 contract at market
• Stop: -60% | Target: +80% (GTC)
• Hold max 3 days → close 3:50 PM day 3

⚠️ Paper-trade. Not financial advice.
```

### New service: `blog-generator/`

Same ADK Planner/Writer/Reviewer/Publisher shape, scoped to weekly blog posts. Writes Firestore `blog_posts/{slug}` for webapp rendering. `scripts/seed_schedule.py` one-shot seeder loads the 13-row 90-day schedule from the copy plan. **NOT yet deployed.** Requires the dangling-state-ref fix (task #15) before first deploy.

### New shared lib: `libs/gammarips_content/`

Vendored into each publisher service by `deploy.sh` (same pattern as `libs/trace_logger/`). Six modules:

- **`brand.py`** — all hex codes (`#a4e600` lime green, `#ffcc00` gold, `#cc3333` bear red, `#1a1f2e` dark bg) + Space Grotesk + Inter font refs + 8 voice markers + personality + visual-language strings, extracted directly from `gammarips-webapp/src/app/globals.css` (HSL→hex). Also exposes `LOGO_GCS = "gs://gammarips-x-media/brand_logo.jpg"`.
- **`compliance.py`** — 6-point rubric (char budget, retired-alias scan, disclaimer present, publisher framing, cashtag position, URL absence) + `canonicalize_draft_text()` that deterministically strips writer drift (disclaimer paraphrases, $SPY/$QQQ/$IWM/$DIA filler, `V/OI None` segments) and enforces the canonical disclaimer per post_type.
- **`tweepy_helper.py`** — OAuth 1.0a client w/ media upload, QRT support, `DRY_RUN=true` honor (returns fake `dry_run_*` tweet_id without hitting X API).
- **`firestore_helpers.py`** — `x_posts/` doc ID schema, idempotency check, QRT tweet_id lookup, `todays_pick` + `overnight_reports` readers.
- **`mcp_client.py`** — `McpToolset` factory for `gammarips-mcp` (phase 2; services currently use direct Firestore/BQ tools).
- **`voice_rules.py`** — prompt-ready rendering of voice rules + retired aliases + banned recommendation phrases.

### Brand assets in GCS (`gs://gammarips-x-media/`)

- `brand_logo.jpg` — the actual @gammarips wordmark + green triangle "A" Evan shared. PIL-composited deterministically onto bottom-right of every generated image at 12% width.
- `brand_ref_card.png` — copy of webapp og-image.png. **Deprecated 2026-04-24** — it featured the multi-agent `/arena` debate visuals which we gated noindex 2026-04-22. No longer used for image generation.
- `preview/` — first-round brand-card previews (AI-generated from text-only prompt, REJECTED by Evan as off-brand)
- `preview_v2/` — second-round themed-editorial previews (Nano Banana cooks from ticker industry + brand palette, PIL composites logo bottom-right, NO AI-rendered text in image)
- `_archive/` — archival snapshots

### win-tracker cleanup

`post_win_to_x()` + call site + X credential env block removed from `win-tracker/main.py` (−74 lines, +3). X posting is exclusively owned by `x-poster` now. `win-tracker` retains signal-performance tracking (BQ + Firestore writes).

### Webapp changes (NOT yet pushed by Evan)

- `apphosting.yaml:42` — GA4 measurement ID `G-KPGTJDBC6N` → `G-ZF0DQVQEKJ` (new property Evan created)
- `src/app/layout.tsx:44` — same swap
- `src/lib/gtag.ts:8` — same swap (fallback const)
- `apphosting.yaml:44-61` — 18-line `scheduledJobs:` block deleted (4 dead cron entries that had been 404-ing for 4 days since the handlers were deleted in commit `17e37919`)

GA_API_SECRET (server-side Measurement Protocol secret) is **not rotated** — Stripe-webhook MP calls silently no-op until Evan creates a new MP API secret in the new GA property. Acceptable per phase-1 plan (conversion tracking is phase 2).

### New GTM plan

`docs/EXEC-PLANS/2026-04-24-100-day-gtm-plan.md` — 100-day sprint 2026-04-27 → 2026-08-04. Framing A locked (funnel validation, 50–150 paid subs Day 100, organic only, no paid acquisition pre-track-record). 7 X post types + cadence table, 13-post blog schedule, weekly Friday metrics report, risk/pivot triggers, founder pricing uncapped decision.

### 8 X secrets in Secret Manager

- Existing OAuth 1.0a secrets refreshed to version 2 (Evan provided new values): `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`
- New OAuth 2.0 secrets (for future engagement features): `X_BEARER_TOKEN`, `X_OAUTH2_CLIENT_ID`, `X_OAUTH2_ACCESS_TOKEN`, `X_OAUTH2_REFRESH_TOKEN` (labeled `oauth=v2,provider=x`)

## Architectural decisions of note

### Decision: deterministic canonicalizer for disclaimer + filler enforcement

**Problem:** LLM writers paraphrase disclaimers (`"Paper-trade. Not financial advice."` drifts to `"Paper-trade only. Not advice."`) and insert $SPY/$QQQ/$IWM/$DIA as generic-index filler on standby posts regardless of prompt rules.

**Decision:** Stop trying to force LLM compliance via prompt. Add `canonicalize_draft_text(text, post_type)` in `compliance.py` — regex-based, post-LLM, runs in the `score_rubric_before_reviewer` callback so the reviewer judges the CANONICAL text, not the writer's draft. Publisher runs it again as belt-and-suspenders (idempotent).

**Result:** Disclaimer drift: 100% → 0%. $SPY filler on empty-data standby: eliminated. `V/OI None` in teaser runner-ups: stripped. Reviewer stops hallucinating rules to enforce (it was demanding `#NotAdvice` hashtag before the canonicalizer moved).

### Decision: theme-driven image gen + PIL logo composite (rejected AI-reproduced brand)

**Problem:** Initial approach passed the webapp og-image.png as a multimodal Part input to Nano Banana. Output was generic "data-card" visuals that poorly mimicked the og-image's specific multi-agent-debate composition. Also: AI-rendered text in images is unreliable (tickers get misspelled, fonts drift).

**Decision:** Split the image into two responsibilities. (1) Nano Banana cooks an editorial IMAGE with no text/logos, themed around the ticker's industry using its own world knowledge (`$NVDA` → semiconductors, `$GOOG` → AI, `$APP` → mobile ads). (2) PIL composites the REAL logo onto bottom-right at 12% width — pixel-perfect, zero AI variance.

**Result:** Brand mark is deterministic. Editorial images show genuine thematic variation per ticker. Image gen failures are non-blocking (text-only post still ships).

### Decision: Option B deferred to 2026-04-25 — PIL ticker overlay for signal/win/loss

Evan confirmed 2026-04-24 EOD. Tomorrow's first ship: PIL-composites a large `$TICKER` (+ direction badge) as a left-aligned overlay at ~45% image width on signal/win/loss posts. Keeps standby/teaser/report/scorecard clean-editorial. Uses Space Grotesk Bold from brand.py. Rationale: top FinTwit accounts stamp the ticker as a huge overlay because readers swipe fast and often never read past the image. Scroll-readable branding.

### Decision: Cloud Scheduler jobs NOT created this session

All 5 scheduler jobs (`x-poster-report-0830`, `-signal-0905`, `-teaser-1230`, `-callback-1600`, `-scorecard-1700`) are drafted as a one-line loop but **not executed**. They would start firing x-poster immediately on their cron, even with DRY_RUN=true. Evan flips DRY_RUN=false + creates schedulers in the same step tomorrow after Option B lands.

### Decision: commit is local-only, not pushed

`031110ec` contains 55 files / +17,223 lines. Git author is Evan (from gitconfig). Not pushed because engine-repo pushes auto-build-trigger on some CI paths — Evan explicitly controls when origin/master changes.

## Bugs fixed along the way

The x-poster service took **8 revisions** (00007 → 00016) before all four smoke scenarios passed cleanly. Notable fixes along the way:

1. `App(name="x-poster")` → `App(name="x_poster")` — pydantic identifier constraint (no hyphens)
2. `before_agent_callback` signatures: `ctx: CallbackContext` → `callback_context: CallbackContext` (ADK requires kwarg name match)
3. `Publisher` uses `EventActions(state_delta={...})` instead of direct `ctx.session.state[...]` assignment — direct mutation doesn't persist across `SequentialAgent` boundaries in this ADK version
4. `_coerce_draft()` helper — writer has no `output_schema`, so `state["post_draft"]` can arrive as a raw string or fenced-JSON block; coerce to `{text: raw}` fallback
5. BigQuery column fixes in `tools.py`: `vol_oi_ratio` → `volume_oi_ratio` (aliased), `exit_price` → removed (column doesn't exist — use `realized_return_pct`), `peak_return` → `realized_return_pct`
6. `_jsonable()` helper — BigQuery `datetime.date` objects blew up ADK's `json.dumps` when serializing tool output into the next agent's prompt. Recursively coerces dates + decimals to strings at tool return boundaries.
7. ADK curly-brace gotcha: `{ticker}`, `{emoji}`, `{direction}`, `{score}` in writer's rule #12 crashed the pipeline with `KeyError: Context variable not found: ticker`. ADK's `inject_session_state` regex-scans every `{identifier}` in an instruction string. Fix: `<slot>` angle-bracket syntax (consistent with rule #9 + all templates). `{?}` suffix marks valid ADK state refs as optional.
8. Reviewer rule hallucination on standby posts (demanded `#NotAdvice` hashtag, `$SPY` cashtag, `Not advice.` instead of `Not financial advice.`). Two fixes: (a) canonicalize draft BEFORE reviewer sees it so it judges the canonical text; (b) reviewer prompt SPECIAL CASES section explicitly saying standby has no cashtag BY DESIGN + both canonical disclaimers are valid.
9. Moneyness rendered as `0.0642% OTM` in some runs (writer forgot to multiply the fraction). Fix: `_normalize_percent()` in `fetch_todays_pick` — if value < 1.0, multiply by 100. Deterministic, no LLM judgment.

## Outcomes / verification

- **All 4 smoke scenarios APPROVE on first iteration** on `x-poster-00015-5b5+` (signal / standby / teaser on 2026-04-23 real data + standby control on 2026-04-24 empty data). Verified via `/post` HTTP responses + Firestore `x_posts/*` reads.
- Signal tweet on real data ($APP 2026-04-23) pixel-matches Evan's premium WhatsApp format.
- Image generation verified `logo_composited=true` via standalone script, previews at `gs://gammarips-x-media/preview_v2/`.
- Email cron remediation: `apphosting.yaml` -18 lines, YAML validates, zero orphan Cloud Scheduler jobs. Committed only in working tree; Evan pushes.
- GA4 code swap verified across 3 files (`apphosting.yaml`, `layout.tsx`, `gtag.ts`); zero remaining refs to `G-KPGTJDBC6N` in webapp source.

## Rationale for key calls

- **Why separate services (`x-poster` + `blog-generator`) vs one multi-surface service?** Different cadences (5x weekday vs 1x weekly), different memory profiles, independent scaling, clearer ownership. Shared code moved to `libs/gammarips_content/`. Same pattern as `libs/trace_logger/`.
- **Why Nano Banana (`gemini-3-pro-image-preview`) over Imagen 3 or static templates?** Image-generation skill + editing capability + same `google-genai` stack we already use. Imagen 3 isn't editing-capable. Static matplotlib templates would require per-post-type layout maintenance; Nano Banana absorbs that into prompting.
- **Why PIL logo composite vs letting AI render the logo?** AI image gen mangles logos reliably. PIL composite is 10 LOC, zero variance, pixel-perfect.
- **Why the revenue-policy decision on uncapped Founder pricing?** Evan said so 2026-04-24. No seat-scarcity copy anywhere in the GTM plan. Memory updated (`project_founder_pricing`).
- **Why Framing A (funnel validation, organic only, 50–150 paid Day 100)?** Honest funnel math shows 1000 paid in 100 days needs ~$100k paid acquisition — not justified before ≥30 V5.3 closed trades exist to anchor the CAC pitch. Memory `project_revenue_target` (9–15 month realistic window) holds.
- **Why keep `preview_v2/manual_nvda_test.png`?** Evan's first eyeball of the new theme-driven architecture. Don't delete — useful archaeology.

## Next-session pointers

See `NEXT_SESSION_PROMPT.md`. Tomorrow's first ship: **Option B (PIL ticker overlay on signal/win/loss)** → redeploy → flip DRY_RUN=false → create 5 Cloud Scheduler jobs → x-poster goes LIVE on @gammarips. Then blog-generator dangling-state fix + deploy.
