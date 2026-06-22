"""
FILL-REALISM model for the entry-timing finding — does the "enter at the open
beats 10:00 by ~+7pp gross" edge SURVIVE realistic AM-spread/slippage, or is it a
thin-tape mirage? This is the deciding test.

HARD CONSTRAINT: this Polygon plan serves NO option NBBO quotes (bid/ask always
NULL — see docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md). So the
spread is ESTIMATED from OHLC, not observed. Three independent lenses:

  1. CORWIN-SCHULTZ (2012) high-low spread estimator — the literature method for
     estimating effective % spread from consecutive high/low bars without quotes.
     Charge half-spread on entry (buy = mid*(1+h)) and exit (sell = mid*(1-h)).
  2. ADVERSE-BAR fill — model-free pessimistic bound: BUY at the entry bar HIGH,
     SELL at the exit bar LOW. If the edge survives this, it is very robust.
  3. VOLUME-FILLABILITY gate — require a real traded print (volume>0) at the entry
     minute, so we don't "fill" at a phantom price.

Plus a BREAKEVEN-SPREAD calc: how much EXTRA open-vs-10:00 half-spread would erase
the gross edge? Compare to the estimated differential.

READ-ONLY; reuses fetch cache + entry_timing_backtest sim. Leakage-safe.
"""
import os
import numpy as np
import pandas as pd
import backtesting_and_research.entry_timing_backtest as B

OUT_DIR = "/home/user/gammarips-engine/backtesting_and_research"
MAX_HALF_SPREAD = 0.50   # cap pathological CS estimates on gappy tape
RULES = ["E_open", "E_0945", "E_1000"]
EXIT_MIN = 15 * 60 + 45


# ---------- Corwin-Schultz (2012) proportional spread from two bars ----------
def cs_spread(h1, l1, h2, l2):
    """Relative (proportional) spread S from two consecutive high/low bars.
    Returns half-spread = S/2, floored at 0, capped at MAX_HALF_SPREAD."""
    if min(h1, l1, h2, l2) <= 0:
        return 0.0
    k = 3 - 2 * np.sqrt(2)
    b = np.log(h1 / l1) ** 2 + np.log(h2 / l2) ** 2
    hi2, lo2 = max(h1, h2), min(l1, l2)
    g = np.log(hi2 / lo2) ** 2
    a = (np.sqrt(2 * b) - np.sqrt(b)) / k - np.sqrt(g / k)
    s = 2 * (np.exp(a) - 1) / (1 + np.exp(a))
    if not np.isfinite(s) or s < 0:
        return 0.0
    return float(min(s / 2.0, MAX_HALF_SPREAD))


def bar_at(bars, entry_min):
    """The bar row used for entry (first bar at/just after entry_min, <=+5)."""
    cand = bars[(bars.et_minutes >= entry_min) & (bars.et_minutes <= entry_min + 5)]
    return None if cand.empty else cand.iloc[0]


def local_half_spread(bars, entry_min):
    """CS half-spread averaged over the entry bar + its neighbor(s)."""
    idx = bars.index[(bars.et_minutes >= entry_min) & (bars.et_minutes <= entry_min + 5)]
    if len(idx) == 0:
        return None
    i = idx[0]
    pos = bars.index.get_loc(i)
    ests = []
    for j in (pos, pos - 1, pos + 1):
        if 0 <= j < len(bars) - 1:
            a, b2 = bars.iloc[j], bars.iloc[j + 1]
            if pd.notna(a["high"]) and pd.notna(b2["high"]):
                ests.append(cs_spread(a["high"], a["low"], b2["high"], b2["low"]))
    return float(np.median(ests)) if ests else 0.0


def simulate_detail(bars, entry_px, entry_min):
    """Like B.simulate but returns (exit_mid, reason, exit_bar)."""
    target = entry_px * (1 + B.TP)
    stop = entry_px * (1 - B.STOP)
    path = bars[(bars.et_minutes > entry_min) & (bars.et_minutes <= EXIT_MIN)]
    path = path.dropna(subset=["high", "low", "close"])
    last = None
    for _, r in path.iterrows():
        last = r
        hi, lo = float(r["high"]), float(r["low"])
        if lo <= stop and hi >= target:
            return stop, "STOP_AMBIG", r
        if hi >= target:
            return target, "TARGET", r
        if lo <= stop:
            return stop, "STOP", r
    if last is None:
        return None, "NO_PATH", None
    return float(last["close"]), "TIMEOUT", last


def build():
    out = B.load_outcomes()
    recs = []
    for o in out.itertuples(index=False):
        day = o.entry_day.isoformat()
        bars = B.load_bars(o.contract, day)
        if bars is None:
            continue
        row = {"contract": o.contract, "entry_day": day, "n_bars": len(bars)}
        ok = True
        for rule in RULES:
            px, emin = B.entry_price(bars, rule)
            if not px or px <= 0:
                ok = False
                break
            mid_exit, reason, exitbar = simulate_detail(bars, px, emin)
            if mid_exit is None:
                ok = False
                break
            ebar = bar_at(bars, emin)
            h = local_half_spread(bars, emin)
            h = 0.0 if h is None else h
            h_exit = local_half_spread(bars, int(exitbar["et_minutes"])) if exitbar is not None else 0.0
            h_exit = 0.0 if h_exit is None else h_exit
            vol_entry = float(ebar["volume"]) if (ebar is not None and pd.notna(ebar["volume"])) else 0.0
            # gross (mid->mid)
            row[rule + "_gross"] = mid_exit / px - 1
            # CS net: buy mid*(1+h), sell mid_exit*(1-h_exit)
            row[rule + "_net_cs"] = (mid_exit * (1 - h_exit)) / (px * (1 + h)) - 1
            # adverse-bar: buy entry-bar HIGH, sell exit-bar LOW
            buy_adv = float(ebar["high"]) if (ebar is not None and pd.notna(ebar["high"])) else px
            sell_adv = float(exitbar["low"]) if (exitbar is not None and pd.notna(exitbar["low"])) else mid_exit
            row[rule + "_net_adv"] = sell_adv / buy_adv - 1
            row[rule + "_h"] = h
            row[rule + "_vol"] = vol_entry
        if ok:
            recs.append(row)
    return pd.DataFrame(recs)


def paired(df, col_rule, col_base, label):
    sub = df.dropna(subset=[col_rule, col_base]).copy()
    sub["_d"] = sub[col_rule] - sub[col_base]
    d2 = {d: g["_d"].to_numpy(float) for d, g in sub.groupby("entry_day")}
    m, lo, hi = B.boot_paired_ci(d2)
    days = sorted(sub.entry_day.unique()); mid = days[len(days) // 2]
    e = sub[sub.entry_day <= mid]["_d"].mean(); l = sub[sub.entry_day > mid]["_d"].mean()
    flag = "  CLEARS 0" if (lo > 0 or hi < 0) else ""
    print(f"  {label:30} N={len(sub):4} Δ={m:+.4f} [{lo:+.4f},{hi:+.4f}] "
          f"early={e:+.4f} late={l:+.4f}{flag}")
    return m


def main():
    df = build()
    print(f"simulated (open/9:45/10:00 all fillable): {len(df)} over "
          f"{df.entry_day.nunique()} days\n")
    df.to_parquet(os.path.join(OUT_DIR, "entry_timing_fill_realism.parquet"), index=False)

    # ---- estimated half-spread by entry time (the core empirical input) ----
    print("=== estimated effective HALF-SPREAD by entry time (Corwin-Schultz) ===")
    for rule in RULES:
        h = df[rule + "_h"]
        print(f"  {rule:8} median={h.median():.4f}  mean={h.mean():.4f}  "
              f"p90={h.quantile(0.90):.4f}")
    diff = (df["E_open_h"] - df["E_1000_h"])
    print(f"  EXTRA open-vs-1000 half-spread: median={diff.median():+.4f} "
          f"mean={diff.mean():+.4f}  (charged on entry)")
    # round-trip extra cost of opening earlier ≈ entry-side diff (exit ~common)
    gross_edge = (df["E_open_gross"] - df["E_1000_gross"]).mean()
    print(f"\n  GROSS open-vs-1000 edge to beat: {gross_edge:+.4f}")
    print(f"  BREAKEVEN: extra open half-spread that erases it ≈ {gross_edge:+.4f} "
          f"vs estimated {diff.mean():+.4f} → "
          f"{'edge > cost (survives in the mean)' if gross_edge > diff.mean() else 'cost >= edge (fragile)'}")

    print("\n=== OPEN vs 10:00 under each fill model (paired, day-clustered CI) ===")
    print("-- gross (mid->mid), as a baseline --")
    paired(df, "E_open_gross", "E_1000_gross", "gross")
    print("-- Corwin-Schultz net (half-spread both legs) --")
    paired(df, "E_open_net_cs", "E_1000_net_cs", "CS-net ALL")
    paired(df[df.n_bars >= 120], "E_open_net_cs", "E_1000_net_cs", "CS-net LIQUID n_bars>=120")
    paired(df[df.E_open_vol > 0], "E_open_net_cs", "E_1000_net_cs", "CS-net + open-volume>0 gate")
    print("-- adverse-bar fill (buy entry HIGH, sell exit LOW) — worst case --")
    paired(df, "E_open_net_adv", "E_1000_net_adv", "adverse ALL")
    paired(df[df.n_bars >= 120], "E_open_net_adv", "E_1000_net_adv", "adverse LIQUID n_bars>=120")

    print("\n=== 9:45 vs 10:00 (the fillable compromise) under each model ===")
    paired(df, "E_0945_gross", "E_1000_gross", "9:45 gross")
    paired(df, "E_0945_net_cs", "E_1000_net_cs", "9:45 CS-net")
    paired(df, "E_0945_net_adv", "E_1000_net_adv", "9:45 adverse")

    print("\nwrote entry_timing_fill_realism.parquet")


if __name__ == "__main__":
    main()
