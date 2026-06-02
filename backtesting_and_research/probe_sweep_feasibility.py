"""H20 feasibility probe (READ-ONLY): can we detect sweeps/ISO and multi-leg
options trades on our Polygon tier? Two questions:
  1. Do options trade-condition codes for sweep/ISO/multi-leg even exist? (reference)
  2. Are they populated + accessible on our tier for a real recent contract? (trades)
Reads POLYGON_API_KEY from env. A few calls only.
"""
import os, requests, json
from collections import Counter
import pandas as pd

KEY = os.environ.get("POLYGON_API_KEY", "").strip()
if not KEY:
    raise SystemExit("POLYGON_API_KEY not in env")
S = requests.Session()
BASE = "https://api.polygon.io"


def get(path, **params):
    params["apiKey"] = KEY
    r = S.get(BASE + path, params=params, timeout=20)
    return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {})


# ---- 1. options trade-condition reference ----
print("=== 1. options trade conditions reference (/v3/reference/conditions) ===")
code, j = get("/v3/reference/conditions", asset_class="options", limit=1000)
print(f"status={code}")
conds = {}
if code == 200:
    for c in j.get("results", []):
        conds[c.get("id")] = c.get("name", "")
    print(f"total options conditions: {len(conds)}")
    kw = ("sweep", "iso", "intermarket", "multi", "leg", "complex", "cross", "auction", "block", "spread")
    hits = {i: n for i, n in conds.items() if any(k in n.lower() for k in kw)}
    print("conditions matching sweep/multi-leg/etc keywords:")
    for i, n in sorted(hits.items()):
        print(f"  id={i:4} {n}")
else:
    print("reference not accessible:", json.dumps(j)[:200])

# ---- 2. real trades for a recent liquid contract ----
print("\n=== 2. sample trades for a recent FILLED contract (/v3/trades) ===")
r = pd.read_pickle("/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl")
fil = r[r["status"] == "FILLED"].copy()
fil["entry_day"] = pd.to_datetime(fil["entry_day"])
fil = fil.sort_values(["entry_day", "recommended_volume"], ascending=[False, False])
row = fil.iloc[0]
contract, ed = row["recommended_contract"], fil.iloc[0]["entry_day"].date()
print(f"probe contract: {contract}  entry_day={ed}  (recommended_volume={row['recommended_volume']})")
start = f"{ed.isoformat()}T13:30:00Z"; end = f"{ed.isoformat()}T20:00:00Z"
code, j = get(f"/v3/trades/{contract}", **{"timestamp.gte": start, "timestamp.lte": end, "limit": 1000, "order": "asc"})
print(f"status={code}")
if code == 200:
    trades = j.get("results", [])
    print(f"trades returned: {len(trades)}")
    if trades:
        print("sample trade keys:", list(trades[0].keys()))
        print("sample trade:", json.dumps(trades[0])[:300])
        cc = Counter()
        for t in trades:
            for c in (t.get("conditions") or []):
                cc[c] += 1
        print("condition-code frequency (code: count -> name):")
        for cid, n in cc.most_common():
            print(f"  {cid:4}: {n:5}  {conds.get(cid,'?')}")
        # exchange spread (sweeps hit multiple exchanges) — count distinct exchanges
        exch = Counter(t.get("exchange") for t in trades)
        print(f"distinct exchanges in trades: {len(exch)}  -> {dict(exch)}")
else:
    print("trades endpoint not accessible on this tier:", json.dumps(j)[:300])
