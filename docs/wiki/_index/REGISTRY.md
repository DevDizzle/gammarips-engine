# Engine Wiki Registry

One line per note: `[[slug]] — tag — one-line claim`. Schema + conventions:
[`WIKI-SCHEMA.md`](WIKI-SCHEMA.md). This registry is the fastest path to "what is the live
policy and why" — the live V7.1 surface is the Policy section, its evidence is in Findings.

## Policy (`policy/`) — live operating rules
- [[v7-1-tilted-gigo-live-policy]] — policy-adopted — the live policy is V7.1 "Tilted GIGO" = V6 selection + V7 same-day exit + the momentum tilt (`policy_version='V7_1_TILTED_GIGO'`, cohort 2026-06-26)
- [[bracket-tournament-selection]] — policy-adopted — one pick/day or none via a 3-bracket randomized tournament (consensus 3/3=high, no memory/rubric, fail-closed no fallback)
- [[bullish-only-hard-gate]] — policy-adopted — BULLISH-only is a HARD gate (env-toggleable, overrides the bearish-regime caveat for now)
- [[tourney-pool-cap-edge-rank]] — policy-adopted — pool is soft-edge-ranked then capped to TOURNEY_POOL_CAP (12→50; fallback skips the edge-cap)
- [[v7-gigo-same-day-exit]] — policy-adopted — live exit: 10:00 entry / +40% TP / −30% stop / flat 15:45 ET, no trail, no overnight; TIMEOUT>STOP>TARGET
- [[live-oi-floor]] — policy-adopted — re-fetch live OI at ~09:45 ET, drop below OI_FLOOR=1000 (fail-soft to top-8)
- [[earnings-exclusion-rail]] — policy-adopted — safety rail 1: no earnings in the hold/exclusion window (literature-anchored)
- [[regime-rail-vix-term]] — policy-adopted — safety rail 2: fail closed when VIX > VIX3M
- [[entry-day-mark-and-limit]] — policy-adopted — published pick shows a FRESH entry-day mark + fair-value limit (display, not selection)
- [[scorecard-life-distributions]] — policy-adopted — public Track Record shows full-life distributions, not ROI under a fixed exit
- [[public-tracks-pool-not-pick]] — policy-adopted — public surfaces track the ~50-name pool; the daily pick is private
- [[market-holiday-standdown]] — policy-adopted — fail closed (no email/trade/tournament) on any non-trading day
- [[quant-md-final-round-priors]] — policy-adopted — macro/sector report context + quant.md priors injected only at the tournament championship round
- [[trailing-stop-retired-v7]] — policy-adopted (SUPERSEDED) — the 25%-off-peak trailing stop is DEAD under V7 no-trail

## Architecture (`architecture/`) — pipeline / data-contract facts
- [[selection-gates-removed]] — architecture-fact — all selection gates removed 2026-06-04; all enriched signals reach the tournament
- [[enrichment-definition]] — architecture-fact — "enriched" = overnight_score ≥ 4 (floor, EV inverts ≥7) + directional UOA > $500K (all directions)
- [[spread-gate-retired]] — architecture-fact — no Polygon NBBO quotes; spread permanently NULL; prices off last-trade/day-close
- [[assert-no-leakage-gate]] — architecture-fact — every candidate is assert_no_leakage-checked before the LLM (the one non-negotiable)
- [[pipeline-bug-hunt-2026-06-04]] — architecture-fact — 13 silent data bugs fixed (fake spreads, divergence-flip order, technicals lookahead, stale fields)
- [[oi-volume-session-frozen-walled-off]] — architecture-fact — OI/volume are session-frozen snapshots, walled off from the judge, used only in scanner ranking
- [[ledger-cohort-version-labels]] — architecture-fact — cohort labels 5=two-stage, 6=judge_v6, 7=tournament; keep policy_version explicit
- [[enrichment-cost-fix-topn-thinking-cap]] — architecture-fact — cost fix: grounding narrowed to top-50 BULLISH with thinking_budget=0; read cost from Monitoring not the trace table
- [[selection-vs-exclusion-filter-bars]] — architecture-fact — selection filters need OOS; exclusion filters deploy on literature/mechanism
- [[labeled-v1-screen-not-validator]] — architecture-fact — signals_labeled_v1 is a frozen screen (kills bad ideas), never a validator
- [[dataset-regime-confounded]] — architecture-fact — the Feb–Apr 2026 cohort is regime-confounded; do not conclude from it alone
- [[regime-scan-date-leakage-fix]] — architecture-fact — the regime feature is as-of scan_date close (research substrate leakage fix)
- [[sweep-iso-detection-parked]] — untested-hypothesis — sweep/ISO detection (H20) is the top future lever, blocked on a Polygon tier upgrade
- [[atomic-substrate-write-path]] — architecture-fact — substrate writers stage-verify-replace; never delete-then-load
- [[autodetect-outage-class]] — architecture-fact — NEVER autodetect a staged BQ load (all-NULL → STRING mistype broke the pipeline 07-02 and the labeler 07-02→06)
- [[paper-shadow-topscore]] — architecture-fact — walled-off research baseline (tournament vs top-score); never surfaced publicly
- [[opportunity-surface-substrate]] — architecture-fact — enriched_option_outcomes captures MFE/MAE + mom_60 so the exit stays a free variable
- [[option-minute-paths]] — architecture-fact — per-minute premium tape recovers first-crossing order and makes any exit rule scoreable
- [[pool-liquidity-snapshot]] — architecture-fact — interval, cache-first pool-liquidity read for the MCP (distinct from the pick-time OI floor)
- [[notifier-duplicate-send-guard]] — architecture-fact — pick-email guard is a transactional claim keyed on the ET run-day (600s deadline)
- [[service-auth-hardening]] — architecture-fact — Cloud Run services are systemically --allow-unauthenticated; OIDC-then-lock (deploy.sh re-opens the door)
- [[public-stats-fixed-dollar-sizing]] — architecture-fact — public ROI uses fixed-dollar ($500) sizing at the display layer
- [[substrate-empty-pool-fails-loud]] — architecture-fact — a degraded/empty label pool returns 500 + freshness monitor (no silent no-op)
- [[mass-leakage-fail-closed]] — architecture-fact — skip the day when every top candidate scores the 1/1/1 leakage pattern; report stamped by scan_date
- [[dbt-semantic-layer]] — architecture-fact — dbt is reporting/analytics only (isolated dataset, read-side dedup), does not touch execution
- [[gemini-model-map]] — architecture-fact — text-gen=gemini-3.5-flash, picker=gemini-3.1-pro-preview; segment cohorts on any model change
- [[picker-case-memory]] — architecture-fact — picker priors are curated MD injected as instruction blocks, not RAG (quant.md at the final round)
- [[contract-selection-tradeability]] — architecture-fact — _best_contract scores OI-primary tradeability, not unusualness
- [[pnl-sim-realism]] — architecture-fact — paper trader uses symmetric 2% slippage + stale-timeout + late-fill guards
- [[daily-cadence-fallback-removed]] — architecture-fact (SUPERSEDED) — the relax-gates-on-empty-days fallback was removed 2026-06-04
- [[active-days-liquidity-gate-removed]] — architecture-fact (SUPERSEDED) — the active_days_20d trailing-liquidity gate was removed 2026-06-04

## Findings (`findings/`) — tested on our cohorts
- [[bullish-direction-asymmetry]] — proven-on-cohort — bullish EV +4.11% vs bearish −7.71% (3-day era); the one robust direction lever
- [[option-pnl-not-underlying]] — proven-on-cohort — evaluate on OPTION PnL, never underlying (54% vs 41% on the same pool)
- [[pool-delta-calibrated]] — proven-on-cohort — the pool is delta-calibrated; zero directional edge at expiration (N=2,146)
- [[path-calibrated-giveback]] — proven-on-cohort — excursion peaks are IV-calibrated and LATE; the real finding is the giveback (median winner keeps 31% of peak)
- [[three-day-harvest-curve]] — proven-on-cohort — P(touch +20% in 3d)=51% but pops land day 2–3; fixed targets are EV-negative pool-wide
- [[fixed-exit-composites-negative]] — proven-on-cohort — the whole pool under any fixed exit is negative; the exit is the free variable; never publish an ROI headline
- [[exit-velocity-same-day-lever]] — proven-on-cohort — the exit lever is SAME-DAY (velocity + halved tail), not the target magnitude
- [[delta-trap-escape]] — proven-on-cohort — delta is the only contract feature separating won from lost; prefer "enough delta"
- [[momentum-60d-enrichment-tilt]] — fragile-conditional — mom_60 ≥ +0.35 works on a 3-day hold, ZERO edge same-day; the ".1 Tilt", proposer-only
- [[pool-cap-coverage]] — proven-on-cohort — the tournament pool can shrink 50→25 with no demonstrated loss of the winner
- [[moneyness-band-10-13-otm]] — proven-on-cohort — the 10–13% OTM increment is additive; cap widened to 0.13, fallback pinned 0.10
- [[premium-stop-earns-keep]] — proven-on-cohort (3-day era) — dropping the −60% premium stop was ZERO EV; on a short hold it behaves like a time-exit
- [[entry-1000-et]] — policy-adopted — enter ~10:00 ET; earlier entries are a thin-tape mirage
- [[voi-ratio-anti-edge]] — falsified-on-cohort — V/OI > 2 removes 55–63% of winners; anti-edge, gate relaxed
- [[oi-not-quality-signal]] — falsified-on-cohort — OI is a fillability gate, not a quality lever (higher OI monotonically worse)
- [[ride-winners-mean-reverts]] — falsified-on-cohort — chasing recent option winners is an anti-edge (0/17 clear zero)
- [[premium-score-anti-predictive]] — falsified-on-cohort — premium_score as a gate is −3.5pp worse than no filter; flags are features, not gates
- [[bracket-optimization-dead]] — falsified-on-cohort — 0/840 bracket variants profitable; it is not a bracket-tuning problem
- [[trailing-liquidity-floor-dead]] — falsified-on-cohort — trailing-volume floors do not separate fillable from unfillable; dead approach
- [[open-untested-exit-hypotheses]] — untested-hypothesis — H19 (DTE 21–45) and H21 (exit-by-D2) remain untested; proposer color only

## Literature (`literature/`) — external, not tested on our data
- [[earnings-iv-crush]] — literature-established — never hold long single-leg options through the print (IV crush)
- [[volatility-idiosyncratic-trap]] — literature-established — UOA scanners select the most overpriced volatility; the instrument bleeds ~89% of the loss
- [[literature-audit-v5-3-stack]] — literature-established — 12 V5.3 parameters graded against peer-reviewed sources; use literature for structural questions
