# 2026-05-08 — V5.3 retired, V5.4 promoted to canonical

## Decision
Operator decision late 2026-05-08: V5.4 is now the only product. V5.3 is retired across every user-facing surface (email, webapp, x-poster, paid subscribers, marketing copy). `forward_paper_ledger` truncated (246 rows wiped) so V5.4 starts a clean cohort from today.

This **supersedes** [`2026-05-08-v5-4-locked-spec.md`](2026-05-08-v5-4-locked-spec.md) — the original "V5.3 + V5.4 cohabit via `policy_version`, V5.3 retires only when V5.4 wins on N≥30 closes" plan is dead. V5.4 goes direct-to-product without the parallel-cohort proving period.

Full implementation handoff: [`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`](../EXEC-PLANS/2026-05-08-v5-4-promotion.md).

## Why now
Operator's read after seeing Phase 3 wired end-to-end ("I don't care at all about V5.3"):
- V5.4's lit-anchored 60/25/15 weighting + multi-input Picker reasoning is the better product story than V5.3's deterministic 4-key SQL `ORDER BY`.
- Subscriber paid funnel needs ONE pick to market, not a "primary V5.3 / shadow V5.4" split that's confusing to explain.
- V5.3's 14-day ledger pattern (10W/32L bearish, 47W/45L bullish) the V5.4 Picker cited as evidence is itself a sign that V5.3's static ranker is mismatched to the current regime — the cohort proves the picker change is needed, not that we should wait 30 trades.
- Park-mode is over. V5.4-as-product means active iteration on prompts/weights based on real returns, not a passive 30-trade observation window.

## Three locked decisions
| Question | Resolution |
|---|---|
| Truncate scope | **Full TRUNCATE TABLE** (all 246 rows). LIVE_COHORT_START_DATE resets to 2026-05-08. cohort_stats/current shows 0 trades until V5.4's first close. |
| V5.4 error handling | **Fail-closed.** No V5.3 fallback. signal-ranker timeout / out-of-set / 5xx → no email, no WhatsApp, no x-poster, empty `todays_pick`. signal-ranker uptime is now an SLO. |
| Subscriber rollout | **Promote V5.4 immediately.** Operator email + paid subscriber emails BOTH carry the V5.4 pick from the next 07:30 ET cron (2026-05-09 Fri). No separate operator-only shadow block. |

## What V5.4-as-canonical means in practice
- `todays_pick/{scan_date}` Firestore doc carries the V5.4 pick. All readers (webapp banner, MCP `get_todays_pick`, x-poster signal, gamma-bot, blog newsletter "featured trade") get V5.4 automatically — no per-reader code change.
- `forward_paper_ledger.policy_version` is `V5_4_AGENT_RANKER` for every row. The "official V5.4 pick" is identified by ticker matching `todays_pick`, NOT by a special policy_version tag.
- `todays_v5_4_pick/{scan_date}` doc is RETIRED — `todays_pick` IS the V5.4 pick.
- The forward-paper-trader V5.4 sidecar (mirror picked-ticker row) is RETIRED — all rows are V5.4 now, no second-row mirroring needed.
- Email subject + body: drop "V5.3 Target 80" copy; replace with "GammaRips agent ranker" or just "GammaRips" (TBD wording).
- cohort_stats/current is scoped to `policy_version='V5_4_AGENT_RANKER'` (the only policy_version going forward, but the filter remains for forward-compat).
- 30-trade DoD gate (win-tracker email watchdog) re-anchored to V5_4_AGENT_RANKER. The watchdog flag in Firestore (`park_watchdog/gate_30_alerted`) is reset so the email fires when V5.4 hits 30 closes.

## What V5.4-as-canonical does NOT mean
- V5.3 hard gates stay. `volume_oi_ratio > 2`, `moneyness 5-10%`, `OI ≥ 20`, `volume ≥ 100`, `VIX ≤ VIX3M`, earnings-overlap exclusion all run UPSTREAM of the V5.4 picker. They produce the candidate pool. Removing them would remove V5.4's filter (the picker's job is to choose among already-clean candidates).
- Trader execution mechanics unchanged: entry 10:00 ET day-1, stop -60%, target +80%, 3-day hold, exit 15:50 ET day-3. V5.4 is a picker change, not a trader change.
- The frozen `signals_labeled_v1` research dataset stays untouched per `.claude/rules/scripts-research.md`. V5.4 cohort attribution starts fresh from `forward_paper_ledger` rows on or after 2026-05-08.

## Replaces
- `2026-04-17-v5-3-target-80.md` — V5.3 adoption (now retired)
- `2026-05-08-v5-4-locked-spec.md` — original "cohabit via policy_version" plan (superseded)
- `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md` Phase 3 spec (superseded — operator email is no longer side-by-side; subscribers no longer V5.3-only)

## State at decision time (2026-05-08 EOD)
- `forward_paper_ledger`: TRUNCATED (0 rows) at 23:48 UTC.
- `signal-notifier-00019-gsw`: still has the V5.3 + V5.4 dual-path code. Phase 1 of the handoff EXEC-PLAN rewrites this to V5.4-only.
- `signal-ranker-00004-5nt`: scorer_v3 + picker_v2, IAM-only, DRY_RUN=true. Will need DRY_RUN flipped to false once Phase 4 IC eval is wired (currently no `signal_ranker_runs` writes).
- `forward-paper-trader-00030-8ct`: still has the V5.4 sidecar. Phase 2 of the handoff retags POLICY_VERSION to V5_4_AGENT_RANKER and removes the sidecar.
- `todays_v5_4_pick/2026-05-07` Firestore doc exists (the WFC pick). Becomes a stale artifact — next-session work optionally cleans it up.
