Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md
Date: 2026-07-17

# Spread gate is permanently retired — this Polygon plan serves no options quotes

The current Polygon plan serves **NO options NBBO quotes** (the v3 snapshot returns no
`last_quote`; bid/ask are always NULL). The 2026-06-04 bug-fix correctly killed
`polygon_client`'s fake day-low/high spread synthesis, which then made `_best_contract`
hard-reject every ticker on `bid<=0 or ask<=0` → 0 enriched → **0 picks/day from
2026-06-04** (the `overnight_score`/webapp 8/10 surface was unaffected; only contract
selection broke).

Fix: `_best_contract` now prices off **last-trade / day-close** and leaves `spread_pct`
NULL (no synthesis, no fabricated spread); enrichment dropped the `spread IS NOT NULL`
fail-closed. **Spread is permanently retired as a selection gate.** The only path back to a
real spread signal is a Polygon plan upgrade to NBBO quotes — deferred pending an owner cost
decision (parked with the H20 trades-feed upgrade, [[sweep-iso-detection-parked]]).
