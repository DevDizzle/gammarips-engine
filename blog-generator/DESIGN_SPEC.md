# DESIGN_SPEC — blog-generator

**Service:** `blog-generator` (Cloud Run, ADK-based, Gemini 3 Flash preview)
**Repo location:** `/home/user/gammarips-engine/blog-generator/`
**Triggered by:** Cloud Scheduler job `blog-generator-weekly` (Mon 05:00 ET)
**Deployment target:** `cloud_run` (session: in-memory, prototype-first; no CI/CD yet)

---

## Overview

`blog-generator` is an ADK multi-agent system that writes and publishes one GammaRips blog post per week, end-to-end, with no human-review gate. It fires from Cloud Scheduler Monday 05:00 ET, reads the next unpublished slot from the 13-post 90-day schedule (stored in Firestore), runs a planner → writer → reviewer loop until the reviewer APPROVEs, and writes the approved post to Firestore `blog_posts/{slug}` with status `published`. The webapp (`gammarips.com/blog`) renders directly from Firestore.

The quality contract is the reviewer agent's rubric — a 6-point check against One Promise alignment, SEC v. Lowe publisher framing, retired-alias hygiene, disclosure presence, internal-link density, and keyword-for-SEO. Max 3 loop iterations; on limit, fail loud and Firestore-log an alert, do NOT ship a half-baked post.

This replaces the Tier-3 MDX-filesystem blog approach in `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` §7 — Firestore + cron-driven publication unlocks automation without a code deploy per post.

---

## Example Use Cases

### 1. Weekly scheduled publication (primary flow)
- **Input:** Cloud Scheduler POST `/run` with empty body (uses today's date).
- **Flow:** Service reads `blog_schedule/current` Firestore doc to find the next row with `status = "pending"`. Planner drafts outline. Writer drafts markdown. Reviewer scores + returns APPROVE or REVISE-with-notes. Loop up to 3×. On APPROVE → write `blog_posts/{slug}`, update schedule row `status = "published"`, POST completes.
- **Output:** `{"status":"published","slug":"why-uoa-is-mostly-noise","iterations":2,"reviewer_score":8.5}`

### 2. Manual backfill / retry
- **Input:** POST `/run` with `{"slug":"why-uoa-is-mostly-noise"}`.
- **Flow:** Targets a specific row in the schedule regardless of status. Useful after a failed run.
- **Output:** Same shape as (1).

### 3. Dry-run preview
- **Input:** POST `/run` with `{"dry_run":true}`.
- **Flow:** Full loop runs; final markdown returned in response body; nothing written to Firestore `blog_posts`.
- **Output:** `{"status":"dry_run","slug":"...","markdown":"# Why UOA...","reviewer_score":8.2}`

### 4. Hard fail (reviewer can't approve in 3 iterations)
- **Input:** Same as (1).
- **Flow:** Loop hits iteration limit. Writer's last draft has not passed review. Instead of publishing, service writes to `blog_posts/{slug}` with status `rejected` and the reviewer's notes; emails Evan via Mailgun; returns 500.
- **Output:** `{"status":"rejected","slug":"...","iterations":3,"reviewer_notes":"..."}`

### 5. Health probe
- **Input:** GET `/health`.
- **Output:** `{"service":"blog-generator","firestore_ready":true,"vertex_ready":true,"schedule_loaded":true,"next_slot":"wk_3_vix3m_gate"}`

---

## Tools Required (ADK tool surface)

Each tool is a Python function the agents call. No external SDK secrets (Vertex uses default ADC; Firestore uses default ADC).

| Tool | Used by | Purpose |
|---|---|---|
| `read_schedule_slot(slug_or_latest: str = "next") -> dict` | planner | Returns next-pending schedule row from `blog_schedule/current` (or a specific slug). Fields: `slug`, `week_num`, `title_candidate`, `persona`, `keywords`, `cta`, `type`, `cross_channel[]`. |
| `read_voice_rules() -> dict` | writer | Returns a dict of voice rules extracted from `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` §2 (or from Firestore `blog_config/voice_rules`, seeded by a one-shot script). |
| `read_prior_posts(limit: int = 5) -> list[dict]` | planner, reviewer | Returns last N published posts from Firestore `blog_posts` for reference + internal-link targets. |
| `read_live_context() -> dict` | writer | Reads today's signal (`todays_pick`), last-week closed trades (BQ `forward_paper_ledger`), current V5.3 policy flags. Used when the post needs live data (e.g. weekly engine recap). Gated by post `type` — evergreen posts skip. |
| `score_against_rubric(markdown: str, keywords: list[str]) -> dict` | reviewer | Deterministic checks: word count, H2/H3 count, disclaimer present, retired-alias scan, internal-link density, keyword density. Returns structured scores. |
| `publish_to_firestore(post: dict) -> str` | root | Writes to `blog_posts/{slug}` with status `published`, timestamp, reviewer score. Also updates `blog_schedule/current.rows[i].status = "published"`. Only called after reviewer APPROVE. |
| `log_failure_to_firestore(slug: str, notes: str) -> None` | root | Writes to `blog_posts/{slug}` with status `rejected` + notes. Called on iteration-limit fail. |

## Agents (planner / writer / reviewer)

All three use `gemini-3-flash-preview` (scaffold default). Orchestration: `LoopAgent` with `max_iterations=3`. Loop termination condition: reviewer writes APPROVE to session state key `review_status`.

### Planner
- **Input:** schedule slot + prior posts + live context (if post type demands).
- **Output state key:** `post_outline` — JSON with `h1`, `intro_hook`, `sections[]` (each `h2`, `bullets[]`), `internal_links[]` (2+ from prior posts), `closing_cta`.
- **Instruction contract:** Must produce a scan-friendly outline (Ogilvy: facts sell). 1200–1800 target word count. 3–5 H2 sections. Must specify the primary keyword + 2 secondary from schedule row.

### Writer
- **Input:** `post_outline` + voice rules.
- **Output state key:** `post_markdown` — full markdown body. Front matter YAML block with `title`, `slug`, `description`, `keywords`, `cta`, `reading_time`.
- **Instruction contract:** Write in Evan-brand voice (§2 of copy plan). Specific dollar amounts + specific times. Publisher framing only. Must end with the standard disclaimer + a tier-matched CTA from the schedule row. Never use retired aliases ("Ripper", "Daily Playbook", "Overnight Edge" as product name, "@mention" for chat tag).
- **Revision behavior:** If session state has `reviewer_notes`, Writer reads them and produces a revised `post_markdown`.

### Reviewer
- **Input:** `post_markdown` + structured `score_against_rubric()` results.
- **Output state key:** `review_status` = `"APPROVE"` | `"REVISE"`, and `reviewer_notes` with specific fixes if REVISE.
- **Rubric (binary pass/fail + free-text notes):**
  1. **One Promise alignment** — Does the post ladder to "one trade a day, scored before you wake up, pushed to your phone at 9 AM"?
  2. **Publisher framing (SEC v. Lowe)** — No individualized recommendation language. "Buy this", "act now", second-person timing imperatives = FAIL. Policy/methodology framing = PASS.
  3. **Disclosure** — Disclaimer block present and unmodified.
  4. **Internal-link density** — ≥1 link to another blog post + ≥1 link to a methodology page (`/how-it-works`, `/signals`, `/about`).
  5. **Keyword density** — Primary keyword appears in H1 + first paragraph + at least 2 H2s. Not stuffed (max 1.5%).
  6. **Retired-alias scan** — Zero matches for: "Ripper", "Daily Playbook", "Overnight Edge" (as product name), "@mention", "score >= 6", "8:30 AM", "$49/$149", "premium signal", "interactive dashboard".

Loop exits APPROVE only if rubric passes + reviewer agrees holistically.

---

## Constraints & Safety Rules

- **No human-review gate.** The reviewer agent is the only gate. This is intentional per Evan 2026-04-24. If reviewer can't APPROVE in 3 iterations, the post is marked `rejected` and Evan is emailed — it does NOT ship.
- **Never fabricate trade outcomes or ticker examples.** When `read_live_context()` is called, all numerics must come from the tool output, not the model. Reviewer rubric rule: numeric claims must be traceable to `live_context` or flagged as structural (e.g. "max per-trade loss is $300 on a $500 position").
- **No real-money P&L** until V5.3 has ≥30 closed trades (per `docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md` §6). Reviewer blocks posts that claim win rates before the track record unlock date. Enforce via `read_live_context().closed_trade_count >= 30` as a precondition for any performance-claiming post type.
- **Disclaimer is literal.** Writer must use the exact string: "Paper-trading performance, educational content only. Not investment advice. Past performance is not a guarantee of future results." No paraphrasing.
- **Keyword targets come from the schedule, not the writer.** Writer cannot invent new keywords; that's SEO drift.
- **NEVER change the model** in `app/agent.py` unless explicitly asked. Current: `gemini-3-flash-preview`.
- **NEVER deploy without `make test` + at least 2 eval cases passing.** This service affects public-facing marketing copy; eval is non-negotiable.
- **Dry-run first production deploy.** First Cloud Run revision deploys with `DRY_RUN=true` env var. Evan inspects 1–2 generated posts in Firestore (status `dry_run_draft`). Only then flip to `DRY_RUN=false`.

---

## Success Criteria (for Phase-3 ADK eval)

Eval cases live in `tests/eval/evalsets/basic.evalset.json`. Minimum suite before first production run:

1. **Happy path, evergreen post** (Wk 1 "Why UOA is mostly noise"). Reviewer APPROVEs in ≤2 iterations. Final markdown: 1200–1800 words, disclaimer present, zero retired aliases, ≥2 internal links.
2. **Happy path, case study post** (Wk 2 FIX-vs-OKLO). Reviewer APPROVEs in ≤3 iterations. Reviewer flags if Writer fabricates numbers not in `live_context`.
3. **Blocked by track record gate** (Wk 10 equivalent but with `closed_trade_count=5`). Reviewer REVISEs until Writer removes win-rate claim, OR service fails loud on iteration limit. Expected: fail loud (not approve a watered-down post).
4. **Retired-alias regression** (Writer is instructed to use "Daily Playbook"). Reviewer must REVISE. If reviewer approves anyway → eval fail.
5. **Internal-link density fail** (Writer drops all internal links). Reviewer REVISEs.

Quality thresholds:
- ≥80% of eval cases end in correct terminal state (APPROVE on good input, REJECT on bad input).
- Average loop iterations ≤2 on happy-path cases.
- Zero false APPROVEs on adversarial cases (cases 3, 4, 5).

---

## Edge Cases to Handle

1. **Schedule exhausted** — All 13 rows published. Service returns `{"status":"no_pending_slots"}` with 200. Emails Evan to add more rows.
2. **Firestore down** — `publish_to_firestore` fails. Service retries 3× with exponential backoff. On final fail: returns 500 with the markdown in the response body so Evan can manually publish.
3. **Vertex AI rate-limited** — ADK retry options handle 429s (already set in scaffold: `retry_options=HttpRetryOptions(attempts=3)`). If all 3 attempts fail, fail loud.
4. **Schedule row missing required field** (e.g. no keywords) — Planner flags it, service returns 400 without spending agent tokens.
5. **Writer produces >3000 words** — Reviewer REVISEs with "trim to 1800". If Writer can't trim in 1 pass, continues loop; if iteration limit hits, `rejected`.
6. **Writer uses a retired alias that wasn't in the block list** — Only way to catch is human inspection of published posts. Mitigation: weekly sanity-read of Firestore `blog_posts` by Evan.
7. **Two Cloud Scheduler fires overlap** (unlikely but possible on retry) — Service uses Firestore transaction to flip schedule row `status = "publishing"` atomically; second fire sees `publishing` and returns `{"status":"skipped","reason":"in_progress"}`.
8. **Tier-1 post (Wk 1–4) with `publisher_gate_enabled=true`** — If we later decide the first 4 posts DO need human review, flip a single Firestore config flag; service adds `status = "draft"` on publish, skipping auto-public. This is a future-proofing hook, disabled by default.

---

## Schema: Firestore

### `blog_schedule/current`
```json
{
  "version": "2026-04-24",
  "rows": [
    {
      "slug": "why-uoa-is-mostly-noise",
      "week_num": 1,
      "title_candidate": "Why \"Unusual Options Activity\" Is Mostly Noise (And the One Signal That Isn't)",
      "persona": ["A", "D"],
      "keywords": ["unusual options activity", "UOA", "volume open interest ratio"],
      "cta": "webapp_visit",
      "type": "evergreen_explainer",
      "cross_channel": ["x_thread", "reddit_options", "linkedin"],
      "status": "pending"
    }
  ]
}
```

### `blog_posts/{slug}`
```json
{
  "slug": "why-uoa-is-mostly-noise",
  "title": "Why 'Unusual Options Activity' Is Mostly Noise (And the One Signal That Isn't)",
  "description": "Most UOA feeds are 99% noise. Here's the one filter that isolates the signal.",
  "markdown": "# Why 'Unusual Options Activity'...\n\n...\n",
  "keywords": ["unusual options activity", "UOA", "volume open interest ratio"],
  "cta": "webapp_visit",
  "published_at": "2026-05-04T05:14:33Z",
  "reviewer_score": 8.5,
  "iterations": 2,
  "status": "published",
  "reading_time_min": 6
}
```

### `blog_config/voice_rules`
Seeded one-shot from `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` §2. Flat list of DO / DO-NOT strings + retired-alias block list.

---

## Open design questions (Evan decides before implementation)

1. **Schedule source** — Firestore-only (simple, one seed script), OR Firestore-mirrored from the markdown plan file (round-trip complexity)? **Recommend Firestore-only, seed once, edit in Firestore console if the schedule changes.**
2. **Live-context post types** — which of the 13 posts need `read_live_context()`? Proposing: Wk 7 (weekly engine recap), Wk 10 (first-30 trades), Wk 11 (post-mortem), Wk 13 (bonus routine demo). All others = evergreen, no live data. Confirm.
3. **Evan-email-on-fail channel** — Mailgun from `evan@gammarips.com`, or a different alert path (PagerDuty, Slack)? **Recommend Mailgun to `evan@gammarips.com`**, consistent with existing deliverability.
4. **Cross-channel artifact generation** — should `blog-generator` ALSO draft the X thread + Reddit post versions? Clean separation = no. Different services (`x-thread-generator`, handed to `reddit-drafter`). **Recommend: blog-generator does blog only; a separate Wk 2 service handles X-thread conversion.**
5. **Webapp `/blog` route** — will be a separate webapp repo patch. Listed as "ready to ship" task once `blog_posts` has ≥1 document.

---

*Spec locked 2026-04-24. Implementation proceeds only after Evan confirms the 5 open questions above. Changes to this spec require a dated decision note in `docs/DECISIONS/`.*
