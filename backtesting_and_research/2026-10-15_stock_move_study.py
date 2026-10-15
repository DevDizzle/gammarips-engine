#!/usr/bin/env python3
"""2026-10-15 stock-move study. READ-ONLY against BigQuery (reads the parquet extracts only).

Binding plan: docs/research_reports/FINDINGS_LEDGER.md, section
"2026-10-15 (stock-move study) PRE-REGISTRATION". This script implements that section and
nothing else. It writes result files into backtesting_and_research/cache/stockmove/
(gitignored) and prints the tables.

Inputs (made by 2026-10-15_extract_bq.py and 2026-10-15_fetch_grouped_bars.py):
  cache/stockmove/overnight_signals.parquet, polygon_iv_history.parquet,
  pool_membership.parquet, vixcls.csv, bars/YYYY-MM-DD.parquet

Usage:
  env -u PROJECT_ID .venv/bin/python backtesting_and_research/2026-10-15_stock_move_study.py
  ... --holdout      # the ONE-TIME live-universe read, run only after the wide-era verdict is in the ledger
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats
from sklearn.linear_model import LogisticRegression, Ridge

warnings.filterwarnings("ignore")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, "backtesting_and_research", "cache", "stockmove")

WIDE_START, WIDE_END = "2026-03-02", "2026-08-21"
HOLD_START, HOLD_END = "2026-09-01", "2026-10-13"
OOS_MONTHS = [5, 6, 7, 8]
MIN_TICKERS_PER_DATE = 7000
CLIP = 0.20
HIT = 0.01

FEATURES = [
    "pc_dollar_share", "call_vol_oi_ratio", "put_vol_oi_ratio", "opt_to_stock",
    "call_uoa_depth", "put_uoa_depth", "call_active_strikes", "put_active_strikes",
    "price_change_pct", "recommended_iv", "cluster_size", "overnight_score", "contract_score",
    "direction", "in_pool", "log_dollar_volume", "log_price",
    "ret_1d_bar", "ret_5d", "ret_20d", "overnight_gap", "intraday", "rvol_20", "vol_surprise",
    "dist_20d_high", "dist_52w_high", "range_pct",
    "atm_iv_30d", "iv_chg_5d", "iv_minus_rvol",
]
assert len(FEATURES) == 30
DAY_LEVEL = ["vix_level", "vix_chg_5d"]
TOP_SECTORS = 10

LGB_PARAMS = dict(objective="regression", num_leaves=15, learning_rate=0.05, n_estimators=300,
                  min_child_samples=200, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                  reg_lambda=1.0, random_state=42, verbose=-1, n_jobs=4)


def log(msg: str) -> None:
    print(msg, flush=True)


def read_pq(name: str) -> pd.DataFrame:
    """Read a BigQuery extract. ignore_metadata drops the dbdate extension type pandas cannot parse."""
    return pq.read_table(os.path.join(CACHE, name)).to_pandas(ignore_metadata=True)


# ----------------------------------------------------------------------------- data
def load_bars(tickers: set[str]) -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(CACHE, "bars", "*.parquet")))
    parts = []
    for f in files:
        df = pd.read_parquet(f)
        if len(df) < MIN_TICKERS_PER_DATE:
            raise SystemExit(f"OUTAGE in cached bars {os.path.basename(f)}: {len(df)} tickers")
        parts.append(df[df["ticker"].isin(tickers)])
    bars = pd.concat(parts, ignore_index=True)
    bars["date"] = pd.to_datetime(bars["date"]).astype("datetime64[ns]")
    bad = int(((bars["open"] <= 0) | (bars["close"] <= 0)).sum())
    log(f"bars: rows with open <= 0 or close <= 0 (dropped): {bad:,}")
    bars = bars[(bars["open"] > 0) & (bars["close"] > 0)]
    # a ticker that appears twice on one date is a symbol collision in the grouped feed; drop it outright
    collided = sorted(bars.loc[bars.duplicated(["date", "ticker"], keep=False), "ticker"].unique())
    if collided:
        log(f"bars: dropped {len(collided)} tickers with duplicate rows per date (symbol collision): {collided}")
        bars = bars[~bars["ticker"].isin(collided)]
    log(f"bars: {len(files)} sessions {os.path.basename(files[0])[:10]} .. {os.path.basename(files[-1])[:10]}, "
        f"{len(bars):,} rows for {bars['ticker'].nunique():,} scan tickers")
    return bars


def bar_features(bars: pd.DataFrame) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    w = {c: bars.pivot(index="date", columns="ticker", values=c).sort_index()
         for c in ["open", "high", "low", "close", "volume"]}
    o, h, l, c, v = w["open"], w["high"], w["low"], w["close"], w["volume"]
    lr = np.log(c / c.shift(1))
    f = {
        "ret_1d_bar": c / c.shift(1) - 1,
        "ret_5d": c / c.shift(5) - 1,
        "ret_20d": c / c.shift(20) - 1,
        "overnight_gap": o / c.shift(1) - 1,
        "intraday": c / o - 1,
        "rvol_20": lr.rolling(20, min_periods=15).std() * np.sqrt(252),
        "vol_surprise": v / v.shift(1).rolling(20, min_periods=15).mean(),
        "dist_20d_high": c / h.rolling(20, min_periods=15).max() - 1,
        "dist_52w_high": c / h.rolling(252, min_periods=120).max() - 1,
        "range_pct": (h - l) / c,
        # forward: entry at the open of the next session, exit at the close two sessions later
        "fwd_open1": o.shift(-1),
        "fwd_close3": c.shift(-3),
        "close0": c,
    }
    # the pivot index must be the exact NYSE session calendar, or shift(-1)/shift(-3) would skip sessions
    import pandas_market_calendars as mcal
    expect = mcal.get_calendar("NYSE").schedule(start_date=c.index[0], end_date=c.index[-1]).index.normalize()
    missing = expect.difference(c.index)
    extra = c.index.difference(expect)
    if len(missing) or len(extra):
        raise SystemExit(f"bar calendar mismatch: missing {list(missing)[:5]} extra {list(extra)[:5]}")
    long = pd.concat({k: v.stack() for k, v in f.items()}, axis=1)
    long.index.names = ["day0", "ticker"]
    return long.reset_index(), c.index


def build(holdout: bool, sector_top: list | None = None) -> pd.DataFrame:
    scan = read_pq("overnight_signals.parquet")
    scan["scan_day"] = pd.to_datetime(scan["scan_day"]).astype("datetime64[ns]")
    scan["scan_date"] = pd.to_datetime(scan["scan_date"]).astype("datetime64[ns]")
    lo, hi = (HOLD_START, HOLD_END) if holdout else (WIDE_START, WIDE_END)
    scan = scan[(scan["scan_day"] >= lo) & (scan["scan_day"] <= hi)].copy()
    n0 = len(scan)
    scan = scan.sort_values("inserted_at").drop_duplicates(["scan_day", "ticker"], keep="last")
    log(f"scan rows {lo}..{hi}: {n0:,} -> {len(scan):,} after dedup on (scan_day, ticker); "
        f"{scan['scan_day'].nunique()} scan days; label-shift rows (scan_date != scan_day): "
        f"{int((scan['scan_date'] != scan['scan_day']).sum()):,}")

    bars = load_bars(set(scan["ticker"]))
    feats, sessions = bar_features(bars)

    # day0 = last session <= scan_day
    idx = np.searchsorted(sessions.values, scan["scan_day"].values, side="right") - 1
    scan["day0"] = pd.to_datetime(sessions.values[idx]).astype("datetime64[ns]")
    log(f"scan days that are not NYSE sessions: {int((scan['day0'] != scan['scan_day']).sum()):,} rows")
    df = scan.merge(feats, on=["day0", "ticker"], how="left")
    no_bar = df["close0"].isna()
    log(f"rows with no bar on day0 (ticker not in grouped-daily): {int(no_bar.sum()):,}")
    df = df[~no_bar]

    # target
    df["r3"] = df["fwd_close3"] / df["fwd_open1"] - 1
    miss = df["r3"].isna()
    log(f"rows with no session-1 open or session-3 close yet: {int(miss.sum()):,}")
    df = df[~miss]
    extreme = df["r3"].abs() >= 1
    log(f"rows with |r3| >= 1 (dropped): {int(extreme.sum()):,}")
    df = df[~extreme].copy()
    df["r3w"] = df["r3"].clip(-CLIP, CLIP)
    df["y"] = (df["r3"] >= HIT).astype(int)

    # scan-row features
    pcv = df["put_dollar_volume"].fillna(0) + df["call_dollar_volume"].fillna(0)
    df["pc_dollar_share"] = np.where(pcv > 0, df["put_dollar_volume"].fillna(0) / pcv, np.nan)
    sv = df["day_volume"].astype(float) * df["underlying_price"]
    df["opt_to_stock"] = np.where(sv > 0, df["total_options_dollar_volume"] / sv, np.nan)
    df["log_dollar_volume"] = np.log(sv.where(sv > 0))
    df["log_price"] = np.log(df["underlying_price"].where(df["underlying_price"] > 0))
    df["direction"] = (df["direction"] == "BULLISH").astype(float)
    pool = read_pq("pool_membership.parquet")
    pool["scan_date"] = pd.to_datetime(pool["scan_date"]).astype("datetime64[ns]")
    pool["in_pool"] = 1.0
    df = df.merge(pool, on=["scan_date", "ticker"], how="left")
    df["in_pool"] = df["in_pool"].fillna(0.0)
    pool_start = pool["scan_date"].min()
    unknown = df["scan_date"] < pool_start
    df.loc[unknown, "in_pool"] = np.nan
    log(f"in_pool unknown before the enriched table starts ({pool_start.date()}): {int(unknown.sum()):,} rows set to missing")

    # IV history: latest as_of_date in [scan_day - 7d, scan_day]; 5 sessions back the same way
    iv = read_pq("polygon_iv_history.parquet")
    iv["as_of_date"] = pd.to_datetime(iv["as_of_date"]).astype("datetime64[ns]")
    iv = iv.dropna(subset=["atm_iv_30d"]).sort_values("as_of_date")
    pos = np.searchsorted(sessions.values, df["day0"].values)
    df["day_m5"] = pd.to_datetime(sessions.values[np.clip(pos - 5, 0, None)]).astype("datetime64[ns]")
    for col, key in [("atm_iv_30d", "scan_day"), ("iv_m5", "day_m5")]:
        tmp = df[["ticker", key]].copy().sort_values(key)
        m = pd.merge_asof(tmp, iv.rename(columns={"atm_iv_30d": col}), left_on=key, right_on="as_of_date",
                          by="ticker", direction="backward", tolerance=pd.Timedelta(days=7))
        df[col] = m.set_index(tmp.index)[col]
    df["iv_chg_5d"] = df["atm_iv_30d"] - df["iv_m5"]
    df["iv_minus_rvol"] = df["atm_iv_30d"] - df["rvol_20"]

    # VIX (FRED), latest close <= scan_day, and 5 sessions back
    vix = pd.read_csv(os.path.join(CACHE, "vixcls.csv"))
    vix.columns = ["date", "vix"]
    vix["date"] = pd.to_datetime(vix["date"]).astype("datetime64[ns]")
    vix = vix.dropna().sort_values("date")
    for col, key in [("vix_level", "scan_day"), ("vix_m5", "day_m5")]:
        tmp = df[[key]].copy().sort_values(key)
        m = pd.merge_asof(tmp, vix.rename(columns={"vix": col}), left_on=key, right_on="date", direction="backward")
        df[col] = m.set_index(tmp.index)[col]
    df["vix_chg_5d"] = df["vix_level"] - df["vix_m5"]

    # sector one-hot (model pass only)
    sec = df["sector"].fillna("").replace("", "BLANK")
    top = list(sec.value_counts().index[:TOP_SECTORS]) if sector_top is None else list(sector_top)
    df["sector_cat"] = np.where(sec.isin(top), sec, "OTHER_SECTOR")
    df.attrs["sector_top"] = top

    df["month"] = df["scan_day"].dt.month
    # within-day rank standardization to [-0.5, +0.5]
    g = df.groupby("scan_day")
    for feat in FEATURES:
        r = g[feat].rank(method="average")
        n = g[feat].transform("count")
        df[f"z_{feat}"] = (r - 0.5) / n - 0.5
    df["r3_rank"] = g["r3"].rank(method="average")
    log(f"final rows: {len(df):,} on {df['scan_day'].nunique()} scan days; "
        f"mean r3 {df['r3'].mean()*100:+.2f}%, hit(r3>=+1%) {df['y'].mean()*100:.1f}%")
    return df


# ----------------------------------------------------------------------------- metrics
def daily_metrics(df: pd.DataFrame, score: pd.Series, name: str) -> pd.DataFrame:
    """Per-day Spearman IC, top-decile excess (r3w, pts), top-decile hit-rate lift (pts), and the top-50 versions."""
    d = df[["scan_day", "r3", "r3w", "y"]].copy()
    d["s"] = score.values
    d = d.dropna(subset=["s"])
    rows = []
    for day, g in d.groupby("scan_day"):
        if len(g) < 30 or g["s"].nunique() < 2:
            continue
        ic = stats.spearmanr(g["s"], g["r3"]).correlation
        q = g["s"].quantile(0.9)
        top = g[g["s"] >= q]
        k50 = g["s"].nlargest(min(50, len(g))).iloc[-1]
        top50 = g[g["s"] >= k50]
        rows.append(dict(scan_day=day, n=len(g), ic=ic, k_top=len(top),
                         exc=(top["r3w"].mean() - g["r3w"].mean()) * 100,
                         hit=(top["y"].mean() - g["y"].mean()) * 100,
                         k50=len(top50),
                         exc50=(top50["r3w"].mean() - g["r3w"].mean()) * 100,
                         hit50=(top50["y"].mean() - g["y"].mean()) * 100))
    out = pd.DataFrame(rows)
    out["name"] = name
    return out


def tstat(x: pd.Series) -> float:
    x = x.dropna()
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 and x.std(ddof=1) > 0 else float("nan")


def tstat_hac(x: pd.Series, lags: int = 2) -> float:
    """Newey-West t of the mean (Bartlett weights). Consecutive scan days share 2 of 3 sessions."""
    v = x.dropna().to_numpy(dtype=float)
    n = len(v)
    if n < 5:
        return float("nan")
    e = v - v.mean()
    acc = float(np.sum(e * e))
    for L in range(1, lags + 1):
        acc += 2.0 * (1.0 - L / (lags + 1)) * float(np.sum(e[L:] * e[:-L]))
    se = np.sqrt(max(acc, 0.0)) / n
    return float(v.mean() / se) if se > 0 else float("nan")


def summarize(dm: pd.DataFrame, name: str, universe_n: pd.Series | None = None) -> dict:
    s = dict(name=name, days=int(len(dm)), mean_n=float(dm["n"].mean()))
    for col in ["ic", "exc", "hit", "exc50", "hit50"]:
        s[col] = float(dm[col].mean())
        s[f"t_{col}"] = tstat(dm[col])
    s["t_ic_hac"] = tstat_hac(dm.sort_values("scan_day")["ic"])
    s["t_exc_hac"] = tstat_hac(dm.sort_values("scan_day")["exc"])
    s["k_top"] = float(dm["k_top"].mean())
    if universe_n is not None:
        s["coverage"] = float((dm.set_index("scan_day")["n"] / universe_n.reindex(dm["scan_day"]).values).mean())
    return s


def bh(pvals: list[float], q: float = 0.10) -> list[bool]:
    p = np.array(pvals, dtype=float)
    finite = np.isfinite(p)
    m = int(finite.sum())
    if m == 0:
        return [False] * len(p)
    order = np.argsort(np.where(finite, p, np.inf))
    thresh = None
    for rank, i in enumerate(order[:m], start=1):
        if p[i] <= q * rank / m:
            thresh = p[i]
    if thresh is None:
        return [False] * len(p)
    return (finite & (p <= thresh)).tolist()


def p_from_t(t: float, n: int) -> float:
    return float(2 * stats.t.sf(abs(t), df=n - 1)) if np.isfinite(t) and n > 2 else float("nan")


# ----------------------------------------------------------------------------- passes
def single_feature_pass(df: pd.DataFrame, fit_months_all: bool) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    universe_n = df.groupby("scan_day").size()
    rows, pooled = [], {}
    for feat in FEATURES:
        z = df[f"z_{feat}"]
        dm_pos = daily_metrics(df, z, feat)
        dm_neg = daily_metrics(df, -z, feat)
        if dm_pos.empty:
            rows.append(dict(name=feat, days=0))
            continue
        dm_pos["month"] = dm_pos["scan_day"].dt.month
        dm_neg["month"] = dm_neg["scan_day"].dt.month
        parts, signs = [], []
        if fit_months_all:  # holdout: sign from the whole wide era, passed in via df attrs
            sign = df.attrs["signs"][feat]
            parts.append(dm_pos if sign > 0 else dm_neg)
            signs.append(sign)
        else:
            for M in OOS_MONTHS:
                fit = dm_pos[dm_pos["month"] < M]
                sign = 1 if fit["ic"].mean() >= 0 else -1
                signs.append(sign)
                src = dm_pos if sign > 0 else dm_neg
                parts.append(src[src["month"] == M])
        oos = pd.concat(parts, ignore_index=True)
        pooled[feat] = oos
        s = summarize(oos, feat, universe_n)
        s["signs"] = "".join("+" if x > 0 else "-" for x in signs)
        s["ic_all_days_raw"] = float(dm_pos["ic"].mean())
        s["t_ic_all_days_raw"] = tstat(dm_pos["ic"])
        rows.append(s)
    out = pd.DataFrame(rows)
    out["p_ic"] = [p_from_t(t, n) for t, n in zip(out["t_ic"], out["days"])]
    out["bh10"] = bh(out["p_ic"].tolist())
    return out, pooled


def design(df: pd.DataFrame, train_stats: dict | None = None) -> tuple[np.ndarray, dict]:
    X = df[[f"z_{f}" for f in FEATURES]].fillna(0.0).to_numpy()
    vix = df[DAY_LEVEL].to_numpy(dtype=float)
    if train_stats is None:
        train_stats = dict(mu=np.nanmean(vix, axis=0), sd=np.nanstd(vix, axis=0) + 1e-9,
                           cats=sorted(df["sector_cat"].unique()))
    vz = np.nan_to_num((vix - train_stats["mu"]) / train_stats["sd"])
    sec = np.stack([(df["sector_cat"] == c).to_numpy(dtype=float) for c in train_stats["cats"]], axis=1)
    return np.hstack([X, vz, sec]), train_stats


def fit_models(tr: pd.DataFrame) -> tuple[dict, dict]:
    Xtr, st = design(tr)
    models = {
        "ridge": Ridge(alpha=10.0).fit(Xtr, tr["r3w"].to_numpy()),
        "logit": LogisticRegression(C=1.0, solver="lbfgs", max_iter=500).fit(Xtr, tr["y"].to_numpy()),
        "lgbm": lgb.LGBMRegressor(**LGB_PARAMS).fit(Xtr, tr["r3w"].to_numpy()),
    }
    return models, st


def score_models(models: dict, st: dict, te: pd.DataFrame) -> pd.DataFrame:
    Xte, _ = design(te, st)
    out = te[["scan_day", "r3", "r3w", "y"]].copy()
    out["ridge"] = models["ridge"].predict(Xte)
    out["logit"] = models["logit"].predict_proba(Xte)[:, 1]
    out["lgbm"] = models["lgbm"].predict(Xte)
    return out


def model_pass_wf(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame]:
    scored = []
    for M in OOS_MONTHS:
        tr, te = df[df["month"] < M], df[df["month"] == M]
        models, st = fit_models(tr)
        s = score_models(models, st, te)
        s["fold"] = M
        scored.append(s)
        log(f"  fold {M}: train {len(tr):,} rows / {tr['scan_day'].nunique()} days -> test {len(te):,} rows / {te['scan_day'].nunique()} days")
    scored = pd.concat(scored, ignore_index=True)
    rows, pooled = [], {}
    for m in ["ridge", "logit", "lgbm"]:
        dm = daily_metrics(scored, scored[m], m)
        pooled[m] = dm
        rows.append(summarize(dm, m))
    out = pd.DataFrame(rows)
    out["p_ic"] = [p_from_t(t, n) for t, n in zip(out["t_ic"], out["days"])]
    out["bh10"] = bh(out["p_ic"].tolist())
    return out, pooled, scored


def null_check(df_like: pd.DataFrame, score: pd.Series, draws: int = 1000, seed: int = 7) -> dict:
    """Within-day shuffle of the score. Returns the shuffled IC-t distribution and the observed t."""
    d = df_like[["scan_day", "r3"]].copy()
    d["s"] = score.values
    d = d.dropna(subset=["s"])
    groups = []
    for _, g in d.groupby("scan_day"):
        if len(g) < 30 or g["s"].nunique() < 2:
            continue
        rs = stats.rankdata(g["r3"])
        ss = stats.rankdata(g["s"])
        rs = (rs - rs.mean()) / rs.std()
        ss = (ss - ss.mean()) / ss.std()
        groups.append((rs, ss))
    obs = np.array([float(np.mean(rs * ss)) for rs, ss in groups])
    t_obs = obs.mean() / (obs.std(ddof=1) / np.sqrt(len(obs)))
    rng = np.random.default_rng(seed)
    ts = np.empty(draws)
    for k in range(draws):
        ics = np.array([float(np.mean(rs * rng.permutation(ss))) for rs, ss in groups])
        ts[k] = ics.mean() / (ics.std(ddof=1) / np.sqrt(len(ics)))
    return dict(t_obs=float(t_obs), draws=draws, pct_of_null_below=float((ts < t_obs).mean()),
                null_t_p975=float(np.quantile(ts, 0.975)), null_t_p025=float(np.quantile(ts, 0.025)),
                frac_null_abs_ge_obs=float((np.abs(ts) >= abs(t_obs)).mean()))


# ----------------------------------------------------------------------------- report
def fmt_table(tab: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in tab.iterrows():
        cells = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, float):
                cells.append(f"{v:.3f}" if abs(v) < 10 else f"{v:,.0f}")
            elif isinstance(v, (bool, np.bool_)):
                cells.append("yes" if v else "")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


SF_COLS = ["name", "days", "coverage", "k_top", "signs", "ic", "t_ic", "t_ic_hac", "p_ic", "bh10", "exc", "t_exc", "t_exc_hac", "hit", "t_hit", "exc50", "t_exc50"]
MD_COLS = ["name", "days", "k_top", "ic", "t_ic", "t_ic_hac", "p_ic", "bh10", "exc", "t_exc", "t_exc_hac", "hit", "t_hit", "exc50", "t_exc50", "hit50", "t_hit50"]


def verdict(sf: pd.DataFrame, md: pd.DataFrame) -> tuple[str, str]:
    both = pd.concat([sf, md], ignore_index=True)
    kill = bool((both["t_ic"] >= 2).sum() == 0)
    elig = both[both["days"] >= 60]
    cand = elig[(elig["exc"] >= 1.0) & (elig["t_exc"] >= 2) & (elig["t_ic"] >= 3)]
    if kill:
        return "KILL", "no listed feature and no model reaches IC t >= 2 on the pooled out-of-sample days"
    if len(cand):
        return "CANDIDATE PASS (pending the one-time holdout read)", ", ".join(cand["name"])
    return "INCONCLUSIVE", "some IC t >= 2, but none meets excess >= +1.0 pts at t >= 2 with IC t >= 3"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", action="store_true", help="ONE-TIME live-universe read (09-01..10-13)")
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--force-holdout-reread", action="store_true")
    args = ap.parse_args()
    tag = "holdout" if args.holdout else "wide"
    if args.holdout and os.path.exists(os.path.join(CACHE, "results_holdout.json")) and not args.force_holdout_reread:
        raise SystemExit("holdout already read once (results_holdout.json exists); the pre-registration allows one read")
    out_md, out_json = [], {}

    if not args.holdout:
        df = build(holdout=False)
        # alignment check
        a = df[["price_change_pct", "ret_1d_bar"]].dropna()
        corr = float(np.corrcoef(a["price_change_pct"], a["ret_1d_bar"] * 100)[0, 1])
        gap = float((a["price_change_pct"] - a["ret_1d_bar"] * 100).abs().median())
        within = float(((a["price_change_pct"] - a["ret_1d_bar"] * 100).abs() <= 0.1).mean())
        align = f"alignment: corr(price_change_pct, bar ret_1d) {corr:.3f}, median |gap| {gap:.3f} pts, within 0.1 pt {within*100:.1f}%"
        log(align)
        out_md.append("### Alignment check\n\n" + align)
        bym = df.groupby("month").agg(days=("scan_day", "nunique"), rows=("r3", "size"),
                                      mean_r3=("r3", lambda x: x.mean() * 100), hit=("y", lambda x: x.mean() * 100)).reset_index()
        out_md.append("### Rows by month (wide era, after filters)\n\n" + fmt_table(bym, ["month", "days", "rows", "mean_r3", "hit"]))

        log("single-feature pass ...")
        sf, sf_pooled = single_feature_pass(df, fit_months_all=False)
        sf = sf.sort_values("t_ic", ascending=False, key=lambda s: s.abs())
        out_md.append("### Single features, walk-forward, pooled out-of-sample (May-Aug), sign fixed on prior months\n\n" + fmt_table(sf, SF_COLS))
        log("model pass ...")
        md, md_pooled, scored = model_pass_wf(df)
        out_md.append("### Models, walk-forward, pooled out-of-sample (May-Aug)\n\n" + fmt_table(md, MD_COLS))

        v, why = verdict(sf, md)
        out_md.append(f"### Wide-era verdict\n\n**{v}**: {why}.")
        log(f"VERDICT {v}: {why}")

        # null check on the best IC t (feature or model)
        best = pd.concat([sf, md]).sort_values("t_ic", ascending=False, key=lambda s: s.abs()).iloc[0]
        if best["name"] in md_pooled:
            nc = null_check(scored, scored[best["name"]], args.draws)
        else:
            sign = 1 if best["ic"] >= 0 else -1
            # pooled OOS rows only, with the per-fold sign
            parts = []
            for M in OOS_MONTHS:
                s = 1 if sf.set_index("name").loc[best["name"], "signs"][OOS_MONTHS.index(M)] == "+" else -1
                part = df[df["month"] == M]
                parts.append((part, part[f"z_{best['name']}"] * s))
            dd = pd.concat([p for p, _ in parts])
            ss = pd.concat([s for _, s in parts])
            nc = null_check(dd, ss, args.draws)
        out_md.append(f"### Null check, best IC t = {best['name']}\n\n" + json.dumps(nc, indent=1))
        log(f"null check {best['name']}: {nc}")

        # secondary tables
        sub = df[df["underlying_price"] >= 5].copy()
        for feat in FEATURES:
            g = sub.groupby("scan_day")
            r = g[feat].rank(method="average"); n = g[feat].transform("count")
            sub[f"z_{feat}"] = (r - 0.5) / n - 0.5
        sf5, _ = single_feature_pass(sub, fit_months_all=False)
        sf5 = sf5.sort_values("t_ic", ascending=False, key=lambda s: s.abs()).head(10)
        out_md.append(f"### Secondary: top 10 by |IC t| with underlying_price >= $5 ({len(sub):,} rows)\n\n" + fmt_table(sf5, SF_COLS))
        md5, _, _ = model_pass_wf(sub)
        out_md.append("### Secondary: models with underlying_price >= $5\n\n" + fmt_table(md5, MD_COLS))
        dl = df.groupby("scan_day").agg(vix=("vix_level", "first"), r3w=("r3w", "mean"), hit=("y", "mean")).reset_index()
        dl["vix_tercile"] = pd.qcut(dl["vix"], 3, labels=["low", "mid", "high"])
        vt = dl.groupby("vix_tercile", observed=True).agg(days=("vix", "size"), vix_mean=("vix", "mean"),
                                                        r3w_pts=("r3w", lambda x: x.mean() * 100), hit=("hit", lambda x: x.mean() * 100)).reset_index()
        out_md.append("### Secondary: day-level mean r3w by VIX tercile\n\n" + fmt_table(vt, ["vix_tercile", "days", "vix_mean", "r3w_pts", "hit"]))

        # persist the wide-era signs and models for the holdout read
        signs = {f: (1 if sf.set_index("name").loc[f, "ic_all_days_raw"] >= 0 else -1) for f in FEATURES}
        out_json = dict(verdict=v, why=why, single=sf.to_dict(orient="records"), models=md.to_dict(orient="records"),
                        null=nc, signs_full_wide=signs, alignment=align)
    else:
        wide = build(holdout=False)
        prior = json.load(open(os.path.join(CACHE, "results_wide.json")))
        df = build(holdout=True, sector_top=wide.attrs["sector_top"])
        df.attrs["signs"] = prior["signs_full_wide"]
        sf, _ = single_feature_pass(df, fit_months_all=True)
        sf = sf.sort_values("t_ic", ascending=False, key=lambda s: s.abs())
        # F leg: same sign as the wide era (walk-forward pooled IC) and top-decile excess >= +0.5 pts
        wide_ic = {r["name"]: r["ic"] for r in prior["single"]}
        sf["f_leg"] = [(np.sign(ic) == np.sign(wide_ic.get(n, 0))) and (ex >= 0.5) for n, ic, ex in zip(sf["name"], sf["ic"], sf["exc"])]
        out_md.append("### HOLDOUT (liquid universe 09-01..10-13), single features, sign from the full wide era\n\n" + fmt_table(sf, SF_COLS + ["f_leg"]))
        models, st = fit_models(wide)
        s = score_models(models, st, df)
        rows, pooled = [], {}
        for m in ["ridge", "logit", "lgbm"]:
            dm = daily_metrics(s, s[m], m)
            rows.append(summarize(dm, m))
        md = pd.DataFrame(rows)
        md["p_ic"] = [p_from_t(t, n) for t, n in zip(md["t_ic"], md["days"])]
        md["bh10"] = bh(md["p_ic"].tolist())
        wide_mic = {r["name"]: r["ic"] for r in prior["models"]}
        md["f_leg"] = [(np.sign(ic) == np.sign(wide_mic.get(n, 0))) and (ex >= 0.5) for n, ic, ex in zip(md["name"], md["ic"], md["exc"])]
        out_md.append("### HOLDOUT, models fit on the full wide era\n\n" + fmt_table(md, MD_COLS + ["f_leg"]))
        out_json = dict(single=sf.to_dict(orient="records"), models=md.to_dict(orient="records"))

    text = "\n\n".join(out_md)
    with open(os.path.join(CACHE, f"results_{tag}.md"), "w") as fh:
        fh.write(text + "\n")
    with open(os.path.join(CACHE, f"results_{tag}.json"), "w") as fh:
        json.dump(out_json, fh, indent=1, default=str)
    print("\n" + text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
