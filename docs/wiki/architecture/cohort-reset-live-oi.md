Status: superseded
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-25-cohort-reset-live-oi.md
Date: 2026-07-17

# Cohort reset for the live-OI floor regime (floor → 2026-06-26)

On 2026-06-25 `forward_paper_ledger` was truncated (3 rows dumped to scratch first) and the
cohort floor pulled forward to **2026-06-26**, so the public scorecard starts clean on the
**live-OI liquidity-floor** selection regime ([[live-oi-floor]]). Same shape as the V7.1 tilt
reset three days earlier. The dumped rows included TTWO (already floor-excluded), VICR (the
lone trade the scorecard was showing), and AFL (the INVALID_LIQUIDITY pick that motivated the
floor).

This is the reset that set the then-current `LIVE_COHORT_START_DATE='2026-06-26'`
([[v7-1-tilted-gigo-live-policy]]) — an instance of the reset-on-filter-change practice
([[cohort-reset-on-filter-change]]), here for a selection-regime change (fresh liquidity read)
rather than an exit change.

**Superseded 2026-08-20.** The cohort has reset again three times since (07-28, 08-07,
08-12). The live value is `LIVE_COHORT_START_DATE` in `signal-notifier/main.py`
(2026-08-13 as of the 2026-08-12 reset). This note stays as the record of the 06-25
reset only.
