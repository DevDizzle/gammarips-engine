# 2026-08-20 — Polygon key rotation DROPPED (owner call)

**Status: DECIDED. Do not re-raise in any framing.**

## Decision

The owner keeps the current `POLYGON_API_KEY`. There is no rotation. The
studies and all other Polygon work use the key as it is, from Secret
Manager.

## Record

- The key leaked into a repo file 2026-07-06 and into an error echo
  2026-08-05. Both were contained.
- The owner pasted the key value into a chat session 2026-08-20.
- The owner accepted the risk 2026-08-20 and directed immediate use.
- The key was verified live from Secret Manager the same day (one
  grouped-daily call, HTTP 200).

## Consequences

- The two pre-registered studies are unblocked. All Polygon phases can run.
- Scripts read the key with
  `gcloud secrets versions access latest --secret=POLYGON_API_KEY
  --project=profitscout-fida8` and `.strip()` the value. No script stores
  the key in a file or prints it.
- Scrubbed surfaces (this note supersedes them): `NEXT_SESSION_PROMPT.md`
  owner queue, `FINDINGS_LEDGER.md` §2026-08-20 caveat, the status lines in
  the two study specs.
