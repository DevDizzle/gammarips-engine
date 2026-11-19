# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place, never append dated blocks. Hard cap ~100 lines.
> Rules in `CLAUDE.md`.

## START HERE: the pipeline is RESTORED (owner "go", 2026-10-29 about 20:00 ET)

The shutdown of 2026-10-29 (`docs/DECISIONS/2026-10-29-shutdown.md`) is REVERSED IN PART. The
same evening Evan canceled the story page ("plan is off, leave site as is") and said "go" to
bring the pipeline back. Do NOT delete or "clean up" anything the restore brought back. The jobs
are PAUSED since 11-04 (see below).

- **Serving again (redeployed from git, env matches the saved live config):** overnight-scanner,
  enrichment-trigger, overnight-report-generator, dbt-runner, win-tracker, forward-paper-trader,
  signal-notifier. The 2 deleted token secrets were recreated 10-30 from the saved job headers.
- **Jobs recreated from `~/workspace/projects/_index/fida8-scheduler-jobs-enabled-2026-10-29.json`
  (18)** through the Cloud Scheduler REST API (strip state, status, the time fields, and the
  User-Agent header). Not recreated: mcp-reconcile-keys (MCP), blog and email drafter jobs, and the
  5 jobs retired 09-28.
- **Verified 10-30:** the 10-29 23:00 ET scan wrote 100 rows (scan_date 2026-10-29), enrichment
  enriched 37 with 0 failures, dbt-daily-build returned 200. No data gap.
- **Open owner call:** is the MCP back for the trader? If yes: gammarips-mcp (mounts POLYGON and
  FMP, both kept), the `mcp.gammarips.com` domain mapping (the CNAME is still at Squarespace), and
  the mcp-reconcile-keys job.
- **ALL 18 JOBS PAUSED 2026-11-04 (owner "pause them").** The Massive cancellation took effect Fri
  10-30 14:32 ET. The key is now free tier: snapshots and options aggregates return 403
  NOT_AUTHORIZED, and reference calls return 429. Every job failed and sent a "Cron failure" alert.
  The last good scan_date is 2026-10-29. The 10-30 scan wrote 0 rows and still returned 200. The
  services stay deployed and the alert policy stays on. Resume the jobs only after Evan restores
  the Massive Stocks and Options plans (commands: `~/workspace/GAMMARIPS-PAUSE-JOBS.txt`). FMP is
  not needed by the pipeline.
- **Mailgun: FIXED 11-02 evening.** A failed payment disabled every key on the shared account from
  about 10-30 to 11-02 (GammaRips digest and TextTimeline sends). Evan updated the payment method.
  The same keys work again, so no secret changed. Verified: the digest delivered at 00:33 UTC 11-03
  and the TextTimeline send returned 200 at 00:37 UTC.
- **Stays off:** signal-judge, gammarips-eval, blog-generator, x-poster, reddit-poster, the
  tournament, the paper cohort, Stripe checkout. The story page is CANCELED.

## Do not

- Do not delete FMP_API_KEY, GOOGLE_API_KEY, or the `mcp` CNAME. The old shutdown owner queue said
  to. It is dead.
- Do not trust "Never redeploy" lines in older shutdown docs. They are superseded by this file.

## Watch

- On resume, dbt-daily-build fails on `assert_opp_surface_labels_fresh`: 142 WINDOW_OPEN rows
  (scan_date 10-23, 10-26, 10-27) cannot fill without options aggregates. It clears on the first
  fill-closed-windows run after Massive is back. The 3 duplicate-key source tests are old history
  (03-06, 06-10) at severity warn and do not fail the build.
- enrichment-trigger is public and runs on a GET (pre-existing). A web probe (VertexProxyCandidateCheck)
  ran the 10-30 enrichment at 02:43 ET, before the 05:30 job. The once-a-day guard stopped a rerun.
- `profit_scout.llm_traces_v1` drops partitions after 180 days.
