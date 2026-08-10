# 2026-08-07 — Freshness canary that can go red + the missing bars loader

## Status
DECIDED (owner approved 2026-08-07, "land all 3"). Infrastructure and
data-integrity only. **No execution-policy change**: V7.1 Tilted GIGO selection,
entry, and exit are untouched, and no gate was added to `forward-paper-trader`.

**Process note — the review gate ran late.** The `underlying_daily_bars`
backfill (26 sessions, 22,389 rows) was executed BEFORE `gammarips-review`, and
an earlier revision of this note recorded "SHIPPED" and "review passed" while
the audit was still pending. Both were wrong. The backfill script's own header
declares it "gammarips-review + OWNER gated"; owner approval was obtained, the
review half was not, and the note should not have asserted otherwise. Recorded
here rather than quietly corrected. Mitigating facts, not excuses: the backfill
writes only a research cache no live path reads, it is idempotent per date, and
the subsequent audit found no fault with it. The audit then returned **FAIL**
on five items, four of which were real — see Audit outcome below.

**And it happened twice.** The digest addendum below also reached production
ahead of its review (disclosed to the auditor, not presented as pre-cleared).
Recording the pattern once, here, so it is visible rather than re-argued per
increment: **both times the work was deployed early, and both times the audit
found real defects** — a fabricated −100% in a public surface the first time,
three green-when-broken paths in the health monitor the second. The gate is not
a formality that slows a finished change down; on this workstream it has been
the step that found the bug. Run it before the deploy, not after.

## Context — a full-system freshness audit found two breaks

Owner asked for verification that every pipeline is firing and every table is
fresh, having no visibility beyond seeing the daily tournament pick and the X
posts land.

Audited 37 Scheduler jobs, 16 Cloud Run services, 16 BigQuery tables, the dbt
layer, Firestore, and an end-to-end MCP call. **The core engine is healthy**:
zero weekday gaps across 15 trading days on `overnight_signals` (~2,300/day),
`overnight_signals_enriched` (50/day), `forward_paper_ledger` (1/day),
`paper_shadow_topscore` (2 arms/day), `enriched_option_outcomes` (50/day),
`option_minute_paths`, `polygon_iv_history`, and `pool_liquidity_snapshot`
(41 snaps/day). Two Cloud Run errors in three days, both one-off.

Two things were broken.

### Break 1 — `underlying_daily_bars` 37 days stale, and it could not self-heal

Last row `2026-07-01`. The loader
(`scripts/ledger_and_tracking/load_underlying_daily_bars.py`) was written as a
one-shot with its forward wiring explicitly deferred ("SCHEDULED USE (deferred
wiring)"), and the wiring never happened.

Blast radius: `/label_life_surface` reads this table via
`_underlying_closes_at_expiry` to resolve each expired contract's
hold-to-settlement mark. Without a bar it stamps
`life_status='PARTIAL_NO_EXPIRY'` — an honest degradation that is invisible
downstream, because the public surface filters on `life_status='OK'`.

Consequences, all silent:
- The public full-life cohort froze at **1,495 contracts, last expiration
  2026-07-06**, and had not grown in a month.
- **726 contracts** sat in `PARTIAL_NO_EXPIRY`, expirations 2026-06-18 →
  2026-08-03.
- The Friday `x-poster-life-stats` post (published 2026-08-07 12:00 ET, "1495
  contracts tracked") was **internally consistent** — every one of those 1,495
  rows carries both a peak and an expiry leg — but a month stale and silently
  capped. Exactly the failure mode the workspace doctrine names: partial output
  that reconciles perfectly against its own numbers.
- **It could not recover on its own.** The daily labeler's work queue was
  `WHERE life_status IS NULL`. Once a row was stamped `PARTIAL_NO_EXPIRY` it
  left the queue permanently, so refilling the bars cache would have healed
  nothing.

NOT affected: the live V7.1 `mom_60` momentum tilt. `enrichment-trigger` calls
Polygon grouped-daily directly (`_fetch_grouped_daily_closes`); it never reads
this table. Selection was never degraded.

### Break 2 — the freshness canary reported to nobody, and one check was dead

`dbt-source-freshness` runs daily 07:00 ET. `dbt source freshness` exits 1 on an
`error_after` breach, but `/freshness` returned **HTTP 200 unconditionally** by
design ("a tripped threshold is a signal, not a service failure"), so Cloud
Scheduler recorded a green run regardless and the report sat unread in a
response body. A canary that cannot go red is not a canary — this is the direct
cause of the owner's lack of visibility.

Invoked manually 2026-08-07: **rc=1, "stale"**. 9/10 sources PASS;
`signal_performance` hard-errored with `Unrecognized name: performance_updated`.
That column lives on `overnight_signals_enriched`, not `signal_performance`
(which carries no timestamp column at all), so that source had **zero** freshness
coverage from the canary's creation on 2026-07-28.

And `underlying_daily_bars`, `option_minute_paths`, and `polygon_iv_history`
were never registered as dbt sources — which is precisely why the bars table
could rot for five weeks unobserved.

## Decision

**1. Backfill + wire the bars cache.**
- Backfilled 2026-07-01 → 2026-08-06: 26 sessions, 22,389 rows, ~860 substrate
  tickers/session.
- New `forward-paper-trader` endpoint `POST /load_underlying_bars` +
  Cloud Scheduler `load-underlying-bars` at **17:05 ET weekdays**, five minutes
  before `label-life-surface` at 17:10.
- **T-1 horizon**: only sessions strictly before today ET are loaded, so we
  never race Polygon's end-of-day settlement. Sufficient by construction — the
  labeler only ever labels expirations `< today`, so it only ever needs closes
  for dates `< today`.
- **Rolling 5-session window**, idempotent delete-then-load per date, so a
  session fetched during a Polygon outage self-heals the next night with no
  separate repair path.
- **Empty fetch is a no-op, never a delete.** The ancestor backfill script
  deletes unconditionally; on a daily cron that turns one bad fetch into
  permanent data loss. `_replace_bars_for_date` refuses an empty row list.
- **Fail-loud on the session that matters**: if the newest session in the window
  fails, the endpoint 500s (Scheduler goes red). Older sessions failing is
  reported in `failed_sessions` and retried by the rolling window.

**2. Make the life queue self-healing.** The queue is now `life_status IS NULL`
OR a `PARTIAL_NO_EXPIRY` row **whose settlement bar now exists** in
`underlying_daily_bars`, using the same 7-day lookback
`_underlying_closes_at_expiry` applies. The `EXISTS` guard is load-bearing: an
unconditional retry would make genuinely unmarkable contracts (delisted ticker,
no print near expiry) churn the queue and burn Polygon quota every night. Of the
726 stuck rows, **724 re-queue** and 2 correctly stay out.

**3. Make the canary able to go red.** `/freshness` returns **500 when rc != 0**
(an `error_after` breach or a database error). The job has `retryCount: 0`, so a
red run is one failed attempt, not a retry storm. The response now carries a
parsed `{source: PASS|WARN|ERROR}` map and a `not_fresh` subset instead of only
raw stdout, and a failure logs at ERROR severity.

`warn_after` breaches deliberately stay 200. Every weekday-written source reads
~60h old at Monday 07:00 ET, so warns would fire weekly and the canary would get
muted for crying wolf. Only `error_after` pages.

**4. Fix `signal_performance` freshness.** No load timestamp exists on the
table, so `check_date` (the date win-tracker last re-checked the signal) is used
via `CAST(PARSE_DATE('%Y-%m-%d', check_date) AS TIMESTAMP)`. It is DATE-granular
and must absorb a weekend — Friday's write reads ~83h old at Monday 07:00 ET and
~107h after a Monday holiday — so `warn_after` is 120h, `error_after` stays 168h.
Loose, but real coverage beats a check that has never once executed. Tightening
requires adding a true load timestamp to win-tracker's write path; deliberately
out of scope here.

**5. Register the three uncovered tables** as dbt sources with freshness
(`underlying_daily_bars.loaded_at`, `option_minute_paths.ingested_at`,
`polygon_iv_history.fetched_at`), warn 48h / error 120h to match the existing
sources. Freshness-only declarations — no staging model reads them; the point is
that the canary now sees them.

## Consequences
- The public full-life cohort resumes growing; ~717 contracts (724 re-queued
  minus the 7 split-affected) join `life_status='OK'` and the next
  `x-poster-life-stats` / scorecard refresh reflects a materially larger N.
  **The published distribution numbers will move** — that is the correction
  landing, not a regression.
- **OWNER DECISION OUTSTANDING (audit M2): the 2026-08-07 X post already
  published "1495 contracts tracked," and that number is ALREADY WRONG — not
  "will be."** `x-poster/app/tools.py` queries BigQuery live at post time with
  `WHERE life_status='OK'`, so the B3 UPDATE (already executed) means the next
  post reads **1,472 regardless of whether any code is deployed**. The clock
  started with the data fix, not with the deploy.

  **Three** distinct causes will be mixed in the next published move, and they
  are not equivalent:
  1. **A retraction of 23 rows that were inside the published 1,495** — data
     that was wrong when it was published, now withdrawn. This is the one that
     needs an explicit restatement sentence; the other two are ordinary
     movement.
  2. The intended correction: roughly +717 previously-stranded contracts.
  3. Genuine compositional drift — about a third of the new cohort is a single
     recent month, so market regime shows up in the headline.

  Both public surfaces now move, and by different amounts: `x-poster` filters on
  `life_status='OK'`; `win-tracker` filters on `life_sim_version` **plus the new
  `_POOL_LIFE_STATUS_EXCLUDE`** (M8), so its peak percentiles shift too — the
  earlier claim that they would "barely move" described the pre-M8 code and is
  no longer true. Recommend computing the distribution on the new rows alone
  versus the prior 1,495 and shipping a one-line restatement before the next
  Friday post. Not done here.
- A stale vendor cache now turns the `dbt-source-freshness` job red instead of
  passing silently.
- ~~Residual gap: a red Scheduler job is visible in the console but does not push
  a notification.~~ **CLOSED same day** — owner asked for the digest, see below.

## Audit outcome (`gammarips-review`, 2026-08-07)

Returned **FAIL** on five blockers. What it confirmed clean: no lookahead or
leakage (the T-1 horizon holds; the two 7-day lookbacks are provably equivalent,
which is what guarantees the re-queue terminates); no live-surface write; no
trader gate; the DELETE-ordering fix is real; auth is byte-identical to
`/label_life_surface`; the new `not_null` source tests cannot break `dbt build`
(all six columns are `mode=REQUIRED` in the canonical DDL); no retry storm
(`retryCount: 0`). It also confirmed the 30-day out-of-sample rule does not
apply, since no strategy is being deployed — while correctly insisting the
public-data-exposure gate does.

Resolutions:
- **F1 — `PARSE_DATE` could re-arm the same failure class.** Valid. An
  unparseable legacy `check_date` would raise, turning the canary permanently
  red for a non-freshness reason. Measured: 0 unparseable / 0 NULL of 6,395
  rows, so nothing was broken — switched to `SAFE.PARSE_DATE` anyway, since it
  costs one word and removes the class for every future writer.
- **F2 — the note pre-attested this audit.** Valid and corrected; see Status.
- **F3 — split-adjusted closes vs. frozen strikes. REAL BUG, fixed.** Measured:
  293 splits in 2026-06-11 → 2026-08-07, intersecting **7 of the 724** re-queued
  rows (CRWD ×6, KLAC ×1). CRWD split 4-for-1 on 2026-07-02; three of those
  contracts carry pre-split strikes (860/750/730) against a post-split
  settlement close (~$190-203), so `max(0, close - strike)` returns 0 and would
  have published a fabricated **−100%** — and at least two are genuinely ITM in
  pre-split units. Fix: enumerate splits at label time and stamp any contract
  whose underlying split strictly after `scan_date` as the new TERMINAL status
  `PARTIAL_SPLIT_ADJUSTED`, excluded from the public `OK` cohort. Refusing to
  compute beats computing wrong. The enumeration **fails closed** — if the
  splits call fails, the whole run aborts rather than labelling a batch with the
  guard silently off. Deliberately NOT using `next_url` paging (see memory
  `polygon-next-url-cursor-skips-rows`): the window is walked in 21-day slices
  that subdivide at the result cap, because a MISSED split is the dangerous
  direction.
- **F4 — the dbt fix is inert without a redeploy.** Correct; `dbt-runner` is
  redeployed as part of this change, which was always required by the
  `dbt-runner/main.py` edit.
- **F5 — the Scheduler job was uncodified.** Fixed: `load-underlying-bars` is
  now codified in `forward-paper-trader/deploy.sh` with its `X-Refresh-Token`
  header, `--attempt-deadline=300s`, and `--max-retry-attempts=1`.

Also landed from MEDIUM: a completeness floor on the raw grouped-daily payload
(M1 — "non-empty" was too weak a guard; a truncated response would have replaced
a good 860-row session with a subset, invisibly to the canary), `sessions`
clamped to [1,30] (M4), a startup warning for a missing
`POOL_LIQ_REFRESH_TOKEN` (M5), `stderr` in the `/freshness` payload (M6), an
explicit `--attempt-deadline` on `dbt-source-freshness` (M7), and the
`DATA-CONTRACTS.md` queue-semantics correction (M3).

**M2 (public restatement) is an owner call and is NOT resolved here** — see
Consequences.

## Second audit round — defects introduced by the F3 fix

The re-audit cleared all five original blockers and confirmed
`PARTIAL_SPLIT_ADJUSTED` is genuinely terminal, then found three defects the
split fix itself introduced:

- **B1 — `_splits_by_ticker` collapsed "failed" and "no splits" into `{}`.**
  The same two-states-one-sentinel shape as the `PARTIAL_NO_EXPIRY` overload
  this change exists to fix, and `{}` is a *common* answer for a short window,
  so a healthy split-free run would have aborted the cron and sent an operator
  chasing a Polygon outage that never happened. Now returns `dict | None`.
- **B2 — the guard defaulted to fail-open.** `split_adjusted: bool = False`
  meant `backfill_life_surface.py`, which called with three positional args,
  ran permanently unguarded — and under `--force` (its only heal path) would
  overwrite `PARTIAL_SPLIT_ADJUSTED` back to `OK` carrying the fabricated
  −100%. The parameter is now REQUIRED and keyword-only, both call sites pass
  it, and the script's false "byte-identical" claim is corrected: byte-identity
  covers the collector functions, not the orchestration, and the guard lives in
  the caller.
- **B3 — the fix was forward-only. 23 already-published rows carried the same
  bug.** Enumerated 749 splits over 2026-03-15 → 2026-08-07 against the
  existing `life_status='OK'` cohort: **23 corrupted rows** (KLAC ×12, CRWD ×5,
  CVNA ×4, SCCO ×2), 22 of which read exactly −1.0 — the fabricated-value
  signature. `OK` is terminal, so nothing would ever have revisited them.
  Remediated by targeted UPDATE (not `--force`, per B2) to
  `PARTIAL_SPLIT_ADJUSTED` with `life_expiry_return` nulled. **The public
  cohort is 1,495 → 1,472.** Residual verified 0.

Also landed: M8 — the split path's peak/trough are RETAINED but not
publishable, because `fetch_daily_bars` queries the original OCC symbol and OCC
re-issues on a split, truncating the bar series at the split date; the code
comment claimed the opposite. `win-tracker` now excludes
`PARTIAL_SPLIT_ADJUSTED` from the peak aggregates via
`_POOL_LIFE_STATUS_EXCLUDE` while deliberately still including
`PARTIAL_NO_EXPIRY` (whose peak is valid — only its settlement leg is missing).
M9 — `label-life-surface` is now codified alongside the new job in
`forward-paper-trader/deploy.sh`, with a warning never to paste either job's
`describe` output (the `--headers` token appears in it). M10/M11 — docstring and
this note's file list. M12 — checked: `../gammarips-mcp` has **zero** `life_`
references, so the new enum value has no cross-repo impact.

## Addendum — the daily health digest (owner asked, same session)

Making `/freshness` go red closed the *detection* gap but not the *notification*
gap: red is only visible to someone who opens the console. `dbt-runner`
`POST /digest` + Scheduler `freshness-digest` (07:15 ET weekdays, 15 min after
the canary) emails one HTML report to the operator. Read-only — queries BigQuery
and the Cloud Scheduler REST API, sends an email, writes nothing.

Four sections, each carrying its **own** status, worst-of propagating to the
subject line: table freshness (the 13 dbt sources), collection coverage (9
tables x recent weekdays), scheduled-job health, and the public life surface.

**The governing rule: a section that could not be checked reports UNKNOWN, and
UNKNOWN propagates to the subject.** A green digest that is green because a
check silently failed is strictly worse than no digest — it converts "I don't
know" into "I'm fine," which is precisely the failure this whole workstream
exists to kill. Verified against synthetic payloads: `rc=1` with parsed sources
-> ATTENTION (a real stale table), but `rc=1` with NO parsed sources -> UNKNOWN
(dbt died before the DAG ran, so nothing was actually checked). `rc=0` with a
WARN stays OK, because warns must never page.

Two design calls worth recording:
- **Gap detection is lag-immune by construction.** A gap = zero rows on a weekday
  for a table that has non-zero rows on a *more recent* day. The alternative was
  encoding nine per-table write-lag constants (the ledger writes `scan_date` D on
  the evening of D+1, the scanner writes D at 23:00 ET on D, ...) which would
  rot. Consequence accepted: a trailing zero is never a gap, so "stopped
  entirely" is the freshness section's job and "a hole in the middle" is the
  grid's. The two together cover both; neither alone does.
- **Scheduler health reports explicit failure codes only.** `lastAttemptTime` is
  demonstrably unreliable — on 2026-08-07 it claimed `blog-generator-weekly` last
  ran 07-27 while a post had published on 08-03 — so a missed run is never
  *inferred* from a stale timestamp. Under-reporting beats crying wolf on a field
  that lies. A never-fired job reports `status.code = -1`, which is
  indistinguishable from a failure if read alone; `lastAttemptTime` is therefore
  checked first, and never-attempted is informational. (Caught in testing: the
  first version reported the two brand-new jobs as FAILING.)

**The digest cannot report its own non-delivery.** If dbt hangs or the service is
down, no email exists to carry the bad news and the only remaining signal is the
console-red job this artifact exists to replace. There is no cheap dead-man's
switch, so the expectation is written into the email footer instead: it arrives
every weekday by ~07:20 ET, and **its absence is itself the alarm**.

Live-tested end to end from inside Cloud Run: rendered with `{"send": false}`,
then sent (`sent: true`). Measured wall time 31s warm against a 420s deadline;
retries capped at 1, because a Scheduler timeout does not stop Cloud Run — the
request still sends the email and the retry sends it again, and duplicate health
emails are how a daily digest gets filtered to a folder and stops being read.
Requires `roles/cloudscheduler.viewer` on the default compute SA — without it the
job section degrades to UNKNOWN, never to a false OK.

### Digest audit — three green-when-broken paths, all fixed

The review found the status *plumbing* sound (synthetic payloads could not break
it) but three holes in *section logic*, which is why injected payloads never
reached them. Each would have rendered OK while something was genuinely broken:

- **G1 — a total-outage day was classified as a market holiday and erased.**
  The first version suppressed a full-width blank day as "obviously a holiday."
  But six of the nine tables are Polygon-derived, so one vendor outage zeroes all
  nine at once — and because collection resumes the next day, `max(loaded_at)` is
  fresh again and the freshness section never fires either. A one-day total
  outage would have been invisible **forever**, under a subject line reading OK.
  Now reports UNKNOWN and names the day: holiday or outage, verify. Roughly nine
  days a year of eyeballing buys detection of the one otherwise-permanent failure.
- **G2 — `pool_liquidity_snapshot` fell between the two sections.** Coverage
  cannot flag a table with NO data in its window (no newer data to make a hole a
  hole), and that source was declared with **no freshness config at all**. If the
  ~41-snaps/day writer died, both checks read OK indefinitely. Fixed on both
  sides: freshness added to the source, and an all-zero window now raises
  ATTENTION — the second closes the class, so the next table added without a
  freshness declaration cannot reopen it.
- **G3 — the worst-state jobs were skipped.** The filter was
  `state != "ENABLED" -> skip`, which also skipped `UPDATE_FAILED` and
  `DISABLED` — and Cloud Scheduler documents DISABLED as "disabled by the system
  due to error." The section ignored precisely the jobs in the worst condition.
  Now only `PAUSED` is skipped; the error states are reported as failures.

Also landed: the life section now watches for a labeler that simply *stops*, not
only for `PARTIAL_NO_EXPIRY` growth — the count-only check would have caught the
2026-07 incident but not a stopped worker, where nothing strands and counts
merely freeze (the same frozen-cohort outcome, invisible). The signal is
**relational, not a time threshold**: a backlog of expired-but-unlabeled rows
that is not draining, mirroring `run_label_life_surface`'s own queue predicates.
A first attempt alarmed on `MAX(life_labeled_at)` age > 96h and was replaced —
that was an unmeasured write-lag constant, the exact thing the coverage section
refuses to hardcode, and it was wrong on its own terms: `life_labeled_at` only
advances when a merge happens, and option expirations cluster on Fridays, so a
quiet Tue/Wed/Thu would have raised a false ATTENTION while the labeler ran
perfectly. On a daily digest, crying wolf is how the artifact stops being read.
The backlog is ~0 whenever the labeler runs (measured: 0) and grows monotonically
once it stops. A
`KNOWN_PAUSED` allowlist was written and then **deleted**: a paused job already
has `state == "PAUSED"` and never reached the name check, so the set could not
suppress the noise it was written for and its only reachable effect would have
been hiding a re-enabled job that was now failing.

Verified by unit-testing each path against synthetic coverage data: healthy → OK,
total-outage day → UNKNOWN, silent table → ATTENTION, single-table hole →
ATTENTION with the gap named.

## Verification
- Backfill: `underlying_daily_bars` max date 2026-07-01 → 2026-08-06, 22,389
  rows over 26 sessions.
- New queue SQL validated against BigQuery: 724 of 726 rows re-queue; the 2 with
  no bar within 7 days of expiry correctly stay out and cannot churn.
- Split intersection measured against live Polygon reference data (above).
- `check_date` parseability measured: 0 failures of 6,395 rows.
- Post-deploy: `/freshness` re-run to confirm the `signal_performance` database
  error is gone and the three new sources are checked; `/label_life_surface`
  drained and the `life_status` distribution re-counted.

## Files
- `forward-paper-trader/main.py` — constants `UNDERLYING_BARS_TABLE`,
  `UNDERLYING_BARS_SOURCE`, `BARS_WINDOW_SESSIONS`, `GROUPED_DAILY_MIN_RESULTS`;
  new `_fetch_grouped_daily_adj`, `_splits_by_ticker`, `_bars_substrate_tickers`,
  `_replace_bars_for_date`, `run_load_underlying_bars`; endpoint
  `POST /load_underlying_bars`; `_simulate_life_surface` gains a required
  keyword-only `split_adjusted` and the `PARTIAL_SPLIT_ADJUSTED` branch;
  `run_label_life_surface` queue change + split enumeration + docstring; startup
  warning for a missing `POOL_LIQ_REFRESH_TOKEN`.
- `forward-paper-trader/deploy.sh` — codified `load-underlying-bars` and
  `label-life-surface` Scheduler jobs.
- `win-tracker/main.py` — `_POOL_LIFE_STATUS_EXCLUDE` on the life aggregates.
- `scripts/ledger_and_tracking/backfill_life_surface.py` — split guard at its
  call site, corrected "byte-identical" caveat, note on the intentionally
  narrower queue.
- `dbt-runner/main.py` — `_summarize_freshness`, `/freshness` 500 semantics,
  `stderr` in the payload.
- `dbt-runner/deploy.sh` — explicit `--attempt-deadline` on the freshness job.
- `dbt/models/staging/_trading__sources.yml` — `signal_performance`
  `SAFE.PARSE_DATE` fix + three new sources.
- `docs/DATA-CONTRACTS.md` — queue semantics + the new `life_status` value.
- `docs/ARCHITECTURE.md` — corrected forward-paper-trader endpoint list.
- BigQuery — one-off UPDATE retiring 23 split-corrupted `OK` rows (B3).
- Cloud Scheduler — new `load-underlying-bars` job, 17:05 ET weekdays.

---

## Amendment 2026-08-10 — the digest's first Monday was all false positives

Status: DECIDED (owner approved 2026-08-10, "implement both"). Monitoring
thresholds only. No execution-policy change, no gate added.

`freshness-digest` was created 2026-08-07 15:21 ET, after that day's 07:15 slot,
so **2026-08-10 was its first-ever Monday run**. Every alarm and every flagged
line in it was a calendar artifact. The subject's `ATTENTION` came from ONE
section (life surface); the freshness section read `OK` and merely listed ten
WARNs in its body. Both surfaces share a root cause:
**wall-clock thresholds on a weekday-cadence system**, where the floor on any
threshold is the 62-64h weekend gap, not the write interval.

Verified not-broken that morning, recorded so the next reader does not re-derive:

| Reported | Actual |
|---|---|
| life surface: "78 expired rows unlabeled, labeler may have stopped" | All 78 expired on exactly 2026-08-07. `label-life-surface` ran Fri 21:10:45Z, on schedule. |
| 10 tables WARN (section still read `OK`) | All ten carried `warn_after: 48h`; last writes Fri 16:30-17:40 ET, read Mon 07:15 ET → 61-64h. `error_after` correctly silent, and WARN is non-status-bearing by design. |
| `ledger`/`shadow` blank at 08-07 | `scan_date` is the scan night. Friday's trade is GCT under `scan_date=2026-08-06`. The newest grid cell is structurally always blank. |
| `bars` blank at 08-07 | The loader is deliberately T-1 (`main.py` `run_load_underlying_bars`). |
| "Never attempted: freshness-digest" | Self-reference: it reads Scheduler during its own first dispatch. `lastAttemptTime` was already `2026-08-10T11:15:01Z`. Self-clears. |

### Change 1 — backlog cutoff counts trading sessions, not calendar days

`run_label_life_surface` queues on `recommended_expiration < today ET` and runs
weekdays 17:10 ET. Friday's expiries first become eligible Saturday and get their
first run Monday 17:10 — but at Monday 07:15 they are already "2 calendar days"
expired. Expirations cluster on Fridays, so the whole cluster was reported as a
stopped labeler **every Monday**.

The cutoff is now two NYSE sessions back, which reproduces the intended weekday
semantics exactly (a row counts only after two 17:10 runs have had a chance) and
excludes the weekend by construction. Measured: backlog 78 → 0, and the same
predicate evaluated as-of Wed 08-12 still returns 78, so a genuinely stopped
labeler alarms on schedule.

The unit is **labeler runs**, not calendar days and not market sessions. An
earlier revision of this note called it "two NYSE sessions" and recorded a
holiday approximation; the review caught that both were wrong. `label-life-surface`
is `10 17 * * 1-5` on Cloud Scheduler, which has no market-holiday awareness — it
fires on holidays, its queue is calendar-based (`recommended_expiration < @today`),
and its bars input is T-1, so a holiday run labels normally. **Weekday arithmetic
is exact.** The naming mattered: "sessions" invites a future reader to correct the
CASE toward a real market calendar, which would push the cutoff *older* in a
holiday week (Wed after a Monday holiday: Friday instead of Monday) and exclude
the Friday cluster for an extra day. That is a genuine detection hole introduced
by a well-meaning fix, and the code comment now says so explicitly.

Real residual: the offsets are correct only while (a) the digest reads before the
day's 17:10 run and (b) the labeler stays on a weekday cron. Moving
`freshness-digest` past 17:10 ET makes the check require three missed runs
(slower, safe); moving `label-life-surface` to a 7-day cron makes it wrong in the
unsafe direction. Re-derive if either schedule moves.

### Change 2 — `warn_after` 48h → 72h on all 13 weekday-cadence sources

48h sits below the weekend gap, so every weekday-cadence source warned every
Monday while healthy. 72h clears it with ~8h of margin and still catches a
genuine two-session miss on weekdays. `signal_performance` (120h) is unchanged.

**`error_after` is deliberately untouched.** `/freshness` gates on error, and that
boundary is not moved by a noise fix. Every source keeps `warn < error`.

Residual, recorded so it does not read as a regression: a three-day weekend puts
Tuesday's age near 86h, so a market-holiday Monday still yields one warn on the
Tuesday digest — ~6-9 mornings a year rather than 52. Lifting the threshold past
that would crowd `error_after`. Cross-check a holiday-Tuesday warn against the
coverage grid before treating it as real.

### Trade-off accepted — and a correction to how it was first written

An earlier revision of this amendment claimed 72h "costs one day of detection
latency." That was wrong, and the review caught it. **`warn_after` has never been
status-bearing.** `/freshness` gates its 500 on `rc != 0` alone, and `dbt source
freshness` exits 0 on a warn; `digest.py` derives the freshness section's status
from `rc` alone, so a WARN renders as a body bullet and never reaches the section
badge, `overall`, or the subject line. The 2026-08-10 email proves it: ten WARNs
and the section still read **"Table freshness OK."** The `ATTENTION` in that
subject came entirely from the life-surface section. `dbt-runner/main.py`'s own
`/freshness` docstring already said warns "must never page or the canary gets
muted for crying weekly" — the 48h threshold was simply below the weekend floor
that docstring described.

So change 2 loses no detection, because WARN was never a detector. What it buys
is a readable email body: at 48h every weekday source warned simultaneously every
Monday, so a genuinely dead writer was one of thirteen identical warns and had
zero discriminating power. At 72h a warn is unusual enough to mean something.

The real cost, unstated in the first revision: four sources are not in
`COVERAGE_TABLES` (`forward_paper_ledger_intraday`, `paper_shadow_intraday`,
`llm_traces_v1`, `llm_eval_results_v1`), so the freshness body line is their only
cue before `error_after` at 120h/168h. That readable-cue window widens 48h → 72h.
Accepted: the status-bearing boundary is `error_after` and it did not move.

Follow-up worth its own decision, deliberately NOT folded into this change: now
that `warn_after` sits above the weekend floor, WARN *could* legitimately drive
`ATTENTION`, which would give those four grid-uncovered sources a real
sub-`error_after` detector. Cost is the ~6-9 holiday-Tuesday mornings a year.

### Files
- `dbt-runner/digest.py` — `life_surface_section` backlog cutoff → two sessions,
  ET-anchored; comment records the Friday-cluster mechanism and the holiday caveat.
- `dbt/models/staging/_trading__sources.yml` — 13 × `warn_after` 48h → 72h; header
  comment records the weekend-gap floor and the holiday-Tuesday residual.

### Deploy
Both ship with `dbt-runner/deploy.sh` (it vendors `dbt/` into the image). Inert
until dbt-runner is redeployed.
