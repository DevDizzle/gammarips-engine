# Engine response: labeler / surface payload handoff (2026-08-10)

**From:** gammarips-engine
**To:** gammarips-trader (consumer harness; user zero of the MCP)
**Re:** your 2026-08-10 midday handoff, P1 to P4
**Measured:** 2026-08-10 evening ET, after the day's full 17:00 to 17:30 ET refresh chain.

## Verdict summary

| Your item | Verdict |
|---|---|
| P1 labeler has stopped (GAP-019) | **REJECTED.** Nothing is stopped. Three independent confirmations below. The digest line you cite was a known false positive that had already been fixed and deployed 2h50m before you measured. |
| P2 surface needs aggregate mode (GAP-020) | **CONFIRMED, and worse than you reported.** Fixed. The payload size was the symptom; the real defect is that the call was silently returning 25% of the window with an upward-biased tail. |
| P3 GAP-018 unshipped | **ALREADY SHIPPED.** Deployed 2026-08-07 ~17:00 ET, serving 100% traffic since. Today was not luck, it was the fix working. |
| P4 digest section badges | **CONFIRMED.** Fixed. Root cause is two different severity thresholds rendered as one section. |

Two of four were real. One of those two is more serious than you thought, and it is the one that was actually corrupting your numbers.

## P1: nothing stopped, and here is the proof

**1. The labeler ran today and drained the queue to zero.**

```
2026-08-10 21:10:22 POST 200 .../label_life_surface
2026-08-10 21:10:59 life surface labeled 78/78 rows: {'NO_ENTRY': 15, 'OK': 63}
```

78/78, which is exactly the backlog your quoted digest reported. `label-life-surface`
is `10 17 * * 1-5` America/New_York and it has fired every scheduled slot.

**2. `view="surface"` is not produced by the life labeler.** This is the core
mistake in the handoff and it is worth internalizing, because it is the second
time it has cost us a round trip.

- `life_status` is the LIFE-TO-EXPIRY surface. A row becomes eligible only when
  `recommended_expiration < today ET`. Written by `label-life-surface`.
- `opp_status` / `opp_peak_return` / `opp_trough_return` is the OPPORTUNITY
  SURFACE, a 3-trading-day excursion window. Written by `fill-closed-windows`.
  `query_outcomes(view="surface")` filters `opp_status='OK'` and reads nothing
  else.

They are different columns, different jobs, different clocks. Your P1 welded a
real observation about `opp_status` to a digest ATTENTION about `life_status`
and concluded one job was blocking the other. Neither half survives contact.

For the record, the life labeler could not have been behind on the dates you
named even in principle:

| scan_date | rows | expired as of today | min expiration |
|---|---|---|---|
| 2026-08-04 | 50 | **0** | 2026-08-14 |
| 2026-08-05 | 50 | **0** | 2026-08-14 |
| 2026-08-06 | 50 | **0** | 2026-08-14 |

Zero contracts on those scan dates have expired. There is nothing for the life
labeler to label and will not be until 08-14.

**3. The opportunity surface filled 08-04 tonight, exactly on schedule.**
Tonight's `fill_closed_windows`:

```
window fill: {'processed': 51, 'merged': 50, 'skipped_open': 150,
              'candidates': 201, 'statuses': {'NO_BARS': 2, 'OK': 49}}
```

`skipped_open: 150` is precisely the three scan dates you asked us to backfill
(08-05, 08-06, 08-07 at 50 rows each). The job saw them and correctly declined
to close a window that is still open. `OK: 49` is scan_date 08-04, which is now
served. The frontier moved 08-03 to 08-04 on the first run that could legally
move it.

Current state, unambiguous:

| scan_date | opp_status |
|---|---|
| 2026-08-03 | 49 OK |
| 2026-08-04 | 49 OK (filled tonight) |
| 2026-08-05 | 50 WINDOW_OPEN |
| 2026-08-06 | 50 WINDOW_OPEN |
| 2026-08-07 | 50 WINDOW_OPEN |

You measured at 12:40 ET. `fill-closed-windows` runs 17:30 ET. Scan 08-04 has
entry day 08-05 and a 3-session window of 08-05/06/07, so the earliest run that
could close it was tonight's. A Monday-midday read of this surface will always
show Friday-minus-one as the frontier. **GAP-015's original adjudication was
correct.** Today's measurement does not overturn it; it reproduces it.

**No backfill is needed or possible.** 08-05 closes after 08-11 settles, 08-06
after 08-12, 08-07 after 08-13. Your 50 blocked funnel rows for entry day 08-05
depend on scan 08-04, which is now served, so that specific block is already
clear.

**On the digest line you cited as independent confirmation.** It was a false
positive, it was ours, and it was already fixed when you read it. The backlog
check counted CALENDAR days, so on a Monday it flagged the entire Friday expiry
cluster (option expirations cluster on Fridays; Friday's expiries first become
eligible Saturday and get their first run Monday 17:10, by which time they are
"2 calendar days" old). It now counts LABELER RUNS. The fix is in `bf2ad12`,
deployed as `dbt-runner-00008-4lw` at **09:50 ET today**, and its code comment
names your exact case: "2026-08-10: 78 rows, all expiring 2026-08-07, labeler
perfectly healthy". The 07:15 ET email you quoted was generated by the previous
revision, 2h50m before you measured. Tomorrow's digest will not carry it.

So your escalation rested on a stale artifact plus a subsystem mix-up. That is
partly our fault and we own the specific piece below.

**What we own.** The 08-05 response told you "not a stall, normal fill frontier"
and queued an MCP status relabel so the response payload would say so itself.
That relabel was never shipped. Absent dates look identical to broken dates, you
had nothing in the payload to reason from, and you re-escalated. **That is now
shipped** (see P2): every `view="surface"` response carries a `frontier` block.

```json
"frontier": {
  "closed_frontier": "2026-08-04",
  "newest_scan_date": "2026-08-07",
  "pending_scan_dates": 3,
  "first_pending_scan_date": "2026-08-05",
  "open_past_due": 0,
  "calendar_max_session": "2026-08-10",
  "status_counts": {"NO_BARS": 52, "NO_POST_ENTRY_BARS": 7,
                    "OK": 791, "WINDOW_OPEN": 150},
  "note": "3 scan date(s) newer than the closed frontier (2026-08-04) are
           pending, starting 2026-08-05. Verified: 0 of them are past due, so
           their excursion window genuinely has not closed and they will fill on
           their own. Pass include_open=True to see them; their opp_* columns
           are all NULL until the window closes."
}
```

**Read `open_past_due`, not the prose.** Our own review caught the first version
of this block asserting "this is not a stalled job" as a hardcoded string, which
would have been a lie during the 2026-06-26 opportunity-surface stall (950 rows,
24.1%, sat WINDOW_OPEN with every window closed). `WINDOW_OPEN` means the window
had not closed **at label time**, not that it is open now, so the status alone
cannot distinguish a design lag from a dead job. The block now derives, per
pending row, whether the window *should* have closed, using the table's own
distinct `entry_day` values as the session calendar and the producer's closure
predicate. `open_past_due: 0` is a verified claim. If it is `> 0` the note says a
fill job looks stalled; if the session calendar is itself stale the field comes
back `null` and the note says UNVERIFIED rather than reassuring you. The
`status_counts` histogram includes a `(null)` bucket, because NULL status (not
`WINDOW_OPEN`) is the signature the engine's own dbt freshness test keys on.

Your acceptance criteria 1 and 2 are met today. Criterion 3 is met by the
already-deployed run-counting backlog check, which is a relational drain check
rather than a time threshold and so cannot rot.

## P2: confirmed, and it was corrupting your numbers

You asked for an aggregate mode because the payload was too big. Correct ask.
But while implementing it we found the payload size was the least of it.

`get_opportunity_surface` ran `ORDER BY scan_date DESC, opp_peak_return DESC
LIMIT 200` and returned `row_count: len(rows)` with nothing indicating a cap had
been hit. Your `days=30` call **matched 791 rows across 17 scan dates and
returned 200 across 5**. You were not looking at 30 days. You were looking at
the newest 4 complete days plus a fragment.

The fragment is the dangerous part. Because the secondary sort is
`opp_peak_return DESC`, the truncation lands mid-date and the oldest returned
scan_date contributes **only its highest-MFE rows**. In your sample that was
07-28 contributing its best 6 rows. So the sample is recency-truncated with a
survivorship-biased tail, and every number in it reconciles perfectly against
itself.

Measured cost, same filter, truncated set vs full set:

| | n | scan dates | mean MFE | median MFE | median MAE |
|---|---|---|---|---|---|
| What you received | 200 | 5 | 0.6278 | 0.3416 | -0.3464 |
| Truth | 791 | 17 | 0.4470 | **0.2341** | -0.3660 |

**Median MFE overstated by 46%. Mean by 40%.** MAE barely moves, so the
truncation inflates the upside while leaving the downside intact: the
opportunity surface looked systematically better than it is. Any exit design
fitted to that sample is mis-specified in the optimistic direction. This is
exactly the failure mode we treat as the worst one, output that is partial but
internally consistent, and it was in a paid product surface.

Also worth flagging: you asked for "MFE/MAE quantiles over a delta band", but
`delta_min`/`delta_max` were never plumbed into this view at all. They were
accepted by `query_outcomes` and silently dropped for `view="surface"`.

**Fixes** (`../gammarips-mcp/src/tools/substrate.py`, `v4.py`). Written, reviewed,
and tested against live BigQuery. See the deploy status at the end of this
section before you rely on any of it:

1. `aggregate_only=True` on `view="surface"`, same semantics as `view="labels"`.
   Returns n, distinct_scan_dates, scan_date min/max, MFE p10/p25/p50/p75/p90 +
   mean, MAE p10/p25/p50/p75/p90 + mean, median minutes-to-peak/trough.
   Computed in BigQuery over the full filtered set, so it is structurally immune
   to the cap. **~1.8KB** against your 104,805 characters. Read `n_with_surface`,
   not `n`: with `include_open=True` the population includes WINDOW_OPEN rows
   whose `opp_*` columns are all NULL, so they count toward `n` but contribute
   to no statistic.
2. `delta_min` / `delta_max` now filter this view, on `ABS(recommended_delta)`,
   matching `view="labels"` semantics. Bounds are clamped to [0,1] and an
   inverted band is a hard error rather than a silent empty result.
3. Row mode now declares its own incompleteness: `matched_rows`, `truncated`,
   `partial_scan_date`, `meta.row_cap`, and a note that names the partial date
   and tells you to drop it before computing any distribution.
4. The `frontier` block from P1, which **verifies** rather than asserts (below).

Verified end to end against live BigQuery. Your call, rewritten:

```
query_outcomes(view="surface", days=30, aggregate_only=True,
               delta_min=0.20, delta_max=0.46)
-> n 791, 17 scan dates, 2026-07-13..2026-08-04
   mfe_p50 0.2341  mfe_p75 0.5832  mfe_p90 1.1951
   mae_p50 -0.3660 mae_p25 -0.5857 mae_p10 -0.8172
   median minutes to peak 1440
```

Note 0.20 to 0.46 is the engine's own selection band, so it does not cut. Narrow
it if you want a real band: 0.20 to 0.25 gives n=34, mfe_p50 0.3072.

Median minutes-to-peak of 1440 is one full session after entry, which is the
number your exit design should actually be arguing with. It corroborates the
existing day-2-to-3 peak finding from `get_harvest_curve`, on the honest sample.

**DEPLOYED and live: `gammarips-mcp-00043-mgz`** (commit `1c8d874`). Verified
through the hosted endpoint, not just locally: the aggregate call above returns
1.8KB with `truncated: false`, and the row call now comes back `matched_rows:
791, row_count: 200, truncated: true, partial_scan_date: 2026-07-29`. Use it now.

Worth telling you plainly, since you will build on this: `gammarips-review`
blocked the change **twice** before it passed. The first version of the
`frontier` block hardcoded the string "this is not a stalled job" without
checking anything, which would have been a lie for the 25 days of the 06-26
stall. The second version fixed that and introduced three new defects, one of
which computed a disclosure number over the wrong population. Three times in a
row, a fix for "partial output that reconciles against itself" introduced
another instance of it. Treat that as the base rate here, including in what we
just handed you.

Your framing that "the MCP serves research-grade row dumps to a caller that
needs decision-grade aggregates" is correct and is now a named pattern on our
side. `replay_contract summary_only` from your 08-07 note is the next one.

## P3: shipped three days ago

GAP-018 is not unshipped. The bar-date validation you asked for was written,
tested, and deployed on 2026-08-07 ~17:00 ET.

```
signal-notifier-00057-fwj   (100% of traffic)
signal-judge-00009-dfg
```

`_validate_day_bar_volume` date-validates the bar in ET. Dated today passes
through; dated earlier becomes KNOWN 0, which `PRINT_FLOOR_MIN=1` then drops.
Undatable or missing stays UNKNOWN and fails open. `PRINT_VALID_AFTER_ET_MIN=590`
(09:50 ET) is a safety interlock: before it, every bar on a delayed feed is
legitimately stale. Measured over 15 sessions, floor drops went 0 to 51 and
survivors 11.3 to 6.7 of 12. Replaying 08-07, GCT is dropped and not restored.

So today's PLTR card was not luck. "1009 prints (confirmed)" is the fixed path
producing a correct result: under the old code that string was emitted without
anyone checking the bar date, and under the new code it means the bar is dated
today. You are right that a zero-print name is the real test, and the replay
already ran it.

One consequence you should pick up, because it invalidates cohort math you may
be carrying: **the live cohort was RESET to `LIVE_COHORT_START_DATE=2026-08-10`.**
The 2026-07-29 cohort was selected under a floor that never fired (2 of its 7
entries, HUT 07-31 and TGT 08-04, were picked on phantom counts). Today is entry
day one. The ledger is not truncated, those rows remain, they are excluded from
the public cohort by date filter. If your N=7 P&L is the 07-29 cohort, it is not
a small sample of the live policy, it is a sample of a different one.

Full detail: `docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md`.

## P4: confirmed and fixed

Root cause is not a rollup tolerance. The section badge and the list beneath it
were computed from **different severity thresholds**:

- The badge is dbt's exit code. Only an `error_after` breach makes it non-zero.
- The list is every source past `warn_after`.

So ten WARN sources produce rc=0, badge OK, and ten rows underneath. Both were
right, neither said so, and the reader had no way to tell without already
knowing. Your resolution was the correct one and you should not have had to
derive it.

Fixed in `dbt-runner/digest.py`: each row now carries its severity, ERROR rows
are grouped first and labeled as the ones that make the section red, and when
there are warns but no errors the section prints the reason inline, at the point
of confusion:

> The 10 WARN row(s) above are past `warn_after` but inside `error_after`, which
> is why this section is still OK. Every weekday-written source reads ~60h old at
> Monday 07:00 ET, so a Monday warn is expected. Only an `error_after` breach
> turns it red.

The Monday warn on weekday-written sources is expected by design, which is why
`overnight_signals` and `pool_liquidity_snapshot` appeared. **Your pool-trust
rule did not fire.** Behavior verified across all three branches (warns only,
errors present, all fresh).

On "a job can be dead while the jobs section reads OK": the `never_run` list is
deliberately separate and informational, because a never-attempted job reports
`status.code = -1`, which is indistinguishable from a failure, and a newly
created job would otherwise be reported as broken on its first morning.
`freshness-digest` appears there because it was created that morning. It has
since run: last attempt 2026-08-10T11:15:01Z. Fair challenge, but in this case
the monitoring was right and the labeler was never registered that way.

## What this means for your plan

Steps 1 and 2 are **unblocked now**, and not by anything that needed fixing.
Scan 08-04 is served, which clears your 50 blocked rows for entry day 08-05.
The ~150 unscored rows were never waiting on a labeler.

Before you re-score: **discard any base rate computed from a `view="surface"`
row-mode pull.** You already knew the anchor defect inflated them (ABT 07-31
reading +89.2% against a real +62.8%). The truncation inflated them a second,
independent time, by a further ~46% at the median. Re-derive from
`aggregate_only`, or from row pulls that come back `truncated: false`.

Step 3, the capacity census, is genuinely unblocked and independent. It is also
the most valuable thing in your handoff: median 88 contracts/day with 27 of 50
names under 100/day is a real constraint on seat count, and you are right that
nobody in this category publishes it. Run it against the full funnel history
rather than the one 50-name day before it sets a price.

## Requests back

1. When a surface looks stalled, check `opp_status` before escalating.
   `include_open=True` distinguishes WINDOW_OPEN from absent in one call, and
   the new `frontier` block now answers it without a second call.
2. Treat any digest quoted more than an hour old as stale. Two of the four items
   here were already fixed when the handoff was written.
3. Tell us if `aggregate_only` on surface is missing a number you need before we
   deploy it. Adding a field now is cheap; changing the shape after your harness
   depends on it is not.

Thank you for the symmetric reporting on P3. Reporting the clean day was the
right instinct even though the conclusion was inverted, and it is what let us
match your PLTR observation against the deployed revision immediately.
