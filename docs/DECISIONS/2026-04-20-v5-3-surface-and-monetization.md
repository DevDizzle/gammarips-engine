# Decision: V5.3 surface alignment + $29/mo WhatsApp monetization plan

**Date:** 2026-04-20
**Status:** Plan approved in principle, Phase 1.0 pending Evan sign-off on audit amendments
**Authors:** Evan Parra + Claude (session 2026-04-20)
**Supersedes:** informal webapp/MCP/arena state; the V3-era "premium_score" is no longer a tradeable concept under V5.3

## Decision

1. Adopt a five-phase plan to bring all non-trading surfaces (webapp, MCP, arena, GTM content, WhatsApp paywall) into lockstep with V5.3 Target 80 execution policy. Plan lives at [`docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md`](../EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md).
2. Introduce Firestore `todays_pick/{scan_date}` as the **single source of truth** for what GammaRips picked on a given day. Schema pinned in the EXEC-PLAN Phase 1.0 section.
3. Move the WhatsApp push out of `forward-paper-trader/main.py` entirely. Push is fired by a new `whatsapp-notifier` service subscribed to Pub/Sub event `gammarips-pick-decided`, published by `signal-notifier` after it writes `todays_pick`.
4. Paying $29/mo subscribers pay for **convenience** (automated push delivery before the 10:00 ET entry moment), NOT for timing advantage. Free users see the same pick on the webapp at the same moment. Strategy doc will be updated before Phase 1 ships.
5. Agent arena output becomes **retrospective commentary** on closed trades (post-15:50 ET day-3), not pre-entry commentary. This prevents a silent paper-vs-real divergence from arena spooking operators off real-money trades while the paper ledger takes them anyway.
6. GTM content (X, Reddit) is **drafted by the engine, emailed to Evan, posted manually**. No Reddit automation. X auto-posting (if it currently exists in `win-tracker` or elsewhere) gets routed through the drafter for approval.

## Why

- **Surfaces drifted from engine.** Webapp renders V3 "premium" flags; MCP has a stale `score >= 6` gate that contradicts V5.3 (`>= 1`); arena picks don't agree with notifier picks on any of the last 21 trading days; GTM has no content pipeline. Reconnaissance reports from three Explore agents (2026-04-20) documented every instance.
- **Monetization thesis is clean** when paid = convenience and free = information. Attempting to blur the webapp for paywall reasons would contradict the freemium strategy and create legal exposure (paying for "timing advantage" is a higher-scrutiny sales framing).
- **One source of truth avoids drift.** Five surfaces (notifier email, webapp banner, WhatsApp push, MCP tool, GTM draft) would otherwise each need to replicate the V5.3 filter SQL. That is a drift magnet. Firestore `todays_pick/{scan_date}`, written exactly once by `signal-notifier`, eliminates the class of "webapp says AAPL, WhatsApp says MSFT" bugs by construction.
- **Audit made the above concrete.** `gammarips-review` found two BLOCKERS (push inside trader is fundamentally wrong timing; inline Firestore+HTTP couples failure domains) and four HIGHs (front-running risk, drift tripwire missing, writer timing undefined, arena feedback loop). Plan v2 addresses all of them.

## Audit findings resolved in plan v2

| # | Severity | Finding | Resolution in plan v2 |
|---|---|---|---|
| 1 | BLOCKER | Push inside forward-paper-trader fires at 16:30 ET simulator time, not 10:00 ET entry | Push moved to `signal-notifier` at 09:00 ET via Pub/Sub to `whatsapp-notifier` |
| 2 | BLOCKER | Inline Firestore subscriber query + HTTP in trader couples failure domains | No sync HTTP/Firestore writes in trader. Pub/Sub decouples. `.claude/rules/forward-paper-trader.md` gets a new forbidding rule |
| 3 | HIGH | Free users see pick at 09:00 ET → pay for nothing; or pay user delayed to 10:00 ET → pay for worse fill | Framing fixed: paid = convenience, not timing. Webapp + WhatsApp both reveal at 09:00 ET. Strategy doc updated |
| 4 | HIGH | "Mirror signal-notifier exactly" had no tripwire | Nightly drift-check scheduler compares email + Firestore doc + MCP output; alerts on diff |
| 5 | HIGH | `todays_pick` writer timing undefined | Pinned to `signal-notifier` at 09:00 ET. Writer is Phase 1.0 prerequisite. Schema frozen in plan |
| 6 | HIGH | Pre-entry arena commentary creates real-vs-paper divergence | Arena output moved to post-15:50-ET retrospective commentary only |
| 7 | MEDIUM | Phase 2/3/5 SLAs under-specified | Specific times + drift assertions added to each DoD |
| 8 | MEDIUM | PIT violation risk in GTM drafter's use of `signal_performance` | Hard-filter `exit_timestamp IS NOT NULL AND DATE(exit_timestamp) < CURRENT_DATE()` |
| 9 | MEDIUM | Webapp cache invariant missing | `revalidate: 60` + explicit "no pick yet" state |
| 10 | LOW | Secrets-in-source not mentioned | Secret Manager mandate added to all phases |
| 11 | LOW | Phase 1 sequencing | Split out Phase 1.0 (schema + writer) as prerequisite to Phase 1 readers |
| 12 | LOW | Simulator version protection | Phase 2 DoD bars any diff to `POLICY_VERSION`, `POLICY_GATE`, `LEDGER_TABLE`, record schema |

## Open items requiring Evan

Listed in plan Section 7. Blockers on execution of specific phases:
- **Phase 1.0 start:** requires sign-off on audit amendments (this doc).
- **Phase 2 ship:** requires legal/compliance confirmation and OpenClaw API contract.
- **Phase 4 arena direction:** keep with post-close reshape or kill entirely.
- **Phase 5 X-posting source:** locate existing auto-poster, decide route.

## What does NOT change

- Trading strategy itself. V5.3 Target 80 execution policy, the gates, the -60%/+80% stop/target, the 3-day hold, the 10:00 ET entry, the 15:50 ET day-3 close — all unchanged. See [`docs/TRADING-STRATEGY.md`](../TRADING-STRATEGY.md) for the canonical spec.
- `forward-paper-trader/main.py` in Phase 2 (explicit non-diff requirement).
- `overnight_signals_enriched` schema or the enrichment gates.
- FMP is still retired from forward-paper-trader per `.claude/rules/forward-paper-trader.md`.

## Rollback plan

If any phase ships poorly:
- **Phase 1 (webapp):** revert the Firebase deploy by reverting the webapp commit and pushing.
- **Phase 1.0 (notifier writer):** revert `signal-notifier/main.py` to pre-writer state; the `todays_pick` doc becomes stale but nothing blocks.
- **Phase 2 (WhatsApp):** pause the scheduler job on `whatsapp-notifier`; subscribers stop receiving pushes; trader and notifier unaffected.
- **Phase 3 (MCP):** redeploy previous revision; tools revert.
- **Phase 4 (arena reshape):** trivially revert scheduler + code; BQ arena tables keep writing.
- **Phase 5 (GTM drafter):** disable scheduler; no user-facing impact.

## References

- Plan: `docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md`
- Audit findings (in-conversation, 2026-04-20): 12 numbered findings from `gammarips-review`
- Canonical strategy: `docs/TRADING-STRATEGY.md`
- V5.3 Target 80 decision: `docs/DECISIONS/2026-04-17-v5-3-target-80.md`
- Trader rules: `.claude/rules/forward-paper-trader.md`
- Research reports (reconnaissance, in-conversation): webapp / MCP / arena Explore agents
