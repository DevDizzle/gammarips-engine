# GammaRips Cheat Sheet — V6 "Tournament"

## What this system does
Scans overnight unusual options activity → a randomized bracket **tournament** over ALL enriched signals picks one trade per day → emails you the pick (with a clickable card linking to `gammarips.com/signals/{ticker}` for rationale) → you execute from your phone at 10 AM → stop + target pre-set → sell at 3:50 PM day-3 if neither hit. Public live-stats panel (`cohort_stats/current` Firestore doc) reflects the V6 cohort starting 2026-06-04 (forward_paper_ledger truncated when V5.4 was retired; `policy_version='V6_TOURNAMENT'`).

## Your daily routine
| Time | Action |
|---|---|
| 7:30 AM ET | Email arrives (or nothing — skip day). Webapp + WhatsApp push fire at the same moment. |
| 10:00 AM ET day 1 | Buy 1 contract at market. Set −60% GTC stop-limit AND +80% GTC limit sell on Robinhood |
| 10:00 AM day 1 – 3:50 PM day 3 | Phone in pocket. Both exit orders armed. |
| Any time either fills | Cancel the other order (Robinhood doesn't auto-OCO options) |
| 3:50 PM ET day 3 | If still open, cancel both pending orders, market sell. Done. |

## The strategy
- Entry: 10:00 AM day 1
- Size: $500/trade ($2k bankroll, max 1 position at a time)
- Stop: −60% option premium (GTC stop-limit)
- Target: +80% option premium (GTC limit sell)
- Timeout: 3:50 PM on day 3 (3 full trading days held)
- Fill realism (2026-06-04): symmetric slippage on entry/exit + stale-TIMEOUT and late-fill guards in the simulator

## The signal filter (what reaches your inbox)
V6 has **no selection gates** — every enriched signal enters the tournament. Only the enrichment bar plus two safety rails apply:
1. Overnight score >= 1 (enrichment)
2. Spread <= 30% (enrichment)
3. Directional UOA > $500k (enrichment)
4. **No earnings in the hold window** — exclude any ticker reporting in `[scan_date, entry_day+2 trading days]`. Literature-anchored hard rule (De Silva et al. 2026 *Review of Finance*: retail loses 5–9% per event). Fail-closed if the earnings calendar is unreachable.
5. **VIX <= VIX3M** — skip the entire day if backwardation.

The old moneyness / OI / volume / DTE / V-OI selection gates were **REMOVED 2026-06-04** — the tournament now ranks the full enriched slate directly.

## The pick (V6 Tournament)
The full enriched slate (~94 signals on a typical day) goes to **signal-judge** (`tournament_v1`, `gemini-3.1-pro-preview`). It runs **3 independent randomized brackets**, each: shuffle signals into batches of ≤10 → the LLM picks the top 2 per batch → advance and repeat (~94 → 20 → 4 → 1). Each batch call gets a simple prompt + the daily report + per-contract JSON; **no memory, no rubrics, no weights**. The 3 bracket winners vote: 3/3 agree → `confidence=high`, 2/3 → `medium`, 1/3 → `low`. One ticker emailed. **Fail-closed on any error** — no fallback; signal-judge uptime is the SLO.

## Math
- Deep Research modeled EV +1.8% to +3.2% per trade post-upgrade
- At $500/trade × 10 trades/month × +2% EV = +$100/month compounding
- Max per-trade loss = $300 (60% of $500)
- Max per-trade win = $400 (80% of $500)
- 5-trade losing streak = −$1,500 (75% drawdown) — size accordingly

## When things go sideways
- No email → do nothing
- Missed the 10:00 entry → skip, don't chase
- Missed 3:50 exit on day 3 → GTC stop and target still armed; close next morning open
- Forgot to cancel the other order after one filled → risk of stray fill on your next trade. Check open orders every morning.

## When to revisit
- After 4 weeks of real data
- If EV > 0 → increase size
- If EV < 0 → pause, rerun Deep Research angle

## Services (reference only)
`overnight-scanner (23:00 ET) → enrichment-trigger (05:30 ET) → overnight-report-generator → signal-notifier (07:30 ET) ← signal-judge (V6 tournament_v1) → email + Firestore todays_pick → forward-paper-trader (ledger)`

## Source of truth
This file + `docs/TRADING-STRATEGY.md` + `docs/GLOSSARY.md`. Everything else in `docs/archive/` is historical.
