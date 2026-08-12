# 2026-08-12 — The fail-soft restore can never produce the pick

**Status:** implemented, NOT yet deployed (review gate + owner call pending)
**Services:** `signal-notifier`, `signal-judge`
**Supersedes the restore half of:** `2026-07-28-tournament-liquidity-upgrade.md`
**Triggered by:** trader handoff `docs/research_reports/handoffs/2026-08-12-tournament-liquidity-regression.txt`
**Closes:** GAP-021 (fail-soft floor masks the thinnest contract in the pool)

## What happened

The 2026-08-07 day-bar date-validation fix worked, and that is what broke the pick.

Before it, the early-print floor was a structural no-op (Polygon never serves a
zero-volume day bar, so a known zero could not exist). After it, the floor fires:
5-6 of 12 candidates get dropped on a normal morning. That trips the fail-soft
floor, which restores dropped candidates up to `TOURNEY_MIN=8` "so the tournament
never starves to zero" — and `_print_floor_restored` was **popped before `/rank`**.

So the judge was handed a slate that was mostly rejects, with no way to tell which
ones, and it selected them roughly in proportion to how much of the slate they
were. Production logs, 2026-08-12:

```
Early-print floor: dropped 5/12 ['MPC','PSX','BX','EMR','AEO']
Fail-soft floor:   only 4/12 cleared both floors; restored 4 ['MDB','AEHR','QMCO','EMR']
Two-tier slate:    ['P','BRK.B','KKR','OWL', MDB, AEHR, QMCO, EMR]   <- judge picked MDB
```

MDB `O:MDB260821C00470000` quoted bid 4.70 x15 / ask 7.40 x144 at 09:59 — a 44.6%
spread, the worst ever measured on a pick — and the rationale read "an
early_volume of 102 and an oi_build of 202 to securely execute". The judge was not
lying; it was blind. Same mechanism on 08-11 (ALC, 26.1% spread, owner entered,
-$312) and, one link back, the same fix chain that produced 08-07 GCT.

`TOURNEY_MIN` was a floor on slate SIZE with no corresponding floor on slate
QUALITY. "The tournament never starves to zero" reads like a reliability property.
It is a correctness bug: it guarantees an output when the correct output is an
empty set.

## Decision

1. **`FAILSOFT_RESTORE_MODE` (new, default `none`).** A candidate that failed
   either liquidity floor never returns to the slate, so it can never become the
   pick. `empty_only` restores up to `TOURNEY_MIN` only when zero cleared;
   `always` is the pre-08-12 behavior, kept purely as a no-redeploy rollback
   lever. An unrecognized value logs an error and falls back to `none` — a typo
   fails to the safe mode, not the defective one.
2. **A no-pick day is a valid output.** When the floors run to completion and
   nothing clears, the slate is empty and the notifier fails closed with
   `skip_reason="no_liquid_candidates"`, carrying the counts
   ("0 of 12 candidates cleared … print-floor dropped 5, OI-floor dropped 3").
   `TOURNEY_MIN` is now a soft target that sizes the restore in the two
   non-default modes and nothing else.
3. **The flag reaches the judge** as the sanctioned alias
   `liquidity_floor_restored` (same idiom as `early_volume`/`_today_volume`: raw
   key popped + blocklisted, alias on the wire). Prompt bumps to
   `tournament_v1_3` / version 10 with one added sentence: never rank a restored
   contract above one that cleared. This is the SECOND wall — under the default
   mode nothing is restored and the field is False on every row. It exists for
   the rollback modes, where the deterministic exclusion is off.
4. **A restored row can never render "(confirmed)".** The 08-11/08-12 cards said
   `N prints by ~09:52 (confirmed) (restored by fail-soft floor)` — an
   attestation next to its own refutation, on the card the operator traded. Every
   restored branch now names the floor it failed and says NOT confirmed. The
   dropped-floor identity is recorded at drop time in `_floor_failed`.

## The interlock that makes an empty slate safe

`_liquidity_refresh_and_rank` returns `(slate_df, stats)` and the caller emits a
no-pick day **only** when `_is_no_liquid_candidates(df, stats)` is True, which
requires `stats["measured"]`.

**`measured` requires EVIDENCE, not the absence of a crash.** The first version
of this change set it at the end of a completed two-tier run, and
`gammarips-review` BLOCKED on the hole that leaves. A total Polygon failure does
not raise: `_fetch_live_oi` returns `(None, None, "polygon_error")` per row and
`_refresh_live_oi_batch` try/excepts each future, so the batch **completes** with
`live_oi=None` everywhere. The print floor then drops nothing (`None` is UNKNOWN,
fail-open per row) and the live-OI floor silently judges the whole slate on
**frozen scan-time `recommended_oi`** against `OI_FLOOR=1000`. Scan-time OI runs
far below live OI on this pool by construction — the 08-07 fixture is 44 frozen
against 2,077 live, and `oi_build` exists because overnight build is large — so a
blind read can sweep the slate to zero and publish "nothing was tradeable" when
nothing was measured. That is the worst artifact shape in the doctrine: it
reconciles perfectly against its own numbers and is false. `no_liquid_candidates`
is read verbatim as a slug by MCP agents, so the false claim propagates.

`LIVE_FETCH_MIN_OK_FRAC` (default 0.5) closes it. A run that gets live OI for
fewer than half the slate is DEGRADED: it returns the input pool untouched,
leaves `measured` False, and never lets a stale frozen-OI read drive selection.

Five paths leave `measured` False, and **none of them can return an empty slate**:

| Path | `stats` marker |
|---|---|
| exception anywhere in the floor | `error` |
| `LIQUIDITY_TILT=false` | `skipped` |
| empty input pool | `skipped` |
| `PRINT_FLOOR_ENABLED=false` (legacy path) | `legacy_path`, own fail-soft |
| live read answered for < `LIVE_FETCH_MIN_OK_FRAC` of the slate | `degraded` |

Fail-soft still means fail-soft on ERROR. What changed is that a *measured*
"nothing here is tradeable" is now allowed to say so.

## Measured impact

Two runs of `scripts/tests_and_diagnostics/dryrun_print_floor_datevalidated.py
--days 21` over the same 15 sessions (2026-07-23 -> 2026-08-12), replayed against
`pool_liquidity_snapshot`. The runs differ ONLY in `FAILSOFT_RESTORE_MODE`, and
both were taken at `OI_FLOOR=1000` to match production. Raw stdout of both,
header lines included, is at
`docs/research_reports/handoffs/2026-08-12-replay-output.txt`.

| | before (`mode=always`) | after (`mode=none`) |
|---|---|---|
| zero-print names handed to the judge | **15 total**, 7 of 15 sessions, max 6/session | **0** |
| fail-soft restores | 2.5/session | 0 |
| slates padded below `TOURNEY_MIN` | 10 of 15 sessions | n/a, the pad is gone |
| genuine survivors on the slate | mean 5.7 of 12 | mean 5.7 of 12 |
| sessions with zero survivors | 0 (padded away) | **1 of 15 (2026-07-24)** |

The first version of this note quoted "up to 6/session across 8 of 15 sessions"
for the before column. That number came from an older replay, not from a paired
run, and it was wrong on the session count. The script now prints
`FAILSOFT_RESTORE_MODE` and `OI_FLOOR` in its header, so a pasted run is
checkable against the settings that produced it.

It is not free: roughly one session a month becomes a no-pick day. That is the
point of the change, not a side effect.

## Consequences / follow-ups

* **Engine-only change — no web surface renders the new reason.** `no_liquid_candidates`
  flows Firestore `todays_pick` -> `forward-paper-trader` skip row (`main.py` ~693)
  -> `gammarips-mcp` `performance_tracker`, where agents read it as a slug. The
  webapp component that maps skip reasons to copy
  (`landing/todays-pick-card.tsx`, `SKIP_REASON_COPY[...] ?? raw`) is imported by
  **nothing** — orphaned by the 2026-07-03 depicking. It reads like a live public
  pick card and is not one; if it is ever touched, delete it rather than update
  it ("No pick, anywhere"). Keep new slugs self-describing: an agent reads them
  verbatim.
* Cohort: **RESET to `2026-08-13`** (owner call 2026-08-12, after
  `gammarips-review` challenged the original no-reset call). The first version of
  this note argued no reset because "exit mechanics unchanged, policy_version
  stays `V7_1_TILTED_GIGO`". That reason does not separate this case from the
  precedent: it was equally true on 07-28 and 08-07, and both reset. The
  criterion that actually applies is the one written on 08-07, in the same words
  — **the deployed policy was never the approved policy**. The 08-10 cohort held
  3 entries and 2 of them (ALC 08-11, MDB 08-12) were fail-soft restores that the
  new code cannot select. Only PLTR 08-10 was a genuine survivor.
  No truncation: the rows stay in `forward_paper_ledger`, excluded from the
  public cohort by the date filter. `policy_version` is unchanged.
* **The cohort constant is mirrored in four places and only two are in this
  repo.** Updated here: `signal-notifier/main.py` and
  `libs/gammarips_content/gammarips_content/cohort.py` (pinned together by
  `libs/gammarips_content/tests/test_cohort_pin.py`). **Still stale until they
  are updated and redeployed:** `gammarips-mcp/src/utils/data.py` (separate repo,
  own review gate) plus the prose in its `historical.py` and
  `performance_tracker.py`, and the x-poster / blog-generator services, which
  vendor the lib at DEPLOY time and so keep 2026-08-10 until they are redeployed.
  Until then the paid MCP surface reports a cohort start that includes ALC and
  MDB while the engine does not. That drift is exactly the 08-07 defect this pin
  test exists to catch, and it is open on purpose, not by oversight.
* **Four resets in seven weeks** (06-25, 07-28, 08-07, 08-12) and the public
  panel has never held more than about 7 closed trades. Each reset is
  individually correct and the pattern still has a real cost: the public track
  record cannot accumulate N. The way out is to stop changing selection in small
  increments, not to skip a warranted reset.
* The FALLBACK gate path (`POLICY_GATE_FALLBACK`) still bypasses the liquidity
  floor entirely — `_liquidity_refresh_and_rank` runs only on STRICT days. Same
  defect class, not addressed here; see the open-engineering note.
* Root cause of all of it is still P3, unfixed and not a code change: **nothing
  in the pipeline measures spread or dollar depth.** OI and print count are
  proxies for the question "can a subscriber get out", and MDB passed both
  proxies at a 44.6% spread. `RM-001b` (quote entitlement) is an owner spend
  decision. Until it lands, the engine is guessing.

## Files

* `signal-notifier/main.py` — `FAILSOFT_RESTORE_MODE`, `(df, stats)` return,
  `_floor_failed`, `liquidity_floor_restored` alias, `no_liquid_candidates`
  branch, `_liquidity_email_line` honesty, `skip_detail` on the standby message
* `signal-judge/app/{agent,schemas,tools}.py`, `deploy.sh` — `tournament_v1_3`
* `signal-notifier/tests/test_print_floor.py` (37 tests),
  `signal-judge/tests/unit/test_prompt_v1_3.py` (11 tests)
