Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (methodology rule)
Source: INTELLIGENCE_BRIEF hard constraints (codified 2026-05-06); docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md
Date: 2026-07-17

# Selection filters vs exclusion filters carry different evidentiary bars

Two filter classes have different evidentiary bars — do not conflate them:
- **Selection filters** rank/pick winners FROM our cohort (a new top-of-rank composite, an
  "earnings-momentum" feature). These need labeled screen + bootstrap CI + walk-forward +
  forward OOS in the live ledger. High overfitting risk (Novy-Marx 2015). Default
  substrate: our cohort, with strict multiple-comparison discipline.
- **Exclusion filters** kick out known-broken parameter regions (earnings overlap, VIX
  backwardation, deep-OTM moneyness). These are theory-driven and literature-anchored.
  Default substrate: peer-reviewed evidence. **Deploy on mechanism, not on our backtest** —
  do NOT backtest exclusion filters on `signals_labeled_v1` to "validate" them (the
  literature has decades and millions of trades; we have 1,563 regime-confounded rows).

Canonical examples: the earnings-overlap rule ([[earnings-exclusion-rail]]) and the V5.3
literature audit ([[literature-audit-v5-3-stack]]) are exclusion-style; the momentum tilt
([[momentum-60d-enrichment-tilt]]) is selection-style and carries the full OOS bar.
