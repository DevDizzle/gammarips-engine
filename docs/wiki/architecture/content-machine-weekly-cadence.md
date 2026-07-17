Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-30-content-machine-live.md
Date: 2026-07-17

# The 4-surface content machine runs on weekly autonomous cadence

The distribution "content machine" went live 2026-04-30 across four surfaces on weekly
autonomous cadence: x-poster (X), blog-generator (webapp `/blog`), a reddit-drafter
(`/draft_reddit` for Tier-1 subs), and email-marketing. It runs off real ledger + report
data — no execution-policy change.

Durable operational facts from this launch: x-poster callbacks are restricted to
publicly-posted tickers (a receipt can only reference what was already public,
[[content-receipts-not-claims]]); the daily-reports Firestore collection-name bug was fixed
here; blog-generator uses the default compute service account
(see the auto-memory `feedback_default_compute_sa`). The current @gammarips posture (dead
CTAs killed, pool-level receipts) is [[x-poster-revamp-agentic]].
