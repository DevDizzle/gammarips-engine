Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-06-paper-trader-reset-and-stats-surface.md
Date: 2026-07-17

# Reset the cohort whenever the selection filter materially changes

Standing practice: when the selection filter materially changes, **truncate
`forward_paper_ledger` and start a fresh cohort** rather than pooling pre-/post-change trades
(apples-to-oranges EV). Established 2026-05-06 (the lit-audit deploys changed the cohort, so
the 562 pre-audit closed trades were dropped), and applied repeatedly since — V5.4 promotion,
V7 cutover, V7.1 tilt reset ([[ledger-cohort-version-labels]]), live-OI reset
([[cohort-reset-live-oi]]).

The same decision stood up the public `cohort_stats/current` Firestore social-proof surface
(trades / ROI / win-rate / invested, visible to unauthenticated users) as the honest-funnel
mechanism — later re-based to fixed-dollar sizing ([[public-stats-fixed-dollar-sizing]]) and
then re-scoped to track the POOL, not the pick ([[public-tracks-pool-not-pick]]).
