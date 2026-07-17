# V5.4 Methodology Audit — 2026-05-09

**Audit type:** Read-only methodology review (NOT a code-safety review).
**Auditor:** `gammarips-researcher` subagent.
**Trigger:** Two methodology bugs (`moneyness abs()`, brackets-blind prompts)
caught today via operator inspection that `gammarips-review` did not flag —
because that subagent audits *code safety* (lookahead, leakage, unsafe
execution), not *whether each parameter has any literature or data backing*.
This audit is the missing layer.

**Scope:** Every parameter, threshold, and filter on `CHEAT-SHEET.md` plus
the live decision-path components (enrichment gates, signal-notifier hard
gates, scorer/picker rubric, trader bracket, scanner cluster boost,
report-v2 mean-reversion threshold).

**Verdict:** Safe to fly Monday 2026-05-11. Three to five items deserve
testing once we have N≥15 closes.

---

## 1. Executive summary

V5.4's filter stack is in **mixed methodological health**:

- **Robust:** spread ≤ 8%, moneyness 5-10% OTM (post-fix), VIX ≤ VIX3M,
  no-earnings-through-hold, V/OI > 2 floor, OI ≥ 20 / volume ≥ 100. These
  have either named-paper support with verified citations OR a defensible
  exclusion logic the literature has settled at scale we can't replicate.
- **Folklore-with-rationalization:** the `+80% / −60% / 3-day` bracket, the
  `10:00 ET / 15:50 ET` entry-exit clock, the `60/25/15` composite weights,
  and the `overnight_score >= 1` enrichment gate. None of these have a
  peer-reviewed paper backing the *specific value*. They are operator /
  Deep-Research recommendations with intuition-grade backing. Not
  known-broken — just unmeasured. The 60/25/15 weights are explicitly
  tagged as v0 priors in the locked-spec note.
- **Compounding-risk:** the gate stack as composed implicitly bets on a
  single regime (calm-market, no-earnings, sector-momentum). Each gate
  alone is defensible; composed, they may select a perverse cohort during
  extended low-vol periods.

The two bugs caught today (moneyness `abs()` and brackets-blind prompts)
are illustrative — both passed `gammarips-review` because that subagent
audits *code safety*, not *whether the parameter has any literature or
data backing for the value chosen*.

---

## 2. Top-3 highest-risk findings

### Finding 1 — `+80% / −60% / 3-day` bracket has NO peer-reviewed support for the specific values
**Severity:** HIGH on uncertainty, LOW on action.

The bracket's only citation is "Deep Research recommendation" in
`2026-04-17-v5-3-target-80.md`. Deep Research is not literature. The
quoted text recommended "+80% to +100% target combined with a trailing
stop-loss that activates only after +30% gain" — we kept the +80% number
and *deleted the trailing-stop conditional*, leaving us with a plain −60%
hard stop the cited recommendation does not endorse. Asymmetric profile
(1.33× win:loss in option-premium space) implies a required win-rate of
~43% to break even at zero EV, before slippage.

**No paper studies +80%/-60% on 3-day OTM bracketed exits.** Adjacent
literature: Bollen & Whaley 2004 (vol surface dynamics, no bracket),
Coval-Shumway 2001 (expected returns, no exit policy), Goyal-Saretto 2009
(vol risk premium, monthly horizon).

**Recommendation:** Don't change pre-launch. After N=15 V5.4 closes, do a
bracket-distribution analysis: histogram realized peak premium gains and
peak drawdowns. If most winners cap out before 80% or most losers blow
through 60%, the bracket is the wrong shape and should be revisited *with
data*. Until then, this is a deliberate operator policy choice, not a
falsified rule.

### Finding 2 — `overnight_score >= 1` is a near-pass-through gate, not a gate
**Severity:** MEDIUM.

`overnight_scanner.py:573-632`: the score ranges 0-12 (six signals each
contributing 0-2 except momentum/divergence at 0-1). Threshold of 1 is
satisfied by *any single hit* in the stack — even just "price moved >1.5%"
alone passes.

**Concern:** the 2026-04-12 V4 launch tightened to score ≥ 1 from the
original ≥ 6. There is no `DECISIONS/` note explaining why ≥1 was chosen
over ≥3. The 2026-05-01 ranker note even reports `premium_score=0` rows
had *higher* win-rate (43.9%) than `premium_score≥1` — actively
anti-predictive on the V5.3 cohort. The score is now functioning as a
"this row was scanned" tag rather than a signal-quality filter.

**Recommendation:** Downstream of V/OI, moneyness, spread, VIX, and
earnings filters that ARE doing real work, so unlikely to be load-bearing.
But the *cluster boost* tops scores up by +1/+2/+3; combined with the ≥1
floor, cluster-boosted tickers are essentially guaranteed to pass. After
N=15, query whether cluster-boosted tickers have different EV than
non-boosted picks. If yes, the cluster boost is doing something. If no,
both the boost and the gate are decoration.

### Finding 3 — Composite weights `60/25/15` are an unargued-from-data prior
**Severity:** MEDIUM.

Per `2026-05-08-v5-4-locked-spec.md`, weights cite Pan-Poteshman 2006,
Hu 2014, Cheng 2019, Tetlock 2007, Engelberg et al. 2012. **Verification:
each paper exists and broadly supports the *ordering* (flow > regime >
narrative for short-horizon directional trades).** Pan-Poteshman 2006
("The Information in Option Volume for Future Stock Prices," RFS) shows
option-flow predictive power peaking days 1-2, consistent with our 3-day
hold. But **none of these papers prescribe a specific 60/25/15 split.**
Decision note honestly tags it "v0 prior" and locks a re-weight trigger
at N=30 V5.4 closes via per-dimension IC analysis. Right disposition.

**Concrete failure mode:** if `narrative_coherence` IC turns out negative
(Engelberg paper shows news is largely priced in by the open, so
narrative-coherent trades may underperform), the 15% weight is still
pulling picks toward "good story" candidates. With composite as a
weighted sum, even a 15% weight on an anti-predictive dimension drags
the whole rank.

**Recommendation:** N=30 IC decomposition is already the trigger. Add a
guardrail: if ANY dimension shows negative IC at N=15 (preliminary signal),
surface it in a research note even if we don't re-weight yet.

---

## 3. Decision matrix

| Decision | Current value | Where it lives | Literature support | Project data support | If wrong, what breaks | Verdict |
|---|---|---|---|---|---|---|
| Enrichment gate `overnight_score >= 1` | 1 (of 0-12) | `enrichment-trigger/main.py:336`, env `MIN_ENRICHMENT_SCORE` | None for the threshold. Score itself is hand-tuned 6-signal composite (skew, V/OI, multi-strike, UOA $, momentum, divergence) with no paper backing weights. | **Anti-evidence:** 2026-05-01 ranker shows `premium_score=0` had higher win-rate than `premium_score≥1` on N=435 V5.3 trades. | Pass-through; if removed, more candidates reach downstream filters. Likely no perceptible effect. | **FOLKLORE** |
| Enrichment gate `recommended_spread_pct <= 0.08` | 8% | `enrichment-trigger/main.py:337` | Muravyev & Pearson 2020 (RFS) — verified. Cremers & Weinbaum 2010 (JFQA) — verified. **Caveat:** doesn't prescribe a single threshold; 8% is operator's calibration. | None directly. | Marginal-fit candidates (8-10%) re-enter pool. ~+15-25% candidate volume. EV impact unknown without backtest. | **LITERATURE-BACKED** (direction) / threshold value calibrated, not derived |
| Enrichment gate directional UOA > $500K | $500,000 | `enrichment-trigger/main.py:339-340` | Pan-Poteshman 2006 implicit — informed flow tends to be institutional-sized. **No paper prescribes $500K specifically.** Johnson-So 2012 (RFS) works in V/OI not absolute dollars. | None for the threshold. | Lower = more retail noise; higher = fewer candidates. Likely modest effect since V/OI gate downstream catches retail noise. | **FOLKLORE** (direction defensible, value not) |
| Notifier gate `volume_oi_ratio > 2.0` at focal strike | 2.0 | `signal-notifier/main.py:92,926` | Johnson-So 2012 (RFS) — V/OI deciles predict cross-sectional returns. Roll-Schwartz-Subrahmanyam 2010 (RFS, O/S ratio). **Threshold 2.0 is not literature-derived.** | 2026-05-01 ranker: `directional V/OI DESC` lead key, 80% win-rate (8/10) on N=435 V5.3 trades. **Walk-forward held 4/5 + 4/5.** Real project-data evidence the *direction* is correct; doesn't validate 2.0 as the threshold. | Pool grows but rank order favors higher V/OI; downstream filters and LLM scorer still see it. Likely safe within ±0.5. | **BOTH** (direction backed; threshold itself folklore) |
| Notifier gate `moneyness_pct BETWEEN 0.05 AND 0.10` | 5-10% OTM (sign-aware as of 2026-05-09) | `signal-notifier/main.py:93,99,928` | H12 audit cites Augustin et al. 2022 (J. Fin. Markets) and Aretz, Lin & Poon 2023 (RoF). **Verified — both papers exist.** Pan-Poteshman 2006 supports OTM-vs-ITM ordering. **Aretz et al. specifically documents the ITM +7% / DOTM −27% systematic-vol return spread.** | None on labeled_v1 (correctly per lit-audit methodology — that cohort is regime-confounded). | Pre-fix bug let ITM through, which the prompt couldn't catch (URI 6.79% ITM picked as bullish). With fix, structurally-wrong contracts are excluded upstream. | **LITERATURE-BACKED** (post-fix; pre-fix actively broken) |
| Notifier gate `VIX <= VIX3M` (no backwardation) | scalar comparison, fail-closed if NULL | `signal-notifier/main.py:983` | Cheng 2019 (RFS, "The VIX premium"). Term-structure papers (Mixon 2007, Whaley 2009 JPM). Direction support strong; no paper prescribes "use this as a binary trade gate on 3-day options." | None directly. | Backwardation days = stress regime; long-premium trades get demolished by IV mean-reversion. ~10-15 trading days/year (estimate). | **LITERATURE-BACKED** (direction); usage as binary gate is operator-calibrated |
| Notifier gate "no earnings during hold window" | `[scan_date, entry_day + 2 trading days]` | `signal-notifier/main.py:994+` | De Silva, Smith & So 2026 (RoF). Cao & Han 2013 (JFE). Dubinsky & Johannes 2006 (Columbia WP, IV crush). Goyal & Saretto 2009 (JFE). **All four cited correctly; this is the most rigorously-grounded gate in the stack.** | CDW 2026-05-06 trigger event (N=1 anecdote). Lit consensus overwhelming. | Per De Silva 2026: 5-9% loss/event for retail through earnings, 10-14% on high-vol names. Removing the gate plausibly catastrophic. | **LITERATURE-BACKED** (highest confidence in stack) |
| Notifier gate `recommended_oi >= 20` and `recommended_volume >= 100` | 20 / 100 | `signal-notifier/main.py:100-101,930-931` | Generic market-microstructure literature on illiquid-option pricing (Mayhew 2002 cited in H11). No paper specifies 20 or 100. | None. | Floor exists to prevent dead-listing fills. Operator-side executability concern (Robinhood fills). | **FOLKLORE** (operator-calibrated; not load-bearing for EV but for executability) |
| Trader bracket `+80% take-profit` | 80% | `forward-paper-trader/main.py:50` | None for +80% specifically. Deep Research (not literature) recommended +80%-+100% combined with a trailing stop. Trailing-stop component was deferred. | None on specific value. labeled_v1 bracket-sweep chose 40/-25 (different bracket entirely) and showed EV −4.26%. | If too tight: cap winners early. If too loose: rare hits. Asymmetry → ~43% win-rate to break even. | **FOLKLORE** |
| Trader bracket `−60% stop` | 60% | `forward-paper-trader/main.py:49` | None. "Wide stop absorbs IV crush" comment is intuition, not citation. | None. | If too tight: stopped out by intraday noise + IV mean-reversion. If too loose: full premium loss. | **FOLKLORE** |
| Trader hold = 3 trading days | 3 | `forward-paper-trader/main.py:48` | Pan-Poteshman 2006 finds option-flow alpha peaks days 1-2 (consistent with 3-day hold). Hu 2014 short-horizon literature aligns. **No paper prescribes exactly 3 days.** | Frozen `signals_labeled_v1` was labeled at 2-day and 3-day holds; bracket sweep was inconclusive. | If 1-2 days: theta less of a problem, cuts off larger moves. If 5+ days: theta tax + event risk. | **FOLKLORE** (direction supported, exact value not) |
| Trader entry `10:00 ET day-1` | 10:00 ET | `forward-paper-trader/main.py:51` | Heston, Korajczyk, Sadka 2010 (JF, "Intraday patterns") — opening-half-hour vol clustering. Stoll-Whaley 1990. **No paper says "10:00 specifically."** | None. | Too early = caught in opening volatility / wide spreads. Too late = premium already moved. 30-min lag from open is operator-calibrated. | **FOLKLORE** (with adjacent lit support for "wait for the open to settle") |
| Trader exit `15:50 ET day-3` | 15:50 ET | `forward-paper-trader/main.py:52` | None for 15:50. End-of-day liquidity literature broadly supports avoiding 16:00 close. | None. | Too early = miss late-day moves. Too close to close = wide spreads. 10-min cushion is operator practical. | **FOLKLORE** |
| Composite weights `60% flow / 25% regime / 15% narrative` | 60/25/15 weighted sum | `signal-ranker/app/agent.py` | Pan-Poteshman 2006 (flow), Hu 2014 + Cheng 2019 (regime), Tetlock 2007 + Engelberg et al. 2012 (narrative). **All papers verified.** Order is correct per literature; **specific weights are not derived.** | None — V5.4's first run. | If narrative IC negative (Engelberg shows news priced in by open), 15% drag on every score. If flow IC lower than thought, 60% over-weights it. | **CONTESTED** (ordering literature-backed; magnitudes v0 prior, explicitly tagged) |
| Scorer hard cap `flow_conviction ≤ 4 if HEDGING` | ≤4 | `scorer_v4.md:65` | Pan-Poteshman 2006 implicit — hedging flow ≠ informed directional. **No paper prescribes ≤4.** | `project_hedge_flag_is_the_alpha.md` documents CONTRADICTED N=30 finding — hedge flow EV was −12% on N=1,563 labeled scan. Hedge flow does anti-predict; cap directionally agrees. | If too lenient: hedge candidates score high. If too strict: legitimately-informed flow tagged as HEDGING gets excluded. | **DATA-BACKED** (project memory confirms hedge anti-predicts) |
| Scorer hard cap `flow_conviction ≤ 4 if ITM` | ≤4 if `moneyness_pct < 0` | `scorer_v4.md:66` (added 2026-05-09) | Coval-Shumway 2001, Pan-Poteshman 2006, Easley-O'Hara-Srinivas 1998 — all support OTM > ITM for short-horizon directional. **Verified.** | None directly. Trigger was the URI 5/8 backfill anecdote. | Belt-and-suspenders cap. The moneyness gate now filters ITM upstream; cap mostly matters as defense against future signed-vs-abs regression. | **LITERATURE-BACKED** |
| Scorer DTE sweet spot `7-30 DTE` | 7-30 | `scorer_v4.md:18` | Theta/gamma calculus — short-dated options gain from realized moves but lose to time decay. **No paper prescribes 7-30 specifically for 3-day holds.** | None directly; `recommended_dte` distribution in V5.3 ledger likely centered here, no recorded EV-by-DTE analysis. | If too short: gamma-heavy but theta-savaged on stalls. If too long: bracket harder to hit on 3-day moves. | **FOLKLORE** (with adjacent theta/gamma intuition) |
| Cluster boost `4 tickers = +1, 5-7 = +2, 8+ = +3` | size-tiered | `scanner.py:280-285`, threshold `CLUSTER_BOOST_THRESHOLD=6` | None. "Industry co-movement" intuition. | None recorded. | Boosts under-threshold tickers when 4+ industry siblings move same direction. | **FOLKLORE** |
| Mean-reversion-risk threshold `>= 0.5` | 0.5 | `overnight-report-generator/main.py:226` | None. Composite (RSI extremes + ATR z-score + price-change extremes + reversal_probability) is hand-tuned heuristic. | Per `2026-05-09-report-v2-literature-grounded.md`: "observed avg 0.16 / max 0.82 over 2026-04+ data." **0.5 is at the ~80th percentile.** Project-data calibration. | Flag is informational in `report_v2`. If too high: silent on borderline risk. If too low: floods report with false flags. | **DATA-BACKED** (project-percentile-derived) |
| Notifier rank lead key `directional V/OI DESC` (V5.4 candidate-pool) | descending V/OI | `signal-notifier/main.py:932-937` | Johnson-So 2012 RFS, Roll-Schwartz-Subrahmanyam 2010 RFS. | 2026-05-01 ranker EDA: 8/10 win-rate vs 17% on dollar-volume primary, walk-forward 4/5 + 4/5. **Strongest project-data evidence in stack.** Multiple-comparison risk per FINDINGS_LEDGER §Filter Discovery; deflated. | This selects the top-10 fed to the LLM ranker. If wrong direction: V5.4's input pool contaminated. | **BOTH** (literature on V/OI; project data on the specific ordering) |

---

## 4. Compounding-effect concerns

The gate stack composes into an **implicitly regime-conditioned filter**:

1. **`VIX ≤ VIX3M`** — calm/contango regime only. ~10-15 trading days/year excluded.
2. **No earnings in hold window** — peak earnings weeks decimate the candidate pool.
3. **5-10% OTM** — excludes ATM and DOTM, both of which dominate flow during stress regimes.
4. **Spread ≤ 8%** — strips out most small-cap names regardless of catalyst quality.
5. **Score ≥ 1, V/OI > 2, UOA > $500K** — biases toward mid-cap-and-up flow.
6. **Sector cluster boost** — implicitly bets on momentum continuing within sectors.

**The composed cohort is calm-market large-cap sector-rotation plays during
non-earnings weeks.** If 2026-Q3 enters a Q4-2018-style stress regime, the
entire system mostly stays out of the market (good — fail-closed). But if
it transitions into a *sustained* low-vol drift regime, the system is
implicitly betting on momentum-continuation in sectors that are already
trending. **A regime shift to mean-reversion would directionally invert EV.**

This is not a bug — it's the system's deliberate posture. But it should be
named explicitly: **V5.4 is a momentum-continuation bet conditioned on calm
regimes.** Not a vol-arbitrage strategy, not a contrarian strategy. The
Picker's `regime_alignment` rubric is the only line of defense against
regime-flip surprise, and it operates on a single daily report.

**Concrete failure mode to monitor:** if `cohort_stats/current` shows a
string of 5+ consecutive losses with no skipped days (gates kept emitting
picks but they kept losing), that's the regime-shift signal — the gate
stack failed to detect that its preferred regime ended.

**Operator rule:** at 5 consecutive losses, pause and rerun the regime
question manually before the next pick.

---

## 5. What to revisit at N=15 V5.4 closes

FOLKLORE/CONTESTED items that become testable with our own ledger data:

1. **`overnight_score >= 1` gate** — query whether score ≥ 3 picks have
   materially different EV than score 1-2. If no difference, gate is
   decoration; if score ≥ 3 outperforms, tighten.
2. **Cluster boost +1/+2/+3** — query EV for cluster-boosted picks vs
   non-boosted. The 2026-05-01 ranker EDA didn't break this out; V5.4
   ledger should.
3. **Composite weights 60/25/15** — per-dimension IC analysis (already
   locked as N=30 trigger). Add soft check at N=15: any dimension with
   negative IC gets a research-note flag.
4. **`+80%/-60%` bracket shape** — at N=15, distribution of *peak*
   premium gain and *peak* drawdown for each closed trade. If peak gains
   cluster at 30-50%, +80% target is too far. If most stops fire from
   intraday wicks, −60% may be too tight.
5. **DTE sweet-spot 7-30** — bucket EV by DTE quartile. If 7-15 outperforms
   20-30 or vice versa, narrow.
6. **VIX≤VIX3M binary gate** — query whether picks taken on small-margin
   days (VIX/VIX3M ratio 0.95-1.00) have similar EV to high-margin days
   (ratio < 0.85). If small-margin days are losers, tighten the gate.
7. **Hedge-flag cap (≤4 flow_conviction)** — query Scorer-level: do
   HEDGING-tagged candidates that nonetheless got picked perform worse
   than DIRECTIONAL picks? Project memory says yes (-12%); confirm on
   V5.4 ledger.
8. **Mean-reversion-risk threshold 0.5** — query whether picks where the
   report flagged MRR ≥ 0.5 underperformed picks where it didn't.

**Items 1, 2, 4, 5 are highest-leverage** — un-evidenced parameters most
likely to be load-bearing on EV.
