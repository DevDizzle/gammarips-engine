# 2026-10-15: Chooser open-interest saturation point, 3,000 to 10,000

**Status:** BUILT 2026-10-15 (owner call: "OK make your change"). NOT deployed. Deploy
after the 2026-10-16 morning read of the first dollar-volume scan, one change at a time.
Deploy command in `~/workspace/DEPLOY-SCANNER-DV.txt`.

## Decision

The open-interest term of the contract chooser (`_best_contract` in
`src/enrichment/core/pipelines/overnight_scanner.py`) is a log ramp that stops rising at a
saturation point. The point is now the env knob `CONTRACT_OI_SATURATION`. The code default
is 3,000 (the 2026-07-28 value, unchanged behaviour). `overnight-scanner/deploy.sh` pins
10,000. Rollback: `CONTRACT_OI_SATURATION=3000` and redeploy.

Nothing else in the chooser changes: the filters, rule set B, the delta band bonus, the
volume, gamma and theta terms, and the 7 to 45 DTE window stay as they are.

## Why

The chooser is a fillability scorer. On the liquid universe its two liquidity terms no
longer separate strikes: 80% of the picks on $150+ names sit above OI 3,000 and 97% above
volume 200, and the spread term is NULL on this Polygon plan. So the strike inside the
delta band falls to the small gamma and theta residual.

The trader's 10:00 Robinhood book says open interest above 3,000 still matters. Rule set B
rows with a book, entry days 2026-09-15 to 2026-10-15, joined to the pool on scan_date
and contract (N=524):

| Scan OI | N | Spread at or below 10% of mark | Ask x 100 at or below $568 | Both |
|---|---|---|---|---|
| 500 to 1k | 11 | 36% | 27% | 9% |
| 1k to 3k | 86 | 72% | 48% | 28% |
| 3k to 10k | 337 | 88% | 58% | 48% |
| 10k and above | 90 | 98% | 60% | 58% |

A saturation point of 10,000 lets the chooser prefer the deepest strike in the band when
one exists. The band bonus still dominates: the most the OI term can add between 3,000 and
10,000 is 0.65 points against the 2.0-point delta band bonus, so an out-of-band strike
cannot win on OI alone.

This is a contract-quality change. It is not a return claim. Contract shape as a return
lever is tested and dead: `contract_score` AUC 0.46 (2026-08-19), delta equals the chance
of finishing in the money (2026-07-06), short DTE is symmetric leverage (2026-07-28), and
the trader's F-060 (2026-10-15) found that the best-expected kind of contract by DTE and IV
does not beat random.

## Dry run (read-only, live chains 2026-10-15 16:03 ET, right after the close)

`scripts/tests_and_diagnostics/dry_run_oi_saturation.py` re-ran the scanner's own chooser
with rule set B fixed on the 2026-10-14 liquid top 100 plus the 28 names the dollar-volume
universe adds. 91 names had an eligible call.

| Saturation | Picks changed | New expiry | Median OI | OI 10k+ | Median mid | Mid x 100 at or below $568 | Median delta | DTE 13 or less |
|---|---|---|---|---|---|---|---|---|
| 3,000 (before) | 0 | 0 | 3,898 | 9% | $4.50 | 56 of 91 | 0.39 | 10% |
| 10,000 (pinned) | 26 | 8 | 5,379 | 26% | $4.15 | 57 of 91 | 0.35 | 4% |
| 20,000 | 29 | 11 | 5,379 | 27% | $4.50 | 55 of 91 | 0.35 | 1% |

What the moves look like: NVDA 220C 8 DTE OI 2,990 to 230C 36 DTE OI 63,859. TSLA 375C mid
$15.82 OI 3,898 to 400C mid $8.07 OI 14,524. AAPL 345C 8 DTE mid $3.60 to 350C 36 DTE mid
$7.85 OI 24,480. The deeper strike is the round-number strike, often one step further out of
the money. The affordable count is flat: five picks become dearer (AAPL, AMZN, NVDA, PLTR,
SPCX move from an 8-DTE weekly to the monthly) and five become cheaper (AVGO, CRWV, HOOD,
MSTR, VST).

Risk shape, stated once: the median delta moves from 0.39 to 0.35 and several picks land
at 0.22 to 0.28. That is inside the chooser's 0.20 to 0.46 band, whose 0.20 floor is
unvalidated (2026-07-28). A lower delta is more leverage in both directions, not an edge.
The trader reads live delta as a sanity check, not a gate.

10,000 is pinned because the measured pass rate flattens there (98%). 20,000 moves three
more picks for no measured gain.

## Cost

None. The chooser already has the chain. No extra API calls.

## What this does not change

- The universe, its rank, rule set B, enrichment, the MCP, the trader.
- No public copy states the chooser's weights, so no site or MCP text changes.
- Selection research stays CLOSED. No DTE or contract-shape outcome study follows from this.

## Measurement

- BigQuery, scan dates after the deploy: the share of pool rows with `recommended_oi` at or
  above 10,000 (dry run says about 25%, the liquid era before was 9% to 17% by price band).
- Trader funnel log from the next entry day: the 10% spread screen pass rate on rule set B
  rows, split by scan OI bucket. The rate at 3k to 10k is the control (88%).

Related: `docs/DECISIONS/2026-06-04-contract-selection-liquidity.md` (the chooser),
`docs/DECISIONS/2026-10-15-contract-premium-floor.md` (rule set B),
`docs/DECISIONS/2026-10-15-dollar-volume-universe-rank.md` (the universe).
