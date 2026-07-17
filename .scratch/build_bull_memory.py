"""Bull-only, feature-aligned case memory: each exemplar is the SAME live-JSON
schema the judge sees + a WON/LOST option-PnL label. Built from
realized_label.pkl (outcome) joined to overnight_signals_enriched (features).

Writes .scratch/bull_memory.json = {"profile": {...}, "exemplars": [ {...features, outcome} ]}.
Leakage-safe: closed past trades only; outcome cols (next_day*, peak_return, is_win)
are NOT emitted as features — only the realized option-PnL label is.
"""
from __future__ import annotations
import json
import pandas as pd
from google.cloud import bigquery

# live-aligned, as-of-scan features (bull-focused; same keys the judge sees live)
FEAT = ["overnight_score", "call_dollar_volume", "call_vol_oi_ratio", "call_uoa_depth",
        "call_active_strikes", "flow_intent", "moneyness_pct", "recommended_dte",
        "recommended_delta", "recommended_gamma", "recommended_theta", "recommended_iv",
        "recommended_mid_price", "recommended_spread_pct", "recommended_oi", "recommended_volume",
        "price_change_pct", "rsi_14", "golden_cross", "above_sma_50", "above_sma_200",
        "atr_normalized_move", "catalyst_type", "catalyst_score", "mean_reversion_risk",
        "move_overdone", "risk_reward_ratio"]

def _r(v, n=4):
    try: return round(float(v), n)
    except (TypeError, ValueError): return v

def main():
    df = pd.read_pickle("backtesting_and_research/realized_label.pkl")
    df = df[(df["realized_ret"].notna()) & (df["direction"] == "BULLISH")].copy()
    df["scan_date"] = df["scan_date"].astype(str).str[:10]
    df["won"] = df["realized_ret"] > 0
    print(f"bull labeled: {len(df)}  won={int(df['won'].sum())} lost={int((~df['won']).sum())}")

    # pull live features from enriched for the scan_dates in scope, join on (contract, scan_date)
    bq = bigquery.Client(project="profitscout-fida8")
    dates = sorted(df["scan_date"].unique())
    cols = ", ".join(["ticker", "scan_date", "recommended_contract"] + FEAT)
    e = bq.query(
        f"SELECT {cols} FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` "
        f"WHERE scan_date BETWEEN '{dates[0]}' AND '{dates[-1]}'").to_dataframe()
    e["scan_date"] = e["scan_date"].astype(str).str[:10]
    m = df.merge(e, on=["recommended_contract", "scan_date"], how="inner", suffixes=("", "_e"))
    print(f"joined to enriched features: {len(m)}")

    # winner/loser PROFILE (median of key features) over the FULL bull set — the distilled contrast
    keyf = ["call_dollar_volume", "call_vol_oi_ratio", "overnight_score", "moneyness_pct",
            "recommended_dte", "recommended_delta", "price_change_pct", "rsi_14", "catalyst_score"]
    prof = {}
    for f in keyf:
        if f in m:
            prof[f] = {"won_median": _r(m[m["won"]][f].median(), 3),
                       "lost_median": _r(m[~m["won"]][f].median(), 3)}

    # balanced curated exemplars: span the flow spectrum on BOTH sides (incl. high-flow LOSERS = traps)
    def span(sub, n=30):
        sub = sub.sort_values("call_dollar_volume", ascending=False)
        if len(sub) <= n: return sub
        step = len(sub) / n
        return sub.iloc[[int(i * step) for i in range(n)]]
    sample = pd.concat([span(m[m["won"]]), span(m[~m["won"]])])

    exemplars = []
    for _, row in sample.iterrows():
        ex = {"ticker": row["ticker"], "scan_date": row["scan_date"]}
        for f in FEAT:
            v = row.get(f)
            if pd.notna(v): ex[f] = _r(v) if isinstance(v, (int, float)) else v
        ex["outcome"] = "WON" if row["won"] else "LOST"
        ex["realized_ret_pct"] = _r(row["realized_ret"] * 100, 1)
        ex["exit_reason"] = row.get("exit_reason")
        exemplars.append(ex)

    out = {"profile": prof, "exemplars": exemplars}
    with open(".scratch/bull_memory.json", "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"wrote {len(exemplars)} exemplars ({sum(e['outcome']=='WON' for e in exemplars)} won / "
          f"{sum(e['outcome']=='LOST' for e in exemplars)} lost)")
    print("\nWINNER vs LOSER profile (medians):")
    for f, d in prof.items():
        print(f"  {f:24} won={d['won_median']:>14}  lost={d['lost_median']:>14}")

if __name__ == "__main__":
    main()
