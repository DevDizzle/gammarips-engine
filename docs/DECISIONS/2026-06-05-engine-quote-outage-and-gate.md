# 2026-06-05 — Engine quote-outage fix + enrichment gate recalibration (score≥4, spread gate retired)

**Status:** FIXED + DEPLOYED 2026-06-05 (the outage was a live production stop — engine produced 0 picks/day from scan_date 2026-06-04). The accompanying gate-discovery study is a PROPOSAL pending `gammarips-review` + the N≥15 live-cohort lock; only the `overnight_score >= 4` floor shipped. Owner-directed; G-Stack ceremony waived per the owner; leakage is the only non-negotiable.

## A. The outage + fix

### Root cause: this Polygon plan serves NO options NBBO quotes
Confirmed live: the v3 options-chain snapshot on our Polygon tier returns no `last_quote` object — only `details`, `day` OHLC, `open_interest`, `volume`, and greeks/IV (when in-session). **Bid/ask are ALWAYS `None`.** There is no quote feed to price a spread from. (This is the same tier limit that returns 403 on `/v3/trades` — see the H20 sweep-feasibility probe in `INTELLIGENCE_BRIEF.md`.)

### How the 2026-06-04 bug-fix exposed it
The 2026-06-04 pipeline bug-hunt (`6b2a6dc`, `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md` #1) correctly removed `polygon_client`'s bogus `day.low`/`day.high` bid/ask synthesis — that synthesis had manufactured fake/exactly-0% spreads on ~43% of picks (the OKTA ghost). **But** `_best_contract` still hard-rejected every contract on `bid <= 0 or ask <= 0`. With quotes now legitimately `None` (no synthesis, and no real quote feed on this plan), that guard rejected EVERY contract for EVERY ticker:

- `_best_contract` returned `None` for all tickers → all `recommended_*` fields NULL → 0 enriched rows → **0 picks/day from scan_date 2026-06-04 onward.**

**Scope note — `overnight_score` / the webapp 8/10 was UNAFFECTED.** The score is pure flow, computed pre-enrichment, spread-independent. Only contract *selection* broke. The haystack the webapp shows was intact; the curated pick went dark.

### The fix (deployed 2026-06-05)
Two files (both owned by another agent — this decision note documents the change, it did not author the code):

1. **`_best_contract` (scanner contract selection):** when there is no quote, price the contract off **last-trade / day-close** and leave `spread_pct` **NULL** (no synthesis — the day-low/high lesson from #1 stands). OI-primary scoring still ranks tradeability across strikes. No-quote strikes are no longer dropped — they're the only strikes that exist on this plan.
2. **Enrichment gate (`enrichment-trigger`):**
   - **Dropped the `recommended_spread_pct IS NOT NULL` fail-closed.** NULL spread now passes (it's the permanent normal state on this plan). A genuinely-wide spread is dropped only if a real quote ever appears.
   - **Raised the score floor `>= 1` → `>= 4`.** Drops the proven-bad `score <= 3` dregs. This is a **floor, NOT a ceiling** — score EV inverts at `>= 7` (see §B), so we do not cap the top; we feed the tournament a broad-but-not-garbage pool and let it discriminate.
   - **Kept:** UOA > $500K, ALL directions.

**Spread is no longer a selection gate anywhere.** It can't be one on this plan. The only path to a real spread signal is a **Polygon plan upgrade** to a tier with NBBO quotes — a spend + vendor decision, deferred pending an owner cost decision (parked alongside the H20 trades-feed upgrade).

## B. The option-PnL gate-discovery result (kept all directions; score≥4 floor only)

**Workflow `wf_16b5c00d-347` (2026-06-05).** Multi-agent fan-out over 8 feature families + walk-forward / day-block-bootstrap validation on the REAL option-PnL bracket-replay label (`analysis_option_pnl.parquet`, **N=1375 FILLED**, entry_day 2026-04-13…05-29, 33 days). Full-pool baseline mean `realized_ret = -0.0044` (win 0.413).

### Headline
The **only** robust, leakage-clean, breadth-viable lever is **DIRECTION**:
- **bullish-only:** EV **+0.0411**, win 0.470, ~26 picks/day
- **bearish:** EV **-0.0771**

Everything else (trend overlays, vix3m, moneyness, catalyst, active-strikes) is noise or redundant-with-direction.

### DECISION (owner, 2026-06-05): do NOT bake in bullish-only
The bearish penalty is almost certainly **regime-conditional** — one 2026-Q1/Q2 war-chop window, and `vix3m_at_enrich` had near-zero variance here (19.45–21.51), so regime-dependence is structurally **untestable** on this data. Keep **ALL directions**. Shelve "exclude bearish" as an **N≥15 live-cohort revisit**. The deployed gate change is the **`score >= 4` floor only** — V6-faithful: feed the tournament a broad pool, let it discriminate. (Consistent with the standing direction-EV-asymmetry memory: don't frame bearish as broken; it reflects the regime.)

### 5 NEW DEAD-ENDS (recorded in `FINDINGS_LEDGER.md`)
1. **Trend overlays** (`above_sma_50/200`, `MACD>0`, `ema_21`) as standalone EV gates — redundant with direction; the ~+0.02 increment is day-block-bootstrap noise and goes negative in the recent third.
2. **`vix3m_at_enrich <= 21.12`** as a regime conditioner — DEAD on this data (no variance; it's a period selector, edge is 100% from kept null-vix rows in the first 5 days).
3. **`moneyness_pct > 5%` OTM keep-null** — null/recency artifact (strip the null trick → below bullish-only; walk-forward inverts).
4. **Catalyst-type exclusion** — selection artifact; CI overlaps baseline; picked from 18-category dispersion (multiple comparisons).
5. **`call+put_active_strikes >= 10`** — clean and NOT a recency artifact, but the increment over bullish-only is within day-block noise — best used as a tournament **TIE-BREAKER**, not a gate.

### Method caveats
Thin (33 days, single regime); 76% of exits are TIMEOUT (3-day option drift dominates, the bracket rarely fires); mild liquidity-survivorship bias (INVALID_LIQUIDITY / CACHE_EMPTY dropped). This is a PROPOSAL pending `gammarips-review` + the N≥15 lock — only the `score >= 4` floor was deployed.

## New enrichment gate spec (as deployed 2026-06-05)
`enrichment-trigger` "enriched" definition:
- `overnight_score >= 4` (floor; EV inverts at `>= 7` — do not add a ceiling)
- `directional UOA > $500K`
- **ALL directions** (bullish + bearish)
- **Spread gate RETIRED** — this Polygon plan serves no options quotes; spread is permanently NULL; `_best_contract` prices off last-trade / day-close.

Everything else is unchanged: the V6 bracket tournament over the full pool, the two `signal-notifier` safety rails (no-earnings-in-hold + `VIX ≤ VIX3M` fail-closed), and the trader mechanics (entry 10:00 ET, −60% stop, +80% target, 3-day hold, 15:50 ET exit).

## Reversibility
- Score floor: one-line revert (`>= 4` → `>= 1`).
- Spread gate / `_best_contract`: revert the two-file diff; but the underlying constraint (no quotes on this plan) means a hard `bid/ask>0` reject re-darkens the engine — do not reinstate without a plan upgrade.

## Open / next
- **Re-validate the direction tilt at N≥15** live closes (the bullish-only +0.0411 vs bearish -0.0771; the bearish penalty's regime-conditionality is the open question).
- **Consider a Polygon quote-plan upgrade** — the only path to a real spread signal (and the H20 trades-feed sweep classification). Spend decision, owner-owned.
- Watch the `has_contract` / enriched-pool size after tonight's scan now that no-quote strikes are priced off last-trade.
