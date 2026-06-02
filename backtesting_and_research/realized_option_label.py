"""
Realized-option-PnL label for enriched candidates (READ-ONLY research).

Replays the forward-paper-trader +80%/-60% bracket (with trail) on each
candidate's recommended option contract using LOCAL minute-bar cache only.
No live Polygon, no BQ writes. See task brief.

Entry  = option close at first minute bar at-or-after 10:00 ET on entry_day,
         x1.02 slippage (mirrors main.py base_entry).
Exit   = bracket (TARGET +80 / STOP -60 / TRAIL) else TIMEOUT 15:50 ET day-3.
Hold   = 3 trading days (entry_day inclusive). exit_day = entry_day + 2 td.
Intrabar precedence: STOP/TRAIL win over TARGET (conservative), matching main.py.
"""
import os, json, glob, datetime, pytz
import pandas as pd
from google.cloud import bigquery

CACHE = "/home/user/gammarips-engine/backtesting_and_research/cache"
EST = pytz.timezone("America/New_York")
STOP_PCT, TARGET_PCT = 0.60, 0.80
TRAIL_TRIGGER_PCT, TRAIL_DRAWDOWN_PCT = 0.30, 0.25
SLIP = 1.02
ENTRY_HHMM, EXIT_HHMM = (10, 0), (15, 50)
HOLD_DAYS = 3

# ---- trading-day calendar from observed daily option bars (robust to env) ----
def trading_days():
    days = set()
    for f in glob.glob(f"{CACHE}/poly_daily/*.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for b in (d.get("results") or []):
            days.add(datetime.datetime.fromtimestamp(b["t"]/1000, tz=EST).date())
    return sorted(d for d in days if datetime.date(2026,3,1) <= d <= datetime.date(2026,7,1))

TD = trading_days()
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

# ---- minute-bar loader: concat a contract's bars across the date-dirs of the hold window ----
def load_window_bars(contract_file, hold_dates):
    """Return sorted list of minute bars for `contract_file` across the
    given hold_dates, pulling from each poly_minute_<DATE> dir. Tracks which
    hold dates had a cache file present and which had bars."""
    bars = []
    dirs_present = []   # dates whose poly_minute_<DATE>/<contract> file exists
    dates_with_bars = []
    for hd in hold_dates:
        p = f"{CACHE}/poly_minute_{hd.isoformat()}/{contract_file}"
        if os.path.exists(p):
            dirs_present.append(hd)
            try:
                r = json.load(open(p)).get("results") or []
            except Exception:
                r = []
            # keep only bars that actually fall on hd (defensive)
            r = [b for b in r if datetime.datetime.fromtimestamp(b["t"]/1000, tz=EST).date() == hd]
            if r:
                dates_with_bars.append(hd)
            bars.extend(r)
    bars.sort(key=lambda b: b["t"])
    return bars, dirs_present, dates_with_bars

def ts_ms(d, hhmm):
    dt = datetime.datetime.combine(d, datetime.time(hhmm[0], hhmm[1]))
    return int(EST.localize(dt).timestamp() * 1000)

def replay_bracket(bars, entry_day, exit_day):
    """Mirror main.py mechanics. Returns dict with status + realized return."""
    entry_ts = ts_ms(entry_day, ENTRY_HHMM)
    timeout_ts = ts_ms(exit_day, EXIT_HHMM)

    entry_day_bars = [b for b in bars
                      if datetime.datetime.fromtimestamp(b["t"]/1000, tz=EST).date() == entry_day]
    entry_bar = None
    if entry_day_bars:
        after = [b for b in entry_day_bars if b["t"] >= entry_ts]
        if after:
            entry_bar = after[0]
        else:
            before = [b for b in entry_day_bars if b["t"] < entry_ts]
            entry_bar = before[-1] if before else None
    if not entry_bar or entry_bar.get("v", 0) == 0:
        return {"status": "INVALID_LIQUIDITY", "ret": None, "exit_reason": None}

    base_entry = entry_bar["c"] * SLIP
    stop = base_entry * (1 - STOP_PCT)
    target = base_entry * (1 + TARGET_PCT)
    trail_trigger = base_entry * (1 + TRAIL_TRIGGER_PCT)

    entry_idx = bars.index(entry_bar)
    peak = base_entry
    trail_active = False
    trail_level = None
    exit_reason, exit_price = "TIMEOUT", None
    last_in_window = None
    for j in range(entry_idx + 1, len(bars)):
        b = bars[j]
        if b["t"] >= timeout_ts:
            exit_reason = "TIMEOUT"
            tb = last_in_window if last_in_window is not None else b
            exit_price = tb["c"]
            break
        if b["h"] > peak:
            peak = b["h"]
            if peak >= trail_trigger:
                trail_active = True
            if trail_active:
                trail_level = peak * (1 - TRAIL_DRAWDOWN_PCT)
        eff_stop = trail_level if trail_active else stop
        eff_reason = "TRAIL" if trail_active else "STOP"
        if b["l"] <= eff_stop:
            exit_reason = eff_reason
            exit_price = eff_stop
            break
        if b["h"] >= target:
            exit_reason = "TARGET"
            exit_price = target
            break
        last_in_window = b
    if exit_price is None:
        last = last_in_window if last_in_window is not None else entry_bar
        exit_reason = "TIMEOUT"
        exit_price = last["c"]
    ret = (exit_price - base_entry) / base_entry
    return {"status": "FILLED", "ret": float(ret), "exit_reason": exit_reason,
            "entry_price": base_entry, "exit_price": exit_price}

def main():
    bq = bigquery.Client(project="profitscout-fida8")
    q = """SELECT ticker,direction,scan_date,recommended_strike,recommended_expiration,
        recommended_contract,recommended_mid_price,recommended_dte,recommended_oi,
        recommended_volume,recommended_spread_pct,moneyness_pct,volume_oi_ratio,
        call_dollar_volume,put_dollar_volume,vix3m_at_enrich,
        next_day_pct,day2_pct,day3_pct,peak_return_3d,is_win,outcome_tier
        FROM `profitscout-fida8.profit_scout.overnight_signals_enriched`
        WHERE scan_date BETWEEN '2026-04-10' AND '2026-06-01'"""
    df = bq.query(q).to_dataframe()
    print(f"loaded {len(df)} rows from BQ")

    recs = []
    for _, r in df.iterrows():
        out = {k: r[k] for k in df.columns}
        scan = r["scan_date"]
        contract = r["recommended_contract"]
        out["entry_day"] = None
        out["status"] = None
        out["realized_ret"] = None
        out["exit_reason"] = None
        out["n_hold_dirs"] = 0
        out["n_hold_bardays"] = 0

        if contract is None or pd.isna(scan):
            out["status"] = "NO_CONTRACT"
            recs.append(out); continue

        entry_day = next_td(scan)
        if entry_day is None:
            out["status"] = "NO_ENTRY_DAY"; recs.append(out); continue
        exit_day = nth_next_td(entry_day, HOLD_DAYS - 1)
        if exit_day is None:
            out["status"] = "NO_EXIT_DAY"; recs.append(out); continue
        out["entry_day"] = entry_day

        # hold dates = entry_day, +1, +2 trading days
        hold_dates = [entry_day, nth_next_td(entry_day, 1), nth_next_td(entry_day, 2)]
        hold_dates = [d for d in hold_dates if d is not None]
        cfile = contract + ".json"
        bars, dirs_present, bardays = load_window_bars(cfile, hold_dates)
        out["n_hold_dirs"] = len(dirs_present)
        out["n_hold_bardays"] = len(bardays)

        if not dirs_present:
            out["status"] = "NOT_IN_CACHE"; recs.append(out); continue
        if not bars:
            out["status"] = "CACHE_EMPTY"; recs.append(out); continue

        res = replay_bracket(bars, entry_day, exit_day)
        out["status"] = res["status"]
        out["realized_ret"] = res["ret"]
        out["exit_reason"] = res["exit_reason"]
        recs.append(out)

    res = pd.DataFrame(recs)
    res.to_pickle("/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl")
    print("saved realized_label.pkl")

    # ---- coverage summary ----
    print("\n=== STATUS COUNTS (all candidates) ===")
    print(res["status"].value_counts(dropna=False).to_string())

    # entry_day-based era buckets (minute cache covers entry_day 04-13..05-15)
    res["entry_day"] = pd.to_datetime(res["entry_day"])
    def era(d):
        if pd.isna(d): return "no_entry_day"
        d = d.date()
        if d <= datetime.date(2026,5,15): return "A_minute_cached(<=05-15)"
        return "B_beyond_minute_cache(>05-15)"
    res["era"] = res["entry_day"].apply(era)
    print("\n=== STATUS x ERA ===")
    print(pd.crosstab(res["era"], res["status"]).to_string())

    return res

if __name__ == "__main__":
    main()
