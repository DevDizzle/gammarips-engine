Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-04-bracket-tournament.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# Selection gates were REMOVED 2026-06-04 — all enriched signals reach the tournament

Since 2026-06-04, ALL enriched signals reach the bracket tournament. The old
`signal-notifier` selection gates are GONE: moneyness, OI, volume, DTE, and V/OI gates,
plus the `active_days_20d` liquidity gate and the daily-cadence fallback.

Rationale: those gates **choked real winners on stale scan-time OI**. The overnight sweep
only becomes visible open interest the NEXT morning; the trade enters at 10:00 ET and rides
the OI build ([[entry-1000-et]]). Gating on the frozen snapshot removed exactly the names
that were about to fill.

What remains upstream is minimal and deliberate: `enrichment-trigger` defines "enriched"
([[enrichment-definition]]), `signal-notifier` keeps exactly two safety rails
([[earnings-exclusion-rail]], [[regime-rail-vix-term]]) plus the pick-time
[[live-oi-floor]]. Do NOT re-add trader-side or notifier-side selection gates — that path
is closed by policy (new gates require Phase 2 feature discovery).
