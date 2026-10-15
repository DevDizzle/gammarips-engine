#!/usr/bin/env python3
"""
Dry run of the liquid-universe rank basis (LIQUID_RANK_BASIS) on live data.

READ-ONLY. Reads the universe file from GCS and Polygon (one snapshot, about
30 grouped-daily calls, and with --pass2 one chain snapshot per candidate).
Writes nothing anywhere.

It runs the scanner's own pass 1 under each basis and reports the pre-rank
candidates. With --pass2 it also runs pass 2 and the liquidity rank, so the
two final 100-name universes are compared name by name.

Caveat the output carries: a run during the session sees PARTIAL day volume
for session T. The 20-session median barely moves on that, the share-volume
basis moves a lot. Re-run after 16:05 ET for session-complete numbers.

Usage (from the repo root):
    PROJECT_ID=profitscout-fida8 python scripts/tests_and_diagnostics/dry_run_universe_rank.py [--pass2]
"""
from __future__ import annotations

import argparse
import logging
import os
import statistics as st
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

PROJECT = "profitscout-fida8"  # explicit: the shell exports a different PROJECT_ID
os.environ["PROJECT_ID"] = PROJECT

from src.enrichment.core.clients.polygon_client import PolygonClient  # noqa: E402
from src.enrichment.core.pipelines import overnight_scanner as sc  # noqa: E402


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


def _describe(label: str, rows: list[dict], n: int) -> dict:
    top = rows[:n]
    px = [r.get("underlying_price") or 0 for r in top]
    return {
        "label": label,
        "names": {r["ticker"] for r in top},
        "median_price": st.median(px) if px else float("nan"),
        "below_15": sum(1 for p in px if p < 15),
        "below_5": sum(1 for p in px if p < 5),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass2", action="store_true", help="also price chains and run the liquidity rank")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    poly = PolygonClient(api_key=_polygon_key())
    universe = sc._load_universe()
    if not universe:
        print("empty universe, aborting")
        return 2
    now = datetime.now(ZoneInfo("America/New_York"))
    print(f"dry run at {now:%Y-%m-%d %H:%M} ET, universe {len(universe)} names, "
          f"pre-rank {sc.LIQUID_PRERANK_N}, top {sc.LIQUID_TOP_N}")
    if now.hour < 16 and now.weekday() < 5:
        print("CAVEAT: session in progress, session T volume is partial")

    out = {}
    for basis in ("share_volume", "dollar_volume_20d"):
        sc.LIQUID_RANK_BASIS = basis
        cands = sc._pass1_stock_snapshots(poly, universe)
        out[basis] = {"pre": _describe(basis, cands, sc.LIQUID_TOP_N), "cands": cands}
        if args.pass2:
            enriched = sc._pass2_options(poly, cands)
            top = sc._rank_liquid_universe(enriched)
            out[basis]["final"] = _describe(basis, top, sc.LIQUID_TOP_N)

    for stage in ("pre", "final"):
        if stage not in out["share_volume"]:
            continue
        a, b = out["share_volume"][stage], out["dollar_volume_20d"][stage]
        print(f"\n== {stage}: top {sc.LIQUID_TOP_N} by share volume vs by 20-session median dollar volume")
        print(f"{'':28}{'share_volume':>14}{'dollar_vol_20d':>16}")
        print(f"{'median price $':28}{a['median_price']:>14.2f}{b['median_price']:>16.2f}")
        print(f"{'names below $15':28}{a['below_15']:>14d}{b['below_15']:>16d}")
        print(f"{'names below $5':28}{a['below_5']:>14d}{b['below_5']:>16d}")
        print(f"{'names in common':28}{len(a['names'] & b['names']):>14d}")
        print("out (share-volume only): " + " ".join(sorted(a["names"] - b["names"])))
        print("in  (dollar-volume only): " + " ".join(sorted(b["names"] - a["names"])))
    ca = {r["ticker"] for r in out["share_volume"]["cands"]}
    cb = {r["ticker"] for r in out["dollar_volume_20d"]["cands"]}
    print(f"\npre-rank {sc.LIQUID_PRERANK_N} candidates in common: {len(ca & cb)}")
    bases = {}
    for r in out["dollar_volume_20d"]["cands"]:
        bases[r.get("rank_basis")] = bases.get(r.get("rank_basis"), 0) + 1
    print(f"rank_basis on the dollar-volume candidates: {bases}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
