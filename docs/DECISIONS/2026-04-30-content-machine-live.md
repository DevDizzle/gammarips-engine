# Content machine live — watchlist post, callback filter, scorecard fix, /draft_reddit, newsletter rewrite

**Date:** 2026-04-30
**Status:** Shipped
**Touches:** `x-poster`, `blog-generator`, `libs/gammarips_content`, Cloud Scheduler

## Summary

Closed out the 4-surface "ship and park" plan from `project_finished_definition.md`. All four surfaces (x-poster, blog-generator, reddit-drafter, email-marketing) are LIVE with weekly autonomous cadence. Two material x-poster bugs fixed (report collection name, callback ticker filter). Newsletter rewritten to use real ledger + report data with FOMO-framed featured-trade callout.

| Service | Final revision today | Change |
|---|---|---|
| `x-poster` | `00022-jpb` | Watchlist post replaces SIGNAL; callback restricts to publicly-posted tickers; scorecard mirrors callback shape; Entry Routine block removed; report URL added; daily_reports collection bug fixed |
| `blog-generator` | `00017-zw6` | Default compute SA (not firebase-adminsdk); DRY_RUN=false; new `/draft_reddit` for Tier-1 sub drafts; newsletter rewritten with featured-trade FOMO + green win color + FOUNDER29 coupon |
| `libs/gammarips_content` | (vendored on each deploy) | `firestore_helpers.fetch_todays_report` reads `daily_reports/{date}` not `overnight_reports/{date}`; `fetch_original_tweet_id` skips dry-run placeholder ids; URL whitelist for `gammarips.com/reports/<date>`; char budgets adjusted for new post types |

## Decision 1 — x-poster: replace SIGNAL with WATCHLIST to stop paid-product leak

**Problem:** SIGNAL post at 09:05 ET was rendering the V5.3 daily pick verbatim — same ticker, same direction, same contract — five minutes after the paid email went to subscribers. Anyone following @gammarips for free got the alpha; the paid email was redundant.

**Fix:**
- New `WATCHLIST` post type: 3 high-dollar-volume tickers from `overnight_signals_enriched`, ranked by `call_dollar_volume + put_dollar_volume DESC`, EXCLUDING the V5.3 daily pick.
- New tool `fetch_watchlist(scan_date, n, exclude_ticker)` — sorts by total option dollar volume (not contract count, which over-weights small-caps).
- Cron `x-poster-signal-0905` payload changed `{"post_type":"signal"}` → `{"post_type":"watchlist"}` (job name retained).
- Writer template: ticker + direction + score + dollar-flow only — NO contract / strike / mid (those go only to paid).
- New rule 11b in writer prompt: "If post_type=watchlist, use WATCHLIST template; do NOT render brief.pick — that re-leaks the paid alpha."
- No-content guard added to Publisher: skips if `runner_ups`/`watchlist`/`weekly_ledger.trades` is empty.

**Result:** V5.3 contract details NEVER appear on X. Email/WhatsApp paid drop becomes meaningfully exclusive. Discovery posts hook search-driven impressions on big names (CAT/MS/MELI/BE class).

## Decision 2 — x-poster: callbacks + scorecard restrict to publicly-posted tickers

**Problem:** Callback at 16:45 ET queried `forward_paper_ledger` for today's closes and would surface ANY V5.3 close (the trader runs brackets on every enrichment signal — ~20 closes/day on big days). That meant we'd post recap tweets on tickers no follower had seen us name. Same applied to scorecard.

**Fix:**
- New tool `fetch_recently_posted_tickers(scan_date, lookback_days)` — scans `x_posts/{date}_{watchlist|signal}` past N days, regex-extracts cashtags.
- `fetch_closing_trades(scan_date, restrict_tickers="")` and `fetch_weekly_ledger(week_ending, restrict_tickers="")` accept comma-joined ticker filter.
- Planner instruction for callback: chain `fetch_recently_posted_tickers` (lookback=5) → `fetch_closing_trades(restrict_tickers=...)`.
- Planner for scorecard: chain `fetch_recently_posted_tickers` (lookback=10) → `fetch_weekly_ledger(restrict_tickers=...)`.
- New tool `find_originating_post_for_ticker(ticker, lookback_days)` — finds the QRT target tweet for win callbacks.
- LOSS template lost the V5.3-specific "stop wins over target on ambiguous bars" line — replaced with "Trade the system, not the pick."
- WIN/LOSS templates use pre-shaped fields (`pct_signed`, `exit_reason_display`, `exit_price` derived from entry × (1+ret)) so the writer doesn't need to do math.

**Side fix:** Also corrected `fetch_weekly_ledger` and `fetch_closing_trades` to filter `policy_version = 'V5_3_TARGET_80' AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')`. Without these filters the scorecard would render dozens of mixed-version dud rows.

**First real scorecard fire window:** Fri 5/8 — Mon-Wed of that week needs publicly-posted watchlist tickers that close by Friday. Tomorrow's Fri 5/1 cron will skip silently (`error=no_scorecard_trades`).

## Decision 3 — x-poster: report posts now actually post + carry the report URL

**Problem:** `x-poster-report-0830` cron was firing daily but always erroring `no_report_today`. Root cause: `gammarips_content/firestore_helpers.fetch_todays_report` read `overnight_reports/{date}`, but `overnight-report-generator/main.py` writes to `daily_reports/{date}`. Schema drift never noticed because reports always quietly skipped.

**Fix:**
- `firestore_helpers.fetch_todays_report` now reads `daily_reports/{date}`.
- REPORT writer template appends a `🔗 https://gammarips.com/reports/<scan_date>` line.
- `compliance.py` whitelist regex `https://gammarips\.com/reports/\d{4}-\d{2}-\d{2}` exempted from the "no URLs" rule for x-poster.
- Char budget bumped 280 → 360 to fit the URL.

## Decision 4 — x-poster: removed Entry Routine block from SIGNAL/WATCHLIST template

**Problem:** Every signal-style post carried 4 lines explaining "Buy 1 contract at market, stop -60%, target +80%, hold 3 days" — bloat that didn't help X-feed scanners.

**Fix:** Removed the Entry Routine sub-block. Signal/watchlist posts shipped at 09:05 are now lean: header + ticker line + contract-or-flow detail. Routine details live in `CHEAT-SHEET.md` and the daily V5.3 email.

## Decision 5 — x-poster: teaser no-runners guard

**Problem:** 2026-04-29 — only MDB cleared the gate stack. Both SIGNAL (9:05) and TEASER (12:30) rendered MDB. Same ticker twice on the public feed.

**Fix:** Publisher skips teaser when `runner_ups` is empty after exclusion (`error=no_runners_today`). Same shape as the report/callback/watchlist guards.

## Decision 6 — blog-generator: switch runtime SA to default compute

**Problem:** `blog-generator/deploy.sh` had `--service-account="firebase-adminsdk-fbsvc@..."`. That SA had no Vertex AI permission so `/draft_email` returned 403 PERMISSION_DENIED on `aiplatform.endpoints.predict`. After granting `roles/aiplatform.user`, the next call failed on `logging.logEntries.create`. Pattern was about to repeat for every capability the service touched.

**Fix:** Removed custom SA flag, set `--service-account="406581297632-compute@developer.gserviceaccount.com"` (same as x-poster). Default compute SA inherits Vertex AI + logging + GCS + Firestore + BigQuery via project Editor. One line changed; all 403s resolved.

**Memory:** `feedback_default_compute_sa.md` — for any new Cloud Run service, default to the compute SA unless there's a real isolation requirement.

## Decision 7 — blog-generator: new `/draft_reddit` endpoint + Thu cron

**Surface 3 of 4 (per `project_finished_definition.md`).** Mechanically mirrors `/draft_email`:

- Three Tier-1 subs: `r/options`, `r/thetagang`, `r/algotrading`. Voice config hardcoded as `_DEFAULT_SUBREDDIT_VOICE` per-sub dict (`lead_style`, `taboo_phrases`, `length_words`, `mod_traps`, `tone`). Migrate to Firestore later if voice tuning becomes regular.
- Single Gemini render per sub (`_render_reddit_post`); 200-400 word target.
- Per-sub rubric: hard fails on URLs, taboo phrases, retired aliases, banned recommendation phrases. Soft warnings on word-count window + lead-with-number heuristic — drafts still ship to GCS even with warnings, operator sees them in the email.
- Each draft → `gs://gammarips-content-drafts/reddit/{date}_{sub}.md`.
- One operator email per fire summarizes all 3 drafts with GCS links + posting-window instructions (Tue 10:00 AM-12:00 PM ET).
- **Drafter NEVER auto-posts.** Operator copy-pastes per sub.
- Cloud Scheduler `content-drafter-weekly-reddit` Thu 10:00 ET → POST `/draft_reddit` body `{"theme":"weekly","dry_run":false}`.

## Decision 8 — blog-generator: newsletter rewrite (anti-hallucination + featured-trade FOMO + green win color)

**Problem:** First operator-preview newsletter (4/30 test fire) hallucinated $SPY/$TSLA, falsely cited "664 closed trades" (mixed V3/V4/V5.3 + INVALID_LIQUIDITY rows), used wrong "$39/mo" pricing copy, and read like a database dump.

**Fix:**
- New tools `tools.get_recent_daily_reports(days=7)` and `tools.get_recent_v53_closes(days=7)` feed REAL content into the writer prompt (report headlines + actual ledger closes).
- `tools.get_closed_trade_count` filtered to V5.3-only valid exits — drops V3/V4 noise (~664 → ~real V5.3 count). Same V5.3 filter applied to `fetch_live_context` so the 30-trade unlock gate isn't falsely tripped.
- Anti-hallucination prompt rule: "ONLY mention tickers that appear verbatim in the data blocks above."
- Internal `closed_trade_count` is NOT printed in body copy ("would mislead readers" since we've publicly posted ~3-5 picks).
- **Featured trade callout** (Evan 2026-04-30): single highest-`return_pct` V5.3 close of the week, with FOMO copy "Did you catch this trade? Paid subscribers get our curated daily V5.3 pick at 09:00 AM ET". Section skipped entirely if no winners closed (losses don't drive sub conversion).
- Win color **locked**: featured trade's pct_signed wraps in `<span style="color: #16a34a; font-weight: 700;">+80%</span>` for ALL winners regardless of BULLISH or BEARISH direction.
- CTA standardized: "Founder pricing $29/mo with code FOUNDER29 (or $39/mo without)". Used FOUNDER29 (no S) — the coupon Evan tested live on Stripe per `2026-04-22-launch-cleanup.md`.
- Paper-trade disclosure under the featured trade as a small italic line; full canonical disclaimer at footer.

**Cron:** `content-drafter-weekly-email` Sun 17:00 ET → POST `/draft_email` body `{"theme":"weekly","dry_run":false}`. Operator-preview-only by design — `/blast_email` to the 211-user list stays manual `curl`.

## Cloud Scheduler — current state (all America/New_York)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 weekday | enrichment-trigger | unchanged |
| `agent-arena-trigger` | 06:00 weekday | agent-arena | unchanged |
| `gammarips-eval-daily` | 07:00 weekday | gammarips-eval `/eval` | unchanged |
| `overnight-report-generator-trigger` | 08:15 weekday | overnight-report-generator | writes `daily_reports/{date}` |
| `x-poster-report-0830` | 08:30 weekday | x-poster `/post {report}` | now actually posts (4/30 fix) |
| `signal-notifier-job` | 09:00 weekday | signal-notifier `/` | dual-writes `todays_pick/{scan,entry}` |
| `x-poster-signal-0905` | 09:05 weekday | x-poster `/post {watchlist}` | **payload changed 4/30 from "signal" to "watchlist"** |
| `x-poster-teaser-1230` | 12:30 weekday | x-poster `/post {teaser}` | skips on 0-runners |
| `polygon-iv-cache-daily` | 16:30 weekday | forward-paper-trader `/cache_iv` | unchanged |
| `forward-paper-trader-trigger` | 16:30 weekday | forward-paper-trader `/` | unchanged |
| `track-signal-performance` | 16:30 weekday | win-tracker `/` | 30-trade gate watcher armed |
| `backfill-signal-performance` | 17:30 weekday | win-tracker backfill | unchanged |
| `x-poster-callback-1645` | 16:45 weekday | x-poster `/post {callback}` | restricts to posted tickers |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | restricts to posted tickers; first real fire 5/8 |
| `overnight-scanner-trigger` | 23:00 weekday | overnight-scanner | unchanged |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly digest | unchanged |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | first auto-fire 5/4 (`why-uoa-is-mostly-noise`) |
| **`content-drafter-weekly-email`** | **Sun 17:00** | **blog-generator `/draft_email`** | **NEW 4/30 — operator preview only** |
| **`content-drafter-weekly-reddit`** | **Thu 10:00** | **blog-generator `/draft_reddit`** | **NEW 4/30 — 3 sub drafts to operator** |

## Compliance / safety guarantees retained

- V5.3 execution policy unchanged. No gates added to `forward-paper-trader`.
- WIN / LOSS / CALLBACK / SCORECARD posts still carry `⚠️ Paper-trade. Not advice.`
- Watchlist posts ship without disclaimer (forward-looking, discovery only — same scope as signal/standby/teaser/report).
- No real-money P&L claims (V5.3 still pre-30-trade unlock).
- Reddit drafts: NO URLs in body, NO paid-product promo (mod-anti-spam compliance).
- Newsletter: paper-trade disclosure + canonical disclaimer in EVERY rendered email.

## Files touched

**x-poster:**
- `app/agent.py` — Planner instructions (watchlist + scorecard ticker filter); WATCHLIST template added; SIGNAL Entry Routine removed; REPORT URL added; LOSS V5.3 line removed; WIN/LOSS use pre-shaped pct_signed/exit_reason_display; rule 5 URL whitelist; rule 11b watchlist no-leak; teaser/watchlist/scorecard no-content guards.
- `app/tools.py` — new `fetch_watchlist`, `fetch_recently_posted_tickers`, `find_originating_post_for_ticker`; `fetch_closing_trades` filters V5.3 + restrict_tickers + derives `exit_price`/`pct_signed`/`exit_reason_display`; `fetch_weekly_ledger` filters V5.3 + restrict_tickers + pre-shapes outcome_emoji/direction_short/pct_signed; `fetch_runner_ups` excludes pick.

**blog-generator:**
- `app/fast_api_app.py` — `/draft_reddit` endpoint + voice config + render + rubric; newsletter `_render_newsletter_html` rewritten with featured-trade + green color + FOUNDER29 + anti-hallucination rules.
- `app/tools.py` — `get_closed_trade_count` V5.3-filtered; `fetch_live_context` V5.3-filtered; new `get_recent_daily_reports` and `get_recent_v53_closes` helpers.
- `deploy.sh` — DRY_RUN default flipped to false; `--service-account` set to default compute SA.

**libs/gammarips_content:**
- `compliance.py` — `CHAR_BUDGETS` adds watchlist=380, report=360, win/loss=240; `ALLOWED_URL_PATTERN` whitelists `gammarips.com/reports/<date>`.
- `firestore_helpers.py` — `fetch_todays_report` reads `daily_reports`; `fetch_original_tweet_id` skips dry-run / `dry_run_*` placeholder ids.

## Memory entries added/updated

- New `feedback_default_compute_sa.md` — Cloud Run services use the default compute SA, not custom isolation SAs.
- Updated `project_finished_definition.md` — flipped from "1 of 4 shipped" to "all 4 LIVE 2026-04-30" with current revs + crons.

## Outstanding gaps (carry to next session)

1. **Email list consolidation.** Two paths feed user emails: webapp `users` Firestore collection (211 docs from Firebase signups) AND a separate "form-capture" path (origin TBD). Need to inventory the form-capture source and decide whether to merge into `users` or filter union at blast time. Surfaced 4/30 by Evan; not yet investigated.
2. **Featured trade — restrict to publicly-posted tickers?** Currently the newsletter's featured-trade picks the top winner from the entire V5.3 ledger (any ticker the trader bracketed). A stricter "we publicly called this" framing would restrict to tickers from the past N days of x_posts (same logic the scorecard uses). Tradeoff: smaller pool, fewer "wow" weeks; more honest.
3. **Watchlist post — first hash check.** Tomorrow 5/1 09:05 ET will be the first real WATCHLIST post on the public feed. Verify the rendered tweet matches the design (3 tickers, dollar-flow callout, no contract details, "Curated daily pick → email subscribers only." footer).
4. **Mon 5/4 05:00 ET first auto-blog.** Slug `why-uoa-is-mostly-noise`. Verify Firestore `blog_posts/why-uoa-is-mostly-noise` lands, webapp `/blog/[slug]` renders cleanly, internal-link slot populated.
5. **Blog page should render visually like `/reports/[date]`** (Evan 2026-04-30). Webapp-side template work, NOT in this repo. Compare `daily_reports/{date}` rendering vs `blog_posts/{slug}` rendering and align headings / disclaimer block / sidebar callouts.
