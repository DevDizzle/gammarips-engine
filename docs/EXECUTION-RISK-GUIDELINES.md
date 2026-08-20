# Execution-Risk Guidelines (for autonomous traders)

**Status:** active, evidence-backed. Written 2026-08-19.
**Audience:** the autonomous trading agents (the live-money Robinhood lane, the
`gammarips-trader` harness, and any subscriber agent driving the MCP).
**Scope:** execution only. This document does not change selection, and it does not
change the V7.1 execution policy in `docs/TRADING-STRATEGY.md`. It tells an agent how to
reason about the gap between a good pick and a realised fill.

**Design intent: this is a calibration, not a rule engine.** The MCP already hands the
agent the raw fields (`get_liquidity` serves open interest, session volume, day range,
`day.last_updated`). What it never gave the agent is the measured meaning of those fields.
That mapping is below. Every number is measured. Read them as priors an agent reasons
with, not as gates it obeys.

---

## 0. The constraint that shapes everything: we have no spread

Confirmed 2026-08-19 against `pool_liquidity_snapshot`: `bid`, `ask`, `mid`, `spread_pct`
and `last_trade_price` are NULL in **all 64,550 reads**. This Polygon plan serves no
options NBBO ([[spread-gate-retired]]). The true cost of crossing the market is therefore
**unmeasurable** with our current data.

Two consequences, and an agent must hold both:

1. Every number in this document is a **print-based proxy** for execution cost. None of
   them is the spread.
2. Any claim of the form "this contract is cheap to trade" is unsupported. The strongest
   honest statement is "this contract prints often enough that the price I see is
   probably near the price I get."

The one paid upgrade that would close this gap is a Polygon NBBO plan. It is parked on an
owner cost decision. Until then, execution risk is inferred from the tape.

---

## 1. The four execution risks, ranked by measured damage

### Risk 1 — The contract is a ghost (largest, most ignored)

From the 2026-07-28 tradeability study (15 entry days, N=750, `FINDINGS_LEDGER.md`):

| measure | share of pool |
|---|---|
| trades under 50 contracts on entry day | **42.8%** |
| GHOST, under 10 contracts | **22.3%** |
| trades exactly zero | **8.9%** |

This replicated on every one of 15 days. It is a property of the pool, not a bad week.

### Risk 2 — The stop is not a stop (sharpest asymmetry)

New measurement, 2026-08-19, on the day-1 minute tape. For every leg entered at 10:00 ET
whose −30% stop level was breached (N=547), where would you actually have filled?

| contract's traded minutes | legs | median fill vs stop | p10 | p01 |
|---|---|---|---|---|
| under 10 | 48 | **−10.3%** | −24.1% | −38.5% |
| 10-29 | 125 | −5.1% | −23.7% | −35.1% |
| 30-59 | 159 | −3.0% | −11.5% | −27.7% |
| 60-119 | 131 | −2.5% | −8.0% | −13.0% |
| 120-199 | 61 | −1.7% | −6.6% | −11.2% |
| 200+ | 23 | −1.8% | −6.6% | −9.3% |

All legs: median **−3.1%** past the stop, p10 **−14.5%**, p01 **−30.4%**, worst **−44.0%**.
**33.6% of stops fill more than 5% below the intended level. 10.1% fill more than 15%
below.**

Read that against the policy. A −30% stop on a contract that trades under 10 minutes is a
−40% stop at the median-to-p10 and a −54% stop in the tail. **This is the single most
important execution number in this document**, because it is asymmetric: you only slip on
the losing side, so it moves the tail without moving the mean opportunity.

### Risk 3 — Price uncertainty between prints (the spread substitute)

If a contract's consecutive prints sit far apart in price, no agent can expect a fill near
the last price it saw, whatever the spread is. Measured over 114,267 consecutive-print
steps:

| gap between prints | median move | p90 | p99 |
|---|---|---|---|
| 1 min (continuous) | 1.6% | 6.4% | 16.7% |
| 5-14 min | 3.0% | 10.9% | 28.3% |
| 15-29 min | 4.2% | 14.3% | 35.4% |
| 30-59 min | 5.6% | 18.8% | 44.4% |
| 60+ min | **8.2%** | 26.7% | 62.7% |

By the field an agent can actually see (how much the contract has printed):

| traded minutes | legs | median move between prints | p90 | median gap |
|---|---|---|---|---|
| under 10 | 2,306 | **6.2%** | 19.7% | 40 min |
| 10-29 | 848 | 4.0% | 8.6% | 10 min |
| 30-59 | 550 | 3.0% | 5.8% | 5 min |
| 60-119 | 371 | 2.4% | 4.2% | 2 min |
| 120-199 | 154 | 2.0% | 3.4% | 1 min |
| 200+ | 63 | **1.5%** | 2.6% | 1 min |

Context for the magnitude: the median same-day peak return under V7.1 is **+3.8%**
(memory `same-day-vs-3day-window-mismatch`, delta 0.35-0.65, N=2,112). On the thin half of
the pool, the price uncertainty between two consecutive prints is larger than the median
same-day opportunity.

### Risk 4 — Stale marks (smallest, fully fixable, still live)

Polygon serves the **prior session's** day bar when a contract has not printed yet today
(memory `polygon-snapshot-never-zero-day-bar`). At the 09:45-10:00 ET read, **44% of
pool-of-50 rows carry a stale bar** (`docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md`).
Raw `day.volume` is never 0 and never NULL in 49,285 reads, so a naive read cannot detect
this. It already produced one real-money loss (GCT, 2026-08-07, card printed
"2045 prints by ~09:52" against a contract that had traded zero).

---

## 2. The one observable that dominates: prints by 10:00 ET

New measurement, 2026-08-19. Count a contract's date-validated prints by 10:00 ET, then
ask whether the rest of the day is manageable (60 or more further traded minutes):

| prints by 10:00 ET | share of pool | P(60+ prints left) | median prints left |
|---|---|---|---|
| **0 (silent tape)** | 36.6% | **0.0%** | 2 |
| 1-2 | 26.1% | 0.5% | 5 |
| 3-5 | 13.2% | 2.6% | 17 |
| 6-10 | 10.2% | 13.5% | 32 |
| 11-20 | 9.3% | 50.6% | 60 |
| **21+** | 4.7% | **93.0%** | 138 |

This is close to deterministic at both ends, and it independently corroborates the
2026-07-28 finding (early ≥5 prints → 96.3% finish ≥50 contracts, early ≥20 → 100%).

**The operational consequence: roughly 14% of the pool is comfortably manageable, and
about 63% is effectively untradeable by 10:00.** An agent that reads this one field before
sizing removes most of its execution risk.

### The anti-heuristic: premium does NOT predict liquidity

| premium | median traded minutes | P(60+ minutes all day) | median move between prints |
|---|---|---|---|
| under $0.50 | 12 | 15.6% | 6.9% |
| $0.50-1 | 11 | 15.5% | 5.0% |
| $1-2 | 13 | 16.9% | 4.0% |
| $2-5 | 10 | 13.8% | 3.5% |
| **over $5** | **6** | 12.2% | 3.1% |

Expensive contracts print **less**, not more. Do not use premium, moneyness or "it is a
big name" as a liquidity proxy. Count prints.

---

## 3. What is NOT the problem (do not spend effort here)

A symmetric round-trip cost model barely moves the result, because a percentage bracket
is scale-invariant: enter higher and your stop and target scale with you. Replaying the
identical V7.1 bracket on identical legs under three fill conventions (N=1,317) gives a
tier drag of about 2 to 4 points, with no clean liquidity gradient.

**So the execution problem is not "you pay a wide spread twice."** It is "you cannot
transact when you need to." That is why Risk 1 and Risk 2 dominate this document, and why
the guidelines below are about *exit certainty*, not entry price.

Caveat on that replay: it requires a real print at both 10:00 and 15:45, which selects the
most liquid members of every thin tier (the "under 10" cell is only 70 legs). Treat it as
"the round trip is second-order", not as a precise cost estimate.

---

## 4. Guidelines

These are priors and reasoning inputs. None is a hard gate. An agent that can justify an
exception against the numbers above should take it and log why.

**G1. Read the tape before you read the pick.** Call `get_liquidity` and count today's
date-validated prints before you size anything. Prints by 10:00 ET is the highest-value
field on the entire surface. Zero prints is a 36.6%-of-pool event with a 0.0% chance of a
manageable day.

**G2. Always date-validate.** Compare `day.last_updated` against today's session before
you believe any volume number. 44% of morning reads are the prior session. A volume figure
without a validated timestamp is not evidence.

**G3. Size on exit certainty, not on direction confidence.** The pick tells you about
direction. The tape tells you whether you can leave. When those disagree, the tape wins,
because a good direction you cannot exit is a bad trade. Practical form: let position size
scale with print density, and treat the thin tail as research-only rather than
capital-bearing.

**G4. Price your stop at the realised level, not the intended one.** Before entering, ask
what a −30% stop actually costs on this contract. On a 200+ print contract the answer is
about −32%. On a sub-10-print contract it is about −40% at the median and −54% in the
tail. Size so that the **realised** stop is survivable. If it is not, the position is too
big regardless of how good the pick is.

**G5. On a thin tape, prefer a time exit to a price exit.** A price stop needs a
counterparty at your price. A time exit only needs a counterparty. When the contract is
thin, leave while the tape is still alive rather than waiting for a level that may never
print at a fillable price.

**G6. Exit where the prints are, not where the clock is.** Session coverage by 30-minute
block (share of legs printing):

| block | legs printing | mean prints |
|---|---|---|
| 09:30-10:00 | 63.0% | 6.5 |
| 10:00-10:30 | 56.5% | 5.7 |
| 10:30-11:30 | 66.0% | 7.6 |
| 11:30-13:00 | 66.9% | 8.1 |
| 13:00-14:30 | 64.4% | 7.0 |
| 14:30-15:30 | 57.1% | 5.4 |
| **15:30-16:00** | **51.6%** | **4.3** |

The last half hour is the thinnest block of the day. A 15:45 flat exit is planned into the
worst liquidity of the session. On a thin contract, exiting earlier into a denser block is
usually the better execution even at a slightly worse price.

**G7. Never chase.** The published card already carries `do_not_chase_above` (mark × 1.08)
and `limit_good_til` 10:15 ET. Honour both. If the fill does not come, the trade does not
happen. A missed trade costs zero. On a thin contract a chased entry raises your stop and
your target in absolute terms while the tape stays just as unable to fill you.

**G8. Do not hold overnight.** Options do not trade overnight, so the stop cannot execute
in the gap. Measured 2026-08-19: the same-day arm's p05 is −31.4% because the stop is the
floor, while every overnight arm prints p05 near −53%. See `FINDINGS_LEDGER.md`
§2026-08-19 (PM entry / morning pop).

**G9. Never trust simulated PnL on a ghost.** `INVALID_LIQUIDITY` catches only 37% of
ghosts. The other sim-"filled" ghosts show mean −2.8% with 79% `illiquid_exit`. Those are
stale marks, not safe trades. A human pays roughly a 30% effective spread on them
(2026-07-28 study, research hygiene rule).

---

## 5. Known gaps

- **No NBBO.** The dominant cost driver is still unmeasured. A Polygon quote plan is the
  only fix, and it is an owner cost decision.
- **Stop-slippage N is modest** (547 breach events, 23 in the deepest tier) and covers one
  regime (Apr-Aug 2026). The tier ordering is monotonic and large, so the direction is
  safe; the precise levels are not.
- **Nothing here is validated against real fills.** Every number comes from the trade tape,
  not from our own executions. The live Robinhood lane is the first source of real fill
  data. Once it accrues, compare realised fills against these priors and re-fit.
- **The 2026-07-28 ghost thresholds were fitted in-sample** on 15 days across roughly 825
  searched cuts. Re-fit rolling before relying on the specific cut points.

---

## 6. Sources

- `docs/research_reports/FINDINGS_LEDGER.md` §2026-07-28 (evening) — ghost-pool study
- `docs/research_reports/FINDINGS_LEDGER.md` §2026-08-19 — PM entry / overnight hold
- `docs/research_reports/FINDINGS_LEDGER.md` §2026-08-19 (execution) — this calibration
- `backtesting_and_research/2026-08-19_execution_risk_calibration.py` — every new number
- `docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md` — the staleness trap
- `docs/wiki/policy/live-oi-floor.md` — what the engine already screens at pick time
- `docs/wiki/architecture/spread-gate-retired.md` — why there is no spread
