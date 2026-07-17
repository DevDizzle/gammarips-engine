import numpy as np, pandas as pd, pyarrow.parquet as pq
np.random.seed(42)
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
tbl = pq.read_table(f"{SP}/retro_itm_data.parquet"); tbl = tbl.replace_schema_metadata(None)
df = tbl.to_pandas()
for c in ["scan_date","expiration","exp_bar_date","max_bar_date"]:
    df[c] = pd.to_datetime(df[c])
MAXBAR = df["max_bar_date"].iloc[0]
exp = df[df["expiration"] <= MAXBAR].copy()
exp["gap_days"] = (exp["expiration"] - exp["exp_bar_date"]).dt.days
A = exp[exp["exp_close"].notna() & (exp["gap_days"]<=7) & exp["delta"].notna()].copy()
BC = A[(A["opp_status"]=="OK") & A["opp_entry_price"].notna()].copy()
BC["intrinsic"] = np.maximum(0.0, BC["exp_close"]-BC["strike"])
BC["floor_roi"] = (BC["intrinsic"]-BC["opp_entry_price"])/BC["opp_entry_price"]

r = BC.sort_values("floor_roi", ascending=False)
print("TOP 12 floor-ROI rows:")
print(r[["scan_date","ticker","recommended_contract","delta","opp_entry_price","exp_close","strike","floor_roi"]].head(12).to_string(index=False))
n=len(BC); tot=BC["floor_roi"].sum()
for k in [1,5,10,25]:
    print(f"mean excluding top {k}: {(tot - r['floor_roi'].head(k).sum())/(n-k):+.4f}")
print(f"full mean: {tot/n:+.4f}; share of gross positive ROI from top 10: "
      f"{r['floor_roi'].head(10).sum()/r.loc[r['floor_roi']>0,'floor_roi'].sum():.3f}")

# April vs later
for ym, sub in BC.groupby(BC["scan_date"].dt.strftime("%Y-%m")):
    rr = sub["floor_roi"]
    print(f"{ym}: N={len(rr)} mean={rr.mean():+.4f} median={rr.median():+.4f} top1={rr.max():+.2f} mean_ex_top3={(rr.sum()-rr.nlargest(3).sum())/(len(rr)-3):+.4f}")

# delta ~ 0 audit
print("\nrows with delta < 0.05 (A universe):", (A["delta"]<0.05).sum())
sub = A[A["delta"]<0.05]
print(sub[["scan_date","ticker","recommended_contract","delta","moneyness_pct","recommended_dte","underlying_price","strike"]].head(15).to_string(index=False))
print("\n0-0.2 bucket with delta>=0.05 only (A universe):")
b = A[(A["delta"]>=0.05)&(A["delta"]<0.2)]
b_itm = (b["exp_close"]>b["strike"])
print(f"N={len(b)} ITM%={b_itm.mean():.4f} mean_delta={b['delta'].mean():.4f} diff={b_itm.mean()-b['delta'].mean():+.4f}")
b0 = A[A["delta"]<0.05]; b0_itm=(b0["exp_close"]>b0["strike"])
print(f"delta<0.05: N={len(b0)} ITM%={b0_itm.mean():.4f} mean_delta={b0['delta'].mean():.4f}")

# moneyness vs delta consistency for delta<0.05
print("\ndelta<0.05 moneyness_pct describe:", b0["moneyness_pct"].describe().round(3).to_dict())

# DTE of post-06-12 expired subset vs pre
BC["era"] = np.where(BC["scan_date"]>=pd.Timestamp("2026-06-12"),"post0612","pre0612")
print("\nDTE by era (expired-only bias check):", BC.groupby("era")["recommended_dte"].describe().round(1).to_string())
# what share of post-06-12 signals are even expired yet?
post_all = df[df["scan_date"]>=pd.Timestamp("2026-06-12")]
print(f"post-06-12 rows total={len(post_all)}, expired={ (post_all['expiration']<=MAXBAR).sum() }")
