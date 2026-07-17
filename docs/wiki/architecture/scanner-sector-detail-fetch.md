Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-09-scanner-sector-detail-endpoint.md
Date: 2026-07-17

# Scanner fetches per-ticker SIC sector detail for movers only

The overnight scanner no longer pre-loads sector/industry for the entire stock universe; it
fetches per-ticker SIC details **only for movers** (~100–300 tickers), called after pass-2
options enrichment and before scoring/cluster boost. This fixed `overnight_signals.sector`
being NULL on every row since at least 2026-03-16 (the universe pre-load was the broken
path).

Sector originates here and is later persisted onto the Firestore signal docs for SEO
internal-linking + same-sector related-signals ([[sector-persisted-on-signals]]); the
tournament also reads a sector-rotation panel from the report ([[quant-md-final-round-priors]]).
