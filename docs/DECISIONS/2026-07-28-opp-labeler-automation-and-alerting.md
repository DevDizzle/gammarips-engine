# 2026-07-28 — Opp-surface labeler: backfill, automation, and project-wide cron alerting

## Problem

The opportunity-surface / 3-day-label "gated backfill" for `enriched_option_outcomes`
was never automated. The daily `/label_enriched_pool` cron writes
`opp_status=WINDOW_OPEN` for windows that have not closed, and nothing ever revisited
them — the fill was a manual run of
`scripts/ledger_and_tracking/backfill_opportunity_surface.py`, last covering scans
through 2026-06-26. Result: 950 rows (scans 06-29..07-24, 24.1% of the table) sat
unlabeled while every window closed — the monetized surface metric was dark for the
entire live V7.1 era (found by the 2026-07-28 pool research pass, FINDINGS_LEDGER).
Separately, the GCP project had ZERO Cloud Monitoring alert policies and ZERO
notification channels — no cron failure had ever paged anyone.

## Owner call (2026-07-28, plain-language session)

Approved: backfill the dark rows + "add an alarm so if it ever stalls again, you get
told the next day instead of a month later." Explicitly declined: any change to the
mom_60 edge-rank tilt (research recommended retiring it; owner keeps it for now —
nothing in this change touches selection/execution policy).

## What shipped (gammarips-review audited 2026-07-28, amendments applied)

1. **One-shot backfill executed** — `backfill_opportunity_surface.py --confirm
   --start 2026-04-10 --end 2026-07-28` (~1,729 closed-window rows). Two review
   amendments landed in the script first: (a) staging dedupe via
   `QUALIFY ROW_NUMBER()=1` on (scan_date,ticker,recommended_contract) — the ~145
   known upstream dup pairs would otherwise crash the MERGE; (b) MATCHED guard so a
   transient Polygon `NO_BARS` can never overwrite a stored `OK` row. Deploy-drift
   verified before running: serving revision `forward-paper-trader-00051-gn8` built
   from HEAD (`4a3ae4e`), so the script's imported collector functions are
   byte-identical to production.
2. **Automated daily filler** — new `POST /fill_closed_windows` endpoint on
   forward-paper-trader (same MERGE semantics + guard, trailing 10 scan_dates,
   400-row per-run cap with loud truncation log) + a daily Cloud Scheduler cron after
   the 17:00 ET label pass. Supersedes all future manual backfill runs.
3. **Staleness tripwire** — dbt singular test
   `dbt/tests/assert_opp_surface_labels_fresh.sql`: any row older than 10 calendar
   days still `WINDOW_OPEN`/NULL fails the daily `dbt-daily-build` (500 → scheduler
   ERROR). Threshold is 10d (not 7d) for holiday weeks + the 06:30 ET build running
   before same-day fills.
4. **Project-wide cron alerting** — email notification channel (operator address, the
   same `RECIPIENT_EMAIL` signal-notifier uses) + log-based alert policy
   `projects/profitscout-fida8/alertPolicies/7876765176662593136`:
   `resource.type="cloud_scheduler_job" severity>=ERROR`, all jobs, rate-limited
   1/30min, auto-close 24h. Every silent-death mode (labeler degradation 500s, dbt
   test failures, any cron) now reaches a human.
5. **polygon-iv-cache-daily 504 noise retired** — measured `/cache_iv` runtime is
   ~335-375s vs a 180s scheduler attempt-deadline; every "failure" was the scheduler
   hanging up on a run that completed (200) server-side, then re-running it 3-4×.
   Deadline raised to 600s (= the service's own `--timeout`), per review amendment.

## Rules going forward

- `backfill_opportunity_surface.py` is now ancestry: do not run it manually again;
  `/fill_closed_windows` owns the fill. (Its per-scan_date claim doc mechanism is
  unchanged; the filler MERGE path does not use claims.)
- The dbt staleness test firing means the FILLER chain broke — check
  `fill-closed-windows` cron logs first, then `/label_enriched_pool`.
- Alert-policy hygiene: if a cron is expected to fail routinely, fix or pause it —
  do not let the channel rot into noise (that is how this outage happened).

## Verification (this session)

- Post-backfill: staleness-test SQL run manually → required zero rows before the dbt
  deploy went live.
- Alert chain: policy enabled + channel verified; first real trip will confirm
  end-to-end delivery.
