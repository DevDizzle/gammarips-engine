Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md
Date: 2026-07-17

# 2026-06-04 pipeline bug-hunt — 13 silent data bugs fixed

An adversarial bug-hunt on 2026-06-04 fixed **13 silent data bugs** in the pick pipeline.
The bugs "built and ran" but corrupted pick inputs for months. The headline fixes:
- **Root cause: fake spreads.** `polygon_client` substituted day low/high for missing
  bid/ask → fabricated / 0% spreads on ~43% of picks. Now NULL when unquoted, real spread
  otherwise (this is also why the spread gate is retired, [[spread-gate-retired]]).
- **Divergence-flip scoring reordered before conviction signals** — the old order was
  suppressing ~87% of the best setups.
- **Technicals lookahead closed** — the indicator window is bounded to `scan_date`
  (leakage fix, [[assert-no-leakage-gate]]).
- **Stale volume/OI fields stripped from the judge prompt**
  ([[oi-volume-session-frozen-walled-off]]).
- **Contract selection made liquidity-aware** (OI-primary, real spread, no-quote strikes
  dropped) and **trader fill-realism** improvements.

Durable lesson (owner doctrine): eval the DATA/code, not just the LLM text — distrust
field values the way you'd distrust model output. This is the canonical example of silent
code/data bugs corrupting picks while everything "worked."
