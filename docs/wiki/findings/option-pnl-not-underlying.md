Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: bracket-replay option PnL vs underlying direction on the same enriched pool
Source: docs/DECISIONS/2026-06-17-enriched-option-outcomes.md; INTELLIGENCE_BRIEF 2026-06-17; reference_option_pnl_research_label
Date: 2026-07-17

# Evaluate on OPTION PnL, never underlying direction

On the same enriched pool, **underlying-up 54% vs option-up 41%** — the option instrument
(theta + slippage + non-linear payoff) systematically diverges from the direction call. Any
gate or lever must be evaluated on realized OPTION PnL, not on whether the underlying moved
the right way; the ~74% "directional accuracy" figure is real but does NOT survive the
translation to the option.

This is why the ongoing `enriched_option_outcomes` substrate replays the live bracket over
the full BULLISH pool daily (leakage-safe, ~50 rows/day) — the frozen 1,375-trade study
could not grow, and the live ledger only labels the 1 pick/day. `win-tracker` /
`signal_performance` tracks the full pool but only on UNDERLYING returns, so it is
misleading for edge work. Foundational to [[fixed-exit-composites-negative]] and the
"surface contracts, exit is discretionary" product thesis.
