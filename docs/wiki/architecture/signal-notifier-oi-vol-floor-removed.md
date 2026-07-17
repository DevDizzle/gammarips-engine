Status: superseded
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-30-signal-notifier-liquidity-floor.md (removed by docs/DECISIONS/2026-06-04-bracket-tournament.md)
Date: 2026-07-17

# signal-notifier OI≥20 / vol≥100 floor — added 2026-04-30, later REMOVED

A liquidity floor (`recommended_oi >= 20`, `recommended_volume >= 100`) was added to the
`signal-notifier` LIMIT-1 query on 2026-04-30 after a 40% fill-rejection rate (2 of 5 picks
stamped INVALID_LIQUIDITY on thin scan-time OI). It was later loosened to OI≥10 / vol≥50
during the V5.4 picker-starvation fix (2026-05-12).

Superseded: these scan-time OI/volume floors were REMOVED with the whole selection-gate stack
on 2026-06-04 ([[selection-gates-removed]]) — scan-time liquidity chokes the names that only
fill the next morning, and OI is a fillability signal not a quality one
([[oi-not-quality-signal]]). Decision-time liquidity now comes from the live pick-time
[[live-oi-floor]].
