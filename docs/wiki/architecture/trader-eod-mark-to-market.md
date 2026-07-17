Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md
Date: 2026-07-17

# Trader EOD mark-to-market + skip-rows must allow NULL ticker/contract/direction

`forward-paper-trader` marks open positions to market at end of day (the `/mark_to_market`
endpoint), and its skip records (`MISSING` / `NO_PICK` / `FETCH_FAILED`) write
`ticker=None`, `recommended_contract=None`, `direction=None` — so those ledger columns must
be **NULLABLE**, not REQUIRED. Both facts come from the 2026-05-15 resurrection, where the
ledger sat empty for four trading days because REQUIRED columns rejected legitimate skip rows
and a missing `google-cloud-firestore` dependency 503'd every boot.

Durable lessons: keep skip-path columns nullable; pin runtime deps explicitly (bigquery no
longer transitively exposes the firestore submodule). Under V7 the exit is same-day, so the
overnight MTM matters mainly for research arms, but the endpoint and the nullable-skip-row
contract remain.
