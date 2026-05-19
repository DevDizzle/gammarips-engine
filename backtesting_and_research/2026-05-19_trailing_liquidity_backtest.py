#!/usr/bin/env python3
"""
2026-05-19 — Trailing-liquidity backtest

Hypothesis: A hard gate at `active_days_20d >= 8` (contract trades on >=40% of
prior 20 sessions) raises entry-day fillability AND preserves edge.

Motivating incident (KBR Jun-18 27.5P, 2026-05-14): scan-day vol=323 but only 4
of prior 21 trading days had any prints. Entry day printed ZERO contracts,
trade marked INVALID_LIQUIDITY.

Data: profitscout-fida8.profit_scout.overnight_signals_enriched
Filter: WHERE recommended_contract IS NOT NULL AND is_win IS NOT NULL.

This script is read-only against BQ and uses Polygon paid-tier daily + minute
aggregates with on-disk caching.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from google.cloud import bigquery
from pandas.tseries.offsets import BDay
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path("/home/user/gammarips-engine/backtesting_and_research")
CACHE_DAILY = ROOT / "cache" / "poly_daily"
CACHE_MINUTE_BASE = ROOT / "cache" / "poly_minute"
RESULTS = ROOT / "results"
CSV_PATH = RESULTS / "2026-05-19_trailing_liquidity_backtest.csv"
MD_PATH = RESULTS / "2026-05-19_trailing_liquidity_summary.md"

CACHE_DAILY.mkdir(parents=True, exist_ok=True)
CACHE_MINUTE_BASE.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

POLY_KEY = os.environ.get("POLYGON_API_KEY")
if not POLY_KEY:
    print("ERROR: POLYGON_API_KEY env var not set", file=sys.stderr)
    sys.exit(1)

PROJECT = "profitscout-fida8"
TABLE = f"{PROJECT}.profit_scout.overnight_signals_enriched"

# ----------------------------- HTTP session ---------------------------------

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


SESSION = make_session()
import threading
_PACING_LOCK = threading.Lock()
_LAST_CALL_TS = [0.0]
MIN_INTERVAL = 0.03  # ~30 req/sec global pacing; Polygon paid tier supports this


def paced_get(url: str) -> requests.Response:
    with _PACING_LOCK:
        now = time.time()
        wait = MIN_INTERVAL - (now - _LAST_CALL_TS[0])
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL_TS[0] = time.time()
    r = SESSION.get(url, timeout=30)
    if r.status_code == 429:
        time.sleep(2.0 + random.random())
    return r


# ----------------------------- Polygon fetchers ------------------------------

def daily_cache_path(contract: str) -> Path:
    safe = contract.replace("/", "_")
    return CACHE_DAILY / f"{safe}.json"


def fetch_daily(contract: str, start_d: date, end_d: date) -> list[dict]:
    """Daily aggs over [start_d, end_d] (inclusive). On-disk cached per contract."""
    path = daily_cache_path(contract)
    if path.exists():
        try:
            with path.open() as f:
                blob = json.load(f)
            if blob.get("contract") == contract:
                return blob.get("results", []) or []
        except Exception:
            pass

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{contract}/range/1/day/"
        f"{start_d.isoformat()}/{end_d.isoformat()}"
        f"?adjusted=true&sort=asc&limit=120&apiKey={POLY_KEY}"
    )
    r = paced_get(url)
    if r.status_code == 404:
        results = []
    else:
        try:
            j = r.json()
        except Exception:
            j = {}
        results = j.get("results", []) or []

    blob = {
        "contract": contract,
        "start": start_d.isoformat(),
        "end": end_d.isoformat(),
        "fetched_at": datetime.utcnow().isoformat(),
        "status": r.status_code,
        "results": results,
    }
    with path.open("w") as f:
        json.dump(blob, f)
    return results


def minute_cache_dir(day: date) -> Path:
    d = CACHE_MINUTE_BASE.parent / f"poly_minute_{day.isoformat()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def minute_cache_path(contract: str, day: date) -> Path:
    safe = contract.replace("/", "_")
    return minute_cache_dir(day) / f"{safe}.json"


def fetch_minute_entry_day(contract: str, day: date) -> list[dict]:
    """Minute aggs for a single trading day. Cached per (day, contract)."""
    path = minute_cache_path(contract, day)
    if path.exists():
        try:
            with path.open() as f:
                blob = json.load(f)
            if blob.get("contract") == contract and blob.get("day") == day.isoformat():
                return blob.get("results", []) or []
        except Exception:
            pass

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{contract}/range/1/minute/"
        f"{day.isoformat()}/{day.isoformat()}"
        f"?adjusted=true&sort=asc&limit=500&apiKey={POLY_KEY}"
    )
    r = paced_get(url)
    if r.status_code == 404:
        results = []
    else:
        try:
            j = r.json()
        except Exception:
            j = {}
        results = j.get("results", []) or []

    blob = {
        "contract": contract,
        "day": day.isoformat(),
        "fetched_at": datetime.utcnow().isoformat(),
        "status": r.status_code,
        "results": results,
    }
    with path.open("w") as f:
        json.dump(blob, f)
    return results


# ----------------------------- BQ load --------------------------------------

def load_signals() -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT)
    sql = f"""
    SELECT
      scan_date,
      ticker,
      direction,
      recommended_contract,
      recommended_dte,
      recommended_volume,
      recommended_oi,
      recommended_spread_pct,
      overnight_score,
      premium_score,
      next_day_pct,
      day2_pct,
      day3_pct,
      peak_return_3d,
      outcome_tier,
      is_win
    FROM `{TABLE}`
    WHERE recommended_contract IS NOT NULL
      AND is_win IS NOT NULL
    ORDER BY scan_date, ticker
    """
    print(f"[bq] loading {TABLE} ...", flush=True)
    df = client.query(sql).to_dataframe()
    print(f"[bq] N={len(df)}", flush=True)
    return df


# ----------------------------- Feature compute -------------------------------

def trailing_features(
    daily_results: list[dict], scan_date: date
) -> tuple[int, float, float, int]:
    """Compute (active_days_20d, median_vol_20d, mean_vol_20d, max_vol_20d)
    over the 20 trading days strictly before scan_date.

    `daily_results` come from Polygon /v2/aggs (1d). `t` field is ms epoch at
    bar START in UTC. Polygon returns 1 bar per US trading day; we treat each
    returned bar's date (UTC) as its trading-day index. We:
      * drop any bar whose date >= scan_date
      * sort desc, take the last 20
      * zero-fill is irrelevant here because Polygon only emits bars for days
        the contract traded; "active" is exactly len(filtered_bars).
      * For median/mean over 20 SESSIONS we need to zero-fill missing sessions
        up to 20. We approximate "20 trading sessions" by taking the 20 most
        recent US business days strictly before scan_date and joining.
    """
    if not daily_results:
        return 0, 0.0, 0.0, 0

    # Build 20 trading-day window prior to scan_date using pandas BDay.
    sd_ts = pd.Timestamp(scan_date)
    sessions = pd.bdate_range(end=sd_ts - BDay(1), periods=20)  # 20 sessions
    session_dates = {ts.date() for ts in sessions}

    # Map polygon results to {date: volume}
    by_date: dict[date, int] = {}
    for bar in daily_results:
        t_ms = bar.get("t")
        v = bar.get("v", 0) or 0
        if t_ms is None:
            continue
        d = datetime.utcfromtimestamp(t_ms / 1000.0).date()
        if d >= scan_date:
            continue
        by_date[d] = int(v)

    # Build vol vector over the 20 sessions (zero-fill missing).
    vols = [by_date.get(d, 0) for d in session_dates]
    active = sum(1 for v in vols if v > 0)
    if vols:
        s = pd.Series(vols, dtype=float)
        median_v = float(s.median())
        mean_v = float(s.mean())
        max_v = int(s.max())
    else:
        median_v = 0.0
        mean_v = 0.0
        max_v = 0
    return active, median_v, mean_v, max_v


def next_business_day(scan_date: date) -> date:
    ts = pd.Timestamp(scan_date) + BDay(1)
    return ts.date()


def is_fillable(minute_results: list[dict]) -> bool:
    if not minute_results:
        return False
    for bar in minute_results:
        if (bar.get("v", 0) or 0) > 0:
            return True
    return False


# ----------------------------- Main loop ------------------------------------

def main():
    df = load_signals()
    n = len(df)

    out_cols = [
        "scan_date", "ticker", "direction", "recommended_contract", "recommended_dte",
        "recommended_volume", "recommended_oi", "recommended_spread_pct",
        "overnight_score", "premium_score",
        "active_days_20d", "median_vol_20d", "mean_vol_20d", "max_vol_20d",
        "scan_day_vs_mean_ratio",
        "fillable_entry_day",
        "next_day_pct", "day2_pct", "day3_pct", "peak_return_3d",
        "outcome_tier", "is_win",
    ]
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_row(idx: int, r):
        scan_d: date = r.scan_date if isinstance(r.scan_date, date) else pd.Timestamp(r.scan_date).date()
        contract = r.recommended_contract
        if not contract:
            return idx, None
        try:
            daily_start = scan_d - timedelta(days=35)
            daily_end = scan_d - timedelta(days=1)
            daily = fetch_daily(contract, daily_start, daily_end)
            active, median_v, mean_v, max_v = trailing_features(daily, scan_d)

            entry_d = next_business_day(scan_d)
            minute = fetch_minute_entry_day(contract, entry_d)
            fillable = is_fillable(minute)

            rec_vol = int(r.recommended_volume) if r.recommended_volume is not None and not pd.isna(r.recommended_volume) else 0
            ratio = rec_vol / max(mean_v, 1.0)

            return idx, {
                "scan_date": scan_d.isoformat(),
                "ticker": r.ticker,
                "direction": r.direction,
                "recommended_contract": contract,
                "recommended_dte": r.recommended_dte,
                "recommended_volume": rec_vol,
                "recommended_oi": r.recommended_oi,
                "recommended_spread_pct": r.recommended_spread_pct,
                "overnight_score": r.overnight_score,
                "premium_score": r.premium_score,
                "active_days_20d": active,
                "median_vol_20d": median_v,
                "mean_vol_20d": mean_v,
                "max_vol_20d": max_v,
                "scan_day_vs_mean_ratio": ratio,
                "fillable_entry_day": fillable,
                "next_day_pct": r.next_day_pct,
                "day2_pct": r.day2_pct,
                "day3_pct": r.day3_pct,
                "peak_return_3d": r.peak_return_3d,
                "outcome_tier": r.outcome_tier,
                "is_win": bool(r.is_win),
            }
        except Exception as e:
            print(f"[err] row {idx} {contract} {scan_d}: {e}", flush=True)
            return idx, None

    rows = []
    skipped = 0
    t0 = time.time()
    done = 0
    records = list(df.itertuples(index=False))
    n = len(records)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = [ex.submit(process_row, i + 1, r) for i, r in enumerate(records)]
        for fut in as_completed(futures):
            idx, row = fut.result()
            done += 1
            if row is None:
                skipped += 1
            else:
                rows.append(row)
            if done % 100 == 0:
                elapsed = time.time() - t0
                rate = done / max(elapsed, 1e-9)
                eta = (n - done) / max(rate, 1e-9)
                print(
                    f"[prog] {done}/{n} kept={len(rows)} skipped={skipped} "
                    f"elapsed={elapsed:.0f}s rate={rate:.1f}/s eta={eta/60:.1f}m",
                    flush=True,
                )

    print(f"[done] processed={n} kept={len(rows)} skipped={skipped} elapsed={time.time()-t0:.0f}s")
    out = pd.DataFrame(rows, columns=out_cols)
    out.to_csv(CSV_PATH, index=False)
    print(f"[csv] {CSV_PATH} rows={len(out)}")

    write_summary(out)


# ----------------------------- Summary --------------------------------------

BUCKETS = [(0, 3, "[0-3]"), (4, 7, "[4-7]"), (8, 13, "[8-13]"), (14, 20, "[14-20]")]


def bucket_of(active: int) -> str:
    for lo, hi, name in BUCKETS:
        if lo <= active <= hi:
            return name
    return "OOB"


def write_summary(df: pd.DataFrame) -> None:
    if df.empty:
        MD_PATH.write_text("# Trailing-liquidity backtest\n\nNo rows produced.\n")
        print(f"[md] {MD_PATH} (empty)")
        return

    df = df.copy()
    df["bucket"] = df["active_days_20d"].astype(int).map(bucket_of)
    df["fillable_entry_day"] = df["fillable_entry_day"].astype(bool)
    df["is_win"] = df["is_win"].astype(bool)

    lines: list[str] = []
    lines.append("# Trailing-liquidity backtest — 2026-05-19")
    lines.append("")
    lines.append(f"Source: `profitscout-fida8.profit_scout.overnight_signals_enriched` "
                 f"(`recommended_contract IS NOT NULL AND is_win IS NOT NULL`).")
    lines.append(f"N = {len(df):,}.  Scan-date range: {df['scan_date'].min()} → {df['scan_date'].max()}.")
    lines.append("")
    lines.append("Feature: `active_days_20d` = number of the 20 US business days "
                 "strictly before scan_date on which the OCC contract printed any volume "
                 "(Polygon `/v2/aggs/.../1/day`, zero-filled to a 20-session grid).")
    lines.append("Fillability: at least one `/v2/aggs/.../1/minute` bar with `v>0` on the "
                 "next US business day after scan_date.")
    lines.append("")

    # ---- Section A: fillability by bucket ----
    lines.append("## Section A — Fillability by `active_days_20d` bucket")
    lines.append("")
    lines.append("| Bucket | N | % fillable | N fillable |")
    lines.append("|---|---:|---:|---:|")
    overall_fill = df["fillable_entry_day"].mean()
    for lo, hi, name in BUCKETS:
        sub = df[df["bucket"] == name]
        nrow = len(sub)
        if nrow == 0:
            lines.append(f"| {name} | 0 | n/a | 0 |")
            continue
        pct = sub["fillable_entry_day"].mean() * 100
        nfill = int(sub["fillable_entry_day"].sum())
        lines.append(f"| {name} | {nrow} | {pct:.1f}% | {nfill} |")
    lines.append(f"| **All** | {len(df)} | {overall_fill*100:.1f}% | {int(df['fillable_entry_day'].sum())} |")
    lines.append("")

    # ---- Section B: edge by bucket, filled-only ----
    lines.append("## Section B — Edge by bucket (filled-only rows)")
    lines.append("")
    fil = df[df["fillable_entry_day"]].copy()
    lines.append(f"Filled-only N = {len(fil)} of {len(df)} ({len(fil)/max(len(df),1)*100:.1f}%).")
    lines.append("")
    lines.append("| Bucket | N | Win rate | Mean d1 % | Mean d3 % | Mean peak_3d % |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for lo, hi, name in BUCKETS:
        sub = fil[fil["bucket"] == name]
        if len(sub) == 0:
            lines.append(f"| {name} | 0 | n/a | n/a | n/a | n/a |")
            continue
        wr = sub["is_win"].mean() * 100
        d1 = sub["next_day_pct"].mean()
        d3 = sub["day3_pct"].mean()
        pk = sub["peak_return_3d"].mean()
        lines.append(f"| {name} | {len(sub)} | {wr:.1f}% | {d1:.2f}% | {d3:.2f}% | {pk:.2f}% |")
    lines.append("")

    # Outcome-tier distribution per bucket (filled)
    if "outcome_tier" in fil.columns:
        tiers = sorted([t for t in fil["outcome_tier"].dropna().unique()])
        if tiers:
            lines.append("### Outcome-tier distribution (filled-only)")
            lines.append("")
            header = "| Bucket | " + " | ".join(tiers) + " |"
            sep = "|---|" + "|".join(["---:"] * len(tiers)) + "|"
            lines.append(header)
            lines.append(sep)
            for lo, hi, name in BUCKETS:
                sub = fil[fil["bucket"] == name]
                if len(sub) == 0:
                    lines.append(f"| {name} | " + " | ".join(["0"] * len(tiers)) + " |")
                    continue
                cells = []
                for t in tiers:
                    c = int((sub["outcome_tier"] == t).sum())
                    pct = c / len(sub) * 100
                    cells.append(f"{c} ({pct:.0f}%)")
                lines.append(f"| {name} | " + " | ".join(cells) + " |")
            lines.append("")

    # ---- Section C: cohort impact at active_days >= 8 ----
    lines.append("## Section C — Cohort impact at gate `active_days_20d >= 8`")
    lines.append("")
    kept = df[df["active_days_20d"] >= 8]
    filt = df[df["active_days_20d"] < 8]
    retain_pct = len(kept) / max(len(df), 1) * 100
    wr_all = df["is_win"].mean() * 100
    wr_kept = kept["is_win"].mean() * 100 if len(kept) else float("nan")
    wr_filt = filt["is_win"].mean() * 100 if len(filt) else float("nan")
    fill_kept = kept["fillable_entry_day"].mean() * 100 if len(kept) else float("nan")
    fill_filt = filt["fillable_entry_day"].mean() * 100 if len(filt) else float("nan")
    lines.append(f"- Retained: {len(kept):,} / {len(df):,} ({retain_pct:.1f}%)")
    lines.append(f"- Filtered: {len(filt):,} ({100-retain_pct:.1f}%)")
    lines.append(f"- Win rate kept = {wr_kept:.1f}%, filtered = {wr_filt:.1f}%, all = {wr_all:.1f}%")
    lines.append(f"- Fillability kept = {fill_kept:.1f}%, filtered = {fill_filt:.1f}%")
    # zero-survival days
    days_total = df["scan_date"].nunique()
    by_day_kept = df.groupby("scan_date").apply(lambda g: (g["active_days_20d"] >= 8).sum())
    days_zero = int((by_day_kept == 0).sum())
    lines.append(f"- Trading days in window: {days_total}")
    lines.append(f"- Days with ZERO surviving candidates under this gate: {days_zero} "
                 f"({days_zero/max(days_total,1)*100:.1f}%)")
    # Also try thresholds 5, 10, 12
    lines.append("")
    lines.append("### Threshold sweep")
    lines.append("")
    lines.append("| Threshold | % retained | Win rate kept | Win rate filtered | Fill % kept | Days with zero survivors |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    for thr in [3, 5, 8, 10, 12, 15]:
        k = df[df["active_days_20d"] >= thr]
        fdf = df[df["active_days_20d"] < thr]
        ret = len(k) / max(len(df), 1) * 100
        wrk = k["is_win"].mean() * 100 if len(k) else float("nan")
        wrf = fdf["is_win"].mean() * 100 if len(fdf) else float("nan")
        fk = k["fillable_entry_day"].mean() * 100 if len(k) else float("nan")
        by = df.groupby("scan_date").apply(lambda g: (g["active_days_20d"] >= thr).sum())
        zd = int((by == 0).sum())
        lines.append(f"| >= {thr} | {ret:.1f}% | {wrk:.1f}% | {wrf:.1f}% | {fk:.1f}% | {zd} |")
    lines.append("")

    # ---- Section D: active_days x overnight_score cross-tab ----
    lines.append("## Section D — Cross-tab `active_days_20d` × `overnight_score`")
    lines.append("")
    if df["overnight_score"].notna().any():
        scores = sorted(df["overnight_score"].dropna().unique().astype(int).tolist())
        header = "| Bucket | " + " | ".join([f"score={s}" for s in scores]) + " |"
        sep = "|---|" + "|".join(["---:"] * len(scores)) + "|"
        lines.append(header)
        lines.append(sep)
        for lo, hi, name in BUCKETS:
            row_cells = []
            for s in scores:
                cell = df[(df["bucket"] == name) & (df["overnight_score"] == s)]
                if len(cell) == 0:
                    row_cells.append("—")
                else:
                    wr = cell["is_win"].mean() * 100
                    row_cells.append(f"{wr:.0f}% (n={len(cell)})")
            lines.append(f"| {name} | " + " | ".join(row_cells) + " |")
    else:
        lines.append("(no overnight_score values in cohort)")
    lines.append("")

    # ---- Section E: recommendation ----
    lines.append("## Section E — Recommendation")
    lines.append("")
    # We make this section data-driven inline.
    diff_fill = (fill_kept - fill_filt) if (not math.isnan(fill_kept) and not math.isnan(fill_filt)) else float("nan")
    diff_wr = (wr_kept - wr_filt) if (not math.isnan(wr_kept) and not math.isnan(wr_filt)) else float("nan")
    lines.append(
        f"Headline: at threshold `active_days_20d >= 8`, fillability "
        f"improves by {diff_fill:.1f} pp (kept {fill_kept:.1f}% vs filtered {fill_filt:.1f}%) "
        f"and win rate moves by {diff_wr:+.1f} pp (kept {wr_kept:.1f}% vs filtered {wr_filt:.1f}%) "
        f"while retaining {retain_pct:.1f}% of historical signals; "
        f"{days_zero}/{days_total} days would have zero survivors."
    )
    lines.append("")

    MD_PATH.write_text("\n".join(lines) + "\n")
    print(f"[md] {MD_PATH}")


if __name__ == "__main__":
    main()
