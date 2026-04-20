# GammaRips Cheat Sheet — V5.3

## What this system does
Scans overnight unusual options activity → emails you the top 1 trade per day → you execute from your phone at 10 AM → stop + target pre-set → sell at 3:50 PM day-3 if neither hit.

## Your daily routine
| Time | Action |
|---|---|
| 9:00 AM ET | Email arrives (or nothing — skip day) |
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
Enrichment layer applies these gates; only signals passing ALL get ranked:
1. Overnight score >= 1
2. Spread <= 10%
3. Directional UOA > $500k
4. V/OI ratio > 2.0 at focal strike
5. Moneyness 5–15% OTM
6. VIX <= VIX3M (skip entire day if backwardation)

Top 1 by directional UOA $vol sent by email.

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
`overnight-scanner → enrichment-trigger → signal-notifier (email) → forward-paper-trader (ledger)`

## Source of truth
This file + `docs/TRADING-STRATEGY.md` + `docs/DECISIONS/2026-04-17-v5-3-target-80.md` + `docs/GLOSSARY.md`. Everything else in `docs/archive/` is historical.
