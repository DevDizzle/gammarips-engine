"""Screen phase for the liquid-universe funnel study (2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-20-liquid-universe-funnel-spec.md (FROZEN).
Shares pulls with the pool-benchmark study (scan window 2026-04-10..08-17).

STEPS (each is resumable, cache under backtesting_and_research/cache/):
  pull      Pull Polygon grouped daily stock bars for every trading day
            2026-04-09..2026-08-17 (~90 calls). Snapshot the as-of universe
            files from GCS. Failed days are recorded, never zero-filled.
  prerank   Per Study 1 scan session: restrict to the as-of universe, apply
            the >= 3M share-volume floor stat, take top-300 by share volume
            (the spec's cheap pre-rank before the chain rebuild).
  measure   Sample reference-chain sizes (as_of, keyset paging, never
            next_url) and print the concrete chain-rebuild call budget.

The key comes from Secret Manager at run time, stripped, never stored and
never printed (docs/DECISIONS/2026-08-20-polygon-key-rotation-dropped.md).

Run:
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_screen_phase.py pull
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_screen_phase.py prerank
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_screen_phase.py measure
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

PROJECT = "profitscout-fida8"  # hardcoded: shell PROJECT_ID env is a footgun
BUCKET = "profit-scout-data"
BACKUP_PREFIX = "universe-backups/"
LIVE_UNIVERSE = "overnight-universe.txt"

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
GROUPED_PQ = os.path.join(CACHE, "lu_grouped_stocks.parquet")
STATUS_PQ = os.path.join(CACHE, "lu_grouped_status.parquet")
UNIVERSE_PQ = os.path.join(CACHE, "lu_universe_asof.parquet")
PRERANK_PQ = os.path.join(CACHE, "lu_screen_prerank.parquet")

PULL_FIRST = dt.date(2026, 4, 9)    # study 2 first scan 04-10, minus one day
PULL_LAST = dt.date(2026, 8, 17)    # study 2 last scan
S1_LAST_ENTRY = dt.date(2026, 8, 14)
S1_N_ENTRY = 60
PRERANK_N = 300
UND_VOL_FLOOR = 3_000_000
WORKERS = 16

NYSE_HOLIDAYS_2026 = {
    dt.date(2026, 1, 1), dt.date(2026, 1, 19), dt.date(2026, 2, 16),
    dt.date(2026, 4, 3), dt.date(2026, 5, 25), dt.date(2026, 6, 19),
    dt.date(2026, 7, 3), dt.date(2026, 9, 7), dt.date(2026, 11, 26),
    dt.date(2026, 12, 25),
}


def polygon_key() -> str:
    out = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=POLYGON_API_KEY", f"--project={PROJECT}"],
        capture_output=True, text=True, check=True).stdout
    return out.strip()  # trailing-newline trap


def get_json(url: str, params: dict) -> dict | None:
    """One GET. Returns None on failure. NEVER prints the response body
    or the exception text (either can contain the key)."""
    qs = urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"{url}?{qs}", timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                print(f"    FAILED {url.split('polygon.io')[-1]}"
                      f" ({type(e).__name__})")
                return None
            time.sleep(2 ** attempt)
    return None


def is_trading_day(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in NYSE_HOLIDAYS_2026


def trading_days(lo: dt.date, hi: dt.date) -> list[dt.date]:
    out, d = [], lo
    while d <= hi:
        if is_trading_day(d):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def s1_scan_days() -> list[dt.date]:
    days, d = [], S1_LAST_ENTRY
    while len(days) < S1_N_ENTRY + 1:
        if is_trading_day(d):
            days.append(d)
        d -= dt.timedelta(days=1)
    days.reverse()
    return days[:-1]  # scan date = prior trading day of each entry day


# ------------------------------------------------------------------ pull
def cmd_pull() -> None:
    os.makedirs(CACHE, exist_ok=True)
    key = polygon_key()
    days = trading_days(PULL_FIRST, PULL_LAST)
    have = set()
    frames = []
    if os.path.exists(GROUPED_PQ):
        old = pd.read_parquet(GROUPED_PQ)
        have = set(pd.to_datetime(old.session).dt.date)
        frames.append(old)
    todo = [d for d in days if d not in have]
    print(f"grouped stocks: {len(days)} sessions, cached {len(have)},"
          f" pulling {len(todo)}")

    def pull_day(d: dt.date):
        j = get_json(
            "https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/"
            + d.isoformat(),
            {"adjusted": "true", "apiKey": key})
        if j is None or j.get("status") not in ("OK", "DELAYED"):
            return d, None
        rows = j.get("results") or []
        df = pd.DataFrame(
            [{"session": d, "ticker": r.get("T"), "volume": r.get("v"),
              "close": r.get("c")} for r in rows])
        return d, df

    status = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(pull_day, d) for d in todo]
        for f in as_completed(futs):
            d, df = f.result()
            if df is None or df.empty:
                status.append({"session": d, "ok": False, "rows": 0})
            else:
                frames.append(df)
                status.append({"session": d, "ok": True, "rows": len(df)})
    # Count what answered. A batch that raises nothing has proven nothing.
    ok = sum(1 for s in status if s["ok"])
    print(f"answered OK: {ok}/{len(todo)}; failed sessions recorded, never"
          " zero-filled")
    if frames:
        alldf = pd.concat(frames, ignore_index=True).drop_duplicates(
            subset=["session", "ticker"])
        alldf.to_parquet(GROUPED_PQ)
        print(f"cache: {len(alldf)} rows,"
              f" {alldf.session.nunique()} sessions -> {GROUPED_PQ}")
    st = pd.DataFrame(status)
    if os.path.exists(STATUS_PQ) and not st.empty:
        st = pd.concat([pd.read_parquet(STATUS_PQ), st], ignore_index=True)
    if not st.empty:
        st.drop_duplicates(subset=["session"], keep="last").to_parquet(STATUS_PQ)

    if not os.path.exists(UNIVERSE_PQ):
        from google.cloud import storage
        gcs = storage.Client(project=PROJECT)
        bucket = gcs.bucket(BUCKET)
        rows = []
        for b in gcs.list_blobs(BUCKET, prefix=BACKUP_PREFIX):
            live_from = dt.date.fromisoformat(
                b.name.split("overnight-universe-")[1][:10])
            for t in b.download_as_text().strip().splitlines():
                rows.append({"live_from": live_from, "ticker": t.strip()})
        live = bucket.get_blob(LIVE_UNIVERSE)
        for t in live.download_as_text().strip().splitlines():
            rows.append({"live_from": live.updated.date(), "ticker": t.strip()})
        u = pd.DataFrame(rows)
        u.to_parquet(UNIVERSE_PQ)
        print(f"universe snapshot: {u.live_from.nunique()} versions,"
              f" {len(u)} rows -> {UNIVERSE_PQ}")


def universe_asof(d: dt.date, u: pd.DataFrame) -> set[str]:
    vers = sorted(v for v in u.live_from.unique() if v <= d)
    return set(u[u.live_from == vers[-1]].ticker)


# ------------------------------------------------------------------ prerank
def cmd_prerank() -> None:
    g = pd.read_parquet(GROUPED_PQ)
    g["session"] = pd.to_datetime(g.session).dt.date
    u = pd.read_parquet(UNIVERSE_PQ)
    u["live_from"] = pd.to_datetime(u.live_from).dt.date
    out, report = [], []
    for d in s1_scan_days():
        day = g[g.session == d]
        if day.empty:
            report.append((d, 0, 0, 0, "NO GROUPED DATA"))
            continue
        uni = universe_asof(d, u)
        dd = day[day.ticker.isin(uni)].copy()
        n_floor = int((dd.volume >= UND_VOL_FLOOR).sum())
        dd = dd.sort_values(["volume", "ticker"], ascending=[False, True])
        top = dd.head(PRERANK_N).copy()
        top["rank"] = range(1, len(top) + 1)
        out.append(top)
        report.append((d, len(uni), len(dd), n_floor, ""))
    pr = pd.concat(out, ignore_index=True)
    pr.to_parquet(PRERANK_PQ)
    rep = pd.DataFrame(report, columns=[
        "scan", "universe", "matched", "vol_ge_3M", "note"])
    bad = rep[rep.note != ""]
    print(f"pre-rank sessions: {len(out)} of {len(rep)}"
          f" | union of top-{PRERANK_N} names:"
          f" {pr.ticker.nunique()}")
    print(f"universe matched by grouped rows: median"
          f" {rep[rep.note == ''].matched.median():.0f} of"
          f" {rep[rep.note == ''].universe.median():.0f}")
    print(f"names with volume >= 3M per session: median"
          f" {rep[rep.note == ''].vol_ge_3M.median():.0f}")
    if len(bad):
        print("sessions with NO grouped data (excluded, reported):")
        for _, r in bad.iterrows():
            print(f"  {r.scan}")
    print(f"-> {PRERANK_PQ}")


# ------------------------------------------------------------------ measure
def enumerate_contracts(key: str, name: str, as_of: dt.date) -> list[str]:
    """Keyset paging on ticker.gte + no-progress guard + hard page cap.

    Mirrors the production convention (universe_refresh.py
    _enumerate_common_stocks). Never next_url. The first version used
    ticker.gt with no guard and looped forever when the endpoint ignored
    the cursor param.
    """
    seen: set[str] = set()
    cursor = ""
    for _ in range(60):  # hard cap ~60k contracts
        params = {"underlying_ticker": name, "as_of": as_of.isoformat(),
                  "limit": 1000, "order": "asc", "sort": "ticker",
                  "apiKey": key}
        if cursor:
            params["ticker.gte"] = cursor
        j = get_json("https://api.polygon.io/v3/reference/options/contracts",
                     params)
        if j is None:
            break
        rows = [r["ticker"] for r in (j.get("results") or [])]
        before = len(seen)
        seen.update(rows)
        if (not rows or (len(seen) == before and cursor)
                or rows[-1] == cursor or len(rows) < 1000):
            break
        cursor = rows[-1]
    else:
        print(f"    WARNING {name} {as_of}: page cap hit, chain truncated",
              flush=True)
    return sorted(seen)


def cmd_measure() -> None:
    key = polygon_key()
    pr = pd.read_parquet(PRERANK_PQ)
    pr["session"] = pd.to_datetime(pr.session).dt.date
    union = pr.ticker.nunique()
    d = sorted(pr.session.unique())[len(pr.session.unique()) // 2]
    day = pr[pr.session == d]
    sample = pd.concat([day.head(4), day.iloc[145:149], day.tail(4)])
    print(f"sample session {d}, {len(sample)} names across the rank range")
    counts = []
    for _, r in sample.iterrows():
        t0 = time.time()
        c = enumerate_contracts(key, r.ticker, d)
        counts.append(len(c))
        print(f"  rank {r['rank']:>3} {r.ticker:<6} contracts as_of:"
              f" {len(c)}  ({time.time() - t0:.1f}s)", flush=True)
    avg = sum(counts) / len(counts)
    # Weekly as_of checkpoints across the window catch listings/expiries.
    fridays = [x for x in trading_days(PULL_FIRST, PULL_LAST)
               if x.weekday() == 4]
    ref_calls = union * len(fridays) * max(1, round(avg / 1000 + 0.5))
    # One day-aggs RANGE call per distinct contract covers every session.
    # Distinct contracts over 4 months ~ 2.2x one day's live chain.
    agg_calls = int(union * avg * 2.2)
    total = ref_calls + agg_calls
    print(f"\nBUDGET: union {union} names | avg {avg:.0f} contracts/name"
          f" (one as_of)")
    print(f"  reference enumeration ({len(fridays)} weekly checkpoints):"
          f" ~{ref_calls:,} calls")
    print(f"  day-aggs range pulls: ~{agg_calls:,} calls")
    print(f"  TOTAL ~{total:,} calls | at 50 req/s ~{total / 50 / 3600:.1f} h"
          f" | at 100 req/s ~{total / 100 / 3600:.1f} h")


# ------------------------------------------------------------------ chain
CHAIN_DIR = os.path.join(CACHE, "lu_chain_aggs")
MANIFEST = os.path.join(CHAIN_DIR, "_manifest.json")


def enumerate_by_expiration(key: str, name: str, expired: bool) -> list[dict]:
    """Keyset walk on expiration_date (a documented range filter on this
    endpoint). ticker.gte is ignored by /v3/reference/options/contracts,
    which silently truncates big chains at limit=1000 (measured 2026-08-20).
    Superset enumeration: every contract with expiration >= the window start,
    so nothing tradeable in-window is missed. Never next_url."""
    out: dict[str, dict] = {}
    cursor = PULL_FIRST.isoformat()
    for _ in range(120):
        j = get_json(
            "https://api.polygon.io/v3/reference/options/contracts",
            {"underlying_ticker": name, "expiration_date.gte": cursor,
             "expired": str(expired).lower(), "limit": 1000,
             "order": "asc", "sort": "expiration_date", "apiKey": key})
        if j is None:
            break
        rows = j.get("results") or []
        if not rows:
            break
        if len(rows) < 1000:
            for r in rows:
                out[r["ticker"]] = r
            break
        last_exp = rows[-1]["expiration_date"]
        kept = [r for r in rows if r["expiration_date"] < last_exp]
        if not kept:  # one expiration holds 1000+ contracts: cannot advance
            print(f"    WARNING {name}: expiry {last_exp} >=1000 contracts,"
                  " truncated", flush=True)
            for r in rows:
                out[r["ticker"]] = r
            break
        for r in kept:
            out[r["ticker"]] = r
        cursor = last_exp
    return list(out.values())


def pull_name(key: str, name: str) -> dict:
    contracts = (enumerate_by_expiration(key, name, expired=True)
                 + enumerate_by_expiration(key, name, expired=False))
    dedup = {c["ticker"]: c for c in contracts}
    rows, failed = [], 0

    def pull_contract(c: dict):
        j = get_json(
            f"https://api.polygon.io/v2/aggs/ticker/{c['ticker']}/range/1/day/"
            f"{PULL_FIRST}/{PULL_LAST}",
            {"adjusted": "true", "limit": 50000, "apiKey": key})
        if j is None:
            return None
        res = []
        for b in j.get("results") or []:
            res.append({
                "contract": c["ticker"],
                "type": c.get("contract_type"),
                "strike": c.get("strike_price"),
                "expiration": c.get("expiration_date"),
                "session": dt.datetime.utcfromtimestamp(
                    b["t"] / 1e3).date(),  # aggs t is epoch ms
                "volume": b.get("v"), "vwap": b.get("vw"),
                "close": b.get("c")})
        return res

    with ThreadPoolExecutor(max_workers=8) as ex:
        for f in as_completed([ex.submit(pull_contract, c)
                               for c in dedup.values()]):
            r = f.result()
            if r is None:
                failed += 1
            else:
                rows.extend(r)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["ticker"] = name
        df.to_parquet(os.path.join(CHAIN_DIR, f"{name}.parquet"))
    return {"name": name, "contracts": len(dedup), "failed": failed,
            "bar_rows": len(df)}


def cmd_chain() -> None:
    os.makedirs(CHAIN_DIR, exist_ok=True)
    key = polygon_key()
    pr = pd.read_parquet(PRERANK_PQ)
    names = sorted(pr.ticker.unique())
    done = {}
    if os.path.exists(MANIFEST):
        done = json.load(open(MANIFEST))
    # A name re-runs when >5% of its contract pulls failed. Count what
    # answered; a batch that raises nothing has proven nothing.
    todo = [n for n in names if n not in done
            or done[n]["failed"] > 0.05 * max(1, done[n]["contracts"])]
    print(f"chain rebuild: {len(names)} names, done {len(names) - len(todo)},"
          f" todo {len(todo)}", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(pull_name, key, n): n for n in todo}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            done[r["name"]] = {k: r[k] for k in
                               ("contracts", "failed", "bar_rows")}
            json.dump(done, open(MANIFEST, "w"))
            el = time.time() - t0
            print(f"  [{i}/{len(todo)}] {r['name']:<6}"
                  f" contracts {r['contracts']:>5} failed {r['failed']:>3}"
                  f" bar_rows {r['bar_rows']:>6}"
                  f" | {el / 60:.0f} min elapsed,"
                  f" ~{el / i * (len(todo) - i) / 3600:.1f} h left",
                  flush=True)
    tot_c = sum(d["contracts"] for d in done.values())
    tot_f = sum(d["failed"] for d in done.values())
    print(f"DONE: {len(done)} names, {tot_c} contracts, {tot_f} failed pulls",
          flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"pull": cmd_pull, "prerank": cmd_prerank, "measure": cmd_measure,
     "chain": cmd_chain}.get(cmd, lambda: print(__doc__))()
