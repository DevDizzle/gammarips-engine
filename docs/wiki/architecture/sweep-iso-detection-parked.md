Status: active
Type: architecture
Tag: untested-hypothesis
Exit-context: n/a (blocked on a data-vendor upgrade)
Source: INTELLIGENCE_BRIEF 2026-06-02 (H20); docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md
Date: 2026-07-17

# Sweep/ISO detection (H20) — parked, blocked on the Polygon tier

The highest-value future flow-quality lever is distinguishing intermarket sweeps / single-leg
ISOs (conviction) from multi-leg spread/vol trades (to exclude). The Polygon trade condition
taxonomy exists and is exactly what we'd want (`id 219` ISO, `228/230` single-leg ISO,
`232–247` multi-leg), BUT `/v3/trades` returns **403 NOT_AUTHORIZED on our tier** (same
limit as the missing NBBO quotes, [[spread-gate-retired]]).

It needs a Polygon Options-Advanced (trades-feed) upgrade — a spend + vendor decision
requiring owner approval. Deferred until the strategy shows positive EV at N≥15–30: don't buy
richer data to refine signal quality on an unvalidated strategy we can't forward-validate at
this N. Revisit as the top lever once EV is proven.
