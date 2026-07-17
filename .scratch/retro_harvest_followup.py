"""READ-ONLY retro #3 follow-up checks. Seed=42."""
import numpy as np, pandas as pd, pyarrow.parquet as pq
from zoneinfo import ZoneInfo
np.random.seed(42)
SP="/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
ET=ZoneInfo("America/New_York"); HOL=["2026-04-03","2026-05-25","2026-06-19","2026-07-03"]
out=pq.read_table(f"{SP}/retro_harvest_outcomes.parquet").replace_schema_metadata(None).to_pandas()
out["scan_date"]=pd.to_datetime(out["scan_date"]).dt.date
out["entry_day"]=pd.to_datetime(out["entry_day"]).dt.date
u=out[(out.opp_status=="OK")&out.opp_entry_price.notna()&out.opp_peak_return.notna()].copy()
ent=pd.to_datetime(u.entry_day.astype(str)).dt.tz_localize(ET)+pd.Timedelta(hours=10)
pk=ent+pd.to_timedelta(u.opp_minutes_to_peak,unit="m")
d0=np.array(u.entry_day,dtype="datetime64[D]")
d1=np.busday_offset(d0,1,roll="forward",holidays=HOL); d2=np.busday_offset(d0,2,roll="forward",holidays=HOL)
pdt=np.array(pk.dt.date,dtype="datetime64[D]")
u["peak_day"]=np.where(pdt==d0,1,np.where(pdt==d1,2,np.where(pdt==d2,3,-1)))

# (1) cohort hold-to-end baselines (bracketed 3d label mean) + ex-STALE
def base(df,label):
    m=df.realized_return_pct_3d; ex=df[df.exit_reason_3d!="STALE_NO_TIMEOUT_PRINT"].realized_return_pct_3d
    print(f"{label:45s} N={len(df):4d}  3d-bracket mean {m.mean():+.1%}  WR {(m>0).mean():.1%}  ex-STALE mean {ex.mean():+.1%} (n={len(ex)})")
band=u[(u.recommended_delta>=0.20)&(u.recommended_delta<=0.46)]
tilt=band[band.mom_60>=0.35]
picks=u[u.was_tournament_pick==True]
print("HOLD-TO-END (V6 -60/+80 3d bracket) baselines:")
base(u,"full pool"); base(band,"delta band"); base(tilt,"tilt"); base(picks,"tournament picks (universe)")
print("STALE rows 3d label describe:", u[u.exit_reason_3d=='STALE_NO_TIMEOUT_PRINT'].realized_return_pct_3d.describe().round(3).to_dict())

# (2) tilt-vs-rest by walk-forward half
med=u.scan_date.astype(str).sort_values().iloc[len(u)//2]
rng=np.random.default_rng(42)
print(f"\nTILT vs REST by half (split at {med}):")
for name,half in [("H1",u[u.scan_date.astype(str)<=med]),("H2",u[u.scan_date.astype(str)>med])]:
    b=half[(half.recommended_delta>=0.20)&(half.recommended_delta<=0.46)]
    t=b[b.mom_60>=0.35]; r=half[~half.index.isin(t.index)]
    for x in [0.20,0.50]:
        d=(t.opp_peak_return>=x).mean()-(r.opp_peak_return>=x).mean()
        a=(t.opp_peak_return>=x).values; c=(r.opp_peak_return>=x).values
        bs=[rng.choice(a,len(a)).mean()-rng.choice(c,len(c)).mean() for _ in range(3000)]
        lo,hi=np.percentile(bs,[2.5,97.5])
        print(f"  {name} X=+{x:.0%}: tilt(n={len(t)})-rest = {d:+.1%} [{lo:+.1%},{hi:+.1%}]")

# (3) peak size by peak-day
print("\nmedian/p90 opp_peak_return by peak-day bucket:")
for d in [1,2,3]:
    s=u[u.peak_day==d].opp_peak_return
    print(f"  day {d}: n={len(s)}  median {s.median():+.1%}  p90 {s.quantile(.9):+.1%}")

# day-1 harvest specifically: P(peak>=X AND peak on day1)
for x in [0.15,0.20]:
    p=((u.opp_peak_return>=x)&(u.peak_day==1)).mean()
    print(f"P(day-1 peak >= +{x:.0%}): {p:.1%}")
# but a day-2/3 peak may still have TOUCHED +X on day 1 — peak-day understates day-1 harvest.
# proxy via same-day GIGO label: realized_return_pct target = +40 same-day
print("same-day GIGO label: P(TARGET +40 same-day) =", (u.exit_reason=="TARGET").mean().round(3),
      "| exit_reason counts:", u.exit_reason.value_counts().to_dict())

# (4) pick exclusion accounting
ap=out[out.was_tournament_pick==True]
print("\npick rows by opp_status:", ap.opp_status.value_counts(dropna=False).to_dict())
print("excluded picks:", ap[ap.opp_status!="OK"][["scan_date","ticker","opp_status"]].to_string(index=False))

# (5) tilt timing conditional on big peaks
t=tilt
for x in [0.20,0.50]:
    big=t[t.opp_peak_return>=x]; vc=big.peak_day.value_counts(normalize=True).sort_index()
    print(f"\ntilt given peak>=+{x:.0%} (n={len(big)}): d1 {vc.get(1,0):.1%} d2 {vc.get(2,0):.1%} d3 {vc.get(3,0):.1%}")

# (6) exact-region EV for cohorts at X<=80 (pure rule)
def ev(df,x,pad=0.0):
    d=df[df.realized_return_pct_3d.notna()]
    f=d.opp_peak_return>=(x+pad); p=f.mean()
    et=d.loc[~f,"realized_return_pct_3d"].mean() if (~f).any() else 0
    return x*p+(1-p)*et
print("\npure-rule EV (X<=80 exact) per cohort:")
print(f"{'X':>6} {'pool':>8} {'band':>8} {'tilt':>8} {'picks':>8}")
for x in [0.15,0.20,0.30,0.40,0.50,0.75,0.80]:
    print(f"{x:>6.0%} {ev(u,x):>+8.1%} {ev(band,x):>+8.1%} {ev(tilt,x):>+8.1%} {ev(picks,x):>+8.1%}")
