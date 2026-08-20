# 2026-08-20 — Liquid-universe funnel: pre-registered study spec

**Status: PRE-REGISTERED, NOT RUN. FROZEN as of 2026-08-20.** Owner directed
2026-08-20. An adversarial review (gammarips-researcher, same day, pre-data)
found 2 blockers and 10 fix-before-freeze defects in the first draft; all are
folded in below. Amendments after this point are allowed only before any data
is pulled, each with a dated note (same rule as
`2026-08-19-pool-benchmark-test-spec.md`, the sibling study). After the first
data pull, everything below is frozen.

## Phase 0 errata and freeze stamp (2026-08-20, first data pull)

Phase 0 ran on 2026-08-20:
`backtesting_and_research/2026-08-20_liquid_universe_phase0_audit.py`
(read-only, verified by three independent re-derivations, evidence in
`docs/research_reports/FINDINGS_LEDGER.md` §2026-08-20). That run was the
first data pull. **The spec is now FROZEN.** Phase 0 read no outcome column
(`realized_return_pct` NULLness only) and made no Polygon call. Two factual
corrections follow. Neither changes the design.

1. **`overnight_signals` retains ~2,000-2,500 names/day, not ~100-300.**
   The >= 1%-move conditioning is real (each populated window day has
   min |price_change_pct| >= 1.00, and the minimum across all days is 1.00). The design conclusion stands: the series is
   activity-conditioned, and the baseline comes from Polygon.
2. **The 15.8% H-LU1 reference line is a closed-label construction.** The
   2026-08-19 base also filtered to `realized_return_pct IS NOT NULL`. The
   study's own Arm A instrument (all tape-joined legs, no label filter)
   gives 14.0% on the same 87 days and 17.9% in this study's window. The
   parity construction gives 19.2% in-window. Report the two constructions
   with labels. Arm B's 80% pass mark stays Arm B's own bar.

## Question

Does a liquidity-first funnel (universe → top-N liquid names → UOA measured
against each name's own baseline) produce a better pool than the live
UOA-first funnel? "Better" is pre-defined on two axes:

1. **Executability** (expected to win; not the interesting question).
2. **Opportunity quality** (the open question): does relative-UOA selection
   inside the liquid universe beat liquidity-matched random controls? This is
   the only path to "more profitable trades" in this study. Prior findings put
   the burden of proof on the signal: every within-pool selection edge has
   died OOS, and the tradeable subset of the current pool is more negative
   under fixed exits than the blended number
   ([[ghost-rows-flatter-pool-composites]], [[bracket-optimization-dead]],
   [[contract-score-lead-dead]]).

**Hindsight caveat (honest framing):** the evaluation window predates this
spec but has been analyzed extensively by prior studies, and the reused
floors were fit on overlapping data. Pre-registration constrains forking, not
hindsight. Any positive result here is graded **"promising, forward-validate
on the live cohort"**, never "proven".

## Data reality (established 2026-08-20, pre-freeze)

- **Historical chain open interest DOES NOT EXIST in this stack.** The only
  OI read is the current-state Polygon v3 snapshot; Polygon aggregates carry
  OHLCV, never OI; in-house OI history covers movers and pool names only.
  Chain OI is therefore **dropped from the name-level rank**, and the
  contract floor is volume-based (below). It is **FORBIDDEN to proxy
  historical OI with a current snapshot read**: that is lookahead.
- **`overnight_signals` retains only movers** (~100-300/day, conditioned on
  a >= 1% price move), so no full-universe nightly series exists in BigQuery,
  and any baseline built from it is activity-inflated. The baseline series
  comes from Polygon, by the fixed method below. (This closes the first
  draft's Phase 0 question: the answer is NO, from code, not from an audit.)
- **Timing convention:** all volume inputs are **session T** (the scan
  session, complete at scan time ~23:00 ET). Entry is session **T+1, 10:00
  ET**. No OI-class input survives in the design.

## Funnel definition (all formulas fixed here)

- **Universe:** the universe file **as of each scan date** (GCS
  `universe-backups/`; if a dated backup is missing, use the nearest earlier
  backup and report which dates were approximated).
- **Liquidity rank:** combined score = `z_cross(log1p(chain dollar volume,
  session T)) + z_cross(log1p(underlying share volume, session T))`, where
  `z_cross` is computed across the eligible universe per session. Take the
  **top 100**. Ties: underlying share volume descending, then ticker
  ascending. Secondary floors reused verbatim from the reviewed 2026-08-19
  design: underlying share volume >= 3M, listed strikes >= 25 (via reference
  `as_of`).
- **Signal:** bullish UOA for name i on session T = **call-side option
  dollar volume**. `z = (log1p(UOA_T) - mean(log1p(UOA), trailing 20
  sessions, T EXCLUSIVE)) / sd(same)`. Admit **z >= 2.0 AND call dollar
  volume > put dollar volume on session T**. A name needs >= 15 valid
  baseline sessions to be eligible; failed-pull sessions are excluded from
  the baseline, never zero-filled. BULLISH-only stays a hard gate. The
  earnings rail and the VIX <= VIX3M rail apply unchanged, **to Arms B and C
  identically** (earnings dates from the FMP historical calendar, with the
  caveat that realized dates can differ from scan-time scheduled dates).
- **Contract selection (reduced rule, reconstructible):** among calls with
  DTE in the production window and OTM in the production band versus the
  session-T close: pick **max session-T contract volume**; ties to the strike
  nearest 10% OTM, then nearest expiry, then lowest strike. Contract-level
  floor: **contract session-T volume >= 500** (replaces the OI >= 1,200 floor,
  which has no historical source). For every selected underlying, query the
  splits API over [T, exit_day]; a contract-day spanning a split is excluded
  and counted in a reported exclusion table
  ([[split-adjusted-close-vs-frozen-strike]] class).
- **Pool cap:** top 50 by z, ties broken as above. Fewer qualifying is an
  accepted outcome; pool depth per day is a reported metric.
- **Sensitivity arms (pre-declared):** N ∈ {50, 100, 200}, z ∈ {1.5, 2.0,
  3.0}. Sensitivity cells report **screen-composition metrics only** (pool
  depth, name overlap, liquidity profile), **never outcomes**. Outcome pulls
  happen only for the decision cell N=100, z=2.0.

## Arms

- **Arm A (reference):** the production pool as it historically was. Metrics
  compute on minute-path tape, not substrate labels; rows without tape are
  counted and reported, never silently dropped. Known in-window composition
  changes (mom_60 tilt start, uneven early daily counts) are listed in the
  report.
- **Arm B:** the liquid-universe funnel pool, reconstructed per the formulas
  above.
- **Arm C (critical control):** seed=42 (`numpy default_rng`). Per day d, C
  draws `|B_d|` names uniformly without replacement from (top-100 minus B_d
  minus earnings-rail exclusions), same contract-selection rule, calls for
  all arms. **M=200** independent control pools; the C distribution pools all
  M draws with per-draw day weights. VIX-rail skip days drop from BOTH arms.
  A day with `|B_d|=0` contributes no pairs, drops from the paired bootstrap,
  and the count of such days is a reported metric.

## Window

**Entry days: the 60 trading days ending 2026-08-14** (fixed pre-data; both
the same-day and the 3-day outcome windows complete before this spec's
date). Scan dates are the prior trading day of each entry day.

## Metrics (operational definitions)

- **Entry fill** = 10:00 ET bar close x 1.02, requiring a date-validated
  print in [09:55, 10:15]. No print = **UNFILLABLE**, excluded from both
  arms and counted per arm. If per-arm exclusion rates differ by more than
  10 points, a pre-declared sensitivity is reported with UNFILLABLE scored
  as MFE=0 (the differential-exclusion bias check: B names print more often
  by construction, and the excluded C legs are the quiet ones).
- **MFE** = (max date-validated bar high in (entry, 15:45 ET] - fill)/fill;
  **MAE** symmetric on lows. A carried-forward bar is not a print
  ([[minute-paths-carried-forward-fill-is-fabricated]]).
- **Windows:** same-day is primary (matches live policy); 3-day secondary,
  always labeled ([[window-mismatch-3day-vs-same-day]]).
- **Tradeability (H-LU1):** share of legs with 11+ date-validated prints by
  10:00 ET, **recomputed in-study for Arm A on the same instrument and
  window**. Reference lines reported alongside, labeled as different
  instruments: 15.8% (87-day pool base, minute paths) and 62.6%
  (post-PRINT_FLOOR_MIN=25 notifier slate, snapshot instrument). The Arm B
  pass mark of 80% is a pre-registered round-number choice.
- **Inference:** pooled-leg median; paired-by-day block bootstrap, seed=42,
  5,000 resamples, 90% CI. First-half vs second-half stability reported. No
  new metric after data is seen.

## Power and Rule 0

z >= 2.0 on a 100-name universe is a tail event; plausible Arm B depth is
2-10 names/day. **Rule 0: if Arm B totals fewer than 150 fillable legs or
fewer than 30 non-empty days, the study reports INSUFFICIENT SAMPLE**, makes
no signal claim in either direction, and the z threshold may be revisited
only via a new pre-registration. Power, stated now by analogy to the sibling
spec's calculation on a larger sample: this test detects a median-MFE
difference on the order of ~5pp and **cannot** detect 1-2pp edges; a rule-2
null therefore means "no large edge", never "no edge".

## Decision rules (read at N=100, z=2.0, same-day median MFE, B vs C)

1. **B > C, 90% CI excludes zero:** the relative-UOA signal is promising.
   Recommend shipping the funnel as signal + executability, as ONE
   architecture change with ONE cohort reset, retiring the bottom-of-funnel
   floor tower where redundant, with forward validation on the live cohort
   as the confirmation step.
2. **B ≈ C (CI includes zero, Rule 0 satisfied):** the signal is unproven at
   the detectable effect size. The funnel decision falls to executability +
   product grounds alone (real fills, honest labels, sellable pool). Owner
   call, presented with both numbers and the power statement.
3. **B < C, CI excludes zero:** the z-score is anti-selective; do not ship
   it. A liquid universe with the existing edge-rank remains a separate
   option needing its own pre-registration.

In all cases: **no production change ships from the study session.**
Deliverables: dated read-only scripts in `backtesting_and_research/`, a
ledger section, a brief update, wiki notes, an owner decision package.

## Pull budget and traps

- Underlying share volume: `/v2/aggs/grouped` (stocks), cheap, full window.
- Chain dollar volume: rebuilt **only for names passing a cheap pre-rank
  (top-300 by underlying share volume per session)**, via reference `as_of`
  enumeration + per-contract day aggregates, keyset paging, never `next_url`
  enumeration ([[polygon-next-url-cursor-skips-rows]]). Count what answered;
  a batch that raises nothing has proven nothing.
- Outcome minute-aggs: |B| + |C unique contracts| legs x 3 trading days
  each, decision cell only. The concrete call budget is recomputed and
  reported to the owner after the screen phase and **before** the outcome
  pull.
- All Polygon phases wait for the `POLYGON_API_KEY` rotation (owner queue).

## Non-goals

- No bracket or exit-parameter search (doctrine closed, every substrate).
- No modification of the 2026-08-19 pool-benchmark spec (sibling; share the
  window and pulls where possible).
- No claim that executability equals profitability. H-LU2 must earn a CI.
