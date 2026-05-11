# DEFERRED — Alpaca agent for live V5.4 execution

**Status:** DEFERRED. Not implemented. Trigger: see below.

**Origin (Evan, 2026-05-09):** "I'll be trading manually for now, but I'm
glad we have it documented because if we get positive expectancy from our
data and if I see I can make money trading, I'm going to turn it over to an
agent to trade using Alpaca programmatically and grow the account balance
with our top trade and strategy."

This note exists so the path is captured before context fades. Implementing
prematurely is the worst-case outcome (real money on an unmeasured edge).

## What the agent would do

A Cloud Run service (or scheduled Alpaca SDK script) that:

1. Reads `todays_pick/{scan_date}` Firestore doc each weekday at 09:55 ET.
2. If `has_pick=True` and `policy_version=V5_4_AGENT_RANKER`, places the
   options order through Alpaca Markets options API at 10:00 ET — same
   contract, same direction, sized per the operator's per-trade budget.
3. Sets the bracket programmatically:
   - GTC limit sell at `entry × 1.80` (hard +80% target)
   - GTC trailing stop with `peak × 0.75` activation at `entry × 1.30`
     (the trail this audit re-introduced into the paper trader 2026-05-09)
   - Day-3 15:50 ET market exit if neither bracket hit
4. Logs every fill back to a parallel `live_alpaca_ledger` BQ table for
   real-vs-paper EV comparison.

## Trigger conditions (ALL must hold before implementation)

1. **N ≥ 30 closed V5.4 paper trades** with measured EV ≥ 0 over the cohort.
   (Cap and floor — single-trade EV averages on N<30 are noise per the
   methodology audit.)
2. **N ≥ 15 V5.4 trades that the operator also traded manually** with
   matching directional outcome (paper trader and operator independently
   confirm the cohort makes money). Manual confirmation is the unit test
   that the paper-trader's modeled fills are achievable in real markets.
3. **Operator explicit go-ahead.** This is real money. No agentic autonomy
   shortcut. The operator confirms account size, per-trade budget, max
   position, max daily loss, kill-switch criteria.
4. **Methodology audit re-run** (`V5_4_METHODOLOGY_AUDIT_*.md` re-validation)
   showing nothing has silently broken since the last audit. Specifically
   the bracket-shape distribution, DTE quartile EV, and HEDGING-cap
   effectiveness — items 1, 4, 5, 7 from the N=15 revisit list.

## What NOT to do

- **No agent autonomy on overrides.** The agent executes the V5.4 pick or
  it executes nothing. It does NOT second-guess the Picker, take its own
  picks, or "skip on intuition." Either the entire pipeline made a pick or
  no trade happens.
- **No size scaling without operator approval.** The agent does not
  compound automatically based on its own perceived edge. Per-trade size
  is operator-set and only changes when the operator changes it.
- **No multi-pick days.** V5.4 is one pick or none per day. The agent does
  not stack picks even if multiple candidates pass thresholds — that's a
  cohort change requiring its own decision.
- **No leverage.** Cash-secured options only. No margin.
- **No naked options (selling premium).** V5.4 is buy-side only.
- **Kill-switch** must trigger automatically on (a) 5 consecutive losses
  with no skipped days, per the methodology audit's regime-shift rule, or
  (b) account drawdown ≥ 25% from peak. Both pause execution; only the
  operator can resume.

## Open design questions (revisit at trigger time)

- **Sizing rule.** Fixed per-trade dollar amount? % of account? Kelly-ish
  scaling on accumulated edge? At trigger time, decide based on N=30+
  data. Pre-trigger, this is unanswerable.
- **Slippage modeling.** Paper trader uses 2% base slippage on entry. Real
  Alpaca fills will reveal actual slippage; tune the paper trader after
  N≥10 real fills for cohort consistency.
- **Cash settlement vs assignment.** Short-dated options 7-30 DTE: ITM at
  expiry causes assignment. V5.4 closes within 3 days, so assignment risk
  is bounded but non-zero on time exits. Decide assignment-handling at
  trigger.
- **Multi-account / paper-account run-up.** Should we run on Alpaca paper
  for 1-2 weeks pre-live to validate the agent's order placement against
  the paper trader's modeled fills? Strongly recommended yes.
- **Operator notification surface.** Should the agent send an email/SMS
  on every fill, or only on exits? Daily summary? Open ETA: at trigger.
- **Manual override path.** What's the kill-switch UX? A Firestore doc the
  agent reads each cycle? A Cloud Run env var flip?

## Why we're not implementing now

- N=0 closed V5.4 trades. Methodology audit explicitly says do not retune
  any FOLKLORE parameter pre-data. Live execution is the maximum
  retune-pre-data violation.
- Operator hasn't manually traded V5.4 yet. Per CHEAT-SHEET, manual
  trading is the validation that paper-trader fills are achievable. Skip
  this and we may build an agent that executes picks the operator
  couldn't have actually filled.
- Compounding-effect risk per audit: V5.4 is implicitly a
  momentum-continuation bet on calm regimes. A regime shift mid-execution
  would be catastrophic without the 5-consec-losses tripwire in place AND
  the operator watching. Agentic execution without that watch is reckless.

## What to build before trigger fires

These are pre-requisites that should land BEFORE the trigger conditions
are met, so we can move fast at activation:

1. **Real-vs-paper EV reconciliation script.** Cron-driven SQL that joins
   `forward_paper_ledger` with the operator's manual-trade log, by
   `scan_date + ticker`. Surface divergence > 5% as a research note. This
   gives us evidence (or counter-evidence) that paper-trader fills are
   realistic.
2. **`live_alpaca_ledger` BQ table schema.** Pre-defined (just DDL, no
   writes yet) so the agent has a destination from day 1.
3. **Kill-switch Firestore doc.** `live_execution/kill_switch` with
   `enabled: true` default; agent halts if false. Operator-flippable
   without code change.

These three items are safe to land any time and are cheap.

## Related work

- `docs/DECISIONS/2026-04-17-v5-3-target-80.md` — original V5.3 decision
  with real-money posture (manual at $500/trade, $2k bankroll). This is
  the operator-manual-trading state being graduated FROM in this design.
- `docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md` — N=15 and
  N=30 revisit triggers feeding into this design.
- `docs/DECISIONS/2026-05-09-trailing-stop-25-at-30-pct.md` — the trail
  the agent will execute, completing the original Deep Research V5.3 spec.
- `docs/DECISIONS/2026-05-09-DEFERRED-few-shot-picker-exemplars.md` —
  similar deferred-design pattern; revisit at N=15.

## File / memory cross-references

- This file: `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`
- Memory pointer:
  `~/.claude/projects/-home-user-gammarips-engine/memory/project_deferred_alpaca_agent.md`
