# 2026-08-19 — Pool liquidity ADMISSION FLOOR, and the cap cut 50 → 20

> **STATUS: NOT ADOPTED. Superseded the same day by `PRINT_FLOOR_MIN=25` on
> `signal-notifier`. The code was written, reviewed, and REVERTED (`git checkout
> enrichment-trigger/main.py`). Nothing in this note ships.**
>
> **Why it lost.** The review found the dominant leg (`call_active_strikes`) is built by a
> Polygon `next_url` walk that silently skips rows (memory
> `polygon-next-url-cursor-skips-rows`), so this design turned a known-lossy read into a
> hard admission gate. It also found the fail-open guard was unreachable in practice: every
> real degradation path produces present-but-wrong values, which land in tier 0 and get
> DROPPED. That is the artifact shape this repo cares most about.
>
> **What replaced it.** The owner's own idea: use the LIVE 10:00 ET print count that
> `signal-notifier` already fetches, instead of a scan-time proxy. It is a direct
> measurement, it is immune to the chain-walk defect, and it does not bias against fresh
> sweeps. Measured over 31 days: raising `PRINT_FLOOR_MIN` from 1 to 25 cuts the ghost rate
> from 36.7% to 9.4% and raises tradeable from 25.4% to 62.6%, at the cost of 3% of days
> falling below `TOURNEY_MIN`. One env var, on a code path already live and already
> fail-open per row.
>
> **Keep this note for the evidence tables below (the 62.7% ghost measurement and the
> supply curve). Those still stand. The proposed mechanism does not.**
>
> **Deploy state (2026-08-20):** the adopted replacement (`PRINT_FLOOR_MIN=25`) is NOT
> yet deployed. The live `signal-notifier` env verified =1, and `deploy.sh` pins 1. The
> deploy is the pending step.

**Owner call (2026-08-19):** no contract in the pool should be a ghost, and a pool of
10-20 names per day is fine because the MCP serves the wider historical datasets
separately.

## Problem

**62.7% of the pool is a ghost.** Measured on 4,292 labelled pool contracts across 87 scan
dates, where GHOST means 2 or fewer prints by 10:00 ET on entry day. Only 14.0% are
tradeable (11 or more prints). See `FINDINGS_LEDGER.md` §2026-08-19 (pool construction).

**The 2026-07-28 `LIQ_DEMOTION` was correct and the cap neutered it.** That change sorted
likely-ghost names below every unflagged name, but never dropped them, so a thin day could
not starve the pool. `ENRICH_TOP_N=50` then padded them straight back in. Only about 18
BULLISH names a day clear a real liquidity bar, so **50 slots guaranteed that roughly 30
flagged names were re-admitted every night.** The demotion did its job and the quota undid
it.

The scores we rank on do not help. Against a 62.7% base rate: `overnight_score>=7` gives
51.6% ghost, `contract_score>=9` gives 59.7%. `contract_score` picks the CONTRACT within a
ticker and was correctly recalibrated on 2026-07-28. **Nothing in the pipeline ranks the
TICKER on liquidity, and the ticker is where ghost risk lives.**

## Decision

Add a liquidity **ADMISSION FLOOR** in `enrichment-trigger`, and make the cap a ceiling
rather than a quota.

```
POOL_LIQ_FLOOR=true                 # kill switch
POOL_LIQ_UND_VOL_MIN=3000000        # underlying share volume
POOL_LIQ_STRIKES_MIN=25             # call_active_strikes + put_active_strikes
POOL_LIQ_OI_MIN=1200                # recommended_oi
POOL_FLOOR_MIN_SIZE=8               # backfill target on a thin day
ENRICH_TOP_N=20                     # was 50
```

The floor is the POSITIVE form of the same three fields the 07-28 demotion already used. It
requires all three to be GOOD instead of all three to be bad.

**Three tiers, and missing data never drops a name** (the 2026-08-07 rule: a fetch failure
is UNKNOWN, not zero):

| tier | meaning | treatment |
|---|---|---|
| 2 | verified liquid, all three present and clearing | admitted, ranked first |
| 1 | UNKNOWN, any component missing | admitted, ranked below tier 2 |
| 0 | verified thin, all present and at least one failing | admitted ONLY to backfill toward `POOL_FLOOR_MIN_SIZE` |

The tier outranks every edge lever in the sort key, because a name you cannot fill is worth
less than any signal it carries. `LIQ_DEMOTION` is unchanged and still orders within a tier.

## Evidence

Ghost rate and supply, measured on the same 87 days (supply = BULLISH candidates per day
after the UOA>$500K gate):

| filter | supply/day (median, p10) | % GHOST | % TRADEABLE | days ≥ 8 |
|---|---|---|---|---|
| **shipped today (no floor)** | 318, 221 | **62.7%** | 14.0% | 100% |
| `oi>=1200` alone | 78, 40 | 32.2% | 31.2% | 100% |
| `oi>=1200 + und>=3M` | 60, 30 | 24.6% | 36.7% | 100% |
| `oi>=1200 + strikes>=25` | 20, 9 | 10.7% | 57.3% | 93% |
| **CHOSEN: all three** | **18, 9** | **9.1%** | **59.3%** | **93%** |
| name-level only (`und>=3M + strikes>=25`) | 57, 29 | 41.1% | 31.7% | 100% |
| `und>=5M + strikes>=35` (name-level, tight) | 37, 16 | 37.0% | 37.7% | 100% |

**A 6.9x reduction in ghost rate.**

**Leg attribution, stated honestly.** Chain breadth is the dominant leg. `oi + strikes`
alone reaches 10.7%. Adding underlying volume buys only 1.6pp more (to 9.1%) and costs 2
names a day of supply. All three are kept because that combination is what was validated
end to end, but the underlying-volume leg is the marginal one and is the first to relax if
supply becomes a problem.

**This corrects a claim made earlier in the same session.** The 2026-07-28 study ranked the
two NAME-level fields as the strongest predictors, and that was read as "the name-level
fields are the fix". They are not sufficient on their own: name-level-only filters plateau
around 37-41% ghost no matter how tight. **Contract-level open interest is required.**

## Why a smaller pool costs nothing measurable

The same session established that within-pool ranking has **no demonstrated edge**: 14
leakage-safe features x pooled and day-demeaned AUC x 2 subsets = 56 looks, and only 3 CIs
excluded 0.50 against about 5.6 expected by chance. The one pre-registered lead
(`contract_score`, cap-50 era, AUC 0.552) **failed** its out-of-sample re-test at 0.481.

If we cannot rank inside the pool, a pool of 50 that is 63% untradeable is strictly worse
than a pool of 18 that is 91% non-ghost. We give up nothing we can measure.

## Risks and what we accept

**1. The scan-time OI leg will exclude fresh-sweep names. Accepted, deliberately.**
Scan-time OI runs far below live OI by construction, because the overnight sweep becomes
OI the next morning (the 08-07 fixture is 44 frozen against 2,077 live). A `recommended_oi
>= 1200` floor therefore drops some names whose OI builds overnight, and those are exactly
the freshest unusual flow. We accept it for two reasons. The measured ghost rate falls to
9.1% including that effect, and [[oi-not-quality-signal]] plus the 07-28 finding that sweep
volume is NON-monotonic at the top (vol>=2000 gives 13.6% ghosts, the one-off-sweep
signature) mean an OR on sweep volume would re-admit ghosts rather than rescue signal.

**2. Thin days now produce a smaller slate, by design.** 6 of 88 days (7%) fall below 8
eligible names and fire the backfill path, which logs a WARNING and admits verified-thin
names up to `POOL_FLOOR_MIN_SIZE` only. Worst day in the window supplies 5.
[[no-liquid-candidates-no-pick]] already covers a no-pick outcome and
`no_liquid_candidates` is read verbatim by MCP agents.

**3. Thresholds are 87-day in-sample fits in one regime.** Re-fit rolling from
`pool_liquidity_snapshot`. Do not treat 3M / 25 / 1200 as permanent.

**4. The ghost label exists only for contracts we DID select.** We hold no entry-day tape
for names we passed over, so the supply table assumes passed-over names behave like
selected names at the same liquidity level. That assumption is untested and is the largest
single risk in this note.

## Consequences

- **Pool size drops 50 → about 18/day.** Everything that reads the pool sees fewer rows:
  the webapp pool surface, `get_pool` on the MCP, `pool_liquidity_snapshot` (≈18 rows/day
  instead of 50), and x-poster copy that cites pool counts.
- **Enrichment cost falls roughly 60%.** `ENRICH_TOP_N` is the grounded-LLM fan-out
  ([[enrichment-cost-fix-topn-thinking-cap]]), so 50 → 20 cuts grounded calls proportionally.
- **A cohort RESET is required.** Selection changes, so the live cohort cannot mix. This
  matches the precedent of the 06-25 OI floor and the 08-07 print floor. Set
  `LIVE_COHORT_START_DATE` to the first scan date under the new pool and refresh
  `cohort_stats/current`. Remember the constant is mirrored in four places
  (`signal-notifier/main.py`, `libs/gammarips_content`, `gammarips-mcp/src/utils/data.py`,
  and the vendored copies in x-poster and blog-generator, which need a redeploy).
- **Stale docs to update on deploy:** `docs/wiki/policy/tourney-pool-cap-edge-rank.md`,
  `docs/wiki/architecture/enrichment-cost-fix-topn-thinking-cap.md`,
  `docs/wiki/architecture/enrichment-funnel-baseline.md`,
  `docs/wiki/findings/pool-delta-calibrated.md`, `docs/wiki/_index/REGISTRY.md`, and
  `docs/TRADING-STRATEGY.md` all cite a 50-name pool.

## Rollback

`POOL_LIQ_FLOOR=false` restores the exact prior ordering (the tier term becomes a
constant). `ENRICH_TOP_N=50` restores the prior pool size. Both are env vars and need no
code change.

## Verification before deploy

1. `gammarips-review` on this note plus the `enrichment-trigger` diff. Not yet run.
2. Dry-run the enrichment funnel on a recent scan_date and confirm the new
   `liq FLOOR ON ...` log line reports `verified_liquid` near 18 and `thin_backfill=0`.
3. Confirm a thin day (for example 2026-07-17, which supplies 5) fires the WARNING and
   produces a pool of exactly `POOL_FLOOR_MIN_SIZE`.
4. Confirm the downstream slate still clears `TOURNEY_MIN=8` after the notifier's print and
   live-OI floors, which now run against an already-filtered pool.
