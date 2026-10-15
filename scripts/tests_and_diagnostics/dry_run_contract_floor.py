#!/usr/bin/env python3
"""
Dry run of the contract premium floor (CONTRACT_MIN_MID) against live chains.

READ-ONLY. Reads BigQuery (the latest scan's BULLISH liquid-universe names) and
Polygon (today's chain snapshot). Writes nothing anywhere.

For each name it re-runs the scanner's own `_best_contract` at each floor and
reports pool size, contract shape, and which names change or drop.

Caveat the output carries: a run during the session sees PARTIAL day volume,
so the `vol >= 10` sanity filter bites harder than it does at the 23:00 ET
scan. Treat an intraday run as the shape, not the number. Re-run after 16:05
ET for session-complete numbers.

Usage (from the repo root, with a venv that has overnight-scanner/requirements.txt):
    python scripts/tests_and_diagnostics/dry_run_contract_floor.py --cells 0:0:0,1.5:0.5:0,1.5:0.5:500

Each cell is min_mid:max_delta:min_oi. 0 = off. The first cell is the baseline.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import statistics as st
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from src.enrichment.core.clients.polygon_client import PolygonClient  # noqa: E402
from src.enrichment.core.pipelines import overnight_scanner as sc  # noqa: E402

PROJECT = "profitscout-fida8"  # explicit: the shell exports a different PROJECT_ID


def _polygon_key() -> str:
    key = os.environ.get("POLYGON_API_KEY", "").strip()
    if key:
        return key
    out = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=POLYGON_API_KEY", f"--project={PROJECT}"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()  # secret mounts and prints carry a trailing newline


def _latest_bullish_universe(scan_date: str | None) -> list[dict]:
    where = f'scan_date = "{scan_date}"' if scan_date else (
        "scan_date = (SELECT MAX(scan_date) FROM `%s.profit_scout.overnight_signals`)" % PROJECT
    )
    sql = f"""
    SELECT scan_date, ticker, underlying_price, recommended_contract,
           recommended_mid_price, recommended_delta, recommended_dte, recommended_oi
    FROM `{PROJECT}.profit_scout.overnight_signals`
    WHERE {where} AND liquidity_rank <= 100 AND direction = "BULLISH"
    ORDER BY ticker
    """
    out = subprocess.run(
        ["bq", "query", f"--project_id={PROJECT}", "--use_legacy_sql=false",
         "--format=csv", "--max_rows=500", sql],
        capture_output=True, text=True, check=True,
    )
    return list(csv.DictReader(io.StringIO(out.stdout)))


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _one(poly: PolygonClient, row: dict, cells: list[tuple[float, float, float]]) -> dict:
    t = row["ticker"]
    chain = poly.fetch_options_chain(t, max_days=45)  # same window the scanner uses
    calls = [c for c in chain if (c.get("option_type") or "").lower() == "call"]
    upx = next((c.get("underlying_price") for c in calls if c.get("underlying_price")), None)
    upx = float(upx) if upx else (_f(row["underlying_price"]) or 0.0)
    picks = {c: sc._best_contract(calls, "call", upx, min_mid=c[0], max_delta=c[1], min_oi=int(c[2])) for c in cells}
    return {"ticker": t, "upx": upx, "n_calls": len(calls), "picks": picks, "row": row}


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 2) if xs else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-date", default=None, help="default: latest scan")
    ap.add_argument("--cells", default="0:0:0,1.5:0.5:0,1.5:0.5:500", help="min_mid:max_delta:min_oi per cell")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    cells = [tuple(float(y) for y in x.split(":")) for x in args.cells.split(",")]

    rows = _latest_bullish_universe(args.scan_date)
    if not rows:
        print("no BULLISH liquid-universe rows for that scan", file=sys.stderr)
        return 1
    scan_date = rows[0]["scan_date"]
    now_et = datetime.now(ZoneInfo("America/New_York"))
    print(f"scan_date {scan_date}: {len(rows)} BULLISH names in the liquid top-100")
    print(f"chains read {now_et:%Y-%m-%d %H:%M} ET -- "
          f"{'PARTIAL session volume, shape not number' if now_et.hour < 16 or (now_et.hour == 16 and now_et.minute < 5) else 'session complete'}")

    poly = PolygonClient(_polygon_key())
    results, failed = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_one, poly, r, cells): r["ticker"] for r in rows}
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                failed.append((futs[fut], type(e).__name__))
    results.sort(key=lambda r: r["ticker"])
    print(f"chains fetched: {len(results)} ok, {len(failed)} failed {failed[:5]}")

    base = cells[0]
    print()
    print(f"{'floor':>6} {'cap':>4} {'minoi':>5} | {'names':>5} | {'dropped':>7} | {'changed':>7} | "
          f"{'med mid':>7} | {'<$1.50':>6} | {'med delta':>9} | {'med dte':>7} | {'med oi':>6} | {'oi<500':>6}")
    for fl in cells:
        picks = [(r, r["picks"][fl]) for r in results]
        have = [(r, p) for r, p in picks if p]
        dropped = [r["ticker"] for r, p in picks if not p]
        changed = sum(
            1 for r, p in have
            if r["picks"][base] and p["contract_symbol"] != r["picks"][base]["contract_symbol"]
        )
        mids = [p["mid_price"] for _, p in have]
        print(f"{fl[0]:>6.2f} {fl[1]:>4.2f} {int(fl[2]):>5} | {len(have):>5} | {len(dropped):>7} | {changed:>7} | "
              f"{_med(mids) if mids else '':>7} | "
              f"{(100 * sum(1 for m in mids if m < 1.5) / len(mids)) if mids else 0:>5.0f}% | "
              f"{_med([abs(p['delta'] or 0) for _, p in have]):>9} | "
              f"{_med([p['dte'] for _, p in have]):>7} | "
              f"{_med([p['open_interest'] for _, p in have]):>6} | "
              f"{sum(1 for _, p in have if (p['open_interest'] or 0) < 500):>6}")
        if fl != base and dropped:
            print(f"         dropped at {fl}: " + ", ".join(
                f"{t}(${next(r['upx'] for r in results if r['ticker'] == t):.0f})" for t in dropped))

    # Per-name detail for the names the floor touches
    print()
    print("names whose contract changes or drops (baseline -> highest floor):")
    hi = cells[-1]
    for r in results:
        b, h = r["picks"][base], r["picks"][hi]
        if b and h and b["contract_symbol"] == h["contract_symbol"]:
            continue
        def fmt(p):
            if not p:
                return "none"
            d = f"d{abs(p['delta']):.2f}" if p['delta'] is not None else "d?"
            return (f"{p['contract_symbol'][2:]} mid {p['mid_price']:.2f} "
                    f"{d} dte{p['dte']} oi{p['open_interest']}")
        print(f"  {r['ticker']:6s} ${r['upx']:>7.2f}  {fmt(b)}  ->  {fmt(h)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
