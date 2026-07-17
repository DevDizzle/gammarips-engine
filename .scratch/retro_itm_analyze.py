"""READ-ONLY analysis: ITM-at-expiry vs delta null, beyond-breakeven, floor ROI. Seed=42."""
import numpy as np, pandas as pd
from math import sqrt

np.random.seed(42)
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
import pyarrow.parquet as pq
tbl = pq.read_table(f"{SP}/retro_itm_data.parquet")
tbl = tbl.replace_schema_metadata(None)
df = tbl.to_pandas()
for c in ["scan_date","expiration","exp_bar_date","max_bar_date"]:
    df[c] = pd.to_datetime(df[c])
MAXBAR = df["max_bar_date"].iloc[0]

print("="*80)
print("UNIVERSE & EXCLUSIONS")
print("="*80)
print(f"total rows in enriched_option_outcomes: {len(df)}")
print(f"unique contracts overall: {df['recommended_contract'].nunique()}")
print(f"max bar date: {MAXBAR.date()}")

# direction / cp sanity
print("direction counts:", df["direction"].value_counts().to_dict())
print("cp_flag counts:", df["cp_flag"].value_counts(dropna=False).to_dict())
print("rows failing strict OCC regex (cp_flag null):", df["cp_flag"].isna().sum(),
      "->", df.loc[df['cp_flag'].isna(),'recommended_contract'].tolist())

# Universe: fully expired
expired = df[df["expiration"] <= MAXBAR].copy()
print(f"\nEXPIRED universe (expiration <= {MAXBAR.date()}): {len(expired)} rows, "
      f"{expired['recommended_contract'].nunique()} unique contracts")
print(f"excluded not-yet-expired: {len(df)-len(expired)}")

# exclusion buckets within expired
expired["gap_days"] = (expired["expiration"] - expired["exp_bar_date"]).dt.days
no_close = expired["exp_close"].isna()
null_delta = expired["delta"].isna()
stale = (~no_close) & (expired["gap_days"] > 7)
print(f"\nWithin expired:")
print(f"  no expiry close at all (ticker absent from bars <= expiry): {no_close.sum()}")
print(f"  stale close fallback >7 calendar days before expiry: {stale.sum()}")
if stale.any():
    print(expired.loc[stale, ["ticker","scan_date","expiration","exp_bar_date"]].to_string())
print(f"  NULL delta: {null_delta.sum()}")
print(f"  gap_days distribution (rows with close): {expired.loc[~no_close,'gap_days'].value_counts().sort_index().to_dict()}")
fallback = (~no_close) & (expired["gap_days"] > 0)
print(f"  fallback fired (last close < expiry date, i.e. no exact expiry-date bar): {fallback.sum()}")

# ITM universe (metric A): expired + close available (allow gap<=7) + delta present
A = expired[(~no_close) & (~stale) & (~null_delta)].copy()
print(f"\nMETRIC-A universe: {len(A)} rows / {A['recommended_contract'].nunique()} unique contracts")

# entry-priced subset (metrics B, C)
A["has_entry"] = (A["opp_status"] == "OK") & A["opp_entry_price"].notna()
ex_entry = A[~A["has_entry"]]
print(f"  excluded from B/C for opp_status!=OK or null entry: {len(ex_entry)}"
      f" (status breakdown: {ex_entry['opp_status'].fillna('NULL').value_counts().to_dict()})")
BC = A[A["has_entry"]].copy()
print(f"METRIC-B/C universe: {len(BC)} rows / {BC['recommended_contract'].nunique()} unique contracts")

# ---- compute outcomes (all calls) ----
for d in (A, BC):
    d["itm"] = d["exp_close"] > d["strike"]
    d["intrinsic"] = np.maximum(0.0, d["exp_close"] - d["strike"])
BC["beyond_be"] = BC["intrinsic"] > BC["opp_entry_price"]
BC["floor_roi"] = (BC["intrinsic"] - BC["opp_entry_price"]) / BC["opp_entry_price"]

def wilson(k, n):
    if n == 0: return (np.nan, np.nan)
    p = k/n; z = 1.959964
    den = 1 + z*z/n
    ctr = (p + z*z/(2*n)) / den
    hw = z*sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return ctr-hw, ctr+hw

def itm_report(d, label):
    n = len(d); k = int(d["itm"].sum())
    lo, hi = wilson(k, n)
    md = d["delta"].mean(); med = d["delta"].median()
    # exact-ish binomial test vs mean-delta null via normal approx + bootstrap of Poisson-binomial null
    # Poisson-binomial null: each contract i ITM w.p. delta_i
    B = 20000
    deltas = d["delta"].clip(0,1).values
    sims = (np.random.rand(B, n) < deltas).sum(axis=1)
    pval = (sims >= k).mean()  # one-sided: observed >= null
    print(f"{label}: N={n}  ITM={k}  ITM%={k/n:.4f}  Wilson95=[{lo:.4f},{hi:.4f}]")
    print(f"   mean|delta|={md:.4f}  median|delta|={med:.4f}  E[ITM|null]={deltas.mean():.4f}")
    print(f"   Poisson-binomial one-sided p(ITM>=obs | null=delta_i): {pval:.4f}  (B=20000, seed=42)")
    return k, n

print("\n" + "="*80)
print("METRIC A — ITM% at expiration vs delta null")
print("="*80)
itm_report(A, "Per-signal, metric-A universe")
itm_report(BC, "Per-signal, entry-priced (B/C) universe")

# per-unique-contract (first scan_date occurrence)
Au = A.sort_values("scan_date").drop_duplicates("recommended_contract", keep="first")
BCu = BC.sort_values("scan_date").drop_duplicates("recommended_contract", keep="first")
itm_report(Au, "Per-unique-contract (first occurrence), metric-A universe")
itm_report(BCu, "Per-unique-contract (first occurrence), entry-priced universe")

print("\n" + "="*80)
print("METRIC B — beyond-breakeven% (intrinsic at expiry > entry premium)")
print("="*80)
for d, lab in [(BC,"per-signal"),(BCu,"per-unique-contract")]:
    n=len(d); k=int(d["beyond_be"].sum()); lo,hi=wilson(k,n)
    print(f"{lab}: N={n}  beyond-BE={k}  {k/n:.4f}  Wilson95=[{lo:.4f},{hi:.4f}]   (ITM% same univ: {d['itm'].mean():.4f})")

print("\n" + "="*80)
print("METRIC C — floor ROI (hold-to-expiry, intrinsic only)")
print("="*80)
def roi_report(d, lab):
    r = d["floor_roi"]
    q = r.quantile([.10,.25,.50,.75,.90])
    # bootstrap CI on mean
    B=20000; idx = np.random.randint(0, len(r), (B, len(r)))
    boots = r.values[idx].mean(axis=1)
    print(f"{lab}: N={len(r)}  mean={r.mean():+.4f}  boot95(mean)=[{np.percentile(boots,2.5):+.4f},{np.percentile(boots,97.5):+.4f}]")
    print(f"   median={q[.5]:+.4f}  win%(>0)={(r>0).mean():.4f}  expire-worthless%(=-1)={(r<=-1+1e-12).mean():.4f}")
    print(f"   p10={q[.10]:+.4f} p25={q[.25]:+.4f} p75={q[.75]:+.4f} p90={q[.90]:+.4f}  max={r.max():+.4f}")
roi_report(BC, "per-signal")
roi_report(BCu, "per-unique-contract")

print("\n" + "="*80)
print("SPLITS (per-signal, entry-priced universe unless noted). N<30 => UNSTABLE")
print("="*80)
def split_table(d, key, order=None):
    rows=[]
    for g, sub in d.groupby(key, observed=True):
        n=len(sub); k=int(sub["itm"].sum()); lo,hi=wilson(k,n)
        rows.append(dict(bucket=str(g), N=n, ITM_pct=round(k/n,4), wilson_lo=round(lo,4), wilson_hi=round(hi,4),
                         mean_delta=round(sub["delta"].mean(),4),
                         itm_minus_delta=round(k/n - sub["delta"].mean(),4),
                         beyondBE_pct=round(sub["beyond_be"].mean(),4),
                         floorROI_mean=round(sub["floor_roi"].mean(),4),
                         floorROI_med=round(sub["floor_roi"].median(),4),
                         flag="UNSTABLE" if n<30 else ""))
    t = pd.DataFrame(rows)
    if order is not None: t = t.set_index("bucket").reindex(order).reset_index()
    print(t.to_string(index=False))

BC["delta_bucket"] = pd.cut(BC["delta"], [0,0.2,0.46,1.01], labels=["0-0.2","0.2-0.46","0.46+"], right=False)
# fix: standard buckets per task: 0–0.2, 0.2–0.46, 0.46+
print("\n-- by |delta| bucket --")
split_table(BC, "delta_bucket", ["0-0.2","0.2-0.46","0.46+"])

BC["scan_month"] = BC["scan_date"].dt.strftime("%Y-%m")
print("\n-- by scan month --")
split_table(BC, "scan_month")

# moneyness: signed for calls
BC["signed_mny"] = (BC["strike"] - BC["underlying_price"]) / BC["underlying_price"]
BC["mny_bucket"] = pd.cut(BC["signed_mny"], [-np.inf,0,0.05,0.10,0.15,np.inf],
                          labels=["ITM at scan","OTM 0-5%","OTM 5-10%","OTM 10-15%","OTM 15%+"])
print("\n-- by moneyness bucket (signed (strike-S)/S at scan) --")
split_table(BC, "mny_bucket")

print("\n-- direction --  (table is 100% BULLISH calls; no bearish era in this substrate)")

# era split: pre vs post 2026-06-12 bullish-top-50 gate (all bullish anyway, but pool construction changed)
BC["era"] = np.where(BC["scan_date"] >= pd.Timestamp("2026-06-12"), "post-06-12 top50",
             np.where(BC["scan_date"] >= pd.Timestamp("2026-06-26"), "V7.1", "pre-06-12 wide"))
BC.loc[BC["scan_date"] >= pd.Timestamp("2026-06-26"), "era"] = "V7.1 (06-26+)"
print("\n-- by pool era --")
split_table(BC, "era")

# recompute A-universe headline restricted to A (not BC) per delta bucket for reference
print("\n-- metric-A universe by delta bucket (ITM only; includes rows without entry price) --")
A2 = A.copy()
A2["delta_bucket"] = pd.cut(A2["delta"], [0,0.2,0.46,1.01], labels=["0-0.2","0.2-0.46","0.46+"], right=False)
for g, sub in A2.groupby("delta_bucket", observed=True):
    n=len(sub); k=int(sub["itm"].sum()); lo,hi=wilson(k,n)
    print(f"  {g}: N={n} ITM%={k/n:.4f} [{lo:.4f},{hi:.4f}] mean_delta={sub['delta'].mean():.4f} diff={k/n-sub['delta'].mean():+.4f}")

print("\n" + "="*80)
print("WALK-FORWARD STABILITY: ITM-minus-delta by half (entry-priced universe)")
print("="*80)
BC_sorted = BC.sort_values("scan_date")
half = len(BC_sorted)//2
for lab, sub in [("first half", BC_sorted.iloc[:half]), ("second half", BC_sorted.iloc[half:])]:
    n=len(sub); k=int(sub["itm"].sum()); lo,hi=wilson(k,n)
    print(f"{lab}: dates {sub['scan_date'].min().date()}..{sub['scan_date'].max().date()}  N={n}  "
          f"ITM%={k/n:.4f} [{lo:.4f},{hi:.4f}]  mean_delta={sub['delta'].mean():.4f}  diff={k/n-sub['delta'].mean():+.4f}"
          f"  floorROI mean={sub['floor_roi'].mean():+.4f}")

# entry premium sanity
print("\nentry premium sanity: opp_entry_price percentiles:",
      BC["opp_entry_price"].quantile([0,.01,.5,.99,1]).round(3).to_dict())
print("rows with opp_entry_price <= 0.02 (penny-premium ratio distortion risk):", (BC["opp_entry_price"]<=0.02).sum())
