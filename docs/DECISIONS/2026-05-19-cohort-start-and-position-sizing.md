# 2026-05-19 — Cohort start date + fixed-dollar position sizing for public stats

## Decision

Two small but visible changes to the public `cohort_stats/current` Firestore doc that the webapp reads:

1. **`LIVE_COHORT_START_DATE` 2026-05-08 → 2026-05-13.** The displayed "Cohort since…" date is now anchored to the first executed V5.4 trade (OKTA scan 2026-05-12 → entry 2026-05-13), not the policy promotion date.
2. **Public ROI now uses fixed-dollar position sizing at `POSITION_SIZE_USD = 500.0`** per trade, computed in-SQL inside `compute_and_write_cohort_stats`. The ledger continues to record per-contract premium and percent return — sizing is applied at the display layer only.

Both constants live in `signal-notifier/main.py`. No schema change to `forward_paper_ledger`. No trader code change.

## Why — cohort start

The promotion-date framing (5/8) over-states the cohort age and creates the impression that fewer trades have fired than expected. The actual timeline:

- 2026-05-08 — V5.4 promoted, V5.3 retired, ledger truncated 246 rows
- 2026-05-08 → 2026-05-11 — V5.4 ranker ran, V5.3-era trader simulated. Picks for VAL (entry 5/11) and GE (entry 5/12) were NOT written to the new ledger because the V5.4-only trader code didn't land until 2026-05-15.
- 2026-05-13 — first row in `forward_paper_ledger` (OKTA, scan 5/12)

Anchoring "Cohort since…" to 5/13 makes the displayed cohort age match the trade record. Users seeing "Cohort since May 8, 2026" + "1 trade" naturally wondered "where did the other 8 days go?" — there were no trades to count.

## Why — fixed-dollar sizing

The old aggregator implicitly assumed **1 contract per trade**, computing `SUM(entry_price * 100)` for invested capital. With our two existing trades:

| Trade | Premium | 1-contract invested | Result | 1-contract P&L |
|---|---:|---:|---:|---:|
| OKTA | $4.67 | $467 | −1.96% (TIMEOUT) | −$9.16 |
| HTZ | $0.40 | $40 | +80.0% (TARGET) | +$31.82 |

Dollar-weighted ROI = $22.66 / $506.94 = **+4.5%**. The HTZ win — a textbook +80% TARGET hit — barely moves the dial because its 1-contract position was a fraction of OKTA's premium cost.

Under fixed-dollar sizing at $500/trade:

| Trade | n_contracts | Invested | P&L |
|---|---:|---:|---:|
| OKTA | round(500/467) = 1 | $467 | −$9.16 |
| HTZ | round(500/40) = 13 | $517 | +$413.60 |
| **Total** | | **$984** | **+$404.44** |
| **ROI** | | | **+41.1%** |

This is a defensible public number: it reflects the strategy's per-trade edge under normalized risk, not the accident of premium price differences.

Equal-risk sizing (e.g., max-loss $300 per trade) reduces to fixed-dollar sizing under our fixed-percent stop (−60%): max_loss = invested × 0.6, so $300 max-loss ↔ $500 invested. The two methodologies are algebraically equivalent for this strategy. Picking fixed-dollar because it's the simpler explanation.

## Why $500 specifically

- Produces sensible n_contracts across our premium range: $0.40 premium → 13 contracts, $4.67 premium → 1 contract, $10 premium → 1 contract (the GREATEST(1, …) floor)
- $500 × max −60% stop = $300 max loss per trade — reasonable for a retail-sized paper-trading sim
- Round number that's easy to communicate publicly ("$500 per trade")
- If later we want to model larger account sizes, scale POSITION_SIZE_USD linearly — total P&L scales 1:1, ROI is invariant

## What the ledger looks like vs what the display shows

The ledger (`forward_paper_ledger`) is unchanged. It still records:
- `entry_price` — per-contract premium at entry
- `realized_return_pct` — percent change in premium at exit
- All other per-contract metadata

The display layer (`compute_and_write_cohort_stats`) computes n_contracts on the fly via:
```sql
GREATEST(1, CAST(ROUND(500.0 / (entry_price * 100)) AS INT64)) AS n_contracts
```
and aggregates `n_contracts * entry_price * 100` for invested and `n_contracts * entry_price * 100 * realized_return_pct` for P&L.

This means if we ever revisit sizing methodology, it's a one-place change. No backfill, no migration, no trader redeploy.

## Cohort_stats Firestore doc now includes `position_size_usd`

So any downstream reader (webapp, MCP, x-poster, GTM) can render "ROI under $500/trade sizing" instead of having to guess the basis.

## What this does NOT change

- The trader still simulates 1 contract per trade for the BQ ledger. The "actual" trade record is unchanged — n_contracts is purely a presentation-layer construct.
- The win rate, trade count, and per-trade returns are unchanged.
- The signal-notifier gate stack is unchanged.

## Definition of done

- Two-line edit to `signal-notifier/main.py` (constants + SQL)
- Redeploy via `bash deploy.sh`
- POST `/refresh_stats` to force immediate recompute
- Verify webapp panel shows "Cohort since May 13, 2026" with updated ROI

## References

- Affected file: `signal-notifier/main.py` (lines 73-95, 982-1015)
- Source of confusion (user, 2026-05-19): cohort_stats panel showed "Cohort since May 8" + "1 trade / −2% ROI" after HTZ +80% had already closed; user asked why ROI was so muted given the recent win
- Related decisions: [2026-05-08 V5.3→V5.4 promotion](2026-05-08-v5-3-retired-v5-4-promoted.md), [2026-05-15 trader resurrection](2026-05-15-trader-resurrection-and-mtm.md), [2026-05-12 V5.4-only ledger](2026-05-12-v5-4-pipeline-alignment.md)
