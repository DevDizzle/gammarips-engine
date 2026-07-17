"""Sanity: IV units check (BS price vs entry premium) + exclusion accounting. Seed=42."""
import numpy as np, pandas as pd, pyarrow.parquet as pq
from math import erf, sqrt as _sqrt
class norm:
    @staticmethod
    def cdf(x): return 0.5*(1.0+erf(x/_sqrt(2.0)))
np.random.seed(42)
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"

def load(p):
    t = pq.read_table(p); t = t.replace_schema_metadata(None); return t.to_pandas()

df = load(f"{SP}/retro_itm_data.parquet")
iv = load(f"{SP}/retro_exc_iv.parquet")
for c in ["scan_date","expiration","exp_bar_date","max_bar_date"]:
    df[c] = pd.to_datetime(df[c])
iv["scan_date"] = pd.to_datetime(iv["scan_date"])
df = df.merge(iv, on=["scan_date","ticker","recommended_contract"], how="left", validate="1:1")
MAXBAR = df["max_bar_date"].iloc[0]

# Prior-study clean universe
exp = df[df["expiration"]<=MAXBAR].copy()
exp["gap_days"]=(exp["expiration"]-exp["exp_bar_date"]).dt.days
A = exp[exp["exp_close"].notna() & (exp["gap_days"]<=7) & exp["delta"].notna()]
BC = A[(A["opp_status"]=="OK") & A["opp_entry_price"].notna() & (A["delta"]>=0.05)].copy()
print(f"prior clean universe (expired, entry-priced, delta>=0.05): N={len(BC)}")
print(f"  NULL recommended_iv: {BC['recommended_iv'].isna().sum()}")
absurd = BC["recommended_iv"].notna() & ((BC["recommended_iv"]<0.01)|(BC["recommended_iv"]>5.0))
print(f"  absurd IV (<1% or >500%): {absurd.sum()}")
if absurd.any():
    print(BC.loc[absurd,["scan_date","ticker","recommended_contract","recommended_iv","opp_entry_price"]].to_string(index=False))
U = BC[BC["recommended_iv"].notna() & ~absurd].copy()
print(f"  STUDY universe: N={len(U)}, unique contracts={U['recommended_contract'].nunique()}, "
      f"dates {U['scan_date'].min().date()}..{U['scan_date'].max().date()}")
print("  IV percentiles:", U["recommended_iv"].quantile([0,.05,.25,.5,.75,.95,1]).round(3).to_dict())

# BS sanity: price call at scan w/ recommended_iv vs opp_entry_price (10:00 next day; rough check)
def bs_call(S,K,T,sig,r=0.04):
    if T<=0 or sig<=0: return max(0.0,S-K)
    d1=(np.log(S/K)+(r+sig*sig/2)*T)/(sig*np.sqrt(T)); d2=d1-sig*np.sqrt(T)
    return S*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
samp = U.sample(12, random_state=42)
print("\nBS(scan, recommended_iv) vs entry premium (entered next 10:00; loose agreement expected):")
for _,r_ in samp.iterrows():
    T=r_["recommended_dte"]/365.0
    bs=bs_call(r_["underlying_price"], r_["strike"], T, r_["recommended_iv"])
    print(f"  {r_['ticker']:6s} {str(r_['scan_date'].date())} K={r_['strike']:8.2f} S={r_['underlying_price']:8.2f} "
        f"dte={r_['recommended_dte']:3.0f} iv={r_['recommended_iv']:.3f} BS={bs:7.3f} entry={r_['opp_entry_price']:7.3f} "
        f"ratio={r_['opp_entry_price']/bs if bs>0 else np.nan:5.2f}")
ratios=[]
for _,r_ in U.iterrows():
    bs=bs_call(r_["underlying_price"], r_["strike"], r_["recommended_dte"]/365.0, r_["recommended_iv"])
    ratios.append(r_["opp_entry_price"]/bs if bs>0.01 else np.nan)
ratios=pd.Series(ratios)
print("\nentry/BS ratio percentiles (all study rows):", ratios.quantile([.05,.25,.5,.75,.95]).round(2).to_dict())
U.to_parquet(f"{SP}/retro_exc_universe.parquet")
print("saved study universe.")
