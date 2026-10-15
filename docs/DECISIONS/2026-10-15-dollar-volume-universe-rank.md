# 2026-10-15: Liquid-universe rank on 20-session median dollar volume

**Status:** BUILT 2026-10-15 (owner call: "Do it"). Dry run passed on live data. Deploy
pending: the session's auto mode blocked `bash deploy.sh`, so the owner runs it
(`~/workspace/DEPLOY-SCANNER-DV.txt`). Update this line with the scanner revision after
the first real scan.

## Decision

The stock-side term of the liquid-universe rank (`_pass1_stock_snapshots` and
`_rank_liquid_universe` in `src/enrichment/core/pipelines/overnight_scanner.py`) is the
20-session median of close x volume, not session T share volume.

| Item | Before (2026-08-24) | Now |
|---|---|---|
| Pre-rank 300 | session T share volume | 20-session median dollar volume |
| Rank stock term | `z_cross(log1p(share volume))` | `z_cross(log1p(dollar_volume_20d))` |
| Rank chain term | `z_cross(log1p(chain dollar volume))`, session T | unchanged |
| Share floor | 3M shares, session T | unchanged |
| Strike floor | 25 listed strikes | unchanged |
| Rule set B contract floor | mid >= 1.50, delta <= 0.50, OI >= 500 | unchanged |

The history comes from Polygon grouped-daily adjusted bars, one call per calendar day
walked back from the session before the snapshot (`PolygonClient.fetch_grouped_daily`),
19 answered sessions plus the snapshot for session T. Env vars pinned in
`overnight-scanner/deploy.sh`: `LIQUID_RANK_BASIS=dollar_volume_20d`,
`LIQUID_DV_SESSIONS=20`. Rollback: `LIQUID_RANK_BASIS=share_volume` and redeploy.

Two new columns on `overnight_signals` (additive, NULLABLE, synced by `_ensure_table`):
`dollar_volume_20d` (the value the rank used) and `rank_basis`. `rank_basis` reads
`dollar_volume_20d` on a normal night, `dollar_volume_T_only` when fewer than 10 sessions
answered (outage) or a name has fewer than 10 sessions of history (new listing), and
`share_volume` on rollback. A thin night logs an ERROR line and still writes a pool.

## Why

This is a contract-quality change, the same axis the liquid universe shipped on. It is
not a return claim.

- The trader's funnel log rejects 33% of pool rows at its 10% spread gate, and the drop
  rate rises as the contract price falls (`docs/DECISIONS/2026-10-15-contract-premium-floor.md`).
  Share volume admits the cheap end of the market: on the last 20 scan days the live pool
  held a median stock price of $63 and 22 names below $15, with MARA, ONDS, SMR, RKT,
  QXO, WULF, PATH, RIVN, PCG and F in it every day.
- Dollar volume ranks the same liquidity in the unit the book trades in. Replayed from
  cached bars over the same 20 days: 58 of 100 names in common with the live pool,
  median price $207, 1 name below $15, daily churn 16 names (single-day dollar volume)
  against 5 (20-session median) and 21 (live).
- The 2026-10-15 stock-move study (`FINDINGS_LEDGER.md` §2026-10-15) found that dollar
  volume predicts nothing in the wide era (IC 0.015, top-decile excess -0.08 pts) and
  that its holdout read was a six-week mega-cap regime. So the rank does not buy a return
  and nobody may say it does. The owner's demand-signal question is answered there too:
  volume over average volume is dead at 3 sessions and the scan-day move reverses.

## Dry run (read-only, live data, 2026-10-15 15:17 ET, session in progress)

`scripts/tests_and_diagnostics/dry_run_universe_rank.py --pass2` ran the scanner's own
pass 1, pass 2 and rank under each basis. 20 sessions answered the history fetch, one
name had a short history.

| Final 100 | Share volume (before) | Dollar volume 20d (now) |
|---|---|---|
| Median stock price | $70 | $177 |
| Names below $15 | 29 | 3 |
| Names below $5 | 4 | 0 |
| Candidates past the 25-strike floor | 213 of 300 | 267 of 300 |
| Names in common | 67 | |

Out: AAL BTDR CLF CLSK CMCSA CORZ EOSE F FRMI GME LUMN MARA NU NVTS OKLO ONDS PATH PCG PFE
QBTS QXO RGTI RIOT RIVN RKT SKYD SMR STM T TE TTD USAR VG.
In: ABBV ABT ADBE APH BA BKNG BX CAT CLS CRM CVX DOCN ETN HD IBM JNJ JPM KO MCD MDT MRK MS
PANW PEP PG PM QCOM SNOW STX TXN V VST XOM.

## Cost of the change

- A 30-delta call on a $200 stock costs $500 to $1,000. The trader sizes smaller.
- Rule set B's $1.50 mid floor binds less, because few calls on these names price below it.
- About 30 grouped-daily calls per scan, under 2 seconds at the rate limit.

## What this does not change

- The 100-name universe size, the share floor, the strike floor, rule set B, enrichment,
  the MCP, the trader. The chain term of the rank is unchanged.
- Selection research stays CLOSED. No return claim attaches to this change on any surface.

## Measurement

- First scan after the deploy, scan log: "Pass 1: rank basis dollar_volume_20d, 20
  sessions in the median", "Liquid rank (dollar_volume_20d)" with a median price near
  $180 to $200, BQ `rank_basis = 'dollar_volume_20d'` on every row of that scan_date.
- Trader funnel log from the next entry day on: liquidity rejection rate. Rule set B and
  this change land close together, so the split is between them, not within.
- Trader drift test F-059 keeps running on pool alumni. It measures stock drift, not this.

## Stale public copy (separate repos, not changed here)

These say "share volume" and are now inaccurate. Webapp copy goes through
`gammarips-copywriter` and `/ship`: `src/app/how-it-works/page.tsx` (line 151),
`src/app/methodology/page.tsx` (lines 43 to 45), `src/app/signals/page.tsx` (line 57),
`src/components/landing/faq.tsx` (line 56), `CLAUDE.md` (lines 95 to 96). MCP content:
`content/playbooks/changelog.md` (line 16), `content/playbooks/start-here.md` (line 3).

Related: `docs/DECISIONS/2026-08-24-liquid-universe-funnel.md` (the universe),
`docs/DECISIONS/2026-10-15-contract-premium-floor.md` (rule set B),
`docs/wiki/architecture/liquid-universe-funnel.md` (the wiki claim, amended).
