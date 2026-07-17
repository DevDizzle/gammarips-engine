"""Sensitivity: mu=4%/yr drift null on a 300-contract subsample; per-half tail Wilson CIs;
randomized-PIT decile shape. Seed=42."""
import numpy as np, pandas as pd, pyarrow.parquet as pq
from math import sqrt
SEED=42; B=2000
SP="/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
def load(p):
    t=pq.read_table(p); t=t.replace_schema_metadata(None); return t.to_pandas()
U=load(f"{SP}/retro_exc_universe.parquet"); bars=load(f"{SP}/retro_exc_bars.parquet")
R=load(f"{SP}/retro_exc_results.parquet")
bars["date"]=pd.to_datetime(bars["date"])
U["scan_date"]=pd.to_datetime(U["scan_date"]); U["expiration"]=pd.to_datetime(U["expiration"])
U["entry_day"]=U["opp_entry_timestamp"].dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
bar_map={t:g.set_index("date").sort_index() for t,g in bars.groupby("ticker")}

# randomized-PIT decile shape (honest under ties)
print("randomized-PIT deciles (should be ~130 each under fair pricing):")
print(pd.cut(R["p_rand"], np.linspace(0,1,11)).value_counts().sort_index().to_string())

def wilson(k,n):
    p=k/n; z=1.959964; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den; hw=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return ctr-hw,ctr+hw
Rs=R.sort_values("scan_date").reset_index(drop=True)
half=len(Rs)//2
for lab,g in [("H1-first",Rs.iloc[:half]),("H2-second",Rs.iloc[half:])]:
    k=int(g["tail_hit"].sum()); n=len(g); lo,hi=wilson(k,n)
    print(f"{lab}: tail {k}/{n}={k/n:.4f} Wilson95=[{lo:.4f},{hi:.4f}]")
for lab,g in Rs.groupby(Rs["scan_date"].dt.strftime("%Y-%m")):
    k=int(g["tail_hit"].sum()); n=len(g); lo,hi=wilson(k,n)
    print(f"{lab}: tail {k}/{n}={k/n:.4f} Wilson95=[{lo:.4f},{hi:.4f}]")

# mu=4%/yr sensitivity, 300-contract subsample
rng=np.random.default_rng(SEED)
sub=U.sample(300, random_state=SEED).reset_index(drop=True)
res={0.0:[],0.04:[]}
for _,r in sub.iterrows():
    g=bar_map[r["ticker"]]
    if r["entry_day"] not in g.index: continue
    S0=g.loc[r["entry_day"],"close"]
    path=g.loc[(g.index>r["entry_day"])&(g.index<=r["expiration"])]
    T=len(path)
    if T==0: continue
    K,entry,iv=r["strike"],r["opp_entry_price"],r["recommended_iv"]
    intr=np.maximum(path["high"].values-K,0.0); real_pb=intr.max()/entry-1.0
    sd=iv/sqrt(252.0)
    for mu_a in (0.0,0.04):
        mu=(mu_a/252.0)-0.5*sd*sd
        b=mu+sd*rng.standard_normal((B,T))
        l=np.cumsum(b,axis=1); lp=l-b
        u=rng.random((B,T))
        mrel=0.5*(b+np.sqrt(b*b-2.0*sd*sd*np.log(u)))
        spb=(np.maximum(S0*np.exp(lp+mrel)-K,0.0)).max(axis=1)/entry-1.0
        lt=int((spb<real_pb).sum()); eq=int((spb==real_pb).sum())
        res[mu_a].append(dict(p_mid=(lt+0.5*eq)/B, tail=real_pb>=np.quantile(spb,0.90)))
for mu_a,v in res.items():
    d=pd.DataFrame(v)
    print(f"mu={mu_a:.0%}/yr subsample N={len(d)}: H1 mean pct={d['p_mid'].mean():.4f}  tail={d['tail'].mean():.4f}")
