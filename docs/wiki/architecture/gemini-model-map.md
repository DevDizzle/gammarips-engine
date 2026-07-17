Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md
Date: 2026-07-17

# Gemini model map + segment cohorts on any model change

Model roles in the engine (as of the 2026-05-27 flash migration):
- **Text generation** (reports, enrichment grounding, editorial) — `gemini-3.5-flash` (GA
  Flash; migrated off `gemini-3-flash-preview`).
- **The tournament picker** — deliberately a pro-tier decider, NOT on the flash cull list
  (`gemini-3.1-pro-preview`, see [[bracket-tournament-selection]]).
- Out of scope of flash migrations: x-poster image gen, the VAPO tuning script, and the dead
  `agent-arena`.

Durable rule: on ANY model change, **segment the paper cohort by model version** (e.g.
`v5_4_scorer_model` / a `scan_date` floor) so pre-change and post-change closed trades are
NOT pooled for the N-trade EV gates. Also note enrichment grounding runs with
`thinking_budget=0` for cost ([[enrichment-cost-fix-topn-thinking-cap]]).
