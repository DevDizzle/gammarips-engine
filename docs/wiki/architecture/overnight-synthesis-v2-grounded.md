Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-09-report-v2-literature-grounded.md
Date: 2026-07-17

# Overnight report is literature-grounded report_v2 (stamped prompt_version)

The `overnight-report-generator` ships a literature-grounded `report_v2` prompt/payload. The
`daily_reports/{scan_date}` doc keeps its backward-compatible top-level fields (`title`,
`headline`, `content`, count rollups) for `signal-notifier` / x-poster / webapp, and adds
`prompt_version: "report_v2"` (also stamped in trace logs), `sentiment_shift` (today's
bullish share vs 14d mean/std/z-score) and `sector_concentration`.

The stamped `prompt_version` is the required semantic label for eval/cohort attribution
(owner rule: keep a light prompt version even without SHA-hashing every tweak). The daily
report later gained deterministic Macro & Regime + Sector Tape blocks
([[quant-md-final-round-priors]]); it is the context the tournament reads, and it must be
written before the pick runs ([[pipeline-cron-schedule]]).