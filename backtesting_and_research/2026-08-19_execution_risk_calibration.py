"""Execution-risk calibration (READ-ONLY research, 2026-08-19).

Owner question: what guidelines minimise EXECUTION risk for the autonomous
traders? The picks are treated as good; the loss is believed to happen between
the decision and the fill.

We have NO NBBO on this Polygon plan. Confirmed 2026-08-19: bid, ask, mid,
spread_pct and last_trade_price are NULL in ALL 64,550 `pool_liquidity_snapshot`
reads. So the true execution cost (the spread) is UNMEASURABLE here, and every
number below is a PRINT-BASED PROXY for it.

The proxy that survives on a print-only tape is PRICE UNCERTAINTY BETWEEN
PRINTS. If a contract's consecutive prints sit 20% apart, no agent can expect a
fill near the last price it saw, whatever the spread is. That is measurable, and
it is what these four questions calibrate.

  Q1. Print density: how often can you transact at all, through the day?
  Q2. Inter-print price uncertainty: how far does price move between prints?
  Q3. Stop reliability: when the -30% stop breaches, where do you really fill?
  Q4. Early warning: what does the 10:00 ET tape say about the rest of the day?

Everything is bucketed by observables the agent HAS at decision time through
`get_liquidity` (prints so far today, open interest, premium), so the output is
a calibration an agent can reason with, not a rule engine.

Substrate: `option_minute_paths` (enriched pool minute tape, day_index 1/2/3).
Cache is shared with 2026-08-19_pm_entry_overnight_study.py.

Run:
    .venv/bin/python backtesting_and_research/2026-08-19_execution_risk_calibration.py
"""

import db_dtypes  # noqa: F401 - registers the BQ DATE dtype used by the parquet cache
import os

import numpy as np
import pandas as pd

from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "pm_entry_minute_paths.parquet")
STOP_PCT = 0.30
SLIP = 0.02

pd.set_option("display.width", 200)


def pct(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:.{d}f}%"


def main():
    bars = pd.read_parquet(CACHE)
    loc = bars["ts"].dt.tz_convert(ET)
    bars["min_et"] = loc.dt.hour * 60 + loc.dt.minute
    bars = bars.sort_values(["scan_date", "contract", "day_index", "min_et"])
    d1 = bars[bars.day_index == 1].copy()

    print(f"tape: {len(bars):,} bars | day-1 subset {len(d1):,} bars | "
          f"{d1.groupby(['scan_date','contract']).ngroups:,} legs")
    print("\nNO NBBO ON THIS PLAN: bid/ask/mid/spread/last_trade are NULL in all")
    print("64,550 pool_liquidity_snapshot reads. Everything below is a print-based")
    print("proxy for execution cost, never the spread itself.")

    # ---------------------------------------------------------------- Q1
    print("\n" + "=" * 88)
    print("Q1. PRINT DENSITY — can you transact at all? (day-1, per leg)")
    print("=" * 88)
    g = d1.groupby(["scan_date", "contract"])
    leg = pd.DataFrame({
        "n_prints": g.size(),
        "premium": g["close"].median(),
        "first_min": g["min_et"].min(),
        "last_min": g["min_et"].max(),
        "vol": g["volume"].sum(),
    })
    leg["prints_by_1000"] = g.apply(
        lambda x: int((x["min_et"] <= 600).sum()), include_groups=False)
    leg["prints_after_1000"] = leg["n_prints"] - leg["prints_by_1000"]
    q = leg["n_prints"].quantile([.10, .25, .50, .75, .90])
    print(f"  traded minutes out of 390 — p10 {q[.10]:.0f} | p25 {q[.25]:.0f} | "
          f"median {q[.50]:.0f} | p75 {q[.75]:.0f} | p90 {q[.90]:.0f}")
    for thr in (10, 30, 60, 120, 200):
        print(f"  legs with < {thr:>3} traded minutes: "
              f"{(leg.n_prints < thr).mean()*100:>5.1f}%")

    print("\n  Session coverage — share of legs printing in each 30-min block:")
    blocks = [(570, 600, "09:30-10:00"), (600, 630, "10:00-10:30"),
              (630, 690, "10:30-11:30"), (690, 780, "11:30-13:00"),
              (780, 870, "13:00-14:30"), (870, 930, "14:30-15:30"),
              (930, 961, "15:30-16:00")]
    tot_legs = len(leg)
    print(f"  {'block':<14}{'legs printing':>15}{'% of legs':>12}{'mean prints':>13}")
    for lo, hi, name in blocks:
        sub = d1[(d1.min_et >= lo) & (d1.min_et < hi)]
        gg = sub.groupby(["scan_date", "contract"]).size()
        print(f"  {name:<14}{len(gg):>15,}{len(gg)/tot_legs*100:>11.1f}%"
              f"{gg.mean():>13.1f}")

    # ---------------------------------------------------------------- Q2
    print("\n" + "=" * 88)
    print("Q2. INTER-PRINT PRICE UNCERTAINTY — the spread proxy that survives here")
    print("=" * 88)
    d1 = d1.copy()
    key = d1["scan_date"].astype(str) + "|" + d1["contract"]
    d1["_key"] = key
    d1["prev_close"] = d1.groupby("_key")["close"].shift(1)
    d1["prev_min"] = d1.groupby("_key")["min_et"].shift(1)
    d1["gap_min"] = d1["min_et"] - d1["prev_min"]
    d1["jump"] = (d1["close"] / d1["prev_close"] - 1).abs()
    steps = d1[d1.prev_close.notna() & (d1.prev_close > 0)]
    print(f"  consecutive-print steps: {len(steps):,}")
    print("\n  |price move| between consecutive prints, by the GAP between them:")
    print(f"  {'gap between prints':<22}{'steps':>9}{'median':>10}{'p75':>9}"
          f"{'p90':>9}{'p99':>9}")
    for lo, hi, name in [(1, 2, "1 min (continuous)"), (2, 5, "2-4 min"),
                         (5, 15, "5-14 min"), (15, 30, "15-29 min"),
                         (30, 60, "30-59 min"), (60, 10000, "60+ min")]:
        s = steps[(steps.gap_min >= lo) & (steps.gap_min < hi)]["jump"]
        if len(s) < 30:
            continue
        print(f"  {name:<22}{len(s):>9,}{pct(s.median()):>10}"
              f"{pct(s.quantile(.75)):>9}{pct(s.quantile(.90)):>9}"
              f"{pct(s.quantile(.99)):>9}")

    print("\n  Same, by how many prints the contract makes all day (the field an")
    print("  agent can see): median |move| between its consecutive prints.")
    lk = leg.reset_index()
    lk["_key"] = lk["scan_date"].astype(str) + "|" + lk["contract"]
    stepstat = steps.groupby("_key").agg(
        med_jump=("jump", "median"), med_gap=("gap_min", "median"))
    lk = lk.merge(stepstat, on="_key", how="left")
    lk["bucket"] = pd.cut(lk.n_prints, [0, 10, 30, 60, 120, 200, 1e9],
                          labels=["<10", "10-29", "30-59", "60-119", "120-199", "200+"])
    print(f"  {'traded minutes':<16}{'legs':>7}{'med |move|':>12}{'p90 |move|':>12}"
          f"{'med gap':>10}{'med premium':>13}")
    for b, gg in lk.groupby("bucket", observed=True):
        print(f"  {str(b):<16}{len(gg):>7}{pct(gg.med_jump.median()):>12}"
              f"{pct(gg.med_jump.quantile(.90)):>12}"
              f"{gg.med_gap.median():>9.0f}m{gg.premium.median():>12.2f}")

    # ---------------------------------------------------------------- Q3
    print("\n" + "=" * 88)
    print("Q3. STOP RELIABILITY — where do you really fill when -30% breaches?")
    print("=" * 88)
    rows = []
    for k, gg in d1.groupby("_key", sort=False):
        m = gg["min_et"].to_numpy()
        c = gg["close"].to_numpy()
        lo_a = gg["low"].to_numpy()
        i = np.searchsorted(m, 600, side="left")
        if i >= len(m) or m[i] - 600 > 15:
            continue
        base = c[i] * (1 + SLIP)
        stop = base * (1 - STOP_PCT)
        after = np.arange(i + 1, len(m))
        if not len(after):
            continue
        br = after[lo_a[after] <= stop]
        if not len(br):
            continue
        j = br[0]
        rows.append({
            "_key": k, "stop": stop, "fill_low": lo_a[j], "fill_close": c[j],
            "gap_before": m[j] - m[j - 1], "n_prints": len(m),
        })
    st = pd.DataFrame(rows)
    if len(st):
        st["slip_low"] = st.fill_low / st.stop - 1
        st["slip_close"] = st.fill_close / st.stop - 1
        st = st.merge(lk[["_key", "bucket"]], on="_key", how="left")
        print(f"  legs whose -30% stop breached after a 10:00 entry: {len(st):,}")
        print("\n  Fill vs the intended stop price (negative = worse than the stop):")
        print(f"  {'traded minutes':<16}{'legs':>7}{'med slip':>11}{'p10 slip':>11}"
              f"{'p01 slip':>11}{'med gap before':>16}")
        for b, gg in st.groupby("bucket", observed=True):
            print(f"  {str(b):<16}{len(gg):>7}{pct(gg.slip_close.median()):>11}"
                  f"{pct(gg.slip_close.quantile(.10)):>11}"
                  f"{pct(gg.slip_close.quantile(.01)):>11}"
                  f"{gg.gap_before.median():>15.0f}m")
        print(f"\n  ALL: median {pct(st.slip_close.median())} | "
              f"p10 {pct(st.slip_close.quantile(.10))} | "
              f"p01 {pct(st.slip_close.quantile(.01))} | "
              f"worst {pct(st.slip_close.min())}")
        print(f"  share filling >5% below the stop:  "
              f"{(st.slip_close < -0.05).mean()*100:.1f}%")
        print(f"  share filling >15% below the stop: "
              f"{(st.slip_close < -0.15).mean()*100:.1f}%")

    # ---------------------------------------------------------------- Q4
    print("\n" + "=" * 88)
    print("Q4. EARLY WARNING — what the 10:00 ET tape says about the rest of the day")
    print("=" * 88)
    lk["ok_rest"] = lk.prints_after_1000 >= 60
    print(f"  {'prints by 10:00 ET':<22}{'legs':>7}{'% of pool':>11}"
          f"{'P(60+ prints left)':>20}{'med prints left':>17}")
    for lo, hi, name in [(0, 1, "0 (silent tape)"), (1, 3, "1-2"), (3, 6, "3-5"),
                         (6, 11, "6-10"), (11, 21, "11-20"), (21, 1e9, "21+")]:
        gg = lk[(lk.prints_by_1000 >= lo) & (lk.prints_by_1000 < hi)]
        if not len(gg):
            continue
        print(f"  {name:<22}{len(gg):>7}{len(gg)/len(lk)*100:>10.1f}%"
              f"{pct(gg.ok_rest.mean()):>20}{gg.prints_after_1000.median():>17.0f}")

    print("\n  Cross-check against premium (both are visible at decision time):")
    lk["pbucket"] = pd.cut(lk.premium, [0, .5, 1, 2, 5, 1e9],
                           labels=["<$0.50", "$0.50-1", "$1-2", "$2-5", ">$5"])
    print(f"  {'premium':<12}{'legs':>7}{'med prints':>12}{'P(60+ all day)':>17}"
          f"{'med |move|':>13}")
    for b, gg in lk.groupby("pbucket", observed=True):
        print(f"  {str(b):<12}{len(gg):>7}{gg.n_prints.median():>12.0f}"
              f"{pct((gg.n_prints >= 60).mean()):>17}"
              f"{pct(gg.med_jump.median()):>13}")

    # ---------------------------------------------------------------- Q5
    print("\n" + "=" * 88)
    print("Q5. THE SAME PICKS UNDER REALISTIC FILLS  (V7.1 bracket, 10:00 -> 15:45)")
    print("=" * 88)
    print("  Three fill conventions on identical legs and identical bracket:")
    print("   PAPER    = production's flat 2% each way (what the ledger reports)")
    print("   ADVERSE  = buy the entry bar's HIGH, sell the exit bar's LOW")
    print("              (model-free, but BLIND on single-print bars where h==l==c,")
    print("               so it UNDERSTATES cost exactly where risk is highest)")
    print("   UNCERT   = pay half the leg's own median inter-print move each way")
    print("              (a spread-equivalent that stays honest on a thin tape)")
    jumpmap = lk.set_index("_key")["med_jump"].to_dict()
    out = []
    for k, gg in d1.groupby("_key", sort=False):
        m = gg["min_et"].to_numpy()
        c = gg["close"].to_numpy()
        h = gg["high"].to_numpy()
        lo_a = gg["low"].to_numpy()
        i = np.searchsorted(m, 600, side="left")
        if i >= len(m) or m[i] - 600 > 15:
            continue
        j = np.searchsorted(m, 945, side="left")
        if j >= len(m) or m[j] - 945 > 15 or j <= i:
            continue
        mj = jumpmap.get(k)
        if mj is None or not np.isfinite(mj):
            continue
        row = {"_key": k, "n_prints": len(m)}
        for name, ep, xp in [
            ("paper", c[i] * (1 + SLIP), None),
            ("adverse", h[i], None),
            ("uncert", c[i] * (1 + mj / 2), None),
        ]:
            stop = ep * (1 - STOP_PCT)
            target = ep * (1 + 0.40)
            res = None
            for t in range(i + 1, j + 1):
                if lo_a[t] <= stop:
                    res = stop
                    break
                if h[t] >= target:
                    res = target
                    break
            if res is None:
                res = {"paper": c[j] * (1 - SLIP), "adverse": lo_a[j],
                       "uncert": c[j] * (1 - mj / 2)}[name]
            else:
                res = {"paper": res * (1 - SLIP), "adverse": res,
                       "uncert": res * (1 - mj / 2)}[name]
            row[name] = (res - ep) / ep
        out.append(row)
    ex = pd.DataFrame(out)
    if len(ex):
        ex = ex.merge(lk[["_key", "bucket"]], on="_key", how="left")
        print(f"\n  legs with both a 10:00 and a 15:45 real print: {len(ex):,}")
        print(f"\n  {'traded minutes':<16}{'legs':>7}{'PAPER':>10}{'ADVERSE':>10}"
              f"{'UNCERT':>10}{'drag vs paper':>16}")
        for b, gg in ex.groupby("bucket", observed=True):
            drag = gg["uncert"].mean() - gg["paper"].mean()
            print(f"  {str(b):<16}{len(gg):>7}{pct(gg['paper'].mean()):>10}"
                  f"{pct(gg['adverse'].mean()):>10}{pct(gg['uncert'].mean()):>10}"
                  f"{pct(drag):>16}")
        drag = ex["uncert"].mean() - ex["paper"].mean()
        print(f"  {'ALL':<16}{len(ex):>7}{pct(ex['paper'].mean()):>10}"
              f"{pct(ex['adverse'].mean()):>10}{pct(ex['uncert'].mean()):>10}"
              f"{pct(drag):>16}")

    print("\ndone.")


if __name__ == "__main__":
    main()
