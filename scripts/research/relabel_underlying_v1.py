"""Re-label every signal in `signals_labeled_v1` under "trade the underlying" mechanics.

For each signal, compute the stock-side return from `entry_timestamp` to
`exit_timestamp` using Polygon minute bars, the SPY benchmark return over the
same window, and join VIX close on `entry_day`. Output a parquet for downstream
analysis and a markdown report at `docs/research_reports/UNDERLYING_VS_OPTIONS_V1.md`.

Same entry, same exit, same cohort. Only the instrument changes.

Usage:
    POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY \
        --project=profitscout-fida8) \
    python scripts/research/relabel_underlying_v1.py
"""

import os
import pickle
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
import yfinance as yf
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "forward-paper-trader"))
import main as trader  # noqa: E402

PROJECT_ID = "profitscout-fida8"
SOURCE_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIM_VERSION = "V3_MECHANICS_2026_04_07"

STOCK_CACHE = Path("/tmp/stock_bars_v1.pkl")
SPY_CACHE = Path("/tmp/spy_bars_v1.pkl")
OUT_PARQUET = Path("/tmp/relabel_underlying_v1.parquet")
REPORT_PATH = REPO / "docs" / "research_reports" / "UNDERLYING_VS_OPTIONS_V1.md"

LEVERAGE_LEVELS = (1, 2, 3, 5)


# ---------- data fetch ----------

def fetch_population(client: bigquery.Client) -> pd.DataFrame:
    sql = f"""
    SELECT
        ticker,
        scan_date,
        direction,
        entry_day,
        entry_timestamp,
        exit_timestamp,
        exit_reason,
        realized_return_pct,
        premium_score,
        recommended_volume,
        recommended_oi,
        recommended_iv,
        recommended_dte,
        recommended_delta
    FROM `{SOURCE_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
      AND entry_timestamp IS NOT NULL
      AND exit_timestamp IS NOT NULL
      AND realized_return_pct IS NOT NULL
    ORDER BY scan_date, ticker
    """
    return client.query(sql).to_dataframe()


def load_pickle(path: Path) -> dict:
    if path.exists():
        with path.open("rb") as f:
            return pickle.load(f)
    return {}


def save_pickle(path: Path, obj) -> None:
    with path.open("wb") as f:
        pickle.dump(obj, f)


def bars_to_df(bars: list) -> pd.DataFrame:
    """Polygon minute bars → DataFrame indexed by UTC timestamp with a 'close' col."""
    if not bars:
        return pd.DataFrame()
    df = pd.DataFrame(bars)
    df["ts"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    df = df[["ts", "c"]].rename(columns={"c": "close"})
    df = df.set_index("ts").sort_index()
    return df


def price_at_or_after(df: pd.DataFrame, ts: pd.Timestamp) -> float | None:
    if df.empty:
        return None
    idx = df.index.searchsorted(ts, side="left")
    if idx >= len(df):
        idx = len(df) - 1
    return float(df.iloc[idx]["close"])


def price_at_or_before(df: pd.DataFrame, ts: pd.Timestamp) -> float | None:
    if df.empty:
        return None
    idx = df.index.searchsorted(ts, side="right") - 1
    if idx < 0:
        idx = 0
    return float(df.iloc[idx]["close"])


def fetch_stock_bars(ticker: str, start: date, end: date) -> list:
    """Fetch minute bars for the underlying stock (not the option ticker)."""
    return trader.fetch_minute_bars(ticker, start, end)


def build_stock_cache(df: pd.DataFrame) -> dict:
    cache = load_pickle(STOCK_CACHE)
    print(f"Stock cache: {len(cache)} entries pre-existing")

    pad = timedelta(days=1)
    n_new = 0
    for i, row in df.iterrows():
        scan_d = row["scan_date"]
        if isinstance(scan_d, datetime):
            scan_d = scan_d.date()
        key = (row["ticker"], scan_d.isoformat())
        if key in cache:
            continue

        entry_day = row["entry_day"]
        if isinstance(entry_day, datetime):
            entry_day = entry_day.date()
        exit_ts = row["exit_timestamp"]
        if isinstance(exit_ts, str):
            exit_ts = pd.Timestamp(exit_ts, tz="UTC")
        exit_day = exit_ts.date()

        start = entry_day
        end = exit_day + pad  # one-day pad for safety
        bars = fetch_stock_bars(row["ticker"], start, end)
        cache[key] = bars
        n_new += 1
        time.sleep(0.13)

        if n_new % 100 == 0:
            print(f"  fetched {n_new} new stock series (cache total: {len(cache)})")
            save_pickle(STOCK_CACHE, cache)

    save_pickle(STOCK_CACHE, cache)
    print(f"Stock cache: {len(cache)} entries total ({n_new} newly fetched)")
    return cache


def build_spy_cache(min_day: date, max_day: date) -> pd.DataFrame:
    """Single contiguous SPY minute-bar fetch covering the full window."""
    if SPY_CACHE.exists():
        with SPY_CACHE.open("rb") as f:
            obj = pickle.load(f)
        if obj.get("min_day") == min_day and obj.get("max_day") == max_day:
            print(f"SPY cache hit ({len(obj['df'])} bars)")
            return obj["df"]

    print(f"Fetching SPY bars {min_day} → {max_day}")
    # Polygon caps at 50000 bars per request; chunk by 30-day windows.
    cur = min_day
    all_bars: list = []
    while cur <= max_day:
        chunk_end = min(cur + timedelta(days=30), max_day)
        bars = trader.fetch_minute_bars("SPY", cur, chunk_end)
        all_bars.extend(bars)
        cur = chunk_end + timedelta(days=1)
        time.sleep(0.15)

    df = bars_to_df(all_bars)
    df = df[~df.index.duplicated(keep="first")]
    with SPY_CACHE.open("wb") as f:
        pickle.dump({"min_day": min_day, "max_day": max_day, "df": df}, f)
    print(f"SPY cache: {len(df)} bars cached")
    return df


def fetch_vix_daily(min_day: date, max_day: date) -> pd.DataFrame:
    """Daily ^VIX close from yfinance, indexed by date."""
    print(f"Fetching ^VIX daily {min_day} → {max_day + timedelta(days=2)}")
    vix = yf.download(
        "^VIX",
        start=min_day.isoformat(),
        end=(max_day + timedelta(days=3)).isoformat(),
        progress=False,
        auto_adjust=False,
    )
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = [c[0] for c in vix.columns]
    vix = vix[["Close"]].rename(columns={"Close": "vix_close"})
    vix.index = pd.to_datetime(vix.index).date
    return vix


# ---------- per-signal computation ----------

def compute_row(
    row: pd.Series,
    stock_cache: dict,
    spy_df: pd.DataFrame,
    vix_df: pd.DataFrame,
) -> dict:
    scan_d = row["scan_date"]
    if isinstance(scan_d, datetime):
        scan_d = scan_d.date()
    key = (row["ticker"], scan_d.isoformat())
    bars = stock_cache.get(key, [])
    stock_df = bars_to_df(bars)

    entry_ts = pd.Timestamp(row["entry_timestamp"]).tz_localize("UTC") if pd.Timestamp(row["entry_timestamp"]).tzinfo is None else pd.Timestamp(row["entry_timestamp"])
    exit_ts = pd.Timestamp(row["exit_timestamp"]).tz_localize("UTC") if pd.Timestamp(row["exit_timestamp"]).tzinfo is None else pd.Timestamp(row["exit_timestamp"])

    entry_px = price_at_or_after(stock_df, entry_ts)
    exit_px = price_at_or_before(stock_df, exit_ts)

    spy_entry = price_at_or_after(spy_df, entry_ts)
    spy_exit = price_at_or_before(spy_df, exit_ts)

    direction = (row["direction"] or "").upper()
    sign = 1.0 if direction == "BULLISH" else -1.0

    if entry_px and exit_px and entry_px > 0:
        stock_ret_unsigned = (exit_px - entry_px) / entry_px
        stock_ret_signed = sign * stock_ret_unsigned
    else:
        stock_ret_unsigned = np.nan
        stock_ret_signed = np.nan

    if spy_entry and spy_exit and spy_entry > 0:
        spy_ret = (spy_exit - spy_entry) / spy_entry
    else:
        spy_ret = np.nan

    entry_day = row["entry_day"]
    if isinstance(entry_day, datetime):
        entry_day = entry_day.date()
    vix_close = np.nan
    if entry_day in vix_df.index:
        vix_close = float(vix_df.loc[entry_day, "vix_close"])
    else:
        # fall back to most recent prior trading day
        prior = [d for d in vix_df.index if d <= entry_day]
        if prior:
            vix_close = float(vix_df.loc[max(prior), "vix_close"])

    out = {
        "ticker": row["ticker"],
        "scan_date": scan_d,
        "entry_day": entry_day,
        "direction": direction,
        "exit_reason": row["exit_reason"],
        "premium_score": row["premium_score"],
        "recommended_iv": row.get("recommended_iv"),
        "recommended_dte": row.get("recommended_dte"),
        "recommended_delta": row.get("recommended_delta"),
        "option_return": float(row["realized_return_pct"]) if row["realized_return_pct"] is not None else np.nan,
        "stock_entry_px": entry_px,
        "stock_exit_px": exit_px,
        "stock_return_unsigned": stock_ret_unsigned,
        "stock_return_1x": stock_ret_signed,
        "spy_return": spy_ret,
        "alpha_vs_spy_unsigned": stock_ret_signed - spy_ret if pd.notna(stock_ret_signed) and pd.notna(spy_ret) else np.nan,
        "alpha_vs_spy_directional": stock_ret_signed - sign * spy_ret if pd.notna(stock_ret_signed) and pd.notna(spy_ret) else np.nan,
        "vix_at_entry": vix_close,
    }
    for n in LEVERAGE_LEVELS:
        out[f"stock_return_{n}x"] = stock_ret_signed * n if pd.notna(stock_ret_signed) else np.nan
    return out


# ---------- report ----------

def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x * 100:+.2f}%"


def stat_block(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) == 0:
        return {"n": 0, "mean": np.nan, "median": np.nan, "win_rate": np.nan, "sum": np.nan}
    return {
        "n": int(len(s)),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "win_rate": float((s > 0).mean()),
        "sum": float(s.sum()),
    }


def make_pnl_table(df: pd.DataFrame) -> str:
    rows = []
    cols = [
        ("Option (current)", "option_return"),
        ("Stock 1x", "stock_return_1x"),
        ("Stock 2x", "stock_return_2x"),
        ("Stock 3x", "stock_return_3x"),
        ("Stock 5x", "stock_return_5x"),
        ("SPY (unsigned)", "spy_return"),
        ("Alpha vs SPY (unsigned)", "alpha_vs_spy_unsigned"),
        ("Alpha vs SPY (directional)", "alpha_vs_spy_directional"),
    ]
    for label, col in cols:
        s = stat_block(df[col])
        rows.append(
            f"| {label} | {s['n']} | {fmt_pct(s['mean'])} | {fmt_pct(s['median'])} | {s['win_rate']*100:.1f}% | {fmt_pct(s['sum'])} |"
        )
    header = (
        "| Instrument | N | Mean return | Median return | Win rate | Cumulative |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    return header + "\n" + "\n".join(rows)


def make_vix_table(df: pd.DataFrame) -> str:
    bins = [(0, 20), (20, 25), (25, 30), (30, 100)]
    labels = ["VIX < 20", "20–25", "25–30", "30+"]
    rows = []
    for (lo, hi), label in zip(bins, labels):
        sub = df[(df["vix_at_entry"] >= lo) & (df["vix_at_entry"] < hi)]
        n = len(sub)
        if n == 0:
            rows.append(f"| {label} | 0 | – | – | – | – |")
            continue
        opt = stat_block(sub["option_return"])
        stk = stat_block(sub["stock_return_1x"])
        spy = stat_block(sub["spy_return"])
        alpha = stat_block(sub["alpha_vs_spy_directional"])
        rows.append(
            f"| {label} | {n} | {fmt_pct(opt['mean'])} | {fmt_pct(stk['mean'])} | {fmt_pct(spy['mean'])} | {fmt_pct(alpha['mean'])} |"
        )
    header = (
        "| VIX bucket | N | Option mean | Stock 1x mean | SPY mean | Directional alpha |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    return header + "\n" + "\n".join(rows)


def make_premium_score_table(df: pd.DataFrame) -> str:
    rows = []
    for ps in sorted(df["premium_score"].dropna().unique()):
        sub = df[df["premium_score"] == ps]
        opt = stat_block(sub["option_return"])
        stk = stat_block(sub["stock_return_1x"])
        rows.append(
            f"| {int(ps)} | {len(sub)} | {fmt_pct(opt['mean'])} | {fmt_pct(stk['mean'])} | {opt['win_rate']*100:.1f}% | {stk['win_rate']*100:.1f}% |"
        )
    header = (
        "| premium_score | N | Option mean | Stock 1x mean | Option win% | Stock win% |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    return header + "\n" + "\n".join(rows)


def make_direction_table(df: pd.DataFrame) -> str:
    rows = []
    for d in ["BULLISH", "BEARISH"]:
        sub = df[df["direction"] == d]
        opt = stat_block(sub["option_return"])
        stk = stat_block(sub["stock_return_1x"])
        spy = stat_block(sub["spy_return"])
        rows.append(
            f"| {d} | {len(sub)} | {fmt_pct(opt['mean'])} | {fmt_pct(stk['mean'])} | {fmt_pct(spy['mean'])} | {opt['win_rate']*100:.1f}% / {stk['win_rate']*100:.1f}% |"
        )
    header = (
        "| Direction | N | Option mean | Stock 1x mean | SPY mean | Win% (opt / stock) |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    return header + "\n" + "\n".join(rows)


def verdict(df: pd.DataFrame) -> str:
    stock_mean = df["stock_return_1x"].dropna().mean()
    alpha_mean = df["alpha_vs_spy_directional"].dropna().mean()
    opt_mean = df["option_return"].dropna().mean()
    if pd.isna(stock_mean) or pd.isna(alpha_mean):
        return "INDETERMINATE — too few rows with stock-side data."
    if stock_mean > 0 and alpha_mean > 0:
        return (
            "**OUTCOME A — Signal is real, options are the wrong instrument.** "
            f"Stock-side 1x mean is {fmt_pct(stock_mean)} (positive) and directional alpha vs SPY is "
            f"{fmt_pct(alpha_mean)} (positive). Compared to option-side mean of {fmt_pct(opt_mean)}, "
            "this is direct evidence the directional read translates to P&L on the underlying. "
            "Recommended next sprint: rebuild forward-paper-trader to trade shares-with-margin or 2x ETFs."
        )
    if stock_mean <= 0 and alpha_mean > 0:
        return (
            "**OUTCOME B — Signal has relative alpha but the regime was hostile to all short-horizon directional plays.** "
            f"Stock-side 1x is {fmt_pct(stock_mean)} (non-positive) but directional alpha vs SPY is "
            f"{fmt_pct(alpha_mean)} (positive). Recommended: build a regime gate (VX1/VX2 backwardation, "
            "ADX, IV-RV spread) before doing anything else."
        )
    return (
        "**OUTCOME C — Cannot conclude the signal generator works in this regime.** "
        f"Stock-side 1x mean is {fmt_pct(stock_mean)} and directional alpha vs SPY is {fmt_pct(alpha_mean)}. "
        "Both are non-positive. Re-label a pre-Iran-war historical window before making any architectural decision."
    )


def write_report(df: pd.DataFrame) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    n_total = len(df)
    n_with_stock = int(df["stock_return_1x"].notna().sum())
    n_with_spy = int(df["spy_return"].notna().sum())
    n_with_vix = int(df["vix_at_entry"].notna().sum())

    body = f"""# Underlying-vs-Options Relabel — V1

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
**Source:** `signals_labeled_v1` (simulator_version = `{SIM_VERSION}`)
**Cohort:** every signal with non-null `entry_timestamp`, `exit_timestamp`, and `realized_return_pct`.

## Question

For the same cohort the V3 paper trader is bleeding on, would the **underlying stock** have made money over the same entry-to-exit windows? If yes, the bleed is an instrument problem (overpriced volatility on high-IVOL names) and the fix is to pivot to leveraged equity. If the underlying also bleeds, the bleed is either a regime problem or a signal-generator problem and we need a different test to disambiguate.

## Cohort

| Metric | Count |
|---|---:|
| Total signals labeled | {n_total} |
| With stock-side data | {n_with_stock} |
| With SPY benchmark   | {n_with_spy} |
| With VIX-at-entry    | {n_with_vix} |

## Headline P&L (cohort-wide)

Same entry timestamp, same exit timestamp, same population. Only the instrument changes. Returns are signed by the signal direction (bullish: long; bearish: short).

{make_pnl_table(df)}

**Notes:**
- *Option (current)* is the realized return from the V3 simulator (already in `signals_labeled_v1.realized_return_pct`).
- *Stock Nx* is the simple leveraged stock return (`(exit_px / entry_px - 1) * sign * N`). It does **not** model funding cost, gap risk, or margin call mechanics — it's the cleanest possible apples-to-apples test of "did the directional read translate to underlying P&L?".
- *SPY (unsigned)* is the SPY return over the same window without direction-signing — what you'd get holding the index over each window.
- *Alpha vs SPY (unsigned)* = `stock_return_1x - spy_return`. Subtracts pure market beta.
- *Alpha vs SPY (directional)* = `stock_return_1x - sign * spy_return`. Subtracts the *directional* market move (so a bearish signal on a day SPY fell isn't credited for being right about the market). This is the most conservative isolation of signal-specific alpha.

## Verdict

{verdict(df)}

## By signal direction

{make_direction_table(df)}

## By premium_score (the filter the trader currently uses)

The V3 trader gates on `premium_score >= 2`. If higher premium_score = higher IVOL = more overpriced options, we should see option means decrease as premium_score rises while stock means stay flat or improve.

{make_premium_score_table(df)}

## By VIX at entry

VIX bucket on the signal's entry day, joined from yfinance `^VIX` daily close. This is the regime-stratification cut from the brief — if the high-VIX buckets dominate the losses and the low-VIX buckets are flat-or-positive, the signal is regime-conditional.

{make_vix_table(df)}

## What this report does NOT yet cover

- **VIX term structure (VX1/VX2 backwardation)** — needs futures data, deferred to a follow-up.
- **IV-RV spread per signal** — needs realized vol on each underlying, deferred.
- **Bull-call / bear-put debit-vertical relabel** — separate script (priority 4 from the brief).
- **Pre-Iran-war historical comparison** — depends on whether `overnight_signals_enriched` extends earlier than 2026-02-18.

## Reproduce

```bash
POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY --project=profitscout-fida8) \\
  python scripts/research/relabel_underlying_v1.py
```

Outputs:
- `/tmp/stock_bars_v1.pkl` — per-signal stock minute-bar cache
- `/tmp/spy_bars_v1.pkl` — single contiguous SPY minute-bar cache
- `/tmp/relabel_underlying_v1.parquet` — per-signal results table
- `docs/research_reports/UNDERLYING_VS_OPTIONS_V1.md` — this file
"""
    REPORT_PATH.write_text(body)
    print(f"Wrote report → {REPORT_PATH}")


# ---------- main ----------

def main():
    if not os.environ.get("POLYGON_API_KEY"):
        print("ERROR: POLYGON_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    trader.POLYGON_API_KEY = os.environ["POLYGON_API_KEY"].strip()

    client = bigquery.Client(project=PROJECT_ID)
    print("Loading population from BigQuery…")
    df = fetch_population(client)
    print(f"  {len(df)} signals with full timestamps + option return")

    print("\nBuilding stock-bar cache…")
    stock_cache = build_stock_cache(df)

    min_day = min(d if isinstance(d, date) and not isinstance(d, datetime) else d.date() for d in df["entry_day"])
    max_day = max(d if isinstance(d, date) and not isinstance(d, datetime) else d.date() for d in df["entry_day"])
    max_day_padded = max_day + timedelta(days=10)

    print("\nBuilding SPY cache…")
    spy_df = build_spy_cache(min_day, max_day_padded)

    print("\nFetching VIX daily…")
    vix_df = fetch_vix_daily(min_day, max_day_padded)

    print("\nComputing per-signal returns…")
    rows = []
    for i, row in df.iterrows():
        rows.append(compute_row(row, stock_cache, spy_df, vix_df))
    out = pd.DataFrame(rows)

    out.to_parquet(OUT_PARQUET)
    print(f"Wrote per-signal results → {OUT_PARQUET} ({len(out)} rows)")

    print("\nWriting markdown report…")
    write_report(out)

    # Quick console summary
    print("\n=== Summary ===")
    for col in ["option_return", "stock_return_1x", "stock_return_2x", "stock_return_3x", "spy_return", "alpha_vs_spy_directional"]:
        s = stat_block(out[col])
        print(f"  {col:30s} n={s['n']:4d}  mean={fmt_pct(s['mean'])}  win%={s['win_rate']*100:.1f}")


if __name__ == "__main__":
    main()
