# Next Session Prompt

**Last session wrapped:** 2026-04-20 (big day — see below)
**Current policy:** V5.3 "Target 80" (unchanged; no execution-policy edits in this session)
**Status:** All engine services live. Paid tier launch blocked only on Evan setting up OpenClaw + Stripe.

---

## Before you do anything

Read in this order:
1. `CHEAT-SHEET.md` — operator one-pager (unchanged; still current).
2. `docs/TRADING-STRATEGY.md` — canonical execution policy. **NEW "Publication timing" section** pins the simultaneous-reveal contract (webapp + WhatsApp + MCP all see today's pick at 09:00 ET). The `signal-notifier` ORDER BY now has a deterministic 5-key tiebreaker documented here.
3. `docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md` — **the master plan for monetization.** v2.6 as of this session, with 6 amendment layers. Read §4.4 (Pricing), §4.5 (Freemium gating), §5 (Timeline), and Phase 2 (the OpenClaw agent spec + compliance guardrails) carefully.
4. `docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md` — accountable decision record.
5. `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` — **copy + SEO + 90-day blog plan, ~11K words.** Section 7 has the prioritized implementation ladder. Section 9 addendum covers AI-discoverability surfaces (llms.txt, ai-plugin.json, mcp.json, developers page) the first pass missed.
6. `docs/EXEC-PLANS/2026-04-20-mcp-chat-readiness.md` — the MCP audit that caught the direction-filter bug and pinned 4 system-prompt patterns for the Phase 2 chat agent.

---

## What happened in this session (2026-04-20)

### Engine-side work (all deployed)
- **Fixed broken Firestore sync** in `enrichment-trigger` (V5.2 had commented out `sync_to_firestore` — webapp had been rendering 4-day-stale signals). Backfilled today's data (FIX BULLISH for 2026-04-17).
- **Fixed scheduler race condition** — `agent-arena-trigger` was firing at 05:30 ET alongside enrichment, causing arena to read yesterday's enriched data. Moved arena to 06:00 ET.
- **Extended enrichment-trigger scheduler deadline** from 180s → 1800s (runs take ~8 min).
- **Phase 1.0 shipped** — `signal-notifier` now writes Firestore `todays_pick/{scan_date}` atomically before email. Deterministic 5-key ORDER BY. All 4 return paths (happy / no-candidates / regime-fail-closed / vix-backwardation) write a canonical doc. Revision: `signal-notifier-00007-pv9`.
- **Phase 1 shipped (webapp)** — home page has `TodaysPickCard` banner reading from Firestore. Killed all V3 "premium" badge/filter UI. Ghost type fields removed. Webapp commit: `e440b733`.
- **Phase 3a shipped (MCP)** — 15 tools registered. 5 new (`get_todays_pick`, `list_todays_picks`, `get_freemium_preview`, `get_open_position`, `get_position_history`, `get_enriched_signal_schema`). 2 fixes (stale score-6 gate, direction casing). Bug fixes: direction filter `LIKE` not `=`, `get_open_position` now returns composite {pending_pick, awaiting_simulation, most_recent_closed_trade, explanation} instead of pretending the batch simulator has live positions. Revision: `gammarips-mcp-00023-q8p`.
- **Diagnosed forward_paper_ledger** via `gammarips-researcher` — batch simulator runs 16:30 ET Mon-Fri processing scan_date = today-4-trading-days. NULL-entry rows are terminal `INVALID_LIQUIDITY` (Polygon had no bars on the contract at 10:00 ET day-1), not pending. Deferred hygiene fix to task #21.

### Planning work (all pushed)
- **Pricing decided** after competitive research across 25 products: Free / Starter $19 / Pro $39 / Pro Annual $399. $29 was undersold by ~4x. Founder lock: first 500 Pro subs get $29/mo lifetime. 7-day free trial. Anchor: $39 is the prosumer sweet spot (Cheddar $45, Benzinga Basic $37, OptionStrat $40).
- **Freemium gating:** gate features, not information. Daily pick / signals / report / methodology stay free. Arena full transcript + debrief pages + full performance ledger soft-gate. Chat agent + live-position tracker + watchlist + journal + alerts hard-gate.
- **Arena repurposed** to Option C: pre-entry verdict debate at 09:15 ET (after notifier, before entry). 3 agents (Claude + Grok + Gemini), 1 round, TAKE / CAUTION / SKIP. Extends `todays_pick` doc with `arena_verdict`. Paper ledger stays full-coverage as the control.
- **Compliance stance:** no counsel at this scale — legal basis is *SEC v. Lowe (1985)* publisher exclusion. Disclaimer hygiene checklist in §6.2. Counsel becomes relevant at >500 subs or state RIA challenge or if we publish real-money track record.
- **WhatsApp architecture:** OpenClaw `/hooks/agent` direct POST from `signal-notifier` at 09:00 ET + new tiny `exit-reminder` service at 15:50 ET day-3. Chat lives ONLY in the WhatsApp group (dropped webapp `/chat` widget). Agent responds only when @mentioned. Paywall = OpenClaw plugin keyed on `senderId` vs Firestore `whatsapp_allowlist`. Model: Claude Haiku 4.5 with prompt caching (~$0.10/user/month).
- **Copy plan (9.2K words + 5K addendum)** — One Promise pinned: *"One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM."* Retires "The Overnight Edge." 17 Tier 1-2 items + 13-post 90-day blog schedule. Addendum §9 adds AI-discoverability cluster (llms.txt, ai-plugin.json, mcp.json, developers page, root layout metadata). `/war-room` and `/history` flagged for KILL.

### Housekeeping
- Project ID cleanup (`profitscout-lx6bb` → `profitscout-fida8`) in 6 active-code files. Archives left alone.
- CI actions bumped to Node 24 natives (`checkout@v6`, `setup-python@v6`, `auth@v3`, `setup-gcloud@v3`).
- **CD workflow deleted** — `gcloud run deploy --source=.` from local shell has been the real deploy path. The GitHub Action was fighting cross-project IAM. CI (ruff format + lint) retained.
- Ruff format + lint now clean across MCP repo.

---

## What's blocked on Evan (not Claude)

Listed in priority order. These unblock Phase 2 (paid launch).

### Must-do before Phase 2 ships
1. **Create the private WhatsApp group + wire OpenClaw hooks.** Add OpenClaw's linked number, get `GROUP_JID`, enable hooks config `{"hooks": {"enabled": true, "token": "<secret>", "path": "/hooks"}}`. Mount 3 secrets via `gcloud secrets create`:
   - `OPENCLAW_GATEWAY_URL` (e.g., `http://<gateway>:18789`)
   - `OPENCLAW_HOOKS_TOKEN`
   - `OPENCLAW_GROUP_JID`
2. **Set up Stripe SKUs.** Starter $19/mo, Pro $39/mo, Pro Annual $399/yr, Founder $29/mo (lifetime lock for first 500 — use a separate Stripe price + coupon).

### Should-do (minor unblocks)
3. **Create Google Programmable Search Engine** at programmablesearchengine.google.com, copy the CX ID, `gcloud secrets create GOOGLE_CSE_ID --data-file=-`. Unblocks `web_search` MCP tool (task #22).
4. **Draft founder-story paragraph for About page** — copy plan flagged this for E-E-A-T + social proof (open question #3).
5. **Decide founder seat count** — plan says 500, adjustable (open question #1).

---

## High-value next steps (ordered by ROI)

Everything below is code-ready from Claude's side and doesn't require the WhatsApp group to exist. Pick top 1-3 for next session.

### 🔥 Tier 1 — conversion-critical (ship before paid launch)
1. **Pricing page rewrite** — `src/app/pricing/pricing-client.tsx` + `page.tsx`. Current schema declares `Product.offers.price = "0.00"` and title "GammaRips is Free" — shipping paid tiers without fixing this will actively damage SERP rankings. Three-tier Product schema with Offer entries drafted in copy plan §4 and §5. **~1-2 hrs.**
2. **Hero + root layout metadata** — `src/components/landing/hero.tsx` and `src/app/layout.tsx`. New One Promise hero: *"One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM."* Retires "The Overnight Edge" alias. **~30 min.**
3. **FAQ full replacement** — `src/components/landing/faq.tsx`. All 8 current items reference retired $49/$149 pricing + 8:30 AM times. 10-item replacement drafted. **~30 min.**
4. **llms.txt + ai-plugin.json + mcp.json + developers page** — the AI-discoverability cluster. Copy plan §9 flags this as "single highest-leverage block" in the whole document. These shape how ChatGPT/Perplexity/Claude describe GammaRips. **~1-2 hrs.**
5. **`signal-notifier` → OpenClaw POST wiring** — code-ready. Non-blocking fire-and-forget HTTP, try/except wrapped, activates the moment the 3 secrets land. Lines up for Phase 2 launch. **~30 min.**

### ⚙️ Tier 2 — ships alongside Phase 2 or soon after
6. **OpenClaw paywall plugin (~100 LOC TS)** — draft locally, Evan deploys into his OpenClaw install. Checks `senderId` vs `whatsapp_allowlist`, short-circuits paywall reply for unknown numbers.
7. **@mention agent system prompt** — compliance guardrails in plan §2 + 4 patterns from MCP chat-readiness audit §5.1-5.5. Ship as a drop-in OpenClaw config.
8. **Arena Phase 4 Option C** — modify `agent-arena/main.py` to read `todays_pick`, run 3-agent 1-round verdict debate at 09:15 ET, write `arena_verdict` field back. Move scheduler from 06:00 ET → 09:15 ET. **~2-3 hrs.**
9. **Exit-reminder cron service** — new Cloud Run service. Query `forward_paper_ledger` for open day-3 positions, POST OpenClaw reminder at 15:50 ET. **~1-2 hrs.**
10. **Phase 3b soft-gating UX** — arena full-transcript blur + read-through counter, per-trade debrief 48h time-delay for free users. Webapp work. **~1-2 hrs.**

### 🧹 Tier 3 — nice-to-have / post-launch
11. `/war-room` and `/history` page deletions + 301 redirects (copy plan §9.7-9.8 killed them).
12. Ledger `INVALID_LIQUIDITY` hygiene fix — stamp placeholder `exit_timestamp` + `realized_return_pct = 0.0` on terminal non-liquid rows (task #21).
13. Pre-commit hook config (solves the ruff-CI-red-on-push problem forever).
14. Legal pages tone pass — copy plan §9.9 flagged no immediate issues but worth a scan.
15. Webapp `/positions` live tracker (post-launch Phase 3c).

---

## DO NOT do

- Do NOT modify V5.3 execution policy. Entry 10:00 ET / stop -60% / target +80% / 3-day hold / exit 15:50 ET day-3. Pinned in `docs/TRADING-STRATEGY.md` and forward-paper-trader.
- Do NOT add gates to `forward-paper-trader` (rule in `.claude/rules/forward-paper-trader.md`). Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT use FMP. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1` — frozen.
- Do NOT reference retired aliases in new copy: "The Overnight Edge", "GammaRips is Free", "7 AI Models", "score >= 6", "8:30 AM", "premium signal", "$49/$149 pricing".
- Do NOT publish real-money track record until there are ≥30 closed V5.3 trades (end of May at earliest). Paper-trader stays the only marketable source until then.
- Do NOT skip the 4 agent-system-prompt patterns from MCP chat-readiness §5. They prevent embarrassing chat turns on day one.
- Do NOT deploy any MCP tool that reads from old tables (`winners_dashboard`, `options_chain`, `calendar_events`, `performance_tracker` singular) — those are V2-era and empty under `profitscout-fida8`.

---

## Deployed revision sheet

| Service | Revision | Deployed | Notes |
|---|---|---|---|
| signal-notifier | `signal-notifier-00007-pv9` | 2026-04-20 13:45 UTC | V5.3 + todays_pick writer + 5-key tiebreaker |
| enrichment-trigger | `enrichment-trigger-00032-2z4` | 2026-04-20 15:30 UTC | Firestore sync restored |
| forward-paper-trader | `forward-paper-trader-...` | 2026-04-20 13:46 UTC (morning) | Untouched by this session |
| agent-arena | `agent-arena-...` | 2026-04-10 | Scheduler moved to 06:00 ET |
| overnight-report-generator | `overnight-report-generator-...` | 2026-04-10 | Working |
| gammarips-mcp | `gammarips-mcp-00023-q8p` | 2026-04-20 20:30 UTC | 15 tools + P0 direction-filter fix |
| gammarips-webapp | `e440b733` (Firebase) | 2026-04-20 | TODAY'S PICK banner live |

Canonical scheduler cron:
- `overnight-scanner` — `0 23 * * 1-5` ET (23:00 ET Mon-Fri)
- `enrichment-trigger-daily` — `30 5 * * 1-5` ET (5:30 ET, deadline 1800s)
- `agent-arena-trigger` — `0 6 * * 1-5` ET (moved from 5:30 today to avoid enrichment race)
- `overnight-report-generator-trigger` — `15 8 * * 1-5` ET
- `signal-notifier-job` — `0 9 * * 1-5` ET
- `forward-paper-trader-trigger` — `30 16 * * 1-5` ET (batch simulator)
- `track-signal-performance` — `30 16 * * 1-5` ET
- `polygon-iv-cache-daily` — `30 16 * * 1-5` ET

---

## Key facts to hold in memory

- **Paper-trader is a batch simulator.** No live positions in `forward_paper_ledger`. Every row is terminal. Chat-agent answers framed as {pending_pick, awaiting_simulation, most_recent_closed_trade} — never fabricate unrealized P&L.
- **Two win-rate universes.** `get_win_rate_summary` = `signal_performance` (enriched 3-day forward returns, ~30/day, ~80% win rate). `get_position_history` = `forward_paper_ledger` (V5.3 realized bracket trades, 1/day). NEVER conflate them.
- **V5.3 filter stack.** Enrichment: score≥1, spread≤10%, UOA>$500K. Notifier: V/OI>2, moneyness 5–15% OTM, VIX≤VIX3M, LIMIT 1 ORDER BY 5-key deterministic.
- **15 MCP tools** registered. Web search still broken until `GOOGLE_CSE_ID` is provisioned.
- **NULL-entry ledger rows = INVALID_LIQUIDITY terminal state.** Downstream MCP queries filter them via `exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')`.
- **Disclaimer on every user-facing surface:** "Paper-trading performance, educational only. Not investment advice."

---

## Open questions for Evan (from copy plan)

1. Founder-price seat count: 500 sticks, or adjust to 250 (tighter scarcity) / 1,000 (dilutes)?
2. GammaMolt character scope — About-only, or wider?
3. Founder-story 200-300 words for About page (E-E-A-T + social proof)?
4. Which Reddit subs for blog schedule — plan recommends skipping r/wallstreetbets for Month 1-2?
5. Hero CTA A/B — "See Today's Pick" (free-funnel) vs "Start 7-Day Free Trial" (Pro) once tier is live?

---

## Subagents available in `.claude/agents/`

- **`gammarips-engineer`** — code cleanup, deployment fixes, BQ integration. Use for implementation work.
- **`gammarips-researcher`** — backtests, cohort analysis, BQ diagnostic reads. Read-only.
- **`gammarips-review`** — audits for lookahead bias, data leakage. **ALWAYS invoke before any forward-paper-trader or signal-notifier diff deploys.**

New subagents proven useful this session (general-purpose + Explore): ledger diagnosis, MCP chat-readiness audit, copywriting/SEO research, pricing research. Spawn fresh for one-shot deliverables.

---

*End of handoff. First action next session: ask Evan the status of the WhatsApp group setup + the GOOGLE_CSE_ID secret. If both done, go direct to Phase 2 code. If not, work the Tier 1 copy rewrites list.*
