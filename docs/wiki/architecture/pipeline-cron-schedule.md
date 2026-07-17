Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-06-signal-notifier-0730-cron.md; docs/DECISIONS/2026-05-09-report-wiring-fix-and-5-8-backfill.md
Date: 2026-07-17

# Daily pipeline cron ordering — enrichment → report → notifier (report BEFORE the pick)

The daily pipeline must fire in dependency order: **enrichment-trigger → overnight-report-
generator → signal-notifier**. Two fixes established this: the notifier was moved earlier
(09:00→07:30 ET) to close the idle gap and give subscribers pre-market planning time
(2026-05-06); and the report generator was moved AHEAD of the notifier (2026-05-09) after it
was discovered the report ran ~45 min AFTER the pick, so the ranker was reading an empty
report and losing all macro/sector context.

Load-bearing invariant: the **report must be written before the pick runs** so selection can
consume it ([[quant-md-final-round-priors]] injects report context at the tournament final
round). Exact cron times have drifted since (e.g. enrichment ~05:30, report ~07:00); the
durable rule is the ORDER, not the specific minutes. The x-poster signal/marketing crons run
on their own schedule, decoupled from delivery freshness.
