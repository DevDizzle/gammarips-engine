"""Validity checks demanded by gammarips-review before the V/OI finding can
become a proposal (READ-ONLY; reads realized_label.pkl). Covers:
  1. Selection-confound: FILLED rate by gate pass/fail (does the gate predict fillability?)
  2. Per-gate recall/precision restricted to n_hold_bardays==3 (no truncated windows)
  3. Bootstrap 90% CI on V/OI precision-lift + recall
  4. Chronological split (entry_day below/above median)
"""
import pandas as pd, numpy as np
np.random.seed(7)

r = pd.read_pickle("/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl")
r["entry_day"] = pd.to_datetime(r["entry_day"])

GATES = {
 "spread<=8%":      lambda d: d["recommended_spread_pct"] <= 0.08,
 "V/OI>2":          lambda d: d["volume_oi_ratio"] > 2,
 "moneyness 5-10%": lambda d: d["moneyness_pct"].abs().between(0.05, 0.10),
 "OI>=10":          lambda d: d["recommended_oi"] >= 10,
 "vol>=50":         lambda d: d["recommended_volume"] >= 50,
}

# ---------- 1. SELECTION CONFOUND ----------
# fill-attempted cohort = had a real window; drop pure coverage/calendar misses
att = r[r["status"].isin(["FILLED", "INVALID_LIQUIDITY", "CACHE_EMPTY"])].copy()
att["filled"] = (att["status"] == "FILLED")
print(f"=== 1. SELECTION CONFOUND  (fill-attempted N={len(att)}, overall fill rate {att['filled'].mean():.3f}) ===")
print("If a gate's PASS fill-rate >> FAIL fill-rate, the FILLED-only recall is confounded by fillability.")
rows = []
for g, fn in GATES.items():
    m = fn(att).fillna(False)
    fr_pass = att.loc[m, "filled"].mean() if m.sum() else float("nan")
    fr_fail = att.loc[~m, "filled"].mean() if (~m).sum() else float("nan")
    rows.append([g, int(m.sum()), round(fr_pass, 3), round(fr_fail, 3), round(fr_pass - fr_fail, 3)])
print(pd.DataFrame(rows, columns=["gate", "n_pass", "fill_rate_pass", "fill_rate_fail", "gap"]).to_string(index=False))

# ---------- helper: recall/lift table on a FILLED subset ----------
def winflags(df, kind):
    if kind == "real80": return (df["realized_ret"] >= 0.80) | (df["exit_reason"] == "TARGET")
    if kind == "real25": return df["realized_ret"] >= 0.25
    raise ValueError

def table(df, kind, title):
    w = winflags(df, kind); base = w.mean(); n = len(df); nwin = int(w.sum())
    print(f"\n--- {title} | {kind} | N={n} winners={nwin} baseline={base:.3f} ---")
    out = []
    for g, fn in GATES.items():
        p = fn(df).fillna(False)
        recall = (p & w).sum() / nwin if nwin else float("nan")
        pass_wr = w[p].mean() if p.sum() else float("nan")
        out.append([g, int(p.sum()), round(recall, 3), round(pass_wr, 3), round(pass_wr - base, 3)])
    print(pd.DataFrame(out, columns=["gate", "n_pass", "recall", "pass_wr", "prec_lift"]).to_string(index=False))

# ---------- 2. n_hold_bardays == 3 only ----------
fil = r[r["status"] == "FILLED"].copy()
full = fil[fil["n_hold_bardays"] == 3].copy()
print(f"\n=== 2. FULL-WINDOW ONLY (n_hold_bardays==3): N={len(full)} of {len(fil)} fills ===")
table(full, "real80", "full-window")
table(full, "real25", "full-window")

# ---------- 3. BOOTSTRAP CI on V/OI (full-window cohort, real25) ----------
print("\n=== 3. BOOTSTRAP 90% CI for V/OI>2 (full-window, real25) ===")
d = full
w = winflags(d, "real25").values
p = (d["volume_oi_ratio"] > 2).fillna(False).values
def stat(idx):
    ww, pp = w[idx], p[idx]
    base = ww.mean()
    recall = (pp & ww).sum() / ww.sum() if ww.sum() else np.nan
    lift = ww[pp].mean() - base if pp.sum() else np.nan
    return recall, lift
N = len(d); B = 2000
recs, lifts = [], []
for _ in range(B):
    idx = np.random.randint(0, N, N)
    rc, lf = stat(idx)
    recs.append(rc); lifts.append(lf)
recs, lifts = np.array(recs), np.array(lifts)
pt_rc, pt_lf = stat(np.arange(N))
print(f"  recall      point={pt_rc:.3f}  90% CI [{np.nanpercentile(recs,5):.3f}, {np.nanpercentile(recs,95):.3f}]")
print(f"  prec_lift   point={pt_lf:.3f}  90% CI [{np.nanpercentile(lifts,5):.3f}, {np.nanpercentile(lifts,95):.3f}]")
print(f"  P(prec_lift <= 0) = {(lifts <= 0).mean():.3f}   (high => gate does NOT improve selection)")

# ---------- 4. CHRONOLOGICAL SPLIT ----------
med = full["entry_day"].median()
print(f"\n=== 4. CHRONOLOGICAL SPLIT at entry_day median {med.date()} (full-window) ===")
table(full[full["entry_day"] < med], "real25", "H1 (early)")
table(full[full["entry_day"] >= med], "real25", "H2 (late)")
