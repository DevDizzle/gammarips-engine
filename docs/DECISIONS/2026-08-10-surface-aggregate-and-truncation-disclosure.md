# 2026-08-10 — `view="surface"`: aggregate mode, truncation disclosure, verified frontier

**Status:** decided, implemented, tested. Deploy of `gammarips-mcp` is the owner's call.
**Scope:** `gammarips-mcp` (`src/tools/substrate.py`, `src/tools/v4.py`, `tests/test_v3_smoke.py`)
and `gammarips-engine` (`dbt-runner/digest.py`). No execution-policy change, no trading
surface touched, no gate added to any service.
**Trigger:** `docs/research_reports/handoffs/2026-08-10-trader-handoff-response.md`
(reply to the trader harness's P1-P4 handoff).

## Context

The consumer harness asked for an aggregate mode on `view="surface"` because the row
payload (104,805 characters for 200 rows) exceeded its tool-result ceiling. Implementing
it surfaced a larger defect underneath the one reported.

## What was actually wrong

`get_opportunity_surface` ran `ORDER BY scan_date DESC, opp_peak_return DESC LIMIT 200`
and returned `row_count: len(rows)` with no indication a cap had been hit. Measured on
2026-08-10, a `days=30` call **matched 791 rows across 17 scan dates and returned 200
across 5**.

The bias matters more than the loss. Because the secondary sort is peak DESC, the cut
lands mid-`scan_date` and the oldest returned date contributes only its highest-MFE rows:

| | n | scan dates | mean MFE | median MFE | median MAE |
|---|---|---|---|---|---|
| returned | 200 | 5 | 0.6278 | 0.3416 | -0.3464 |
| full set | 791 | 17 | 0.4470 | **0.2341** | -0.3660 |

Median MFE overstated **46%**, mean **40%**, MAE effectively unchanged. Truncation
inflated the upside and left the downside intact, so the opportunity surface read
systematically better than it is, on the monetized surface, feeding the consumer's exit
design. This is the "partial output that reconciles perfectly against its own numbers"
failure mode, which is the one we treat as worst.

Separately, `delta_min`/`delta_max` were accepted by `query_outcomes` and silently
dropped for this view.

## Decision

1. **`aggregate_only=True` on `view="surface"`**, mirroring `view="labels"`. MFE/MAE
   p10/p25/p50/p75/p90 + mean, n, `n_with_surface`, distinct scan dates, date range,
   `opp_sim_versions`, median minutes-to-peak/trough. Computed in BigQuery over the full
   filtered set, so it is structurally immune to the row cap. ~1.8KB.
2. **Row mode declares its own incompleteness**: `matched_rows`, `truncated`,
   `partial_scan_date`, `meta.row_cap`, and a note that names the date to drop. The
   matched count rides on the row query via `COUNT(*) OVER ()` rather than a second
   query, so the count and the rows come from one snapshot.
3. **`delta_min`/`delta_max` plumbed through**, on `ABS(recommended_delta)`.
4. **A `frontier` block** that explains why `max(scan_date)` lags today.

## The frontier block must verify, not assert

The first implementation hardcoded "This is not a stalled job." `gammarips-review`
blocked it, correctly. `WINDOW_OPEN` means the window had not closed **at label time**;
a row keeps that status forever if the fill job stops. `FINDINGS_LEDGER` records exactly
that: the opportunity-surface labeler stalled from 2026-06-26 leaving 950 rows (24.1%)
`WINDOW_OPEN` although every window had closed. The reassuring string would have told a
paying consumer, inside the product payload, that a dark surface was fine. That is the
freshness-canary failure mode ("could not determine" rendering as "fine") shipped into
the revenue surface.

The block now derives, per pending row, whether the window *should* have closed:

- **Session calendar** = the table's own `DISTINCT entry_day` values (the engine emits a
  pool every trading day). No new table dependency, no hardcoded holiday list.
- **Closure predicate** mirrors the producer's
  (`get_nth_next_trading_day(entry_day, n-1) < today_et`): closed once
  `opp_window_days - 1` sessions have elapsed strictly between `entry_day` and today.
- **Pending** = `WINDOW_OPEN` **or NULL**, the same definition the engine's dbt freshness
  test uses. Terminal statuses (`NO_BARS`, `NO_POST_ENTRY_BARS`, ...) are
  resolved-as-unusable, not a stall, and appear in a `status_counts` histogram instead.
- **Three outcomes, never conflated:** `open_past_due == 0` earns the reassuring note;
  `> 0` reports a probable stalled fill job; a stale session calendar returns `null` and
  the note says UNVERIFIED.
- Scoped to the **date window only**, never the delta/ticker filters, so a narrow band
  cannot make an empty result look like a lagging frontier.
- **Fail-soft**: the block is explanatory, so a failure degrades to
  `frontier: {"status": "unavailable"}` rather than failing the whole tool.

Validated 2026-08-10: 791 OK rows all have closed windows, 150 `WINDOW_OPEN` rows are all
genuinely still open, `open_past_due` = 0. Perfect separation, which is what gives
confidence the predicate matches the producer's.

## Other review findings folded in

- Statistics guarded with `IF(opp_status='OK', ...)` and `n_with_surface` reported
  separately. `WINDOW_OPEN` rows carry NULL in every opp_* **value** column (never
  partial), so with `include_open=True` an unguarded `COUNT(*)` reported an `n` the
  quantiles were never fitted to: the same defect class, reintroduced inside its own fix.
  Note `opp_window_days` and `opp_sim_version` ARE populated while a window is open, so
  neither can be used to test closure.
- `_COMPOSITE_DISCLAIMER` appended. Every peer aggregate on this substrate carries it and
  the new one did not, while being the densest number block on the paid surface.
- `opp_sim_versions` pinned, so a multi-version table cannot pool silently.
- `excluded_null_delta` reported: a NULL delta cannot satisfy either bound, so banding
  silently shrinks the population.
- **`utils.safety.clamp` is int-by-contract** (`int(value)`). Routing delta bounds through
  it collapsed 0.20 to 0 and silently emptied the band. Deltas use a local float
  validator; do not "simplify" that back to `clamp()`. This one was caught by testing the
  fix, not by reading it.
- Fresh `QueryJobConfig` per query (a `QueryJob` references the config's `_properties`
  rather than copying).
- `partial_scan_date` is `null` when every returned row shares one `scan_date`, since
  "drop it first" would empty the sample; the note says narrow the query instead.

## Engine side: `dbt-runner/digest.py`

The "Table freshness" badge read dbt's exit code (only `error_after` is non-zero) while
the list beneath it showed every source past `warn_after`. Ten WARN sources therefore
rendered under an OK header, and a consumer following the documented pool-trust rule
could not tell whether it had fired. Rows now carry severity, ERROR rows are grouped and
labeled as what makes the section red, and a warns-only section prints why it is still OK
at the point of confusion. Guarded on the badge (`fresh["status"] == OK`), not merely on
the absence of errors, so the explanation can never print under a red badge.

## Consequences

- Any base rate computed from a `view="surface"` **row-mode** pull before this change is
  inflated twice over: once by the known 10:00 anchor defect, again by ~46% at the median
  from truncation. Re-derive from `aggregate_only`, or from pulls returning
  `truncated: false`.
- Query count per call: row mode 2 (frontier + rows), `aggregate_only` 2, and **3 when a
  delta band is passed** (the `excluded_null_delta` count). Was 1 before this change.
  `enriched_option_outcomes` is partitioned on `entry_day` and every filter here is on
  `scan_date`, so **none of these prune a partition** and `days` buys no cost control.
  `query_outcomes` has no dedicated rate-limit bucket. Verified on the live revision at
  deploy time: `REQUIRE_API_KEY=true` and `AUTH_SHADOW=true` (shadow is deliberately kept
  so a REQUIRE_API_KEY rollback degrades to shadow rather than fully open — memory
  `auth-shadow-flag-is-deliberate`). So this is pro-tier traffic only, which is also what
  keeps the frontier block's pipeline-health telemetry ("this looks like a stalled fill
  job") off the anonymous surface. Left as-is, logged here.
- **Not audited:** the same undeclared-cap shape likely exists in `view="labels"`,
  `positions`, and `signal_performance`. `labels` at least discloses
  `pool_rows_in_window`. Follow-up.

## Definition of Done

Item 1 (30-day forward paper validation) is **not applicable**: no execution-policy or
strategy change, no gate, no selection or exit mechanics touched.

Item 2 `gammarips-review`: run **twice**, DO-NOT-SHIP both times.

- Pass 1 blocked on four items: the frontier note asserting "this is not a stalled job"
  without checking, a `WINDOW_OPEN`-only status count blind to the NULL outage signature,
  a missing composite disclaimer, and `include_open=True` inflating `n` above the
  population the statistics were fitted to. Plus highs on sim-version pooling, silent
  NULL-delta exclusion, the frontier inheriting the caller's delta filter, and the
  explanatory query being a hard dependency.
- Pass 2 blocked on three defects introduced or left behind BY those fixes:
  `excluded_null_delta` counted over the date window instead of the call's own
  population; `opp_sim_versions` left unguarded; and the "all opp_* are NULL when open"
  claim being false (`opp_window_days` and `opp_sim_version` are written on open rows).
  Plus a medium: the calendar-completeness assumption behind the word "Verified", and
  `calendar_stale` defaulting NULL to "fine".

The recurring shape is worth naming: **three separate times, a fix for a
"partial output that reconciles against itself" defect introduced another one.** The
disclosure number computed over the wrong population is the same bug as the truncated
sample that started this. Assume the next one is there too.

Items 3 and 4: this note, `README.md` in the MCP repo, and the `v4.py` tool docstring.
Smoke coverage added for truncation disclosure, aggregate shape, frontier verification,
and delta-band validation; an induced assertion failure confirmed the new checks
actually execute rather than passing vacuously.
