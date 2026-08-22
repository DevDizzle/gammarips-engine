"""Outcome phase for the liquid-universe funnel study (2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-20-liquid-universe-funnel-spec.md (FROZEN).
Budget reported by the compute step: 5,433 legs, ~16K minute-agg calls.

STEPS:
  pull     One minute-agg range call per (session, contract) leg over
           [entry_day, entry_day + 2 trading days]. Resumable, cached.
  metrics  Per leg: fill at the 10:00 ET bar close x 1.02 with a real print
           in [09:55, 10:15] (else UNFILLABLE, counted per arm), MFE/MAE
           same-day (primary) and 3-day (secondary), tradeability (11+
           prints by 10:00 ET). Inference: pooled-leg median, paired-by-day
           block bootstrap (seed 42, 5,000 resamples, 90% CI), C pooled
           over 200 draws with per-draw weights, half-split stability, the
           UNFILLABLE differential check, Rule 0, decision rules 1-3.
           Arm A reference on the in-house tape, same instrument.

Run:
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_outcomes.py pull
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_outcomes.py metrics
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.machinery import SourceFileLoader
from zoneinfo import ZoneInfo

import db_dtypes  # noqa: F401
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SP = SourceFileLoader("sp", os.path.join(
    HERE, "2026-08-20_liquid_universe_screen_phase.py")).load_module()
CP = SourceFileLoader("cp", os.path.join(
    HERE, "2026-08-20_liquid_universe_compute.py")).load_module()
ET = ZoneInfo("America/New_York")
CACHE = SP.CACHE
BARS_PQ = os.path.join(CACHE, "lu_outcome_bars.parquet")
LEGS_PQ = os.path.join(CACHE, "lu_outcome_legs.parquet")

SLIP = 0.02
FILL_LO, FILL_HI, FILL_AT = 9 * 60 + 55, 10 * 60 + 15, 10 * 60
EXIT_MIN = 15 * 60 + 45
TRADEABLE_MIN_PRINTS = 11
N_BOOT, SEED, CI = 5000, 42, 90
M_DRAWS = CP.M_DRAWS


def legs_needed() -> pd.DataFrame:
    a = pd.read_parquet(CP.ARMS_PQ)
    a = a[a.contract.notna()].copy()
    a["session"] = pd.to_datetime(a.session).dt.date
    a["entry_day"] = [CP.next_td(d) for d in a.session]
    a["exit_day"] = [CP.next_td(d, 3) for d in a.session]
    return a


# ------------------------------------------------------------------ pull
def cmd_pull():
    key = SP.polygon_key()
    a = legs_needed()
    uniq = a.drop_duplicates(["session", "contract"])[
        ["session", "contract", "entry_day", "exit_day"]]
    have = set()
    frames = []
    if os.path.exists(BARS_PQ):
        old = pd.read_parquet(BARS_PQ)
        old["session"] = pd.to_datetime(old.session).dt.date
        have = set(zip(old.session, old.contract))
        frames.append(old)
    todo = [r for r in uniq.itertuples() if (r.session, r.contract) not in have]
    print(f"pull: {len(uniq)} unique legs, cached {len(have)}, todo {len(todo)}",
          flush=True)

    def one(r):
        j = SP.get_json(
            f"https://api.polygon.io/v2/aggs/ticker/{r.contract}/range/1/minute/"
            f"{r.entry_day}/{r.exit_day}",
            {"adjusted": "true", "limit": 50000, "apiKey": key})
        if j is None:
            return None
        rows = [{"session": r.session, "contract": r.contract, "t": b["t"],
                 "open": b["o"], "high": b["h"], "low": b["l"],
                 "close": b["c"], "volume": b["v"]}
                for b in (j.get("results") or [])]
        return pd.DataFrame(rows) if rows else pd.DataFrame(
            [{"session": r.session, "contract": r.contract, "t": np.nan,
              "open": np.nan, "high": np.nan, "low": np.nan, "close": np.nan,
              "volume": np.nan}])  # NO_BARS marker row

    failed = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, f in enumerate(as_completed([ex.submit(one, r) for r in todo]), 1):
            df = f.result()
            if df is None:
                failed += 1
            else:
                frames.append(df)
            if i % 500 == 0:
                print(f"  {i}/{len(todo)} legs, failed {failed}", flush=True)
    allb = pd.concat(frames, ignore_index=True)
    allb.to_parquet(BARS_PQ)
    print(f"pull done: failed {failed} (count what answered), bars"
          f" {int(allb.t.notna().sum())}, legs {len(allb.drop_duplicates(['session', 'contract']))}")


# ------------------------------------------------------------------ per-leg
def leg_metrics(bars: pd.DataFrame, entry_day: dt.date, exit_day: dt.date) -> dict:
    """bars: one (session, contract) leg. Returns fill + MFE/MAE + prints."""
    out = {"fillable": False, "prints_by_1000": 0}
    b = bars[bars.t.notna()].copy()
    if b.empty:
        return out
    ts = pd.to_datetime(b.t, unit="ms", utc=True).dt.tz_convert(ET)
    b["d"] = ts.dt.date
    b["m"] = ts.dt.hour * 60 + ts.dt.minute
    b = b[(b.m >= 9 * 60 + 30) & (b.m <= 16 * 60)]  # regular session only
    e = b[b.d == entry_day]
    out["prints_by_1000"] = int((e.m <= FILL_AT).sum())
    win = e[(e.m >= FILL_LO) & (e.m <= FILL_HI)]
    if win.empty:
        return out
    k = (win.m - FILL_AT).abs()
    fb = win.loc[k[k == k.min()].index[-1]]  # nearest to 10:00, later on ties
    fill = float(fb.close) * (1 + SLIP)
    if fill <= 0:
        return out
    out["fillable"], out["fill"] = True, fill
    after_sd = e[(e.m > fb.m) & (e.m <= EXIT_MIN)]
    out["mfe_sd"] = (after_sd.high.max() - fill) / fill if len(after_sd) else 0.0
    out["mae_sd"] = (after_sd.low.min() - fill) / fill if len(after_sd) else 0.0
    after_3d = b[((b.d == entry_day) & (b.m > fb.m)) |
                 ((b.d > entry_day) & (b.d <= exit_day))]
    out["mfe_3d"] = (after_3d.high.max() - fill) / fill if len(after_3d) else 0.0
    out["mae_3d"] = (after_3d.low.min() - fill) / fill if len(after_3d) else 0.0
    return out


def wmedian(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    if len(x) == 0:
        return np.nan
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return x[o][np.searchsorted(cw, 0.5 * cw[-1])]


def boot_diff(B: pd.DataFrame, C: pd.DataFrame, col: str, rng) -> tuple:
    """Paired-by-day block bootstrap of median_B - wmedian_C."""
    days = sorted(set(B.session))
    b_by = {d: g[col].to_numpy() for d, g in B.groupby("session")}
    c_by = {d: (g[col].to_numpy(), g.w.to_numpy()) for d, g in C.groupby("session")}
    point = np.median(B[col]) - wmedian(C[col], C.w)
    stats = []
    for _ in range(N_BOOT):
        pick = rng.choice(days, len(days), replace=True)
        bx = np.concatenate([b_by[d] for d in pick if d in b_by])
        cx = np.concatenate([c_by[d][0] for d in pick if d in c_by])
        cw = np.concatenate([c_by[d][1] for d in pick if d in c_by])
        stats.append(np.median(bx) - wmedian(cx, cw))
    lo, hi = np.percentile(stats, [(100 - CI) / 2, 100 - (100 - CI) / 2])
    return point, lo, hi


# ------------------------------------------------------------------ metrics
def cmd_metrics():
    a = legs_needed()
    bars = pd.read_parquet(BARS_PQ)
    bars["session"] = pd.to_datetime(bars.session).dt.date
    per = {}
    for (s, c), g in bars.groupby(["session", "contract"]):
        row = a[(a.session == s) & (a.contract == c)].iloc[0]
        per[(s, c)] = leg_metrics(g, row.entry_day, row.exit_day)
    m = pd.DataFrame([{"session": s, "contract": c, **v} for (s, c), v in per.items()])
    legs = a.merge(m, on=["session", "contract"], how="left")
    legs["fillable"] = legs.fillable.fillna(False).astype(bool)
    legs["w"] = np.where(legs.arm == "C", 1.0 / M_DRAWS, 1.0)
    legs.to_parquet(LEGS_PQ)

    B, C = legs[legs.arm == "B"], legs[legs.arm == "C"]
    print("ARM B / ARM C  (decision cell N=100, z>=2.0, earnings rail not"
          " applied, VIX rail applied)")
    for name, X in (("B", B), ("C (unique legs)", C.drop_duplicates(["session", "contract"]))):
        print(f"  {name:<16} legs {len(X):>6} | UNFILLABLE"
              f" {(~X.fillable).mean() * 100:5.1f}% | tradeable (11+ prints)"
              f" {(X.prints_by_1000 >= TRADEABLE_MIN_PRINTS).mean() * 100:5.1f}%"
              f" | no bars at all {int(X.prints_by_1000.isna().sum()) if 'prints_by_1000' in X else 0}")
    Bf, Cf = B[B.fillable], C[C.fillable]
    days_ok = Bf.session.nunique()
    r0 = len(Bf) >= 150 and days_ok >= 30
    print(f"\nRULE 0: fillable B legs {len(Bf)} (>=150) on {days_ok} days (>=30):"
          f" {'PASS' if r0 else 'FAIL -> INSUFFICIENT SAMPLE, no signal claim'}")
    rate_b, rate_c = (~B.fillable).mean(), (~C.drop_duplicates(['session', 'contract']).fillable).mean()
    diff_excl = abs(rate_b - rate_c) * 100

    rng = np.random.default_rng(SEED)
    print(f"\nPRIMARY  same-day median MFE, B minus C, paired-by-day block"
          f" bootstrap {N_BOOT} x, {CI}% CI")
    for col, label in (("mfe_sd", "same-day MFE (PRIMARY)"), ("mae_sd", "same-day MAE"),
                       ("mfe_3d", "3-day MFE (secondary)"), ("mae_3d", "3-day MAE (secondary)")):
        pt, lo, hi = boot_diff(Bf, Cf, col, rng)
        print(f"  {label:<24} B {np.median(Bf[col]) * 100:6.1f}%  C"
              f" {wmedian(Cf[col], Cf.w) * 100:6.1f}%  diff {pt * 100:6.1f}pp"
              f"  CI [{lo * 100:.1f}, {hi * 100:.1f}]")
    # Stability: first half vs second half of days.
    days = sorted(set(Bf.session))
    half = days[len(days) // 2]
    for tag, sel in (("first half", lambda x: x.session < half),
                     ("second half", lambda x: x.session >= half)):
        b1, c1 = Bf[sel(Bf)], Cf[sel(Cf)]
        if len(b1) and len(c1):
            pt, lo, hi = boot_diff(b1, c1, "mfe_sd", rng)
            print(f"  stability {tag:<12} B {np.median(b1.mfe_sd) * 100:6.1f}%  C"
                  f" {wmedian(c1.mfe_sd, c1.w) * 100:6.1f}%  diff {pt * 100:6.1f}pp"
                  f"  CI [{lo * 100:.1f}, {hi * 100:.1f}]  (B legs {len(b1)})")
    print(f"\nUNFILLABLE differential: B {rate_b * 100:.1f}% vs C {rate_c * 100:.1f}%"
          f" ({diff_excl:.1f} pts)")
    if diff_excl > 10:
        B0, C0 = B.copy(), C.copy()
        for X in (B0, C0):
            X.loc[~X.fillable, "mfe_sd"] = 0.0
        pt, lo, hi = boot_diff(B0, C0, "mfe_sd", rng)
        print(f"  SENSITIVITY (UNFILLABLE scored MFE=0): diff {pt * 100:.1f}pp"
              f"  CI [{lo * 100:.1f}, {hi * 100:.1f}]")
    # Decision rule readout on the primary.
    pt, lo, hi = boot_diff(Bf, Cf, "mfe_sd", np.random.default_rng(SEED))
    if not r0:
        verdict = "INSUFFICIENT SAMPLE (Rule 0)"
    elif lo > 0:
        verdict = "RULE 1: B > C, CI excludes zero -> signal PROMISING, forward-validate"
    elif hi < 0:
        verdict = "RULE 3: B < C, CI excludes zero -> anti-selective, do not ship"
    else:
        verdict = "RULE 2: B ~ C, CI includes zero -> unproven at ~5pp detectable size"
    print(f"\nDECISION (same-day median MFE, B-C = {pt * 100:.1f}pp,"
          f" CI [{lo * 100:.1f}, {hi * 100:.1f}]): {verdict}")
    print("  Power: detects ~5pp, cannot detect 1-2pp. A null means 'no large"
          " edge', never 'no edge'.")
    arm_a_reference()


def arm_a_reference():
    """Arm A on the in-house tape, same instrument and window."""
    from google.cloud import bigquery
    sd = SP.s1_scan_days()
    df = bigquery.Client(project=SP.PROJECT).query(f"""
      SELECT p.scan_date AS session, p.recommended_contract AS contract,
             UNIX_MILLIS(t.ts) AS t, t.open, t.high, t.low, t.close, t.volume
      FROM `{SP.PROJECT}.profit_scout.enriched_option_outcomes` p
      JOIN `{SP.PROJECT}.profit_scout.option_minute_paths` t
        ON t.scan_date = p.scan_date AND t.contract = p.recommended_contract
      WHERE p.scan_date BETWEEN '{sd[0]}' AND '{sd[-1]}'""").to_dataframe()
    df["session"] = pd.to_datetime(df.session).dt.date
    rows = []
    for (s, c), g in df.groupby(["session", "contract"]):
        rows.append({"session": s, "contract": c,
                     **leg_metrics(g, CP.next_td(s), CP.next_td(s, 3))})
    A = pd.DataFrame(rows)
    Af = A[A.fillable]
    print(f"\nARM A reference (production pool, in-house tape, same window,"
          f" same instrument): legs with tape {len(A)} | UNFILLABLE"
          f" {(~A.fillable).mean() * 100:.1f}% | tradeable"
          f" {(A.prints_by_1000 >= TRADEABLE_MIN_PRINTS).mean() * 100:.1f}%")
    print(f"  same-day median MFE {np.median(Af.mfe_sd) * 100:.1f}% | MAE"
          f" {np.median(Af.mae_sd) * 100:.1f}% | 3-day MFE"
          f" {np.median(Af.mfe_3d) * 100:.1f}%  (reference only, not a"
          " decision input; VIX-rail days included)")


if __name__ == "__main__":
    {"pull": cmd_pull, "metrics": cmd_metrics}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
