# Engine Wiki Registry

One line per note: `[[slug]] — tag — one-line claim`. Schema + conventions:
[`WIKI-SCHEMA.md`](WIKI-SCHEMA.md). This registry is the fastest path to "what is the live
policy and why" — the live V7.1 surface is the Policy section, its evidence is in Findings.

## Policy (`policy/`) — live operating rules
- [[v7-1-tilted-gigo-live-policy]] — policy-adopted — the live policy is V7.1 "Tilted GIGO" = V6 selection + V7 same-day exit + the momentum tilt (`policy_version='V7_1_TILTED_GIGO'`; cohort start lives in `signal-notifier/main.py`, 2026-08-21 as of the 08-20 reset)
- [[bracket-tournament-selection]] — policy-adopted — one pick/day or none via a 3-bracket randomized tournament (consensus 3/3=high, no memory/rubric, fail-closed no fallback)
- [[bullish-only-hard-gate]] — policy-adopted — BULLISH-only is a HARD gate (env-toggleable, overrides the bearish-regime caveat for now)
- [[tourney-pool-cap-edge-rank]] — policy-adopted — pool is soft-edge-ranked then capped to TOURNEY_POOL_CAP (live value 12, code default; fallback skips the edge-cap)
- [[v7-gigo-same-day-exit]] — policy-adopted — live exit: 10:00 entry / +40% TP / −30% stop / flat 15:45 ET, no trail, no overnight; TIMEOUT>STOP>TARGET
- [[live-oi-floor]] — policy-adopted — two-tier slate floor at ~09:52 ET (early prints `PRINT_FLOOR_MIN=25` since 08-20, then OI_FLOOR=1000); a dropped candidate never comes back
- [[no-liquid-candidates-no-pick]] — policy-adopted — when nothing clears the liquidity floors the engine stands down instead of ranking the reject pile
- [[earnings-exclusion-rail]] — policy-adopted — safety rail 1: no earnings in the hold/exclusion window (literature-anchored)
- [[regime-rail-vix-term]] — policy-adopted — safety rail 2: fail closed when VIX > VIX3M
- [[entry-day-mark-and-limit]] — policy-adopted — published pick shows a date-validated entry-day mark + fair-value limit (display, not selection); the mark is a delayed day.close and prior-session prices are REFUSED (amended 08-14)
- [[scorecard-life-distributions]] — policy-adopted — public Track Record shows full-life distributions, not ROI under a fixed exit
- [[public-tracks-pool-not-pick]] — policy-adopted — public surfaces track the ~50-name pool; the daily pick is private
- [[market-holiday-standdown]] — policy-adopted — fail closed (no email/trade/tournament) on any non-trading day
- [[quant-md-final-round-priors]] — policy-adopted — macro/sector report context + quant.md priors injected only at the tournament championship round
- [[trailing-stop-retired-v7]] — policy-adopted (SUPERSEDED) — the 25%-off-peak trailing stop is DEAD under V7 no-trail
- [[content-receipts-not-claims]] — policy-adopted — public content posts RECEIPTS (timestamped, quote-tweeted on close), not picks or claims
- [[v5-3-target-80-retired]] — policy-adopted (RETIRED) — the V5.3 +80/−60/3-day exit is history; live exit is same-day GIGO

## Architecture (`architecture/`) — pipeline / data-contract facts
- [[selection-gates-removed]] — architecture-fact — all selection gates removed 2026-06-04; all enriched signals reach the tournament
- [[enrichment-definition]] — architecture-fact — "enriched" = overnight_score ≥ 1 (floor accepted at 1 on 08-20, cosmetic; EV inverts ≥7) + directional UOA > $500K (all directions)
- [[spread-gate-retired]] — architecture-fact — no Polygon NBBO quotes; spread permanently NULL; prices off last-trade/day-close
- [[assert-no-leakage-gate]] — architecture-fact — every candidate is assert_no_leakage-checked before the LLM (the one non-negotiable)
- [[pipeline-bug-hunt-2026-06-04]] — architecture-fact — 13 silent data bugs fixed (fake spreads, divergence-flip order, technicals lookahead, stale fields)
- [[oi-volume-session-frozen-walled-off]] — architecture-fact — OI/volume are session-frozen snapshots, walled off from the judge, used only in scanner ranking
- [[ledger-cohort-version-labels]] — architecture-fact — cohort labels 5=two-stage, 6=judge_v6, 7=tournament; keep policy_version explicit
- [[enrichment-cost-fix-topn-thinking-cap]] — architecture-fact — cost fix: grounding narrowed to top-50 BULLISH with thinking_budget=0; the Monitoring-only cost rule holds only for trace rows before 2026-08-17
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
- [[polygon-snapshot-never-zero-day-bar]] — architecture-fact — Polygon's option snapshot serves the prior session's bar instead of a zero, so day.volume alone can never mean "no prints today"; read day.last_updated
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

### Architecture — services, data-contract details, prior-era markers
- [[eval-system-monitoring-only]] — architecture-fact — the LLM eval system is monitoring-first and never gates a pick/report/deploy
- [[llm-cost-from-billing-catalog]] — architecture-fact — trace_logger prices from the Cloud Billing Catalog, unknown models log NULL; cost_usd is trustworthy only from 2026-08-17 (~26x low before)
- [[content-services-x-poster-blog]] — architecture-fact — x-poster + blog-generator ADK services + shared content lib are the distribution layer
- [[mcp-sole-attack-surface]] — architecture-fact — gammarips-mcp is the sole (sandboxed) attack surface for paid-agent interactions; never a pick endpoint
- [[content-machine-weekly-cadence]] — architecture-fact — the 4-surface content machine (X/blog/reddit/email) runs weekly autonomous cadence off real ledger+report data
- [[todays-pick-dual-write]] — architecture-fact — signal-notifier dual-writes todays_pick under {scan_date} AND {entry_day}
- [[pipeline-cron-schedule]] — architecture-fact — daily cron order is enrichment → report → notifier; the report must be written before the pick runs
- [[cohort-reset-on-filter-change]] — architecture-fact — truncate the ledger + start a fresh cohort whenever the selection filter materially changes
- [[cohort-reset-live-oi]] — architecture-fact (SUPERSEDED) — the 2026-06-25 reset that set the then-current LIVE_COHORT_START_DATE=2026-06-26; three later resets, live value in signal-notifier/main.py
- [[moneyness-sign-direction-aware]] — architecture-fact — moneyness_pct is direction-aware (positive = OTM) for both calls and puts
- [[scanner-sector-detail-fetch]] — architecture-fact — the scanner fetches per-ticker SIC sector detail for movers only (fixed the NULL-sector bug)
- [[sector-persisted-on-signals]] — architecture-fact — sector/industry is persisted onto signal docs for SEO internal-linking + related-signals
- [[overnight-synthesis-v2-grounded]] — architecture-fact — the daily report is literature-grounded report_v2 with a stamped prompt_version
- [[trader-simulates-todays-pick-only]] — architecture-fact — the trader simulates ONLY todays_pick; one ledger row per day
- [[trader-eod-mark-to-market]] — architecture-fact — EOD mark-to-market; skip-row columns (ticker/contract/direction) must be NULLABLE
- [[deferred-alpaca-agent]] — untested-hypothesis — real-money Alpaca execution is DEFERRED until EV is proven (worst case = real money on an unmeasured edge)
- [[deferred-few-shot-exemplars]] — untested-hypothesis — few-shot picker exemplars deferred until ≥15 closed trades (≥5W/≥5L)
- [[intraday-hold-shadow-retired]] — architecture-fact (RETIRED) — the day-trade shadow collapsed once V7 made the live exit intraday
- [[x-poster-revamp-agentic]] — architecture-fact — @gammarips revamp: dead paid-pick CTAs killed, pool-level receipts, pick hard-private
- [[signal-notifier-oi-vol-floor-removed]] — architecture-fact (SUPERSEDED) — the OI≥20/vol≥100 scan-time floor was added 04-30, later removed 06-04
- [[enrichment-funnel-baseline]] — architecture-fact (SUPERSEDED) — the V5.3-era funnel baseline (~2,264 raw → ~75/day); superseded by top-50 grounding
- [[ranker-voi-first-retired]] — architecture-fact (RETIRED) — the V/OI-first deterministic ranker; the whole ranker era ended at the tournament
- [[v5-3-monetization-retired]] — architecture-fact (RETIRED) — the V5.3-era WhatsApp/tiered-pricing plan; now free-UI / paid-MCP
- [[webapp-launch-cleanup-ssr]] — architecture-fact (RETIRED) — webapp-only V5.3 launch cleanup + SSR crawlability (engine untouched)
- [[v5-4-promotion-retired]] — architecture-fact (RETIRED) — V5.4 promoted to canonical 2026-05-08; later collapsed to V6/V7
- [[v5-4-scorer-picker-retired]] — architecture-fact (RETIRED) — the V5.4 Scorer→Picker pair; collapsed to a single judge, then the tournament

## Findings (`findings/`) — tested on our cohorts
- [[bullish-direction-asymmetry]] — proven-on-cohort — bullish EV +4.11% vs bearish −7.71% (3-day era); the one robust direction lever
- [[option-pnl-not-underlying]] — proven-on-cohort — evaluate on OPTION PnL, never underlying (54% vs 41% on the same pool)
- [[pool-delta-calibrated]] — proven-on-cohort — the pool is delta-calibrated; zero directional edge at expiration (N=2,146)
- [[path-calibrated-giveback]] — proven-on-cohort — excursion peaks are IV-calibrated and LATE; the real finding is the giveback (median winner keeps 31% of peak)
- [[three-day-harvest-curve]] — proven-on-cohort — P(touch +20% in 3d)=51% but pops land day 2–3; fixed targets are EV-negative pool-wide
- [[fixed-exit-composites-negative]] — proven-on-cohort — the whole pool under any fixed exit is negative; the exit is the free variable; never publish an ROI headline
- [[ghost-rows-flatter-pool-composites]] — proven-on-cohort — ghost rows exit at fabricated near-flat marks (16.8% carry exactly −1.9608%), so every whole-pool composite is optimistic by construction (−4.67% vs tradeable −9.59%)
- [[execution-risk-is-exit-certainty]] — proven-on-cohort — execution risk is exit certainty, not spread: stop fills slip one-sided (median −3.1%, thin names −10.3%), prints-by-10:00 is the dominant observable, premium does not predict liquidity
- [[window-mismatch-3day-vs-same-day]] — proven-on-cohort — the harvest/surface views are 3-day while V7.1 exits same-day; quoting a 3-day statistic at a same-day decision inverts the answer
- [[exit-velocity-same-day-lever]] — proven-on-cohort — the exit lever is SAME-DAY (velocity + halved tail), not the target magnitude
- [[delta-trap-escape]] — proven-on-cohort — delta is the only contract feature separating won from lost; prefer "enough delta"
- [[momentum-60d-enrichment-tilt]] — fragile-conditional — mom_60 ≥ +0.35 works on a 3-day hold, ZERO edge same-day; the ".1 Tilt", proposer-only
- [[pool-cap-coverage]] — proven-on-cohort — the tournament pool can shrink 50→25 with no demonstrated loss of the winner
- [[moneyness-band-10-13-otm]] — proven-on-cohort — the 10–13% OTM increment is additive; cap widened to 0.13, fallback pinned 0.10
- [[premium-stop-earns-keep]] — proven-on-cohort (3-day era) — dropping the −60% premium stop was ZERO EV; on a short hold it behaves like a time-exit
- [[entry-1000-et]] — policy-adopted — enter ~10:00 ET; earlier entries are a thin-tape mirage; the LATER-entry question is an OPEN owner call since 08-19
- [[first-hour-bleed]] — proven-on-cohort — the day's bleed concentrates in the 10:00→11:00 window (−5.32% mean, tradeable N=548); a later entry loses less and gains less, no edge either way
- [[voi-ratio-anti-edge]] — falsified-on-cohort — V/OI > 2 removes 55–63% of winners; anti-edge, gate relaxed
- [[oi-not-quality-signal]] — falsified-on-cohort — OI is a fillability gate, not a quality lever (higher OI monotonically worse)
- [[ride-winners-mean-reverts]] — falsified-on-cohort — chasing recent option winners is an anti-edge (0/17 clear zero)
- [[premium-score-anti-predictive]] — falsified-on-cohort — premium_score as a gate is −3.5pp worse than no filter; flags are features, not gates
- [[bracket-optimization-dead]] — falsified-on-cohort — 0/840 bracket variants profitable; it is not a bracket-tuning problem
- [[overnight-hold-breaks-the-stop]] — falsified-on-cohort — PM entry / morning pop refuted: the overnight hold removes the stop (p05 −31% → −53%) and every liquid-tier PM variant is negative
- [[contract-score-lead-dead]] — falsified-on-cohort — the cap-50-era contract_score lead (AUC 0.552) failed its pre-committed re-test (0.481, N=737); closed, never re-slice; no demonstrated within-pool ranking edge
- [[catalyst-atr-inversion-refuted]] — falsified-on-cohort — the catalyst/ATR "inversions" are a between-day tape artifact (day-demeaned AUC 0.499, N=3,040); do not down-rank high-catalyst/high-ATR within a day
- [[trailing-liquidity-floor-dead]] — falsified-on-cohort — trailing-volume floors do not separate fillable from unfillable; dead approach
- [[open-untested-exit-hypotheses]] — untested-hypothesis — H19 (DTE 21–45) and H21 (exit-by-D2) remain untested; proposer color only
- [[lit-audit-h11-h12-spread-moneyness]] — literature-established (SUPERSEDED) — H11 spread 10→8% and H12 moneyness 15→10%; both later superseded

## Literature (`literature/`) — external, not tested on our data
- [[earnings-iv-crush]] — literature-established — never hold long single-leg options through the print (IV crush)
- [[volatility-idiosyncratic-trap]] — literature-established — UOA scanners select the most overpriced volatility; the instrument bleeds ~89% of the loss
- [[literature-audit-v5-3-stack]] — literature-established — 12 V5.3 parameters graded against peer-reviewed sources; use literature for structural questions
