"""
Backfill full 3-day hold-window option minute bars (RESEARCH, read-only on BQ).

The local cache (poly_minute_<DATE>/) only held entry-day bars, so the +80/-60
bracket (a 3-day mechanism) could not be replayed honestly. This script fetches
the MISSING day-2 / day-3 minute bars (and any uncovered contracts) for every
labeled enriched candidate, writing them into the SAME cache layout that
realized_option_label.py already reads. It does NOT modify the replay logic and
does NOT write to BigQuery.

Auth: reads POLYGON_API_KEY from the environment (inject at run time; never
persisted to disk). Only fetches PAST/closed bars -> no lookahead in the fetch.

One Polygon call per (contract, hold-window) using the range endpoint; results
are split by calendar date into poly_minute_<DATE>/<contract>.json. Idempotent:
a (contract, entry_day) window whose three hold-date files already exist with
results is skipped, so the job is resumable.
"""
import os, json, glob, time, datetime
import requests
import pandas as pd
from google.cloud import bigquery

CACHE = "/home/user/gammarips-engine/backtesting_and_research/cache"
POLY_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
HOLD_DAYS = 3
SESS = requests.Session()


def fetch_range(ticker, start_d, end_d):
    """Minute bars for ticker over [start_d, end_d] inclusive. Mirrors
    forward-paper-trader/main.py fetch_minute_bars (range/1/minute, 50k limit)."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_d.isoformat()}/{end_d.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLY_KEY}
    for attempt in range(4):
        try:
            resp = SESS.get(url, params=params, timeout=20)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or [], resp.status_code
        except Exception as e:
            if attempt == 3:
                return [], getattr(getattr(e, "response", None), "status_code", -1)
            time.sleep(1.5 * (attempt + 1))
    return [], -1


def fetch_daily(ticker, start_d, end_d):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_d.isoformat()}/{end_d.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": POLY_KEY}
    resp = SESS.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json().get("results", []) or []


def build_calendar():
    """Fetch SPY daily bars to get the complete trading-day calendar, and drop
    them into poly_daily/ so realized_option_label.trading_days() sees the full
    window (it globs poly_daily/*.json for t-stamps)."""
    start, end = datetime.date(2026, 3, 15), datetime.date(2026, 6, 10)
    bars = fetch_daily("SPY", start, end)
    os.makedirs(f"{CACHE}/poly_daily", exist_ok=True)
    with open(f"{CACHE}/poly_daily/_CALENDAR_SPY.json", "w") as f:
        json.dump({"contract": "SPY", "fetched_at": datetime.datetime.now().isoformat(),
                   "status": 200, "results": bars}, f)
    days = sorted({datetime.datetime.utcfromtimestamp(b["t"] / 1000).date() for b in bars})
    print(f"calendar: {len(days)} trading days {days[0]}..{days[-1]}")
    return days


def main():
    if not POLY_KEY:
        raise SystemExit("POLYGON_API_KEY not in env -- inject it at run time.")

    TD = build_calendar()
    TD_SET = set(TD)

    def next_td(d):
        for x in TD:
            if x > d:
                return x
        return None

    def nth_next_td(d, n):
        for _ in range(n):
            d = next_td(d)
            if d is None:
                return None
        return d

    bq = bigquery.Client(project="profitscout-fida8")
    q = """SELECT DISTINCT ticker, direction, scan_date, recommended_strike,
        recommended_expiration, recommended_contract
        FROM `profitscout-fida8.profit_scout.overnight_signals_enriched`
        WHERE scan_date BETWEEN '2026-04-10' AND '2026-06-01'
          AND recommended_contract IS NOT NULL"""
    df = bq.query(q).to_dataframe()
    print(f"loaded {len(df)} candidate rows from BQ")

    # unique (contract, entry_day) windows
    windows = {}
    today = datetime.date.today()
    for _, r in df.iterrows():
        scan = r["scan_date"]
        contract = r["recommended_contract"]
        if contract is None or pd.isna(scan):
            continue
        scan = scan if isinstance(scan, datetime.date) else pd.Timestamp(scan).date()
        entry_day = next_td(scan)
        if entry_day is None:
            continue
        exit_day = nth_next_td(entry_day, HOLD_DAYS - 1)
        if exit_day is None or exit_day >= today:
            continue  # window not fully closed yet -> no day-3 data exists
        windows[(contract, entry_day)] = exit_day

    print(f"{len(windows)} unique (contract, entry_day) windows to ensure")

    n_skip = n_fetch = n_empty = n_err = 0
    for i, ((contract, entry_day), exit_day) in enumerate(sorted(windows.items(), key=lambda kv: kv[0][1])):
        hold_dates = [entry_day, nth_next_td(entry_day, 1), nth_next_td(entry_day, 2)]
        hold_dates = [d for d in hold_dates if d is not None]
        cfile = contract + ".json"
        # resumable: skip only if every hold-date file already exists with results
        have_all = True
        for hd in hold_dates:
            p = f"{CACHE}/poly_minute_{hd.isoformat()}/{cfile}"
            if not os.path.exists(p):
                have_all = False
                break
            try:
                if not (json.load(open(p)).get("results") or []):
                    have_all = False
                    break
            except Exception:
                have_all = False
                break
        if have_all:
            n_skip += 1
            continue

        bars, status = fetch_range(contract, entry_day, exit_day)
        if status == -1:
            n_err += 1
        # split by calendar date and write per-date files (write even if empty,
        # so we don't re-fetch a genuinely empty contract next run)
        by_date = {}
        for b in bars:
            d = datetime.datetime.utcfromtimestamp(b["t"] / 1000).date()
            by_date.setdefault(d, []).append(b)
        for hd in hold_dates:
            dd = f"{CACHE}/poly_minute_{hd.isoformat()}"
            os.makedirs(dd, exist_ok=True)
            recs = by_date.get(hd, [])
            with open(f"{dd}/{cfile}", "w") as f:
                json.dump({"contract": contract, "day": hd.isoformat(),
                           "fetched_at": datetime.datetime.now().isoformat(),
                           "status": status, "results": recs}, f)
        if bars:
            n_fetch += 1
        else:
            n_empty += 1
        time.sleep(0.08)  # polite pacing
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(windows)} | fetched={n_fetch} empty={n_empty} skip={n_skip} err={n_err}")

    print(f"DONE: windows={len(windows)} fetched={n_fetch} empty={n_empty} skipped={n_skip} errors={n_err}")


if __name__ == "__main__":
    main()
