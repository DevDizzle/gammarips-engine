# TESTING.md

## Goal
Provide a minimal validation checklist for changes to GammaRips execution policy and ledger-writing logic.

## Before policy changes
- confirm the canonical policy in `docs/TRADING-STRATEGY.md`
- confirm target ledger table name and schema in `docs/DATA-CONTRACTS.md`
- verify whether current code still points at the intended ledger table

## Validation checklist for forward-paper-trader
### 1. Static sanity
- verify no hardcoded secrets remain
- verify policy constants match the documented strategy
- verify table target is `forward_paper_ledger`

### 2. Query sanity
- run a read-only query against `overnight_signals_enriched`
- confirm the trader has NO execution gates — all enriched signals should execute
- confirm enrichment gate is applied upstream: `overnight_score >= 1 AND directional UOA > $500K` (floor accepted at 1, 2026-08-20; spread gate retired 2026-06-05; then edge-ranked/grounded to the top-50 BULLISH names)

### 3. Dedup sanity
- verify only one row per `ticker` per `scan_date` is eligible for execution

### 4. Ledger write sanity
- verify rows include:
  - `policy_version`
  - `policy_gate`
  - `is_skipped`
  - `skip_reason`
- verify VIX is logged as telemetry, not used as a skip reason

### 5. Dry-run / limited run
- run a dry test or one-day cohort simulation before trusting the next live scheduled run
- inspect written rows manually

### 6. Outcome tracking sanity
- verify downstream win tracking still resolves against the chosen ledger target and contract identity fields

## Deploys
For the deploy-time checklist, run the `/deploy-service` skill.
