# 2026-07-01 — Substrate integrity + hardening pass (#3, #7, and #1's review notes)

Substrate-readiness audit must-fixes #3 and #7, plus the two non-blocking
hardening notes surfaced by must-fix #1's review
(`.scratch/substrate_readiness_audit_2026-07-01.md`). Working-tree change only —
NOT deployed; NO BQ write/dedup/backfill run. Must pass `gammarips-review` before
any deploy; the dedup/backfill script needs `gammarips-review` + owner OK before
running.

## Scope
Research substrate + collector reliability + input hardening ONLY. No change to
execution policy, trade selection, or mechanics. `forward_paper_ledger`,
`_write_ledger_records`, `_simulate_contract`, Firestore/`todays_pick`, and the
live-pick path are untouched. Builds on must-fix #1 (atomic staging→verify→
transactional-replace write path) and #2 (scan-date regime), already in the tree.

## Changes

### Must-fix #3 — empty/degraded pool = failure + freshness monitor
- `forward-paper-trader/main.py` `run_label_enriched_pool`: on a real NYSE trading
  day (`is_trading_day(target_date)`), the run now returns non-2xx (endpoint 500)
  when `pool_size == 0`, `labeled == 0`, OR `wins+losses == 0` (a Polygon
  minute-bar outage that writes an all-`INVALID_LIQUIDITY` / NULL-label pool — the
  confirmed root cause of the two permanent holes). Previously this returned HTTP
  200 "success" and was swallowed. The legitimate no-trading-day path (backfill of
  a weekend/holiday) still returns success on an empty pool.
- `scripts/ledger_and_tracking/check_substrate_freshness.py` (NEW, read-only): a
  morning monitor asserting the just-closed NYSE session (keyed on the table's
  `entry_day` DATE column) has ≥1 row AND label fill-rate
  (`COUNT(realized_return_pct)/COUNT(*)`) ≥ 0.80; exits non-zero + prints an ALERT
  otherwise. This is the safety net for the untracked label-pool cron SPOF. Header
  notes it is MEANT to be wired to Cloud Scheduler / a monitoring alert policy —
  it is NOT wired up here (separate review-gated step).

### Must-fix #7 — dedup at source + uniqueness guard + per-scan_date lock
- `forward-paper-trader/main.py` `_assert_outcomes_unique` (NEW): after the write,
  a read-only SELECT counts `(scan_date, ticker, recommended_contract)` groups with
  `COUNT(*)>1` for the scan_date and logs LOUDLY (error) if any exist — the atomic
  replace can't dup THIS run, so a hit means an UPSTREAM doubling faithfully copied
  by the collector. Count is surfaced in the summary as `dup_groups`.
- `forward-paper-trader/main.py` `claim_label_pool_run` / `release_label_pool_run` /
  `_mark_label_pool_done` (NEW): a per-`scan_date` Firestore transactional claim
  (`label_pool_runs/{scan_date}`) around the label-pool run, mirroring
  signal-notifier's `claim_email_send`. Prevents a concurrent daily-cron +
  manual/backfill double-run on the same scan_date. Fail-OPEN on Firestore error
  (still labels); already-claimed → idempotent skip (200, `skip_reason=already_claimed`);
  released on degraded-pool/exception so the next Scheduler retry re-runs; marked
  `status=done` on success. ESCAPE HATCH: delete `label_pool_runs/{scan_date}` to
  force a deliberate re-label (matches the notifier's `email_sends` gotcha).
- `scripts/ledger_and_tracking/dedup_enriched_060_source.py` (NEW, gated,
  NOT executed): remediates the confirmed UPSTREAM 2026-06-10 doubling
  (`overnight_signals_enriched` scan_date 06-10 == 329 tickers × 2). STEP 1 reports
  the counts; STEP 2 dedups the source to one row/ticker via the same
  stage→verify→tx-replace pattern; STEP 3 clears `label_pool_runs/2026-06-10`
  (so the new lock doesn't skip) then re-labels via `/label_enriched_pool`. Default
  `--dry-run`; `--confirm` gated on review + owner OK.

### Hardening notes from #1's review
- `forward-paper-trader/main.py` `_write_shadow_records`: explicit
  `raise ValueError` if `table == LEDGER_TABLE` (not `assert` — asserts strip under
  `-O`), enforcing "never write the live ledger via the shadow writer" in code, not
  just docstring.
- `enrichment-trigger/main.py` `write_enriched_signals`: hard-validate `scan_date`
  with `datetime.strptime(..., '%Y-%m-%d')` before it is interpolated into the
  staging table NAME (an identifier — cannot be parameterized) and the
  multi-statement replace transaction's DELETE literal. This is a
  **defense-in-depth** guard — see the FIX-FIRST review follow-up below for why it
  is NOT by itself sufficient.

## FIX-FIRST review follow-up (2026-07-01) — two blockers closed

`gammarips-review` found two FIX-FIRST blockers in this batch. Both are now fixed
(working-tree only; NOT deployed; still returns to `gammarips-review`).

### BLOCKER 1 — request-controlled SQL injection (enrichment-trigger)
The `write_enriched_signals` `strptime` guard above ran **too late**: the
`--allow-unauthenticated` entrypoint (`enrichment_trigger`) reads
`override_scan_date` from `req_body`/query args and passes it into
`get_signal_tickers`, which interpolated it RAW into `WHERE scan_date = '{scan_date}'`
— and that query runs BEFORE `write_enriched_signals`. The entrypoint's other
`strptime` (in the non-force staleness guard) ran AFTER the vulnerable query and
was skipped entirely when `force=true`, leaving a live stacked-DML injection
surface. FIX (`enrichment-trigger/main.py`):
  1. **Entrypoint validation ONCE, before any query** (`enrichment_trigger`,
     immediately after `override_scan_date` is read): when truthy,
     `datetime.strptime(override_scan_date, "%Y-%m-%d")` and return HTTP 400 on
     failure. Covers BOTH the `force=true` and `force=false` paths. This is what
     actually closes the surface.
  2. **`get_signal_tickers` parameterized**: the `scan_date` is now bound as a
     DATE `ScalarQueryParameter` (`WHERE scan_date = @scan_date`) instead of
     string-interpolated — the `overnight_signals.scan_date` column is DATE and
     the client accepts an ISO `YYYY-MM-DD` string for a DATE parameter, so this
     is a clean drop-in with identical semantics but injection-proof.
  3. **`get_signal_tickers` inline `strptime` assertion** at the top (belt-and-
     suspenders so no future caller can pass an unvalidated value).
  4. The `write_enriched_signals` guard stays as a third defense-in-depth layer.
`get_signal_tickers` has exactly one caller (`enrichment_trigger`); it passes the
entrypoint-validated value. Surface closed.

### BLOCKER 2 — degraded day overwrote good rows before the 500 (forward-paper-trader)
The original must-fix #3 raised the "degraded" 500 in `run_label_enriched_pool`
AFTER `_write_enriched_outcomes` had already called `_write_shadow_records`, which
**atomically REPLACES** the scan_date. So on the realized==0 / all-INVALID_LIQUIDITY
/ Polygon-outage shape, a deliberate re-label of a GOOD scan_date replaced its good
labels with all-NULL rows and only THEN 500'd. FIX
(`forward-paper-trader/main.py` `_write_enriched_outcomes`): decide "degraded"
BEFORE the write. After the per-row loop, compute `realized = wins + losses` from
the in-memory rows; if `is_trading_day(target_date)` AND `realized == 0`, SKIP the
`_write_shadow_records` call entirely (do NOT touch the table), log the degradation,
and return `degraded_skip_write=True`. `run_label_enriched_pool` then releases the
per-scan_date claim and returns the 500 as before — but the table was never
overwritten. Preserved-correct behavior: `pool_size==0` still early-returns before
the write; `labeled==0` still no-ops the write (rows empty); a genuinely degraded
FRESH date still 500s without writing NULLs; a healthy day (`realized>0`) writes
exactly as before, including the new #5/#6 `mom_60` / opportunity-surface / 3-day
label columns. The atomic write, claim/lock release-on-failure, and the
post-write uniqueness assertion are unchanged.

## Behavior changes to be aware of (not "execution policy")
- `/label_enriched_pool` now 500s on a degraded/empty pool for a trading day
  WITHOUT writing all-NULL rows (BLOCKER-2 fix): the realized==0 degraded case is
  detected before the atomic replace, so existing GOOD rows for that scan_date are
  left untouched and the failure is surfaced (500). The existing backfill driver
  (`backfill_enriched_option_outcomes.py`) treats non-200 as SKIP/ERR and reports
  it — so degraded old dates (e.g. Polygon minute-bar retention gaps) are reported,
  never silently overwritten as all-NULL. `dedup_enriched_060_source.py`'s STEP 3
  re-label POSTs to this same deployed endpoint, so it INHERITS the skip-on-degrade
  behavior: if the 06-10 re-label runs during a Polygon outage / past bar
  retention, it 500s and leaves the existing outcomes rows in place rather than
  nulling them — run STEP 3 only when minute bars for the window are available.
  Intended.
- Re-running the SAME scan_date is now an idempotent skip unless the claim doc is
  deleted — this is the requested concurrency guard; the escape hatch preserves
  deliberate re-labels.

## Follow-ups
- Not deployed. `gammarips-review` required before the `forward-paper-trader` +
  `enrichment-trigger` deploys.
- `dedup_enriched_060_source.py` needs review + owner OK before running.
- Wire `check_substrate_freshness.py` to Cloud Scheduler + an alert policy
  (separate review-gated step); also commit the `/label_enriched_pool` cron to
  IaC (should-fix: the untracked-cron SPOF).
- RESOLVED (was "out of scope"): `get_signal_tickers` in enrichment-trigger no
  longer interpolates the request `scan_date` — it is now parameterized (DATE
  query parameter) with an inline `strptime` assertion, and the entrypoint
  validates the override once before any query. See the FIX-FIRST review follow-up
  (BLOCKER 1) above.

See also: `docs/DECISIONS/2026-07-01-atomic-schema-drift-safe-substrate-write.md`,
`docs/DECISIONS/2026-07-01-regime-scan-date-leakage-fix.md`,
`docs/DECISIONS/2026-06-11-notifier-duplicate-send-guard.md`,
`.scratch/substrate_readiness_audit_2026-07-01.md`, memory
`project_substrate_audit_2026_07_01`, `project_ledger_schema_drift_landmine`.
