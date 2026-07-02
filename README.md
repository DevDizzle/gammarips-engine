# GammaRips Engine

Overnight options-flow **intelligence engine**: scan the US options market for unusual activity, curate *hard* (anti-firehose) down to a tiny high-signal BULLISH pool, and surface each candidate's **opportunity surface** (realized MFE/MAE excursions) — profit *potential*, with the exit left as a free variable. This repo is the backend + research substrate.

## The product

The human web UI (gammarips.com) is **free** — it is the SEO top-of-funnel. The monetized product is **MCP access** for bring-your-own-agent traders (`gammarips-mcp`, a **separate repo**): data + tools sold as a data vendor — the curated pool, historical opportunity/outcome surfaces, and selection methodology — **not a return and not single-contract advice**. The MCP exposes primitives each user's agent reasons over to its own contract (never a pick-returning endpoint). The engine surfaces good contracts; profitability depends on how they're traded (discretionary entry/exit, human or agent).

## Strategy: V7.1 "Tilted GIGO" (live)

At most one BULLISH options alert per trading day, chosen by a randomized bracket **tournament** and executed **same-day**:

- **Selection** (the V6 tournament, unchanged): the enriched BULLISH pool is edge-ranked (|delta| 0.20–0.46 + a 60-day-momentum soft tilt), capped, and live-OI-floored (≥ 1000 at the ~09:45 ET pick); 3 independent brackets each reduce the pool in batches of ≤10 (top-2 advance) and vote a **consensus winner** at `signal-judge` (`tournament_v1`, `gemini-3.1-pro-preview`).
- **Exit** (V7 GIGO): 10:00 ET entry → **+40% target / −30% stop, flat 15:45 ET** — no trail, no overnight.
- **Safety rails**: no earnings in the hold window + regime fail-closed (`VIX ≤ VIX3M`). No trader-side gates — signal quality lives upstream.
- `policy_version='V7_1_TILTED_GIGO'`, live cohort since 2026-06-26. **Paper-only.** Ledger: `forward_paper_ledger`.

Canonical policy: `docs/TRADING-STRATEGY.md`. One-page operator view: `CHEAT-SHEET.md`.

### Data flow

```
23:00 ET   overnight-scanner       Scan full US options market for unusual institutional flow
05:30 ET   enrichment-trigger      Edge-rank to top-50 BULLISH + ground news → overnight_signals_enriched
07:00 ET   overnight-report-gen    Gemini editorial synthesis (daily report = tournament context)
09:45 ET   signal-notifier         Safety rails + live-OI floor → signal-judge tournament → todays_pick + email
10:00 ET   forward-paper-trader    Same-day GIGO bracket sim (10:00 entry, 15:45 flat) → forward_paper_ledger
           win-tracker             Post-trade outcome tracking
```

## Services (this repo)

| Service | Directory | Purpose |
|---|---|---|
| Scanner | `overnight-scanner/`, `src/` | Nightly Polygon options-flow scan + signal scoring |
| Enrichment | `enrichment-trigger/` | Edge-rank + Gemini/Polygon enrichment → `overnight_signals_enriched` (atomic write path; never `autodetect`) |
| Report | `overnight-report-generator/` | Gemini editorial synthesis + macro/sector context for the tournament |
| Signal Judge | `signal-judge/` | The bracket-tournament picker (`tournament_v1`); IAM-locked |
| Signal Notifier | `signal-notifier/` | Safety rails + live-OI floor, runs the tournament, writes `todays_pick`, emails operator/subscribers, owns cohort stats |
| Paper Trader | `forward-paper-trader/` | Same-day GIGO paper trading + research-shadow writers + IV cache |
| Win Tracker | `win-tracker/` | Post-trade outcome tracking |
| Eval Service | `gammarips-eval/` | LLM eval (monitoring-only, non-gating) |
| X Poster | `x-poster/` | ADK multi-agent X publisher (@gammarips) |
| Blog Generator | `blog-generator/` | ADK multi-agent blog writer → Firestore `blog_posts` |
| ~~Agent Arena~~ | `agent-arena/` | **DEAD** (deprecated 2026-05-04) — kept for history only |
| **MCP (product)** | `gammarips-mcp` (**separate repo**) | Monetized bring-your-own-agent surface — data + tool primitives, not a pick |

## Research substrate

`enriched_option_outcomes` replays the full BULLISH pool with the **opportunity surface** (MFE/MAE `opp_*`) + an interim 3-day label arm; leakage-safe agent views `enriched_features_v1` + `overnight_signals_enriched_safe`; `underlying_daily_bars` is the point-in-time momentum cache. This substrate feeds both edge research and the MCP data product. Leakage-safety is enforced by `gammarips-review` and the feature/label column tags.

## Tech stack

- **Language:** Python 3.12
- **Runtime:** GCP Cloud Run (source deploy)
- **Data:** BigQuery (canonical), Firestore (picks / eval / stats), GCS (ticker universe)
- **APIs:** Polygon (options/equity), FRED (VIX), Gemini (enrichment, reports, tournament)
- **Framework:** Flask + Gunicorn; ADK for the x-poster / blog-generator agents
- **Orchestration:** Cloud Scheduler, Pub/Sub

## Deployment

Each service has its own `Dockerfile` + `deploy.sh`; all deploy to Cloud Run in `us-central1`.

```bash
cd forward-paper-trader && bash deploy.sh
cd enrichment-trigger && bash deploy.sh
cd signal-notifier && bash deploy.sh
```

## Documentation

- `docs/TRADING-STRATEGY.md` — canonical execution policy
- `docs/ARCHITECTURE.md` — system map + data flow
- `docs/DATA-CONTRACTS.md` — BigQuery schemas (incl. the research substrate)
- `docs/DECISIONS/` — dated decision trail
- `docs/EVAL-SYSTEM.md` — eval framework
- `CHEAT-SHEET.md` — one-page operator view
- `NEXT_SESSION_PROMPT.md` — live session handoff

Research reports + historical analysis live in `docs/research_reports/` and `docs/archive/` (historical, not authoritative).
