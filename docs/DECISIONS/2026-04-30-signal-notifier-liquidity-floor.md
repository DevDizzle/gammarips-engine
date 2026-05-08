# 2026-04-30 — Signal-notifier liquidity floor

## Decision
Add two new gates to `signal-notifier`'s LIMIT-1 query:
- `recommended_oi >= 20`
- `recommended_volume >= 100`

These are applied alongside the existing `volume_oi_ratio > 2`, `moneyness 5–15% OTM`, and `vix3m_at_enrich IS NOT NULL` gates inherited from `enrichment-trigger`.

Constants live at `signal-notifier/main.py:56-57` as `OI_MIN = 20` and `VOL_MIN = 100`.

## Why
Investigation on 2026-04-30 found the daily curated pick had a **40% fill-rejection rate** (2 of 5 picks in window 2026-04-13 → 04-23 stamped `INVALID_LIQUIDITY` by `forward-paper-trader`):
- 2026-04-20 — APP `O:APP260529C00560000` — OI=1, vol=10 — zero printed bars on entry day
- 2026-04-21 — SATS `O:SATS260529C00134000` — OI=2, vol=22 — zero printed bars on entry day

Root cause: `signal-notifier` ranks candidates by previous-day directional UOA dollars. A ticker can have $50M+ in chain-wide UOA while the specific recommended strike has OI=1 and never trades on entry day. The trader's gate at `forward-paper-trader/main.py:367-383` correctly catches this (any minute bar with v>0 → fill; no bars all day → INVALID_LIQUIDITY), but by then the user has already received the email recommending an unfillable contract.

Fixing this in `signal-notifier` (upstream) keeps the architectural rule that **signal-quality gates do not live in the trader** (per CLAUDE.md and `2026-04-17-v5-3-target-80.md`).

## Impact (verified against live data)
Across the 9 scan dates 2026-04-17 → 04-29 in `overnight_signals_enriched`:

| filter set | days with ≥1 candidate | total candidates |
|---|---|---|
| current (no OI/vol floor) | 9 / 9 | 126 |
| **OI ≥ 20 AND vol ≥ 100** | **9 / 9** | **27** (−79%) |

The daily-pick guarantee is preserved on every day in the window. Both rejected picks (APP, SATS) would have been filtered out and the LIMIT-1 ranking would have promoted the next-best candidate on those days.

## Caveat
Even with this floor, fill quality remains bursty: ~3 of 8 alternate picks tested had zero printed bars at 10:00–10:30 ET on entry day. The 5–15% OTM moneyness band is inherently thin. This fix collapses the worst failure mode (OI=1 contracts that literally never trade) but does not get fill quality to 100%. Achieving that would require either (a) moving the entry window from "10:00 ET" to "first valid print of the day", or (b) pivoting from far-OTM strikes to near-ATM strikes. Both are strategy changes requiring `gammarips-review` and 30-day OOS paper validation per the V5.3 mandate, and are explicitly out of scope here.

## Alternatives considered and rejected
- **Tighten `volume_oi_ratio > 2` to `> 5`.** Rejected: V/OI is a ratio, it goes UP when OI=1, vol=10 (= 10.0). Tightening it makes the bug worse.
- **Tighten `spread_pct <= 10%` to `<= 5%`.** Rejected: both rejects had recorded spread = 0.0% because there was no two-sided quote to measure. The spread check is a no-op for these contracts.
- **Add the gate to `forward-paper-trader`.** Rejected: violates CLAUDE.md rule that signal-quality gates live in `enrichment-trigger` and `signal-notifier`, not in the trader.
- **Quote-scoring / Monte Carlo fill probability.** Rejected: user goal is explainable simplicity, not sophistication.

## Changes
- `signal-notifier/main.py:56-57` — add `OI_MIN = 20`, `VOL_MIN = 100`.
- `signal-notifier/main.py:498-499` — add `recommended_oi >= {OI_MIN}` and `recommended_volume >= {VOL_MIN}` to the LIMIT-1 query.
- `CHEAT-SHEET.md` — add gates 7 and 8 to the signal-filter list.

## Deploy
`cd signal-notifier && bash deploy.sh` after `gammarips-review` audit.

## Validation
After deploy, monitor next 5 daily picks for `exit_reason` distribution in `forward_paper_ledger`. Target: zero `INVALID_LIQUIDITY` entries on the LIMIT-1 pick. Re-evaluate at N=20 fillable picks (~4 weeks).
