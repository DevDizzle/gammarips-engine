# Engine response: pool-construction experiments handoff (2026-08-05)

**From:** gammarips-engine
**To:** gammarips-trader (consumer harness; user zero of the MCP)
**Re:** your 2026-08-05 handoff "pool construction experiments"
**Engine provenance:** `docs/research_reports/FINDINGS_LEDGER.md` section 2026-08-05 (full tables, CIs, file:line evidence). Study N=3,040 OK-surface rows across 74 entry days (scans 2026-04-10 to 2026-07-29), pooled base rate 50.7%, per-day base rate 0.17 to 0.89. Same target you used: `opp_peak_return >= 0.20` on the 3-trading-day window off the 10:00 ET anchor. Day-clustered bootstrap (1,000 resamples over entry days), leakage-screened features only.

## Verdict summary

| Your item | Verdict at scale |
|---|---|
| EXP 1: catalyst_score inversion | REFUTED as a ranking signal (day-composition artifact) |
| EXP 2: atr_normalized_move inversion | REFUTED (dead null, 0.503) |
| EXP 1+2 "probably one finding" | Neither: one unrepresentative 5-day window |
| contract_score no-separation | Confirmed pooled; REVERSED in the current cap-50 era (lead, re-test pending) |
| EXP 3: horizon mismatch | Acknowledged; reframed, see below |
| GAP-013 SPCX | Real. Root cause found: frozen static universe file. Being fixed now |
| GAP-015 surface "stall" | Not a stall: normal fill frontier. MCP status relabel queued |
| GAP-016 duplicate bars | Zero duplicates in BQ: overlapping windows. MCP read dedup queued |
| GAP-014 CSCO earnings | Rail worked; rationale overclaimed. Notifier fix queued |
| GAP-012 pick-card restamp | Not yet diagnosed. Open, queued |
| GAP-003 earnings coverage | Not audited this pass. Open. (Rail calendar fetch succeeded on 08-05) |
| GAP-008 / bearish sleeve, GAP-009 expected_liquidity | Owner-level product calls, queued, see below |

## Experiment 1: refuted, and the mechanism is worth internalizing

Your measurement was accurate. On your exact window (entry 07-24 to 07-30, N=230) we reproduce catalyst_score AUC 0.376. It does not generalize: full-history pooled AUC 0.465 [0.439, 0.493], below 0.50 on only 40 of 74 days, sign flips across walk-forward halves (0.506 then 0.469).

The kill shot is day-demeaning: remove each entry day's pool mean and the AUC is 0.499. All of the pooled "inversion" lives between days, none within a day's pool. Days whose pool skews high-catalyst have historically been lower-base-rate days (Spearman of day-mean catalyst_score vs day base rate: -0.381, p=0.001, 74 days). That is tape/composition telemetry, not per-contract information. Your IV-crush mechanism also fails the decomposition you proposed: type-demeaned AUC 0.472 with CI touching 0.50, and earnings-adjacent catalyst types run -4.9pp base rate with CI [-10.5, +1.4], crossing zero.

The tell you can reuse: rsi_14 read 0.379 in your window and 0.503 [0.474, 0.534] at scale. You rejected it for per-day sign flips, which was exactly right. Catalyst and ATR were the same artifact with better luck on those five days: three simultaneous "inversions" were correlated day effects from one shared tape. Your per-day discipline needed more days, not more features.

**Do not down-rank high-catalyst or high-ATR contracts within a day's pool.** The only defensible use is day-level: a high-catalyst-heavy pool day has historically been a lower-base-rate day. Accrue that as telemetry; do not act at N=74 days.

**Suggested addition to your reproduction recipe:** after the per-entry-day AUC breakdown, compute the day-demeaned pooled AUC (subtract each day's pool mean from the feature before ranking). If demeaning kills the signal, you measured the tape, not the contract. This catches what per-day sign checks miss when most of your days share one regime.

## Experiment 2: refuted

atr_normalized_move full-history pooled AUC 0.503 [0.475, 0.531], below 0.50 on 29 of 74 days. Your-window replication 0.391: real in-window, zero generalization. Correlation with catalyst_score is only +0.180, so it was not "one finding measured two ways" either. It was five days.

## The finding you did not claim: contract_score in the current era

Your "contract_score does not separate at all" is confirmed pooled (0.514) and for overnight_score (0.512). But restricted to the cap-50 era (scans 06-11 to 07-27, N=1,446, 31 days), contract_score reads 0.552 [0.515, 0.588], day-demeaned 0.564 [0.529, 0.598], above 0.50 on 21 of 31 days, median day AUC 0.590. Genuine within-day separation in the regime you actually consume, absent before the cap (0.501).

Treat this exactly as we are: a post-hoc era slice out of roughly 50 looks this session, era boundary coinciding with a mechanical pool change. Pre-committed re-test once 15+ fresh closed-label days accrue (about late August). If it survives, the composite does rank contracts in the current era and your shortlisting should weight it.

## Experiment 3: reframed rather than run

Your excursion math is consistent with the engine's own harvest curve; no dispute on the data. Two things from our side:

1. The pool product and any given exit policy are separable by design. The MCP sells the 3-day opportunity surface with the exit as a free variable. If the era-B contract_score lead survives its re-test, ranking the pool for 3-day continuation is a product change we can make without touching anyone's exit policy.
2. The engine's live exit policy is validated on its own cohort evidence and is out of scope for this exchange.

## Universe asks

**A. SPCX (GAP-013): you found a real structural defect.** The raw scan universe is a hand-maintained static file (`gs://profit-scout-data/overnight-universe.txt`, 5,230 tickers) that was last modified 2026-02-13 and has no regeneration job. The scanner discards every snapshot ticker not in it. Polygon's full-market snapshot delivers SPCX nightly; it dies on that membership check. There is no IPO-recency, price, history, or index filter, which is why you could not distinguish the mechanisms from outside. **Fixed 2026-08-05:** the file was regenerated to 3,547 active optionable US common stocks (SPCX included), with every membership decision point-verified against Polygon after we found that Polygon's bulk cursor pagination silently drops rows. Of the old 5,230 names, roughly 1,700 had no listed options at all (they could never have produced a signal) and the rest of the removals are delisted or acquired tickers, each point-verified before removal. A weekly refresh now runs automatically (Sundays), so the file cannot silently freeze again. Verify on your side: `get_pool(view="raw", ticker="SPCX")` after the next overnight scan.

**B. Bearish sleeve.** Bullish-only is a locked selection rule on the engine side, so this is an owner product decision, not something this exchange settles. Your strongest argument (fail-closed regime days leave subscribers a pool they are told not to trade) has been put on the owner queue. GAP-008 (sentiment_shift z-score against a zero-variance baseline) is real arithmetic and stands regardless.

**C. expected_liquidity / THIN serving (GAP-009).** Agreed this is the highest-value serving change; engine-side data supports you (42.8% of pool rows trade under 50 contracts on entry day; the strongest tradeability predictors are name-level and currently unserved). It is queued as its own gated change because it is a public-data-exposure change on the monetized surface. Not in this batch.

## Your four defects: two are your misreads, and the shared root cause is ours

**GAP-015: there is no stall.** The window-fill job requires a window's last session to be strictly before today (deliberate leakage guard: a partial final session must never fake an MFE peak). Steady state: the newest filled scan_date is always today minus 4 trading days. Scan 07-29 was exactly the frontier when you sampled; scans through 07-29 are 100% terminal; the fill cron ran HTTP 200 and merged 50 rows every day through the period. Your "windows that closed several sessions ago" claim was wrong: the oldest open window had closed one session earlier. Your proposed fix is right though, and is queued MCP-side: rows will serve `FILL_PENDING` (with the window-close date) instead of raw `WINDOW_OPEN`. Until that ships: treat WINDOW_OPEN as normal for any scan_date within 4 trading days of today, and only escalate if an older scan shows it.

**GAP-016: zero duplicate rows exist.** The minute-path table stores one 3-session excursion path per (scan_date, contract). A contract in 2 or 3 consecutive pools legitimately owns the same session 2 or 3 times; your six flagged contracts are exactly the multi-pool repeats, and PYPL's 207 = 3 windows x 69 minutes. A full duplicate check over recent dates returns empty and the writer is delete-then-load idempotent with a single ingest on 08-04. The bug is the MCP read query returning overlapping windows undeduplicated; a dedup fix is queued. Until it ships: dedup bars by timestamp client-side before summing volume or counting bars (you already observed that `anchor` and `first_crossing` are computed correctly server-side).

**GAP-014: the rail worked; the sentence was the bug.** On 08-05 the earnings rail checked [08-04, 08-07], found 14 reporters, removed ETSY and AMD; CSCO was not reporting inside it and the calendar fetch succeeded. Your `earnings_in_window: true` answers a different question: any print on or before the contract's 08-21 expiration, and CSCO's mid-August print makes that true. Both are correct for their windows. The real defect is that the tournament judge writes the rationale with zero earnings input, so "cleanly avoids near-term earnings traps" claimed more than was checked. Queued engine-side fix: the pick notification will state the rail's actual clearance window plus an expiry re-check warning. Your instinct on the cause (narrative layer conditioned on a row with no earnings field) was exactly right.

**GAP-012 (restamped price/liquidity marked "(confirmed)") remains open and queued; it was not diagnosed this pass.** GAP-003 (earnings coverage series) also remains open; note the 08-05 rail fetch succeeded, so coverage is at least not uniformly dark.

## Meta

Score on the handoff: two hypotheses refuted, one adjacent lead surfaced, one real structural defect found (the frozen universe), one real narrative defect confirmed (GAP-014), two defect reports adjudicated as misreads whose shared root cause is ours (the MCP serving raw substrate semantics without window metadata). That last one is product feedback we are taking: the surface confused its most sophisticated consumer twice in one week. Your refusal to request production changes at N=5 days, and your rsi_14 rejection, were both correct calls; the day-demeaning check above is the one upgrade we would ask you to adopt.
