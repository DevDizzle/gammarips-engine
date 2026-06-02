"""Moneyness-band study (READ-ONLY research).

Re-replays the +80/-60/trail bracket on the cached option bars with REALISTIC
spread-based entry/exit cost (not the flat 1.02 slippage), stratified by
moneyness bucket, to test whether the current 5-10% OTM gate is mis-set for the
3-day bracket. Leverage-aware by construction: realized OPTION bracket PnL per
moneyness level, with the deep-OTM liquidity penalty charged via the actual
recommended_spread_pct (enrichment already caps spread <= 8%).

Cost models:
  flat102      : base_entry = bar_close * 1.02, no exit haircut (the prior label)
  half_spread  : entry = bar_close*(1+s/2), exit fill = level*(1-s/2)   [DECISION]
  full_spread  : entry = bar_close*(1+s),   exit fill = level*(1-s)     [punitive]
where s = recommended_spread_pct. Bracket TRIGGER levels scale with base_entry
(mirrors main.py: target/stop are relative to entry cost).
"""
import datetime, json, os
import numpy as np
import pandas as pd

# reuse cache loader + trading calendar + constants from the existing replay
from realized_option_label import (
    load_window_bars, next_td, nth_next_td, ts_ms, CACHE, EST,
    HOLD_DAYS, TARGET_PCT, STOP_PCT, TRAIL_TRIGGER_PCT, TRAIL_DRAWDOWN_PCT,
)

np.random.seed(7)
PKL = "/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl"


def replay(bars, entry_day, exit_day, spread, mode):
    """Parameterized bracket replay. Returns (exit_reason, realized_ret) or (None, None)."""
    s = float(spread) if spread is not None and not pd.isna(spread) else 0.0
    if mode == "flat102":
        entry_mult, haircut = 1.02, 0.0
    elif mode == "half_spread":
        entry_mult, haircut = 1 + s / 2, s / 2
    else:  # full_spread
        entry_mult, haircut = 1 + s, s

    entry_ts = ts_ms(entry_day, (10, 0))
    timeout_ts = ts_ms(exit_day, (15, 50))
    eday = [b for b in bars
            if datetime.datetime.fromtimestamp(b["t"] / 1000, tz=EST).date() == entry_day]
    if not eday:
        return None, None
    after = [b for b in eday if b["t"] >= entry_ts]
    entry_bar = after[0] if after else (eday[-1] if eday else None)
    if not entry_bar or entry_bar.get("v", 0) == 0:
        return None, None

    base_entry = entry_bar["c"] * entry_mult
    stop = base_entry * (1 - STOP_PCT)
    target = base_entry * (1 + TARGET_PCT)
    trail_trigger = base_entry * (1 + TRAIL_TRIGGER_PCT)
    idx = bars.index(entry_bar)
    peak = base_entry
    trail_active, trail_level = False, None
    exit_reason, exit_level, last_in = "TIMEOUT", None, None
    for j in range(idx + 1, len(bars)):
        b = bars[j]
        if b["t"] >= timeout_ts:
            tb = last_in if last_in is not None else b
            exit_reason, exit_level = "TIMEOUT", tb["c"]
            break
        if b["h"] > peak:
            peak = b["h"]
            if peak >= trail_trigger:
                trail_active = True
            if trail_active:
                trail_level = peak * (1 - TRAIL_DRAWDOWN_PCT)
        eff_stop = trail_level if trail_active else stop
        if b["l"] <= eff_stop:
            exit_reason, exit_level = ("TRAIL" if trail_active else "STOP"), eff_stop
            break
        if b["h"] >= target:
            exit_reason, exit_level = "TARGET", target
            break
        last_in = b
    if exit_level is None:
        exit_reason = "TIMEOUT"
        exit_level = (last_in if last_in is not None else entry_bar)["c"]

    fill = exit_level * (1 - haircut)              # pay half/full spread on the way out
    ret = (fill - base_entry) / base_entry
    return exit_reason, float(ret)


def bucket(m):
    if pd.isna(m):
        return None
    if m < 0:       return "1_ITM(<0)"
    if m < 0.05:    return "2_ATM(0-5%)"
    if m <= 0.10:   return "3_BAND(5-10%)*"
    if m <= 0.15:   return "4_OTM(10-15%)"
    return "5_DEEP(>15%)"


def main():
    r = pd.read_pickle(PKL)
    r["m"] = pd.to_numeric(r["moneyness_pct"], errors="coerce")
    r["s"] = pd.to_numeric(r["recommended_spread_pct"], errors="coerce")
    r["b"] = r["m"].apply(bucket)
    r["entry_day"] = pd.to_datetime(r["entry_day"])
    fil = r[r["status"] == "FILLED"].copy()
    print(f"FILLED rows: {len(fil)}")

    # re-replay each FILLED row under all three cost models
    modes = ["flat102", "half_spread", "full_spread"]
    out = {mode: [] for mode in modes}
    for _, row in fil.iterrows():
        contract, ed = row["recommended_contract"], row["entry_day"]
        if pd.isna(ed) or contract is None:
            for mode in modes: out[mode].append((None, None))
            continue
        ed = ed.date()
        xd = nth_next_td(ed, HOLD_DAYS - 1)
        hold = [d for d in [ed, nth_next_td(ed, 1), nth_next_td(ed, 2)] if d is not None]
        bars, _, _ = load_window_bars(contract + ".json", hold)
        for mode in modes:
            out[mode].append(replay(bars, ed, xd, row["s"], mode) if (xd and bars) else (None, None))
    for mode in modes:
        fil[f"reason_{mode}"] = [x[0] for x in out[mode]]
        fil[f"ret_{mode}"] = [x[1] for x in out[mode]]

    # ---- A. per-bucket table, all cost models ----
    print("\n=== A. PER-BUCKET realized bracket PnL by cost model (FILLED only) ===")
    rows = []
    for b in sorted(x for x in fil["b"].dropna().unique()):
        sub = fil[fil["b"] == b]
        rec = [b, len(sub), round(sub["s"].mean(), 3)]
        for mode in modes:
            rr = sub[f"ret_{mode}"].dropna()
            tgt = (sub[f"reason_{mode}"] == "TARGET").mean()
            rec += [round(rr.mean(), 3), round(tgt, 3), round((rr >= 0.25).mean(), 3)]
        rows.append(rec)
    cols = ["bucket", "n", "mean_spread"]
    for mode in modes:
        cols += [f"{mode[:4]}_meanRet", f"{mode[:4]}_tgt", f"{mode[:4]}_w25"]
    print(pd.DataFrame(rows, columns=cols).to_string(index=False))

    # ---- B. bootstrap 90% CI on mean_ret per bucket (half_spread = decision model) ----
    print("\n=== B. BOOTSTRAP 90% CI on mean realized return, half_spread (B=2000) ===")
    rows = []
    for b in sorted(x for x in fil["b"].dropna().unique()):
        v = fil.loc[fil["b"] == b, "ret_half_spread"].dropna().values
        if len(v) < 5:
            rows.append([b, len(v), "n/a", "n/a", "n/a"]); continue
        boot = [np.mean(np.random.choice(v, len(v), replace=True)) for _ in range(2000)]
        rows.append([b, len(v), round(v.mean(), 3),
                     round(np.percentile(boot, 5), 3), round(np.percentile(boot, 95), 3)])
    print(pd.DataFrame(rows, columns=["bucket", "n", "mean_ret", "ci_lo", "ci_hi"]).to_string(index=False))

    # ---- C. chronological split (half_spread mean_ret) ----
    med = fil["entry_day"].median()
    print(f"\n=== C. CHRONOLOGICAL SPLIT at {med.date()} (half_spread mean_ret) ===")
    rows = []
    for b in sorted(x for x in fil["b"].dropna().unique()):
        sub = fil[fil["b"] == b]
        h1 = sub.loc[sub["entry_day"] < med, "ret_half_spread"].dropna()
        h2 = sub.loc[sub["entry_day"] >= med, "ret_half_spread"].dropna()
        rows.append([b, len(h1), round(h1.mean(), 3) if len(h1) else None,
                     len(h2), round(h2.mean(), 3) if len(h2) else None])
    print(pd.DataFrame(rows, columns=["bucket", "n_H1", "H1_meanRet", "n_H2", "H2_meanRet"]).to_string(index=False))

    # ---- D. candidate-band decision table (slate size + pooled EV + CI, half_spread) ----
    print("\n=== D. CANDIDATE BANDS: fillable slate size + pooled mean_ret (half_spread) ===")
    att = r[r["status"].isin(["FILLED", "INVALID_LIQUIDITY", "CACHE_EMPTY"])].copy()
    att["filled"] = att["status"] == "FILLED"
    bands = {
        "current [0.05,0.10]": (0.05, 0.10),
        "widen cap [0.05,0.15]": (0.05, 0.15),
        "widen cap [0.05,0.20]": (0.05, 0.20),
        "drop floor [0.0,0.15]": (0.0, 0.15),
        "all-OTM [0.0,0.99]": (0.0, 0.99),
    }
    rows = []
    for name, (lo, hi) in bands.items():
        a = att[(att["m"] >= lo) & (att["m"] <= hi)]
        f = fil[(fil["m"] >= lo) & (fil["m"] <= hi)]
        v = f["ret_half_spread"].dropna().values
        if len(v) >= 5:
            boot = [np.mean(np.random.choice(v, len(v), replace=True)) for _ in range(2000)]
            ci = f"[{np.percentile(boot,5):.3f}, {np.percentile(boot,95):.3f}]"
        else:
            ci = "n/a"
        rows.append([name, len(a), round(a["filled"].mean(), 2), len(v),
                     round(v.mean(), 3) if len(v) else None,
                     round((v >= 0.25).mean(), 3) if len(v) else None, ci])
    print(pd.DataFrame(rows, columns=["band", "n_attempted", "fill_rate", "n_filled",
                                      "mean_ret", "w25_rate", "meanRet_90CI"]).to_string(index=False))


if __name__ == "__main__":
    main()
