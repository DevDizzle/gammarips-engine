# Blog-generator to production · X-poster text-only · todays_pick dual-write

**Date:** 2026-04-28
**Status:** Shipped
**Touches:** `x-poster`, `signal-notifier`, `blog-generator`, `libs/gammarips_content`

## Summary

One bundled session shipping three independent fixes that together close out
the "ship and park" content-publishing trinity to a clean state. Forward
trading policy unchanged.

| Service | Revision | Change |
|---|---|---|
| `x-poster` | `00018-2j2` | Text-only posts; disclaimer scoped to perf posts only; report no-content guard |
| `signal-notifier` | `00008-6jh` | Dual-write `todays_pick/{scan_date}` + `todays_pick/{entry_day}` |
| `blog-generator` | `00008-9qt` | First production deploy; `DRY_RUN=false`; weekly cron live |

## Decision 1 — x-poster: kill editorial images, gate the disclaimer

**Problem:** Live feed inspection showed Nano Banana editorial images "looking
stupid" and the `⚠️ Paper-trade. Not financial advice.` line cluttering every
forward-looking post (signal/standby/teaser/report). Disclaimer is only
meaningful when describing realized P&L — on forward setups it reads as
hedge-speak.

**Fix:**

- Publisher always passes `image_bytes=None` to `publish_to_x`. `tools.generate_image`
  and PIL composite helpers retained but unused (deletable later).
- `compliance.IMAGE_REQUIRED == frozenset()` (was `{signal, standby, scorecard}`).
- New `compliance.DISCLAIMER_REQUIRED == {win, loss, callback, scorecard}`.
- `compliance.canonicalize_draft_text` returns body-only when `post_type` not
  in `_DISCLAIMER_BY_POST_TYPE`.
- Writer prompt rule 4 gated to perf-only types; SIGNAL/STANDBY/TEASER/REPORT
  templates no longer carry trailing disclaimer lines.

**Result:** `signal`, `standby`, `teaser`, `report` ship without disclaimer.
`win`, `loss`, `callback`, `scorecard` keep `⚠️ Paper-trade. Not advice.`

## Decision 2 — x-poster: no-content guard for `report` post_type

**Problem:** 2026-04-28 8:30 ET `report` cron fired before `overnight_reports/2026-04-28`
existed in Firestore. Writer drifted to STANDBY template, posting a duplicate
"GammaRips Standby" 35 minutes before the 9:05 ET signal cron's STANDBY post.

**Fix:** Mirror the existing `callback` no-content guard. Publisher checks
`post_outline.report_summary.headline` — if empty, log `no_report_today` and
skip publish. No more drift-to-STANDBY artifacts.

## Decision 3 — signal-notifier: dual-write `todays_pick`

**Problem:** `signal-notifier` writes `todays_pick/{scan_date}` (the previous
trading day). `x-poster-signal-0905` reads `todays_pick/{today}` (the entry
day). On 2026-04-28 the SNDK pick lived under `todays_pick/2026-04-27` and
x-poster's lookup of `todays_pick/2026-04-28` returned empty → STANDBY fallback.

**Fix:** `signal-notifier.write_todays_pick_doc` now writes the same payload
under BOTH `{scan_date}` and `{entry_day}` keys. Webapp / MCP / arena-verdict
keep working (still keyed by scan_date as primary). Entry-day readers can
look up by `today_et_iso()` without calendar arithmetic.

**Drift-prevention invariant:** if doc schema changes, update BOTH writes in
`write_todays_pick_doc`.

## Decision 4 — blog-generator: first production deploy

**Status before today:** code complete (`4eb9a80` fix), zero deploys, zero
Firestore docs.

**Shipped today:**

1. **Endpoint rename** — `/run` → `/generate`. ADK's `get_fast_api_app`
   reserves `/run` for its built-in session-based endpoint; competing
   `@app.post("/run")` returned `422 missing appName/userId/sessionId`.
   Cloud Scheduler hits `/generate`.
2. **Callback param rename** — `seed_voice_rules(ctx)` → `seed_voice_rules(callback_context)`.
   ADK invokes callbacks with kwarg `callback_context=...`; mismatched name
   raised `TypeError: got an unexpected keyword argument`.
3. **State propagation fix** — Publisher now yields `EventActions(state_delta=...)`
   instead of mutating `state["publish_result"]` directly. ADK only persists
   in-session state via `state_delta` events; direct mutation was invisible
   to `session_service.get_session()` after the run ended.
4. **CTA enforcement** —
   - Writer prompt: front-matter `cta` MUST equal `post_outline.schedule_slot.cta`
     verbatim. `webapp_visit` slots: NO paid-tier mentions in body.
   - `score_blog_rubric(markdown, expected_cta=...)`: hard-fails on YAML CTA
     mismatch AND on `pro_trial`/`starter_trial`/`founder_pricing`/`paid_tier`
     mentions when slot is `webapp_visit`.
5. **Disclaimer canonicalization** — `compliance.canonicalize_blog_disclaimer(markdown)`:
   walks back over trailing blockquote / disclaimer-trigger lines, strips
   them if any disclaimer signal is present, appends the canonical block.
   Prevents Gemini paraphrase drift ("GammaRips is a publisher...") from
   defeating the rubric's substring check.
6. **Rubric gate at both EscalationChecker and Publisher** — loop only
   escalates when `review.APPROVE AND rubric.passed`. Publisher only ships
   under the same condition. Defense in depth: Gemini occasionally returns
   APPROVE on iteration 3 even when rubric fails.
7. **Firestore composite index** `(status, published_at)` on `blog_posts`
   collection. Required by `fetch_prior_posts` query for internal-link
   suggestions.
8. **`.gcloudignore` added** to blog-generator. `_gammarips_content_vendor/`
   is gitignored but must be uploaded for Docker COPY. Mirrors x-poster's
   approach.
9. **Cloud Scheduler** `blog-generator-weekly` — `0 5 * * 1` America/New_York
   → `POST https://blog-generator-406581297632.us-central1.run.app/generate`
   with empty body. First fire **Mon 2026-05-04 05:00 ET**.

**Final validation (rev `00008-9qt`, dry_run=true):** status=`dry_run`,
iterations=2, reviewer_score=10.0, YAML cta=`webapp_visit`, exactly 1
canonical disclaimer block, no paid pitches, 1342 words.

## Operational notes

- The Cloud Run service has `PROJECT_ID=profitscout-fida8` set explicitly via
  deploy.sh — that overrides the user's shell `PROJECT_ID=profitscout-lx6bb`.
  Local seed scripts must be prefixed with `PROJECT_ID=profitscout-fida8` or
  they silently write to the wrong project (memory: `feedback_seed_script_project_env.md`).
- Mailgun DNS / spam: 2026-04-28 SNDK pick email was delivered to
  `eraphaelparra@gmail.com` per Mailgun events (`accepted` + `delivered`
  code=250) but landed in Gmail spam. User marked not-spam; future delivery
  should normalize.
- 2026-04-28 SNDK BULLISH paper position is **on the books** (entered 10:00 ET
  via `forward-paper-trader`), expected exit Wed 2026-04-30 15:50 ET unless
  −60% stop or +80% target hits earlier.
- The 2026-04-28 X-feed posted 2× STANDBY (8:30 report + 9:05 signal). Editorial
  decision: do NOT manually post a corrective SIGNAL retroactively — the
  trade is already on, a stale post is feed-confusing. Win/loss callback in
  2-3 days will be the clean recap.

## Compliance / safety guarantees retained

- V5.3 execution policy unchanged. No gates added to `forward-paper-trader`.
- Win/loss/callback/scorecard still carry the `⚠️ Paper-trade. Not advice.`
  disclaimer. Realized-P&L posts ship with the explicit limit.
- `gammarips-mcp` trust model unchanged.
- No real-money P&L claims (V5.3 still pre-30-trade unlock).

## Files touched

- `x-poster/app/agent.py` — Publisher image-skip; report no-content guard;
  writer template disclaimer removal; reviewer special-case rewrite.
- `signal-notifier/main.py` — dual-write block in `write_todays_pick_doc`.
- `blog-generator/app/agent.py` — `/run`→`/generate` callback fix;
  `score_rubric_before_reviewer` reads `expected_cta`; `EscalationChecker`
  rubric gate; `Publisher` rubric gate + state_delta yields.
- `blog-generator/app/tools.py` — `score_blog_rubric(expected_cta=)`;
  YAML CTA mismatch + paid-pitch detection on `webapp_visit`.
- `blog-generator/app/fast_api_app.py` — `/run`→`/generate`.
- `blog-generator/deploy.sh` — header comment path update.
- `blog-generator/.gcloudignore` — new (matches x-poster pattern).
- `libs/gammarips_content/gammarips_content/compliance.py` —
  `IMAGE_REQUIRED=frozenset()`; `DISCLAIMER_REQUIRED` set; `canonicalize_blog_disclaimer`;
  `canonicalize_draft_text` short-circuits for non-perf post types.
- `libs/gammarips_content/gammarips_content/voice_rules.py` —
  `render_for_prompt` updated wording on disclaimer scope.

## Memory entries added

- `project_no_disclaimer_no_images.md`
- `project_todays_pick_dual_write.md`
- `feedback_adk_route_reserved.md`
- `feedback_seed_script_project_env.md`
