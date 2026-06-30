# GammaRips Cheat Sheet — V7.1 "Tilted GIGO"

## What this system does
Scans overnight unusual options activity → a randomized bracket **tournament** over the enriched BULLISH pool picks one trade per day → emails you the pick (clickable card linking to `gammarips.com/signals/{ticker}` for rationale) → you execute from your phone at 10 AM using the **published limit price** → stop + target pre-set → **flat by 3:45 PM the SAME day** (no overnight, no trail). Public live-stats panel (`cohort_stats/current`) reflects the live cohort (`policy_version='V7_1_TILTED_GIGO'`, reset to 2026-06-26 for the live-OI-floor regime).

## Your daily routine
| Time | Action |
|---|---|
| ~9:50 AM ET | Email arrives (or nothing — skip day). Webapp + WhatsApp push fire at the same moment, just before the open settles. |
| 10:00 AM ET | Buy 1 contract with a **LIMIT** at the published Entry/Limit price — **do NOT market-buy, do NOT chase above the "don't chase" cap.** Then set the −30% stop AND +40% target. |
| 10:00 AM – 3:45 PM (same day) | Phone in pocket. Both exit orders armed. |
| Any time either fills | Cancel the other order (Robinhood doesn't auto-OCO options). |
| 3:45 PM ET (same day) | If neither hit, close the position (flat). Done — nothing held overnight. |

## The strategy
- Entry: 10:00 AM, via a **limit** at the published ~9:50 ET mark (a small buffer makes it marketable) — never market, never chase past the cap
- Size: $500/trade ($2k bankroll, max 1 position at a time)
- Stop: −30% option premium
- Target: +40% option premium
- Exit: flat by 3:45 PM the SAME day — no overnight hold, no trailing stop
- Why same-day ("GIGO"): ~3× return-per-capital-day vs the old 3-day hold and ~half the disaster tail; per-trade EV ~tied (velocity + tail is the case)

## The entry price (new 2026-06-30)
The email / webapp / WhatsApp now show a **fresh ~9:50 ET mark** (not the stale overnight price), a **Limit BUY** price, a **"don't chase above"** cap, and the −30% / +40% dollar levels. Rest your limit there; if the contract runs past the cap before you fill, **skip it** — don't buy the top. (Reference levels are computed off the 9:50 mark; your actual fill sets your real bracket.)

## The signal filter (what reaches your inbox)
V7.1 has **no execution-side gates** — selection is the tournament. Upstream, only the enrichment bar + a hard direction gate + a liquidity floor + two safety rails apply:
1. Overnight score ≥ 4 (enrichment floor; EV inverts at ≥ 7)
2. Directional UOA > $500K (enrichment)
3. **BULLISH-only** (hard gate — the edge levers are call-delta-defined)
4. **Live OI ≥ 1000** at the 09:45 pick (liquidity floor, 2026-06-25 — picks on FRESH open interest, not stale scan-time OI)
5. **No earnings during the hold** — exclude any ticker reporting in the hold window. Literature-anchored hard rule (De Silva et al. 2026 *Review of Finance*). Fail-closed if the earnings calendar is unreachable.
6. **VIX ≤ VIX3M** — skip the whole day if backwardation.

Spread is **permanently retired** as a gate — this Polygon plan serves no options quotes. The old moneyness / OI / volume / DTE / V-OI selection gates were removed 2026-06-04; the enrichment edge-rank also applies a 60-day-momentum tilt and caps the pool before the tournament.

## The pick (V7.1 Tournament)
The enriched BULLISH slate goes to **signal-judge** (`tournament_v1`, `gemini-3.1-pro-preview`). It runs **3 independent randomized brackets**, each: shuffle signals into batches of ≤10 → the LLM picks the top 2 per batch → advance and repeat. Each batch call gets a simple prompt + the daily report + per-contract JSON; **no memory, no rubrics, no weights**. The 3 bracket winners vote: 3/3 agree → `confidence=high`, 2/3 → `medium`, 1/3 → `low`. One ticker emailed. **Fail-closed on any error** — no fallback; signal-judge uptime is the SLO.

## Math
- Velocity backtest: same-day GIGO ~tied per-trade with the old 3-day hold but ~3× return-per-capital-day and ~half the disaster tail
- Max per-trade loss = $150 (30% of $500)
- Max per-trade win = $200 (40% of $500)
- 5-trade losing streak = −$750 — size accordingly

## When things go sideways
- No email → do nothing
- Missed the 10:00 entry → skip, don't chase
- Contract ran past the "don't chase" cap before you filled → skip it; there's always tomorrow
- One order filled → cancel the other (no auto-OCO); a stray armed order can hit your next trade. Check open orders every morning.

## When to revisit
- After the cohort reaches a real sample (N ≥ 15)
- If EV > 0 → increase size (capped per-position)
- If EV < 0 → pause, re-run the research angle

## Services (reference only)
`overnight-scanner (23:00 ET) → enrichment-trigger (05:30 ET) → overnight-report-generator → signal-notifier (09:45 ET) ← signal-judge (V7.1 tournament_v1) → email + Firestore todays_pick → forward-paper-trader (ledger)`

## Source of truth
This file + `docs/TRADING-STRATEGY.md` + `docs/GLOSSARY.md`. Everything else in `docs/archive/` is historical.
