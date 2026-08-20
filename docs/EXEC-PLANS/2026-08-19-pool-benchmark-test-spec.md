# Pool-versus-benchmark test — SPEC (pre-registered, not yet run)

**Written 2026-08-19. Status: SPEC ONLY. Nothing has been pulled or measured.**

**This document is a pre-registration.** Everything below is fixed BEFORE any data is
pulled. Nobody may change the hypotheses, the matching, the metrics, or the decision rules
after seeing a result. Two hypotheses died this session from post-hoc slicing
(`catalyst_score` on 2026-08-05, `contract_score` on 2026-08-19). This test does not get to
die that way.

**AMENDMENT 2026-08-20 (pre-data, no data pulled yet).** Arm B's liquidity bar was written
as "the same liquidity floor we ship in `POOL_LIQ_FLOOR`". That floor never shipped: the
2026-08-19 pool-admission design lost review and was NOT ADOPTED
(`docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md`). The three thresholds
(und_vol >= 3M, strikes >= 25, oi >= 1200) stay exactly as written, relabeled as the
study's own research-side bar. No hypothesis, metric, matching rule, or decision rule
changed.

---

## 1. The question

**Do our selected contracts outperform contracts we did not select?**

Every measurement this program has ever made is WITHIN the pool. AUC asks "can we rank the
50 against each other?" and the answer is no. **No test has ever asked whether the 50 beat
50 other contracts.** Until that is answered, selection quality is UNKNOWN, not refuted,
and every downstream question (bracket, entry hour, intraday feed) is premature.

## 2. What is deliberately held constant

The scanner does two separate jobs:

1. It picks a **NAME + direction** from unusual options flow.
2. It picks a **CONTRACT** within that name (`_best_contract`, the `contract_score` logic).

**This test isolates job 1.** Control contracts are chosen from control names using the
**identical** `_best_contract` logic, the identical moneyness band, and the identical delta
band. So the only systematic difference between arms is whether unusual flow selected the
name.

If we let contract selection differ too, a null result would be uninterpretable.

## 3. Universe and arms

For each of the 87 scan dates from 2026-04-10 to 2026-08-17:

- **ARM A (POOL).** The delivered pool contracts on that date. Already have the tape.
- **ARM B (MATCHED CONTROL).** 20 contracts per date drawn from names in
  `gs://profit-scout-data/overnight-universe.txt` that were NOT in the pool that date,
  matched to that date's pool profile on:
  - underlying **day volume decile** (so we are not comparing liquid pool names to
    illiquid controls),
  - **sector**, where the pool has 3 or more names in a sector,
  - the **study's own liquidity bar** (und_vol >= 3M, strikes >= 25, oi >= 1200), so both
    arms are tradeable by construction. This bar is research-side only, not a production
    floor (see the 2026-08-20 amendment note above).
- **ARM C (UNMATCHED CONTROL).** 10 contracts per date drawn at random from the same
  universe with NO matching beyond the delta and DTE bands. This measures the total effect
  of everything we do, including the liquidity floor.

Arm C exists so that a null on Arm B can be read correctly. If A beats C but not B, the
value is in the liquidity bar, not in the flow signal.

## 4. Outcome, identical across arms

The same replay used all session, with production conventions:

- entry 10:00 ET on entry_day, fill = bar close x 1.02
- bracket +40% / −30%, conservative order TIMEOUT > STOP > TARGET
- flat 15:45 ET same day, exit pays 2%
- **a real print required within 15 minutes at BOTH anchors.** A leg with no print near an
  anchor is UNFILLABLE, not flat. This is the stale-exit rule, and it is the single
  correction that reversed a conclusion earlier today.

Secondary outcome, no bracket: median same-day MFE and MAE from the 10:00 anchor.

## 5. Pre-committed hypotheses and decision rules

Primary metric: **difference in mean per-trade return, A minus B, day-clustered bootstrap,
90% CI, 10,000 resamples, paired by scan_date.**

| ID | Hypothesis | Rejected if |
|---|---|---|
| **H1** | Pool beats matched control on mean same-day return | 90% CI on (A − B) includes 0 |
| **H2** | Pool beats matched control on median MFE | 90% CI on the median difference includes 0 |
| **H3** | Pool beats UNMATCHED control (A − C) | 90% CI includes 0 |

**Decision rules, fixed now:**

- **H1 or H2 survives** → selection carries measurable value. Keep the scan. The program's
  next question becomes how to harvest it, and the intraday-feed question becomes worth
  costing.
- **H1 and H2 both fail, H3 survives** → the flow signal adds nothing, but our liquidity
  and contract-selection machinery does. Retire the unusual-activity scan as a ranking
  device and keep the pipeline as a liquidity-filtered contract finder.
- **All three fail** → the pool is not distinguishable from matched random optionable
  contracts. **The scan is not a selection edge.** Reposition the product on the
  opportunity-surface data itself, which is what the doctrine already sells, and stop
  spending on selection research.

No fourth branch. No "re-slice by era". No "check a sub-window".

## 6. Power, stated before the result

Arm A tradeable is about 600 legs over 87 days, with a day-clustered CI of roughly ±3.8pp
on the mean. Arm B at 20/day is about 1,740 legs.

**This test can detect a difference of roughly 5 percentage points per trade. It cannot
detect 1 to 2 points.** A null therefore means "no large edge", never "no edge". Write that
sentence into the result, whatever the result is.

## 7. Cost and prerequisites

- **Polygon minute aggs: about 2,610 calls** (20 + 10 per date x 87 dates), one per
  (contract, entry_day). At `minute_paths.py`'s 16 workers this is roughly 10 minutes of
  wall clock. Plus about 87 reference calls to enumerate contracts per date.
- **BLOCKER: rotate `POLYGON_API_KEY` first.** It leaked 2026-07-06 and was echoed in an
  error body 2026-08-05. It is still open in the owner queue. Do not add call volume to a
  leaked key.
- **Use keyset paging, never `next_url`.** Bulk `next_url` enumeration silently and
  deterministically SKIPS rows (memory `polygon-next-url-cursor-skips-rows`). A control
  sample built from a lossy walk is a biased control sample.
- Write control tape to a NEW table `profit_scout.control_minute_paths` with the same
  schema as `option_minute_paths`. **Never write control rows into `option_minute_paths`**,
  which the MCP and the labeler both read.

## 8. Known ways this test could mislead

1. **Control names have no flow by construction.** A name with zero unusual activity may
   differ from a pool name in ways the matching does not capture, for example news
   exposure. Matching on sector and liquidity decile reduces this and does not remove it.
2. **The pool is BULLISH-only.** Controls must also be call contracts in the same delta
   band, or the comparison is a direction bet, not a selection test.
3. **Survivorship in the universe file.** The universe was refreshed 2026-08-05 to 3,547
   point-verified names. Dates before that used the stale 5,230-name file. Draw controls
   from the file **as it existed on each scan date**, or the control set contains names the
   scanner could not have seen.
4. **Single regime.** April to August 2026 only. A null here is a null for this regime.

## 9. Implementation order

1. Rotate `POLYGON_API_KEY`, redeploy every service that mounts it.
2. Build the control sampler. Reuse `_best_contract` from the scanner **by import, not by
   reimplementation**, so contract selection is provably identical.
3. Dry-run on 3 dates. Confirm the matched control profile actually matches on delta, DTE,
   and liquidity decile. Publish that balance table BEFORE pulling the full sample.
4. Pull the full control tape into `control_minute_paths`.
5. Run the replay, report against §5 verbatim.
6. Record in `FINDINGS_LEDGER.md` and update `INTELLIGENCE_BRIEF.md` whatever the answer is.

**Step 3 is a gate.** If the balance table shows the arms are not comparable, fix the
matching before pulling, and note that the matching changed before any outcome was seen.
