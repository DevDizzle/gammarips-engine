Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-28-blog-gen-prod-text-only-x.md
Date: 2026-07-17

# signal-notifier dual-writes todays_pick under {scan_date} AND {entry_day}

`signal-notifier` writes the daily pick doc under BOTH `todays_pick/{scan_date}` and
`todays_pick/{entry_day}` doc ids, so downstream readers (x-poster, webapp, MCP) can fetch
"today's pick" without doing calendar math to translate between the scan night and the entry
morning.

This dual-write shipped in the 2026-04-28 content bundle (which also made X posting text-only
and put blog-generator into production). The duplicate-send guard keys on the ET run-day, a
separate concern ([[notifier-duplicate-send-guard]]); the entry-day mark/limit fields are
written onto this same doc after the pick ([[entry-day-mark-and-limit]]).
