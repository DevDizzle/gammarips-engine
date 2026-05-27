#!/usr/bin/env python3
"""
2026-05-27 — Active-day VOLUME FLOOR sweep

Follow-up to 2026-05-19_trailing_liquidity_backtest.py. That gate
(`active_days_20d >= 5`, where an "active day" is any day with vol > 0) shipped
2026-05-19 but EQIX (05-20) and BLK (05-21) still became picks and hit
INVALID_LIQUIDITY:

  EQIX active_days=6  but daily vols were 3,3,7,2,2,2   (1-7 lots/day)
  BLK  active_days=12 but daily vols were 4,1,1,1,3,1,1,1,1,1,2,1 (mostly 1 lot)

Defect: "active day" = vol > 0 has no SIZE floor, so a contract printing one lot
a day for 12 days scores active_days=12 and passes. This sweeps a per-day volume
floor MIN_DAILY_VOL and redefines an active day as `vol >= MIN_DAILY_VOL`, then
picks the smallest floor that maximizes entry-day fillability while keeping ZERO
V5.4-eligible dry days (the funnel-starvation constraint).

READ-ONLY. Reuses the on-disk daily cache from the 2026-05-19 run (no new API
calls for cached contracts). Does NOT modify the frozen 2026-05-19 script.
"""

from __future__ import annotations

import json
import os
import random
import sys
import threading
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
RESULTS = ROOT / "results"
PRIOR_CSV = RESULTS / "2026-05-19_trailing_liquidity_backtest.csv"
SWEEP_CSV = RESULTS / "2026-05-27_active_day_volume_floor_sweep.csv"
MD_PATH = RESULTS / "2026-05-27_active_day_volume_floor_summary.md"
CACHE_DAILY.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

POLY_KEY = os.environ.get("POLYGON_API_KEY")
if not POLY_KEY:
    print("ERROR: POLYGON_API_KEY env var not set", file=sys.stderr)
    sys.exit(1)

PROJECT = "profitscout-fida8"
TABLE = f"{PROJECT}.profit_scout.overnight_signals_enriched"

# Per-day volume floors to sweep. 1 == the current shipped gate (vol > 0).
THRESHOLDS = [1, 5, 10, 25, 50]
ACTIVE_DAYS_MIN = 5  # held fixed (minimum-knob); the floor is the new lever.

# Scenario-C V5.4 eligibility gates that are expressible in BQ (signal-notifier
# main.py lines 117-154). VIX<=VIX3M and earnings-overlap are additional runtime
# gates we cannot replay here, so the per-day candidate counts below are an
# UPPER bound -> dry-day counts are optimistic (a lower bound). Relative movement
# across thresholds is what drives the decision.
VOL_OI_MIN, MONEYNESS_MIN, MONEYNESS_MAX = 2.0, 0.05, 0.10
OI_MIN, VOL_MIN, DTE_MIN, DTE_MAX = 10, 50, 7, 45

# ----------------------------- HTTP (cache-backed) ---------------------------

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=1.5,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=frozenset(["GET"]), respect_retry_after_header=True)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    s.mount("https://", adapter)
    return s

SESSION = make_session()
_LOCK = threading.Lock()
_LAST = [0.0]
MIN_INTERVAL = 0.03

def paced_get(url: str) -> requests.Response:
    with _LOCK:
        wait = MIN_INTERVAL - (time.time() - _LAST[0])
        if wait > 0:
            time.sleep(wait)
        _LAST[0] = time.time()
    r = SESSION.get(url, timeout=30)
    if r.status_code == 429:
        time.sleep(2.0 + random.random())
    return r

def daily_cache_path(contract: str) -> Path:
    return CACHE_DAILY / f"{contract.replace('/', '_')}.json"

def fetch_daily(contract: str, start_d: date, end_d: date) -> list[dict]:
    """Daily aggs over [start_d, end_d]. On-disk cached per contract (reuses the
    2026-05-19 cache). Only hits the API on a cache miss."""
    path = daily_cache_path(contract)
    if path.exists():
        try:
            with path.open() as f:
                blob = json.load(f)
            if blob.get("contract") == contract:
                return blob.get("results", []) or []
        except Exception:
            pass
    url = (f"https://api.polygon.io/v2/aggs/ticker/{contract}/range/1/day/"
           f"{start_d.isoformat()}/{end_d.isoformat()}"
           f"?adjusted=true&sort=asc&limit=120&apiKey={POLY_KEY}")
    r = paced_get(url)
    results = [] if r.status_code == 404 else (r.json().get("results", []) or [])
    with path.open("w") as f:
        json.dump({"contract": contract, "start": start_d.isoformat(),
                   "end": end_d.isoformat(), "fetched_at": datetime.utcnow().isoformat(),
                   "status": r.status_code, "results": results}, f)
    return results

# ----------------------------- Core compute ---------------------------------

def active_at_thresholds(daily_results: list[dict], scan_date: date,
                         thresholds: list[int]) -> dict[int, int]:
    """For each per-day floor n, count sessions in the 20 business days strictly
    before scan_date with vol >= n. Mirrors compute_active_days_20d's windowing."""
    sd_ts = pd.Timestamp(scan_date)
    sessions = pd.bdate_range(end=sd_ts - BDay(1), periods=20)
    session_dates = {ts.date() for ts in sessions}
    by_date: dict[date, int] = {}
    for bar in daily_results:
        t_ms = bar.get("t")
        if t_ms is None:
            continue
        v = bar.get("v", 0) or 0
        d = datetime.utcfromtimestamp(t_ms / 1000.0).date()
        if d >= scan_date:
            continue
        by_date[d] = int(v)
    vols = [by_date.get(d, 0) for d in session_dates]
    return {n: sum(1 for v in vols if v >= n) for n in thresholds}

def active_for_contract(contract: str, scan_d: date) -> dict[int, int]:
    daily = fetch_daily(contract, scan_d - timedelta(days=35), scan_d - timedelta(days=1))
    return active_at_thresholds(daily, scan_d, THRESHOLDS)

def _to_date(x) -> date:
    return x if isinstance(x, date) and not isinstance(x, datetime) else pd.Timestamp(x).date()

# ----------------------------- Part 1: fillability ---------------------------

def part1_fillability(lines: list[str]) -> None:
    if not PRIOR_CSV.exists():
        lines.append("## Part 1 — Fillability gradient\n\n(prior CSV missing; skipped)\n")
        return
    df = pd.read_csv(PRIOR_CSV)
    df = df[df["recommended_contract"].notna()].copy()
    df["fillable_entry_day"] = df["fillable_entry_day"].astype(bool)

    # recompute active-day count at each floor from the cache
    recs = []
    for r in df.itertuples(index=False):
        scan_d = _to_date(r.scan_date)
        recs.append(active_for_contract(r.recommended_contract, scan_d))
    for n in THRESHOLDS:
        df[f"ad_{n}"] = [rec[n] for rec in recs]
    df.to_csv(SWEEP_CSV, index=False)

    lines.append("## Part 1 — Entry-day fillability under gate `active_days(vol>=N) >= %d`" % ACTIVE_DAYS_MIN)
    lines.append("")
    lines.append(f"Cohort: prior backtest CSV, N={len(df):,}, "
                 f"scan {df['scan_date'].min()} → {df['scan_date'].max()}. "
                 "Fillability label = >=1 entry-day minute bar with v>0.")
    lines.append("")
    lines.append("| MIN_DAILY_VOL | retained | retain % | fill% kept | fill% filtered | fill lift (pp) |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    base_fill = df["fillable_entry_day"].mean() * 100
    for n in THRESHOLDS:
        kept = df[df[f"ad_{n}"] >= ACTIVE_DAYS_MIN]
        filt = df[df[f"ad_{n}"] < ACTIVE_DAYS_MIN]
        ret = len(kept) / max(len(df), 1) * 100
        fk = kept["fillable_entry_day"].mean() * 100 if len(kept) else float("nan")
        ff = filt["fillable_entry_day"].mean() * 100 if len(filt) else float("nan")
        lines.append(f"| {n} | {len(kept):,} | {ret:.1f}% | {fk:.1f}% | {ff:.1f}% | {fk-base_fill:+.1f} |")
    lines.append("")
    lines.append(f"(baseline fillability across all {len(df):,} rows = {base_fill:.1f}%)")
    lines.append("")

# ----------------------------- Part 2: funnel / dry days ---------------------

def part2_funnel(lines: list[str]) -> None:
    client = bigquery.Client(project=PROJECT)
    sql = f"""
    SELECT scan_date, ticker, direction, recommended_contract
    FROM `{TABLE}`
    WHERE recommended_contract IS NOT NULL
      AND recommended_strike IS NOT NULL AND recommended_expiration IS NOT NULL
      AND volume_oi_ratio IS NOT NULL AND volume_oi_ratio > {VOL_OI_MIN}
      AND moneyness_pct IS NOT NULL AND moneyness_pct BETWEEN {MONEYNESS_MIN} AND {MONEYNESS_MAX}
      AND recommended_oi >= {OI_MIN} AND recommended_volume >= {VOL_MIN}
      AND recommended_dte BETWEEN {DTE_MIN} AND {DTE_MAX}
    ORDER BY scan_date, ticker
    """
    cand = client.query(sql).to_dataframe()
    lines.append("## Part 2 — V5.4-eligible funnel impact (dry-day constraint)")
    lines.append("")
    if cand.empty:
        lines.append("(no V5.4-eligible candidates returned)\n")
        return
    recs = [active_for_contract(r.recommended_contract, _to_date(r.scan_date))
            for r in cand.itertuples(index=False)]
    for n in THRESHOLDS:
        cand[f"ad_{n}"] = [rec[n] for rec in recs]

    days = cand["scan_date"].nunique()
    lines.append(f"Eligible cohort (Scenario-C BQ gates only; VIX/earnings not replayed, "
                 f"so candidates are an upper bound): N={len(cand):,} over {days} scan days, "
                 f"{cand['scan_date'].min()} → {cand['scan_date'].max()}.")
    lines.append("")
    lines.append("| MIN_DAILY_VOL | candidates kept | retain % | median/day | dry days |")
    lines.append("|---:|---:|---:|---:|---:|")
    for n in THRESHOLDS:
        kept = cand[cand[f"ad_{n}"] >= ACTIVE_DAYS_MIN]
        per_day = cand.groupby("scan_date").apply(
            lambda g: int((g[f"ad_{n}"] >= ACTIVE_DAYS_MIN).sum()))
        dry = int((per_day == 0).sum())
        med = float(per_day.median()) if len(per_day) else 0.0
        ret = len(kept) / max(len(cand), 1) * 100
        lines.append(f"| {n} | {len(kept):,} | {ret:.1f}% | {med:.1f} | {dry} |")
    lines.append("")

# ----------------------------- Part 3: named spot-check ----------------------

def part3_named(lines: list[str]) -> None:
    client = bigquery.Client(project=PROJECT)
    named = [("OKTA", "2026-05-12", "PASS (real fill)"),
             ("KBR", "2026-05-13", "REJECT (incident)"),
             ("HTZ", "2026-05-14", "PASS (real fill +80%)"),
             ("BBY", "2026-05-18", "PASS (real fill +15%)"),
             ("EQIX", "2026-05-20", "REJECT (INVALID_LIQUIDITY)"),
             ("BLK", "2026-05-21", "REJECT (no entry bars)")]
    lines.append("## Part 3 — Named contract spot-check (ACTIVE_DAYS_MIN=%d)" % ACTIVE_DAYS_MIN)
    lines.append("")
    header = "| ticker | scan | expected | " + " | ".join(f"ad@vol>={n}" for n in THRESHOLDS) + " |"
    lines.append(header)
    lines.append("|---|---|---|" + "|".join(["---:"] * len(THRESHOLDS)) + "|")
    for tkr, sd, expect in named:
        q = f"""SELECT recommended_contract FROM `{TABLE}`
                WHERE ticker='{tkr}' AND scan_date='{sd}' AND recommended_contract IS NOT NULL
                LIMIT 1"""
        rows = list(client.query(q).result())
        if not rows:
            lines.append(f"| {tkr} | {sd} | {expect} | " + " | ".join(["n/a"] * len(THRESHOLDS)) + " |")
            continue
        contract = rows[0]["recommended_contract"]
        ad = active_for_contract(contract, _to_date(sd))
        cells = []
        for n in THRESHOLDS:
            mark = "✓" if ad[n] >= ACTIVE_DAYS_MIN else "✗"
            cells.append(f"{ad[n]}{mark}")
        lines.append(f"| {tkr} | {sd} | {expect} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("✓ = passes gate (active_days >= %d), ✗ = rejected." % ACTIVE_DAYS_MIN)
    lines.append("")

# ----------------------------- Main ------------------------------------------

def main():
    lines: list[str] = ["# Active-day volume-floor sweep — 2026-05-27", ""]
    lines.append("Redefines an 'active day' as `vol >= MIN_DAILY_VOL` (was `vol > 0`) in the "
                 "signal-notifier liquidity gate. Goal: pick the smallest floor that maximizes "
                 "entry-day fillability with zero V5.4-eligible dry days.")
    lines.append("")
    print("[part1] fillability gradient ...", flush=True)
    part1_fillability(lines)
    print("[part2] funnel / dry days ...", flush=True)
    part2_funnel(lines)
    print("[part3] named spot-check ...", flush=True)
    part3_named(lines)
    MD_PATH.write_text("\n".join(lines) + "\n")
    print(f"[md] {MD_PATH}")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
