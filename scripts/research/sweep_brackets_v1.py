"""Bracket / hold sweep over the cached signal bars.

Reads `signals_labeled_v1` for signal metadata and `/tmp/signal_bars_v1.pkl`
for the cached minute bars. For every combination of:

    entry_time   ∈ {15:00, 15:30, 15:45, 15:55}
    target_pct   ∈ {0.25, 0.50, 0.75, 1.00, 1.50, 2.00, none (let it ride)}
    stop_pct     ∈ {0.20, 0.35, 0.50, 0.75, none (no stop)}
    hold_days    ∈ {2, 3, 5, 7, 10, 15}

simulates every signal under V3-style mechanics with the variant's parameters
and reports per-variant aggregates. The chronological holdout (older 70% of
scan_dates → train, newer 30% → OOS) is the headline metric.

Production-trader exit logic is preserved exactly:
  - target/stop touched in the same bar → STOP wins
  - timeout exit uses last bar at-or-before timeout_ts as the exit price
  - +2% slippage on entry, target/stop are filled at exact target/stop price

Output: writes `/tmp/sweep_results_v1.parquet` with one row per variant +
  prints summary tables for the top variants.

Usage:
    python scripts/research/sweep_brackets_v1.py
"""

from __future__ import annotations

import math
import pickle
import sys
import time
from dataclasses import dataclass
from datetime import datetime, date
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "forward-paper-trader"))
import main as trader  # noqa: E402

PROJECT_ID = "profitscout-fida8"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIM_VERSION = "V3_MECHANICS_2026_04_07"
CACHE_PATH = Path("/tmp/signal_bars_v1.pkl")
RESULTS_PATH = Path("/tmp/sweep_results_v1.parquet")
SIGNAL_DETAIL_PATH = Path("/tmp/sweep_signal_detail_v1.pkl")

est = pytz.timezone("America/New_York")
SLIPPAGE = 1.02

ENTRY_TIMES = ["15:00", "15:30", "15:45", "15:55"]
TARGET_PCTS = [0.25, 0.50, 0.75, 1.00, 1.50, 2.00, None]  # None = no target
STOP_PCTS   = [0.20, 0.35, 0.50, 0.75, None]              # None = no stop
HOLD_DAYS   = [2, 3, 5, 7, 10, 15]


# ----------------------------------------------------------------------------
# Per-signal precomputation
# ----------------------------------------------------------------------------

@dataclass
class SignalPrecomp:
    """Vectorized representation of one signal's bars, ready for fast bracket sims."""
    ticker: str
    scan_date: date
    entry_day: date
    expiration: date
    premium_score: int
    direction: str
    recommended_volume: int
    recommended_oi: int
    recommended_spread_pct: float
    recommended_dte: int
    recommended_mid_price: float
    # Per-entry-time data: dict[entry_time_str] -> tuple of arrays
    by_entry: dict
    # Per-hold-days timeout timestamps (ms): dict[int] -> int
    timeout_ts_by_hold: dict


def precompute_signal(bars: list, meta: dict) -> SignalPrecomp | None:
    """Build the per-signal vectorized data for every entry time."""
    if not bars:
        return None
    entry_day = meta["entry_day"]

    # Bars are in ms timestamps from Polygon. Filter to entry_day's bars only
    # for the entry-bar lookup; keep all bars for the post-entry walk.
    entry_day_bars = [
        b for b in bars
        if datetime.fromtimestamp(b["t"] / 1000, tz=est).date() == entry_day
    ]
    if not entry_day_bars:
        return None

    # Build a ticker→index map once for O(1) lookups when slicing post-entry bars.
    bars_ts = [b["t"] for b in bars]
    by_entry: dict = {}
    for et_str in ENTRY_TIMES:
        et_dt = datetime.combine(entry_day, datetime.strptime(et_str, "%H:%M").time())
        et_ms = int(est.localize(et_dt).timestamp() * 1000)

        # Same fallback logic as the production trader.
        after_or_at = [b for b in entry_day_bars if b["t"] >= et_ms]
        entry_bar = None
        if after_or_at:
            entry_bar = after_or_at[0]
        else:
            before = [b for b in entry_day_bars if b["t"] < et_ms]
            entry_bar = before[-1] if before else None
        if not entry_bar or entry_bar.get("v", 0) == 0:
            by_entry[et_str] = None
            continue

        # O(log n) index lookup via bisect on the precomputed ts list.
        import bisect
        entry_idx = bisect.bisect_left(bars_ts, entry_bar["t"])
        post = bars[entry_idx + 1:]
        if not post:
            by_entry[et_str] = None
            continue

        ts = np.array([b["t"] for b in post], dtype=np.int64)
        h = np.array([b["h"] for b in post], dtype=np.float64)
        l = np.array([b["l"] for b in post], dtype=np.float64)
        c = np.array([b["c"] for b in post], dtype=np.float64)
        cum_high = np.maximum.accumulate(h)
        cum_low = np.minimum.accumulate(l)
        base_entry = entry_bar["c"] * SLIPPAGE
        by_entry[et_str] = {
            "entry_price": base_entry,
            "entry_ts": entry_bar["t"],
            "ts": ts,
            "cum_high": cum_high,
            "cum_low_neg": -cum_low,  # for searchsorted on ascending
            "close": c,
        }

    # Precompute timeout_ts_ms for each hold_days value once per signal.
    timeout_ts_by_hold: dict = {}
    expiration = meta["expiration"]
    for hd in HOLD_DAYS:
        td = trader.get_nth_next_trading_day(entry_day, hd)
        if expiration and td and td > expiration:
            td = expiration
        if td is None:
            td = entry_day
        td_dt = datetime.combine(td, datetime.strptime("15:55", "%H:%M").time())
        timeout_ts_by_hold[hd] = int(est.localize(td_dt).timestamp() * 1000)

    return SignalPrecomp(
        ticker=meta["ticker"],
        scan_date=meta["scan_date"],
        entry_day=meta["entry_day"],
        expiration=meta["expiration"],
        premium_score=meta["premium_score"],
        direction=meta["direction"],
        recommended_volume=meta["recommended_volume"],
        recommended_oi=meta["recommended_oi"],
        recommended_spread_pct=meta["recommended_spread_pct"],
        recommended_dte=meta["recommended_dte"],
        recommended_mid_price=meta["recommended_mid_price"],
        by_entry=by_entry,
        timeout_ts_by_hold=timeout_ts_by_hold,
    )


# ----------------------------------------------------------------------------
# Variant simulation
# ----------------------------------------------------------------------------

INF = float("inf")


def simulate_one(p: SignalPrecomp, entry_time: str,
                 target_pct: float | None, stop_pct: float | None,
                 hold_days: int) -> dict | None:
    """Run one (signal, variant) combination. Returns outcome dict or None
    if the signal has no usable entry under this entry_time."""
    e = p.by_entry.get(entry_time)
    if e is None:
        return None
    base = e["entry_price"]
    ts = e["ts"]
    cum_high = e["cum_high"]
    cum_low_neg = e["cum_low_neg"]
    close = e["close"]

    if len(ts) == 0:
        return {"exit_reason": "TIMEOUT", "entry_price": base, "exit_price": base,
                "realized_return_pct": 0.0, "bars_to_exit": 0}

    # Precomputed timeout boundary (no per-call calendar work).
    timeout_ts_ms = p.timeout_ts_by_hold[hold_days]

    # Find first bar idx where each exit type triggers.
    if target_pct is None:
        target_idx = len(ts)  # never
    else:
        target_price = base * (1 + target_pct)
        target_idx = int(np.searchsorted(cum_high, target_price, side="left"))

    if stop_pct is None:
        stop_idx = len(ts)
    else:
        stop_price = base * (1 - stop_pct)
        stop_idx = int(np.searchsorted(cum_low_neg, -stop_price, side="left"))

    timeout_idx = int(np.searchsorted(ts, timeout_ts_ms, side="left"))

    first_exit = min(target_idx, stop_idx, timeout_idx, len(ts))

    if first_exit == len(ts):
        # Ran off the end of cached bars before any exit triggered (e.g.,
        # contract stopped printing or expired). Use last available close.
        exit_price = close[-1]
        exit_reason = "TIMEOUT"
    elif first_exit == target_idx and first_exit == stop_idx:
        # Both touched in same bar — production rule: STOP wins.
        exit_price = base * (1 - stop_pct) if stop_pct is not None else close[first_exit]
        exit_reason = "STOP"
    elif first_exit == target_idx:
        exit_price = base * (1 + target_pct)
        exit_reason = "TARGET"
    elif first_exit == stop_idx:
        exit_price = base * (1 - stop_pct)
        exit_reason = "STOP"
    else:
        # TIMEOUT — exit at last in-window bar.
        # last_in_window = bar at index first_exit - 1 if first_exit > 0
        idx = max(0, first_exit - 1)
        exit_price = close[idx]
        exit_reason = "TIMEOUT"

    return {
        "exit_reason": exit_reason,
        "entry_price": base,
        "exit_price": float(exit_price),
        "realized_return_pct": float((exit_price - base) / base),
        "bars_to_exit": first_exit if first_exit < len(ts) else len(ts),
    }


# ----------------------------------------------------------------------------
# Main sweep
# ----------------------------------------------------------------------------

def load_population(client: bigquery.Client) -> dict:
    """Return a dict keyed by (ticker, scan_iso) of metadata rows."""
    sql = f"""
    SELECT
        ticker, scan_date, recommended_strike, recommended_expiration,
        direction, premium_score, recommended_volume, recommended_oi,
        recommended_spread_pct, recommended_dte, recommended_mid_price
    FROM `{LABELED_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND exit_reason != 'FUTURE_TIMEOUT'
    """
    df = client.query(sql).to_dataframe()
    out = {}
    for _, row in df.iterrows():
        scan_d = row["scan_date"]
        if isinstance(scan_d, datetime):
            scan_d = scan_d.date()
        entry_day = trader.get_next_trading_day(scan_d)
        exp_d = row["recommended_expiration"]
        if isinstance(exp_d, (pd.Timestamp, datetime)):
            exp_d = exp_d.date()
        out[(row["ticker"], scan_d.isoformat())] = {
            "ticker": row["ticker"],
            "scan_date": scan_d,
            "entry_day": entry_day,
            "expiration": exp_d,
            "premium_score": int(row["premium_score"] or 0),
            "direction": row["direction"],
            "recommended_volume": int(row["recommended_volume"] or 0),
            "recommended_oi": int(row["recommended_oi"] or 0),
            "recommended_spread_pct": float(row["recommended_spread_pct"] or 0.0),
            "recommended_dte": int(row["recommended_dte"] or 0),
            "recommended_mid_price": float(row["recommended_mid_price"] or 0.0),
        }
    return out


def main():
    print("Loading bar cache…", flush=True)
    with CACHE_PATH.open("rb") as f:
        cache = pickle.load(f)
    print(f"  cache size: {len(cache)} signals")

    print("Loading population metadata from BigQuery…")
    client = bigquery.Client(project=PROJECT_ID)
    pop = load_population(client)
    print(f"  population: {len(pop)} signals")

    print("Pre-computing per-signal vectorized data…")
    t0 = time.time()
    precomp: list[SignalPrecomp] = []
    skipped_no_bars = 0
    skipped_no_entry = 0
    for key, meta in pop.items():
        bars = cache.get(key) or []
        if not bars:
            skipped_no_bars += 1
            continue
        p = precompute_signal(bars, meta)
        if p is None:
            skipped_no_entry += 1
            continue
        precomp.append(p)
    print(f"  precomp size: {len(precomp)}  "
          f"(skipped {skipped_no_bars} no_bars, {skipped_no_entry} no_entry)  "
          f"[{time.time() - t0:.1f}s]")

    # Chronological holdout split.
    all_dates = sorted({p.scan_date for p in precomp})
    cutoff_idx = int(len(all_dates) * 0.70)
    cutoff_date = all_dates[cutoff_idx] if cutoff_idx < len(all_dates) else all_dates[-1]
    print(f"  chronological cutoff: {cutoff_date} "
          f"(train < cutoff, test >= cutoff)")

    print("\nRunning sweep…")
    variants = list(product(ENTRY_TIMES, TARGET_PCTS, STOP_PCTS, HOLD_DAYS))
    print(f"  {len(variants)} variants × {len(precomp)} signals "
          f"= {len(variants) * len(precomp):,} simulations")

    rows = []
    detail_records = []  # store per-signal results for the BEST variant later
    t0 = time.time()
    for vi, (et, tgt, stp, hd) in enumerate(variants):
        rets = []
        rets_train = []
        rets_test = []
        target_n = stop_n = timeout_n = 0
        target_n_test = stop_n_test = timeout_n_test = 0
        n_executed = 0
        n_executed_test = 0
        # We don't store per-signal detail here for memory; only aggregate.
        for p in precomp:
            out = simulate_one(p, et, tgt, stp, hd)
            if out is None:
                continue
            r = out["realized_return_pct"]
            rets.append(r)
            n_executed += 1
            er = out["exit_reason"]
            if er == "TARGET":
                target_n += 1
            elif er == "STOP":
                stop_n += 1
            else:
                timeout_n += 1
            if p.scan_date < cutoff_date:
                rets_train.append(r)
            else:
                rets_test.append(r)
                n_executed_test += 1
                if er == "TARGET":
                    target_n_test += 1
                elif er == "STOP":
                    stop_n_test += 1
                else:
                    timeout_n_test += 1

        if not rets:
            continue
        rets_arr = np.array(rets)
        rets_tr_arr = np.array(rets_train) if rets_train else np.array([0.0])
        rets_te_arr = np.array(rets_test) if rets_test else np.array([0.0])

        rows.append({
            "entry_time": et,
            "target_pct": tgt if tgt is not None else -1.0,
            "stop_pct": stp if stp is not None else -1.0,
            "hold_days": hd,
            "n_executed": n_executed,
            "avg_return": float(rets_arr.mean()),
            "median_return": float(np.median(rets_arr)),
            "win_rate": float((rets_arr > 0).mean()),
            "win_rate_5pct": float((rets_arr >= 0.05).mean()),
            "total_return": float(rets_arr.sum()),
            "std_return": float(rets_arr.std()),
            "target_count": target_n,
            "stop_count": stop_n,
            "timeout_count": timeout_n,
            "train_n": len(rets_train),
            "train_avg": float(rets_tr_arr.mean()),
            "train_win_rate": float((rets_tr_arr > 0).mean()),
            "test_n": len(rets_test),
            "test_avg": float(rets_te_arr.mean()),
            "test_win_rate": float((rets_te_arr > 0).mean()),
            "test_target": target_n_test,
            "test_stop": stop_n_test,
            "test_timeout": timeout_n_test,
        })

        if (vi + 1) % 10 == 0 or vi == 0:
            elapsed = time.time() - t0
            eta = elapsed / (vi + 1) * (len(variants) - vi - 1)
            print(f"  {vi + 1}/{len(variants)} variants "
                  f"({elapsed:.0f}s elapsed, ETA {eta:.0f}s)", flush=True)

    df = pd.DataFrame(rows)
    df.to_parquet(RESULTS_PATH)
    print(f"\nWrote {RESULTS_PATH}  ({len(df)} variants)")

    # Re-run the best OOS variant with per-signal detail capture for the report.
    df_sorted = df.sort_values("test_avg", ascending=False).reset_index(drop=True)
    best = df_sorted.iloc[0]
    print(f"\n=== TOP 10 by OOS avg_return ===")
    cols_show = ["entry_time", "target_pct", "stop_pct", "hold_days",
                 "n_executed", "avg_return", "win_rate", "test_avg", "test_win_rate"]
    print(df_sorted[cols_show].head(10).to_string(index=False))

    print(f"\nCapturing per-signal detail for best OOS variant: "
          f"{best['entry_time']} tgt={best['target_pct']} stop={best['stop_pct']} "
          f"hold={best['hold_days']}d")
    best_tgt = best["target_pct"] if best["target_pct"] >= 0 else None
    best_stp = best["stop_pct"] if best["stop_pct"] >= 0 else None
    detail = []
    for p in precomp:
        out = simulate_one(p, best["entry_time"], best_tgt, best_stp, int(best["hold_days"]))
        if out is None:
            continue
        detail.append({
            "ticker": p.ticker,
            "scan_date": p.scan_date,
            "premium_score": p.premium_score,
            "direction": p.direction,
            "recommended_oi": p.recommended_oi,
            "recommended_volume": p.recommended_volume,
            "recommended_spread_pct": p.recommended_spread_pct,
            "recommended_dte": p.recommended_dte,
            "recommended_mid_price": p.recommended_mid_price,
            "entry_price": out["entry_price"],
            "exit_price": out["exit_price"],
            "exit_reason": out["exit_reason"],
            "realized_return_pct": out["realized_return_pct"],
            "is_test": p.scan_date >= cutoff_date,
        })
    detail_df = pd.DataFrame(detail)
    detail_df.to_pickle(SIGNAL_DETAIL_PATH)
    print(f"Wrote {SIGNAL_DETAIL_PATH} ({len(detail_df)} rows)")
    print(f"\nTotal sweep time: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
