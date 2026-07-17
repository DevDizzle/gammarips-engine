Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (leakage/data-contract fix on the research substrate)
Source: docs/DECISIONS/2026-07-01-regime-scan-date-leakage-fix.md
Date: 2026-07-17

# Regime feature is as-of scan_date close (research substrate leakage fix)

In `enriched_option_outcomes`, `VIX_at_entry` / `SPY_trend_state` / `vix_5d_delta_entry`
were filed under FEATURES but computed by `get_regime_context(entry_day)` = the latest
close ≤ entry_day. Because the V7 trade opens 10:00 and closes 15:45 the SAME entry_day, an
entry_day close is realized AFTER the trade closed — a headless agent conditioning on it
would **leak the future**. It was also non-deterministic (the daily cron might catch only
scan_date's close while backfill caught entry_day's).

Fix: the regime FEATURE is now computed as-of **scan_date close** (the real decision-point
regime, since selection happens overnight into entry_day); the entry_day close is retained
only as labeled telemetry, not a feature. Scope: research substrate ONLY — `forward_paper_ledger`
and the live pick path keep their documented `VIX_at_entry` telemetry unchanged. This is a
concrete instance of the standing leakage discipline ([[assert-no-leakage-gate]]).
