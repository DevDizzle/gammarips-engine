# Next Session Prompt

**Last session wrapped:** 2026-04-27 (X publisher LIVE, MCP hardened to 18 tools, blog-gen unblocked, webapp cleanup, email-only delivery locked)
**Current policy:** V5.3 "Target 80" — unchanged. Still ~0 closed paper trades; track-record narrative gates on ≥30 closed (~end of May 2026).
**Operator goal:** ship-and-park GammaRips so Evan can shift bandwidth to other projects, return when V5.3 ledger crosses 30 closed.

---

## Read first (in this order)

1. `CHEAT-SHEET.md` — operator one-pager.
2. `docs/DECISIONS/2026-04-27-mcp-hardening-x-poster-live-email-only.md` — **what shipped today** (4 bundled decisions: MCP hardening, x-poster live, email-only lock, /signals/[ticker] kill).
3. `docs/EXEC-PLANS/2026-04-27-90-day-content-plan.md` — **the 90-day GTM content plan** (blog + Reddit + email cadence, Apr 28 → Jul 27 2026, calibrated to track-record milestones).
4. `gammarips-mcp/SECURITY.md` — trust model. Read before adding any new MCP tool.
5. `blog-generator/DESIGN_SPEC.md` — read before deploying blog-generator (next session's first action).

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## Definition of "GammaRips finished" (Evan's stated intent)

Four surfaces auto-running with zero daily attention. Then he parks the project until V5.3 produces ≥30 closed trades and the track-record narrative arc unlocks.

| Surface | State as of 2026-04-27 |
|---|---|
| **`x-poster`** — @gammarips X publisher, 5 schedulers, 5×/day | ✅ LIVE (revision `x-poster-00017-ggj`, DRY_RUN=false) |
| **`blog-generator`** — auto-publish weekly to Firestore + render on `/blog` | ⏳ Code unblocked + pushed (`4eb9a80`); first deploy + Firestore seed pending Evan's go |
| **Reddit-drafter** — emails Evan weekly with `(GCS link, target sub, time, copy-paste instructions)` | ⏳ Not started — design in 90-day GTM plan; reuse blog-gen scaffold |
| **Email marketing** — weekly newsletter + Stripe lifecycle (welcome, trial-end, win-back) | ⏳ Not started — Mailgun + DMARC + Proofpoint allow-list ready; email-drafter is variant-of blog-gen pattern |

---

## Priority ladder for next 4 sessions (in order)

### Session 1 (next) — Blog-generator first deploy

**Why first:** blog content is the raw material that feeds Reddit + email surfaces. Lifeblood of the content factory.

**Steps:**

1. Read `blog-generator/DESIGN_SPEC.md` and `blog-generator/scripts/seed_schedule.py`.
2. Run the seeder once: `cd blog-generator && uv run python scripts/seed_schedule.py` — populates prod Firestore `blog_schedule/current` + `blog_config/voice_rules`. Read-only-after re-runs.
3. `bash deploy.sh` with DRY_RUN=true first (verify Firestore write happens but no public publish).
4. Smoke-test against the Wk-1 post slug ("Why UOA is mostly noise"): `curl -X POST <url>/run -H "Content-Type: application/json" -d '{"slug":"why-uoa-is-mostly-noise","dry_run":true}'`. Verify markdown lands in Firestore `blog_posts/{slug}` with valid YAML front matter, 1,200-1,800 words, ≥2 internal links + 1 methodology link, canonical disclaimer block.
5. Smoke webapp render: `https://gammarips.com/blog/why-uoa-is-mostly-noise` should serve the rendered post.
6. Flip DRY_RUN=false in `blog-generator/deploy.sh`, redeploy.
7. Create `blog-generator-weekly` Cloud Scheduler job — `0 5 * * 1` America/New_York → `POST /run` no body.
8. Update `docs/DECISIONS/2026-04-27-mcp-hardening-x-poster-live-email-only.md` with deployment-notes addendum.

**Gotcha left from today's commit `4eb9a80`:** writer + reviewer prompts now expect `schedule_slot` and `live_context` as nested fields inside `post_outline`. Verify the planner actually produces that shape before claiming smoke-passed. The fix is verbal-only; no test exercises it.

### Session 2 — Stripe-webhook lifecycle (welcome + trial-end emails)

Minimum-viable: just two emails (welcome on `customer.created` + trial-end-3 on `customer.subscription.trial_will_end`). Skip the other 5 emails until churn data demands them. Reuse Mailgun + the existing trial-end template Evan got intercepted today by Proofpoint (which is now fixed).

### Session 3 — Reddit-drafter scaffold

Variant of blog-generator. Emails Evan weekly Thu 10:00 ET with 3 GCS-hosted markdown drafts + per-sub posting metadata. Per-sub voice variance handled by the planner reading subreddit rules from a Firestore `reddit_subs/{sub_name}` doc. **Do not** auto-post to Reddit — just draft + email. Manual posting Fri-Sun.

### Session 4 — Email-marketing weekly newsletter

Variant of blog-gen. Sunday afternoon cadence. Pulls last-week ledger summary + top runners-up + blog excerpt. Sends to current Mailgun list (free signups + WhatsApp invitees + churned trials).

---

## Pending engineering work (smaller items, batch when convenient)

- `x-poster` local-dev ergonomics — `gammarips_content` is only vendored at Docker build; `make playground` / direct `uv run` needs `PYTHONPATH=/home/user/gammarips-engine/libs/gammarips_content`. Add a `make install-dev` target that `uv pip install -e`'s the lib into the venv.
- `webapp` `/about?welcome=1` WhatsApp invite link — leftover from pre-email-only era. Decide: leave (community surface) or remove (avoids confusing paid-product expectations). Punted from 2026-04-27.
- CSE 2027 deprecation prep (8 months out) — convert CSE to a curated finance-news whitelist (FT, WSJ, Bloomberg, Reuters, MarketWatch, SeekingAlpha, ~20 sites) before Jan 1, 2027. Better quality than open web for an options-flow bot anyway. Don't act yet; just remember.

## Pending on Evan (admin)

- **GA_API_SECRET rotation** — when conversion tracking turns on (Phase 2). Silent no-op until then.
- **Proofpoint allow-list verification** — added 4 entries today (`gammarips.com`, `mg.gammarips.com`, the bounce email, evan@gammarips.com). Watch the next Stripe trial-end email at the work inbox: confirm rendered HTML + clickable "Manage subscription" link survive intact. If still stripped, file a ticket with `owenec.com` Proofpoint admin team referencing the DKIM `d=mg.gammarips.com` alignment.
- **Blog content review window** — after blog-gen ships, glance at the first 2 auto-published posts before they go to Reddit-drafter as raw material.

---

## Key facts to hold in memory

### Production state

| Service | Revision | Notes |
|---|---|---|
| `x-poster` | `x-poster-00017-ggj` | LIVE, DRY_RUN=false, 5 schedulers, first tweet `2048829378331558255` |
| `gammarips-mcp` | `gammarips-mcp-00027-mcl` | 18 tools (3 new today: market-calendar, signal-explainer, historical-performance); rate-limited 60/min default + 10/min web_search; `GOOGLE_CSE_ID` mounted |
| `forward-paper-trader` | unchanged | V5.3 ledger ~0 closed; trader-trigger fires Mon-Fri 16:30 |
| `enrichment-trigger` | unchanged | gates: score≥1, spread≤10%, UOA>$500K |
| `signal-notifier` | unchanged | gates: V/OI>2, moneyness 5-15%, VIX≤VIX3M, LIMIT 1 |
| `agent-arena`, `overnight-report-generator` | unchanged | |
| `blog-generator` | NOT DEPLOYED | code unblocked `4eb9a80`; pending first deploy |
| `webapp` | latest (`d3b53241`) | `/signals/[ticker]` killed, footer cleaned, Disallow `/signals/` |

### x-poster cadence (Mon-Fri ET unless noted)

- 08:30 `report` — overnight brief from `overnight_reports/{date}` (Gemini synthesis, written at 08:15)
- 09:05 `signal` (or `standby` fallback) — V5.3 daily pick from `todays_pick/{date}`. Standby fallback when no pick clears gates.
- 12:30 `teaser` — top 3 runner-ups from `overnight_signals_enriched`
- 16:45 `callback` — win (QRT) / loss (single) / skip-on-empty if no closes today (writer ticker=null detected by Publisher)
- Fri 17:00 `scorecard` — 3-tweet thread, weekly recap

### Disclaimer canonical (writer canonicalizes; reviewer can't approve drift)

- Signal/standby/teaser/report: `⚠️ Paper-trade. Not financial advice.`
- Win/loss/scorecard: `⚠️ Paper-trade. Not advice.`

### MCP guarantees (from `gammarips-mcp/SECURITY.md`)

- Read-only against BQ + Firestore + GCS + Polygon + Google CSE
- Parameterized queries everywhere (no SQL-injection vector)
- Per-IP token-bucket rate limit (60/min default, 10/min web_search)
- All errors sanitized via `utils.safety.safe_error` (project IDs, table paths, SA emails redacted)
- Schema introspection whitelisted to 18 public-safe columns (`_PUBLIC_SCHEMA_COLUMNS` in `tools/metadata.py`)
- Trust model + vuln-report contact in `gammarips-mcp/SECURITY.md`

---

## DO NOT do

- Do NOT modify V5.3 execution policy. Entry 10:00 ET / stop −60% / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT use FMP. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27.
- Do NOT add a customer-facing chat agent in V1. The bot is sandboxed to `gammarips-mcp` and routes group `@gamma` mentions only — DMs still hit Evan personally. Re-evaluate post-track-record.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record. Founder pricing $39/mo uncapped is the only commercial surface.
- Do NOT add MCP tools without going through `safe_error` / `clamp` and adding to `_PUBLIC_SCHEMA_COLUMNS` if the tool surfaces BQ schema.
- Do NOT publish real-money track record until V5.3 has ≥30 closed trades.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation work.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier deploys.** Not needed for x-poster / blog-gen / mcp.

For GTM / content / strategy work this session: spawned a `general-purpose` subagent. Consider creating `.claude/agents/gammarips-gtm.md` if more than 2 GTM-focused sessions land in a row.

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Today added:
- `project_mcp_hardened.md` — MCP is sole attack surface; `safe_error`/`clamp`/rate-limit pattern.
- `project_email_only_delivery.md` — WhatsApp deprecated as of 2026-04-27.
- `project_finished_definition.md` — Evan's 4-surface ship-and-park criteria.
- `feedback_no_own_subreddit.md` — don't recommend r/gammarips; Discord if community needed.

---

*End of handoff. First action next session: blog-generator first deploy + Firestore seed + scheduler. After that, work the 4-surface ship-and-park ladder in `docs/EXEC-PLANS/2026-04-27-90-day-content-plan.md`.*
