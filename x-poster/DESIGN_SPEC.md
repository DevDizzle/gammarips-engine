# DESIGN_SPEC — x-poster

**Service:** `x-poster` (Cloud Run, ADK-based)
**Repo:** `/home/user/gammarips-engine/x-poster/`
**Triggered by:** 5 Cloud Scheduler jobs (`x-poster-{report,signal,teaser,callback,scorecard}-*`)
**Handle:** `@gammarips` (X Premium / blue check → 400-char budget)

---

## Overview

`x-poster` is an ADK multi-agent service that drafts, reviews, illustrates, and publishes X posts for `@gammarips` across 7 post types, automatically, with no human-in-the-loop. One Cloud Run service, one `POST /` endpoint, 5 Cloud Scheduler jobs routing by `post_type` payload. Every published post includes a Nano Banana (`gemini-3-pro-image-preview`) generated image pinned to a shared brand reference card for consistent look.

Quality contract = reviewer agent's compliance rubric (char budget, retired-alias scan, disclaimer, publisher framing, cashtag position, image dimensions). LoopAgent retries up to 3× before failing loud. Zero auto-reply-with-link (shadowban risk per 2026-04 X/FinTwit research — pinned tweet and bio link instead).

Shares code with `blog-generator` via `libs/gammarips_content/` (voice rules, compliance helpers, MCP client, X client wrapper).

---

## Post types + cadence

| # | Type | Trigger | Payload | Image | Length |
|---|---|---|---|---|---|
| 1 | `signal` | Mon–Fri 09:05 ET | `{"post_type":"signal"}` | YES (required) | 400 chars premium |
| 2 | `standby` | Auto when `signal` finds no pick | — | YES (minimal "silence" card) | ≤280 chars |
| 3 | `report` | Mon–Fri 08:30 ET | `{"post_type":"report"}` | optional | ≤280 chars |
| 4 | `teaser` | Mon–Fri 12:30 ET | `{"post_type":"teaser"}` | optional | ≤300 chars |
| 5 | `win` (QRT) | Mon–Fri 16:00 ET (if wins exist) | `{"post_type":"callback"}` → routes | optional | ≤200 chars (QRT quote) |
| 6 | `loss` (neutral single) | Mon–Fri 16:00 ET (if losses exist) | same | NO (text-only per research) | ≤200 chars |
| 7 | `scorecard` (3-tweet thread) | Fridays 17:00 ET | `{"post_type":"scorecard"}` | YES on tweet 1 | 400 chars × 3 |

**Weekly total:** ~20 auto posts + ~3 Evan originals + ~60 Evan replies = 83 touchpoints. FinTwit sweet spot.

---

## Agent pipeline

```
  POST / {"post_type":"signal"}
         │
         ▼
  ┌─────────────────────────────────────────┐
  │ SequentialAgent "x_poster_pipeline"     │
  │                                         │
  │  ┌──────────────────────────────────┐  │
  │  │ LoopAgent "draft_review_loop"    │  │
  │  │  max_iterations=3                │  │
  │  │                                  │  │
  │  │  Planner  ──► Writer  ──► Reviewer ──► EscalationChecker
  │  │             (tools: fetch_*)           (Pydantic schema)   (escalate on APPROVE)
  │  └──────────────────────────────────┘  │
  │                  │                      │
  │                  ▼                      │
  │  PublishAgent (BaseAgent)               │
  │    1. generate_image(prompt, style_ref) │
  │    2. publish_to_x(text, image, QRT?)   │
  │    3. log_post(scan_date, type, ...)    │
  └─────────────────────────────────────────┘
         │
         ▼
  {"status":"posted", "tweet_id":"...", "iterations":1}
```

### Agents

| Agent | Model | Role |
|---|---|---|
| `planner` (LlmAgent) | `gemini-3-flash-preview` | Reads `post_type` from initial state + calls fetch tools → writes `post_brief` to state (structured: data_summary, primary_angle, image_direction, qrt_tweet_id?) |
| `writer` (LlmAgent) | `gemini-3-flash-preview` | Reads `{post_brief}` + `{voice_rules}` → writes `post_draft` to state (text, image_prompt, qrt_tweet_id?) |
| `reviewer` (LlmAgent with `output_schema=ReviewResult`) | `gemini-3-flash-preview` | Reads `{post_draft}` + rubric check results → writes `review` to state (status: APPROVE/REVISE, notes) |
| `escalation_checker` (BaseAgent) | n/a | Reads `review` state → yields `Event(actions=EventActions(escalate=True))` if `status == APPROVE` → exits LoopAgent |
| `publisher` (BaseAgent) | n/a | Runs after LoopAgent: calls generate_image → publish_to_x → log_post tools |

### State keys (session.state)

| Key | Set by | Used by |
|---|---|---|
| `post_type` | entry (request body) | planner |
| `scan_date` | entry | planner, publisher |
| `post_brief` | planner | writer |
| `post_draft` | writer | reviewer, publisher |
| `review` | reviewer | escalation_checker, publisher |
| `voice_rules` | `before_agent_callback` (loads once) | writer |
| `rubric_check` | writer's tool call to `score_against_rubric` | reviewer |

---

## Tools (deterministic)

All tools live in `x-poster/app/tools.py`. Return JSON-serializable dicts.

| Tool | Agent(s) | Purpose |
|---|---|---|
| `fetch_todays_pick(scan_date: str) -> dict` | planner | Firestore `todays_pick/{date}` |
| `fetch_todays_report_summary(scan_date: str) -> dict` | planner | Firestore `overnight_reports/{date}` → returns title + headline + top-2 bullets |
| `fetch_closing_trades(scan_date: str) -> dict` | planner | BQ `forward_paper_ledger` WHERE `exit_date = scan_date` |
| `fetch_runner_ups(scan_date: str, n: int) -> dict` | planner | BQ `overnight_signals_enriched` top-N by score, excluding the daily pick |
| `fetch_original_tweet_id(original_scan_date: str) -> dict` | planner | Firestore `x_posts/{date}_signal.tweet_id` — for QRT on win/loss callbacks |
| `fetch_weekly_ledger(week_ending: str) -> dict` | planner | BQ aggregate of past 5 trading days' closes for scorecard |
| `score_against_rubric(text: str, post_type: str) -> dict` | writer (optional), reviewer | Deterministic 6-point rubric — char count, retired-alias regex, disclaimer present, cashtag position, URL absence, image-required-for-type check |
| `generate_image(prompt: str, post_type: str) -> dict` | publisher | Calls `gemini-3-pro-image-preview` with brand_ref_card as input image; uploads PNG to GCS `gs://gammarips-x-media/{date}_{type}.png`; returns signed URL. |
| `publish_to_x(text: str, image_url: str \| None, qrt_tweet_id: str \| None, thread_parent_id: str \| None) -> dict` | publisher | Tweepy Client OAuth 1.0a `create_tweet(text, media_ids=[], quote_tweet_id=, in_reply_to_tweet_id=)` — returns `{"tweet_id": "..."}` |
| `log_post(scan_date: str, post_type: str, text: str, tweet_id: str \| None, image_url: str \| None, iterations: int, error: str \| None) -> dict` | publisher | Firestore `x_posts/{date}_{post_type}` |

**MCP access:** A sixth "live state" tool via `McpToolset(SseConnectionParams(url=gammarips-mcp))` gives the planner abstract query access (SELECT-like) without hardcoding BQ SQL for every new post type. **Start with direct Firestore/BQ tools**, add MCP toolset in phase 2 once we've validated baseline.

---

## Data sources (read-only)

| Source | Fields used | Who reads |
|---|---|---|
| Firestore `todays_pick/{date}` | ticker, direction, strike, expiration, mid, vol_oi, moneyness, has_pick | planner (via `fetch_todays_pick`) |
| Firestore `overnight_reports/{date}` | title, headline, content | planner (via `fetch_todays_report_summary`) |
| BQ `profit_scout.forward_paper_ledger` | scan_date, ticker, direction, entry_price, exit_price, exit_reason, peak_return | planner (via `fetch_closing_trades`, `fetch_weekly_ledger`) |
| BQ `profit_scout.overnight_signals_enriched` | ticker, direction, overnight_score, vol_oi_ratio, scan_date | planner (via `fetch_runner_ups`) |
| Firestore `x_posts/{date}_{type}` | tweet_id (read for QRT), full history (for idempotency) | planner, publisher |

## Data sinks (write)

| Sink | Purpose |
|---|---|
| GCS `gs://gammarips-x-media/{date}_{type}.png` | Generated images |
| Firestore `x_posts/{date}_{type}` | Post log (text, tweet_id, image_url, iterations, error, posted_at, dry_run) |
| X API v2 via Tweepy | Actual tweets |

---

## Image-gen strategy

**Shared brand reference.** Canonical `brand_ref_card.png` stored at `gs://gammarips-x-media/brand_ref_card.png`. Every `generate_image` call passes this as input image per Nano Banana's image-editing capability (per `https://ai.google.dev/gemini-api/docs/image-generation.md.txt`). Model preserves brand layout, varies data/colors per post.

**Reference card design (for the one-shot generator):**
- 1200×675 PNG (X preferred ratio)
- 3-zone layout:
  - Top-left: `🔥 GammaRips` wordmark
  - Center: 2 × 2 grid placeholder for ticker/direction/contract/flow stats
  - Bottom-right: `V5_3_TARGET_80` watermark
- Color palette: dark navy background (#0F1419), accent green (#00BA7C) for bullish, accent red (#F4212E) for bearish, off-white text (#E7E9EA)
- Typography: sans-serif, bold for tickers

**Per-post image prompt templates** (owned by `writer` agent, emitted in `post_draft.image_prompt`):
- `signal` — "Apply to brand_ref_card: ticker ${TICKER}, direction ${DIR}, strike ring ${STRIKE}, flow stats V/OI ${VOI}, DTE ${DTE}, keep V5_3_TARGET_80 watermark"
- `standby` — "Apply to brand_ref_card: empty scanner animation, '0 signals cleared' badge in center, subdued palette"
- `report` — "Abstract market-mood illustration matching theme: ${THEME}, brand colors, no text except 'Overnight Brief'"
- `win` — "Victory overlay on brand_ref_card: ${TICKER} ${DIR} callout, +${PCT}% badge in green"
- `scorecard` — "Week strip: 5 cells with ticker + outcome color, wins green losses red, 'Week ending ${DATE}' header"

**Fallback:** if `gemini-3-pro-image-preview` errors/rate-limits, ship text-only with Firestore log flag `image_skipped: true`. Never block post on image.

---

## Compliance rubric (reviewer's 6-point check)

Implemented in `libs/gammarips_content/compliance.py::score_against_rubric()`. Run deterministically by reviewer tool call; LLM reviewer reads scores + does holistic read.

1. **Char budget.** Single-tweet posts ≤280 (standard) or ≤400 (Premium, @gammarips has blue check). Per-tweet budget for scorecard thread. FAIL if over.
2. **Retired-alias scan.** Zero matches for block list: `["Ripper", "Daily Playbook", "The Overnight Edge", "@mention", "score >= 6", "8:30 AM", "$49/$149", "premium signal", "interactive dashboard", "#TheOvernightEdge"]`. Case-insensitive. FAIL on any match.
3. **Disclaimer present.** Post contains `"Paper-trade"` AND `"Not advice"` (exact substrings, case-sensitive). Exception: `win` QRT quote (gets disclaimer via first-reply or parent tweet already carries it). FAIL if missing.
4. **Publisher framing.** No banned phrases: `["buy this", "sell this", "act now", "for you", "your next trade", "entry for you"]`. Case-insensitive substring. FAIL on match.
5. **Cashtag position.** First `$` cashtag must appear in the first 80 chars (above-the-fold on mobile). FAIL if absent or later.
6. **URL absence.** Zero `http://` or `https://` or `www.` substrings in post body. (Link lives in pinned tweet + bio only.) FAIL on any URL.

Reviewer can override rubric FAIL only for `loss` single (which exempts cashtag rule — "Stopped -60% on $TSLA BEARISH" already has cashtag).

---

## Failure modes + fallbacks

| Mode | Behavior |
|---|---|
| Loop hits `max_iterations=3` without APPROVE | Log Firestore `x_posts/{date}_{type}` with status=`rejected` + last reviewer notes. Email Evan via Mailgun. Return 500. **Do NOT ship a half-baked post.** |
| Image gen errors / rate limits | Ship text-only, log `image_skipped=true`. Continue publish pipeline. |
| Tweepy `create_tweet` errors (auth, rate, duplicate) | Retry 1× with backoff. On second fail: log `error`, return 500. |
| Firestore log fails | Retry 1×. On second fail: return 200 (post succeeded) with warning in body. |
| MCP server unavailable | Fall back to direct Firestore/BQ tools. (MCP is phase-2 convenience, never blocking.) |
| Planner tool returns empty (e.g. no closing trades) | Planner decides post_type → 'no_op' → publisher exits early, logs `x_posts/{date}_{type}.status=no_op`. |
| Idempotency (duplicate fire) | Publisher checks `x_posts/{date}_{type}` exists → returns `{"status":"skipped","reason":"already_posted"}`. |

---

## Success Criteria (ADK eval)

Eval cases in `tests/eval/evalsets/basic.evalset.json`. First 5 cases pre-deploy:

1. **Happy signal.** Valid `todays_pick` → APPROVE in ≤2 iterations. Char budget met, cashtag at pos 1, disclaimer present.
2. **Standby.** `todays_pick.has_pick=false` → standby post variant, no ticker references, disclaimer present.
3. **Win callback QRT.** `fetch_original_tweet_id` returns valid id; closing trade has positive P&L; post cites +X% and QRTs the original.
4. **Retired-alias regression.** Writer is seeded with instruction to use "Daily Playbook". Reviewer REVISEs. Loop eventually fails loud OR writer fixes.
5. **URL-in-body regression.** Writer tries to include gammarips.com URL. Reviewer REVISEs. Loop fixes.

Quality thresholds:
- ≥80% eval cases end in correct terminal state
- Avg loop iterations ≤2 on happy cases
- Zero false APPROVEs on cases 4 and 5

---

## Open questions

1. **`gammarips-mcp` server URL** — what's the Cloud Run URL for the MCP server? Need the SSE endpoint to wire `McpToolset`. Defer to phase 2 if unclear.
2. **Cloud Scheduler auth** — call the `x-poster` Cloud Run endpoint with `--allow-unauthenticated` (simple) or via OIDC token (more secure)? Other engine services use unauth; match for consistency.
3. **Mailgun-on-fail template** — which template for the "post rejected, manual review needed" email? Create a new one or reuse generic?
4. **GCS bucket** — does `gammarips-x-media` exist? If not, one-shot create in first deploy's `deploy.sh`.

---

*Spec locked 2026-04-24. Implementation: `libs/gammarips_content/` first, then `x-poster/app/agent.py`, `tools.py`, `fast_api_app.py` mods, `deploy.sh`. Changes to this spec require a dated note in `docs/DECISIONS/`.*
