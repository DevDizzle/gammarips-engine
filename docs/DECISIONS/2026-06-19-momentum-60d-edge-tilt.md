# 2026-06-19 — 60-day momentum as a soft edge-rank tilt (PROPOSAL → implement, review-gated)

## Finding
Tested underlying price momentum on REAL split/dividend-adjusted daily bars (new
686-ticker cache `backtesting_and_research/cache/poly_daily_underlying/`, Dec 2024–
Jun 2026) against the frozen 1,375-trade full-pool **option-PnL** set. Evaluated on
option PnL (never underlying), leakage-guarded (trailing window anchored ≤ scan_date),
bootstrap 95% CIs, walk-forward split.

**Underlying momentum is a REAL, additive selection lever for buying calls** — the
owner's instinct ("stocks that are ripping are the options to trade") is confirmed.
But the tradeable horizon is the **1–3 month rip, NOT literal year-over-year:**

- Bullish baseline: +4.11% EV / 47.0% win.
- **60-day top-quintile (`mom_60 ≥ +0.35`): ~+11.4% EV / 55.9% win**; marginal lift
  over the bullish pool +8.4pp, CI clears zero. Win-rate effect, broad-based (not tails).
- Term structure: pure momentum at every horizon {20,60,126,189,252}, **no reversal**.
- Walk-forward (split 2026-05-04) is the discriminator: 60-day Q5 held in **both**
  halves (+16.9% → +7.5%, both clear zero). Literal **YoY (252d ≥ +50%) clears zero
  in-sample (+5.45%) but its marginal lift CI does NOT clear zero and it collapses
  out-of-sample (H2 −0.22%)** — so we anchor the rule on 60 days, not 252.
- Not redundant with `overnight_score` (corr +0.29; high-mom beats low within every
  score stratum).

## Decision
Add `mom_60` as an **additional SOFT pre-rank tilt** in `enrichment-trigger`
`_edge_select_top_n`, alongside the existing confirmed delta-band lever — favoring
BULLISH names with `mom_60 ≥ +0.35` into the top-`ENRICH_TOP_N` pool that seeds the
tournament. **NOT a hard gate** (no name is excluded for low momentum). This improves
the single live pick; it is not (yet) a separate sleeve.

- `mom_60 = adj_close(last session ≤ scan_date) / adj_close(60 trading sessions earlier) − 1`.
- **Leakage rule (non-negotiable):** anchor on the last close ON OR BEFORE scan_date;
  never read an entry-day-or-later bar (entry is 10:00 the next trading day).
- Computed for the full pre-cap bullish pool via Polygon **grouped-daily adjusted**
  closes (2 calls/day, not 344 per-ticker calls). Names without ≥60 sessions of
  history (recent IPOs) get a **neutral** tilt, not exclusion.
- Env-toggleable (default on): `MOMENTUM_TILT`, `MOM_LOOKBACK_DAYS=60`, `MOM_THRESHOLD=0.35`.

## Caveats / governance
- **7-week in-sample outcome window.** Walk-forward-stable is encouraging, not proven.
  Carries the **N≥15 live-cohort revisit lock** — re-evaluate the tilt's live option-PnL
  contribution at 15 closed trades before treating it as settled.
- Research finding, leakage-audited; **`gammarips-review` PASS required before deploy**
  (this changes a live strategy gate).
- Source of truth: this note + `docs/TRADING-STRATEGY.md` + `enrichment-trigger/main.py`
  `_edge_select_top_n`. Evidence: `[[project_momentum_60d_lever]]` memory; the falsified
  "ride recent winners" variant is in `docs/DECISIONS` history / `[[project_exploit_winners_falsified]]`.

## Implementation status (2026-06-19)
- **DEPLOYED 2026-06-19 — `gammarips-review` PASS — rev `enrichment-trigger-00045-f89` (100% traffic).** First momentum-tilted pick: Mon 2026-06-22 (05:30 ET enrichment → 07:30 ET pick). N≥15 live-cohort revisit lock in force. Branch `gate-changes-2026-06-02`.
- `enrichment-trigger/main.py`: added `MOMENTUM_TILT` / `MOM_LOOKBACK_DAYS` / `MOM_THRESHOLD`
  config; `_resolve_momentum_dates` (NYSE-calendar anchor + 60-session lookback, both
  asserted ≤ scan_date), `_fetch_grouped_daily_closes` (1 grouped-daily ADJUSTED call →
  {ticker: close}), `_compute_momentum_map` (2 calls, per-run module cache `_MOM_CACHE`);
  `_edge_select_top_n` gained `scan_date`/`polygon_key` kwargs and the soft +1.25 momentum
  bump + `mom_60`-desc tie-break, with per-pick audit logging and a fail-soft delta-only path.
- `enrichment-trigger/requirements.txt`: added `pandas-market-calendars==4.6.1`.
- mom_60 is LOGGED only (not persisted to `overnight_signals_enriched`) — no schema change,
  no load-job risk.
