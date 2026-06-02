# 2026-06-02 — Remove the `V/OI > 2` conviction gate (STRICT path)

**Status:** IMPLEMENTED in code 2026-06-02 (owner-directed), pending `gammarips-review` on the diff + `bash deploy.sh`. Applied GLOBALLY to the STRICT path (not tag-segmented).
**Service:** `signal-notifier` (STRICT selection path; `_build_candidate_query`).
**Decision owner:** Evan — directed immediate implementation for pick quality, explicitly overriding the N≥15-closes revisit lock (see "Governance override" below).
**Evidence:** realized-option-PnL backtest, N=1,375 fills (`backtesting_and_research/realized_option_label.py`, `gate_recall.py`, `gate_validity_checks.py`), `gammarips-review` signed off the finding as proposal-grade 2026-06-02.
**Related:** [[2026-06-01-daily-cadence-fallback]], [[2026-05-12-v5-4-pipeline-alignment]], [[2026-05-19-active-days-liquidity-gate]], [[2026-05-27-invalid-liquidity-accepted]]

## Problem

Operator hypothesis: the pipeline over-filters and is discarding real winners in a tape where we keep getting mangled (e.g. CIEN BEARISH entered 2026-05-29, underlying +8% against us). A multi-agent pipeline audit confirmed the *surface* over-engineering (21 gates across 4 services; the signal-notifier stack collapses ~80 enriched names/day to a **median of 2** candidates *before* the LLM Scorer→Picker even runs, so the picker is "choosing" from ~2 names and is forced on 86% of days — CIEN was exactly this: a regime-3.0, LOW-confidence forced pick on a thin day).

The audit's first pass also claimed the conviction/liquidity gates "filter out 60–75% of winners" — but that rested on the **leaked `peak_return_3d` label** (an *underlying* 3-day peak move, 78.5% base "win" rate), not realized option PnL. That label was unsafe to act on.

## What we did to get an honest answer

1. Backfilled the full 3-trading-day option **minute** bars for every labeled candidate from Polygon (`fetch_hold_window_bars.py`; past-only, no lookahead) — the local cache previously held only entry-day bars, which had degenerated 99% of the first replay into day-1 truncations.
2. Replayed the **exact** forward-paper-trader bracket (entry 10:00 ET D+1 ×1.02 slippage, −60% stop / +80% target / 25%-trail-at-+30%, conservative intrabar precedence, 3-day hold, 15:50 ET exit) on 1,375 fillable candidates. Real outcome distribution: TIMEOUT 1040 / STOP 120 / TARGET 119 / TRAIL 96; baseline +80% rate 8.7%, +25% rate 20.7% (vs. the degenerate 0.4% day-1 proxy).
3. Re-ran per-gate winner-recall on this **realized-option** label and ran the four validity checks `gammarips-review` required.

## Finding (review-validated)

**`V/OI > 2` is the prime gate to relax.** It removes **~55–63% of real option winners**, and the survivors are **no better than baseline** — precision lift is statistically ≤ 0:

| Check | Result for `V/OI > 2` |
|---|---|
| Winner recall (real +25%, full-window n=806) | 0.371 — drops ~63% of winners |
| Precision lift (full-window, real +25%) | **−0.031**, bootstrap 90% CI **[−0.061, −0.001]**, P(lift ≤ 0) = **95.7%** |
| Selection confound (fill-rate gap pass vs fail) | **+0.057** — barely predicts fillability; dropping it won't raise the unfillable rate |
| Chronological stability (split at 2026-05-01) | −0.034 (H1) / −0.033 (H2) — stable, not a recency artifact |

Interpretation: "unusual volume" (`V/OI > 2`) is **not even a good conviction signal** — it discards most winners without improving win quality. This is the EV backing for what the [[2026-06-01-daily-cadence-fallback]] already does intuitively on zero-candidate days ("V/OI is a conviction signal, not a fillability signal"). The proposal is to extend that relaxation to the STRICT path.

**Bonus:** because `V/OI > 2` is a conviction (not tradeability) gate, dropping it on the STRICT path widens the slate the picker chooses from — directly attacking the median-2 starvation that produces forced, low-conviction picks like CIEN.

## Why NOT the other gates (the leaked label had us aimed at the wrong target)

- **`OI ≥ 10` — keep.** The first (leaked-label) audit fingered this as the *worst* gate (−3.2 lift). On real option PnL it **flips to modestly positive/neutral**. It is a fillability gate; the FILLED cohort is conditioned on fillability, and 587 candidates died as INVALID_LIQUIDITY ([[2026-05-27-invalid-liquidity-accepted]]). Do not touch.
- **`vol ≥ 50` — keep.** Same fillability category; lift ~0.
- **moneyness `5–10% OTM` — keep, cannot be judged this way.** Relaxing the band selects a *different contract* with different leverage/convexity, so same-contract recall says nothing about the contract you'd actually trade. Contract-selection parameter, lit-locked (Augustin 2022), not a pass/fail filter.

## Mandatory caveats (carry these forward; do not drop)

1. **Backtest, not live.** Evidence is a local-cache option-bar replay, not forward paper results. Promotion is gated on 30-day forward OOS.
2. **N ≥ 15-closes lock still binds.** We are at ~6 V5.4 closes; `V/OI` relax was previously "Scenario D, rejected 2026-05-12, revisit at N ≥ 15 closes." This is a hypothesis to *test*, not an authorized change.
3. **Uniform 1.02 single-minute-bar slippage** likely overstates winners across all gates (does not differentially favor V/OI); absolute win rates are optimistic.
4. **Full-window cohort N = 806** after dropping 569 truncated-window fills; the headline CI is computed on `n_hold_bardays == 3` only.
5. **`VIX ≤ VIX3M` is still a `notna()` placeholder** in `gate_recall.py` — NOT validated and NOT part of this proposal; imply no VIX-gate conclusion.
6. **Funnel-starvation interaction is real but possibly small:** dropping V/OI should raise candidate count, but the OI/vol liquidity floor remains the structural ceiling ([[2026-05-19-active-days-liquidity-gate]]), so the cadence gain may be modest. Re-run the funnel at N ≥ 15 V5.4 days.
7. **Selection-confound residual:** V/OI's +0.057 fill-rate gap is small but nonzero; the FILLED-only recall retains a minor upward bias.
8. **Multiple-comparison context:** five gates were evaluated; V/OI is singled out because its lift CI sits entirely ≤ 0 across both the bootstrap and the chronological split — not cherry-picked from a wider sweep.

## Governance override + monitoring/revert plan

The owner directed immediate global implementation rather than the tag-segmented 30-day OOS originally proposed. This **overrides** the `2026-05-12` N≥15-closes revisit lock for this gate. Recorded plainly so the trail is honest:

- **Why override is defensible:** the gate is being *removed*, not added; the removal is backed by the strongest evidence we have (N=1,375 realized-option-PnL fills, review-validated on lookahead/selection/bootstrap/chronological); and the trader still simulates every enriched signal, so the research dataset is preserved regardless.
- **What we trade away:** no tag-segmented STRICT-vs-STRICT_NOVOI A/B. We will NOT have a clean within-window control; before/after is confounded by regime. Accepted for speed.
- **Safety net = monitoring + fast revert, not a pre-deploy gate:**
  1. The change is one SQL condition; **revert = re-add two lines** (kill switch is trivial).
  2. The removal date is logged here and in `INTELLIGENCE_BRIEF.md`; treat the cohort as pre-/post-2026-06-02 for any EV read.
  3. Watch realized EV and the INVALID_LIQUIDITY rate on `forward_paper_ledger` after the first ~10 post-change closes (the OI/vol/active-days floors stay, so fillability should hold; if INVALID_LIQUIDITY rises, that is the revert signal).
- **Still required before deploy:** `gammarips-review` on the actual diff (read-only, fast) — done this session — then `cd signal-notifier && bash deploy.sh`. `docs/TRADING-STRATEGY.md` and CLAUDE.md updated in the same change (done).

## Companion change (2026-06-02): STRICT pool re-ranked

With `V/OI > 2` gone as a *filter*, leaving it as the STRICT `ORDER BY` *primary* key would still bias the `LIMIT 10` pool the picker draws from toward a metric we just showed has no selection value (`gammarips-review` flagged this as the one line to watch). So the STRICT ordering was changed to match FALLBACK: `overnight_score DESC, recommended_oi DESC, recommended_spread_pct ASC, ticker ASC`. This supersedes the 2026-05-01 directional-V/OI-DESC primary (whose N=435 EDA only established V/OI-DESC over a *dollar-volume* primary, not over composite score). Lower-stakes than the gate removal — it only changes which candidates reach the picker on high-inventory days, and the scorer re-scores survivors by composite regardless.

## Path forward (sequencing, informed by the full pipeline audit)

The audit produced a tiered cleanup list. Sequenced by leverage × safety:

1. **(this doc) Remove `V/OI > 2`** — **DONE in code 2026-06-02**, pending deploy. Highest-leverage, surgical, evidence-backed. Attacks both winner-recall and slate-starvation.
2. **Documentation accuracy check (no OOS needed) — verified 2026-06-02:** the canonical gate map (`docs/TRADING-STRATEGY.md:34-42`, CLAUDE.md policy summary) is **already accurate**. `directional UOA > $500K` is correctly attributed to `enrichment-trigger` (enforced at `enrichment-trigger/main.py:339-340`; `signal-notifier` carries the columns but does not re-check it) — genuinely upstream-only. `DTE 7–45` is correctly attributed to `signal-notifier` (`main.py:1155`). **Correction to the pipeline audit:** it classified `DTE 7–45` as REDUNDANT off its "100% pass / recall 1.00" number, but that is an *active* notifier gate that merely didn't bite in the 2026-04-10..06-01 window (upstream contract selection currently keeps DTE short). It is a documented backstop against the 2026-05-11 VAL 40+ DTE incident — **keep it; do not mark it non-binding.** Net: no doc change required; the map is already correct and only UOA is genuinely upstream-only.
3. **Open question — the dual-LLM picker.** With the slate at a median of 2, the Scorer→Picker pair is expensive relative to what it decides. If (1) widens the slate materially, the picker earns its keep; if it does not, evaluate a deterministic composite-score sort. Defer until post-(1) funnel data at N ≥ 15.
4. **Fix the `VIX ≤ VIX3M` placeholder** in research tooling (`gate_recall.py`) so the regime gate can be evaluated honestly in the next pass — currently we cannot say whether it helps.
5. **Locked until N ≥ 15 closes:** bracket/target/trail mechanics (the +80% tail debate), and any move on the OI/vol liquidity floor.

## What this does NOT change

- Trader execution mechanics (entry, −60/+80, trail, 3-day hold). Unchanged.
- The daily-cadence fallback. Unchanged (it already relaxes V/OI on zero-candidate days; this proposal addresses the STRICT path).
- Any tradeability gate (OI, vol, DTE, regime, earnings, active-days). Unchanged.
- The one-pick-per-day cap and ledger mechanics. Unchanged.
