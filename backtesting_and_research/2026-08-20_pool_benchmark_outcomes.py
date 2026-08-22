"""Outcome phase for the pool-versus-benchmark test (2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-19-pool-benchmark-test-spec.md §4-§5 + AMENDMENT 2.

STEPS:
  pull     One minute-agg range call per primary leg (A re-derived, B, C)
           over [entry_day, entry_day + 2 trading days]. Resumable parquet.
  load     Load the control tape into profit_scout.control_minute_paths
           (NEW table, explicit schema, LOAD job, never autodetect; never
           option_minute_paths, which the MCP and the labeler read).
  metrics  Replay per leg with production conventions: entry 10:00 ET fill =
           bar close x 1.02 (real print within 15 min), bracket +40% / -30%
           with STOP checked before TARGET intrabar, flat 15:45 ET exit
           pays 2% on a real print within 15 min (else UNFILLABLE, not
           flat). H1 mean return A-B, H2 median MFE A-B, H3 mean return A-C,
           day-clustered bootstrap paired by scan_date, 10,000 resamples,
           90% CI. Secondary: Arm A as-delivered legs on the in-house tape.

Run:
    .venv/bin/python backtesting_and_research/2026-08-20_pool_benchmark_outcomes.py pull
    .venv/bin/python backtesting_and_research/2026-08-20_pool_benchmark_outcomes.py load
    .venv/bin/python backtesting_and_research/2026-08-20_pool_benchmark_outcomes.py metrics
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.machinery import SourceFileLoader
from zoneinfo import ZoneInfo

import db_dtypes  # noqa: F401
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SP = SourceFileLoader("sp", os.path.join(
    HERE, "2026-08-20_liquid_universe_screen_phase.py")).load_module()
SAMP = SourceFileLoader("samp", os.path.join(
    HERE, "2026-08-20_pool_benchmark_control_sampler.py")).load_module()
ET = ZoneInfo("America/New_York")
PROJECT, CACHE = SP.PROJECT, SP.CACHE
BARS_PQ = os.path.join(CACHE, "s2_outcome_bars.parquet")
RESULT_PQ = os.path.join(CACHE, "s2_outcome_legs.parquet")
CONTROL_TABLE = f"{PROJECT}.profit_scout.control_minute_paths"

SLIP, TARGET, STOP = 0.02, 0.40, 0.30
ENTRY_MIN, EXIT_MIN, TOL = 10 * 60, 15 * 60 + 45, 15
N_BOOT, SEED, CI = 10000, 42, 90


def next_td(d, n=1):
    while n > 0:
        d += dt.timedelta(days=1)
        if SP.is_trading_day(d):
            n -= 1
    return d


def legs_needed():
    lg = pd.read_parquet(SAMP.LEGS_PQ)
    lg = lg[lg.contract.notna()].copy()
    lg["scan_date"] = pd.to_datetime(lg.scan_date).dt.date
    lg["entry_day"] = [next_td(d) for d in lg.scan_date]
    lg["exit_day"] = [next_td(d, 3) for d in lg.scan_date]
    return lg


# ------------------------------------------------------------------ pull
def cmd_pull():
    key = SP.polygon_key()
    lg = legs_needed().drop_duplicates(["scan_date", "contract"])
    have, frames = set(), []
    if os.path.exists(BARS_PQ):
        old = pd.read_parquet(BARS_PQ)
        old["scan_date"] = pd.to_datetime(old.scan_date).dt.date
        have = set(zip(old.scan_date, old.contract))
        frames.append(old)
    todo = [r for r in lg.itertuples() if (r.scan_date, r.contract) not in have]
    print(f"pull: {len(lg)} unique legs, cached {len(have)}, todo {len(todo)}",
          flush=True)

    def one(r):
        j = SP.get_json(
            f"https://api.polygon.io/v2/aggs/ticker/{r.contract}/range/1/minute/"
            f"{r.entry_day}/{r.exit_day}",
            {"adjusted": "true", "limit": 50000, "apiKey": key})
        if j is None:
            return None
        rows = [{"scan_date": r.scan_date, "entry_day": r.entry_day,
                 "contract": r.contract, "ticker": r.ticker, "t": b["t"],
                 "open": b["o"], "high": b["h"], "low": b["l"], "close": b["c"],
                 "volume": b["v"], "vwap": b.get("vw"),
                 "transactions": b.get("n")} for b in (j.get("results") or [])]
        return pd.DataFrame(rows) if rows else pd.DataFrame([{
            "scan_date": r.scan_date, "entry_day": r.entry_day,
            "contract": r.contract, "ticker": r.ticker, "t": np.nan}])

    failed = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, f in enumerate(as_completed([ex.submit(one, r) for r in todo]), 1):
            df = f.result()
            if df is None:
                failed += 1
            else:
                frames.append(df)
            if i % 500 == 0:
                print(f"  {i}/{len(todo)}, failed {failed}", flush=True)
    allb = pd.concat(frames, ignore_index=True)
    allb.to_parquet(BARS_PQ)
    print(f"pull done: failed {failed} (count what answered), bars"
          f" {int(allb.t.notna().sum())}")


# ------------------------------------------------------------------ load
def cmd_load():
    from google.cloud import bigquery
    b = pd.read_parquet(BARS_PQ)
    b = b[b.t.notna()].copy()
    ts = pd.to_datetime(b.t, unit="ms", utc=True)
    b["ts"] = ts
    b["bar_date"] = ts.dt.tz_convert(ET).dt.date
    b["scan_date"] = pd.to_datetime(b.scan_date).dt.date
    b["entry_day"] = pd.to_datetime(b.entry_day).dt.date
    # day_index 1..3 by distinct ET session date per leg.
    b = b.sort_values(["scan_date", "contract", "t"])
    b["day_index"] = (b.groupby(["scan_date", "contract"]).bar_date
                      .transform(lambda s: s.rank(method="dense")).astype(int))
    b["source"] = "polygon minute aggs (study 2 control tape 2026-08-20)"
    b["ingested_at"] = pd.Timestamp.utcnow()
    cols = ["scan_date", "entry_day", "contract", "ticker", "ts", "bar_date",
            "day_index", "open", "high", "low", "close", "volume", "vwap",
            "transactions", "source", "ingested_at"]
    schema = [
        bigquery.SchemaField("scan_date", "DATE", "REQUIRED"),
        bigquery.SchemaField("entry_day", "DATE", "REQUIRED"),
        bigquery.SchemaField("contract", "STRING", "REQUIRED"),
        bigquery.SchemaField("ticker", "STRING"),
        bigquery.SchemaField("ts", "TIMESTAMP", "REQUIRED"),
        bigquery.SchemaField("bar_date", "DATE"),
        bigquery.SchemaField("day_index", "INTEGER"),
        bigquery.SchemaField("open", "FLOAT"), bigquery.SchemaField("high", "FLOAT"),
        bigquery.SchemaField("low", "FLOAT"), bigquery.SchemaField("close", "FLOAT"),
        bigquery.SchemaField("volume", "FLOAT"), bigquery.SchemaField("vwap", "FLOAT"),
        bigquery.SchemaField("transactions", "INTEGER"),
        bigquery.SchemaField("source", "STRING"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP"),
    ]
    client = bigquery.Client(project=PROJECT)
    job = client.load_table_from_dataframe(
        b[cols], CONTROL_TABLE,
        job_config=bigquery.LoadJobConfig(
            schema=schema, autodetect=False,
            write_disposition="WRITE_TRUNCATE",
            time_partitioning=bigquery.TimePartitioning(field="entry_day"),
            clustering_fields=["contract"]))
    job.result()
    print(f"loaded {len(b)} rows into {CONTROL_TABLE} (WRITE_TRUNCATE)")


# ------------------------------------------------------------------ replay
def replay(bars: pd.DataFrame, entry_day: dt.date) -> dict:
    out = {"status": "NO_BARS"}
    b = bars[bars.t.notna()].copy()
    if b.empty:
        return out
    ts = pd.to_datetime(b.t, unit="ms", utc=True).dt.tz_convert(ET)
    b["d"], b["m"] = ts.dt.date, ts.dt.hour * 60 + ts.dt.minute
    e = b[(b.d == entry_day) & (b.m >= 9 * 60 + 30) & (b.m <= 16 * 60)].sort_values("m")
    out["prints_by_1000"] = int((e.m <= ENTRY_MIN).sum())
    ent = e[(e.m >= ENTRY_MIN) & (e.m <= ENTRY_MIN + TOL)]
    if ent.empty:
        out["status"] = "UNFILLABLE_ENTRY"
        return out
    fb = ent.iloc[0]
    fill = float(fb.close) * (1 + SLIP)
    tgt, stp = fill * (1 + TARGET), fill * (1 - STOP)
    path = e[e.m > fb.m]
    mfe = (path.high.max() - fill) / fill if len(path) else 0.0
    mae = (path.low.min() - fill) / fill if len(path) else 0.0
    for r in path.itertuples():
        if r.m > EXIT_MIN:
            break
        if r.low <= stp:  # STOP before TARGET intrabar (conservative)
            return {"status": "STOP", "ret": min(stp, r.low, r.open) * (1 - SLIP) / fill - 1,
                    "mfe": mfe, "mae": mae, "prints_by_1000": out["prints_by_1000"]}
        if r.high >= tgt:
            return {"status": "TARGET", "ret": tgt * (1 - SLIP) / fill - 1,
                    "mfe": mfe, "mae": mae, "prints_by_1000": out["prints_by_1000"]}
    ex = path[(path.m >= EXIT_MIN - TOL) & (path.m <= EXIT_MIN)]
    if ex.empty:
        return {"status": "UNFILLABLE_EXIT", "mfe": mfe, "mae": mae,
                "prints_by_1000": out["prints_by_1000"]}
    return {"status": "TIMEOUT", "ret": float(ex.iloc[-1].close) * (1 - SLIP) / fill - 1,
            "mfe": mfe, "mae": mae, "prints_by_1000": out["prints_by_1000"]}


def boot(A: pd.DataFrame, X: pd.DataFrame, col: str, stat, rng):
    days = sorted(set(A.scan_date) | set(X.scan_date))
    a_by = {d: g[col].to_numpy() for d, g in A.groupby("scan_date")}
    x_by = {d: g[col].to_numpy() for d, g in X.groupby("scan_date")}
    point = stat(A[col]) - stat(X[col])
    s = []
    for _ in range(N_BOOT):
        pick = rng.choice(days, len(days), replace=True)
        a = np.concatenate([a_by[d] for d in pick if d in a_by])
        x = np.concatenate([x_by[d] for d in pick if d in x_by])
        s.append(stat(a) - stat(x))
    lo, hi = np.percentile(s, [(100 - CI) / 2, 100 - (100 - CI) / 2])
    return point, lo, hi


def cmd_metrics():
    lg = legs_needed()
    bars = pd.read_parquet(BARS_PQ)
    bars["scan_date"] = pd.to_datetime(bars.scan_date).dt.date
    res = {}
    for (s, c), g in bars.groupby(["scan_date", "contract"]):
        res[(s, c)] = replay(g, next_td(s))
    R = pd.DataFrame([{"scan_date": s, "contract": c, **v} for (s, c), v in res.items()])
    lg = lg.merge(R, on=["scan_date", "contract"], how="left")
    lg.to_parquet(RESULT_PQ)
    filled = lg[lg.status.isin(["STOP", "TARGET", "TIMEOUT"])]
    print("PRIMARY ARMS (reduced rule for all arms, AMENDMENT 2)")
    for arm in "ABC":
        X = lg[lg.arm == arm]
        Xf = filled[filled.arm == arm]
        print(f"  {arm}: legs {len(X):>5} | filled {len(Xf):>5}"
              f" ({len(Xf) / max(1, len(X)) * 100:4.0f}%) | status"
              f" {X.status.value_counts().to_dict()} | mean ret"
              f" {Xf.ret.mean() * 100:6.2f}% | median MFE {Xf.mfe.median() * 100:5.1f}%")
    A, B, C = (filled[filled.arm == a] for a in "ABC")
    rng = np.random.default_rng(SEED)
    print(f"\nHYPOTHESES (day-clustered bootstrap {N_BOOT} x, {CI}% CI)")
    h1 = boot(A, B, "ret", np.mean, rng)
    h2 = boot(A, B, "mfe", np.median, rng)
    h3 = boot(A, C, "ret", np.mean, rng)
    for tag, (pt, lo, hi) in (("H1 mean ret A-B", h1), ("H2 median MFE A-B", h2),
                              ("H3 mean ret A-C", h3)):
        verdict = "SURVIVES" if lo > 0 else "REJECTED (CI includes 0 or below)"
        print(f"  {tag:<20} {pt * 100:6.2f}pp  CI [{lo * 100:.2f}, {hi * 100:.2f}]  {verdict}")
    if h1[1] > 0 or h2[1] > 0:
        rule = "H1 or H2 survives -> selection carries measurable value; keep the scan"
    elif h3[1] > 0:
        rule = ("H1+H2 fail, H3 survives -> flow signal adds nothing, liquidity +"
                " contract machinery does; retire the scan as a ranking device")
    else:
        rule = ("All three fail -> pool not distinguishable from matched random"
                " optionable contracts; the scan is not a selection edge")
    print(f"\nDECISION RULE: {rule}")
    print("  Power: detects ~5pp per trade, cannot detect 1-2pp. A null means"
          " 'no large edge', never 'no edge'.")
    secondary_delivered(lg)


def secondary_delivered(lg):
    from google.cloud import bigquery
    lo, hi = min(lg.scan_date), max(lg.scan_date)
    df = bigquery.Client(project=PROJECT).query(f"""
      SELECT p.scan_date, p.recommended_contract AS contract,
             UNIX_MILLIS(t.ts) AS t, t.open, t.high, t.low, t.close
      FROM `{PROJECT}.profit_scout.enriched_option_outcomes` p
      JOIN `{PROJECT}.profit_scout.option_minute_paths` t
        ON t.scan_date = p.scan_date AND t.contract = p.recommended_contract
      WHERE p.scan_date BETWEEN '{lo}' AND '{hi}'""").to_dataframe()
    df["scan_date"] = pd.to_datetime(df.scan_date).dt.date
    rows = [{"scan_date": s, "contract": c, **replay(g, next_td(s))}
            for (s, c), g in df.groupby(["scan_date", "contract"])]
    S = pd.DataFrame(rows)
    Sf = S[S.status.isin(["STOP", "TARGET", "TIMEOUT"])]
    print(f"\nSECONDARY (labeled): Arm A AS-DELIVERED contracts on the in-house"
          f" tape: legs {len(S)} | filled {len(Sf)} | mean ret"
          f" {Sf.ret.mean() * 100:.2f}% | median MFE {Sf.mfe.median() * 100:.1f}%")


if __name__ == "__main__":
    {"pull": cmd_pull, "load": cmd_load, "metrics": cmd_metrics}.get(
        sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
