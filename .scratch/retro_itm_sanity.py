import numpy as np, pandas as pd, pyarrow.parquet as pq
from math import sqrt
from google.cloud import bigquery
np.random.seed(42)
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
tbl = pq.read_table(f"{SP}/retro_itm_data.parquet"); tbl = tbl.replace_schema_metadata(None)
df = tbl.to_pandas()
for c in ["scan_date","expiration","exp_bar_date","max_bar_date"]:
    df[c] = pd.to_datetime(df[c])

# 1) sanity: underlying move for top winners (scan price vs expiry close)
top = [("TLN","2026-06-10"),("DELL","2026-04-16"),("MU","2026-04-14"),("DOCN","2026-04-29"),("STRL","2026-04-30")]
client = bigquery.Client(project="profitscout-fida8")
q = """
SELECT ticker, date, close FROM `profitscout-fida8.profit_scout.underlying_daily_bars`
WHERE ticker IN ('TLN','DELL','MU','DOCN','STRL') AND date BETWEEN '2026-04-01' AND '2026-07-01'
ORDER BY ticker, date"""
bars = client.query(q).to_dataframe()
bars["date"]=pd.to_datetime(bars["date"])
for t,sd in top:
    row = df[(df["ticker"]==t)&(df["scan_date"]==sd)].iloc[0]
    b = bars[bars["ticker"]==t].set_index("date")["close"]
    print(f"{t} scan {sd}: underlying@scan={row['underlying_price']}, exp={row['expiration'].date()}, exp_close={row['exp_close']}")
    # detect discontinuities: max abs 1-day log return
    lr = np.log(b).diff().abs()
    big = lr[lr>0.35]
    print(f"   move={row['exp_close']/row['underlying_price']-1:+.1%}; 1-day |logret|>35% days: {dict((k.date(),round(v,2)) for k,v in big.items())}")

# 2) headline recompute excluding delta<0.05 contamination
MAXBAR = df["max_bar_date"].iloc[0]
exp = df[df["expiration"] <= MAXBAR].copy()
exp["gap_days"] = (exp["expiration"] - exp["exp_bar_date"]).dt.days
A = exp[exp["exp_close"].notna() & (exp["gap_days"]<=7) & exp["delta"].notna()].copy()
A["itm"] = A["exp_close"]>A["strike"]
def wilson(k,n):
    p=k/n; z=1.959964; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den; hw=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return ctr-hw, ctr+hw
for lab, d in [("A universe as-is", A), ("A universe, delta>=0.05 (drop 41 bad-delta rows)", A[A["delta"]>=0.05])]:
    n=len(d); k=int(d["itm"].sum()); lo,hi=wilson(k,n)
    deltas=d["delta"].clip(0,1).values
    sims=(np.random.rand(20000,n)<deltas).sum(axis=1)
    p_hi=(sims>=k).mean(); p_lo=(sims<=k).mean()
    print(f"{lab}: N={n} ITM%={k/n:.4f} [{lo:.4f},{hi:.4f}] mean_delta={deltas.mean():.4f} "
          f"diff={k/n-deltas.mean():+.4f} p(>=obs)={p_hi:.4f} p(<=obs)={p_lo:.4f}")

BC = A[(A["opp_status"]=="OK")&A["opp_entry_price"].notna()&(A["delta"]>=0.05)].copy()
BC["itm"]=BC["exp_close"]>BC["strike"]
n=len(BC);k=int(BC["itm"].sum());lo,hi=wilson(k,n)
deltas=BC["delta"].clip(0,1).values
sims=(np.random.rand(20000,n)<deltas).sum(axis=1)
print(f"B/C universe delta>=0.05: N={n} ITM%={k/n:.4f} [{lo:.4f},{hi:.4f}] mean_delta={deltas.mean():.4f} "
      f"diff={k/n-deltas.mean():+.4f} p(>=obs)={(sims>=k).mean():.4f} p(<=obs)={(sims<=k).mean():.4f}")
BC["intrinsic"]=np.maximum(0.0,BC["exp_close"]-BC["strike"])
BC["floor_roi"]=(BC["intrinsic"]-BC["opp_entry_price"])/BC["opp_entry_price"]
r=BC["floor_roi"]
idx=np.random.randint(0,len(r),(20000,len(r)))
boots=r.values[idx].mean(axis=1)
print(f"floor ROI (delta>=0.05): N={len(r)} mean={r.mean():+.4f} boot95=[{np.percentile(boots,2.5):+.4f},{np.percentile(boots,97.5):+.4f}] "
      f"median={r.median():+.4f} win%={(r>0).mean():.4f} beyondBE handled same as before")

print("\n--- clean-universe completeness ---")
BCu = BC.sort_values("scan_date").drop_duplicates("recommended_contract", keep="first")
for lab,d in [("per-signal",BC),("per-unique",BCu)]:
    n=len(d); k=int(d["itm"].sum()); lo,hi=wilson(k,n)
    kb=int((d["intrinsic"]>d["opp_entry_price"]).sum()); lob,hib=wilson(kb,n)
    print(f"{lab}: N={n} ITM%={k/n:.4f}[{lo:.4f},{hi:.4f}] mean_delta={d['delta'].mean():.4f} "
          f"beyondBE%={kb/n:.4f}[{lob:.4f},{hib:.4f}] floorROI mean={d['floor_roi'].mean():+.4f} "
          f"med={d['floor_roi'].median():+.4f} p10={d['floor_roi'].quantile(.1):+.3f} p25={d['floor_roi'].quantile(.25):+.3f} "
          f"p75={d['floor_roi'].quantile(.75):+.3f} p90={d['floor_roi'].quantile(.9):+.3f}")
Au = A[A["delta"]>=0.05].sort_values("scan_date").drop_duplicates("recommended_contract", keep="first")
n=len(Au); k=int((Au["exp_close"]>Au["strike"]).sum()); lo,hi=wilson(k,n)
deltas=Au["delta"].clip(0,1).values
sims=(np.random.rand(20000,n)<deltas).sum(axis=1)
print(f"A-univ per-unique delta>=0.05: N={n} ITM%={k/n:.4f}[{lo:.4f},{hi:.4f}] mean_delta={deltas.mean():.4f} "
      f"diff={k/n-deltas.mean():+.4f} p(>=obs)={(sims>=k).mean():.4f} p(<=obs)={(sims<=k).mean():.4f}")
