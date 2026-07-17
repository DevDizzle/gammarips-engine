Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-11-leakage-fail-closed-and-dte-gate.md
Date: 2026-07-17

# Fail-closed on mass leakage; report scan_date stamping

Two coupled leakage safeguards landed after the VAL incident (the inaugural V5.4 pick shipped
a `confidence=low` signal the leakage detector had already flagged):
- **Mass-leakage fail-close.** When EVERY top candidate scores the prescribed leakage pattern
  (1/1/1), selection short-circuits and returns `skip=True, skip_reason="mass_leakage"`
  rather than picking a leaked signal. This is the era-appropriate expression of the
  non-negotiable leakage discipline ([[assert-no-leakage-gate]]).
- **Report scan_date stamping.** `overnight-report-generator` stamps the
  `daily_reports/{underlying_scan_date}` doc BY scan_date (title/headline/content/scan_date
  rewritten), fixing a dual-write that had entry-day-stamped both keys.

Historical note: this same decision also added a `DTE 7–30` gate at `signal-notifier`, but
that DTE selection gate was REMOVED with the rest of the selection gates on 2026-06-04
([[selection-gates-removed]]). The leakage fail-close and report stamping are the durable
parts.
