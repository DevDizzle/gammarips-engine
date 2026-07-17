"""READ-ONLY analysis: excursion path study (H1 fatness, H2 sharpness, G giveback). Seed=42.
Realized: intrinsic-bound peak from daily HIGHs, entry-day-close anchor, days 1..expiration.
Null: per-contract GBM (sigma=recommended_iv, mu=0 arithmetic => log drift -s^2/2),
      B=2000 paths, exact Brownian-bridge intraday-max per day (so sim also has 'highs')."""
import numpy as np, pandas as pd, pyarrow.parquet as pq
from math import sqrt

SEED = 42
B = 2000
SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"

def load(p):
    t = pq.read_table(p); t = t.replace_schema_metadata(None); return t.to_pandas()

U = load(f"{SP}/retro_exc_universe.parquet")
bars = load(f"{SP}/retro_exc_bars.parquet")
bars["date"] = pd.to_datetime(bars["date"])
U["scan_date"] = pd.to_datetime(U["scan_date"])
U["expiration"] = pd.to_datetime(U["expiration"])
U["entry_day"] = U["opp_entry_timestamp"].dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)

# per-ticker bar frames
bar_map = {t: g.set_index("date").sort_index() for t, g in bars.groupby("ticker")}

rng = np.random.default_rng(SEED)

rows, excl_no_entry_bar, excl_no_path = [], 0, 0
for i, r in U.iterrows():
    g = bar_map.get(r["ticker"])
    if g is None: excl_no_entry_bar += 1; continue
    if r["entry_day"] not in g.index: excl_no_entry_bar += 1; continue
    S0 = g.loc[r["entry_day"], "close"]
    path = g.loc[(g.index > r["entry_day"]) & (g.index <= r["expiration"])]
    T = len(path)
    if T == 0: excl_no_path += 1; continue
    K, entry, iv = r["strike"], r["opp_entry_price"], r["recommended_iv"]

    # ---- realized ----
    intr = np.maximum(path["high"].values - K, 0.0)
    peak_intr = intr.max(); d2p = int(np.argmax(intr)) + 1          # 1-based, first argmax
    real_pb = peak_intr / entry - 1.0                                # = -1 if never ITM
    term = (max(0.0, r["exp_close"] - K) - entry) / entry
    intr0 = max(0.0, g.loc[r["entry_day"], "high"] - K)              # sensitivity: include day-0 high
    real_pb_d0 = max(peak_intr, intr0) / entry - 1.0

    # ---- simulated null ----
    sd = iv / sqrt(252.0)
    mu = -0.5 * sd * sd                                              # arithmetic mu=0
    b = mu + sd * rng.standard_normal((B, T))
    l = np.cumsum(b, axis=1); lp = l - b
    u = rng.random((B, T))
    mrel = 0.5 * (b + np.sqrt(b * b - 2.0 * sd * sd * np.log(u)))
    shigh = S0 * np.exp(lp + mrel)
    sintr = np.maximum(shigh - K, 0.0)
    speak = sintr.max(axis=1)
    sd2p = np.argmax(sintr, axis=1) + 1
    spb = speak / entry - 1.0

    # H1 percentile (mid-P) + randomized PIT
    lt = int((spb < real_pb).sum()); eq = int((spb == real_pb).sum())
    p_mid = (lt + 0.5 * eq) / B
    p_rand = (lt + rng.random() * (1 + eq)) / (B + 1)
    q90 = np.quantile(spb, 0.90)
    tail_hit = real_pb >= q90
    p_pos_sim = float((spb > 0).mean())                              # implied P(ever beyond breakeven)
    p_ge100_sim = float((spb >= 1.0).mean())

    # H2 timing percentile: condition BOTH legs on peak_bound > 0
    tp_mid = np.nan; n_qual = int((spb > 0).sum())
    sim_med_d2p = np.nan; sim_p3 = np.nan
    if real_pb > 0 and n_qual >= 50:
        qd = sd2p[spb > 0]
        tp_mid = ((qd < d2p).sum() + 0.5 * (qd == d2p).sum()) / n_qual
        sim_med_d2p = float(np.median(qd)); sim_p3 = float((qd <= 3).mean())

    rows.append(dict(scan_date=r["scan_date"], ticker=r["ticker"], contract=r["recommended_contract"],
        delta=r["delta"], dte=r["recommended_dte"], iv=iv, entry=entry, T=T,
        real_pb=real_pb, real_pb_d0=real_pb_d0, d2p=d2p, term=term,
        p_mid=p_mid, p_rand=p_rand, tail_hit=bool(tail_hit), p_pos_sim=p_pos_sim, p_ge100_sim=p_ge100_sim,
        tp_mid=tp_mid, n_qual=n_qual, sim_med_d2p=sim_med_d2p, sim_p3=sim_p3))

R = pd.DataFrame(rows)
R.to_parquet(f"{SP}/retro_exc_results.parquet")
print(f"universe in: {len(U)}  excluded no-entry-bar: {excl_no_entry_bar}  no-path: {excl_no_path}  analyzed: {len(R)}")
print(f"life length T: median={R['T'].median():.0f} p25={R['T'].quantile(.25):.0f} p75={R['T'].quantile(.75):.0f} max={R['T'].max()}")

def boot_ci(x, w_dates=None, nb=10000, seed=SEED):
    """plain + scan_date-clustered bootstrap CI of the mean"""
    rg = np.random.default_rng(seed)
    x = np.asarray(x, float)
    idx = rg.integers(0, len(x), (nb, len(x)))
    plain = np.sort(x[idx].mean(axis=1))[[int(nb*0.025), int(nb*0.975)]]
    clus = None
    if w_dates is not None:
        d = pd.Series(x).groupby(w_dates.values)
        groups = [g.values for _, g in d]
        ng = len(groups)
        means = []
        for _ in range(nb):
            pick = rg.integers(0, ng, ng)
            means.append(np.concatenate([groups[j] for j in pick]).mean())
        means = np.sort(means); clus = means[[int(nb*0.025), int(nb*0.975)]]
    return plain, clus

def ks_uniform(p):
    p = np.sort(np.asarray(p, float)); n = len(p)
    cdf = np.arange(1, n+1)/n
    D = max(np.max(cdf - p), np.max(p - (np.arange(n)/n)))
    lam = (sqrt(n) + 0.12 + 0.11/sqrt(n)) * D
    pv = 2*sum((-1)**(k-1)*np.exp(-2*(lam*k)**2) for k in range(1, 101))
    return D, max(min(pv,1.0),0.0)

print("\n" + "="*88)
print("H1 FATNESS — realized peak percentile within own IV-implied peak distribution")
print("="*88)
mp = R["p_mid"].mean()
plain, clus = boot_ci(R["p_mid"], R["scan_date"])
D, pv = ks_uniform(R["p_rand"])
print(f"mean percentile (mid-P): {mp:.4f}   boot95 plain=[{plain[0]:.4f},{plain[1]:.4f}]  "
      f"scan_date-clustered=[{clus[0]:.4f},{clus[1]:.4f}]   (null=0.500)")
print(f"median percentile: {R['p_mid'].median():.4f}")
print(f"KS vs Uniform(0,1) on randomized PIT: D={D:.4f}  p={pv:.2e}")
k = int(R["tail_hit"].sum()); n = len(R)
def wilson(k,n):
    p=k/n; z=1.959964; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den; hw=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return ctr-hw, ctr+hw
lo,hi = wilson(k,n)
tp, tc = boot_ci(R["tail_hit"].astype(float), R["scan_date"])
print(f"tail: share realized peak >= implied p90: {k}/{n} = {k/n:.4f}  Wilson95=[{lo:.4f},{hi:.4f}]  "
      f"clustered boot95=[{tc[0]:.4f},{tc[1]:.4f}]   (null=0.10)")
print(f"deciles of mid-P percentile:\n{pd.cut(R['p_mid'], np.linspace(0,1,11)).value_counts().sort_index().to_string()}")
print(f"\nsensitivity — include entry-day high in realized peak: mean pct shifts from computed-on-days-1..T only")
d0_gain = (R["real_pb_d0"] > R["real_pb"]).mean()
print(f"  share of contracts where day-0 high exceeds later peak: {d0_gain:.4f} (realized-only descriptive; percentiles not recomputed)")

print("\nraw magnitude vs implied:")
print(f"  realized: P(ever beyond breakeven, peak_bound>0) = {(R['real_pb']>0).mean():.4f}   "
      f"implied mean P = {R['p_pos_sim'].mean():.4f}")
print(f"  realized: P(peak_bound >= +100%) = {(R['real_pb']>=1).mean():.4f}   implied mean P = {R['p_ge100_sim'].mean():.4f}")
print(f"  realized: never-ITM share (peak_bound = -100%) = {(R['real_pb']<=-1+1e-12).mean():.4f}")
print(f"  realized peak_bound: median={R['real_pb'].median():+.3f} p75={R['real_pb'].quantile(.75):+.3f} "
      f"p90={R['real_pb'].quantile(.9):+.3f} p99={R['real_pb'].quantile(.99):+.3f} max={R['real_pb'].max():+.2f}")

print("\n" + "="*88)
print("H2 SHARPNESS — realized days-to-peak percentile vs implied timing (both legs | peak_bound>0)")
print("="*88)
H = R[R["real_pb"] > 0].copy()
print(f"conditioning: realized peak_bound>0 -> N={len(H)} of {len(R)} ({len(H)/len(R):.1%}); "
      f"excluded for <50 qualifying sim paths: {H['tp_mid'].isna().sum()}")
H2 = H[H["tp_mid"].notna()]
mtp = H2["tp_mid"].mean()
plain, clus = boot_ci(H2["tp_mid"], H2["scan_date"])
print(f"mean timing percentile (mid-P): {mtp:.4f}  boot95 plain=[{plain[0]:.4f},{plain[1]:.4f}]  "
      f"clustered=[{clus[0]:.4f},{clus[1]:.4f}]   (<0.5 = earlier than implied)")
print(f"median timing percentile: {H2['tp_mid'].median():.4f}")
print(f"raw realized timing: median d2p={H2['d2p'].median():.0f} trading days; "
      f"P(d2p<=3)={ (H2['d2p']<=3).mean():.4f}  P(<=5)={(H2['d2p']<=5).mean():.4f}  median life T={H2['T'].median():.0f}")
print(f"implied (per-contract means): median sim d2p={H2['sim_med_d2p'].mean():.2f}; mean P_sim(d2p<=3)={H2['sim_p3'].mean():.4f}")

print("\n" + "="*88)
print("G GIVEBACK — peak_bound minus terminal intrinsic return")
print("="*88)
R["giveback"] = R["real_pb"] - R["term"]
print("all contracts: giveback percentiles:",
      R["giveback"].quantile([.1,.25,.5,.75,.9]).round(3).to_dict())
G = R[R["real_pb"] >= 0.5].copy()
G["retained"] = G["term"] / G["real_pb"]
print(f"\nconditional on peak_bound >= +50%: N={len(G)}")
print(f"  giveback (peak - terminal): median={G['giveback'].median():+.3f} mean={G['giveback'].mean():+.3f}")
print(f"  share of peak GAIN retained at expiry (term/peak): median={G['retained'].median():.3f} mean={G['retained'].mean():.3f}")
print(f"  round-tripped to a LOSS at expiry (term<0): {(G['term']<0).mean():.4f}")
print(f"  retained >= 50% of peak: {(G['retained']>=0.5).mean():.4f}   retained <=0: {(G['retained']<=0).mean():.4f}")
Gpos = R[R["real_pb"] > 0]
print(f"reference, all peak_bound>0 (N={len(Gpos)}): round-trip-to-loss share={(Gpos['term']<0).mean():.4f}")

print("\n" + "="*88)
print("SPLITS — H1 mean pct / tail share / H2 mean timing pct  (N<30 => UNSTABLE)")
print("="*88)
def split(dfr, key):
    out=[]
    for gname, g in dfr.groupby(key, observed=True):
        h = g[(g["real_pb"]>0) & g["tp_mid"].notna()]
        out.append(dict(bucket=str(gname), N=len(g),
            H1_meanpct=round(g["p_mid"].mean(),4), tail=round(g["tail_hit"].mean(),4),
            N_H2=len(h), H2_meanpct=round(h["tp_mid"].mean(),4) if len(h) else np.nan,
            real_pb_med=round(g["real_pb"].median(),3),
            flag="UNSTABLE" if len(g)<30 else ""))
    print(pd.DataFrame(out).to_string(index=False))

R["month"] = R["scan_date"].dt.strftime("%Y-%m")
print("\n-- scan month --"); split(R, "month")
Rs = R.sort_values("scan_date").reset_index(drop=True)
Rs["half"] = np.where(Rs.index < len(Rs)//2, "H1-first", "H2-second")
hb = Rs.groupby("half")["scan_date"].agg(["min","max"])
print(f"\n-- walk-forward halves ({hb.loc['H1-first','min'].date()}..{hb.loc['H1-first','max'].date()} | "
      f"{hb.loc['H2-second','min'].date()}..{hb.loc['H2-second','max'].date()}) --")
split(Rs, "half")
for lab, g in Rs.groupby("half"):
    pl, cl = boot_ci(g["p_mid"], g["scan_date"])
    h = g[(g["real_pb"]>0) & g["tp_mid"].notna()]
    pl2, cl2 = boot_ci(h["tp_mid"], h["scan_date"]) if len(h)>10 else ((np.nan,np.nan),(np.nan,np.nan))
    print(f"   {lab}: H1 clustered CI=[{cl[0]:.4f},{cl[1]:.4f}]  H2 clustered CI=[{cl2[0]:.4f},{cl2[1]:.4f}] (N_H2={len(h)})")
R["delta_bucket"] = pd.cut(R["delta"], [0.05,0.2,0.46,1.01], labels=["0.05-0.2","0.2-0.46","0.46+"], right=False)
print("\n-- delta bucket --"); split(R, "delta_bucket")
R["dte_bucket"] = pd.cut(R["dte"], [6,10,21,46], labels=["7-10","11-21","22-45"])
print("\n-- DTE bucket --"); split(R, "dte_bucket")

print("\n-- per-unique-contract robustness (first occurrence) --")
Ru = R.sort_values("scan_date").drop_duplicates("contract", keep="first")
pl, cl = boot_ci(Ru["p_mid"], Ru["scan_date"])
hu = Ru[(Ru["real_pb"]>0) & Ru["tp_mid"].notna()]
print(f"N={len(Ru)}  H1 mean pct={Ru['p_mid'].mean():.4f} clustered CI=[{cl[0]:.4f},{cl[1]:.4f}]  "
      f"tail={Ru['tail_hit'].mean():.4f}  H2 mean pct={hu['tp_mid'].mean():.4f} (N={len(hu)})")
