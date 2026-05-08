# 2026-05-06 — Earnings-overlap exclusion at signal-notifier

## Decision
Add a hard exclusion at `signal-notifier`: skip any candidate ticker whose scheduled earnings date falls inside `[scan_date, entry_day + 2 trading days]` (i.e., V5.3's full 3-trading-day hold from 10:00 ET entry to 15:50 ET exit, plus the scan_date to catch AMC-scan_date contamination). Implementation pulls top-10 ranked candidates and walks the list, taking the first non-earnings ticker. If all 10 are earnings-overlap, skip the day.

The window starts at `scan_date`, not `entry_day`, after `gammarips-review` flagged a scope gap: a ticker reporting AMC on `scan_date` generates its V/OI surge under known-imminent-earnings positioning, then the print fires before our 10:00 ET entry_day open. The CDW failure mode (BMO on entry_day) is caught by `entry_day`; AMC on scan_date is the symmetric case and is now also caught.

## Trigger
2026-05-06 V5.3 picked CDW BULL (`O:CDW260515C00125000`, 8.6% OTM, 9 DTE) on top of all V5.3 gates clearing (V/OI 92.16, VIX 18.29 ≤ VIX3M 21.05, score 8). CDW reported BMO 2026-05-06: revenue beat (+9.2% YoY, +3.8% vs. consensus) but adjusted op income missed by 18.1%; stock gapped −5.5% to $129.27 by the open. Trade was dead on arrival — the V/OI 92x was earnings-event positioning, not informed flow, and V5.3 had no event-calendar awareness anywhere in the stack (`enrichment-trigger`, `signal-notifier`, `forward-paper-trader`).

## Why this is a literature-driven rule, not a backtest
This is an **exclusion filter** — kicking out a known-broken setup — not a **selection filter** that picks winners from our cohort. Different evidentiary bar: theory-driven exclusion does not require labeled_v1 backtesting (which would be regime-confounded anyway). Same epistemic class as the existing `VIX ≤ VIX3M` backwardation gate.

The literature has settled this at scale we cannot match on a 1,563-row cohort:

- **De Silva, Smith & So (2026), *Review of Finance*** — "Losing is Optional." Retail-flagged long-options trades through earnings lose **5–9% on average per event, 10–14% on high-vol names**. Sample population maps directly onto our setup (large-cap, OTM, short-dated, held through the print).
- **Cao & Han (2013), *JFE*** — long delta-hedged options on high-idiosyncratic-vol names earn ~−1.4%/month cross-sectionally; earnings concentrate this exposure into a binary event. Already in our evidence base as the volatility-idiosyncratic trap (`UNDERLYING_VS_OPTIONS_V1.md`).
- **Goyal & Saretto (2009), *JFE*** — vol risk premium structure: long premium has structurally negative cross-sectional expected returns. Earnings concentrate the VRP into a single discontinuous event.
- **Dubinsky & Johannes (2006, Columbia WP)** — IV crush magnitudes: front-month IV climbs to ~70% pre-EA on liquid names, collapses to ~20% post-print (30–60% IV decline). OTM short-dated options take a worse hit because they're nearly pure vega.
- **Boundary conditions documented but do NOT fit our setup:** Gao, Xing & Zhang (2018, JFQA) found pre-EA straddles closed *before* the print were marginally positive in small-cap / illiquid names; Khan & Khan (SSRN 4832160) show that edge has compressed to negative post-2011 even in the original cohort. Holding *through* the print has no positive-EV subset documented anywhere in the literature.

Our V5.3 trade structure (large-cap, OTM 5–15%, ~9 DTE, held through the print) sits in the worst quadrant on every axis the literature studies: liquid (no transaction-cost edge), OTM (max vega / min delta protection), short-dated (max theta), through-the-event (full crush).

## Implementation
- **Calendar source:** FMP `/v3/earning_calendar?from=YYYY-MM-DD&to=YYYY-MM-DD&apikey=...`. FMP_API_KEY mounted as a Secret Manager binding via `signal-notifier/deploy.sh`.
- **Window:** `[scan_date, entry_day + 2 trading days]` inclusive. Covers the V5.3 hold plus scan_date to catch AMC-scan_date contamination.
- **SQL change:** `LIMIT 1` → `LIMIT 10`. The earnings filter walks the ranked list and selects the first non-overlapping ticker.
- **Fail-closed behaviors (new `skip_reason` values written to `todays_pick`):**
  - `earnings_calendar_unavailable` — FMP fetch failed, `FMP_API_KEY` missing, OR FMP returned a non-list payload (quota-exhausted free-tier: HTTP 200 + `{"Error Message": "..."}` body). Cannot distinguish "no earnings" from "API down," so we skip.
  - `earnings_overlap_all_candidates` — all 10 top candidates report in the window. Rare but possible during peak earnings season.
- **No backfill, no historical relabeling.** This is a forward-only change. Existing ledger rows stay tagged `V5_3_TARGET_80`; the new behavior takes effect on the next signal-notifier run after deploy.

## Why the existing ranker is not changed
The 5-key `ORDER BY` is preserved verbatim. The earnings filter is a post-rank exclusion, not a re-rank. Rank-1 still goes to email when it has no earnings overlap. The decision to fall through to rank-2..10 only fires when rank-1 is contaminated.

This means rank-2 (and lower) signals occasionally reach production. That is acceptable: every candidate already passes the V5.3 quality minimum gates (`V/OI > 2`, moneyness 5–15% OTM, OI ≥ 20, vol ≥ 100, spread ≤ 10%, score ≥ 1, UOA $ > $500K), so it is a tradeable signal by V5.3 standards. The literature on rank-stratified UOA edge (Pan-Poteshman, Johnson-So) shows decile spreads, not all-or-nothing alpha at rank-1.

## Counterfactual on CDW
If the earnings filter had been live on 2026-05-06: FMP would have returned CDW in the calendar for entry_day=2026-05-06, the engine would have skipped CDW and walked to rank-2. CDW's loss never enters the ledger.

## Validation posture
This is a hard rule, not a hypothesis. Do not treat post-deploy ledger results as "filter validation evidence." The rule's evidence base is the literature; the ledger only validates that the *implementation* is correct (the right tickers get excluded).

Watch for:
- Skip-day rate spike during earnings-heavy weeks (expected; not a bug).
- FMP API reliability — if `earnings_calendar_unavailable` fires more than ~once a month, escalate to a fallback source (Polygon, Finnhub) or pre-cache the calendar daily.
- Drift between FMP's reported earnings dates and actual reporting dates — companies occasionally shift by a day. Acceptable as long as the skip is biased toward over-exclusion (false positive = lose a trade; false negative = take a contaminated trade).

## Review sign-off
`gammarips-review` audit required before deploy per CLAUDE.md ground rule (`forward-paper-trader` and `signal-notifier` production-touching changes). This change does NOT touch the trader; it modifies signal-notifier's gate stack only.

## Files changed
- `signal-notifier/main.py` — added `FMP_API_KEY`, `get_hold_window_end()`, `fetch_earnings_calendar()`, restructured `run_notifier()` to walk top-10 with earnings filter; added two `skip_reason` values; updated module docstring.
- `signal-notifier/deploy.sh` — added `FMP_API_KEY` to `--set-secrets`.
- `CHEAT-SHEET.md` — gate #9 added.
- `docs/TRADING-STRATEGY.md` — notifier filter stack updated; `skip_reason` enum extended.
- `docs/research_reports/INTELLIGENCE_BRIEF.md` — 2026-05-06 update entry written separately (literature-anchored exclusion adopted).
