# 2026-06-25 — Live-OI liquidity floor for the pick-time pool

**Status:** IMPLEMENTED in the working tree, **NOT deployed**. `gammarips-review` returned **SHIP-WITH-CONDITIONS** (C1–C5, baked in below). A **mandatory re-review** of the leakage extraction (`_fetch_live_oi`) + the C3 assert is required before any deploy. The G-Stack ceremony is owner-waivable; the leakage audit is not.

## Problem
The tournament keeps picking **illiquid contracts** — e.g. **BBWI on 2026-06-25: live OI ~617, today's option volume 2**. The enriched row carries a **one-day-stale scan-time OI snapshot**; by the 10:00 ET entry the contract that earned the UOA score can be effectively dead. The 2026-06-04 bracket-tournament deliberately stripped OI from the judge because the *scan-time* OI was a stale snapshot — but stripping it left the engine with **no liquidity signal at all** at pick time, so the tournament selects names that cannot be filled / exited cleanly.

## Decision
Add a **deterministic, fail-soft live-OI liquidity floor** in `signal-notifier`, run on the edge-capped strict pool **just before** the `/rank` tournament call. At ~09:45 ET pick time we **re-fetch live OI** per candidate from Polygon's option snapshot, **drop dead contracts below `OI_FLOOR`**, fail-soft to keep the tournament from starving, and **soft-tilt** survivors by fillability.

### Threshold: fill-rate, NOT PnL
`OI_FLOOR = 200`. The backtest set the floor on **fill-rate tradeability** — there is an ~OI=200 cliff below which contracts cannot be reliably entered/exited. We did **NOT** floor on PnL: thin contracts show a spurious **"0% PnL" stale-print artifact** (the last print never moves), so PnL is not a usable signal for this gate. This is a tradeability floor, full stop.

### Explicit reversal of the 2026-06-04 OI-strip — and why it's now safe
The 2026-06-04 decision blocked `recommended_oi` (and volume) from the judge because they were **stale scan-time snapshots**. We are re-introducing OI to the pipeline, but the objection does not apply because the new value is:

1. **FRESH** — re-fetched from Polygon `v3/snapshot/options/{underlying}/{contract}` at pick time (~09:45 ET), not the prior-evening scan snapshot.
2. **OI-ONLY** — the snapshot also returns `implied_volatility`, `greeks` (delta/gamma/theta/vega), `day` OHLC, `last_trade`, and `last_quote`. **All of those are entry-day-LIVE (10:00+ window) and would leak the future.** They are **discarded at fetch time** (`_fetch_live_oi` extracts only `open_interest` and `day.volume`) and asserted absent again before the `/rank` payload. Only `live_oi` is surfaced to the judge. `recommended_oi` stays blocked in `STALE_FIELDS_BLOCKLIST`; `live_oi` replaces it as the one permitted fresh OI field.

`day.volume` (→ `today_volume`, carried internally as `_today_volume`) is used **only** for the floor/tilt computation and is **popped before** the payload is built — it never reaches the LLM.

## Mechanics (`signal-notifier/main.py`)
- **`_fetch_live_oi(underlying, contract)`** — one Polygon snapshot call, 8s timeout, single attempt, fail-soft (never raises). Mirrors the `compute_active_days_20d` pattern. Returns `(live_oi, today_volume, status)`; extracts ONLY `results.open_interest` and `results.day.volume`, lets the rest of the response go out of scope.
- **`_refresh_live_oi_batch(df)`** — parallelizes the ≤50 calls over a `ThreadPoolExecutor` (default 16 workers). Per-future try/except: a timeout/error = `live_oi=None` for that row → **keep it with frozen OI, never drop** (C4). Attaches `live_oi` + `_today_volume` columns.
- **`_liquidity_refresh_and_rank(candidates_df)`** — the orchestrator:
  1. refresh live OI,
  2. drop candidates with effective OI `< OI_FLOOR` (effective = live where present, else frozen `recommended_oi`),
  3. **fail-soft floor:** if fewer than `TOURNEY_MIN` (8) survive, restore the top-effective-OI names up to `TOURNEY_MIN` so the tournament never starves to zero (no spurious `no_candidates_passed_gates`),
  4. **soft tilt:** order survivors by effective OI desc.
  Wrapped in a top-level try/except that returns the **input df unchanged** on any error.

Wired in `run_notifier` immediately after `_edge_rank_and_cap`, before `call_signal_ranker`. FALLBACK path (which bypasses the tournament via `df.iloc[0]`) is **unaffected**.

## Conditions baked in (gammarips-review SHIP-WITH-CONDITIONS)
- **C1 (leakage):** `_fetch_live_oi` extracts ONLY `open_interest` + `day.volume`. IV/greeks/day-OHLC/last-trade/last-quote are never read. `_today_volume` is internal and popped before `/rank`.
- **C3 (leakage guard assert):** in `call_signal_ranker`, immediately before the payload is serialized:
  ```python
  _FORBIDDEN_LIVE_KEYS = {
      "live_iv","live_delta","live_gamma","live_theta","live_vega",
      "last_trade","last_trade_price","last_quote",
      "day_close","day_open","day_high","day_low","day_vwap",
  }
  for cand in candidates:
      leaked = _FORBIDDEN_LIVE_KEYS & set(cand.keys())
      assert not leaked, f"entry-day-live leak into /rank payload: {leaked}"
  ```
  Defense-in-depth: the same keys (plus `_today_volume`/`today_volume`) are added to `signal-judge/app/agent.py` `STALE_FIELDS_BLOCKLIST`. `live_oi` is intentionally NOT blocked — it is the one new permitted key.
- **C4 (total fail-soft):** any exception in the refresh returns the input df unchanged (edge-rank order, frozen OI), never empty, never raises into the live pick. Per-candidate fetch failures keep the candidate with frozen OI.
- **C5 (ledger landmine):** `live_oi`/`today_volume` are **NOT** added to any `forward_paper_ledger` record dict. The trader builds its ledger record from a fresh BQ query of `overnight_signals_enriched` (not from `todays_pick`), and the load job uses `ALLOW_FIELD_ADDITION` **without** `autodetect=True` (`forward-paper-trader/main.py:976-984`) — a new field 500s the run after the pre-write DELETE. `live_oi` lives only in the candidate dict, the `/rank` payload, and (optionally) the schemaless `todays_pick` Firestore doc.

### Worst-case wall-clock
With up to ~50 candidates fanned across the default 16-worker pool at 8s/timeout each: **ceil(50/16) × 8s ≈ 24s** plus negligible HTTP setup. Absolute worst case (workers=1): ~50 × 8s = 400s, still inside the notifier's 540s request timeout. At the default 16 workers it lands in ~half a minute — well before the trader cron reads `todays_pick` at/after 10:00 ET. The ~09:45 cron + ~24s refresh + tournament finalize completes by ~09:50; the trader entry-sim reads the doc on a later cron.

## C2 — cron co-move (PREPARE ONLY; commands NOT run)
The notifier+tournament cron must move **07:30 → ~09:45 ET** so live OI is fetched at pick time. That requires co-moving the x-poster **`signal` post** (it reads `todays_pick`) to fire **AFTER** the ~09:50 finalize.

**Live job names (verified 2026-06-25, `us-central1`):**
- Notifier: **`signal-notifier-job`** — currently `30 7 * * 1-5` (07:30 ET).
- Signal post: **`x-poster-signal-0800`** — currently `0 8 * * 1-5` (08:00 ET), body `{"post_type":"signal"}`. (Name still encodes the old 08:00 slot; the `DESIGN_SPEC` "09:05" entry was stale text, not the live schedule. Rename optional.)

**Deploy checklist (run ONLY after the mandatory re-review + deploy sign-off):**
```bash
# 1) Move the notifier+tournament cron 07:30 -> 09:45 ET
gcloud scheduler jobs update http signal-notifier-job \
  --project=profitscout-fida8 --location=us-central1 \
  --schedule="45 9 * * 1-5" --time-zone="America/New_York"

# 2) Move the x-poster `signal` post 08:00 -> 09:55 ET (AFTER the ~09:50 finalize)
gcloud scheduler jobs update http x-poster-signal-0800 \
  --project=profitscout-fida8 --location=us-central1 \
  --schedule="55 9 * * 1-5" --time-zone="America/New_York"
```
> Do NOT run these until the leakage re-review passes AND deploy is signed off. Until then the notifier stays at 07:30 and the live-OI refresh runs against the prior-evening snapshot (still correct — it just re-confirms frozen OI rather than catching the overnight-to-morning OI build; the floor and fail-soft behave identically).

## Env kill-switches (all reversible, no code change)
| Env | Default | Effect |
|---|---|---|
| `OI_FLOOR` | `200` | drop contracts with effective OI below this (fill cliff) |
| `TOURNEY_MIN` | `8` | fail-soft floor: never starve the tournament below this many |
| `LIQUIDITY_TILT` | `true` | kill switch — `false` = bit-identical pre-2026-06-25 behavior (no re-fetch, no drop, no tilt) |
| `LIVE_OI_FETCH_TIMEOUT_S` | `8` | per-candidate snapshot timeout |
| `LIVE_OI_MAX_WORKERS` | `16` | refresh parallelism |

Documented in `signal-notifier/deploy.sh`. **`deploy.sh` was NOT run.**

## Files touched
- `signal-notifier/main.py` — env knobs + `_FORBIDDEN_LIVE_KEYS`; `_fetch_live_oi`, `_refresh_live_oi_batch`, `_effective_oi`, `_liquidity_refresh_and_rank`; `_today_volume` pop + C3 assert in `call_signal_ranker`; wiring in `run_notifier`; `live_oi` into the `todays_pick` doc.
- `signal-judge/app/agent.py` — forbidden live keys added to `STALE_FIELDS_BLOCKLIST` (defense-in-depth; `live_oi` permitted).
- `signal-notifier/deploy.sh` — env-knob docs + defaults (not run).
- `x-poster/DESIGN_SPEC.md` — `signal` post cadence 09:05 → 09:55 ET + co-move note.
- `docs/TRADING-STRATEGY.md` — policy update.

## Follow-ups
- **Mandatory:** `gammarips-review` re-audit of `_fetch_live_oi` (OI-only extraction) + the C3 assert before deploy.
- Watch the first live runs: `Live-OI refresh` + `Live-OI floor` log lines should show the drop count and survivors; confirm fail-soft never fires on a healthy day.
- Consider renaming `x-poster-signal-0800` → `x-poster-signal-0955` after the cron move (cosmetic).
