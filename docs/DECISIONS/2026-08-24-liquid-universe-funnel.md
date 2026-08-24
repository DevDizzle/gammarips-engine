# 2026-08-24 — The funnel goes liquidity-first. Cohort resets to 2026-08-25

**Status:** CODE COMPLETE, NOT YET DEPLOYED. Owner approved 2026-08-24.
Two owner calls in one session: ship the liquid universe, and drop the
$500K call-UOA floor with it.

## The call

The scan no longer selects candidates by price move. It selects them by
liquidity.

- **Before:** pass 1 kept universe names with `|price change| >= 1%` (~100-300
  movers). Pass 2 priced their chains. Everything downstream ranked those.
- **After:** pass 1 keeps the most liquid universe names by session share
  volume (floor 3M shares, pre-rank top 300). Pass 2 prices their chains. A
  combined rank cuts to the top 100. Enrichment reads only that universe.

Rank = `z_cross(log1p(chain dollar volume)) + z_cross(log1p(share volume))`,
session T, with a 25-listed-strike chain-depth floor. This is the exact
definition the 2026-08-22 study measured. Open interest is NOT an input: no OI
history exists in this stack, so ranking on the current snapshot would be
lookahead.

## Why

The 2026-08-22 liquid-universe study measured the production funnel against the
liquid universe on the same tape and window:

| | production pool | liquid universe |
|---|---|---|
| no fill at 10:00 ET | 40.5% | 6.1% |
| tradeable by 10:00 ET | 17.9% | 63.1% |

The old funnel selects contracts that are **harder to trade** than random
liquid ones. It chases unusual volume, and unusual volume in a thin name is one
large print, not a market you can exit.

The same study found the selection signal on top of the liquid universe is
null (+0.4pp, 90% CI [-1.7, 2.1]), and the sibling pool-vs-benchmark study
found the production pool is not distinguishable from matched random contracts
(-1.33pp [-3.78, 1.04]). So this change ships on **executability alone**. It
is not a claim of edge, and no measured return improves because of it. Decision
rule 2 of `docs/EXEC-PLANS/2026-08-20-liquid-universe-funnel-spec.md`.

## Call 2: the $500K call-UOA floor is dropped

The floor belonged to the UOA-first funnel, where it was the only thing
separating an unusual print from ordinary volume. Inside the liquid universe
every name already carries heavy flow, so the floor stopped selecting and only
thinned the pool.

Measured on a full-size dry run against live data (2026-08-24, ~12:30 ET,
partial-session volumes, 216 names priced):

| stage | with the floor | without it |
|---|---|---|
| ranked liquid universe | 100 | 100 |
| BULLISH | 45 | 45 |
| into the enrichment pool | 30 | **44** |

The owner chose the higher-depth option at maximum liquidity. Removing a
selection gate is itself a selection change, and there is no direct evidence
either way inside a liquid universe. It is recorded here as an owner call.

`ENRICH_UOA_FLOOR` restores a floor under either funnel. The legacy mover path
keeps the $500K floor, because there it still does work.

## Measured funnel (2026-08-24 dry run, ~12:30 ET, partial session)

3,532 universe names -> 216 over the 3M share floor -> 100 ranked liquid ->
45 BULLISH -> 44 clear `overnight_score >= 1` and carry a contract -> pool of
44 (`ENRICH_TOP_N=50` does not bind).

**These counts come from a partial session.** The dry run ran at ~12:30 ET, so
day bars were incomplete and fewer names had cleared the 3M share floor than
will clear it at the 23:00 ET run. Treat 44 as the shape, not the number.

Pool depth now floats with the market. A down day gives a smaller pool. That is
the honest reading of a bullish-only pool, and the spec accepted it: "fewer
qualifying is an accepted outcome".

## What changed

| file | change |
|---|---|
| `src/enrichment/core/pipelines/overnight_scanner.py` | liquid pass-1 selection, `_rank_liquid_universe`, snapshot staleness check, `listed_strikes`, 4 new columns, additive schema sync |
| `enrichment-trigger/main.py` | `liquidity_rank <= LIQUID_TOP_N` gate, UOA floor follows the funnel, column and era probes |
| `signal-notifier/main.py` | `LIVE_COHORT_START_DATE = 2026-08-25` |
| both `deploy.sh` | env pins for every new knob |

New columns on `overnight_signals`: `liquidity_rank`, `liquidity_score`,
`listed_strikes`, `universe_mode`. Added by an additive schema sync in
`_ensure_table`, never by `autodetect`.

## Cohort reset

`LIVE_COHORT_START_DATE = "2026-08-25"`. Sixth reset in nine weeks. This is a
funnel-level selection change, so the standing doctrine applies. No truncation:
prior rows stay in `forward_paper_ledger` and the date filter excludes them from
the public cohort. `policy_version` STAYS `V7_1_TILTED_GIGO` because exit
mechanics did not change.

**The date is verified from the live scheduler, not assumed.**
`overnight-scanner-trigger` next fires 2026-08-25T03:00Z = 2026-08-24 23:00 ET.
So scan_date 2026-08-24 is the first liquid scan, enrichment reads it at
08-25 05:30 ET, and the first entry is 08-25.

## Rollback

One env var per service, no code change:

- `LIQUID_UNIVERSE=false` on overnight-scanner restores the mover funnel.
- `ENRICH_LIQUID_ONLY=false` on enrichment-trigger removes the gate and
  restores the $500K floor.

Roll back both together. Then move the cohort date back.

## Deploy order and safety

Deploy **overnight-scanner first**. It creates the four columns. Deploying
enrichment-trigger first is safe anyway: it probes for the column and for
ranked rows on the scan date, and falls back to the legacy funnel with a logged
warning instead of failing. A replay of a pre-switch date takes the same
fallback, so old dates still reproduce.

## Known limits

- The snapshot staleness check finds a name whose day bar disagrees with the
  rest of the feed. It cannot find a whole feed that is one session stale,
  because it calibrates on the feed itself. The scanner runs 23:00 ET on
  trading days only, so this is a non-production path.
- Executability was measured at N=100. `LIQUID_TOP_N=200` is a pre-declared
  screen-composition cell, not a measured executability cell. Do not raise the
  knob and claim the fill numbers still hold.
- The 2026-08-24 dry run is one partial-session tape, not a distribution.

## Downstream, not done here

The public copy still describes a market-wide unusual-activity scan. The
universe is now the 100 most liquid names and the UOA floor is gone. Webapp
copy changes go through that repo's `gammarips-copywriter` agent and `/ship`
from `~/workspace`. Not touched in this session.
