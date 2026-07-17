Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-05-11-leakage-fail-closed-and-dte-gate.md
Date: 2026-07-17

# Every candidate is assert_no_leakage-checked before the LLM

Every candidate is passed through `assert_no_leakage` before it reaches the tournament
LLM. Leakage-safety is the program's one non-negotiable — it is physics, not policy — so
the check is fail-closed: a candidate that cannot be shown leakage-clean does not go to the
judge.

This is why point-in-time discipline is enforced everywhere upstream: technicals windows
are bounded to `scan_date` ([[pipeline-bug-hunt-2026-06-04]]), the regime feature is
as-of scan_date close in the research substrate ([[regime-scan-date-leakage-fix]]), and
session-frozen OI/volume are walled off from the judge
([[oi-volume-session-frozen-walled-off]]). The leakage-safety audit is never owner-waivable
(the 30-day-OOS ceremony is).
