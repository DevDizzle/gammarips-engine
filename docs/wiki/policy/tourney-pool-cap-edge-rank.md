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

`TOURNEY_POOL_CAP` history: introduced at default 12 (2026-06-11). The 2026-06-12 note
recorded a raise to 50 via env, but that raise is NOT true of the live service: **the
live value is the code default 12**, with no deploy.sh override (verified; see
docs/TRADING-STRATEGY.md, and do not "restore" 50). Enrichment already narrows to the
top-50 BULLISH upstream ([[enrichment-cost-fix-topn-thinking-cap]]), then the edge-rank
cap takes the top 12 into the tournament. Research shows a pool cap of 25 loses no
demonstrated winner coverage ([[pool-cap-coverage]]).
