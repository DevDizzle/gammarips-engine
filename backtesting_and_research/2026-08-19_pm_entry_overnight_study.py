"""PM-entry / morning-pop study (READ-ONLY research, 2026-08-19).

Owner question: is it better to enter in the AFTERNOON and catch the next
MORNING pop, than to enter in the morning?

The live policy (V7.1 GIGO) enters 10:00 ET on day-1 and is flat 15:45 ET the
SAME day. The challenger enters 15:45 ET on day-1, holds overnight, and exits
on day-2 morning. Both cadences are one trade per day, so capital velocity is
approximately equal and the V7 velocity lever does NOT decide this comparison.
It is a pure EV + tail comparison.

Substrate: `profit_scout.option_minute_paths` — realized minute bars for the
ENRICHED POOL (day_index 1/2/3, regular session only). This is post-entry
label data behind the leakage wall. It is used here for outcome replay only,
never as a feature.

Conventions copied from production (forward-paper-trader/main.py):
  * entry fill = bar close * (1 + 2% slippage); every exit pays 2% the other way
  * conservative intrabar order: TIMEOUT > STOP > TARGET
  * bracket +40% / -30% on option premium
Gap handling (the honest part, and the whole point of an overnight hold):
  options do NOT trade overnight, so a stop CANNOT execute in the gap. On the
  first bar of a new session the stop fills at the OPEN when the open is
  already through it (gap-through), while the target is capped at the limit
  price. That is deliberately conservative against the challenger; a symmetric
  variant is reported alongside so the asymmetry is visible.

Head-to-head is restricted to the INTERSECTION set — legs fillable under both
rules — so a thinner 15:45 tape cannot flatter the challenger by dropping the
illiquid names.

Run:
    .venv/bin/python backtesting_and_research/2026-08-19_pm_entry_overnight_study.py
"""

import db_dtypes  # noqa: F401 - registers the BQ DATE dtype used by the parquet cache
import os
import re
import sys
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ET = ZoneInfo("America/New_York")
PROJECT = "profitscout-fida8"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "pm_entry_minute_paths.parquet")
PICKS_CACHE = os.path.join(HERE, "cache", "pm_entry_picks.parquet")

SLIP = 0.02
TARGET_PCT = 0.40
STOP_PCT = 0.30
FILL_TOL_MIN = 15          # symmetric fill tolerance for every entry anchor
N_BOOT = 10000
RNG = np.random.default_rng(7)

OCC_RE = re.compile(r"^O:([A-Z]+)(\d{6})([CP])(\d{8})$")


# ---------------------------------------------------------------- data load
def load_bars() -> pd.DataFrame:
    if os.path.exists(CACHE):
        return pd.read_parquet(CACHE)
    from google.cloud import bigquery

    sql = f"""
    SELECT scan_date, entry_day, contract, ticker, ts, bar_date, day_index,
           open, high, low, close, volume
    FROM `{PROJECT}.profit_scout.option_minute_paths`
    WHERE close IS NOT NULL AND close > 0
    """
    df = bigquery.Client(project=PROJECT).query(sql).to_dataframe()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    df.to_parquet(CACHE)
    return df


def load_picks() -> pd.DataFrame:
    if os.path.exists(PICKS_CACHE):
        return pd.read_parquet(PICKS_CACHE)
    from google.cloud import bigquery

    sql = f"""
    SELECT scan_date, recommended_contract AS contract, policy_version,
           realized_return_pct, exit_reason
    FROM `{PROJECT}.profit_scout.forward_paper_ledger`
    WHERE scan_date >= '2026-04-10' AND is_skipped IS NOT TRUE
    """
    df = bigquery.Client(project=PROJECT).query(sql).to_dataframe()
    os.makedirs(os.path.dirname(PICKS_CACHE), exist_ok=True)
    df.to_parquet(PICKS_CACHE)
    return df


def contract_expiry(sym: str):
    m = OCC_RE.match(sym)
    if not m:
        return None
    return datetime.strptime(m.group(2), "%y%m%d").date()


# ------------------------------------------------------------ replay engine
def _minutes_et(ts_series) -> np.ndarray:
    """Minutes since midnight ET for a tz-aware timestamp series."""
    local = ts_series.dt.tz_convert(ET)
    return (local.dt.hour * 60 + local.dt.minute).to_numpy()


def anchor_index(day: dict, hhmm: str, tol: int = FILL_TOL_MIN):
    """Index of the first bar at-or-after hhmm, within `tol` minutes. Else None."""
    want = int(hhmm[:2]) * 60 + int(hhmm[3:])
    mins = day["min"]
    idx = np.searchsorted(mins, want, side="left")
    if idx >= len(mins):
        return None
    if mins[idx] - want > tol:
        return None
    return int(idx)


def walk(days, entry_day_idx, entry_bar_idx, base, timeout_day_idx, timeout_hhmm,
         target_pct=TARGET_PCT, stop_pct=STOP_PCT, favorable_gap=False):
    """Walk bars from just after the entry bar to the timeout.

    `days` maps day_index -> dict of numpy arrays. Returns (net_return, reason)
    or None when the tape cannot support the walk.

    STALE-EXIT RULE (2026-08-19): the timeout must fill on a bar that actually
    PRINTED within FILL_TOL_MIN of the exit time on the timeout day. The first
    version of this study carried the last seen close forward, which invented a
    near-flat exit (slippage only) for every illiquid leg and silently flattered
    whichever arm held the thinner tape. A leg with no print near its exit time
    is UNFILLABLE, not flat.
    """
    target = base * (1 + target_pct) if target_pct is not None else None
    stop = base * (1 - stop_pct) if stop_pct is not None else None
    timeout_min = int(timeout_hhmm[:2]) * 60 + int(timeout_hhmm[3:])

    tday = days.get(timeout_day_idx)
    if tday is None:
        return None
    t_idx = anchor_index(tday, timeout_hhmm)
    if t_idx is None:
        return None  # no real print near the exit time — cannot exit here
    if timeout_day_idx == entry_day_idx and t_idx <= entry_bar_idx:
        return None  # exit anchor is not after the entry

    for di in range(entry_day_idx, timeout_day_idx + 1):
        day = days[di] if di in days else None
        if day is None:
            return None  # missing a session we must hold through
        start = entry_bar_idx + 1 if di == entry_day_idx else 0
        stop_at = t_idx if di == timeout_day_idx else len(day["min"])
        first_bar_of_new_day = di != entry_day_idx
        for j in range(start, stop_at):
            o, h, lo, c = day["open"][j], day["high"][j], day["low"][j], day["close"][j]
            gap_bar = first_bar_of_new_day and j == 0
            # STOP before TARGET (conservative), gap-aware on a session open.
            if stop is not None and lo <= stop:
                fill = min(o, stop) if gap_bar else stop
                return (fill * (1 - SLIP) - base) / base, "STOP"
            if target is not None and h >= target:
                fill = (max(o, target) if favorable_gap else target) if gap_bar else target
                return (fill * (1 - SLIP) - base) / base, "TARGET"
        if di == timeout_day_idx:
            # The timeout bar itself: honour the bracket inside it, else fill.
            o, h, lo, c = (tday["open"][t_idx], tday["high"][t_idx],
                           tday["low"][t_idx], tday["close"][t_idx])
            gap_bar = first_bar_of_new_day and t_idx == 0
            if stop is not None and lo <= stop:
                fill = min(o, stop) if gap_bar else stop
                return (fill * (1 - SLIP) - base) / base, "STOP"
            if target is not None and h >= target:
                fill = (max(o, target) if favorable_gap else target) if gap_bar else target
                return (fill * (1 - SLIP) - base) / base, "TARGET"
            return (c * (1 - SLIP) - base) / base, "TIMEOUT"
    return None


def build_legs(bars: pd.DataFrame):
    """Group the tape into per-leg, per-day numpy arrays sorted by time."""
    bars = bars.sort_values(["scan_date", "contract", "ts"])
    bars["min_et"] = _minutes_et(bars["ts"])
    legs = {}
    for (scan_date, contract), g in bars.groupby(["scan_date", "contract"], sort=False):
        days = {}
        for di, gd in g.groupby("day_index", sort=True):
            days[int(di)] = {
                "min": gd["min_et"].to_numpy(),
                "open": gd["open"].to_numpy(dtype=float),
                "high": gd["high"].to_numpy(dtype=float),
                "low": gd["low"].to_numpy(dtype=float),
                "close": gd["close"].to_numpy(dtype=float),
            }
        legs[(scan_date, contract)] = {
            "days": days,
            "ticker": g["ticker"].iloc[0],
            "entry_day": g["entry_day"].iloc[0],
        }
    return legs


# ------------------------------------------------------------------- arms
def run_arms(legs, favorable_gap=False):
    rows = []
    for (scan_date, contract), leg in legs.items():
        days = leg["days"]
        exp = contract_expiry(contract)
        d1 = days.get(1)
        rec = {
            "scan_date": scan_date,
            "contract": contract,
            "ticker": leg["ticker"],
            "entry_day": leg["entry_day"],
            "expiry": exp,
            "expires_d1": (exp is not None and exp == leg["entry_day"]),
            "has_d2": 2 in days,
        }
        if d1 is None:
            rows.append(rec)
            continue

        i_am = anchor_index(d1, "10:00")
        i_pm = anchor_index(d1, "15:45")
        rec["fill_am"] = i_am is not None
        rec["fill_pm"] = i_pm is not None

        # ---- Arm A: LIVE V7.1 — enter 10:00 d1, bracket, flat 15:45 d1.
        if i_am is not None:
            base = d1["close"][i_am] * (1 + SLIP)
            rec["px_am_entry"] = base
            out = walk(days, 1, i_am, base, 1, "15:45", favorable_gap=favorable_gap)
            if out:
                rec["A_am_same_day"], rec["A_reason"] = out

        # ---- PM arms: enter 15:45 d1, hold overnight, exit d2 at various times.
        # The bracket is live from the moment of entry (15:45-16:00 d1 included)
        # but cannot execute in the overnight gap.
        if i_pm is not None and 2 in days:
            base_pm = d1["close"][i_pm] * (1 + SLIP)
            rec["px_pm_entry"] = base_pm
            for label, hhmm in [("0935", "09:35"), ("1000", "10:00"),
                                ("1030", "10:30"), ("1100", "11:00"),
                                ("1200", "12:00"), ("1545", "15:45")]:
                out = walk(days, 1, i_pm, base_pm, 2, hhmm, favorable_gap=favorable_gap)
                if out:
                    rec[f"B_pm_to_{label}"], rec[f"B_reason_{label}"] = out

        # ---- Arm C (control): enter 10:00 d1 but hold to d2 10:00.
        # Separates "PM entry" from "overnight hold".
        if i_am is not None and 2 in days:
            base = d1["close"][i_am] * (1 + SLIP)
            out = walk(days, 1, i_am, base, 2, "10:00", favorable_gap=favorable_gap)
            if out:
                rec["C_am_to_d2_1000"], rec["C_reason"] = out

        # ---- Raw decomposition, no bracket, no slippage (diagnostic only).
        # Every leg of the decomposition needs a REAL print at both ends.
        # d2["open"][0] is the first print of day-2, whose median is 09:38 and
        # which is after 10:15 a quarter of the time — it is NOT an opening
        # price, so the gap is measured only against a genuine 09:30 anchor.
        if i_am is not None:
            j = anchor_index(d1, "15:45")
            if j is not None:
                rec["raw_d1_1000_1545"] = d1["close"][j] / d1["close"][i_am] - 1
        if i_pm is not None and 2 in days:
            d2 = days[2]
            p_pm = d1["close"][i_pm]
            i_open = anchor_index(d2, "09:30")
            k = anchor_index(d2, "10:00")
            if i_open is not None:
                rec["raw_gap_overnight"] = d2["close"][i_open] / p_pm - 1
            if k is not None:
                rec["raw_pm_to_d2_1000"] = d2["close"][k] / p_pm - 1
            if i_open is not None and k is not None:
                rec["raw_d2_open_to_1000"] = d2["close"][k] / d2["close"][i_open] - 1

        # ---- Liquidity descriptors (the tape is thin; tier the results).
        rec["bars_d1"] = len(d1["min"])
        rec["bars_d2"] = len(days[2]["min"]) if 2 in days else 0
        rec["premium_d1"] = float(np.median(d1["close"]))
        rows.append(rec)
    return pd.DataFrame(rows)


# --------------------------------------------------------------- statistics
def cluster_bootstrap(df, col, by="scan_date", n=N_BOOT):
    """Day-clustered bootstrap mean + 90% CI. Effective N is DAYS, not rows."""
    groups = [g[col].to_numpy() for _, g in df.groupby(by) if g[col].notna().any()]
    groups = [g[~np.isnan(g)] for g in groups]
    groups = [g for g in groups if len(g)]
    if len(groups) < 3:
        return np.nan, np.nan, np.nan, 0
    obs = np.concatenate(groups).mean()
    k = len(groups)
    means = np.empty(n)
    for b in range(n):
        pick = RNG.integers(0, k, k)
        means[b] = np.concatenate([groups[i] for i in pick]).mean()
    return obs, float(np.percentile(means, 5)), float(np.percentile(means, 95)), k


def paired_bootstrap(df, col_a, col_b, by="scan_date", n=N_BOOT):
    """Day-clustered bootstrap of the PAIRED difference (b - a) on legs with both."""
    sub = df[df[col_a].notna() & df[col_b].notna()].copy()
    sub["_d"] = sub[col_b] - sub[col_a]
    return cluster_bootstrap(sub, "_d", by=by, n=n), len(sub)


def describe(s: pd.Series) -> dict:
    s = s.dropna()
    if not len(s):
        return {}
    return {
        "n": len(s),
        "mean": s.mean(),
        "median": s.median(),
        "win%": (s > 0).mean(),
        "p05": s.quantile(0.05),
        "p95": s.quantile(0.95),
        "min": s.min(),
        "worse_than_-30%": (s < -0.30).mean(),
    }


def pct(x, d=2):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:+.{d}f}%"


# -------------------------------------------------------------------- main
def main():
    bars = load_bars()
    print(f"tape: {len(bars):,} bars  "
          f"{bars['scan_date'].min()} .. {bars['scan_date'].max()}", flush=True)
    legs = build_legs(bars)
    print(f"legs: {len(legs):,}", flush=True)

    res = run_arms(legs, favorable_gap=False)
    res_fav = run_arms(legs, favorable_gap=True)
    res.to_parquet(os.path.join(HERE, "cache", "pm_entry_results.parquet"))

    # --------------------------------------------------- fill availability
    print("\n" + "=" * 78)
    print("1. FILL AVAILABILITY  (can you even get in? tolerance = 15 min)")
    print("=" * 78)
    tot = len(res)
    print(f"  legs total                          {tot:>6,}")
    print(f"  printed bar within 15m of 10:00 ET  {int(res['fill_am'].sum()):>6,} "
          f"({res['fill_am'].mean()*100:.1f}%)")
    print(f"  printed bar within 15m of 15:45 ET  {int(res['fill_pm'].sum()):>6,} "
          f"({res['fill_pm'].mean()*100:.1f}%)")
    print(f"  has any day-2 tape                  {int(res['has_d2'].sum()):>6,} "
          f"({res['has_d2'].mean()*100:.1f}%)")
    print(f"  expires ON day-1 (cannot hold)      {int(res['expires_d1'].sum()):>6,} "
          f"({res['expires_d1'].mean()*100:.1f}%)")

    both = res[res["A_am_same_day"].notna() & res["B_pm_to_1000"].notna()]
    print(f"\n  INTERSECTION (both arms fillable)   {len(both):>6,} legs, "
          f"{both['scan_date'].nunique()} scan dates")

    # ------------------------------------------------------ decomposition
    print("\n" + "=" * 78)
    print("2. RAW DECOMPOSITION  (no bracket, no slippage — where does return live?)")
    print("=" * 78)
    print("  The mean is NOT the story here. On cheap contracts a single print at")
    print("  $0.01 against a later print at $0.21 reads as +2000%, so the mean of")
    print("  the morning leg is set by two penny options. Read the median and the")
    print("  liquid tier.")
    legs_rows = [("raw_d1_1000_1545", "day-1 10:00 -> 15:45 (AM session)"),
                 ("raw_gap_overnight", "day-1 15:45 -> day-2 09:30 (GAP)"),
                 ("raw_d2_open_to_1000", "day-2 09:30 -> 10:00 (morning pop)"),
                 ("raw_pm_to_d2_1000", "day-1 15:45 -> day-2 10:00 (PM tot)")]
    liq = res[(res.bars_d1 >= 120) & (res.bars_d2 >= 120) & (res.premium_d1 >= 1.00)]
    print(f"\n  {'leg':<36}{'n':>5}{'mean':>10}{'trim99':>9}{'median':>10}"
          f"{'win%':>7}{'  | LIQUID n':>13}{'mean':>9}{'median':>9}")
    for col, name in legs_rows:
        d, dl = describe(res[col]), describe(liq[col])
        if not d:
            continue
        s = res[col].dropna()
        trim = s.clip(upper=s.quantile(0.99), lower=s.quantile(0.01)).mean()
        print(f"  {name:<36}{d['n']:>5}{pct(d['mean']):>10}{pct(trim):>9}"
              f"{pct(d['median']):>10}{d['win%']*100:>6.1f}%"
              f"{dl.get('n', 0):>13}{pct(dl.get('mean')):>9}"
              f"{pct(dl.get('median')):>9}")

    # ------------------------------------------------------- bracket arms
    arms = [("A_am_same_day", "A. LIVE: 10:00 -> 15:45 d1"),
            ("B_pm_to_0935", "B. PM 15:45 -> d2 09:35"),
            ("B_pm_to_1000", "B. PM 15:45 -> d2 10:00"),
            ("B_pm_to_1030", "B. PM 15:45 -> d2 10:30"),
            ("B_pm_to_1100", "B. PM 15:45 -> d2 11:00"),
            ("B_pm_to_1200", "B. PM 15:45 -> d2 12:00"),
            ("B_pm_to_1545", "B. PM 15:45 -> d2 15:45"),
            ("C_am_to_d2_1000", "C. CTRL 10:00 d1 -> d2 10:00")]

    # The tape is thin (median 11 traded minutes on day-2, 73% single-print
    # bars). Tier the head-to-head so a conclusion cannot rest on contracts
    # nobody could actually trade.
    tiers = [
        ("ALL fillable", both),
        ("LIQUID  >=60 min/day, prem>=$0.50",
         both[(both.bars_d1 >= 60) & (both.bars_d2 >= 60) & (both.premium_d1 >= 0.50)]),
        ("DEEP    >=120 min/day, prem>=$1.00",
         both[(both.bars_d1 >= 120) & (both.bars_d2 >= 120) & (both.premium_d1 >= 1.00)]),
        # The two tiers above screen on day-2 bar count, which is NOT knowable at
        # entry — it conditions the sample on a future variable. The paired
        # difference stays valid (same legs, both arms) but the tier does not
        # describe a rule you could run forward. This last tier screens only on
        # day-1 liquidity, so it IS a decision rule the trader could apply.
        ("ENTRY-KNOWABLE  day-1 >=120 min, prem>=$1.00",
         both[(both.bars_d1 >= 120) & (both.premium_d1 >= 1.00)]),
    ]

    print("\n" + "=" * 78)
    print("3. BRACKETED ARMS  (+40%/-30%, 2% slip each way, real prints at both ends)")
    print("=" * 78)
    for tname, tdf in tiers:
        print(f"\n  -- {tname}  (n={len(tdf)} legs, {tdf['scan_date'].nunique()} days)")
        print(f"  {'arm':<30}{'n':>6}{'mean':>10}{'90% CI (day-clustered)':>26}"
              f"{'win%':>8}{'p05':>9}{'<-30%':>8}")
        for col, name in arms:
            sub = tdf[tdf[col].notna()]
            if len(sub) < 20:
                continue
            d = describe(sub[col])
            m, lo, hi, k = cluster_bootstrap(sub, col)
            ci = f"[{pct(lo,1)}, {pct(hi,1)}]"
            print(f"  {name:<30}{d['n']:>6}{pct(d['mean']):>10}{ci:>26}"
                  f"{d['win%']*100:>7.1f}%{pct(d['p05'],1):>9}"
                  f"{d['worse_than_-30%']*100:>7.1f}%")

    # ------------------------------------------------------------- paired
    print("\n" + "=" * 78)
    print("4. PAIRED DIFFERENCE vs the live arm  (challenger minus A, same legs)")
    print("=" * 78)
    for tname, tdf in tiers:
        print(f"\n  -- {tname}")
        print(f"  {'contrast':<30}{'n':>6}{'diff':>10}{'90% CI':>26}{'days':>7}  verdict")
        for col, name in arms[1:]:
            (m, lo, hi, k), n = paired_bootstrap(tdf, "A_am_same_day", col)
            if np.isnan(m) or n < 20:
                continue
            ci = f"[{pct(lo,1)}, {pct(hi,1)}]"
            verdict = "BETTER" if lo > 0 else ("WORSE" if hi < 0 else "no signal")
            print(f"  {name:<30}{n:>6}{pct(m):>10}{ci:>26}{k:>7}  {verdict}")

    # ------------------------------------------------- favorable-gap check
    print("\n" + "=" * 78)
    print("5. ROBUSTNESS — symmetric gap fills (target also fills at a gapped open)")
    print("=" * 78)
    bf = res_fav[res_fav["A_am_same_day"].notna() & res_fav["B_pm_to_1000"].notna()]
    for col, name in [("A_am_same_day", "A. LIVE 10:00 -> 15:45 d1"),
                      ("B_pm_to_1000", "B. PM 15:45 -> d2 10:00")]:
        d = describe(bf[col])
        print(f"  {name:<30}{d['n']:>6}{pct(d['mean']):>10}  win {d['win%']*100:.1f}%")
    (m, lo, hi, k), n = paired_bootstrap(bf, "A_am_same_day", "B_pm_to_1000")
    print(f"  paired diff  {pct(m)}  90% CI [{pct(lo,1)}, {pct(hi,1)}]  n={n}")

    # ----------------------------------------------------------- by month
    print("\n" + "=" * 78)
    print("6. STABILITY BY MONTH  (mean per-trade, intersection set)")
    print("=" * 78)
    both = both.copy()
    both["month"] = pd.to_datetime(both["scan_date"]).dt.to_period("M").astype(str)
    print(f"  {'month':<10}{'n':>6}{'A live':>11}{'B PM->10:00':>14}{'diff':>11}")
    for mth, g in both.groupby("month"):
        a, b = g["A_am_same_day"].mean(), g["B_pm_to_1000"].mean()
        print(f"  {mth:<10}{len(g):>6}{pct(a):>11}{pct(b):>14}{pct(b-a):>11}")

    # ------------------------------------------------------- exit reasons
    print("\n" + "=" * 78)
    print("7. EXIT MIX")
    print("=" * 78)
    for col, name in [("A_reason", "A. LIVE 10:00 -> 15:45 d1"),
                      ("B_reason_1000", "B. PM 15:45 -> d2 10:00")]:
        vc = both[col].value_counts(normalize=True)
        print(f"  {name:<30}" + "  ".join(f"{k} {v*100:.0f}%" for k, v in vc.items()))

    # -------------------------------------------------------- picks-only
    print("\n" + "=" * 78)
    print("8. TOURNAMENT PICKS ONLY  (the operator signal — small N, directional)")
    print("=" * 78)
    try:
        picks = load_picks()
        picks["scan_date"] = pd.to_datetime(picks["scan_date"]).dt.date
        res2 = res.copy()
        res2["scan_date"] = pd.to_datetime(res2["scan_date"]).dt.date
        pk = res2.merge(picks[["scan_date", "contract"]], on=["scan_date", "contract"],
                        how="inner")
        pk = pk[pk["A_am_same_day"].notna() & pk["B_pm_to_1000"].notna()]
        print(f"  matched picks with both arms fillable: {len(pk)}")
        if len(pk) >= 5:
            for col, name in [("A_am_same_day", "A. LIVE 10:00 -> 15:45 d1"),
                              ("B_pm_to_1000", "B. PM 15:45 -> d2 10:00"),
                              ("B_pm_to_1545", "B. PM 15:45 -> d2 15:45")]:
                d = describe(pk[col])
                print(f"  {name:<30}{d['n']:>4}  mean {pct(d['mean'])}  "
                      f"median {pct(d['median'])}  win {d['win%']*100:.0f}%  "
                      f"min {pct(d['min'],0)}")
    except Exception as e:  # noqa: BLE001 — diagnostic block, never fatal
        print(f"  picks join skipped: {e}")

    print("\ndone.")


if __name__ == "__main__":
    sys.exit(main())
