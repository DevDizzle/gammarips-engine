Status: active
Type: policy
Tag: policy-adopted
Exit-context: the soft pre-rank levers come from the 1,375-trade 3-day-bracket study
Source: docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md; docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md
Date: 2026-07-17

# Tournament pool is soft-edge-ranked, then capped to TOURNEY_POOL_CAP

Among the BULLISH names, the pool is **deterministically edge-ranked and capped** to the
top `TOURNEY_POOL_CAP` before the tournament (cost control — the full ~94-pool tournament
was ~39 model calls/pick; a cap of 12 → ~9 calls, 10 → ~3).

The rank is a **SOFT pre-rank** (not a gate) by the 1,375-trade study's levers: mid-|delta|
0.20–0.46, RR < 1.4, ATR-normalized move — all point-in-time / leakage-safe. The FALLBACK
path inherits the [[bullish-only-hard-gate]] but SKIPS the edge-cap.

`TOURNEY_POOL_CAP` history: introduced at default 12 (2026-06-11), then **raised to 50
(env) on 2026-06-12** so that all ~50 grounded-enriched names seed the tournament — the
current effective value is 50 (the cap now rarely binds; enrichment already narrows to
top-50 upstream, see [[enrichment-cost-fix-topn-thinking-cap]]). Research shows the cap can
shrink 50→25 with no demonstrated loss of the eventual winner ([[pool-cap-coverage]]).
