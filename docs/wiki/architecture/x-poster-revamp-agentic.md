Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-09-x-poster-revamp.md
Date: 2026-07-17

# x-poster revamp — dead paid-pick CTAs killed, pool-level receipts, pick hard-private

The 2026-07-09 @gammarips revamp brought the X surface into line with the current posture:
- **Killed dead-product CTAs** — the pinned tweet + templates still sold the retired paid
  email pick (fan-out retired 2026-07-03).
- **The daily pick is now PRIVATE** (scalping optics), so `signal` / `callback` / `scorecard`
  post types are hard-403'd; public receipts are POOL-level, not pick-level
  ([[public-tracks-pool-not-pick]], [[content-receipts-not-claims]]).
- Added the agentic-trading education angle + new post types + a metrics loop; fixed the
  report cron that fired 06:30 ET BEFORE the 07:00 ET report generator and no-op'd every week
  ([[pipeline-cron-schedule]]).

Pin/bio/replies remain owner-manual. This is the current @gammarips content posture.
