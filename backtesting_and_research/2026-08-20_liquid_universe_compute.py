"""Compute step for the liquid-universe funnel study (2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-20-liquid-universe-funnel-spec.md (FROZEN).
Inputs: the screen-phase caches (grouped stock bars, as-of universe,
top-300 pre-rank) and the per-name chain store lu_chain_aggs/.
This script STOPS before any outcome pull: the spec requires the concrete
outcome-pull budget to be reported to the owner first.

STEPS:
  aggregate  Per (name, session): chain dollar volume, call and put dollar
             volume, from the chain store (volume x vwap x 100).
  rank       Per scan session: eligible = pre-rank top-300 with strikes >= 25
             (reference as_of) and a chain store present. Score =
             z_cross(log1p(chain $)) + z_cross(log1p(share volume)) across
             the eligible set. Ties: share volume desc, ticker asc.
             NOTE (spec implication): z_cross runs over the eligible
             pre-rank-300 subset, because the spec scopes the chain rebuild
             to that subset.
  signal     UOA = call dollar volume. z vs the trailing 20 sessions
             (T exclusive, >= 15 valid). Admit z >= 2.0 AND call $ > put $.
  arms       Decision cell N=100, z=2.0. Rails (VIX <= VIX3M day skip,
             earnings window [T, entry+2td]) on B and C identically. B = top
             50 by z. C = 200 seeded draws (default_rng(42)) of |B_d| names
             from top-100 minus B_d minus earnings exclusions. Contract =
             the reduced rule (sampler script), splits checked.
  sensitivity Composition metrics only for N in {50,100,200}, z in
             {1.5,2.0,3.0}. Never outcomes.
  budget     Outcome minute-agg call budget. Report. STOP.

Run:
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_compute.py all
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from importlib.machinery import SourceFileLoader

import db_dtypes  # noqa: F401
import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SP = SourceFileLoader("sp", os.path.join(
    HERE, "2026-08-20_liquid_universe_screen_phase.py")).load_module()
SAMP = SourceFileLoader("samp", os.path.join(
    HERE, "2026-08-20_pool_benchmark_control_sampler.py")).load_module()
PROJECT, CACHE, CHAIN_DIR = SP.PROJECT, SP.CACHE, SP.CHAIN_DIR
DAILY_PQ = os.path.join(CACHE, "lu_chain_daily.parquet")
RANK_PQ = os.path.join(CACHE, "lu_rank.parquet")
SIGNAL_PQ = os.path.join(CACHE, "lu_signal.parquet")
ARMS_PQ = os.path.join(CACHE, "lu_arms.parquet")
EARN_JSON = os.path.join(CACHE, "lu_earnings.json")
SPLITS_JSON = os.path.join(CACHE, "lu_splits.json")

Z_DEC, N_DEC = 2.0, 100
POOL_CAP = 50
BASE_N, BASE_MIN_VALID = 20, 15
M_DRAWS, SEED = 200, 42
N_CELLS, Z_CELLS = (50, 100, 200), (1.5, 2.0, 3.0)


def fmp_key() -> str:
    return subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=FMP_API_KEY", f"--project={PROJECT}"],
        capture_output=True, text=True, check=True).stdout.strip()


def next_td(d: dt.date, n: int = 1) -> dt.date:
    while n > 0:
        d += dt.timedelta(days=1)
        if SP.is_trading_day(d):
            n -= 1
    return d


def sessions_all() -> list[dt.date]:
    return SP.trading_days(SP.PULL_FIRST, SP.PULL_LAST)


# ------------------------------------------------------------------ aggregate
def cmd_aggregate():
    pr = pd.read_parquet(SP.PRERANK_PQ)
    names = sorted(pr.ticker.unique())
    frames, missing = [], []
    for n in names:
        p = os.path.join(CHAIN_DIR, f"{n}.parquet")
        if not os.path.exists(p):
            missing.append(n)
            continue
        c = pd.read_parquet(p, columns=["type", "session", "volume", "vwap"])
        c["dollar"] = c.volume * c.vwap * 100
        g = c.groupby(["session", "type"]).dollar.sum().unstack(fill_value=0)
        g = g.reindex(columns=["call", "put"], fill_value=0)
        g["ticker"] = n
        frames.append(g.reset_index())
    d = pd.concat(frames, ignore_index=True)
    d["session"] = pd.to_datetime(d.session).dt.date
    d = d.rename(columns={"call": "call_dollar", "put": "put_dollar"})
    d["chain_dollar"] = d.call_dollar + d.put_dollar
    d.to_parquet(DAILY_PQ)
    print(f"aggregate: {len(names)} names, {len(missing)} without a chain"
          f" store (excluded, reported): {missing[:20]}")
    print(f"  rows {len(d)}, sessions {d.session.nunique()}")


# ------------------------------------------------------------------ rank
def cmd_rank():
    key = SP.polygon_key()
    pr = pd.read_parquet(SP.PRERANK_PQ)
    pr["session"] = pd.to_datetime(pr.session).dt.date
    daily = pd.read_parquet(DAILY_PQ)
    have_store = set(daily.ticker.unique())
    strikes = SAMP.load_json(SAMP.STRIKES_JSON)
    pairs = [(r.ticker, r.session) for r in pr.itertuples()
             if f"{r.ticker}|{r.session}" not in strikes]
    print(f"rank: strikes as_of lookups to fetch: {len(pairs)}", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        list(ex.map(lambda p: SAMP.strikes_asof(key, p[0], p[1], strikes),
                    pairs))
    json.dump(strikes, open(SAMP.STRIKES_JSON, "w"))
    out = []
    for d, day in pr.groupby("session"):
        day = day.copy()
        assert (day.volume >= SP.UND_VOL_FLOOR).all(), f"{d}: pre-rank below 3M"
        day["strikes"] = [strikes.get(f"{t}|{d}", -1) for t in day.ticker]
        day["in_store"] = day.ticker.isin(have_store)
        elig = day[(day.strikes >= SAMP.STRIKES_FLOOR) & day.in_store].copy()
        cd = daily[daily.session == d].set_index("ticker").chain_dollar
        elig["chain_dollar"] = elig.ticker.map(cd).fillna(0.0)
        lc, lv = np.log1p(elig.chain_dollar), np.log1p(elig.volume)
        elig["score"] = ((lc - lc.mean()) / lc.std(ddof=0)
                         + (lv - lv.mean()) / lv.std(ddof=0))
        elig = elig.sort_values(["score", "volume", "ticker"],
                                ascending=[False, False, True])
        elig["liquid_rank"] = range(1, len(elig) + 1)
        elig["n_eligible"] = len(elig)
        elig["n_strikes_fail"] = int((day.strikes < SAMP.STRIKES_FLOOR).sum())
        elig["n_no_store"] = int((~day.in_store).sum())
        out.append(elig[["session", "ticker", "volume", "chain_dollar",
                         "score", "liquid_rank", "n_eligible",
                         "n_strikes_fail", "n_no_store"]])
    rk = pd.concat(out, ignore_index=True)
    rk.to_parquet(RANK_PQ)
    per = rk.groupby("session").n_eligible.first()
    print(f"  eligible per session: min {per.min()} median {per.median():.0f}"
          f" max {per.max()} | strikes<25 median"
          f" {rk.groupby('session').n_strikes_fail.first().median():.0f}"
          f" | no chain store median"
          f" {rk.groupby('session').n_no_store.first().median():.0f}")


# ------------------------------------------------------------------ signal
def cmd_signal():
    rk = pd.read_parquet(RANK_PQ)
    rk["session"] = pd.to_datetime(rk.session).dt.date
    daily = pd.read_parquet(DAILY_PQ)
    daily["session"] = pd.to_datetime(daily.session).dt.date
    sess = sessions_all()
    idx = {s: i for i, s in enumerate(sess)}
    piv = daily.pivot_table(index="ticker", columns="session",
                            values=["call_dollar", "put_dollar"],
                            aggfunc="sum").reindex(columns=sess, level=1)
    call = piv["call_dollar"].reindex(columns=sess)
    put = piv["put_dollar"].reindex(columns=sess)
    out = []
    for r in rk[rk.liquid_rank <= max(N_CELLS)].itertuples():
        i = idx[r.session]
        base = call.loc[r.ticker].iloc[max(0, i - BASE_N):i]
        # A name present in the store has a valid session everywhere in the
        # pulled window (0 failed contract pulls); a session with no rows is
        # a true zero. Validity = the session lies inside the pulled window.
        valid = base.fillna(0.0)
        n_valid = min(i, BASE_N)
        lb = np.log1p(valid)
        mu, sd = lb.mean(), lb.std(ddof=1)
        c_t = float(np.nan_to_num(call.loc[r.ticker, r.session]))
        p_t = float(np.nan_to_num(put.loc[r.ticker, r.session]))
        z = (np.log1p(c_t) - mu) / sd if (n_valid >= BASE_MIN_VALID
                                          and sd > 0) else np.nan
        out.append({"session": r.session, "ticker": r.ticker,
                    "liquid_rank": r.liquid_rank, "n_valid": n_valid,
                    "call_dollar": c_t, "put_dollar": p_t, "z": z,
                    "bullish": c_t > p_t})
    sg = pd.DataFrame(out)
    sg.to_parquet(SIGNAL_PQ)
    adm = sg[(sg.z >= Z_DEC) & sg.bullish & (sg.liquid_rank <= N_DEC)]
    print(f"signal: {len(sg)} (name, session) rows | baseline-ineligible"
          f" {int(sg.z.isna().sum())}")
    print(f"  decision cell N=100 z>=2.0 bullish: {len(adm)} admissions on"
          f" {adm.session.nunique()} sessions"
          f" (per-day median {adm.groupby('session').size().median():.0f})")


# ------------------------------------------------------------------ arms
def vix_skip_days() -> set[dt.date]:
    from google.cloud import bigquery
    df = bigquery.Client(project=PROJECT).query(f"""
      SELECT scan_date FROM `{PROJECT}.profit_scout.enriched_option_outcomes`
      WHERE scan_date BETWEEN '{SP.PULL_FIRST}' AND '{SP.PULL_LAST}'
      GROUP BY scan_date
      HAVING ANY_VALUE(vix_at_scan) > ANY_VALUE(vix3m_at_enrich)""").to_dataframe()
    return set(pd.to_datetime(df.scan_date).dt.date)


def earnings_window(key: str, lo: dt.date, hi: dt.date, cache: dict) -> set:
    k = f"{lo}|{hi}"
    if k not in cache:
        r = requests.get("https://financialmodelingprep.com/stable/earnings-calendar",
                         params={"from": lo.isoformat(), "to": hi.isoformat()},
                         headers={"apikey": key}, timeout=30)
        j = r.json() if r.status_code == 200 else None
        cache[k] = sorted({x.get("symbol") for x in j}) if isinstance(j, list) else None
    return cache[k]


def has_split(key: str, name: str, lo: dt.date, hi: dt.date, cache: dict) -> bool:
    k = f"{name}|{lo}|{hi}"
    if k not in cache:
        j = SP.get_json("https://api.polygon.io/v3/reference/splits",
                        {"ticker": name, "execution_date.gte": lo.isoformat(),
                         "execution_date.lte": hi.isoformat(), "apiKey": key})
        cache[k] = bool((j or {}).get("results")) if j is not None else None
    return cache[k]


def cmd_arms():
    pkey, fkey = SP.polygon_key(), fmp_key()
    sg = pd.read_parquet(SIGNAL_PQ)
    sg["session"] = pd.to_datetime(sg.session).dt.date
    g = SAMP.grouped()
    earn, splits = SAMP.load_json(EARN_JSON), SAMP.load_json(SPLITS_JSON)
    skip = vix_skip_days()
    rng = np.random.default_rng(SEED)
    chains = {}

    def chain(n):
        if n not in chains:
            c = pd.read_parquet(os.path.join(CHAIN_DIR, f"{n}.parquet"))
            c["session"] = pd.to_datetime(c.session).dt.date
            chains[n] = c
        return chains[n]

    def leg(d, n, arm, draw, z):
        day = g[(g.session == d) & (g.ticker == n)]
        und_close = float(day.close.iloc[0]) if len(day) else None
        r = SAMP.reduced_rule(chain(n), d, und_close)
        if r is None:
            return None
        return {"session": d, "arm": arm, "draw": draw, "ticker": n, "z": z,
                "contract": r.contract, "strike": r.strike,
                "expiration": r.expiration, "dte": int(r.dte),
                "moneyness": float(r.moneyness), "volume": float(r.volume),
                "und_close": und_close}

    legs, report = [], []
    for d in SP.s1_scan_days():
        if d in skip:
            report.append((d, "VIX_RAIL_SKIP", 0, 0, 0))
            continue
        entry, exit_day = next_td(d), next_td(d, 3)
        ex_set = earnings_window(fkey, d, exit_day, earn)
        if ex_set is None:
            report.append((d, "EARNINGS_CAL_UNAVAILABLE_FAIL_CLOSED", 0, 0, 0))
            continue
        top = sg[(sg.session == d) & (sg.liquid_rank <= N_DEC)]
        top = top[~top.ticker.isin(ex_set)]
        b = top[(top.z >= Z_DEC) & top.bullish].sort_values(
            ["z", "ticker"], ascending=[False, True]).head(POOL_CAP)
        if b.empty:
            report.append((d, "EMPTY_B", 0, 0, len(top)))
            continue
        nb = 0
        for r in b.itertuples():
            if has_split(pkey, r.ticker, d, exit_day, splits):
                legs.append({"session": d, "arm": "B", "draw": 0,
                             "ticker": r.ticker, "z": r.z, "contract": None,
                             "excluded": "SPLIT"})
                continue
            L = leg(d, r.ticker, "B", 0, r.z)
            if L:
                legs.append(L)
                nb += 1
        pool_c = sorted(set(top.ticker) - set(b.ticker))
        k = len(b)
        nc = 0
        if len(pool_c) >= k:
            for m in range(M_DRAWS):
                for n in rng.choice(pool_c, k, replace=False):
                    if has_split(pkey, n, d, exit_day, splits):
                        continue
                    L = leg(d, n, "C", m + 1, np.nan)
                    if L:
                        legs.append(L)
                        nc += 1
        report.append((d, "OK", len(b), nb, nc))
    json.dump(earn, open(EARN_JSON, "w"))
    json.dump(splits, open(SPLITS_JSON, "w"))
    lg = pd.DataFrame(legs)
    lg.to_parquet(ARMS_PQ)
    rep = pd.DataFrame(report, columns=["session", "status", "B_names",
                                        "B_legs", "C_legs"])
    ok = rep[rep.status == "OK"]
    print("arms (decision cell N=100, z>=2.0):")
    print(f"  sessions: {len(rep)} | OK {len(ok)} | skipped:"
          f" {rep[rep.status != 'OK'].status.value_counts().to_dict()}")
    print(f"  Arm B names/day: median {ok.B_names.median():.0f}"
          f" (min {ok.B_names.min()}, max {ok.B_names.max()}) |"
          f" B legs total {ok.B_legs.sum()} on {int((ok.B_legs > 0).sum())}"
          f" non-empty days")
    print(f"  splits excluded: {int((lg.get('excluded') == 'SPLIT').sum())}")
    print(f"  C legs total (200 draws) {ok.C_legs.sum()} | unique C contracts"
          f" {lg[lg.arm == 'C'].contract.nunique()}")
    r0 = (ok.B_legs.sum() >= 150) and ((ok.B_legs > 0).sum() >= 30)
    print(f"  RULE 0 pre-check (>=150 B legs AND >=30 non-empty days):"
          f" {'PASS' if r0 else 'FAIL -> INSUFFICIENT SAMPLE'}"
          " (fillability still to be checked on tape)")


# ------------------------------------------------------------------ sensitivity
def cmd_sensitivity():
    from google.cloud import bigquery
    sg = pd.read_parquet(SIGNAL_PQ)
    sg["session"] = pd.to_datetime(sg.session).dt.date
    rk = pd.read_parquet(RANK_PQ)
    rk["session"] = pd.to_datetime(rk.session).dt.date
    pool = bigquery.Client(project=PROJECT).query(f"""
      SELECT scan_date, ticker FROM `{PROJECT}.profit_scout.enriched_option_outcomes`
      WHERE scan_date BETWEEN '{SP.PULL_FIRST}' AND '{SP.PULL_LAST}'""").to_dataframe()
    pool["scan_date"] = pd.to_datetime(pool.scan_date).dt.date
    a_sets = pool.groupby("scan_date").ticker.apply(set).to_dict()
    print("\nSENSITIVITY (screen composition only, never outcomes)")
    print(f"{'N':>4}{'z':>5}{'depth mean':>12}{'depth med':>11}"
          f"{'empty days':>12}{'overlap w/ A':>14}{'med und vol(M)':>16}"
          f"{'med chain $(M)':>16}")
    for N in N_CELLS:
        for z in Z_CELLS:
            adm = sg[(sg.liquid_rank <= N) & (sg.z >= z) & sg.bullish]
            adm = adm.sort_values(["session", "z"], ascending=[True, False])
            adm = adm.groupby("session").head(POOL_CAP)
            depth = adm.groupby("session").size().reindex(
                SP.s1_scan_days(), fill_value=0)
            ov = []
            for d, grp in adm.groupby("session"):
                a = a_sets.get(d, set())
                bset = set(grp.ticker)
                if a and bset:
                    ov.append(len(a & bset) / len(a | bset))
            liq = adm.merge(rk[["session", "ticker", "volume", "chain_dollar"]],
                            on=["session", "ticker"], how="left")
            print(f"{N:>4}{z:>5.1f}{depth.mean():>12.1f}{depth.median():>11.0f}"
                  f"{int((depth == 0).sum()):>12}"
                  f"{(np.mean(ov) if ov else float('nan')):>14.3f}"
                  f"{liq.volume.median() / 1e6:>16.1f}"
                  f"{liq.chain_dollar.median() / 1e6:>16.1f}")


# ------------------------------------------------------------------ budget
def cmd_budget():
    lg = pd.read_parquet(ARMS_PQ)
    lg = lg[lg.contract.notna()]
    b = lg[lg.arm == "B"]
    c_unique = lg[lg.arm == "C"].drop_duplicates(["session", "contract"])
    n = len(b) + len(c_unique)
    print("\nOUTCOME-PULL BUDGET (decision cell only; spec: report BEFORE"
          " pulling)")
    print(f"  B legs {len(b)} + unique C (session, contract) {len(c_unique)}"
          f" = {n} legs")
    print(f"  minute aggs: {n} legs x 3 trading days = {3 * n:,} calls"
          f" (or {n:,} range calls); at 16 workers ~{3 * n / 16 / 5 / 60:.0f}"
          " min")
    print("  STOP. Outcome pull waits for the owner's budget acknowledgement.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    steps = (["aggregate", "rank", "signal", "arms", "sensitivity", "budget"]
             if cmd == "all" else [cmd])
    for s in steps:
        print(f"== {s}", flush=True)
        globals()[f"cmd_{s}"]()
