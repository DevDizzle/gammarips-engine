# GammaRips Engine

Overnight options-flow scanning, enrichment, paper trading, and performance tracking. The goal is to identify unusual options activity (whale trades) and paper-trade them to validate signal quality before committing real capital.

## Architecture

Single paper-trading pipeline on GCP Cloud Run, writing to BigQuery.

**Strategy: Whale Following** -- Deployed April 2026. Relaxed enrichment gates: `overnight_score >= 1`, `spread <= 10%`, directional UOA > $500K. No trader-side filters -- all enriched signals execute. Premium flags computed and stored as features for post-hoc discovery. Goal: collect 500+ trades for tree-based feature importance analysis. Ledger: `forward_paper_ledger`.

### Data Flow

```
23:00 ET   Scanner           Scans full US options market for unusual institutional flow
05:30 ET   Enrichment        Whale filter enrichment (score >= 1, spread <= 10%, UOA > $500K)
16:30 ET   Paper Trader      Enters/exits paper positions at market close
           Win Tracker       Tracks signal performance over holding period
           Overnight Report  Gemini editorial synthesis of daily results
```

## Services

| Service | Directory | Purpose |
|---|---|---|
| Scanner | `overnight-scanner/`, `src/` | Nightly Polygon options flow scan and signal scoring |
| Enrichment | `enrichment-trigger/` | Gemini + Polygon enrichment pipeline |
| Paper Trader | `forward-paper-trader/` | Paper trading + IV cache |
| Agent Arena | `agent-arena/` | Multi-model debate and signal ranking |
| Overnight Report | `overnight-report-generator/` | Gemini editorial synthesis |
| Eval Service | `gammarips-eval/` | LLM eval (monitoring-only, non-gating) |
| Win Tracker | `win-tracker/` | Post-trade outcome tracking |
| Signal Notifier | `signal-notifier/` | Alert notifications |

## Tech Stack

- **Language:** Python 3.12
- **Runtime:** GCP Cloud Run (source deploy)
- **Data:** BigQuery (canonical), Firestore (eval reports), GCS (ticker universe)
- **APIs:** Polygon (options/equity data), FRED (VIX), Gemini (enrichment + reports)
- **Framework:** Flask + Gunicorn
- **Orchestration:** Cloud Scheduler, Pub/Sub

## Deployment

Each service has its own `Dockerfile` and `deploy.sh`. All deploy to Cloud Run in `us-central1`.

```bash
cd forward-paper-trader && bash deploy.sh
cd enrichment-trigger && bash deploy.sh
cd agent-arena && bash deploy.sh
```

## Documentation

Detailed docs live in `docs/`:

- `docs/TRADING-STRATEGY.md` -- Canonical execution policy
- `docs/ARCHITECTURE.md` -- System map and data flow
- `docs/DATA-CONTRACTS.md` -- BigQuery schemas
- `docs/DECISIONS/` -- Decision trail for policy changes
- `docs/EVAL-SYSTEM.md` -- Eval framework

Research reports and historical analysis are in `docs/research_reports/` and `_archive/`.
