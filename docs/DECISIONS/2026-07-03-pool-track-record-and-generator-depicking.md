# 2026-07-03 — Public Track Record tracks the POOL; content generators de-picked; pick leaves every public surface

**Owner calls (this session):** (1) the public scorecard must track *everything
the engine produces daily* — the ~50-candidate enriched pool — not the
tournament pick ("this was aligned with our old 1-pick-per-day approach");
(2) extend outcome tracking toward expiration (multi-day follow collector —
same build the mom_60 3-day validation arm needs; not landed today);
(3) full site coherence pass after a three-persona adversarial audit found the
site "three companies sharing one domain."

## What changed

### 1. Pool outcomes replace the pick-cohort scorecard (public surface)
- NEW win-tracker endpoint `POST/GET /pool_outcomes`: aggregates
  `enriched_option_outcomes` (whole labeled pool: same-day bracket labels,
  3-day labels, opportunity surfaces) → Firestore `pool_outcomes/current`.
  Values are FRACTIONS. Fail-loud on degraded substrate. Idempotent recompute
  from BQ truth (an unauth trigger can only refresh, not poison).
- Cloud Scheduler: `pool-outcomes-refresh` daily 17:20 ET weekdays (after the
  17:00 label cron), POST to win-tracker `/pool_outcomes`.
- Webapp `/scorecard` → **Track Record**: distribution tiles (median/p90 peak
  excursion, median drawdown, blind-buy baseline avg + WR, counts) with the
  NEGATIVE blind-buy baseline published prominently. Homepage cohort tiles
  replaced by the same pool tiles. Pick-cohort `cohort_stats`/`ledger_trades`
  retired from all public surfaces (pipelines keep running; data stays
  operator-private). Compliance shape: distributions + conditions, never one
  blended ROI headline (per `project_gigo_pool_composite_negative`).

### 2. Nightly generators de-picked (prompt_version bumps)
- `enrichment-trigger`: thesis prompt → **`thesis_v2_descriptive`** — data
  narrative voice; no entry/target/stop, no "recommended", no scan-count
  quoting (fixes the 127-vs-50 public inconsistency); "RECOMMENDED CONTRACT"
  block → "FOCUS CONTRACT". Output JSON schema unchanged.
- `overnight-report-generator`: **`report_v3_descriptive`** — "Per-Candidate
  Directional Calls" → "Pool Snapshot"; no trade instructions on any horizon
  (the "3-day premium" advice was DEAD V6 policy); bullish-share/z-score
  commentary forbidden (pool is bullish-only by construction); no internal
  field-name debris in prose. Pydantic field names unchanged.
- `blog-generator` + `libs/gammarips_content/voice_rules.py`: positioning
  context updated to free-site/Agent-Access; retired-product strings
  (WhatsApp, $19 tier, pushed pick, −60/+80/3-day) forbidden at the
  writer/reviewer PROMPT level (LLM instruction, not deterministic).
  DELIBERATELY NOT added to `RETIRED_ALIASES` (the deterministic scorer):
  x-poster's own live templates contain "GammaRips pick today"/"Curated
  daily pick" and would hard-fail at its next deploy — add the aliases in
  the dedicated x-poster pass together with the template rewrites.
  NOTE: voice_rules is vendored into x-poster at ITS next deploy.

### 3. X + blog pick exposure closed
- Cloud Scheduler PAUSED (reversible): `x-poster-signal-0800` (publicly
  posted the private pick's ticker+direction daily), `x-poster-callback-1645`,
  `x-poster-scorecard-fri-1700` (pick-cohort stats). `watchlist` + Monday
  `report` remain enabled (pool-level content; watchlist's footer line still
  says "Curated daily pick → email subscribers only" — fix in a dedicated
  x-poster pass before re-enabling anything).
- Firestore blog triage (owner-approved): 9 posts archived (sold retired
  products / built on dead V6 exits), 3 patched (removed −60/+80 example
  parameters + "See today's pick" closers). Webapp ships 301s for the 9
  archived slugs.

## Not changed
Live trading policy (V7.1 GIGO), forward-paper-trader, signal-judge,
signal-notifier, ledger mechanics — all untouched. The tournament + validation
cohort keep running privately.

## Follow-ups
- Multi-day/to-expiration follow collector (public outcomes-through-expiry +
  mom_60 3-day arm — one collector, two consumers).
- Dedicated x-poster pass: retire/rewrite the `signal` post type + pick-era
  template lines, then re-enable crons that make sense.
- blog-generator: regenerate on-message replacements for the archived posts;
  consider a prompt_version convention for ADK agents.
- ~~signal-notifier subscriber emails~~ **DONE 2026-07-03 (late):** the paid-
  subscriber pick fan-out was RETIRED and deployed (`signal-notifier-00053-xjt`,
  review SHIP). The old code emailed the pick to every `plan=pro/active` user —
  i.e. every future Agent Access subscriber; the only matching account at
  retirement was the operator's own. Operator email + WhatsApp path unchanged
  (note: `OPENCLAW_*` env vars are absent on the live service, so the WhatsApp
  push has been silently fail-soft skipping — operator delivery is email).
- **WhatsApp/OpenClaw channel DEPRECATED (owner call, late 07-03):**
  `post_to_openclaw` is now a hard no-op (`signal-notifier-00054-vsb`) — the
  channel cannot be revived by re-adding env vars; all ten call sites are
  unchanged (the function was already never-raises). The retired
  implementation is kept inline as history. `tools/openclaw/
  whatsapp_allowlist_sync.py` is likewise dead tooling. Webapp-side residue
  for the parallel key-lifecycle session: the Stripe webhook still writes
  `whatsapp_allowlist/{uid}` on new subs — harmless (nothing reads it) but
  should be dropped in that session's webhook cleanup.
