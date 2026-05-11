# 2026-05-09 — Trailing stop re-introduced (25% off peak, activated at +30% gain)

## Decision

`forward-paper-trader/main.py` adds a trailing-stop conditional that
completes the original V5.3 Deep Research recommendation. Mechanics:

- **Trigger:** once peak premium during the hold reaches `entry × 1.30`
  (any bar high; intraday counts), the trail activates.
- **Trail level:** `peak_premium × (1 - 0.25) = peak × 0.75`. Ratchets up
  with every new peak; never moves down.
- **Effect:** original `−60%` hard stop is dominated by the trail once
  active (at peak +30%, trail = 0.975 × entry vs hard 0.40 × entry). The
  `+80%` hard target is unchanged.

New BQ columns on `forward_paper_ledger` (`ALTER TABLE ADD COLUMN IF NOT
EXISTS`, completed 2026-05-09):

- `trail_trigger_price FLOAT64` — `entry × 1.30`, recorded at trade setup.
- `peak_premium FLOAT64` — highest bar high observed during the hold.
- `trail_activated BOOL` — true if peak ≥ trigger at any point.
- `trail_stop_at_exit FLOAT64` — the trail level at the moment of exit, if
  trail was active. Null otherwise.

`exit_reason` adds new value `"TRAIL"` (existing values: `TARGET`, `STOP`,
`TIMEOUT`, `INVALID_LIQUIDITY`, `SKIPPED`).

## Why

The 2026-04-17-v5-3-target-80 decision quotes Deep Research:

> "A pure 3-day timeout should be completely abandoned. Implement a hard
> take-profit target at +80% to +100%, combined with a trailing stop-loss
> that activates only after the option has achieved a +30% gain."

V5.3 deployed the +80% target but **deferred the trailing stop and the
underlying-based stop to Phase 2** for one specific reason — Robinhood
mobile execution didn't support OCO orders that condition on premium peaks.
That deferral was an *operator-execution constraint*, not a methodology
choice.

Two contexts now make the constraint moot:

1. **Paper trader is programmatic.** The bar walk can model the trail
   exactly. Recording it gives us peak/drawdown distributions that the
   N=15 audit (per `V5_4_METHODOLOGY_AUDIT_2026_05_09.md`, Finding 1) needs
   to evaluate the +80%/-60% bracket shape itself.
2. **Future Alpaca-agent execution** (deferred design saved 2026-05-09)
   removes the mobile constraint entirely. When that path activates, the
   trail will execute exactly as the paper trader models.

## Bracket precedence (intrabar conservative)

When a bar both crosses the trail trigger AND has a low below the resulting
trail level (e.g., bar high = +50%, bar low = +10%), we assume worst-case
intrabar sequence: high happens first → trail activates → low happens second
→ trail triggers. Exit at trail level. This matches the existing STOP-vs-
TARGET conservative ordering.

Composite precedence per bar:

1. TIMEOUT — first bar at-or-after 15:50 ET on `exit_day`. Always wins.
2. TRAIL or STOP — whichever is active. Trail dominates once peak ≥ trigger.
3. TARGET — `+80%` take-profit.

## Literature support

Trailing stops have broad market-microstructure literature support
(Jegadeesh-Titman 1993 momentum continuation, Glasserman-Wu 2010 on
optimal-stopping bracket design). For options specifically, Whaley & Cheang
1996 modeled the asymmetry between stop-loss and take-profit on premium
returns. **None of these prescribe "25% off peak after +30% gain"
specifically** — those values are the Deep Research operator calibration.
The audit's earlier classification stands: this is FOLKLORE-level support
for the specific values, but LITERATURE-BACKED for the trailing-stop
*concept*. The N=15 revisit will measure peak-and-drawdown distributions
to validate or retune.

## Risk and rollback

**Risks:**
- The trail can both activate and trigger on the same bar. This is a
  legitimate model of intrabar volatility but produces tight exits on
  highly-volatile bars (e.g., a single up-and-down bar that pierces both
  the trigger and the trail level locks profit early).
- Adding the trail changes EV characteristics. Paper-trader EV under V5.4
  with trail will not be directly comparable to V5.3 paper-trader EV.
  This is acknowledged and accepted; the alternative (running both in
  parallel) is more complexity for limited cohort-attribution gain.

**Rollback:** revert the trader main.py edits (single commit). The 4 new BQ
columns become unused but harmless (NULL on rollback rows). `exit_reason="TRAIL"`
rows become anomalous — handle with a `WHERE exit_reason != "TRAIL"` filter
in any post-rollback analysis.

## Files

- `forward-paper-trader/main.py` — bar walk + record schema + startup log.
- `forward_paper_ledger` BQ schema — 4 columns added.
- `docs/DECISIONS/2026-05-09-trailing-stop-25-at-30-pct.md` — this note.
- `docs/TRADING-STRATEGY.md` — to be updated with bracket section.

## Audit

`gammarips-review` pre-deploy audit required (forward-paper-trader rule).
Specific concerns for the auditor:

1. **Same-bar activation + trigger** — verify the conservative ordering
   matches the existing STOP-vs-TARGET ambiguity policy.
2. **Peak update placement** — peak is updated from `bar.high` BEFORE the
   exit check on the same bar. Verify this is the intended behavior (it
   is; documented above) and not a bug.
3. **Lookahead** — peak only ever uses bars up to and including the
   current iteration. No future bars peeked. Verify.
4. **TIMEOUT path** — peak does NOT update from the timeout bar (loop
   breaks before the peak update). This is the correct semantics: peak
   is the realized peak DURING the held window, exclusive of the timeout
   bar where we're forced to exit at close. Verify acceptable.
5. **Floor case** — if no bar has `high > base_entry`, peak stays at
   base_entry, trail never activates, original −60% stop applies. Verify.

## Cohort attribution

`policy_version` stays `V5_4_AGENT_RANKER` (NOT bumped to a new label).
Rationale: the ledger is empty post-truncate, so this trail addition is
part of "what V5.4 actually is" — not a separate cohort. Future analyses
that need to distinguish trail-on vs trail-off can pivot on
`trail_trigger_price IS NOT NULL` (set on every V5.4 row from this point
forward; would be NULL on any pre-2026-05-09 row, of which there are none).
