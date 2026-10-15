# 2026-10-15: Contract premium floor, delta cap and OI floor on the overnight scanner

**Status:** SHIPPED 2026-10-15 (owner call: "ship B"). First real scan 2026-10-15 23:00 ET.

## Decision

The scanner's contract chooser (`_best_contract` in
`src/enrichment/core/pipelines/overnight_scanner.py`) now rejects a contract when:

| Rule | Env var | Value |
|---|---|---|
| Mid price below the floor | `CONTRACT_MIN_MID` | 1.50 |
| Delta above the cap, or delta missing | `CONTRACT_MAX_DELTA` | 0.50 |
| Open interest below the floor | `CONTRACT_MIN_OI` | 500 |

A name with no eligible call leaves the pool for that night. The values are pinned
in `overnight-scanner/deploy.sh`. Rollback: set the three values to 0 and redeploy.

## Evidence

Measured on the trader's funnel log (`gammarips-trader/eval/funnel-log.jsonl`),
entry days 2026-09-15 to 2026-10-13, N=977 pool rows:

- 33% of pool rows (323) were rejected at the trader's liquidity screen: 272 on a
  spread above 10% of mark (Robinhood book), 49 on a carried 10:00 mark.
- The drop rate is monotone in the scan mid price: below $0.50 69%, $0.50 to $0.99
  52%, $1.00 to $1.49 38%, $1.50 to $2.49 32%, $2.50 to $3.99 21%, $4 to $7.99 17%,
  $8 and above 8%. The same gradient holds by delta (below 0.30: 63%) and by OI
  (below 2k: 61%).
- 40% of pool rows had a mid below $1.50. The engine's `recommended_spread_pct` is
  NULL on every row (no NBBO on this Polygon plan), so the chooser's spread term was
  dead and price is the only point-in-time proxy for the spread.

Dry run (`scripts/tests_and_diagnostics/dry_run_contract_floor.py`, read-only, live
chains at 10:04 ET on 2026-10-15, partial session volume):

| Rule set | Names | Dropped | Mid below $1.50 | OI below 500 | Trader rejection (est.) |
|---|---|---|---|---|---|
| A, as before | 61 | 0 | 41% | 3 | 33% |
| B, shipped (1.50 / 0.50 / 500) | 42 | 19 | 0% | 0 | 17% |
| C (1.00 / 0.50 / 500) | 48 | 13 | 27% | 0 | 20% |
| D (1.50 / 0.50 / 1000) | 41 | 20 | 0% | 0 | 16% |

The delta cap exists because a price floor alone walked PFE, T and VZ onto 0.67 to
0.77 delta in-the-money calls. A missing delta is excluded because PFE 27C with no
greeks passed the cap. The OI floor exists because re-picks landed on OI 15 (WULF),
145 (FSLY) and 130 (XP).

## What this does not change

- The 100-name liquid universe and its rank (2026-08-24 definition) stay the same.
- This is a contract-quality change, not a name change. The trader's drift test
  (F-059, `gammarips-trader/scripts/pool_drift_test.sql`) found zero stock drift in
  the pool. B cuts contracts the broker book rejects. It does not add a return edge.
- No public copy states the contract price shape, so no site or MCP text changes.

Trader-side check, same day (trader session, 10 entry days 10-01 to 10-15, 414 rows with a
10:00 book, mid and delta only because OI is not in the funnel log): rows that pass the B
floor passed the trader's 10% spread screen 81% of the time (204 of 253), the rest 35% (56
of 159). B plus the spread pass plus one contract at or below the trader's $568 per-trade
budget left 5 to 16 contracts a day on the old names. The dollar-volume universe
(`2026-10-15-dollar-volume-universe-rank.md`) prices higher, so the affordable count on
10-16 is the number to read first.

## Measurement

- 2026-10-16 morning: read the first scan log. Expect "Contract floor" lines for
  dropped names, a pool of about 40 names, no mid below $1.50.
- Trader funnel log: the liquidity rejection rate on entry days from 2026-10-16 on.
  The trader's screen-vs-pool stats split at this date.

Related: `docs/DECISIONS/2026-06-04-contract-selection-liquidity.md` (the chooser),
`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md` (the universe).
