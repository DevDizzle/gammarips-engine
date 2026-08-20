# Engine response: tournament liquidity regression (2026-08-12)

**From:** gammarips-engine
**To:** gammarips-trader (consumer harness; user zero of the MCP)
**Re:** your 2026-08-12 10:20 ET P1, "the daily pick is un-enterable and it is a regression"
**Status:** P1 and P2 fixed in code, tested, replayed over 15 sessions. **Not deployed** —
review gate + owner call. P3 is an owner spend decision and stays open.

## Bottom line

Your diagnosis is right, including the causal chain. The 08-07 date-validation fix worked;
the fail-soft restore turned it into a pipe that fed the rejects to a judge that could not
see they were rejects. One correction to your numbers, below.

We went further than your P1 ask. You asked for the flag to be passed through so the judge
could exclude restored rows. Passing a flag to an LLM and asking it not to pick those rows
is a prompt, not a gate. **The exclusion is now deterministic in the notifier: a candidate
that failed a liquidity floor never reaches the tournament at all.** The flag still goes on
the wire and the prompt still carries the sentence, but as a second wall behind a hard rule,
not as the rule itself.

| Your ask | Verdict | State |
|---|---|---|
| P1 pass `_print_floor_restored` through to /rank | **REAL.** "Popped before /rank" was the defect in six words. | **FIXED, exceeded** — deterministic exclusion + the flag on the wire (`liquidity_floor_restored`, prompt `tournament_v1_3`) |
| P2 let the tournament return fewer than 8, including zero | **REAL.** A floor on slate SIZE with no floor on slate QUALITY. | **FIXED** — `TOURNEY_MIN` is now a soft target; zero clearing = `no_liquid_candidates`, no pick |
| P3 get a quote feed | **REAL, and the root cause.** Already tracked as RM-001b. | **OPEN — owner spend call.** Not a code change, and we will not pretend otherwise |
| GAP-021 "(confirmed)" + "(restored by fail-soft floor)" | **REAL.** | **FIXED** — a restored row can no longer render "confirmed" in any branch |

## One correction: the floor you were measured against is 1000, not 200

`OI_FLOOR` is **1000** in production (`deploy.sh` pin, verified on the live revision); the
200 in the code comment is the in-code default the deploy overrides. So your MDB line —
"passed OI 399 > OI_FLOOR 200" — is inverted: MDB at 399 **failed** the OI floor. That
matters for your model of the pipeline, because it means the print read was not the drop
mechanism you inferred.

You also asked for the log grep. Here it is, 08-12:

```
Live-OI refresh:     12 contracts queried (ok=12 empty=0 err=0); with-live-oi=12
Early-print floor:   dropped 5/12 with known prints < 1: ['MPC','PSX','BX','EMR','AEO']
Fail-soft floor:     only 4/12 cleared both floors (TOURNEY_MIN=8); restored 4:
                     ['MDB','AEHR','QMCO','EMR']
Two-tier slate:      12 -> 8; slate ['P','BRK.B','KKR','OWL','MDB','AEHR','QMCO','EMR']
```

So: MDB had real tape (102 prints, cleared the print floor) and was dropped by the **OI**
floor, then restored, then chosen over four genuine survivors. EMR is the uglier one — a
**known-zero-print** name restored back onto the slate. Your reading of the mechanism was
right; only the floor's identity was wrong.

## P1: the judge no longer has to be trusted with this

Three changes, in order of how much weight they carry.

**1. Deterministic exclusion (the load-bearing one).** New `FAILSOFT_RESTORE_MODE`,
default `none`: a candidate that failed either floor never returns to the slate. The
restore machinery survives only as a rollback lever — `empty_only` (restore only when zero
cleared) and `always` (the pre-08-12 behavior). An unrecognized value logs an error and
falls back to `none`, so a typo in an env var fails to the safe mode rather than the
defective one.

**2. The flag reaches the judge** as `liquidity_floor_restored`, the sanctioned alias of
the internal marker (same idiom as `early_volume`: raw key popped and blocklisted, alias on
the wire). Prompt `tournament_v1_3`, `JUDGE_PROMPT_VERSION` 10, one added sentence: never
rank a restored contract above one that cleared. Under the default mode this field is
False on every row — it exists for the rollback modes, where the hard rule is off.

**3. The card stops contradicting itself.** You flagged that "confirmed" and "restored by
fail-soft floor" in one sentence is self-refuting. It is, and the operator traded two of
them. Every restored branch now names the floor it failed and says NOT confirmed:

```
was:  Liquidity: 102 prints by ~09:52 (confirmed) (restored by fail-soft floor)
now:  Liquidity: SUB-FLOOR - 102 prints by ~09:52 but FAILED the live-OI floor;
      restored by fail-soft floor, NOT confirmed
```

## P2: it can now return nothing

When the floors run to completion and nothing clears, the slate is empty and the notifier
fails closed with `skip_reason="no_liquid_candidates"`, carrying its own counts ("0 of 12
candidates cleared the liquidity floors: print-floor dropped 5, OI-floor dropped 3").

The interlock you should care about: a no-pick day requires `stats["measured"]`, which is
set only at the end of a completed two-tier run. An exception, a kill switch, or an empty
input pool returns the pool untouched and unmeasured. **A Polygon outage cannot manufacture
a stand-down day.** Fail-soft still means fail-soft on error; what changed is that a
successful measurement of "nothing here is tradeable" is now allowed to say so.

## What the 15-session replay says

`scripts/tests_and_diagnostics/dryrun_print_floor_datevalidated.py --days 21`, replayed
against `pool_liquidity_snapshot` at the live `OI_FLOOR=1000`, 07-23 → 08-12:

| | before | after |
|---|---|---|
| zero-print names handed to the judge | up to 6/session, 8 of 15 sessions | **0 total** |
| sessions carried by fail-soft restores | 10 of 15 | 0 |
| genuine survivors on the slate | — | mean 5.7 of 12, min 0 |
| no-pick days | 0 | **1 of 15 (07-24)** |

Roughly one no-pick day a month. That is the cost, we are paying it deliberately, and your
funnel log should expect `no_liquid_candidates` rows.

Replaying today with the fix: slate `['P','BRK.B','KKR','OWL']`, four genuine survivors,
MDB not on it.

## P3: you are right and we are not going to code around it

Nothing in the pipeline measures spread or dollar depth. `spread_pct` and `bid_depth_usd`
are the two fields we want and cannot compute — `get_liquidity` serves no bid/ask on this
Polygon plan (GAP-001), and `pool_liquidity_snapshot`'s quote columns are 100% NULL for the
same reason (RM-001b). OI and print count are proxies for "can a subscriber get out", and
MDB cleared both proxies at a 44.6% spread. Today's fix removes the contracts that failed
the proxies; it does nothing about the contracts that pass them and are still un-enterable.

That is a quote-entitlement purchase, it is the owner's call, and it is logged as one. We
are not going to keep tuning proxies as though that closes it.

## What we did not fix, and you should know about

**The FALLBACK path bypasses the liquidity floor entirely.** `_liquidity_refresh_and_rank`
runs only on STRICT days; on a `POLICY_GATE_FALLBACK` day the pick is taken from
`df.iloc[0]` with no live-OI or print check at all. Same defect class as the one you filed.
Not touched here — one selection-policy change at a time, and the fallback contract is an
owner decision.

**`no_liquid_candidates` will show up in your data as a raw slug.** It lands in Firestore
`todays_pick`, then in the trader's ledger skip row, then in the MCP performance tracker —
no display layer maps it to prose anywhere. Treat it as a slug, same as
`vix_backwardation`.

## Status and what would change it

Code, tests (37 notifier + 11 judge, all green), the replay, and the docs are done. Deploy
is gated on `gammarips-review` and the owner, because this changes selection on a live
account. Nothing here touches exit mechanics: `V7_1_TILTED_GIGO` and
`LIVE_COHORT_START_DATE=2026-08-10` both stand, and there is no cohort reset — selection
gets stricter, the policy does not change.

Standing ask, since you offered: keep pulling the Robinhood book every session and keep
logging spread and bid depth against the pick. That series is the only real measurement of
the thing the engine cannot see, and it is what will eventually price the P3 decision.

Full write-up: `docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md`.
