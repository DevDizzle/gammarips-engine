# 2026-07-28 — Tournament liquidity upgrade: 09:52 cron, early-print slate floor, judge liquidity fields, prompt tournament_v1_1

**Status: CODE LANDED — deploy + cron move pending `gammarips-review`.**

## Problem

The tournament keeps delivering picks that cannot be traded. Owner real-money
kill on UNP 260821C310 (6 contracts all day, ~30% effective spread) despite the
live-OI>=1000 floor passing it. The entry-day tradeability study (15 days,
N=750, FINDINGS_LEDGER "2026-07-28 (evening)") quantified why OI alone cannot
close the gap: **OI>=1000 still leaves 23.9% of contracts under 50 entry-day
contracts.** The near-deterministic predictor is the entry-day print count read
early: at the ~09:52 snapshot (Polygon 15-min-delayed feed = prints through
~09:37), **>=5 prints -> 96.3% finish the day tradeable (>=50 contracts);
>=20 -> 100%; 0 prints (52% of the pool) -> 68.1% under-50 / 40.6% ghost.**
A 0-print veto would have blocked the owner's UNP entry.

## Delayed-feed mechanics + the cron move (09:45 -> 09:52 ET)

The notifier already fetches per-contract live data at pick time
(`_fetch_live_oi` -> `(live_oi, today_volume, status)`), but at the current
09:45 cron the 15-min-delayed feed shows **nothing** for the entry day —
`today_volume` is ~always 0/None, so the print signal is unreadable. At 09:52
the feed turns real (prints through ~09:37). The cron therefore moves
**09:45 -> 09:52 ET post-deploy** (Cloud Scheduler change, NOT in this code
change). **Sequencing hazard:** if the new code deploys while the cron is still
09:45, the print floor sees zeros everywhere and fail-soft restores a top-live-OI
slate (behavior degrades to roughly the old floor, emails say UNVERIFIED) — so
the deploy and the cron move must land in the same change window, or deploy
with `PRINT_FLOOR_ENABLED=false` until the cron moves.

## What changed (code)

1. **Two-tier slate floor** (`signal-notifier/main.py::_liquidity_refresh_and_rank`):
   - **PRIMARY — early-print floor**: drop candidates whose `_today_volume` is
     a KNOWN int `< PRINT_FLOOR_MIN` (default 1: a known-0-print contract is
     dropped). `None` (fetch failure/timeout) = UNKNOWN -> the row is KEPT and
     falls through to the OI floor — **fail-open per-row**, mirroring the
     existing live-OI failure semantics (C4).
   - **SECONDARY — live-OI floor**: `effective_oi < OI_FLOOR` drop, applied
     exactly as before (live env value 1000).
   - **Fail-soft floor**: if fewer than `TOURNEY_MIN` (8) survive BOTH floors,
     dropped candidates are restored ranked by `(today_volume desc NULLS LAST,
     live_oi desc NULLS LAST)` up to `TOURNEY_MIN` — the tournament never
     starves. Restored rows carry an internal `_print_floor_restored=True`
     marker (popped before `/rank`; surfaced only in the operator email).
   - Loud logging: zero-print-dropped tickers+count, fail-soft-restored
     tickers+count, one-line before/after summary.
   - Kill switch `PRINT_FLOOR_ENABLED=false` runs the legacy single-tier
     OI-floor block **bit-identically** (pre-2026-07-28 behavior).
     `LIQUIDITY_TILT=false` still short-circuits everything (pre-2026-06-25).
2. **Judge candidate JSON enriched** (`_candidate_for_ranker`): three fields,
   each OMITTED when unknown:
   - `early_volume` — sanctioned wire alias of the internal `_today_volume`
     (raw key still popped + judge-blocklisted).
   - `oi_build` — `live_oi - recommended_oi` (overnight OI change; only when
     both known). `recommended_oi` itself stays judge-blocked (stale snapshot)
     — the delta is the tradability signal (study: OI-up vs flat/down =
     INVALID_LIQUIDITY 3.0% vs 21.5%).
   - `expected_liquidity` — the scan-time CLEAN/THIN verdict from the enriched
     row (2026-07-28 pool-tradeability build; first populated by tomorrow's
     05:30 enrichment). Added to the notifier pool SELECT; NULL rows omit the
     key.
3. **Prompt `tournament_v1_1`** (`signal-judge/app/agent.py::_build_prompt`):
   ONE added instruction — "Candidates may include early_volume ..., oi_build
   ..., and expected_liquidity (CLEAN/THIN). A pick that cannot be traded is a
   loss regardless of thesis: among comparable setups, prefer the one showing
   real early trading activity." Otherwise byte-identical. Provenance:
   `JUDGE_PROMPT_VERSION` 7 -> **8**, `JUDGE_PROMPT_LABEL` `tournament_v1` ->
   **`tournament_v1_1`** (deploy.sh env pins updated — prod pins these via
   `--set-env-vars`, the code default alone is inert). Verified read-only that
   no version-8 rows pre-exist in `signal_ranker_runs`, so 8 cleanly labels the
   v1_1 cohort in eval traces.
4. **Operator email**: one liquidity line under the entry/limit block —
   `Liquidity: {n} prints by ~09:52` + `(confirmed)` at >=5, `(CAUTION - thin
   tape)` at 1-4, `UNVERIFIED - restored by fail-soft floor` when the pick only
   exists because fail-soft restored it, `UNVERIFIED - live print count
   unavailable` when the pick's own fetch failed (kept fail-open). No line on
   FALLBACK runs (`LIQUIDITY_TILT=false`). Review amendment A2: under
   `PRINT_FLOOR_ENABLED=false` alone the refresh still runs, so the email line
   STILL renders (and the judge still receives the three fields) — the kill
   switch reverts the SLATE only.

## Leakage posture

`early_volume`/`oi_build` are **pre-entry** information: read ~09:52, prints
through ~09:37, entry 10:00 — the same leakage class as the already-permitted
`live_oi` (2026-06-25 decision). The C1 discard of every other live snapshot
field (IV/greeks/day OHLC/last trade/quote), the C3 `_FORBIDDEN_LIVE_KEYS`
assert, and the judge-side `STALE_FIELDS_BLOCKLIST` all stand unchanged; only
the sanctioned aliases pass. `expected_liquidity` is scan-time (05:30), fully
point-in-time. Nothing touches `forward_paper_ledger` writes (C5) — the new
fields live only in the candidate dicts, `/rank` payload, and logs.

## Caveats

- **Thresholds are 15-day IN-SAMPLE fits** (scans 07-06..07-24). The >=5 /
  0-print cuts were selected on the same data that scored them. Re-fit rolling
  as `pool_liquidity_snapshot` accrues; `PRINT_FLOOR_MIN` is env-tunable.
- Deploy-order dependency: the notifier pool query now SELECTs
  `expected_liquidity`, which is ALTER-added by the enrichment-trigger DDL
  (pool-tradeability build, same night). enrichment-trigger must deploy and run
  (05:30) before the notifier's 09:52 query, or the query 400s and the day
  fail-closes.
- Email lands later: notifier end-to-end POST / latency over the last 13 runs
  is 56-175s (median ~78s) — at a 09:52:00 start the email lands ~09:53-09:55,
  inside the 09:58 bound.
- **Cohort-reset adjudication is an OPEN ITEM for `gammarips-review`**: this
  change alters the slate (drops) and the judge's information set. Precedent
  (2026-06-25 live-OI floor) reset the cohort. `policy_version` /
  `LIVE_COHORT_START_DATE` are deliberately NOT changed here.

## Rollback (review amendment A3 — the honest version)

Rollback is degradation-shaped in every combination (never fail-closed), but it
is NOT residue-free, and two orderings are FORBIDDEN:

- **Slate**: `PRINT_FLOOR_ENABLED=false` (env) -> bit-identical pre-2026-07-28
  SLATE. Residue: the refresh still runs, so `early_volume`/`oi_build`/
  `expected_liquidity` still reach the judge and the email line still renders.
  Full judge-input rollback additionally requires `LIQUIDITY_TILT=false` (which
  also reverts the 06-25 OI floor) or a code revert.
- **Cron**: NEVER revert 09:52 -> 09:45 while the print floor is enabled — at
  09:45 the delayed feed shows known-0 everywhere, mass-dropping the slate into
  a fail-soft restore. Pair any cron revert with `PRINT_FLOOR_ENABLED=false`.
- **Judge prompt**: env-reverting `JUDGE_PROMPT_VERSION=7` alone is FORBIDDEN —
  the v1_1 prompt line is unconditional in code, so the env revert would
  mislabel v1_1 runs as version 7 and pollute provenance. Correct judge
  rollback = git revert + redeploy of signal-judge (env pins follow the code).
- **Cohort**: the 07-29 `LIVE_COHORT_START_DATE` reset is a constant revert +
  DECISIONS note if ever undone; no data was truncated.

## Cohort reset (review adjudication, owner may override)

`LIVE_COHORT_START_DATE` reset `2026-06-26` -> `2026-07-29` (first entry under
the new selection). Rationale: exact 06-25 precedent (a smaller change reset
the cohort); the pre-upgrade cohort's ghost-contract sim fills are exactly what
the tradeability study discredited; N=22 is cheap to restart; prompt-version 8
gives a clean research join either way. UNLIKE 06-25: NO truncation — the 22
prior rows remain in `forward_paper_ledger`, excluded by the date filter
(archival over deletion). `policy_version` unchanged (`V7_1_TILTED_GIGO`).
