# 2026-07-30 — Blog topic strategy: query-shaped schedule + directed improvisation + clobber guards

**Context.** SEO diagnosis (2026-07-30): organic search flat at 14 sessions/28d.
Kill-audit of Firestore `blog_posts` (22 docs, 7 published) found the 68% kill
rate was NOT the reviewer gate: 12 archived posts were a one-time 2026-07-03
repositioning purge (topics sold retired products), 2 rejections were
banned-phrase substring misfires ('for you', 'guaranteed'), 1 was a word-count
loop exhaustion. The 14-row schedule has been exhausted since ~2026-06-08 and
the planner has been silently improvising topics every Monday (8 of 22 slugs
were never schedule rows), contradicting DESIGN_SPEC edge case 1.

**Incident found.** 2026-07-13 retry storm: 3 rejected runs in 6 minutes; one
reused the slug of a published post (`building-options-flow-pipeline-ai-agents`,
published 2026-07-06) and `log_rejected`'s merge flipped the live doc
`published → rejected`, silently unpublishing an SEO page. Markdown intact
(10,135 chars); restore is a one-field status flip (owner decision pending).

**Decision.**
1. `scripts/seed_schedule.py` → v2026-07-30: re-adds wk14 (was Firestore-only)
   and 6 query-shaped pending rows — wk15–17 MCP/AI-agent cluster
   (cta `pro_trial`), wk18–20 flow education (cta `webapp_visit`), all
   `evergreen_explainer`. Titles read like search queries, not positioning.
2. Planner step 1a: on `status == "empty"` improvisation is now DIRECTED
   (query-shaped, MCP cluster priority, `fetch_prior_posts(limit=200)` first,
   never reuse a slug); on `status == "error"` the planner STOPS instead of
   improvising blind.
3. Deterministic guards (not prompts): `publish_to_firestore` and
   `log_rejected` refuse to overwrite any doc with `status == "published"`.
   Deliberate regeneration requires flipping the doc status in the console
   first. `fetch_prior_posts` clamp raised 20 → 200 (inventory is 22+).
4. DESIGN_SPEC edge case 1 rewritten to match reality.

**Known follow-ups (deliberately not in this change).**
- Restore `building-options-flow-pipeline-ai-agents` to published (owner call).
- Banned-phrase substring misfires: `'for you'` matches "for your agent";
  fix lives in shared `libs/gammarips_content/compliance.py` (blast radius:
  x-poster + newsletter) — needs its own gated pass.
- `"$19"`/`"Starter tier"` enforced only in prompts, not `RETIRED_ALIASES`.
- Disaster-recovery hazard: a FRESH `blog_schedule/current` seed would set
  retired-topic legacy rows (wk7–wk9) to pending → permanent reject loops.
- DESIGN_SPEC edge case 7 claims a `status="publishing"` transaction lock that
  does not exist in tools.py.

**Review trail.** gammarips-review: initial FAIL (step 1a triggered on
infrastructure errors; slug-reuse rule unenforceable) → both fixed → re-audit
verdict recorded in session; seed run with `--schedule-only` only.
