"""READ-ONLY retro #3: harvest/target-exit study on the opp surface. Seed=42."""
import numpy as np, pandas as pd, pyarrow.parquet as pq
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

np.random.seed(42)
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
ET = ZoneInfo("America/New_York")
HOLIDAYS = ["2026-04-03","2026-05-25","2026-06-19","2026-07-03"]

out = pq.read_table(f"{SP}/retro_harvest_outcomes.parquet").replace_schema_metadata(None).to_pandas()
led = pq.read_table(f"{SP}/retro_harvest_ledger.parquet").replace_schema_metadata(None).to_pandas()
out["scan_date"] = pd.to_datetime(out["scan_date"]).dt.date
out["entry_day"] = pd.to_datetime(out["entry_day"]).dt.date

# ---------- universe accounting ----------
print("="*80); print("UNIVERSE ACCOUNTING")
print(f"total rows: {len(out)}  scan {out.scan_date.min()} -> {out.scan_date.max()}  (all {out.direction.unique()})")
for s, n in out.opp_status.value_counts(dropna=False).items():
    print(f"  opp_status={s}: {n}")
u = out[(out.opp_status=="OK") & out.opp_entry_price.notna() & out.opp_peak_return.notna()].copy()
print(f"UNIVERSE N={len(u)}  ({len(u)/len(out):.1%} of table; NO_BARS tail = {(out.opp_status=='NO_BARS').sum()/len(out):.1%})")
print(f"universe scan range: {u.scan_date.min()} -> {u.scan_date.max()}")
print(f"3d-label present on universe: {u.realized_return_pct_3d.notna().sum()}  STALE prints: {(u.exit_reason_3d=='STALE_NO_TIMEOUT_PRINT').sum()}")
# entry-price cross-check between opp arm and 3d arm
m = u[u.entry_price_3d.notna()]
rel = ((m.opp_entry_price - m.entry_price_3d)/m.entry_price_3d).abs()
print(f"opp vs 3d entry price: median rel diff {rel.median():.4f}, >5% diff on {(rel>0.05).mean():.1%} rows")
bad = ((u.exit_reason_3d=="TARGET") & (u.opp_peak_return < 0.75)).sum()
print(f"consistency: TARGET(3d) rows with opp_peak<0.75: {bad}")

# ---------- timing conversion ----------
def peak_bucket(df):
    ent = pd.to_datetime(df.entry_day.astype(str)).dt.tz_localize(ET) + pd.Timedelta(hours=10)
    pk = ent + pd.to_timedelta(df.opp_minutes_to_peak, unit="m")
    pk_date = pk.dt.date
    d0 = np.array(df.entry_day, dtype="datetime64[D]")
    d1 = np.busday_offset(d0, 1, roll="forward", holidays=HOLIDAYS)
    d2 = np.busday_offset(d0, 2, roll="forward", holidays=HOLIDAYS)
    pd_ = np.array(pk_date, dtype="datetime64[D]")
    b = np.where(pd_==d0, 1, np.where(pd_==d1, 2, np.where(pd_==d2, 3, -1)))
    return b, pk

u["peak_day"], u["peak_ts"] = peak_bucket(u)
u["trough_day"], _ = peak_bucket(u.rename(columns={"opp_minutes_to_peak":"_tmp","opp_minutes_to_trough":"opp_minutes_to_peak"})
                                  .rename(columns={}))[0], None
# redo trough cleanly
tb, _ = peak_bucket(u.assign(opp_minutes_to_peak=u.opp_minutes_to_trough))
u["trough_day"] = tb
print(f"\npeak-day bucket conversion failures (outside window): {(u.peak_day==-1).sum()}")
print("peak_day distribution:", u.peak_day.value_counts().sort_index().to_dict())

# ---------- helpers ----------
def wilson(k, n, z=1.96):
    if n==0: return (np.nan,np.nan,np.nan)
    p = k/n; d = 1+z*z/n
    c = (p + z*z/(2*n))/d; h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return p, c-h, c+h

XGRID = [0.05,0.10,0.15,0.20,0.30,0.40,0.50,0.75,1.00,1.50,2.00]

def harvest_curve(df, label, xs=XGRID):
    n = len(df); rows=[]
    for x in xs:
        k = (df.opp_peak_return>=x).sum(); p,lo,hi = wilson(k,n)
        rows.append((x,k,p,lo,hi))
    return rows

def ev_curve(df, xs=XGRID, pad=0.0, drop_stale=False):
    d = df[df.realized_return_pct_3d.notna()].copy()
    if drop_stale: d = d[d.exit_reason_3d!="STALE_NO_TIMEOUT_PRINT"]
    res=[]
    for x in xs:
        fill = d.opp_peak_return >= (x+pad)
        p = fill.mean()
        term = d.loc[~fill, "realized_return_pct_3d"]
        et = term.mean() if len(term) else 0.0
        ev = x*p + (1-p)*et
        wr = p + ((term>0).sum()/len(d) if len(term) else 0)
        res.append((x,p,et,ev,wr))
    return res

def timing_buckets(df):
    n=len(df); vc = df.peak_day.value_counts()
    return {d: (vc.get(d,0), vc.get(d,0)/n) for d in [1,2,3]}

def summarize(df, label):
    n=len(df)
    print(f"\n--- {label} (N={n})" + ("  ** N<30 ANECDOTAL **" if n<30 else ""))
    if n==0: return
    q = df.opp_peak_return.quantile([.5,.75,.9])
    print(f"peak: median {q[.5]:+.1%}  p75 {q[.75]:+.1%}  p90 {q[.9]:+.1%}")
    for x in [0.15,0.20,0.50,1.00]:
        k=(df.opp_peak_return>=x).sum(); p,lo,hi=wilson(k,n)
        print(f"  P(peak>=+{x:.0%}): {p:.1%} [{lo:.1%},{hi:.1%}] (k={k})")
    tb = timing_buckets(df)
    print("  peak day: " + "  ".join(f"d{d}: {v[1]:.1%}({v[0]})" for d,v in tb.items()))
    d1 = df[df.peak_day==1]
    if len(d1): print(f"  day-1 peaks: median {d1.opp_minutes_to_peak.median():.0f} min from 10:00 entry")
    ev = ev_curve(df)
    best = max(ev, key=lambda r: r[3])
    print(f"  EV argmax: X=+{best[0]:.0%} -> EV {best[3]:+.1%} (fill {best[1]:.1%}, else-terminal {best[2]:+.1%}, rule WR {best[4]:.1%})")
    print(f"  stop-risk: P(trough<=-30%) {(df.opp_trough_return<=-0.30).mean():.1%}; trough-before-peak & <=-30%: {((df.opp_trough_return<=-0.30)&(df.opp_minutes_to_trough<df.opp_minutes_to_peak)).mean():.1%}; P(trough<=-60%) {(df.opp_trough_return<=-0.60).mean():.1%}")
    return ev

# ---------- 1. full-pool harvest ----------
print("\n"+"="*80); print("1. FULL-POOL HARVEST CURVE  (touch-based CEILING, X as fraction of 10:00 fill)")
print(f"{'X':>6} {'k':>5} {'P(peak>=X)':>11} {'Wilson95':>18}")
for x,k,p,lo,hi in harvest_curve(u,"pool"):
    print(f"{x:>6.0%} {k:>5} {p:>10.1%} [{lo:>6.1%},{hi:>6.1%}]")
q = u.opp_peak_return.quantile([.25,.5,.75,.9])
print(f"peak quantiles: p25 {q[.25]:+.1%} | median {q[.5]:+.1%} | p75 {q[.75]:+.1%} | p90 {q[.9]:+.1%}")
print(f"mean peak {u.opp_peak_return.mean():+.1%}")

# ---------- 2. timing ----------
print("\n"+"="*80); print("2. TIMING OF PEAK WITHIN THE 3-DAY WINDOW")
tb = timing_buckets(u)
for d,v in tb.items(): print(f"  peak on day {d}: {v[0]} ({v[1]:.1%})")
d1 = u[u.peak_day==1]
print(f"  day-1 peaks: median {d1.opp_minutes_to_peak.median():.0f} min after 10:00 (p25 {d1.opp_minutes_to_peak.quantile(.25):.0f}, p75 {d1.opp_minutes_to_peak.quantile(.75):.0f})")
# conditional: given a big peak, when?
for x in [0.15,0.20,0.50]:
    big = u[u.opp_peak_return>=x]
    vc = big.peak_day.value_counts(normalize=True).sort_index()
    print(f"  given peak>=+{x:.0%} (n={len(big)}): d1 {vc.get(1,0):.1%} d2 {vc.get(2,0):.1%} d3 {vc.get(3,0):.1%}")
# trough timing
print(f"  trough day distribution: {u.trough_day.value_counts(normalize=True).sort_index().round(3).to_dict()}")
print(f"  trough before peak: {(u.opp_minutes_to_trough<u.opp_minutes_to_peak).mean():.1%}")

# ---------- 3. EV curves ----------
print("\n"+"="*80); print("3. TARGET-RULE EV: limit-sell +X% else 3d-window-end (w/ -60 disaster stop embedded in label)")
print(f"{'X':>6} {'P(fill)':>8} {'E[term|no]':>10} {'EV':>8} {'ruleWR':>7} | conservative pad=+10pts")
evs = ev_curve(u); evc = ev_curve(u, pad=0.10); evn = ev_curve(u, drop_stale=True)
for (x,p,et,ev,wr),(xc,pc,etc_,evc_,wrc),(xn,pn,etn,evn_,wrn) in zip(evs,evc,evn):
    print(f"{x:>6.0%} {p:>8.1%} {et:>+10.1%} {ev:>+8.1%} {wr:>7.1%} |  fill {pc:>6.1%}  EV {evc_:>+7.1%}   (ex-STALE EV {evn_:>+7.1%})")
best = max(evs, key=lambda r:r[3]); bestc = max(evc, key=lambda r:r[3])
print(f"argmax: X=+{best[0]:.0%} EV {best[3]:+.1%} | conservative argmax: X=+{bestc[0]:.0%} EV {bestc[3]:+.1%}")
print(f"baseline (no target, hold to window end w/ -60/+80 bracket): {u.realized_return_pct_3d.mean():+.1%}, WR {(u.realized_return_pct_3d>0).mean():.1%}")
print("NOTE: for X>80% the else-leg label itself sells at +80 target -> hybrid rule, not pure limit-at-X.")

# ---------- 4. cohorts ----------
print("\n"+"="*80); print("4. COHORTS")
summarize(u, "(a) full pool")
band = u[(u.recommended_delta>=0.20)&(u.recommended_delta<=0.46)]
summarize(band, "(b) delta 0.20-0.46")
tilt = band[band.mom_60>=0.35]
summarize(tilt, "(c) tilt: mom_60>=+0.35 AND delta band")
picks = u[u.was_tournament_pick==True]
summarize(picks, "(d) tournament picks (all eras, was_tournament_pick)")
p71 = picks[pd.to_datetime(picks.scan_date.astype(str))>=pd.Timestamp("2026-06-25")]
summarize(p71, "(e) tournament picks V7.1 era (scan>=06-25)")
pre = u[pd.to_datetime(u.scan_date.astype(str))<pd.Timestamp("2026-06-12")]
post = u[pd.to_datetime(u.scan_date.astype(str))>=pd.Timestamp("2026-06-12")]
summarize(pre, "(f) era pre-06-12")
summarize(post, "(f) era post-06-12")
med = u.scan_date.astype(str).sort_values().iloc[len(u)//2]
h1 = u[u.scan_date.astype(str)<=med]; h2 = u[u.scan_date.astype(str)>med]
summarize(h1, f"(g) walk-forward H1 (<= {med})")
summarize(h2, f"(g) walk-forward H2 (> {med})")

# picks-vs-pool delta with bootstrap CI on P(peak>=X)
print("\nPICKS vs POOL deltas (bootstrap 95% CI on difference, B=4000, seed=42):")
rng = np.random.default_rng(42)
pool_ex = u[u.was_tournament_pick!=True]
for x in [0.15,0.20,0.50]:
    dp = (picks.opp_peak_return>=x).mean() - (pool_ex.opp_peak_return>=x).mean()
    bs=[]
    a = (picks.opp_peak_return>=x).values; b = (pool_ex.opp_peak_return>=x).values
    for _ in range(4000):
        bs.append(rng.choice(a,len(a)).mean() - rng.choice(b,len(b)).mean())
    lo,hi = np.percentile(bs,[2.5,97.5])
    print(f"  X=+{x:.0%}: pick-pool = {dp:+.1%}  [{lo:+.1%},{hi:+.1%}]")
dp = (picks.peak_day==1).mean() - (pool_ex.peak_day==1).mean()
a=(picks.peak_day==1).values; b=(pool_ex.peak_day==1).values
bs=[rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(4000)]
lo,hi=np.percentile(bs,[2.5,97.5])
print(f"  P(day-1 peak): pick-pool = {dp:+.1%}  [{lo:+.1%},{hi:+.1%}]")

# tilt-vs-pool
tilt_ex = u[~u.index.isin(tilt.index)]
print("\nTILT vs REST-OF-POOL deltas:")
for x in [0.15,0.20,0.50]:
    dpv = (tilt.opp_peak_return>=x).mean() - (tilt_ex.opp_peak_return>=x).mean()
    a=(tilt.opp_peak_return>=x).values; b=(tilt_ex.opp_peak_return>=x).values
    bs=[rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(4000)]
    lo,hi=np.percentile(bs,[2.5,97.5])
    print(f"  X=+{x:.0%}: tilt-rest = {dpv:+.1%}  [{lo:+.1%},{hi:+.1%}]")

# ---------- ledger join hit-rate ----------
print("\n"+"="*80); print("LEDGER JOIN (live ledger, 7 rows, V7.1 only — pre-reset eras absent)")
lj = led[led.is_skipped!=True].copy()
lj["scan_date"]=pd.to_datetime(lj.scan_date).dt.date
mfull = lj.merge(out, on=["scan_date","ticker","recommended_contract"], how="left", suffixes=("","_o"))
hit_full = mfull.opp_status.notna().sum() + mfull.realized_return_pct.notna().sum()*0  # presence via any outcome col
in_tbl = lj.merge(out[["scan_date","ticker","recommended_contract"]], on=["scan_date","ticker","recommended_contract"], how="inner")
in_tk = lj.merge(out[["scan_date","ticker"]].drop_duplicates(), on=["scan_date","ticker"], how="inner")
print(f"non-skipped ledger rows: {len(lj)}; full-key join: {len(in_tbl)}/{len(lj)}; (scan,ticker) fallback: {len(in_tk)}/{len(lj)}")
print(lj[["scan_date","ticker","recommended_contract"]].to_string(index=False))
flag = out[out.was_tournament_pick==True][["scan_date","ticker"]]
print(f"was_tournament_pick flag rows: {len(flag)} spanning {flag.scan_date.min()} -> {flag.scan_date.max()} (primary pick-cohort source)")
