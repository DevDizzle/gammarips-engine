# GammaRips Cheat Sheet — V5.4

## What this system does
Scans overnight unusual options activity → an LLM agent ranker (Scorer + Picker) chooses one trade per day with a written justification → emails you the pick (with a clickable card linking to `gammarips.com/signals/{ticker}` for rationale) → you execute from your phone at 10 AM → stop + target pre-set → sell at 3:50 PM day-3 if neither hit. Public live-stats panel (`cohort_stats/current` Firestore doc) reflects the V5.4 cohort starting 2026-05-08 (forward_paper_ledger truncated when V5.3 was retired).

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

## The signal filter (what reaches your inbox)
Hard gates run UPSTREAM of the agent ranker. Only signals passing ALL get into the candidate pool:
1. Overnight score >= 1
2. Spread <= 8% (tightened from 10% on 2026-05-06 per lit-audit H11)
3. Directional UOA > $500k
4. V/OI ratio > 2.0 at focal strike
5. Moneyness 5–10% OTM (tightened from 15% on 2026-05-06 per lit-audit H12)
6. VIX <= VIX3M (skip entire day if backwardation)
7. Recommended contract OI >= 10 (relaxed from 20 on 2026-05-12 to lift picker-starvation floor)
8. Recommended contract volume >= 50 (relaxed from 100 on 2026-05-12, same reason)
9. DTE 7-45 (added 2026-05-11 at 7-30, widened to 7-45 on 2026-05-12 — picker rubrics penalize >45 DTE)
10. **No earnings near hold window** — exclude any ticker reporting in `[scan_date, entry_day+2 trading days]`. Window includes scan_date to catch AMC prints that contaminate the V/OI signal pre-entry. Literature-anchored hard rule (De Silva et al. 2026 *Review of Finance*: retail loses 5–9% per event). Fail-closed if FMP earnings calendar is unreachable OR returns a non-list payload (quota-exhausted).

Top 10 gate-clean candidates fed to the V5.4 agent ranker. Scorer (`gemini-3.5-flash`, scorer_v5) grades each on three rubrics (1-10): `flow_conviction` (60% weight), `regime_alignment` (25%, must cite the daily report), `narrative_coherence` (15%). HEDGING-tagged flow is hard-capped at flow_conviction ≤4. Top-5 by composite go to the Picker (`gemini-3.1-pro-preview`, picker_v4) — single high-stakes call that returns one ticker + runner-up + justification + confidence enum (`high`/`medium`/`low`). Picker reads top-5 candidate enriched data + Scorer reasoning prose (no raw rubric scores) + the daily report markdown + 14d ledger summary. **No abstain.** **Fail-closed on any error** — no fallback ranker; signal-ranker uptime is the SLO.

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
`overnight-scanner → enrichment-trigger → signal-notifier ← signal-ranker (V5.4 picker) → email + Firestore todays_pick → forward-paper-trader (ledger)`

## Source of truth
This file + `docs/TRADING-STRATEGY.md` + `docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md` + `docs/GLOSSARY.md`. Everything else in `docs/archive/` is historical.
