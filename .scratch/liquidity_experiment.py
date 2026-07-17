"""Liquidity-gate experiment: is scan-time OI/vol a valid filter, or are we
rejecting contracts that are tradeable by entry day?

Two questions, one Polygon pull:
  (A) TRADEABILITY — for high-score contracts we REJECTED on liquidity, what does
      their ACTUAL volume / price range look like on entry day (day-1) and across
      the 3-day hold? If they trade fine, the scan-time gate over-rejects.
  (B) STALENESS — does our stored `recommended_volume` (scan-time snapshot) match
      Polygon's actual scan-day aggregate volume? If not, the field is stale.

Polygon /v2/aggs gives historical daily VOLUME / OHLC / transactions per contract
(OI is not in aggs — but volume + a tradeable price range is the more direct
"could we fill it" measure; the OI-staleness is already proven in-data: CAR 3->103).

Run:  POLYGON_API_KEY=... /home/user/gammarips-engine/.venv/bin/python .scratch/liquidity_experiment.py
(or:  ! POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY --project=profitscout-fida8) python .scratch/liquidity_experiment.py)
"""
from __future__ import annotations

import os
import time
import statistics as st

import requests
from google.cloud import bigquery

KEY = os.environ.get("POLYGON_API_KEY")
if not KEY:
    raise SystemExit("Set POLYGON_API_KEY in the environment first.")

PROJECT = "profitscout-fida8"
BASE = "https://api.polygon.io"
# Tradeable-by-entry threshold: >= this many contracts traded on entry day to plausibly fill.
ENTRY_VOL_OK = 50

SAMPLE_SQL = """
SELECT scan_date, ticker, direction, recommended_contract AS contract,
       recommended_oi AS scan_oi, recommended_volume AS scan_vol, overnight_score AS score,
       CASE WHEN recommended_oi >= 10 AND recommended_volume >= 50 THEN 'TRADEABLE_baseline'
            ELSE 'REJECTED_on_liquidity' END AS bucket
FROM `profitscout-fida8.profit_scout.overnight_signals_enriched`
WHERE scan_date BETWEEN "2026-05-18" AND "2026-05-29"
  AND moneyness_pct BETWEEN 0.05 AND 0.13 AND recommended_dte BETWEEN 7 AND 45
  AND recommended_contract IS NOT NULL
  AND (overnight_score >= 6 OR (recommended_oi >= 10 AND recommended_volume >= 50))
ORDER BY bucket, scan_date, ticker
"""


def daily_aggs(contract: str, start: str, end: str) -> list[dict]:
    url = f"{BASE}/v2/aggs/ticker/{contract}/range/1/day/{start}/{end}"
    for attempt in range(4):
        r = requests.get(url, params={"adjusted": "true", "sort": "asc", "apiKey": KEY}, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json().get("results", []) or []
    return []


def main() -> None:
    bq = bigquery.Client(project=PROJECT)
    rows = list(bq.query(SAMPLE_SQL).result())
    print(f"sample: {len(rows)} contracts\n")

    out = []
    for row in rows:
        import datetime as _dt
        sd = row["scan_date"].isoformat()
        # request a wide window; Polygon returns only trading days.
        # idx 0 = scan day, 1 = entry day (day-1), 2-4 = the 3-day hold.
        end = (row["scan_date"] + _dt.timedelta(days=9)).isoformat()
        aggs = daily_aggs(row["contract"], sd, end)
        time.sleep(0.15)
        vols = [a.get("v", 0) for a in aggs]
        # index 0 = scan day (if present), 1 = entry day, 2-4 = hold
        scan_actual = vols[0] if len(vols) >= 1 else None
        entry_vol = vols[1] if len(vols) >= 2 else 0
        hold_vol = sum(vols[2:5]) if len(vols) > 2 else 0
        entry_bar = aggs[1] if len(aggs) >= 2 else None
        rng_pct = None
        if entry_bar and entry_bar.get("l"):
            rng_pct = round(100 * (entry_bar["h"] - entry_bar["l"]) / entry_bar["l"], 1)
        out.append({
            "bucket": row["bucket"], "scan_date": sd, "ticker": row["ticker"],
            "score": row["score"], "stored_vol": row["scan_vol"], "stored_oi": row["scan_oi"],
            "polygon_scan_vol": scan_actual, "entry_vol": entry_vol, "hold_vol": hold_vol,
            "entry_range_pct": rng_pct,
        })
        print(f"{row['bucket'][:8]:8} {sd} {row['ticker']:6} score={row['score']} "
              f"stored(vol={row['scan_vol']},oi={row['scan_oi']}) "
              f"| polygon scan_vol={scan_actual} entry_vol={entry_vol} hold_vol={hold_vol} "
              f"entry_range={rng_pct}%")

    rej = [r for r in out if r["bucket"].startswith("REJECTED")]
    base = [r for r in out if r["bucket"].startswith("TRADEABLE")]

    def med(xs):
        xs = [x for x in xs if x is not None]
        return round(st.median(xs), 1) if xs else None

    print("\n================ VERDICT ================")
    print(f"REJECTED-on-liquidity (n={len(rej)}):")
    print(f"  median ENTRY-day volume: {med([r['entry_vol'] for r in rej])}")
    print(f"  % with entry_vol >= {ENTRY_VOL_OK} (plausibly fillable): "
          f"{round(100*sum(1 for r in rej if (r['entry_vol'] or 0)>=ENTRY_VOL_OK)/max(len(rej),1),1)}%")
    print(f"  median entry-day price range: {med([r['entry_range_pct'] for r in rej])}%")
    print(f"TRADEABLE baseline (n={len(base)}):")
    print(f"  median ENTRY-day volume: {med([r['entry_vol'] for r in base])}")
    print("\n(B) STALENESS — stored scan_vol vs Polygon actual scan-day vol:")
    disc = [(r['stored_vol'], r['polygon_scan_vol']) for r in out
            if r['polygon_scan_vol'] is not None and r['stored_vol'] is not None]
    mism = sum(1 for s, p in disc if abs((s or 0) - (p or 0)) > 2)
    print(f"  {mism}/{len(disc)} contracts where stored vol != Polygon scan-day vol (>2 diff)")


if __name__ == "__main__":
    main()
