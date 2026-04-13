"""
Does liquidity correlate with bracket outcome?

Slices the v4_bracket_sim parquet (6,799 bullish+liquid signals, +40/-25/2d real
bracket, entry at D+1 open) by volume and OI buckets, reports mean return,
win rate, and exit distribution per bucket.
"""
import pandas as pd

df = pd.read_parquet("/tmp/v4_bracket_sim.parquet")

# Re-apply the bracket exactly as in v4_bracket_sim.py
TP_PCT, SL_PCT = 0.40, 0.25


def sim_row(row):
    s = max(0.0, min(0.8, float(row.get("spread_pct") or 0)))
    entry_eff = row["d1_o"] * (1 + s / 2)
    tp = entry_eff * (1 + TP_PCT)
    sl = entry_eff * (1 - SL_PCT)
    last_close = None
    for h, l, c in [
        (row.get("d1_h"), row.get("d1_l"), row.get("d1_c")),
        (row.get("d2_h"), row.get("d2_l"), row.get("d2_c")),
        (row.get("d3_h"), row.get("d3_l"), row.get("d3_c")),
    ]:
        if h is None or l is None:
            continue
        last_close = c
        tp_hit = h >= tp
        sl_hit = l <= sl
        if tp_hit and sl_hit:
            return ("STOP", -SL_PCT)  # pessimistic default
        if tp_hit:
            return ("TARGET", TP_PCT)
        if sl_hit:
            return ("STOP", -SL_PCT)
    if last_close is None:
        return ("NO_DATA", float("nan"))
    exit_eff = last_close * (1 - s / 2)
    return ("TIMEOUT", (exit_eff - entry_eff) / entry_eff)


rows = []
for _, r in df.iterrows():
    reason, ret = sim_row(r)
    if reason == "NO_DATA":
        continue
    rows.append({
        "vol": int(r["vol"]) if pd.notna(r["vol"]) else 0,
        "oi":  int(r["oi"])  if pd.notna(r["oi"])  else 0,
        "spread_pct": float(r["spread_pct"] or 0),
        "reason": reason,
        "ret": ret,
    })
res = pd.DataFrame(rows)
print(f"=== Liquidity correlation: {len(res)} bracketed trades ===\n")
print(f"Overall: mean={res['ret'].mean():+.4f}  win%={100*(res['ret']>0).mean():.1f}")
print(f"Exit dist: {res['reason'].value_counts().to_dict()}\n")


def bucket(df, col, edges, labels):
    cuts = pd.cut(df[col], bins=edges, labels=labels, include_lowest=True)
    g = df.groupby(cuts, observed=True)["ret"].agg(["count", "mean", "median"])
    g["win%"] = df.groupby(cuts, observed=True)["ret"].apply(lambda s: 100 * (s > 0).mean())
    g["stop%"] = df.groupby(cuts, observed=True)["reason"].apply(
        lambda s: 100 * (s == "STOP").mean()
    )
    g["target%"] = df.groupby(cuts, observed=True)["reason"].apply(
        lambda s: 100 * (s == "TARGET").mean()
    )
    return g


# --- Volume buckets ---
vol_edges = [0, 100, 250, 500, 1000, 2500, 10000, 1_000_000_000]
vol_labels = ["<100", "100-249", "250-499", "500-999", "1k-2.4k", "2.5k-9.9k", "10k+"]
print("VOLUME buckets:")
print(bucket(res, "vol", vol_edges, vol_labels))
print()

# --- OI buckets ---
oi_edges = [0, 50, 250, 500, 1000, 2500, 10000, 1_000_000_000]
oi_labels = ["<50", "50-249", "250-499", "500-999", "1k-2.4k", "2.5k-9.9k", "10k+"]
print("OPEN INTEREST buckets:")
print(bucket(res, "oi", oi_edges, oi_labels))
print()

# --- Spread buckets ---
spr_edges = [0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
spr_labels = ["0-5%", "5-10%", "10-15%", "15-20%", "20-30%", "30-40%"]
print("SPREAD buckets:")
print(bucket(res, "spread_pct", spr_edges, spr_labels))
print()

# --- Joint high-liquidity slice ---
print("=== Joint gates (hypothetical tighter floors) ===")
for v_min, o_min in [(100, 50), (250, 250), (500, 500), (1000, 1000), (2500, 2500)]:
    sub = res[(res["vol"] >= v_min) & (res["oi"] >= o_min)]
    if len(sub) < 10:
        continue
    print(f"vol>={v_min:>5d} AND oi>={o_min:>5d}: "
          f"n={len(sub):>5d}  mean={sub['ret'].mean():+.4f}  "
          f"win%={100*(sub['ret']>0).mean():5.1f}  "
          f"stop%={100*(sub['reason']=='STOP').mean():5.1f}  "
          f"target%={100*(sub['reason']=='TARGET').mean():5.1f}")

# Pearson correlations
print(f"\nPearson corr(log vol, ret)    = {res[['ret']].assign(lv=res['vol'].apply(lambda v: 0 if v<=0 else __import__('math').log(v))).corr().iloc[0,1]:+.4f}")
print(f"Pearson corr(log oi, ret)     = {res[['ret']].assign(lo=res['oi'].apply(lambda v: 0 if v<=0 else __import__('math').log(v))).corr().iloc[0,1]:+.4f}")
print(f"Pearson corr(spread_pct, ret) = {res[['spread_pct','ret']].corr().iloc[0,1]:+.4f}")
