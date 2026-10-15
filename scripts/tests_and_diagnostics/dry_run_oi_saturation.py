#!/usr/bin/env python3
"""
Dry run of the chooser's OI saturation point (CONTRACT_OI_SATURATION) against live chains.

READ-ONLY. Reads BigQuery (the latest scan's liquid-universe names) and Polygon
(today's chain snapshot). Writes nothing anywhere.

For each name it re-runs the scanner's own `_best_contract` with rule set B fixed
(mid >= 1.50, delta <= 0.50, OI >= 500) at each saturation point and reports how
many picks change, the open interest, price, delta and DTE of the picks, and the
per-name moves.

Caveat the output carries: a run during the session sees PARTIAL day volume. Re-run
after 16:05 ET for session-complete numbers.

Usage (repo root, venv with overnight-scanner/requirements.txt, PROJECT_ID unset):
    python scripts/tests_and_diagnostics/dry_run_oi_saturation.py --sats 3000,10000,20000
    python scripts/tests_and_diagnostics/dry_run_oi_saturation.py --extra ABBV,ABT,ADBE

--extra appends names that are not in the latest scan (the dollar-volume universe
adds names the share-volume scan never held). The first saturation is the baseline.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
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
RULE_SET_B = dict(min_mid=1.5, max_delta=0.5, min_oi=500)


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


def _latest_universe(scan_date: str | None, bullish_only: bool) -> list[dict]:
    where = f'scan_date = "{scan_date}"' if scan_date else (
        "scan_date = (SELECT MAX(scan_date) FROM `%s.profit_scout.overnight_signals`)" % PROJECT
    )
    if bullish_only:
        where += ' AND direction = "BULLISH"'
    sql = f"""
    SELECT scan_date, ticker, underlying_price
    FROM `{PROJECT}.profit_scout.overnight_signals`
    WHERE {where} AND liquidity_rank <= 100
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


def _one(poly: PolygonClient, row: dict, sats: list[float]) -> dict:
    t = row["ticker"]
    chain = poly.fetch_options_chain(t, max_days=45)  # same window the scanner uses
    calls = [c for c in chain if (c.get("option_type") or "").lower() == "call"]
    upx = next((c.get("underlying_price") for c in calls if c.get("underlying_price")), None)
    upx = float(upx) if upx else (_f(row.get("underlying_price")) or 0.0)
    picks = {s: sc._best_contract(calls, "call", upx, oi_saturation=s, **RULE_SET_B) for s in sats}
    return {"ticker": t, "upx": upx, "n_calls": len(calls), "picks": picks}


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 2) if xs else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-date", default=None, help="default: latest scan")
    ap.add_argument("--sats", default="3000,10000,20000", help="saturation points, first = baseline")
    ap.add_argument("--extra", default="", help="comma list of tickers to append")
    ap.add_argument("--bullish-only", action="store_true", help="only the scan's BULLISH names")
    ap.add_argument("--budgets", default="568,360", help="per-trade budgets in dollars, one column each")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    sats = [float(x) for x in args.sats.split(",")]
    budgets = [float(x) for x in args.budgets.split(",")]

    rows = _latest_universe(args.scan_date, args.bullish_only)
    if not rows:
        print("no liquid-universe rows for that scan", file=sys.stderr)
        return 1
    scan_date = rows[0]["scan_date"]
    have = {r["ticker"] for r in rows}
    extra = [t for t in args.extra.upper().split(",") if t and t not in have]
    rows += [{"scan_date": scan_date, "ticker": t, "underlying_price": None} for t in extra]
    now_et = datetime.now(ZoneInfo("America/New_York"))
    print(f"scan_date {scan_date}: {len(rows) - len(extra)} liquid-universe names"
          f"{' (BULLISH only)' if args.bullish_only else ''} + {len(extra)} extra")
    print(f"chains read {now_et:%Y-%m-%d %H:%M} ET -- "
          f"{'PARTIAL session volume, shape not number' if now_et.hour < 16 or (now_et.hour == 16 and now_et.minute < 5) else 'session complete'}")
    print(f"rule set B fixed at {RULE_SET_B}; a <=$N column counts picks whose mid x 100 is at or "
          "below that per-trade budget (the ask runs a little higher). The trader's budget is a "
          "fraction of equity and moves day to day.")

    poly = PolygonClient(_polygon_key())
    results, failed = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_one, poly, r, sats): r["ticker"] for r in rows}
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                failed.append((futs[fut], type(e).__name__))
    results.sort(key=lambda r: r["ticker"])
    print(f"chains fetched: {len(results)} ok, {len(failed)} failed {failed[:5]}")

    base = sats[0]
    print()
    print(f"{'sat':>6} | {'names':>5} | {'changed':>7} | {'new exp':>7} | {'med oi':>6} | {'oi>=10k':>7} | "
          f"{'med mid':>7} | " + " | ".join(f"{'<=$' + str(int(b)):>6}" for b in budgets)
          + f" | {'med delta':>9} | {'med dte':>7} | {'dte<=13':>7}")
    for s in sats:
        picks = [(r, r["picks"][s]) for r in results]
        have_p = [(r, p) for r, p in picks if p]
        changed = [(r, p) for r, p in have_p
                   if r["picks"][base] and p["contract_symbol"] != r["picks"][base]["contract_symbol"]]
        new_exp = sum(1 for r, p in changed if p["expiration_date"] != r["picks"][base]["expiration_date"])
        n = len(have_p)
        print(f"{int(s):>6} | {n:>5} | {len(changed):>7} | {new_exp:>7} | "
              f"{_med([p['open_interest'] for _, p in have_p]):>6} | "
              f"{(100 * sum(1 for _, p in have_p if (p['open_interest'] or 0) >= 10000) / n) if n else 0:>6.0f}% | "
              f"{_med([p['mid_price'] for _, p in have_p]):>7} | "
              + " | ".join(f"{sum(1 for _, p in have_p if p['mid_price'] * 100 <= b):>6}" for b in budgets) + " | "
              f"{_med([abs(p['delta'] or 0) for _, p in have_p]):>9} | "
              f"{_med([p['dte'] for _, p in have_p]):>7} | "
              f"{(100 * sum(1 for _, p in have_p if p['dte'] <= 13) / n) if n else 0:>6.0f}%")

    print()
    print(f"names whose contract changes (baseline {int(base)} -> {int(sats[-1])}):")
    for r in results:
        b, h = r["picks"][base], r["picks"][sats[-1]]
        if not b or not h or b["contract_symbol"] == h["contract_symbol"]:
            continue

        def fmt(p):
            d = f"d{abs(p['delta']):.2f}" if p["delta"] is not None else "d?"
            return f"{p['contract_symbol'][2:]} mid {p['mid_price']:.2f} {d} dte{p['dte']} oi{p['open_interest']}"
        print(f"  {r['ticker']:6s} ${r['upx']:>7.2f}  {fmt(b)}  ->  {fmt(h)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
