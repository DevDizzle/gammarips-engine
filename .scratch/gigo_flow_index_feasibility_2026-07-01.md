# Feasibility Finding — GIGO Whole-Pool "Flow Index" Composite

**Date:** 2026-07-01
**Context:** Grounding pass for the monetization-pivot BUILD workflow (Workflow #1 in `NEXT_SESSION_PROMPT.md`, 2026-07-01 block). The pivot wants to repurpose the public Scorecard into a **"GammaRips Flow Index"** — a daily composite of the WHOLE tilted-BULLISH enriched pool, with each name's ROI unit = the live V7.1 "GIGO" bracket-replay (10:00 ET entry / +40% take-profit / −30% stop / flat 15:45 ET, same-day).
**Method:** read-only scout — BigQuery on `enriched_option_outcomes` + code read of `forward-paper-trader`. This is a **preview / grounding number**, not a fully-adversarial measurement. See "Confidence & caveats."

---

## TL;DR (the decision-relevant two lines)

1. **Feasibility is SOLVED.** The GIGO-at-pool-width dataset already exists, is correct, current, and self-maintaining. No re-replay needed. Go straight to measurement.
2. **The composite loses money, robustly.** Whole-pool GIGO composite is **−2.14%/day** (all 53 days) and **−5.71%/day** on the ~50-name pool you'd actually surface today, win rate 29.7%, and it **gets worse walk-forward**. Publishing a tradeable-ROI "Flow Index" off this markets a losing strategy — do **not** ship it as-is (this is exactly the handoff's step-(c) "MEASURE, THEN MARKET" backfire).

---

## 1. Feasibility verdict: ALREADY BUILT & CURRENT

The long-pole question ("can we get minute option bars at pool width, ~50/day, or must we re-replay?") is a non-issue. Confirmed from code, not docs:

- **Table:** `profitscout-fida8.profit_scout.enriched_option_outcomes` (BQ, dataset `profit_scout`), 64 columns, partitioned on `entry_day`, clustered on `ticker`.
- **Live cron:** Cloud Scheduler job `forward-paper-trader-label-pool` is ENABLED, fires `0 17 * * 1-5 America/New_York` (17:00 ET, after the 16:30 trade cron + 16:15 MTM). Endpoint `POST /label_enriched_pool` → `run_label_enriched_pool` → `_write_enriched_outcomes`.
- **Genuine intraday touch detection:** the replay calls `fetch_minute_bars(opt_ticker, entry_day, exit_day)` (Polygon `/range/1/minute/`) and walks bars checking `h >= target` / `l <= stop`. GIGO is same-day so `entry_day == exit_day` → one session of 1-minute option bars per contract. Not a daily-bar proxy.
- **Byte-identical to production:** the pool replay reuses `_simulate_contract` verbatim (`pick_doc=None`), so labels match the live ledger mechanics exactly (proven earlier: SPG 2026-06-09 replay row == ledger row).

**No extension work is required for feasibility.** The only remaining work is the *measurement* (methodology choices below) — and the measurement is what returns a red light.

---

## 2. Coverage & schema (what's in the table)

- **Rows:** 3,189 raw / **3,044 after dedup** (145 dup rows, all on 2026-06-11).
- **Distinct entry_days:** 53. **Range 2026-04-13 → 2026-06-30** (current through last trading day).
- **Continuity:** 53 of 55 in-window NYSE sessions. Two genuine holes: **2026-05-20** (scan 05-19 lost to a DNS hiccup) and **2026-06-05** (engine quote-outage day). 05-26 / 06-22 are Memorial Day / Juneteenth (not real gaps).
- **Mechanics:** `policy_version` = `V7_INTRADAY` (2,839) + `V7_1_TILTED_GIGO` (350). **Both are same-day GIGO** (verified empirically: avg target 1.40× entry, avg stop 0.70× entry, 0 multiday rows, 0 trail activations, every filled row exits on the entry calendar day). The two tags differ only in the upstream selection tilt, not the exit regime.
- **Direction:** 100% BULLISH (matches the surfaced tilted-BULLISH pool, not all-directions/raw scan).
- **Per-day width:** min 24 / median 50 / max 290 (the 06-11 dup). Recent 10 sessions: exactly 50/day. **Fill rate ~71%** have realized PnL; ~29% are `INVALID_LIQUIDITY` (no tradeable 10:00 option bar).
- **Exit-reason mix (filled):** ~77% TIMEOUT (avg −1.24%) / ~15% STOP (avg −37.5%) / ~7% TARGET (avg +37.2%).
- **Key columns:** point-in-time features (`recommended_delta/gamma/theta/vega/iv`, `risk_reward_ratio`, `atr_normalized_move`, `moneyness_pct`, `volume_oi_ratio`, `overnight_score`, `contract_score`, `catalyst_score`, `premium_score`, `underlying_price`, `atr_14`, `rsi_14`), regime (`VIX_at_entry`, `SPY_trend_state`, `vix_5d_delta_entry`, `vix3m_at_enrich`), label group (`entry/target/stop/trail` prices, `peak_premium`, `exit_timestamp`, `exit_reason`, **`realized_return_pct`**, `exit_slippage`, `illiquid_exit`, `late_fill_minutes`), benchmarks (underlying/SPY entry/exit/return), linkage (**`was_tournament_pick`**, **`was_topscore_pick`**, `pool_size`, `policy_version`, `labeled_at`). Weightable columns: `overnight_score`, `contract_score`, `premium_score`, `catalyst_score`, `call_dollar_volume`, `put_dollar_volume`.

---

## 3. Preview composite number (the landmine)

Dedup applied; all rows BULLISH. "Filled" = `realized_return_pct IS NOT NULL` (excludes `INVALID_LIQUIDITY`); "clean" additionally drops `illiquid_exit = TRUE`.

### Row-level (each filled contract = 1 obs)
| Metric | Value |
|---|---|
| EW mean, filled-only | **−4.29%** |
| Median, filled | −1.96% |
| Win rate | 29.7% |
| EW "clean" (excl illiquid_exit) | **−6.15%** (n=1,133, WR 36.6%) |
| EW, INVALID-as-0% | −3.05% |
| Score-weighted (overnight_score) | −4.80% |

### Day-level (each day = 1 obs — the fairer "index" construction)
| Window | Days | Mean daily EW | SD | Worst / Best |
|---|---|---|---|---|
| ALL | 53 | **−2.14%** | 5.72% | −18.98% / +8.40% |
| First half | 26 | −0.29% | 3.69% | |
| Second half | 26 | −4.03% | 6.86% | |
| Last 20 | 20 | −5.20% | 7.31% | |
| **Post-cap ~50 pool (≥2026-06-12)** | 12 | **−5.71%** | 6.39% | |
| Pre-cap wide pool (<2026-06-12) | 41 | −1.10% | 5.13% | |

### Three findings that make this hard to salvage
1. **Walk-forward makes it WORSE, not better** (first half −0.29% → last-20 −5.20%). Robust negative, not a recency artifact inflating a fake edge.
2. **The pool-as-surfaced-today is the worst slice** (−5.71%/day post-cap). The edge-ranked top-50 the pivot would index underperforms the old wide pool — consistent with prior "edge-tilted / top-score picks mean-revert" findings.
3. **Restricting to liquid names does NOT rescue it** (−6.15% clean). The +40/−30 same-day bracket on liquid contracts just times out (77% timeout, 7% target).

### Consistency with prior project knowledge
This is not a surprising outlier — it agrees with `project_exploit_winners_falsified` (edge-tilted picks mean-revert), `project_agent_data_readiness` (edge-test underpowered, 0 levers survived walk-forward, pool baseline ~−0.63%), and `project_live_oi_liquidity_floor` (V7.1 ran ~−8% mean Apr–Jun; "buys execution honesty, NOT alpha").

---

## 4. Methodology levers & gotchas (for a rigorous follow-on)

1. **Dedup 2026-06-11** (145 contracts × 2). Use `ROW_NUMBER() OVER (PARTITION BY entry_day, ticker, recommended_contract ORDER BY labeled_at DESC)`. Without it 06-11 gets ~3× weight in any row-level mean.
2. **Non-stationary pool definition** = a structural break in the index. `ENRICH_TOP_N=50` cap landed ~2026-06-12; before that the grounded pool ran ~60–170/day. Scope the "as-marketed" index to `entry_day >= 2026-06-12`, or disclose the two regimes. Prefer **day-level equal-weighting** so wide early days don't dominate.
3. **`INVALID_LIQUIDITY` (29%) is the single biggest methodology lever AND a survivorship trap.** Filled-only (−4.29%) silently drops untradeable names; invalid-as-0% (−3.05%) is more honest. Never publish filled-only without flagging it.
4. **Stale docstrings:** `backfill_enriched_option_outcomes.py` / `create_enriched_option_outcomes.py` still say "+80/−60/trail, 3-day hold" — WRONG. The data is empirically same-day GIGO because the script drives the live `_simulate_contract`. Trust the data, not the docstring; do not re-run expecting 3-day labels.
5. **Two missing sessions** (05-20, 06-05) — decide carry-forward vs skip for any index series.
6. **Leakage posture is clean for measurement.** `realized_return_pct` is a forward bracket-replay OUTCOME (correct as a label); features are point-in-time. The label group must be used ONLY as labels, never fed back as features. No feature leakage detected in table construction. **Leakage remains the one non-negotiable — any measurement that gets published must be re-audited by `gammarips-review`.**
7. **`was_tournament_pick` / `was_topscore_pick`** let you test whether the operator's single private pick beats the pool composite (keeps the private-pick and public-index narratives separate).

---

## 5. Separate finding (same grounding pass): the MCP leaks the pick publicly

Not part of the composite question, but it directly affects the pivot's "make the single pick private" decision:

- `gammarips-mcp` (repo `/home/user/gammarips-mcp`, FastMCP, Cloud Run) is deployed **`--allow-unauthenticated`** and listed publicly on Smithery.
- Its **`get_todays_pick`** tool returns the exact daily tournament pick (ticker/direction/contract/strike) to **any caller** — i.e. the "private" pick is currently public via the MCP.
- 18 tools total, cleanly tiered (8 raw-data / 6 methodology / 2 pick-returning), with good input-validation / error-redaction / schema-whitelist / IP rate-limiting — but **no per-subscriber auth, no metering, no tier-gating** (single-tenant-by-assumption, not access-controlled).
- Productization gap list (for the WF #2 single→multi-tenant thesis): per-key auth, subscriber-based rate-limiting, usage metering/billing, feature/tier gating, data-exposure policy. The `get_todays_pick` tier is the legal+leakage crux.

---

## 6. Decision implications & recommended forward paths

The pivot's premise — "sell a proven Flow Index; the composite proves the sort works" — is **falsified by the data**. The composite doesn't clear zero; it's negative and worsening on the exact pool you'd surface.

Coherent options (owner to choose):

- **A. Reframe + go agent-mode (recommended).** Drop the tradeable-ROI "Flow Index." Reframe any public index as a backward-looking **flow-strength / activity descriptor** (data-not-advice — does NOT need profitability). Pursue **agent-mode/MCP as a data-vendor** (sells flow data + methodology primitives, buyer's agent decides — also does NOT need the pool profitable; fits the "anti-firehose" positioning of record). Fix the MCP pick-leak.
- **B. Salvage-hunt.** Run a rigorous adversarial measurement workflow: bootstrap + day-level CIs, all `INVALID_LIQUIDITY` conventions, and a multiple-comparison-aware search for any leakage-safe sub-slice (score band, delta, momentum tilt, regime) whose walk-forward composite clears zero. **Odds low** (every prior finding agrees), real overfitting risk on a 53-day / single-regime sample.
- **C. Radical transparency.** Publish the composite as-is including the negative number; sell honesty + curation. Maximally defensible, hard to convert on a negative track record.

The composite still has value regardless: it's the engine's label substrate (~50× the single-pick cohort) and an honest internal benchmark, and it settles the owner's "the picks do alright" bet (they don't, on the pool under GIGO).

---

## 7. Confidence & caveats

- The composite numbers are a **single read-only scout pass** (dedup applied, day-level + row-level, walk-forward split, multiple conventions — internally consistent). They are strong enough to **stop a build** but should get a **bootstrap/CI + `gammarips-review` confirmation** before being *published* in any form.
- The direction of the result (robustly negative, worsening) is high-confidence because it matches all prior project findings; a confirmation pass is about the exact magnitude and any salvageable sub-slice, not about whether the sign flips.

---

## 8. Reproduce / source paths

- **Table:** `profitscout-fida8.profit_scout.enriched_option_outcomes` — query with `bq query --use_legacy_sql=false --project_id=profitscout-fida8 ...` (read-only; the shell's `PROJECT_ID` may point elsewhere — pass `--project_id` explicitly).
- **Replay + label writer:** `forward-paper-trader/main.py` — `_simulate_contract` (~L571-935), `fetch_minute_bars` (~L662), `_write_enriched_outcomes` (~L1381-1551), `run_label_enriched_pool` (~L1554-1591), `POST /label_enriched_pool` (~L1921-1946), GIGO constants (~L54-111).
- **Backfill driver (STALE docstring):** `scripts/ledger_and_tracking/backfill_enriched_option_outcomes.py`
- **DDL:** `scripts/ledger_and_tracking/create_enriched_option_outcomes.py`
- **MCP:** `/home/user/gammarips-mcp/src/server.py` + `src/tools/*` + `src/utils/safety.py`
- **Publish surfaces (for the wire-up if a path is chosen):** engine `signal-notifier/main.py` (`write_todays_pick_doc`, `compute_and_write_cohort_stats`, `compute_and_write_ledger_trades`), `x-poster/app/{agent,tools}.py`; webapp `/home/user/gammarips-webapp` (`app/page.tsx`, `todays-pick-card.tsx`, `app/scorecard/page.tsx`, `lib/firebase-admin.ts`, `pro-lock.tsx`, Firestore rules). Note: webapp `/signals` list + `/signals/[ticker]` are currently **free/ungated (the SEO haystack)** — gating them as the paid feed would cost that SEO surface; resolve the free-vs-paid line before any wire-up.
- **Memory:** `project_gigo_pool_composite_negative` (this finding), `project_monetization_pivot_decouple_pick`, `project_agent_mode_mcp_byoa`.
