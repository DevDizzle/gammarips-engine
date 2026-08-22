"""Control sampler for the pool-versus-benchmark test (2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-19-pool-benchmark-test-spec.md + AMENDMENT 2
(owner option 3, 2026-08-20): the reduced volume-based contract rule for
ALL arms, the oi bar replaced by the volume floor, delivered Arm A as a
labeled secondary.

STEPS (cache under backtesting_and_research/cache/, shares the chain store
lu_chain_aggs/ with the liquid-universe screen phase):
  profile   Pool names per scan date + underlying volume decile (deciles
            over the as-of universe) + sector (Polygon SIC, one source for
            every arm; the scanner's own sector column is 'Other' or blank
            on ~45% of rows).
  draw      Seeded draws (numpy default_rng(42)). Arm B: 20 names per date
            matched on decile and on sector where the pool has >= 3 names,
            from candidates passing the research bar (und_vol >= 3M,
            strikes >= 25 via reference as_of). Arm C: 10 names uniform
            from the as-of universe minus the pool. Each slot also gets one
            backup draw, used only when the primary yields no contract.
  contracts Pull option day bars for every name the draws need (same
            per-name store as the screen phase).
  select    The reduced rule on session T: calls, DTE 7..45, moneyness
            0.90..1.25 vs the session-T close, volume >= 500, pick max
            volume. Ties: nearest 10% OTM, nearest expiry, lowest strike.
            Applied to Arm A (pool names), B, and C identically.
  balance   The §9 step-3 balance table. Publish it BEFORE the full pull.

Run (dry run, 3 dates):
    .venv/bin/python backtesting_and_research/2026-08-20_pool_benchmark_control_sampler.py all --dates 2026-04-23,2026-06-17,2026-08-06
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from importlib.machinery import SourceFileLoader

import db_dtypes  # noqa: F401
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SP = SourceFileLoader(
    "sp", os.path.join(HERE, "2026-08-20_liquid_universe_screen_phase.py")
).load_module()
PROJECT = SP.PROJECT
CACHE = SP.CACHE
CHAIN_DIR = SP.CHAIN_DIR
SIC_JSON = os.path.join(CACHE, "s2_sic.json")
STRIKES_JSON = os.path.join(CACHE, "s2_strikes_asof.json")
PROFILE_PQ = os.path.join(CACHE, "s2_pool_profile.parquet")
DRAWS_PQ = os.path.join(CACHE, "s2_draws.parquet")
LEGS_PQ = os.path.join(CACHE, "s2_legs.parquet")
S2_MANIFEST = os.path.join(CHAIN_DIR, "_manifest_s2.json")

SEED = 42
N_B, N_C = 20, 10
UND_VOL_FLOOR = 3_000_000
STRIKES_FLOOR = 25
DTE_LO, DTE_HI = 7, 45
MONEY_LO, MONEY_HI = 0.90, 1.25
VOL_FLOOR = 500
OTM_TARGET = 1.10

SIC_SECTORS = [  # 2-digit SIC major group -> the scanner's label set
    ((1, 9), "Basic Materials"), ((10, 14), "Energy"),
    ((15, 17), "Industrials"), ((20, 21), "Consumer Defensive"),
    ((22, 27), "Consumer Cyclical"), ((28, 28), "Healthcare"),
    ((29, 29), "Energy"), ((30, 34), "Basic Materials"),
    ((35, 36), "Technology"), ((37, 37), "Industrials"),
    ((38, 38), "Healthcare"), ((39, 39), "Consumer Cyclical"),
    ((40, 47), "Industrials"), ((48, 48), "Communication Services"),
    ((49, 49), "Utilities"), ((50, 51), "Industrials"),
    ((52, 59), "Consumer Cyclical"), ((60, 64), "Financial Services"),
    ((65, 65), "Real Estate"), ((67, 67), "Financial Services"),
    ((70, 79), "Consumer Cyclical"), ((80, 80), "Healthcare"),
    ((81, 89), "Technology"),
]


def load_json(p):
    return json.load(open(p)) if os.path.exists(p) else {}


def grouped():
    g = pd.read_parquet(SP.GROUPED_PQ)
    g["session"] = pd.to_datetime(g.session).dt.date
    return g


def universe():
    u = pd.read_parquet(SP.UNIVERSE_PQ)
    u["live_from"] = pd.to_datetime(u.live_from).dt.date
    return u


def pool_dates(dates: list[dt.date] | None) -> list[dt.date]:
    from google.cloud import bigquery
    sql = f"""SELECT DISTINCT scan_date FROM
      `{PROJECT}.profit_scout.enriched_option_outcomes`
      WHERE scan_date BETWEEN '{SP.PULL_FIRST}' AND '{SP.PULL_LAST}'
      ORDER BY scan_date"""
    all_d = [pd.Timestamp(x).date() for x in
             bigquery.Client(project=PROJECT).query(sql).to_dataframe().scan_date]
    return [d for d in all_d if dates is None or d in dates]


def sector_of(key: str, name: str, sic: dict) -> str:
    if name not in sic:
        j = SP.get_json(f"https://api.polygon.io/v3/reference/tickers/{name}",
                        {"apiKey": key})
        code = ((j or {}).get("results") or {}).get("sic_code")
        sic[name] = code or ""
    code = sic[name]
    if not code:
        return "Other"
    mg = int(str(code)[:2])
    for (lo, hi), lab in SIC_SECTORS:
        if lo <= mg <= hi:
            return lab
    return "Other"


def strikes_asof(key: str, name: str, d: dt.date, cache: dict) -> int:
    k = f"{name}|{d}"
    if k not in cache:
        j = SP.get_json("https://api.polygon.io/v3/reference/options/contracts",
                        {"underlying_ticker": name, "as_of": d.isoformat(),
                         "limit": 1000, "apiKey": key})
        rows = (j or {}).get("results") or []
        cache[k] = len({r.get("strike_price") for r in rows}) if j else -1
    return cache[k]


# ------------------------------------------------------------------ profile
def cmd_profile(dates):
    from google.cloud import bigquery
    key = SP.polygon_key()
    g, u, sic = grouped(), universe(), load_json(SIC_JSON)
    dl = ",".join(f"'{d}'" for d in dates)
    pool = bigquery.Client(project=PROJECT).query(f"""
      SELECT scan_date, ticker, recommended_contract, recommended_dte,
             moneyness_pct
      FROM `{PROJECT}.profit_scout.enriched_option_outcomes`
      WHERE scan_date IN ({dl})""").to_dataframe()
    pool["scan_date"] = pd.to_datetime(pool.scan_date).dt.date
    rows = []
    for d in dates:
        uni = SP.universe_asof(d, u)
        day = g[(g.session == d) & g.ticker.isin(uni)].copy()
        day["decile"] = pd.qcut(day.volume.rank(method="first"), 10,
                                labels=False) + 1
        pd_ = pool[pool.scan_date == d].merge(
            day[["ticker", "volume", "close", "decile"]], on="ticker",
            how="left")
        pd_["sector"] = [sector_of(key, t, sic) for t in pd_.ticker]
        rows.append(pd_)
    prof = pd.concat(rows, ignore_index=True)
    json.dump(sic, open(SIC_JSON, "w"))
    prof.to_parquet(PROFILE_PQ)
    miss = prof.volume.isna().sum()
    print(f"profile: {len(prof)} pool legs on {len(dates)} dates;"
          f" {miss} without grouped volume (not in as-of universe or no bar)")
    print("  decile share:", prof.decile.value_counts(normalize=True)
          .sort_index().round(2).to_dict())


# ------------------------------------------------------------------ draw
def cmd_draw(dates):
    key = SP.polygon_key()
    g, u = grouped(), universe()
    sic, strikes = load_json(SIC_JSON), load_json(STRIKES_JSON)
    prof = pd.read_parquet(PROFILE_PQ)
    prof["scan_date"] = pd.to_datetime(prof.scan_date).dt.date
    rng = np.random.default_rng(SEED)
    out = []
    for d in dates:
        pool = prof[prof.scan_date == d]
        uni = SP.universe_asof(d, u)
        day = g[(g.session == d) & g.ticker.isin(uni)].copy()
        day["decile"] = pd.qcut(day.volume.rank(method="first"), 10,
                                labels=False) + 1
        cand = day[~day.ticker.isin(set(pool.ticker))].copy()
        # Arm C: uniform, no bar, no matching beyond the contract bands.
        c_names = list(rng.choice(cand.ticker.to_numpy(), 2 * N_C,
                                  replace=False))
        for i, n in enumerate(c_names):
            out.append({"scan_date": d, "arm": "C", "slot": i % N_C,
                        "backup": i >= N_C, "ticker": n})
        # Arm B: research bar + decile + sector matching.
        bar = cand[cand.volume >= UND_VOL_FLOOR].copy()
        bar["strikes"] = [strikes_asof(key, t, d, strikes) for t in bar.ticker]
        bar = bar[bar.strikes >= STRIKES_FLOOR]
        bar["sector"] = [sector_of(key, t, sic) for t in bar.ticker]
        dec_share = pool.decile.value_counts(normalize=True)
        target = (dec_share * N_B).round().astype(int)
        while target.sum() != N_B:  # largest-remainder fix-up
            target[target.idxmax()] += int(np.sign(N_B - target.sum()))
        sec_ok = set(pool.sector.value_counts()[lambda s: s >= 3].index)
        pool_sec = pool[pool.sector.isin(sec_ok)]
        used, slot = set(), 0
        for dec, k in target.items():
            if k <= 0:
                continue
            # Sector slots inside this decile, proportional to the pool.
            secs = (pool_sec[pool_sec.decile == dec].sector.value_counts()
                    if len(pool_sec) else pd.Series(dtype=int))
            want = list(np.repeat(secs.index, secs.values))[:k]
            want += [None] * (k - len(want))
            for sec in want:
                for is_backup in (False, True):
                    p = bar[(bar.decile == dec) & ~bar.ticker.isin(used)]
                    if sec is not None and (p.sector == sec).any():
                        p = p[p.sector == sec]
                    if p.empty:  # fall back: neighbouring deciles
                        p = bar[~bar.ticker.isin(used)]
                        p = p.iloc[(p.decile - dec).abs().argsort()[:25]]
                    if p.empty:
                        break
                    n = str(rng.choice(p.ticker.to_numpy()))
                    used.add(n)
                    out.append({"scan_date": d, "arm": "B", "slot": slot,
                                "backup": is_backup, "ticker": n,
                                "want_decile": int(dec), "want_sector": sec})
                slot += 1
        print(f"  {d}: pool {len(pool)} | candidates {len(cand)} | pass bar"
              f" {len(bar)} | B drawn {slot} slots | C {N_C} slots")
    json.dump(sic, open(SIC_JSON, "w"))
    json.dump(strikes, open(STRIKES_JSON, "w"))
    dr = pd.DataFrame(out)
    dr.to_parquet(DRAWS_PQ)
    print(f"draws -> {DRAWS_PQ} ({len(dr)} rows)")


# ------------------------------------------------------------------ contracts
def cmd_contracts(dates):
    key = SP.polygon_key()
    prof = pd.read_parquet(PROFILE_PQ)
    dr = pd.read_parquet(DRAWS_PQ)
    names = sorted(set(prof.ticker) | set(dr.ticker))
    have = set(os.path.splitext(f)[0] for f in os.listdir(CHAIN_DIR)
               if f.endswith(".parquet"))
    todo = [n for n in names if n not in have]
    print(f"contracts: {len(names)} names needed, {len(todo)} to pull")
    man = load_json(S2_MANIFEST)
    for i, n in enumerate(todo, 1):
        r = SP.pull_name(key, n)
        man[n] = r
        json.dump(man, open(S2_MANIFEST, "w"))
        print(f"  [{i}/{len(todo)}] {n:<6} contracts {r['contracts']:>5}"
              f" failed {r['failed']:>3} bar_rows {r['bar_rows']:>6}",
              flush=True)


# ------------------------------------------------------------------ select
def reduced_rule(chain: pd.DataFrame, d: dt.date, und_close: float):
    c = chain[(chain.session == d) & (chain.type == "call")].copy()
    if c.empty or not und_close:
        return None
    c["dte"] = [(pd.Timestamp(e).date() - d).days for e in c.expiration]
    c["moneyness"] = c.strike / und_close
    c = c[(c.dte >= DTE_LO) & (c.dte <= DTE_HI)
          & (c.moneyness >= MONEY_LO) & (c.moneyness <= MONEY_HI)
          & (c.volume >= VOL_FLOOR)]
    if c.empty:
        return None
    c["otm_dist"] = (c.moneyness - OTM_TARGET).abs()
    c = c.sort_values(["volume", "otm_dist", "expiration", "strike"],
                      ascending=[False, True, True, True])
    return c.iloc[0]


def cmd_select(dates):
    g = grouped()
    prof = pd.read_parquet(PROFILE_PQ)
    prof["scan_date"] = pd.to_datetime(prof.scan_date).dt.date
    dr = pd.read_parquet(DRAWS_PQ)
    dr["scan_date"] = pd.to_datetime(dr.scan_date).dt.date
    chains = {}

    def chain(n):
        if n not in chains:
            p = os.path.join(CHAIN_DIR, f"{n}.parquet")
            chains[n] = pd.read_parquet(p) if os.path.exists(p) else pd.DataFrame()
            if not chains[n].empty:
                chains[n]["session"] = pd.to_datetime(chains[n].session).dt.date
        return chains[n]

    def leg(d, n, arm, extra):
        day = g[(g.session == d) & (g.ticker == n)]
        und_close = float(day.close.iloc[0]) if len(day) else None
        und_vol = float(day.volume.iloc[0]) if len(day) else None
        r = reduced_rule(chain(n), d, und_close)
        base = {"scan_date": d, "arm": arm, "ticker": n, "und_volume": und_vol,
                "und_close": und_close, **extra}
        if r is None:
            return {**base, "contract": None}
        return {**base, "contract": r.contract, "strike": r.strike,
                "expiration": r.expiration, "dte": int(r.dte),
                "moneyness": float(r.moneyness), "volume": float(r.volume)}

    legs, fails = [], {"A": 0, "B": 0, "C": 0}
    for d in dates:
        for _, p in prof[prof.scan_date == d].iterrows():
            L = leg(d, p.ticker, "A", {"decile": p.decile, "sector": p.sector,
                                       "delivered": p.recommended_contract})
            legs.append(L)
            fails["A"] += L["contract"] is None
        for arm in ("B", "C"):
            dd = dr[(dr.scan_date == d) & (dr.arm == arm)]
            for slot, grp in dd.groupby("slot"):
                got = None
                for _, row in grp.sort_values("backup").iterrows():
                    L = leg(d, row.ticker, arm, {"slot": slot,
                                                "backup": bool(row.backup)})
                    if L["contract"] is not None:
                        got = L
                        break
                if got is None:
                    fails[arm] += 1
                else:
                    legs.append(got)
    lg = pd.DataFrame(legs)
    lg.to_parquet(LEGS_PQ)
    print(f"select: legs A {int((lg.arm == 'A').sum())} B"
          f" {int((lg.arm == 'B').sum())} C {int((lg.arm == 'C').sum())}")
    print(f"  no qualifying contract: pool names {fails['A']} (excluded from"
          f" the primary, reported) | B slots unfilled {fails['B']} | C"
          f" slots unfilled {fails['C']}")
    if "backup" in lg:
        print(f"  backups used: B {int(lg[lg.arm == 'B'].backup.sum())}"
              f" C {int(lg[lg.arm == 'C'].backup.sum())}")


# ------------------------------------------------------------------ balance
def cmd_balance(dates):
    lg = pd.read_parquet(LEGS_PQ)
    lg = lg[lg.contract.notna()]
    g = grouped()
    u = universe()
    # Decile of every leg, over the as-of universe on its date.
    dec = {}
    for d in pd.to_datetime(lg.scan_date).dt.date.unique():
        uni = SP.universe_asof(d, u)
        day = g[(g.session == d) & g.ticker.isin(uni)].copy()
        day["decile"] = pd.qcut(day.volume.rank(method="first"), 10,
                                labels=False) + 1
        dec.update({(d, t): k for t, k in zip(day.ticker, day.decile)})
    lg["decile"] = [dec.get((pd.Timestamp(d).date(), t)) for d, t in
                    zip(lg.scan_date, lg.ticker)]
    sic = load_json(SIC_JSON)
    key = SP.polygon_key()
    lg["sector"] = [sector_of(key, t, sic) for t in lg.ticker]
    json.dump(sic, open(SIC_JSON, "w"))
    print("\nBALANCE TABLE (spec §9 step 3 gate) - dry run"
          f" {sorted(set(lg.scan_date))}")
    hdr = f"{'metric':<28}{'A pool':>14}{'B matched':>14}{'C random':>14}"
    print(hdr)
    arms = [lg[lg.arm == a] for a in "ABC"]
    def row(name, f, fmt="{:>14.2f}"):
        print(f"{name:<28}" + "".join(fmt.format(f(a)) for a in arms))
    row("legs", len, "{:>14d}")
    row("und volume median (M)", lambda a: a.und_volume.median() / 1e6)
    row("und decile median", lambda a: a.decile.median())
    row("decile >= 8 share", lambda a: (a.decile >= 8).mean())
    row("DTE median", lambda a: a.dte.median())
    row("moneyness median", lambda a: a.moneyness.median())
    row("moneyness IQR lo", lambda a: a.moneyness.quantile(.25))
    row("moneyness IQR hi", lambda a: a.moneyness.quantile(.75))
    row("contract volume median", lambda a: a.volume.median())
    row("contract volume p25", lambda a: a.volume.quantile(.25))
    print("sector shares (top 4 in pool):")
    for sec in arms[0].sector.value_counts().index[:4]:
        row(f"  {sec}", lambda a, s=sec: (a.sector == s).mean())
    print("\nRead: B must sit on A's decile and sector profile. C need not.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["profile", "draw", "contracts",
                                     "select", "balance", "all"])
    ap.add_argument("--dates", default=None)
    a = ap.parse_args()
    dates = ([dt.date.fromisoformat(x) for x in a.dates.split(",")]
             if a.dates else None)
    dates = pool_dates(dates)
    steps = (["profile", "draw", "contracts", "select", "balance"]
             if a.step == "all" else [a.step])
    for s in steps:
        print(f"== {s} ({len(dates)} dates)", flush=True)
        globals()[f"cmd_{s}"](dates)


if __name__ == "__main__":
    main()
