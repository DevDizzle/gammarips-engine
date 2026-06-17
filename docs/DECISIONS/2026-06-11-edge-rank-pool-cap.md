# 2026-06-11 — Edge-rank pool cap: deterministically narrow the tournament pool

**Status:** IMPLEMENTED, pending `gammarips-review` (leakage + regime-bet check) + deploy. Owner-directed (cost-forced). The G-Stack ceremony is waived by the owner; only the leakage audit is non-negotiable.

## Problem
The 2026-06-04 tournament runs over the **full** enriched pool (~94 signals/day). That is **~39 `gemini-3.1-pro-preview` calls/pick** (3 brackets × ~13). At ~$0.85/pick it is not affordable to keep running, and the cost scales with pool size, not model tier — a Flash swap does ~nothing (Pro is only ~25% more sticker at our <200k context, and Flash's thinking-token inflation can erase even that).

## Decision
Two-part change before the tournament:

1. **HARD gate — BULLISH only** (`BULLISH_ONLY=true`, owner-directed). Bearish signals are removed from the candidate query on **both** the strict and fallback paths, so no bearish name reaches email by any route. Env-toggleable.
2. **SOFT edge-rank cap** among the surviving (bullish) pool: rank by the four levers the 1,375-trade realized-option-PnL study proved separate winners from losers, and feed only the top `TOURNEY_POOL_CAP` (default 12) into the tournament. Among bullish names, nothing is categorically dropped by structure — a high-RR or deep-delta bullish name can still rank into the top-K; the score only orders the pool. The tournament still makes the actual pick.

### The edge score (`signal-notifier/main.py:_edge_score`)
All inputs are already SELECTed into the pool df and are **point-in-time at `scan_date`** (leakage-safe — unlike the stale-OI gates retired 2026-06-04):

| Lever | Field | Winning side | Losing side | Weight |
|---|---|---|---|---|
| Direction | `direction` | BULLISH +4.1% | BEARISH −7.7% | hard gate (see above); +2.0 term retained for the toggle-off case |
| Delta (trap-escape, confirmed Q19) | `recommended_delta` | \|δ\| 0.20–0.46 → +6.6% | deep ITM 0.46+ → +0.1% | +1.5 if in band |
| Advertised RR | `risk_reward_ratio` | RR < 1.4 → +2–3% | RR > 1.4 (far-OTM lottery) → −7.7% | +1.0 if < 1.4 |
| Move size | `atr_normalized_move` | already-moved-hard → +4.1% | quiet → −3.3% | +0.5·min(move, 2.5) |

Ties broken by `overnight_score` desc. `_edge_rank_and_cap(df, k)` is a no-op when the pool already fits within `k`.

### Cost impact
| Cap | Bracket shape | Calls/pick | Cut |
|---|---|---|---|
| 94 (today) | 13/bracket | ~39 | — |
| **12 (default)** | 12→4→1 = **3/bracket** | **~9** | **~77%** |
| 10 | single batch = 1/bracket | ~3 | ~92% |

`TOURNEY_POOL_CAP` is an env var — dial cost without a code redeploy. At 12 the bracket still does real cross-batch work and the consensus-confidence signal stays meaningful; at 10 it collapses to a single batch (near-deterministic consensus).

## Why BULLISH-only (owner override of the regime caveat)
The regime caution was raised and **explicitly overruled by the owner** on 2026-06-11. The decision is **not** a regime bet — it is scoping to the trade family the edge actually describes:

- The delta lever (\|δ\| 0.20–0.46) and the advertised-RR lever are defined on **call** structure. Bearish puts carry the opposite delta sign and a different contract geometry, so the study's bands do not transfer to them.
- Restricting to bullish keeps the pipeline inside the region where the deterministic edge is measured and meaningful, rather than ranking puts on a score that wasn't fit for them.

This **supersedes**, for now, the prior "don't frame bearish trades as broken / bearish −7.7% is regime-conditional" guidance ([[project_direction_ev_asymmetry]], [[feedback_regime_and_direction]]). It is reversible: flip `BULLISH_ONLY=false` to re-admit bearish (the soft edge-rank's +2.0 BULLISH term then resumes tilting, not banning).

## Distinction from the gates retired 2026-06-04
Those were **stale-liquidity** gates (scan-time OI/vol — a one-day-stale snapshot that dies before our 10:00 entry). This is a **structural-edge pre-rank** on stable, point-in-time features (direction label, contract greeks, advertised RR, ATR-normalized move). It does not re-introduce the failure mode that killed the old gates.

## What is unchanged
- **FALLBACK path** bypasses the tournament (`df.iloc[0]`) and is **untouched by the edge-rank cap**, but the **BULLISH-only hard gate DOES apply to it** (it lives in the shared candidate query), so fallback picks are bullish too.
- The two SAFETY rails (no earnings in hold; regime fail-closed) and `assert_no_leakage` still run before the cap.
- The tournament mechanics, prompt, quant.md final-round priors, and persistence are unchanged.
- The judge's prompt **already sees** `recommended_delta` and `atr_normalized_move`: `_candidate_for_ranker` serializes every non-null row field into the `/rank` payload, and `Candidate` is `model_config={"extra":"allow"}` (`signal-judge/app/schemas.py:45`), so `model_dump(exclude_none=True)` in the prompt builder emits them (neither is in `STALE_FIELDS_BLOCKLIST`). The edge-rank cap therefore reinforces, deterministically and pre-LLM, the same features the judge can already weigh — no schema change needed.

## Revisit
Watch the live ledger: if the capped cohort underperforms the historical full-pool cohort at N≥15 closes, loosen `TOURNEY_POOL_CAP` or revisit the weights. The cap and every weight are reversible via env / one-line edits.
