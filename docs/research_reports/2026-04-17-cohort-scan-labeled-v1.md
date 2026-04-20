# Cohort Scan — `signals_labeled_v1` (2026-04-17)

Researcher: gammarips-researcher
Dataset: `profitscout-fida8.profit_scout.signals_labeled_v1` (FROZEN, 2,162 rows, 2026-02-18 to 2026-04-06)
Scope: find 2-day option-trade cohorts with positive EV after 1% round-trip fees, statistically robust enough to justify real-money entries.

---

## 1. Executive summary

- **No cohort passes the gate.** Zero of ~35 hypotheses tested (5 flags, 10 flag×direction, 5 score thresholds, 10 two-flag AND combos, 4 continuous features × 4 quartiles, plus targeted follow-ups on `premium_hedge` and `premium_high_rr`) meet N≥50 AND train EV>0 with 95% CI excluding zero AND test EV>0.
- **The full sample is EV-negative** at −4.26% per trade after 1% fees (win rate 33.1%, N=1,563 tradable). Winners average +31.6%, losers average −22.0% — the stop-to-target payoff ratio (~1.4:1) is not enough to overcome the 33% hit rate.
- **Regime deteriorated in the test window** (Mar 23 – Mar 31): baseline test EV fell to −6.93% (CI [−9.6%, −4.1%]), vs −3.53% on train. Any cohort improvement is fighting a worsening tape.
- **The "premium_hedge is the alpha" prior is NOT supported here.** `premium_hedge=True` posted +0.38% EV on train (CI crosses zero) and crashed to −12.00% on test — worse than baseline. The live-ledger N=30 signal memory cites is likely a small-sample artifact.
- **Recommendation: DO NOT enter real-money positions yet.** The labeled research dataset does not support a positive-expectancy subset. Wait for more data or re-engineer the entry policy — do not dress up marginal train-only cohorts as edges.

---

## 2. Baseline (full tradable sample, net of 1% fees)

Non-tradable rows (INVALID_LIQUIDITY=273, NO_BARS=148, FUTURE_TIMEOUT=178) excluded; tradable set = 1,563.

| Split | N | EV | 95% CI | Win rate | Avg winner | Avg loser |
|-------|---|-----|--------|----------|------------|-----------|
| Full  | 1,563 | **−4.26%** | [−5.59%, −2.94%] | 33.1% | +31.55% | −21.97% |
| Train (Feb 18 – Mar 20) | 1,226 | −3.53% | [−5.01%, −1.96%] | 34.0% | +31.75% | −21.72% |
| Test  (Mar 23 – Mar 31) | 337   | −6.93% | [−9.61%, −4.13%] | 29.7% | +30.73% | −22.81% |

Note: the originally requested test window was through Apr 6, but all Apr 1/2/6 rows are `FUTURE_TIMEOUT` (outcome not yet known). Effective test window is **7 trading days** (Mar 23 – Mar 31). That is honest but thin, and it's the binding constraint on any cohort validation.

---

## 3. Passing cohorts

**None.** No cohort satisfied all three criteria simultaneously (N≥50 on train, train EV>0 with bootstrap 95% CI excluding zero, test EV>0).

The closest candidate — `premium_high_rr=True AND direction=BEARISH` — posted train EV +3.59% (N=97, win rate 45.4%, 30 targets / 34 stops / 33 timeouts), but its bootstrap CI [−1.88%, +9.36%] includes zero, and the test window contains only N=2 trades for this cohort. It cannot be validated either way. Do not deploy.

---

## 4. Negative results

### 4a. Single premium flags

| Cohort | Train N | Train EV | Train 95% CI | Test N | Test EV | Test 95% CI | Verdict |
|---|---|---|---|---|---|---|---|
| premium_hedge=True      | 226 | +0.38% | [−3.16%, +4.13%] | 47 | **−12.00%** | [−18.18%, −5.17%] | FAIL — train CI crosses 0, test collapses |
| premium_bull_flow=True  |  33 | −8.06% | [−15.28%, −0.03%] | 5 | −5.52% | [−23.35%, +12.85%] | FAIL — N<50 on train |
| premium_bear_flow=True  |  10 | −2.63% | [−19.50%, +15.30%] | 0 | — | — | FAIL — N<50 |
| premium_high_rr=True    | 150 | −2.44% | [−6.92%, +1.94%] | 20 | +1.88% | [−9.91%, +14.37%] | FAIL — train EV<0 |
| premium_high_atr=True   |  10 | −4.86% | [−17.20%, +9.00%] | 0 | — | — | FAIL — N<50 |

### 4b. Premium score thresholds

| Cohort | Train N | Train EV | Train 95% CI | Test N | Test EV | Verdict |
|---|---|---|---|---|---|---|
| premium_score >= 1 | 376 | −1.89% | [−4.49%, +0.96%] | 72 | −7.70% | FAIL |
| premium_score >= 2 |  52 | +2.22% | [−5.23%, +9.98%] |  0 | — | FAIL — no test data |
| premium_score >= 3 |   1 | −26.00% | — | 0 | — | FAIL |
| premium_score >= 4 |   0 | — | — | 0 | — | FAIL |
| premium_score >= 5 |   0 | — | — | 0 | — | FAIL |

Note: `premium_score >= 2` on train has EV +2.22% but CI [−5.23%, +9.98%] crosses zero, and zero test rows — unverifiable. Scores ≥3 are vanishingly rare in this dataset.

### 4c. Flag × direction (highlights)

| Cohort | Train N | Train EV | Test N | Test EV | Verdict |
|---|---|---|---|---|---|
| premium_hedge & BEARISH  | 211 | −0.06% | 44 | **−12.53%** | FAIL |
| premium_hedge & BULLISH  |  15 | +6.56% | 3  | −4.33% | FAIL — N<50 |
| premium_high_rr & BEARISH | 97 | +3.59% | 2  | +6.50% | FAIL — test N=2 |
| premium_high_rr & BULLISH | 53 | −13.48% | 18 | +1.37% | FAIL — train CI negative |

### 4d. Two-flag AND combos

No two-flag combination reached N≥50 on train. Premium flags are too rare and too overlapping to form joint cohorts in this dataset.

### 4e. Continuous-feature quartile splits (cuts defined on train, applied to test)

| Feature | Best train quartile | Train EV | Test EV same bucket | Verdict |
|---|---|---|---|---|
| rsi_14 | Q2 (35.3–45.9) | −1.77% (CI crosses 0) | −5.19% | FAIL |
| atr_14 | Q3 (5.9–10.6) | −2.11% | −6.56% | FAIL |
| overnight_score | score=6 bucket | −3.18% | −6.47% | FAIL |
| risk_reward_ratio | Q3 (0.30–1.07) | −3.06% | −1.15% | FAIL — train EV<0 |
| catalyst_score | Q3 (>0.85) | −1.55% | −5.22% | FAIL |
| contract_score | Q1 (<9.3) | −1.52% | −7.36% | FAIL |
| atr_normalized_move | Q1 (<0.42) | −2.47% | −6.07% | FAIL |
| close_loc | Q1 | −2.63% | (test N=0) | FAIL |

No quartile on any continuous feature produced a positive train EV, let alone one with CI excluding zero.

### 4f. Targeted probes on the "hedge + BEARISH" family

Since user memory suggested `premium_hedge` carries alpha in the live ledger, we layered technicals on top of `hedge & BEARISH` (N=211 train, N=44 test). Adding `above_sma_50=False`, `golden_cross=False`, `move_overdone=True`, or `rsi<30` all kept train EV near zero and drove test EV to −13% to −21%. Adding `above_sma_50=True` gave train EV +6.74% / test +9.66% but with N=13 train and N=2 test — unusable.

### 4g. Direction alone

- BULLISH: train −6.12%, test −4.59% — uniformly negative
- BEARISH: train −1.28%, test −9.36% — train hint collapses on test

---

## 5. Methodology notes

- **Fees**: 1% subtracted from `realized_return_pct` (which already includes 2% entry slippage baked into `entry_price`). So `ret_net = realized_return_pct - 0.01`.
- **Non-tradable exclusion**: `exit_reason IN ('INVALID_LIQUIDITY','NO_BARS','FUTURE_TIMEOUT')` (599 rows) removed from all EV computations.
- **Train/test cutoff**: train = `scan_date <= 2026-03-22` (N=1,226), test = `scan_date >= 2026-03-23 AND scan_date <= 2026-04-06` (N=337). Requested test end was Apr 6, but rows past Mar 31 are all FUTURE_TIMEOUT. Effective test window = Mar 23 – Mar 31, 7 trading days.
- **Bootstrap**: 5,000 resamples with replacement, seed = 42. 2.5th / 97.5th percentile for the 95% CI of the mean (EV).
- **Pass gate**: N≥50 on train AND train bootstrap EV CI lower bound > 0 AND test EV > 0. Did not require test CI > 0 (test N too small to expect that in most cases).
- **Cohort space searched** (~35 hypotheses): 5 single flags + 10 flag×direction + 5 score thresholds + all two-flag AND combos with train N≥50 (none qualified) + 8 continuous features × 4 quartiles + targeted hedge-follow-ups. Did not exhaustively search three-way combos.
- **No features excluded for leakage** in the feature set used (we only used enrichment-time columns: premium flags, direction, score, rsi_14, atr_14, etc.). The forbidden outcome-derived columns from the brief were never used as predicates.
- **RNG seed**: 42 (for bootstrap reproducibility).

---

## 6. Next step recommendation

**No signal found — rethink.** Do NOT start small real-money positions next week based on subsets of `signals_labeled_v1`. Concrete follow-ups in priority order:

1. **Question the entry model itself.** The underlying option-trade has a ~1.4:1 payoff ratio with a ~33% hit rate. Both need to move. Either the target/stop geometry is wrong (a 40/-25 bracket is punishing on 2-day holds where most TIMEOUTs land slightly negative) or the signal is not identifying a real directional edge.
2. **Look at the live `forward_paper_ledger`, not this labeled set.** The V4 ledger uses enriched-gate signals (different filter population) and policy changes that `signals_labeled_v1` doesn't reflect. The "hedge is the alpha" memory came from that cohort; it should be re-tested there with a proper bootstrap once N is sufficient.
3. **Test exit-policy variants on this frozen dataset.** Before deploying new entry logic, check whether different brackets (30/-20, 25/-15, time-based exits on D+1) produce positive EV on the same entry population. That's a different research question (entry-neutral) and the existing research infra supports it.
4. **If the user insists on live testing**, size it as a research probe (≤$500 per trade), flag it explicitly as hypothesis-generating rather than edge-exploiting, and pre-commit the hypothesis before the trade (e.g., "hedge=True & direction=BULLISH", which at least was non-negative on both splits even with tiny N). But my honest recommendation is still: don't.

