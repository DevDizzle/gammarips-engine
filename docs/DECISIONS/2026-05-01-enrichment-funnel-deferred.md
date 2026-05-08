# 2026-05-01 — Enrichment funnel tightening: DEFERRED

## Decision
Do **not** tighten `enrichment-trigger` gates today. Re-evaluate after 30 closed V5.3 trades under the new V/OI-first ranker (shipped same day, see `2026-05-01-ranker-v2-voi-first.md`).

## Why we looked
User goal was to compress the enrichment-stage candidate pool to ~20-30/day for cost-reduction (Gemini grounded search + Polygon technicals run on every enriched row). Initial belief was that the pool was already ~6/day; EDA corrected this.

## Funnel baseline (V5.3 era 2026-04-13 → 2026-04-30, 14 trading days)

| Stage | Per-day mean | p25 | p50 | p75 |
|---|---|---|---|---|
| `overnight_signals` raw | 2,264 | — | 2,161 | — |
| Post enrichment-trigger gates (`overnight_score≥1`, `spread≤10%`, dirUOA>$500K) | **74.6** | 64 | 71 | 84 |
| `overnight_signals_enriched` (1:1 with above) | 74.6 | 64 | 71 | 84 |
| Post signal-notifier filters (V/OI>2, moneyness 5–15%, VIX3M, OI≥20, vol≥100) | **2.3** | 0 | 1 | 3 |

The earlier `~6/day` figure was the *notifier* output, not enrichment. Enrichment is fat at ~75/day.

## Single-knob tightening sweep (N=726, baseline win-rate 25.8% over candidate pool)

| Gate | n/day | winners_lost | win_rate |
|---|---|---|---|
| baseline (current) | 73 | 0 / 187 | 25.8% |
| `overnight_score ≥ 2` | 70 | 5 | 26.1% |
| `overnight_score ≥ 3` | 60 | 29 | 26.2% |
| `spread ≤ 0.07` | 58 | 50 | 23.5% |
| `dirUOA > $1M` | 49 | 58 | 26.2% |
| `dirUOA > $1.5M` | 36 | 97 | 24.9% |
| **`dirUOA > $2M`** | **30** | **108** | **26.3%** |
| `dirUOA > $5M` | 13 | 155 | 24.1% |
| All 4 notifier filters brought forward | 1 | 185 | 18.2% |

**Critical finding:** no single knob raises pool win-rate materially. UOA depth, score, spread, OI, volume — none correlate with winning at the −60/+80 bracket. These are cost-reduction knobs, not edge knobs. Bringing notifier filters forward causes recall collapse (185/187 winners killed) and is explicitly rejected.

## Empirical dry-run under NEW V/OI-first ranker (last 8 trading days)

Tightening to `dirUOA > $2M` would have:

| scan_date | $500K gate | $2M gate | Δ |
|---|---|---|---|
| 2026-04-30 | NBIS | NBIS | same |
| 2026-04-29 | MS | MS | same |
| 2026-04-28 | PH | PH | same |
| 2026-04-27 | TER | TER | same |
| 2026-04-24 | CLSK ($1.0M) | DIS ($2.8M) | **changes** |
| 2026-04-23 | PH | PH | same |
| 2026-04-22 | NEM | NEM | same |
| 2026-04-21 | UBS ($961K) | **NO PICK** | **day killed** |

7/8 same, 1/8 changes, 1/8 kills the pick day entirely. Cost cut of ~60% Gemini calls in exchange for ~1-in-8 pick-day loss.

A `dirUOA > $1M` gate (counter-proposal) would have left **8/8 days identical** to current under the new ranker (UBS at $961K dies but isn't picked anyway under V/OI lead key — wait, it IS picked at $500K and dies at $1M, so 7/8 same, 1/8 killed). Net: $1M is also a recall hit, just a smaller one (~33% Gemini cut, ~1 pick-day loss in 8).

## Why deferred
1. **The new ranker just deployed today.** We don't yet know how V/OI-first behaves in production. Tightening the candidate pool now is acting on a counterfactual, not data. Wait for the ranker to log real picks.
2. **No gate move shows positive edge.** Win-rate moves ±2 points across all tightening knobs — pure noise at N=726. This is purely a cost decision, not a quality decision.
3. **Park-mode + no active trading.** The system is logging picks for the email/WhatsApp pipeline; cost pressure is real but not urgent. Cost of running for 30 more days at current funnel width is bounded and known.
4. **A killed pick-day is a real user-facing cost.** "No email today" because we tightened a cost knob is a worse outcome than "we paid 60% more for Gemini this month."

## Trigger to revisit
Re-open this decision when **either** condition is met:
- **30 closed V5.3 trades** are in `forward_paper_ledger` under the new V/OI-first ranker (currently 32 closed, all under old ranker — so "30 new closed trades after 2026-05-01")
- **Gemini/Polygon enrichment cost** exceeds $X/month (set a threshold the user is willing to tolerate; today's cost is acceptable)

When revisiting, the right question is **"under the new ranker's actual production picks, would tightening the gate have changed the LIMIT-1 winner?"** — measured against real picks, not counterfactual replays. If the new ranker consistently picks high-UOA tickers anyway, the gate change is free; if it sometimes picks low-UOA tickers that win, the gate change costs real edge.

## Alternatives explicitly rejected today
- **Ship `dirUOA > $2M`** — kills 1-in-8 pick days; insufficient justification at park-mode.
- **Ship `dirUOA > $1M`** — kills ~1-in-8 pick days; smaller cost cut for the same recall hit profile.
- **Bring notifier filters forward into enrichment** — collapses recall (185/187 winners lost), worsens pool win-rate.
- **Tighten on `overnight_score`** — buys little (60-70/day at score≥3), loses 29 winners for marginal cost cut.

## What we're shipping today instead
- The V/OI-first ranker change in `signal-notifier/main.py` (separate DECISIONS note).
- This funnel analysis as documentation only — no code change.
- Cron `agent-arena-trigger` paused (separate retro).

## Files referenced
- `/home/user/gammarips-engine/enrichment-trigger/main.py` (lines 213-220 — the gate that would change if we revisit)
- `/home/user/gammarips-engine/signal-notifier/main.py` (lines 53-57, 480-516 — downstream filters and new ranker)

## Re-evaluation checklist (when revisiting)
1. Pull `forward_paper_ledger` rows where `entry_date >= 2026-05-01` (post new-ranker era).
2. For each ledger row, look up the enriched candidates that day and check: would `dirUOA > $1M` (or `$2M`) have killed the actual picked ticker?
3. If kill-rate < 5% and avg_pnl_pct of killed picks ≤ baseline, ship the gate. If kill-rate > 5% OR killed picks have above-baseline win rate, keep the gate as-is.
4. If revisiting, gate change does not require `gammarips-review` (signal-quality, not execution policy), but does require a follow-up DECISIONS note.
