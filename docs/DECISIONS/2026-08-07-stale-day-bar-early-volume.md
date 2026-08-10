# 2026-08-07 — Stale day bar: `early_volume` was the prior session's total, and the print floor never fired

**Status: DEPLOYED 2026-08-07 (owner go), `gammarips-review` PASS-WITH-CONDITIONS, all conditions met.**
**Revisions: `signal-judge-00009-dfg`, `signal-notifier-00057-fwj`. Live env verified (`PRINT_VALID_AFTER_ET_MIN=590`, `PRINT_BAR_MAX_AGE_DAYS=10`, `OI_FLOOR=1000`, `JUDGE_PROMPT_VERSION=9`, `JUDGE_PROMPT_LABEL=tournament_v1_2`).**
**Cohort RESET applied — `LIVE_COHORT_START_DATE = 2026-08-10`; `cohort_stats/current` refreshed to 0 closed. First pick under the fixed floor: Mon 2026-08-10 09:52 ET.**

## Problem

Tournament pick GCT (`O:GCT260918C00055000`, confidence HIGH) emailed 09:53 ET
with `Liquidity: 2045 prints by ~09:52 (confirmed)`. At 10:40 ET the contract had
traded **zero** contracts for the session (bid 2.65x56 / ask 2.95x15, 10.7%
spread on a 2.80 mark). The card's entry $3.20 / limit $3.25 sat **above** the
live ask. The 2045 was 2026-08-06's total volume.

`oi_build` was real and is not implicated: OI 44 at scan -> 2,077 next morning
(yesterday's sweep becoming today's OI) is exactly what that field measures.

Logged trader-side as GAP-018 (`gammarips-trader/docs/GAP-LOG.md`); GAP-017 is
the related stale-card defect from 2026-08-06.

## Root cause

`signal-notifier/main.py::_fetch_live_oi` extracted `results.day.volume` and
never read `results.day.last_updated`. Polygon's v3 option snapshot serves the
**prior session's** `day` bar when a contract has not printed yet today, so
yesterday's total masquerades as this morning's print count whenever the tape is
silent.

The 2026-07-28 design assumed the opposite. That decision note states
`today_volume` is "~always 0/None" before the feed turns real, and the
`_fetch_live_oi` docstring said the same. **Both were false.** Measured against
`pool_liquidity_snapshot`:

| measurement | result |
|---|---|
| successful snapshot reads examined | 49,285 |
| reads where `day.volume` is exactly 0 | **0** |
| reads where `day.volume` is NULL | **0** |
| stale-bar reads carrying volume >= 5 | **100%** |
| pool-of-50 rows with a stale bar at the 09:45-10:00 ET read | **44% mean** (13-29 of 50 daily) |

Polygon never serves a zero-volume day bar. Therefore `_known_prints()` could
not return 0, and:

1. **The primary print floor never dropped a single candidate.** Replaying 15
   sessions (2026-07-20 -> 08-07) through the production floor: `print-floor
   dropped 0` on every one. It has been a structural no-op since go-live
   2026-07-29, not an intermittent miss.
2. **The judge's `early_volume` was an unlabeled mix of two different
   quantities.** ~40% of each capped slate carried a full prior session; the rest
   carried ~22 minutes of real tape. The stale values are systematically
   **larger**, so the prompt's "prefer the one showing real early trading
   activity" directive systematically preferred the **least**-traded contracts.
   It was inverted, not merely noisy.
3. **The operator email stamped phantom counts "(confirmed)".** Because a stale
   bar always carries volume >= 5, the failure mode was always the
   maximum-confidence string, never a marginal 1-4.

The 2026-07-28 tradeability study is **not** implicated and does not need
re-running — see "What the study got right" below.

## Fix 1 — date-validate the day bar (`signal-notifier/main.py`)

New `_day_bar_et_date()` + `_validate_day_bar_volume()`, called from
`_fetch_live_oi`, which now takes an injectable `read_dt_et` (defaults to now;
tests use it).

| snapshot state | resolved print count |
|---|---|
| bar dated TODAY (ET) | volume passes through (real prints) |
| bar dated EARLIER, read after `PRINT_VALID_AFTER_ET_MIN` | **KNOWN 0** (int) |
| bar dated EARLIER, read before `PRINT_VALID_AFTER_ET_MIN` | None (UNKNOWN) |
| no parseable `last_updated` | None (UNKNOWN, fail-open, logged WARNING) |
| missing `day` dict / fetch failure | None (UNKNOWN) — unchanged |

`PRINT_VALID_AFTER_ET_MIN` (default 590 = 09:50 ET) is new and is a **safety
interlock, not a tuning knob**. Pre-open and in the first minutes after the open,
every bar is legitimately the prior session's on a 15-minute-delayed feed;
asserting "0 prints" there would empty the entire slate into the fail-soft
restore. This directly de-fuses the 2026-07-28 note's "sequencing hazard": if the
cron ever drifts earlier than 09:50, the floor degrades to fail-open instead of
nuking the pool.

Known-zero and UNKNOWN stay distinct — `_known_prints` and C4 fail-open depend on
it. **No new gate:** the existing `PRINT_FLOOR_MIN=1` now receives values it can
act on. The false docstring claim is corrected in place.

### Leakage argument (C1)

`day.last_updated` is a **timestamp used solely to validate the volume field**.
No price, greek, or IV information crosses the C1 wall. It is strictly pre-entry
(read ~09:52 vs 10:00 entry) — the same leakage class as the already-permitted
`live_oi` and `day.volume` reads sanctioned on 2026-07-28. Every other live
field remains discarded at fetch time. The C1 comment block is updated to name
three surviving scalars instead of two.

## Fix 2 — prompt `tournament_v1_2` (`signal-judge`)

Two sentences added to `_build_prompt`, everything else byte-identical to v1_1
(enforced by `signal-judge/tests/unit/test_prompt_v1_2.py` against a golden
captured from the pre-edit code):

- **(a)** "An early_volume of 0 means the contract has not traded at all this
  morning; treat it as untradeable unless no candidate shows prints." Until this
  fix a zero could not physically reach the prompt. Now it is common, and the
  fail-soft restore deliberately puts sub-floor names back in front of the judge
  — this is the second wall behind the floor, load-bearing on real sessions, not
  a corner case.
- **(b)** the `why` must state the `early_volume` / `oi_build` values it relied
  on when liquidity influenced the ranking. Today's rationale ("massive early
  volume (2045) confirming actionable liquidity") flowed into the operator email
  as if verified; a why that carries its numbers makes a bad number auditable.

Provenance: `JUDGE_PROMPT_VERSION` 8 -> **9** (an INT, the ledger column) and
`JUDGE_PROMPT_LABEL` -> `tournament_v1_2`. **`signal-judge/deploy.sh` pins both
via `--set-env-vars` and was updated too** — the pin overrides the code default,
so a bump that touches only `tools.py` never reaches production. A regression
test now asserts deploy.sh and the code defaults agree.

## Fix 3 — email honesty (`_liquidity_email_line`)

Every rendered count is date-validated upstream, so "(confirmed)" can only
describe prints that actually happened. A known zero restored by the fail-soft
floor now reads `0 prints by ~09:52 (NO TAPE - restored by fail-soft floor)`
instead of collapsing into `UNVERIFIED`: "no tape" is a measurement, "UNVERIFIED"
is the absence of one, and merging them re-hides exactly what this fix exposes.

## Measured deploy impact

`scripts/tests_and_diagnostics/dryrun_print_floor_datevalidated.py` (read-only)
replays production code over persisted snapshots. 15 sessions, 2026-07-20 ->
08-07, at the **production config** (an earlier pass at the code-default
`OI_FLOOR=200` materially understated the impact — `gammarips-review` FINDING C1):

```
PRINT_FLOOR_MIN=1  OI_FLOOR=1000  TOURNEY_MIN=8  TOURNEY_POOL_CAP=12  PRINT_VALID_AFTER_ET_MIN=590
```

| | pre-fix | post-fix |
|---|---|---|
| print-floor drops (capped-12 slate) | **0** | 58 |
| known-zero per capped slate, mean | 0 | 4.9 / 12 |
| survivors clearing both floors, mean | 6.9 | **5.1** |
| fail-soft restores, mean per session | 3.1 | 3.1 |
| sessions where fail-soft carries the slate | 8/15 | **11/15** |
| **zero-print names restored to the judge** | 0 | **24 total, 8/15 sessions, max 6** |
| top-of-slate name changes | — | 2/15 |

Read the bolded row as the operative one. On more than half of sessions the
fail-soft floor hands zero-print names **back** to the judge, up to 6 at once.
**Fix 2a is therefore not a backstop, it is the only remaining wall on those
sessions** — the floor cannot be the last line of defense when starvation
protection is designed to overrule it. Do not ship Fix 1 without Fix 2.

Genuinely-clearing candidates average 5.1 against `TOURNEY_MIN=8`, so the
tournament now routinely sees a slate padded with floor-failing names. That is
the intended fail-soft behavior (the tournament must never starve), but it is a
real change in what the judge is asked to choose among, and it is the single
thing most worth watching in the first week of the new cohort.

**Acceptance met at production config:** replaying 2026-08-07, the print floor
drops `['AEVA', 'GCT', 'FSLY']`, 5 clear both floors, and the 3 restores go to
`['NET', 'ROKU', 'MET']` — prints-bearing names that failed only the OI floor.
The restore key `(prints desc NULLS LAST, live_oi desc)` ranks any name with real
tape above a known zero, so **GCT does not return to the slate.** A zero-print
contract can no longer pass the floor, reach the judge with nonzero
`early_volume`, or appear in an email as "confirmed".

## Review conditions (`gammarips-review`, PASS-WITH-CONDITIONS, 2026-08-07)

All four blocking conditions resolved before deploy:

1. **`docs/TRADING-STRATEGY.md` cohort date** — was two resets stale (still read
   2026-06-26 at lines 4/34/100/119/125). Propagated to 2026-08-10. `CHEAT-SHEET.md`
   likewise still claimed the 09:52 cron move was "deploy pending review".
2. **Dry-run measured at the wrong secondary floor** — re-run at production
   `OI_FLOOR=1000`; the table above is the corrected one, and the conclusion
   changed (fail-soft carries 11/15 sessions, not 8/15, and zero-print names are
   restored to the judge on 8/15).
3. **Cron verified, not assumed** — `gcloud scheduler jobs describe
   signal-notifier-job` returns `52 9 * * 1-5`, `America/New_York`, `ENABLED`.
   The 09:50 guard is therefore live-correct and the deploy is not a no-op.
4. **`PRINT_VALID_AFTER_ET_MIN=590` + `PRINT_BAR_MAX_AGE_DAYS=10` pinned** in
   `signal-notifier/deploy.sh` — that line is `--set-env-vars`, which replaces
   the whole set, so an unpinned rollback lever would be wiped by the next deploy.

Recommended items also taken:

- **Replay provenance on `todays_pick`** — `early_volume`, `day_bar_stale`,
  `print_floor_restored`. The incident was not "a number was wrong" but "the
  artifact could not tell you the number was phantom", and Cloud Run logs age out.
  Firestore is schemaless; this never touches the ledger load job.
- **Sanity-bounded bar date** — a bar outside `[read - 10d, read]` is UNDATABLE,
  not zero. If Polygon ever changes `last_updated` units, every contract would
  parse to 1970 and the interlock would invert from fail-open into
  drop-everything. Same vendor-semantics class as the defect itself.
- **One read clock per batch** — each worker previously evaluated
  `datetime.now(est)` independently, so a batch straddling 09:50 could split a
  slate between UNKNOWN and KNOWN-ZERO and make the run non-replayable.
- **Prompt wording** — "has not traded at all this morning" overstated the
  measurement by ~15 minutes on a delayed feed; now "had not printed at all as of
  the pick-time read".

**Downstream cohort filters — DONE 2026-08-07 (all three).** Every consumer that
defined the live cohort by `policy_version` alone now uses the (label, start
date) PAIR:

- **`gammarips-mcp`** (separate repo, monetized surface) — `src/utils/data.py`
  is the single source of truth; `positions`/`performance` carry `cohort_start`;
  aggregates are `null` (never `0.0`) at N=0; `policy_version="all"` carries an
  explicit disowned-cohort warning. `SERVER_VERSION` 4.1.0, rev
  `gammarips-mcp-00042-kq2`. Its V3 spec had ALWAYS specified a
  `LIVE_COHORT_START_DATE`; the code simply never applied it.
- **`blog-generator`** (rev `blog-generator-00032-8k9`) — the catch of the day:
  its 30-trade unlock gate, the thing that decides whether a public post may
  claim wins/P&L at all, read **30** (unlocked) against the repudiated cohort
  and would have fired Monday 2026-08-10 05:00 ET. It now reads 0 (blocked).
  The gate also **fails closed** now — a BigQuery error returns `blocked`, not
  `error`, because the writer/reviewer prompts branched on `blocked` alone and
  an error handed the writer a numbers-requiring post type with no suppression.
- **`x-poster`** (rev `x-poster-00043-mxv`) — both ledger queries floored.
- Shared definition lives in `libs/gammarips_content/gammarips_content/cohort.py`
  (vendored into both publishers), pinned to the engine constant by
  `libs/gammarips_content/tests/test_cohort_pin.py` so the next reset cannot
  silently drift.

Still deferred to `gammarips-engineer`, not this work: the Polygon key travels in
the `_fetch_live_oi` query string while raw request exceptions are logged, so an
outage can write the key into Cloud Logging (`pool_liquidity.py` already solved
this with a Bearer header — same defect at `_fetch_entry_mark` and
`compute_active_days_20d`); and `ledger_trades` writes `merge=True` and never
prunes docs that fall out of a cohort (no live renderer today).

**Real-money go-live trigger: RETIRED 2026-08-07 (owner decision, DECIDED).**
The old "N >= 30 closed trades" automated-go-live condition is deleted from
`docs/TRADING-STRATEGY.md`, not re-anchored. It was written for a paper-only era
the project is long past — the operator already trades live and discretionarily,
and no trade counter gates anything. Do not reintroduce it in any form. (This is
unrelated to `blog-generator`'s `N_TRADES_UNLOCK`, which is a publishing
compliance guard and stays.)

## What the study got right (correction to the incoming handoff)

The handoff proposed re-running the tradeability study on the assumption its
cohort "carried the same contamination in both directions". **It did not, and
re-running it is unnecessary.** `FINDINGS_LEDGER` records `early==0 (52% of
pool)` and "09:45 shows NOTHING — first fresh data 09:52"; the measured stale-bar
rate in that read window is ~50%. A field that is never 0 in the raw feed cannot
produce a 52%-zero bucket, so the study date-validated (or equivalent) and got
the right answer. **This was a research-to-production translation gap: the
study's definition of "prints" was never implemented in `_fetch_live_oi`.**
`PRINT_FLOOR_MIN` and the >=5 email threshold rest on sound work.

The real exposure on that finding is different: the ledger notes its scripts and
labeled data live in a **session scratchpad**, so the study may no longer be
reproducible. Confirm the print construction survives somewhere before it is
next relied on.

## Follow-on 2 audit — other readers of snapshot `day.volume`

- `signal-notifier/pool_liquidity.py:172` — persists `day_volume` **and**
  `day_last_updated` together. Clean; it is the substrate this investigation used.
- `enrichment-trigger` `day_volume` / `volume` — the **underlying equity's**
  daily share volume, not the option snapshot day bar. Not affected.
- `gammarips-mcp` `market_snapshot.py` — returns `day.last_updated` alongside
  `day_volume` and its `freshness_note` tells the consumer to "judge staleness
  from day.last_updated". Structurally clean. **One wording defect flagged, not
  fixed here** (separate repo, its own rules): the note calls `day_volume` "the
  live (delayed) session", which is false on a stale bar. Route any copy change
  through that repo's context files.
- No other reader on the selection or email path.

## Cohort — RESET (owner call, 2026-08-07)

**DECIDED: `LIVE_COHORT_START_DATE` 2026-07-29 -> 2026-08-10** (first entry under
a print floor that actually fires; the cron is `52 9 * * 1-5` ET, so the next run
after this deploy is Mon 08-10). Rationale: the reset argument below carried —
what ran since 07-29 was v1_1 *minus* its primary floor, i.e. never the policy
approved on 07-28.

Same shape as the 07-28 and 06-25 resets: **no truncation.** The 7 rows of the
07-29 cohort and the 22 before them stay in `forward_paper_ledger`, excluded from
the public cohort by the date filter. `cohort_stats/current` is fully recomputed
from the constant, so there is no Firestore state to clear — the public panel
legitimately reads 0 closed trades until the first 08-10+ entry closes.
`policy_version` stays `V7_1_TILTED_GIGO`.

**Ledger annotation of HUT / TGT: NOT executed, and now moot for the public
surface** — the reset excludes both by date filter, and `forward_paper_ledger`
has no annotation column (adding one is a production schema change). The durable
record of which picks were affected is this document plus the FINDINGS_LEDGER
correction. Raise it again only if a research pass needs the flag in-table.

### Original question as posed (retained for the trail)

`LIVE_COHORT_START_DATE = 2026-07-29`. Of the 7 entries in the live cohort, **2
were selected on a stale-bar `early_volume`** and would not have survived the
fixed floor (both days had zero fail-soft restores, so neither would have
returned to the slate):

| entry | ticker | `early_volume` shown to judge | reality | realized |
|---|---|---|---|---|
| 2026-07-31 | HUT | 2,053 | 0 prints | +12.9% |
| 2026-08-04 | TGT | 1,586 | 0 prints | -11.3% |

(GCT 2026-08-07 is the third such pick; not yet in the ledger at time of writing.)
The other 5 (ABT, CVS, AMZN, CSCO, FIG) had fresh bars and are unaffected. Net
P&L effect of the two is roughly a wash — this is a selection-integrity question,
not a returns question, and should not be decided on those two numbers.

**Argument to RESET:** selection inputs were corrupted on stale-bar days, the
primary floor was inert for the entire cohort, and the judge's liquidity
directive was inverted. What ran since 07-29 was never the policy
`gammarips-review` approved on 07-28 — it was v1_1 *minus* its primary floor.

**Argument to CONTINUE:** the fix restores intended v1_1 behavior rather than
changing policy, N=7 is small enough that a reset costs little information, and
the affected picks are individually identifiable and can be annotated in place.

Either way the two rows above should be annotated in `forward_paper_ledger`.
**Ledger annotation is a write and is NOT executed** pending the owner's call on
this section.

## Rollback

- `PRINT_FLOOR_ENABLED=false` -> bit-identical pre-2026-07-28 single-tier OI floor.
- `PRINT_VALID_AFTER_ET_MIN=1441` -> date validation never asserts a zero
  (every stale bar becomes UNKNOWN / fail-open), i.e. pre-2026-08-07 floor
  behavior without reverting code.
- `JUDGE_PROMPT_VERSION=8` + `JUDGE_PROMPT_LABEL=tournament_v1_1` -> prompt revert.

## Tests

- `signal-notifier/tests/test_print_floor.py` (16) — fresh / stale / missing-day
  / fetch-error / pre-open guard / undatable bar; floor integration (known-zero
  dropped, UNKNOWN kept, fail-soft marks the row, all-zero slate still returns
  candidates); email-line honesty incl. a GCT-shaped fixture asserting a
  zero-print contract can never render "(confirmed)".
- `signal-judge/tests/unit/test_prompt_v1_2.py` (8) — byte-diff vs the stored
  v1_1 golden, both additions present exactly once and correctly anchored,
  provenance bumped, deploy.sh pins match code defaults.

Both suites pass: `.venv/bin/python -m pytest signal-notifier/tests
signal-judge/tests/unit/test_prompt_v1_2.py -q` -> 24 passed.
