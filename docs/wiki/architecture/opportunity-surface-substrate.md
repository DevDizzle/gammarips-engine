Status: active
Type: architecture
Tag: architecture-fact
Exit-context: research substrate captures MFE/MAE so exit stays a free variable; 3-day arm is a LABEL never a trade
Source: docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md; docs/DECISIONS/2026-06-17-enriched-option-outcomes.md
Date: 2026-07-17

# enriched_option_outcomes captures the opportunity surface (MFE/MAE) + persists mom_60

`enriched_option_outcomes` is the ongoing, leakage-safe, OPTION-level research substrate: a
lagged 17:00 ET cron replays the live bracket over the FULL enriched BULLISH pool daily
(~50 rows/day; reuses production `_simulate_contract`), so edge tests run on CURRENT data and
keep growing (the frozen 1,375-trade study could not — [[option-pnl-not-underlying]]).

Two substrate hardening additions: (1) it persists **`mom_60`** as a point-in-time BQ column
so the momentum lever ([[momentum-60d-enrichment-tilt]]) is replayable; (2) it records the
**opportunity surface** (MFE/MAE excursions) plus a 3-day research-label arm, so the EXIT is
left a free variable rather than baked in — the mechanical embodiment of "surface good
contracts; profit depends on how they're traded" ([[fixed-exit-composites-negative]]). The
3-day arm is a RESEARCH LABEL, never a trade; the live same-day trader is unchanged. This
substrate feeds the webapp Scorecard life-distributions ([[scorecard-life-distributions]]).
