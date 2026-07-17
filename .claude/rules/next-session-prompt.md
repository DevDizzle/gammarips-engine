# Rules for NEXT_SESSION_PROMPT.md

This file is a HANDOFF, not a log. Owner call 2026-07-17, after append-only updates
grew it to 172KB/722 lines with ~90% stale content.

- REFRESH in place: rewrite or delete stale content on every update. NEVER prepend a
  new dated block on top of old ones — that is the failure mode this rule exists for.
- Hard cap ~100 lines. If an update doesn't fit, you are logging, not handing off.
- Content leaving the file graduates to its permanent home:
  - execution-policy changes → `docs/DECISIONS/` (dated file — usually already exists)
  - research results → `docs/research_reports/FINDINGS_LEDGER.md` / `INTELLIGENCE_BRIEF.md`
  - durable operational facts and gotchas → auto-memory
  - everything else → `docs/archive/` (archive, never delete)
- A block leaves when its work ships, its checkpoint passes, or its content is promoted.
  "Kept for context" is what `DECISIONS/` and `docs/archive/` are for.
- Keep the section shape: Active workstream · Owner queue · Watch/dated checkpoints ·
  Open engineering · Live posture. Pointers over prose — link the doc, don't restate it.
