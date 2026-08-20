"""Bracket sweep on the TRADEABLE subset only (READ-ONLY research, 2026-08-19).

Owner call. [[bracket-optimization-dead]] is settled doctrine: 0 of 840 bracket variants
were profitable in-sample AND out-of-sample. This re-runs the question on the ONE
substrate that sweep never had: contracts labelled TRADEABLE by the entry-day tape.

Why it is not simply a re-litigation. The 840-variant sweep ran on `signals_labeled_v1`,
a whole-pool cohort. The 2026-08-19 tradeability work showed that cohort class is about
58% ghost-contaminated, with 16.8% of rows carrying the exact no-move return -1.9608%
(the exit filling at the entry bar's own close). A bracket cannot be evaluated on rows
where the bracket never fires: on 0-2-print contracts STOP fires on 8.8% of rows against
35.8% on tradeable ones. So the prior sweep's verdict was measured mostly on
non-participation.

Protocol, matched to the original so the verdicts are comparable:
  * Grid of target x stop x same-day exit time. `None` means that leg is disabled.
  * Production conventions: 2% slippage each way, TIMEOUT > STOP > TARGET (conservative),
    and a REAL print required within 15 min at both the entry and the exit anchor
    (the stale-exit rule; a carried-forward price is a fabricated fill).
  * HOLDOUT IS THE HEADLINE. The grid is 432 variants against ~550 legs, so the
    in-sample maximum is heavily selected and means nothing on its own. Days are split
    chronologically 60/40; the best in-sample config is then read once out-of-sample.
  * Reported the same way the 840-sweep was: how many variants are profitable in-sample,
    and how many survive out-of-sample.

Run:
    .venv/bin/python backtesting_and_research/2026-08-19_bracket_sweep_tradeable.py
"""

import db_dtypes  # noqa: F401 - registers the BQ DATE dtype used by the parquet cache
import os

import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
TAPE = os.path.join(HERE, "cache", "pm_entry_minute_paths.parquet")

SLIP = 0.02
FILL_TOL = 15
N_BOOT = 5000
RNG = np.random.default_rng(23)

TARGETS = [None, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80]
STOPS = [None, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]
EXITS = ["11:00", "12:00", "13:00", "14:00", "15:00", "15:45"]
LIVE = (0.40, 0.30, "15:45")


def anchor(mins, hhmm, tol=FILL_TOL):
    want = int(hhmm[:2]) * 60 + int(hhmm[3:])
    i = np.searchsorted(mins, want, "left")
    if i >= len(mins) or mins[i] - want > tol:
        return None
    return int(i)


def build():
    bars = pd.read_parquet(TAPE)
    loc = bars["ts"].dt.tz_convert(ET)
    bars["min_et"] = loc.dt.hour * 60 + loc.dt.minute
    d1 = bars[bars.day_index == 1].sort_values(["scan_date", "contract", "min_et"])
    legs = []
    for (sd, c), g in d1.groupby(["scan_date", "contract"], sort=False):
        m = g.min_et.to_numpy()
        i = anchor(m, "10:00")
        if i is None:
            continue
        pb = int((m <= 600).sum())
        legs.append({
            "scan_date": sd, "contract": c, "prints_by_1000": pb, "i": i,
            "min": m, "open": g.open.to_numpy(float), "high": g.high.to_numpy(float),
            "low": g.low.to_numpy(float), "close": g.close.to_numpy(float),
        })
    return legs


def replay(leg, target_pct, stop_pct, exit_hhmm):
    """Return net return, or None when the tape cannot support the trade."""
    m, i = leg["min"], leg["i"]
    j = anchor(m, exit_hhmm)
    if j is None or j <= i:
        return None
    base = leg["close"][i] * (1 + SLIP)
    tgt = base * (1 + target_pct) if target_pct is not None else None
    stp = base * (1 - stop_pct) if stop_pct is not None else None
    hi, lo = leg["high"], leg["low"]
    for t in range(i + 1, j + 1):
        if stp is not None and lo[t] <= stp:
            return (stp * (1 - SLIP) - base) / base
        if tgt is not None and hi[t] >= tgt:
            return (tgt * (1 - SLIP) - base) / base
    return (leg["close"][j] * (1 - SLIP) - base) / base


def evaluate(legs, cfg):
    t, s, x = cfg
    out, days = [], []
    for lg in legs:
        r = replay(lg, t, s, x)
        if r is not None:
            out.append(r)
            days.append(lg["scan_date"])
    if not out:
        return None
    return pd.DataFrame({"ret": out, "scan_date": days})


def mean_ci(df, n=N_BOOT):
    gs = [g["ret"].to_numpy() for _, g in df.groupby("scan_date")]
    if len(gs) < 5:
        return np.nan, np.nan, np.nan
    obs = np.concatenate(gs).mean()
    k = len(gs)
    v = np.empty(n)
    for b in range(n):
        v[b] = np.concatenate([gs[i] for i in RNG.integers(0, k, k)]).mean()
    return obs, float(np.percentile(v, 5)), float(np.percentile(v, 95))


def sweep(legs, label):
    rows = []
    for t in TARGETS:
        for s in STOPS:
            for x in EXITS:
                df = evaluate(legs, (t, s, x))
                if df is None or len(df) < 30:
                    continue
                rows.append({
                    "target": t, "stop": s, "exit": x, "n": len(df),
                    "days": df.scan_date.nunique(), "mean": df["ret"].mean(),
                    "median": df["ret"].median(), "win": (df["ret"] > 0).mean(),
                    "p05": df["ret"].quantile(0.05),
                })
    r = pd.DataFrame(rows)
    print(f"\n  {label}: {len(r)} variants evaluated, "
          f"{(r['mean'] > 0).sum()} with a positive mean "
          f"({(r['mean'] > 0).mean()*100:.1f}%)")
    return r


def fmt(v):
    return "none" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.0%}"


def show(r, k=12, title="top variants by mean"):
    print(f"\n  {title}")
    print(f"  {'target':>7}{'stop':>7}{'exit':>8}{'n':>6}{'days':>6}"
          f"{'mean':>9}{'median':>9}{'win%':>7}{'p05':>9}")
    for _, x in r.sort_values("mean", ascending=False).head(k).iterrows():
        print(f"  {fmt(x.target):>7}{fmt(x.stop):>7}{x['exit']:>8}{int(x.n):>6}"
              f"{int(x.days):>6}{x['mean']*100:>8.2f}%{x['median']*100:>8.2f}%"
              f"{x.win*100:>6.1f}%{x.p05*100:>8.1f}%")


def main():
    legs = build()
    print(f"legs with a real 10:00 print: {len(legs):,}")
    for name, sel in [("TRADEABLE (11+ prints by 10:00)", lambda l: l["prints_by_1000"] >= 11),
                      ("SEMI (6+ prints by 10:00)", lambda l: l["prints_by_1000"] >= 6)]:
        sub = [l for l in legs if sel(l)]
        days = sorted({l["scan_date"] for l in sub})
        print("\n" + "=" * 86)
        print(f"{name}: {len(sub)} legs, {len(days)} days")
        print("=" * 86)

        base = evaluate(sub, LIVE)
        m, lo, hi = mean_ci(base)
        print(f"  LIVE V7.1 (+40/-30/15:45): n={len(base)} mean {m*100:+.2f}% "
              f"90% CI [{lo*100:+.1f}%, {hi*100:+.1f}%] win {(base['ret']>0).mean()*100:.1f}%")

        full = sweep(sub, "FULL PERIOD")
        show(full)

        # ---- chronological holdout: the only column that decides anything
        cut = days[int(len(days) * 0.6)]
        ins = [l for l in sub if l["scan_date"] < cut]
        oos = [l for l in sub if l["scan_date"] >= cut]
        print(f"\n  HOLDOUT SPLIT at {cut}: in-sample {len(ins)} legs / "
              f"out-of-sample {len(oos)} legs")
        r_in = sweep(ins, "IN-SAMPLE")
        if not len(r_in):
            continue
        best = r_in.sort_values("mean", ascending=False).iloc[0]
        cfg = (best.target if not pd.isna(best.target) else None,
               best.stop if not pd.isna(best.stop) else None, best["exit"])
        print(f"  best in-sample: target {fmt(best.target)} / stop {fmt(best.stop)} / "
              f"exit {best['exit']}  ->  in-sample mean {best['mean']*100:+.2f}% "
              f"(n={int(best.n)})")
        d_oos = evaluate(oos, cfg)
        if d_oos is not None and len(d_oos) >= 20:
            m2, lo2, hi2 = mean_ci(d_oos)
            print(f"  SAME CONFIG OUT-OF-SAMPLE: n={len(d_oos)} mean {m2*100:+.2f}% "
                  f"90% CI [{lo2*100:+.1f}%, {hi2*100:+.1f}%]")
        else:
            print("  out-of-sample sample too thin to read")

        r_oos = sweep(oos, "OUT-OF-SAMPLE (all variants)")
        if len(r_oos):
            j = r_in.merge(r_oos, on=["target", "stop", "exit"], how="inner",
                           suffixes=("_in", "_oos"))
            both = j[(j["mean_in"] > 0) & (j["mean_oos"] > 0)]
            print(f"\n  VARIANTS PROFITABLE IN BOTH HALVES: {len(both)} of {len(j)}"
                  f"   (the 840-sweep's comparable figure was 0)")
            if len(both):
                print(f"  {'target':>7}{'stop':>7}{'exit':>8}"
                      f"{'in mean':>10}{'oos mean':>10}{'oos n':>7}")
                for _, x in both.sort_values("mean_oos", ascending=False).head(10).iterrows():
                    print(f"  {fmt(x.target):>7}{fmt(x.stop):>7}{x['exit']:>8}"
                          f"{x['mean_in']*100:>9.2f}%{x['mean_oos']*100:>9.2f}%"
                          f"{int(x.n_oos):>7}")
            corr = j[["mean_in", "mean_oos"]].corr().iloc[0, 1]
            print(f"  rank correlation of variant means across halves: {corr:.3f}"
                  f"   (near 0 = the grid is noise)")

    print("\ndone.")


if __name__ == "__main__":
    main()
