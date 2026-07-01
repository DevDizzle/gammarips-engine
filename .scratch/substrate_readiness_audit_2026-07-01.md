================================================================================
SUBSTRATE-READINESS AUDIT — enriched_option_outcomes + upstream feed + collector
Date: 2026-07-01
Provenance: dynamic Workflow "substrate-readiness-audit" (run wf_0f464253-ca3,
            7 agents: 4 parallel auditors -> adversarial verify of the 2 critical
            claims -> synthesis). Read-only.
Purpose: verify the feature/data substrate is complete, leakage-safe, reliable,
            and usable by headless edge-hunting agents. Foundation for: Option 1
            (curated data product), Option 2 (operator discretionary trading),
            Option 3 (VM data-science agents).
================================================================================

VERDICT: NOT-READY (fixable, not fatal).
The daily pipeline is ALIVE, FRESH, and its labels are byte-faithful to production
— but there is ONE genuine live leak, silent-data-loss landmines, and the substrate
is structurally unable to answer the very question it exists for (the 3-day
mom_60/delta finding). Close the 7 ranked must-fixes (WRITE PATH FIRST) before
turning headless agents loose or trusting any lever screen.

--------------------------------------------------------------------------------
WHAT IS ALREADY SOLID (trust it)
--------------------------------------------------------------------------------
- Cadence is rock-solid: exactly 50 rows / 50 distinct tickers per trading day from
  2026-06-12, current through 2026-07-01, label fill-rate 0.90-1.00; the 17:00-ET
  cron fires daily and writes same-day (verified from 06-22).
- The classic forward-outcome leak is CLOSED by construction: the labeler SELECT is
  a hard whitelist that omits next_day_pct/day2_pct/day3_pct/peak_return_3d/is_win/
  outcome_tier; none exist in the table.
- Labels are byte-faithful: produced by the SAME production simulator
  (_simulate_contract, pick_doc=None) with realistic slippage / gap-through-stop /
  refusal to sim an unclosed window. realized_return_pct is trustworthy AS a
  same-day GIGO label.
- The delta lever is first-class: recommended_delta 100% populated (2200/3239 in the
  0.20-0.46 band). Greeks, recommended_iv, moneyness, RR, atr_move all persisted.
- Literature IV triad present (current arm): iv_rank_entry ~80% / iv_percentile ~96%
  / hv_20d ~96%. Technicals are lookahead-guarded (window bounded to scan_date +
  post-filter dropping any bar > scan_date).
- Collector is walled from the live system: writes ONLY the research table, never
  the ledger/Firestore/webapp; per-contract sim errors are caught and skipped.

--------------------------------------------------------------------------------
MUST-FIX BEFORE HEADLESS AGENTS (ranked; do #1 first)
--------------------------------------------------------------------------------
1. ATOMIC, SCHEMA-DRIFT-SAFE WRITE PATH — do this FIRST, it unblocks every
   "add a column" fix below.
   Where: forward-paper-trader _write_shadow_records (main.py ~L1306-1324) AND
   enrichment-trigger's enriched load (~L1556/L1593-1600). Both do delete-then-load
   with ALLOW_FIELD_ADDITION and autodetect OFF, DELETE not wrapped in try/except.
   Risk: adding any new field 500s the load AFTER the DELETE -> silent loss of that
   scan_date's rows (the documented forward_paper_ledger landmine, now in the
   substrate designed to grow features). A >10min timeout mid-run also wipes the day.
   Fix: load-to-staging-then-MERGE (or partition swap) so rows are never deleted
   before a successful load. Stopgap: autodetect=True + mandate ALTER TABLE ADD
   COLUMN before shipping any new field. Route via gammarips-review. [M, 1-3d]

2. FIX THE LIVE REGIME LOOKAHEAD (the real leak the adversarial pass caught).
   VIX_at_entry / SPY_trend_state / vix_5d_delta_entry are entry-day CLOSE (16:00)
   values, but the trade enters 10:00 and exits 15:45 the SAME day — so they are
   realized AFTER the trade, yet filed under "FEATURES / regime". A headless agent
   conditioning on them LEAKS THE FUTURE. Also non-deterministic between cron and
   backfill (as-of drift -> poisons fits + defeats replay).
   Fix: recompute regime as-of scan_date (prior close = the real selection point),
   OR move these to the OUTCOME/telemetry group and add distinct scan-date-dated
   regime FEATURE columns; drop the misleading _at_entry naming; backfill. [S-M]

3. EMPTY/DEGRADED POOL = FAILURE + LABEL-FILL FRESHNESS MONITOR.
   A Polygon-minute-bar outage writes 50 INVALID_LIQUIDITY rows (NULL label) and
   still returns HTTP 200 — the confirmed root cause of the two permanent holes. A
   row-presence check would PASS it.
   Fix: return non-2xx / page when pool_size==0; morning monitor asserting the
   just-closed day has >=1 row AND labeled/rows >= 0.8. Also covers the untracked-
   cron SPOF. [S-M]

4. LEAKAGE-SAFE FEATURES-ONLY VIEW + MACHINE-READABLE DATA CONTRACT.
   Today only DDL comments keep an agent/MCP out of the label columns (flat ~64-col
   table, SELECT * ingests the labels).
   Fix: create enriched_features_v1 VIEW (point-in-time features + join keys only);
   point ALL agent/MCP/research access at it (raw table for label joins only); set
   BQ column descriptions tagging feature|label|regime|identity; adopt label_/oc_
   prefix so leakage is greppable; add to docs/DATA-CONTRACTS.md with the exact label
   definition. Also a safe view over overnight_signals_enriched (it STILL carries
   next_day_pct/.../outcome_tier). [M]

5. PERSIST mom_60 (the finding's headline lever) AS A POINT-IN-TIME BQ COLUMN.
   Today mom_60 is computed transiently in enrichment (_compute_momentum_map,
   leakage-guarded) but written NOWHERE; the only recompute path is a gitignored,
   stale (2026-06-19) local parquet -> a naive "60d return as of this row" pulls
   post-scan bars = future leak. The keystone finding is not reproducible from BQ.
   Fix: persist mom_60 (+ anchor_date/lookback_date) on overnight_signals_enriched
   at enrichment time via the existing _resolve_momentum_dates guard; add to the
   labeler SELECT; stand up a SCHEDULED underlying-daily-bar BQ cache (not a local
   artifact); backfill. (Depends on #1.) [M, 2-3d]

6. EXIT-FREEDOM IN THE LABEL == THE OWNER'S "OPPORTUNITY SURFACE" REFRAME.
   Substrate carries ONLY the same-day GIGO bracket; the flagship finding is a 3-DAY
   hold. More broadly: profitability depends on HOW a contract is traded, so exit
   must be a FREE VARIABLE.
   Fix (target): persist the per-contract intraday+multi-day option-premium BAR PATH
   (+ max favorable / max adverse excursion) into a companion table keyed by
   (entry_day,ticker,contract) so agents re-derive ANY exit rule offline, leakage-
   safe. Interim (cheaper): add a parallel 3-day label group
   (realized_return_pct_3d/exit_reason_3d/exit_day_3d) via a second _simulate_contract
   call (HOLD_DAYS=3/+80/-60) in the same pass. Tag every label group with a
   persisted simulator_version + HOLD/STOP/TARGET so horizons never silently mix.
   (Depends on #1.) [L target / M interim]

7. REMEDIATE THE 06-10 DUPLICATION AT ITS SOURCE + UNIQUENESS GUARD.
   Root cause (adversarial correction): the 145 dups on 06-11 are a faithful copy of
   an UPSTREAM doubling — overnight_signals_enriched scan_date 06-10 is fully doubled
   (658=329x2). The collector has zero dedup and propagated it. NOT a collector race.
   Fix: dedup/re-run enrichment for 06-10, THEN re-label; fix enrichment idempotency
   (folded into #1); add a post-load uniqueness assertion on
   (scan_date,ticker,recommended_contract) that fails LOUDLY + a per-scan_date lock. [M]

--------------------------------------------------------------------------------
SHOULD-FIX (after the must-fixes; enrich the feature set for edge discovery)
--------------------------------------------------------------------------------
- Stand up append-only market_regime_daily (one row/NYSE day, UNCONDITIONAL, scan-
  date-dated: VIX, VIX3M, term ratio, SPY trend/return, breadth, realized vol) —
  decouples regime from the pool, one canonical point-in-time series, serves the
  "regime-detection first" priority. Confirmed absent.
- Propagate call/put-split flow-imbalance + skew proxies from source (call/put V/OI,
  active-strike breadth, uoa_depth, flow_intent, mean_reversion_risk, move_overdone,
  reversal_probability) — the UOA literature (Pan & Poteshman 2006; Johnson & So
  2012) says these carry the signal; none reach the substrate today.
- Persist earnings proximity per candidate (days_to_next_earnings + in-window bool)
  — IV-crush driver (De Silva 2026; Cao/Han 2013), today only a downstream gate.
- Backfill iv_rank/iv_percentile/hv on the historical V7_INTRADAY arm (~36/36/69%
  vs ~80/96/96% current) so full-history vol-context screens aren't starved.
- Reconcile win-tracker premium recompute drift: its backfill SELECT omits
  put_vol_oi_ratio + atr_normalized_move -> premium_score/is_premium_signal on
  backfilled rows can differ from what the tournament saw. Treat as LOW-TRUST until
  fixed.
- Add an is_labelable / clean_fill flag (27.7% of rows are INVALID_LIQUIDITY NULL-
  label — non-random, illiquid tail; biases any screen). Document the exclusion.
- Commit the /label_enriched_pool Cloud Scheduler job to deploy.sh/IaC (LIVE but
  untracked SPOF).
- Persist per-row label-semantics tag (simulator_version + HOLD/STOP/TARGET) — today
  policy_version is a hardcoded constant on every row incl. April backfill.

--------------------------------------------------------------------------------
RECOMMENDED BUILD ORDER
--------------------------------------------------------------------------------
Phase 0 (unblocker):        Must-fix #1 (atomic write path). Nothing else is safe first.
Phase 1 (integrity+leak):   #2 (regime leak), #3 (freshness monitor), #7 (dedup+guard).
Phase 2 (the finding + exit-freedom): #5 (persist mom_60), #6 (opportunity-surface
                            bar path / interim 3-day arm). This is what makes the
                            substrate answer the flagship finding AND supports the
                            "exit is the trader's, not the engine's" product.
Phase 3 (agent-safe access): #4 (features-only view + data contract).
Phase 4 (enrich features):  the should-fix list (regime table, flow-imbalance,
                            earnings, IV backfill, etc.).
LEAKAGE (#2, #4) is the non-negotiable; gammarips-review gates anything touching the
pipeline. No deploys without explicit owner OK.

--------------------------------------------------------------------------------
COMPANION FILES / MEMORY
--------------------------------------------------------------------------------
- .scratch/edge_discovery_finding_2026-07-01.txt (the mom_60xdelta 3-day finding)
- .scratch/gigo_flow_index_feasibility_2026-07-01.md (the negative GIGO composite)
- Memory: project_substrate_audit_2026_07_01, project_agent_data_readiness,
  project_surface_contracts_discretionary_exit, project_ledger_schema_drift_landmine
================================================================================
