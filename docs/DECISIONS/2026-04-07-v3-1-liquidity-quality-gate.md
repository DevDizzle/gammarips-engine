# Decision: tighten the V3 liquidity gate to a quality-first AND-floor (V3.1)

- **Date:** 2026-04-07
- **Status:** accepted for forward validation
- **Supersedes:** the liquidity portion of `2026-03-26-drop-vix-gate.md`. The no-VIX-gate decision still stands.

## Context
After fixing three off-by-one bugs in `forward-paper-trader/main.py` and replaying the V3 cohort cleanly into `forward_paper_ledger_v3` (3-day hold) and `forward_paper_ledger_v3_hold2` (2-day hold), an audit of the recent regime (Mar 23 – Apr 7) showed only 3 V3-eligible trades over 13 trading days — well below the operating floor of 2 trades/week.

A funnel analysis of `overnight_signals_enriched` for the recent window confirmed the scanner is still producing signals (43–85/day, 17 with `premium_score >= 2` in the window). The bottleneck is the intersection of `premium_score >= 2` with the V3 liquidity gate: most of the recent premium-passing signals fall in mid-cap names whose recommended contracts have asymmetric liquidity (e.g. high volume but near-zero open interest).

A separate audit of the *historical* V3 cohort showed that the OR-form gate `vol >= 250 OR oi >= 500` was admitting trades with severely anemic open interest (CEG vol=500/oi=0, EA vol=5037/oi=0, FTNT vol=252/oi=1, etc.). When the trader simulated these in `forward_paper_ledger_v3`, **7 of 10 such "asymmetric" trades came back `INVALID_LIQUIDITY`** because Polygon could not even find minute bars for them at entry. The 3 that did execute were on contracts with `oi=0` or `oi=36`, where the simulator's mid-bar pricing materially overstates real fillable prices on retail venues like Robinhood.

The core problem was not the *threshold* of the V3 OR-gate; it was the *shape*. An OR between two metrics lets one extreme value mask the other, admitting structurally un-tradeable contracts.

## Strategy thesis (clarification)

While the original V3.1 decision note focused on the liquidity-gate shape change, an investigation into the contract picker NULL rate surfaced that the previous framing of the strategy was inconsistent with how `premium_score` is actually computed in `enrichment-trigger/main.py:599-625`. `is_tradeable` requires HEDGING flow plus a high-risk-reward or high-ATR qualifier; HEDGING flow is a positive contributor to the score, not a reason to skip.

The strategy is a follow-the-hedged-long-position trade. When an institution buys puts as cheap insurance on a name they're long, the hedge tells us they're committed (they spent money protecting the position) and confident (they haven't closed it). We trade WITH the long position by buying calls in the direction the underlying just moved, with high_rr or high_atr ensuring the move still has room to run. The put flow is a confirmation signal, not a directional one.

The current V3.1 forward ledger reflects this: 27 of 31 trades (87%) are HEDGING flow and average +2.5% per trade. 4 trades are DIRECTIONAL at +5.0% (n too small to compare). The cohort is empirically consistent with the thesis and is NOT contaminated.

The premium-score formula and `is_tradeable` rule are load-bearing empirical work (per the 287-signal backfill comment) and must not be modified without fresh backtest analysis.

## Decision
Adopt a V3.1 forward-validation gate that requires both liquidity metrics to clear a floor, with a single fallback for genuinely deep open interest:

```
premium_score >= 2
AND (
      (recommended_volume >= 100 AND recommended_oi >= 50)
      OR recommended_oi >= 250
)
AND recommended_strike IS NOT NULL
AND recommended_expiration IS NOT NULL
```

- `MIN_PREMIUM_SCORE = 2` — unchanged
- `MIN_RECOMMENDED_VOLUME = 100` — both-must-pass floor (was 250 in OR-form)
- `MIN_RECOMMENDED_OI = 50` — both-must-pass floor (was 500 in OR-form)
- `MIN_RECOMMENDED_OI_FALLBACK = 250` — admits contracts with a deep book even if today's volume is light
- `POLICY_VERSION = "V3_1_LIQUIDITY_QUALITY"`
- `POLICY_GATE = "PREMIUM_GTE_2__VOL_GE_100_AND_OI_GE_50__OR__OI_GE_250"`

The macro VIX-gate decision from `2026-03-26-drop-vix-gate.md` is unchanged: VIX remains telemetry only, never an eligibility filter.

## Rationale
- **Both metrics must clear a floor.** Volume measures today's activity; open interest measures the size of the existing book. Either alone is insufficient — exit liquidity in a 2–3 day hold depends on the book existing tomorrow, and the book existing today depends on someone having traded the contract previously.
- **The simulator overstates edge on oi-anemic contracts.** Minute-bar mid pricing in `fetch_minute_bars` does not model bid-ask spread, which is wide on illiquid contracts. The +40% targets the simulator records on `oi=0` strikes are partially fictional: the real Robinhood fill on a contract with no book is at the market maker's spread, often 20–50% worse than the displayed mid. Cutting these trades removes simulator-only edge that would not survive live execution.
- **Empirical evidence**: of 10 historical "STRICT_ONLY" trades that the V3 OR-gate admitted but the V3.1 AND-form rejects, 7 came back `INVALID_LIQUIDITY` in the simulator. The other 3 (n=3) showed a 67% target rate on contracts with oi ≤ 36 — almost certainly simulator artifact rather than real edge.
- **Recent regime**: V3.1 admits one new mid-cap trade in the recent window (GLAD 3/30, vol=161, oi=60) that V3 strict missed.
- **Sample-size cost is acceptable**: V3.1 reduces the historical cohort from 38 → 29 trades, but every trade in that smaller cohort has both an active book and daily volume. The user's stated preference is fewer but solid trades; the operating floor of 2 trades/week is treated as aspirational, not absolute.

## Cohort impact
| | V3 strict (current) | V3.1 quality (new) |
|---|---|---|
| Pre 3/20 (22 days / 4.4 weeks) | 38 trades / 8.6 per week | 29 trades / 6.6 per week |
| Post 3/20 (13 days / 2.6 weeks) | 3 trades / 1.2 per week | 4 trades / 1.5 per week |
| Trades cut (asymmetric oi-anemic) | — | 10 (7 of which were `INVALID_LIQUIDITY` in sim) |
| Trades added (modest-but-balanced) | — | 2 (PDYN, GLAD) |

## Consequences
- Both `forward_paper_ledger_v3` and `forward_paper_ledger_v3_hold2` were truncated and re-replayed under the V3.1 gate. **Update 2026-04-08:** the 3-day shadow table `forward_paper_ledger_v3` and its scheduler trigger were deleted after concluding both hold variants were statistically tied on n=29; the 2-day variant in `forward_paper_ledger_v3_hold2` is the sole canonical ledger going forward.
- The historical winners that V3 strict admitted via the asymmetric OR-form (e.g. STX, MSTR with oi ≤ 36) will not appear in the new V3.1 ledger. Comparisons against the prior V3-strict snapshot are not apples-to-apples.
- The recent-regime cohort remains small (4 trades over 2.6 weeks). The hold-window decision is locked at 2 days for capital-velocity reasons; revisit only with a fresh decision note if a meaningful sample (~6 weeks of forward V3.1 data) shows a clear edge for a different window.
- The 41.6% NULL `recommended_strike` rate in `overnight_signals` is a separate, larger systemic question (the contract picker often rejects all candidates) and remains out of scope for this decision. RGC and SBAC were initially flagged as "correctly NULL" under a hedging-is-bad framing that has since been retracted (see "Strategy thesis (clarification)" above). Whether RGC and SBAC should have been tradeable under the corrected framing is addressed in the "Re-examination of RGC and SBAC" section appended below.

## Follow-up
- The single canonical cron `forward-paper-trader-trigger` runs at 16:30 ET Mon-Fri and writes to `forward_paper_ledger_v3_hold2`. NKE, SLNO, SPCE, UNH, and any other recent-regime trades will land automatically as their 2-day hold windows close — no manual replay needed.
- Investigate the 41.6% NULL-`recommended_strike` rate in `overnight_signals` as a separate work item — likely lives in `src/` or `overnight-scanner/` contract-picker logic. Decide whether un-tradeable signals should be filtered at the scanner stage so premium scoring isn't being run on them at all.
- Revisit the hold-window comparison after both tables have ~6 weeks of forward-only V3.1 data accumulated.

## Re-examination of RGC and SBAC under corrected thesis

The corrected thesis is: trade WITH the underlying's recent move when an institution is HEDGING a long position with cheap puts AND the setup has high_rr or high_atr (room to run). `is_tradeable = (hedge AND high_rr) OR (hedge AND high_atr)`.

### RGC, 2026-04-01

| field | value |
|---|---|
| premium_score | 2 |
| premium_hedge | true |
| premium_high_rr | false (`risk_reward_ratio = 0.47`) |
| premium_high_atr | true (`atr_normalized_move = 2.86`) |
| flow_intent | HEDGING |
| direction | BULLISH |
| price_change_pct | +31.77% |
| atr_normalized_move | 2.86 |
| recommended_strike | NULL (confirmed) |
| call_active_strikes | 3 |
| put_active_strikes | 2 |

Thesis text: *"RGC BEAR $30P Apr 17. Speculative squeeze in a pre-revenue biotech driven by 59% intraday volatility indicates a blow-off top scenario. Entry on signs of momentum exhaustion with a target back toward $26 support as the squeeze fades. Risk: Parabolic extension if rumored strategic partnerships are formally confirmed via SEC filing."*

**Q1 — Did this signal qualify under the corrected thesis?**
`is_tradeable = (hedge AND high_rr) OR (hedge AND high_atr) = (true AND false) OR (true AND true) = TRUE`. Yes — the signal qualifies. The strategy would have wanted to buy a call (direction is BULLISH because price moved +31.77%), not the put referenced in the LLM-generated thesis text. The thesis text is from the Agent Arena's narrative layer and is decoupled from the mechanical `direction` field; under the corrected framing the trade is a long-call follow-the-hedged-long, not the bearish put trade the narrative describes.

**Q2 — Was the picker NULL the right call, or did it fail us?**
**Borderline, leaning right call.** RGC is a low-float pre-revenue biotech with very thin chains. The raw row shows only 3 active call strikes total. With three candidates and a +31.77% intraday spike, every surviving call almost certainly had wide bid/ask spreads (the picker rejects `spread_pct > 0.40`) and/or near-zero quoted bids on the open side. The picker NULL is plausibly correct here — the contract probably wasn't fillable on retail venues even if it had been admitted. Cannot fully verify without re-pulling the historical Polygon snapshot.

### SBAC, 2026-04-02

| field | value |
|---|---|
| premium_score | 2 |
| premium_hedge | true |
| premium_high_rr | false (`risk_reward_ratio = 0.22`) |
| premium_high_atr | true (`atr_normalized_move = 6.51`) |
| flow_intent | HEDGING |
| direction | BULLISH |
| price_change_pct | +22.32% |
| atr_normalized_move | 6.51 |
| recommended_strike | NULL (confirmed) |
| call_active_strikes | 3 |
| put_active_strikes | 2 |
| call_dollar_volume | $14.69M |
| put_dollar_volume | $152K |

Thesis text: *"SBAC NEUTRAL/HEDGE. Takeover interest from infrastructure funds provides a valuation floor, but the +22.3% spike suggests a significant portion of the deal premium is already priced in. Avoid chasing the $14.7M flow as it appears reactive; wait for a retracement to the $190-$195 support zone or a formal bid confirmation. Risk: Rumors are denied or deal talks stall, leading to a rapid 'rumor fade' retracement."*

**Q1 — Did this signal qualify under the corrected thesis?**
`is_tradeable = (true AND false) OR (true AND true) = TRUE`. Yes. SBAC is the cleanest possible expression of the thesis: a $204 large-cap REIT with a +22% takeover-rumor move, $14.69M of call dollar-volume (a 96x skew over puts), HEDGING flow classification, and a high ATR normalized move. The strategy would have wanted to buy a call.

**Q2 — Was the picker NULL the right call, or did it fail us?**
**Likely picker failure.** SBAC is a large-cap with definitely-tradeable listed options on a deal-rumor day with $14.69M of institutional call flow. Three active call strikes is suspiciously thin for a name like this — the most plausible explanation is that the picker's narrow moneyness window `[0.90, 1.25]` excluded the strikes where the $14.69M flow actually concentrated (deep ITM bid-up calls or far OTM upside calls on a takeover spike are both common and both outside that window). This is exactly the failure mode the corrected thesis cares most about: a clean DIRECTIONAL+HEDGING+high_ATR setup on a liquid name that the picker silently dropped. SBAC is the best evidence in the cohort that the picker is leaving real trades on the table.

### Summary

Both signals qualified under the corrected thesis. RGC's NULL is plausibly correct (thin biotech chain, wide spreads). SBAC's NULL is most likely a picker failure on a clean, liquid setup. RGC and SBAC should not be removed from the cohort on a "hedging is bad" basis — the previous note's framing on this point was wrong. SBAC in particular is a worked example of the problem the next section addresses.

## Picker fix recommendation

**Recommendation: needs more analysis before implementing, but lean yes.** Adding an OI-only fallback to `_best_contract` that mirrors the V3.1 trader gate's `oi >= 250` bypass (admit a contract whose moneyness is in band and whose `open_interest >= 250` even if `vol < 10`, `spread_pct > 0.40`, or `bid/ask` are missing) would plausibly recover 2-5 additional trades over the 35-day Feb 18 - Apr 7 window — concentrated in large-cap names like SBAC, CHE, TYL, and CVCO where deep books exist but daily prints on individual contracts are sparse. Microcap NULLs (ATOM, RXT, ALTO) would not be recovered because they don't have any oi-deep contracts. The risk of admitting unfillable contracts is bounded: the V3.1 trader gate already requires `(vol >= 100 AND oi >= 50) OR oi >= 250`, so any picker emission that the trader gate rejects produces no trade, and any contract that does fire and isn't fillable shows up as `INVALID_LIQUIDITY` in the ledger — a safe failure mode the existing pipeline already handles. The fallback should be **unconditional** (not gated on `flow_intent = HEDGING`) because the picker runs at the scanner stage before `flow_intent` is computed in enrichment, and conditioning would require restructuring the pipeline. Before implementing, the picker should be instrumented to log per-candidate reject reasons for one to two days so we can confirm which filter is biting on the SBAC-class failures — without that, the OI-fallback is an educated guess about the failure mode rather than a measured fix. User decision required.
