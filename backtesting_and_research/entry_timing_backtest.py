"""
ENTRY-TIMING backtest — does the fixed 10:00 ET entry systematically bleed vs an
earlier fill? Re-simulates the SAME V7 GIGO bracket (+40% TP / -30% stop / 15:45
ET flat, stop-wins-ambiguous) from four entry rules on the option-premium path:

  E_open   : 09:30 bar open
  E_0945   : 09:45 bar open
  E_1000   : 10:00 bar open   (≈ production V7 entry — validated vs the table)
  E_vwap   : volume-weighted avg over [09:30, 10:00)

Substrate: enriched_option_outcomes (46 days, 04-13..06-18) ⨝ the cached option
minute bars (fetch_option_minute_bars.py). GROSS premium returns (no slippage) so
the comparison is clean + apples-to-apples across rules. Day-CLUSTERED bootstrap
CIs (resample entry_days) on the PAIRED diff vs E_1000, plus an early/late
walk-forward split. READ-ONLY against BQ; writes only local artifacts.

LEAKAGE: this varies the mechanical entry EXECUTION time only — no forward info
selects anything; the full pool is used. Safe by construction.
"""
import os
import glob
import json
import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from google.cloud import bigquery

CACHE_DIR = "/home/user/gammarips-engine/backtesting_and_research/cache/poly_minute_option"
OUT_DIR = "/home/user/gammarips-engine/backtesting_and_research"
BQ_TABLE = "profitscout-fida8.profit_scout.enriched_option_outcomes"
ET = ZoneInfo("America/New_York")
TP, STOP = 0.40, 0.30
EXIT_HM = (15, 45)
N_BOOT = 2000
RULES = ["E_open", "E_0945", "E_1000", "E_vwap"]


def sanitize(c):
    return c.replace(":", "_")


def load_outcomes():
    bq = bigquery.Client(project="profitscout-fida8")
    df = bq.query(f"""
        SELECT recommended_contract AS contract, entry_day, direction,
               entry_price AS prod_entry_price, realized_return_pct AS prod_ret
        FROM `{BQ_TABLE}`
        WHERE recommended_contract IS NOT NULL AND entry_day IS NOT NULL
    """).to_dataframe()
    df["entry_day"] = pd.to_datetime(df["entry_day"]).dt.date
    return df


def load_bars(contract, day):
    p = os.path.join(CACHE_DIR, f"{sanitize(contract)}__{day}.parquet")
    if not os.path.exists(p):
        return None
    b = pd.read_parquet(p)
    if b.empty:
        return None
    b = b.copy()
    ts = pd.to_datetime(b["ts_utc"], utc=True)
    et = ts.dt.tz_convert(ET)
    b["et_hm"] = et.dt.strftime("%H:%M")
    b["et_minutes"] = et.dt.hour * 60 + et.dt.minute
    return b.sort_values("et_minutes").reset_index(drop=True)


def entry_price(bars, rule):
    """Executable entry price for a rule, or None."""
    if rule == "E_vwap":
        w = bars[(bars.et_minutes >= 9 * 60 + 30) & (bars.et_minutes < 10 * 60)]
        w = w.dropna(subset=["close"])
        if w.empty:
            return None, None
        vol = w["volume"].fillna(0).to_numpy(dtype=float)
        vw = w["vwap"].where(w["vwap"].notna(), w["close"]).to_numpy(dtype=float)
        px = float(np.average(vw, weights=vol)) if vol.sum() > 0 else float(w["close"].mean())
        return px, 10 * 60  # vwap "fills" by 10:00; bracket walks bars after 10:00
    hm = {"E_open": 9 * 60 + 30, "E_0945": 9 * 60 + 45, "E_1000": 10 * 60}[rule]
    # the bar at that minute; tolerate up to 5 min late (sparse tape) but not earlier
    cand = bars[(bars.et_minutes >= hm) & (bars.et_minutes <= hm + 5)]
    if cand.empty:
        return None, None
    row = cand.iloc[0]
    if pd.isna(row["open"]):
        return None, None
    return float(row["open"]), int(row["et_minutes"])


def simulate(bars, entry_px, entry_min):
    """V7 GIGO bracket on the option-premium path. Returns (ret, reason)."""
    target = entry_px * (1 + TP)
    stop = entry_px * (1 - STOP)
    exit_min = EXIT_HM[0] * 60 + EXIT_HM[1]
    path = bars[(bars.et_minutes > entry_min) & (bars.et_minutes <= exit_min)]
    path = path.dropna(subset=["high", "low", "close"])
    last_close = None
    for _, r in path.iterrows():
        hi, lo, last_close = float(r["high"]), float(r["low"]), float(r["close"])
        hit_stop = lo <= stop
        hit_tp = hi >= target
        if hit_stop and hit_tp:
            return stop / entry_px - 1, "STOP_AMBIG"   # stop wins ambiguous
        if hit_tp:
            return target / entry_px - 1, "TARGET"
        if hit_stop:
            return stop / entry_px - 1, "STOP"
    if last_close is None:
        return None, "NO_PATH"
    return last_close / entry_px - 1, "TIMEOUT"


def boot_mean_ci(day_to_vals, n=N_BOOT, seed=7):
    """Day-clustered bootstrap CI for the mean of a per-row metric."""
    days = list(day_to_vals.keys())
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        samp = rng.choice(days, size=len(days), replace=True)
        vals = np.concatenate([day_to_vals[d] for d in samp])
        means.append(vals.mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    allv = np.concatenate([day_to_vals[d] for d in days])
    return allv.mean(), lo, hi


def boot_paired_ci(day_to_diff, n=N_BOOT, seed=11):
    """Day-clustered bootstrap CI for a paired per-row difference (rule - E_1000)."""
    days = list(day_to_diff.keys())
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        samp = rng.choice(days, size=len(days), replace=True)
        vals = np.concatenate([day_to_diff[d] for d in samp])
        means.append(vals.mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    allv = np.concatenate([day_to_diff[d] for d in days])
    return allv.mean(), lo, hi


def main():
    out = load_outcomes()
    print(f"outcomes rows: {len(out)}")
    recs = []
    n_no_bars = n_incomplete = 0
    for o in out.itertuples(index=False):
        day = o.entry_day.isoformat()
        bars = load_bars(o.contract, day)
        if bars is None:
            n_no_bars += 1
            continue
        rule_ret = {}
        ok = True
        for rule in RULES:
            px, emin = entry_price(bars, rule)
            if px is None or px <= 0:
                ok = False
                break
            ret, reason = simulate(bars, px, emin)
            if ret is None:
                ok = False
                break
            rule_ret[rule] = ret
            rule_ret[rule + "_px"] = px
            rule_ret[rule + "_reason"] = reason
        if not ok:
            n_incomplete += 1
            continue
        rec = {"contract": o.contract, "entry_day": day, "direction": o.direction,
               "prod_entry_price": o.prod_entry_price, "prod_ret": o.prod_ret,
               "n_bars": len(bars)}
        rec.update(rule_ret)
        recs.append(rec)

    res = pd.DataFrame(recs)
    print(f"simulated (all 4 rules fillable): {len(res)}  "
          f"| dropped no-bars={n_no_bars} incomplete={n_incomplete}")
    if res.empty:
        raise SystemExit("no simulatable rows yet — is the fetch done?")
    res.to_parquet(os.path.join(OUT_DIR, "entry_timing_results.parquet"), index=False)

    # ---- validation: E_1000 sim vs production realized ----
    v = res.dropna(subset=["prod_ret"])
    if len(v) > 20:
        corr = np.corrcoef(v["E_1000"], v["prod_ret"])[0, 1]
        print(f"\nVALIDATION  E_1000 sim vs production realized_return_pct: "
              f"corr={corr:.3f}  mean(sim)={v['E_1000'].mean():+.4f} "
              f"mean(prod)={v['prod_ret'].mean():+.4f}  N={len(v)}")

    days_all = sorted(res["entry_day"].unique())
    mid = days_all[len(days_all) // 2]

    def per_day(col):
        return {d: g[col].to_numpy(dtype=float)
                for d, g in res.groupby("entry_day")}

    print(f"\n=== ENTRY-RULE OUTCOMES (gross premium return; N={len(res)}, "
          f"{len(days_all)} days) ===")
    print(f"{'rule':8} {'mean':>9} {'95% CI':>20} {'median':>8} {'win%':>6} "
          f"{'TP%':>5} {'STOP%':>6} {'TIME%':>6}")
    for rule in RULES:
        m, lo, hi = boot_mean_ci(per_day(rule))
        med = res[rule].median()
        win = (res[rule] > 0).mean() * 100
        reasons = res[rule + "_reason"]
        tp = (reasons == "TARGET").mean() * 100
        st = reasons.isin(["STOP", "STOP_AMBIG"]).mean() * 100
        tm = (reasons == "TIMEOUT").mean() * 100
        print(f"{rule:8} {m:+8.4f} [{lo:+.4f},{hi:+.4f}] {med:+8.4f} "
              f"{win:5.1f} {tp:4.1f} {st:5.1f} {tm:5.1f}")

    print("\n=== PAIRED vs E_1000 (per-contract diff; day-clustered CI) ===")
    print(f"{'rule':8} {'Δmean vs 1000':>14} {'95% CI':>22} {'early½':>9} {'late½':>9}")
    for rule in ["E_open", "E_0945", "E_vwap"]:
        res["_d"] = res[rule] - res["E_1000"]
        d2 = {d: g["_d"].to_numpy(dtype=float) for d, g in res.groupby("entry_day")}
        m, lo, hi = boot_paired_ci(d2)
        early = res[res.entry_day <= mid]["_d"].mean()
        late = res[res.entry_day > mid]["_d"].mean()
        flag = "  <-- CI clears 0" if (lo > 0 or hi < 0) else ""
        print(f"{rule:8} {m:+13.4f} [{lo:+.4f},{hi:+.4f}] "
              f"{early:+8.4f} {late:+8.4f}{flag}")

    # ---- liquid subset (>=120 minute bars ~ continuously traded) ----
    liq = res[res.n_bars >= 120]
    if len(liq) > 50:
        print(f"\n=== LIQUID SUBSET (n_bars>=120; N={len(liq)}) paired vs E_1000 ===")
        for rule in ["E_open", "E_0945", "E_vwap"]:
            liq = liq.copy()
            liq["_d"] = liq[rule] - liq["E_1000"]
            d2 = {d: g["_d"].to_numpy(dtype=float) for d, g in liq.groupby("entry_day")}
            m, lo, hi = boot_paired_ci(d2)
            flag = "  <-- CI clears 0" if (lo > 0 or hi < 0) else ""
            print(f"{rule:8} Δ={m:+.4f} [{lo:+.4f},{hi:+.4f}]{flag}")

    summary = {
        "n_simulated": int(len(res)),
        "n_days": int(len(days_all)),
        "rules": {r: {"mean": float(res[r].mean()),
                      "median": float(res[r].median()),
                      "win_rate": float((res[r] > 0).mean())} for r in RULES},
    }
    with open(os.path.join(OUT_DIR, "entry_timing_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nwrote entry_timing_results.parquet + entry_timing_summary.json")


if __name__ == "__main__":
    main()
