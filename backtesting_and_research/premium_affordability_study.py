"""Entry-premium / affordability study (READ-ONLY research).

Question: does ENTRY CONTRACT PREMIUM (per-contract cost = D+1 open fill x 100)
relate to outcomes under the +80/-60/trail bracket? Owner wants a <=$1,000/contract
affordability cap (~$1k account, max-1-lot floor).

Entry premium = base_entry (D+1 10:00 ET bar close x 1.02 slippage) x 100.
This is the SAME base_entry the realized label used. recommended_mid_price is the
scan-day mid (edge-inflating artifact) and is NOT used for entry.

We recompute base_entry per FILLED row from the local cache to get the exact
per-contract entry cost, then bucket and control for moneyness + DTE.
"""
import datetime, json, os
import numpy as np
import pandas as pd
from realized_option_label import (
    load_window_bars, next_td, nth_next_td, ts_ms, CACHE, EST,
    HOLD_DAYS, SLIP, ENTRY_HHMM,
)

np.random.seed(7)
PKL = "/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl"


def entry_premium(contract, entry_day):
    """Recompute base_entry (per-share) = entry-bar close * SLIP. Returns None if no bar."""
    if contract is None or pd.isna(entry_day):
        return None
    ed = entry_day.date() if hasattr(entry_day, "date") else entry_day
    hold = [d for d in [ed, nth_next_td(ed, 1), nth_next_td(ed, 2)] if d is not None]
    bars, _, _ = load_window_bars(contract + ".json", hold)
    if not bars:
        return None
    entry_ts = ts_ms(ed, ENTRY_HHMM)
    eday = [b for b in bars
            if datetime.datetime.fromtimestamp(b["t"]/1000, tz=EST).date() == ed]
    if not eday:
        return None
    after = [b for b in eday if b["t"] >= entry_ts]
    entry_bar = after[0] if after else (eday[-1] if eday else None)
    if not entry_bar or entry_bar.get("v", 0) == 0:
        return None
    return entry_bar["c"] * SLIP


def boot_ci(v, B=2000):
    v = np.asarray(v, dtype=float)
    if len(v) < 5:
        return (np.nan, np.nan)
    bs = [np.mean(np.random.choice(v, len(v), replace=True)) for _ in range(B)]
    return (np.percentile(bs, 5), np.percentile(bs, 95))


def main():
    r = pd.read_pickle(PKL)
    r["entry_day"] = pd.to_datetime(r["entry_day"])
    fil = r[r["status"] == "FILLED"].copy()
    print(f"FILLED rows: {len(fil)}")

    # recompute exact per-contract entry premium
    prem = []
    for _, row in fil.iterrows():
        bp = entry_premium(row["recommended_contract"], row["entry_day"])
        prem.append(bp * 100 if bp is not None else np.nan)
    fil["entry_prem"] = prem
    print(f"entry_prem recomputed for {fil['entry_prem'].notna().sum()} / {len(fil)} fills")
    miss = fil["entry_prem"].isna().sum()
    if miss:
        print(f"  ({miss} could not be recomputed from cache -> dropped from premium analysis)")
    fil = fil[fil["entry_prem"].notna()].copy()

    fil["m"] = pd.to_numeric(fil["moneyness_pct"], errors="coerce")
    fil["dte"] = pd.to_numeric(fil["recommended_dte"], errors="coerce")
    fil["ret"] = pd.to_numeric(fil["realized_ret"], errors="coerce")
    fil = fil[fil["ret"].notna()].copy()

    print("\n=== entry_prem distribution (per-contract $, FILLED) ===")
    print(fil["entry_prem"].describe().to_string())
    print(f"  share <= $1000/contract: {(fil['entry_prem'] <= 1000).mean():.3f}")

    # ---- premium buckets ----
    def pbucket(p):
        if p < 300:    return "1_<300"
        if p < 750:    return "2_300-750"
        if p < 1500:   return "3_750-1500"
        if p < 3000:   return "4_1500-3000"
        return "5_>3000"
    fil["pb"] = fil["entry_prem"].apply(pbucket)
    order = ["1_<300", "2_300-750", "3_750-1500", "4_1500-3000", "5_>3000"]

    def outcomes(sub):
        n = len(sub)
        tgt = (sub["exit_reason"] == "TARGET").mean()
        stp = (sub["exit_reason"] == "STOP").mean()
        tmo = (sub["exit_reason"] == "TIMEOUT").mean()
        trl = (sub["exit_reason"] == "TRAIL").mean()
        ev = sub["ret"].mean()
        lo, hi = boot_ci(sub["ret"].values)
        return n, tgt, stp, tmo, trl, ev, lo, hi

    print("\n=== 1. OUTCOMES BY ENTRY-PREMIUM BUCKET (FILLED) ===")
    rows = []
    for b in order:
        sub = fil[fil["pb"] == b]
        if len(sub) == 0:
            continue
        n, tgt, stp, tmo, trl, ev, lo, hi = outcomes(sub)
        rows.append([b, n, round(tgt,3), round(stp,3), round(tmo,3), round(trl,3),
                     round(ev,3), f"[{lo:.3f},{hi:.3f}]"])
    print(pd.DataFrame(rows, columns=["prem_bucket","N","P_TARGET","P_STOP","P_TIMEOUT",
                                      "P_TRAIL","mean_ret","EV_90CI"]).to_string(index=False))

    # ---- binary at owner's threshold ----
    print("\n=== 2. OWNER FILTER: entry_prem <= $1000/contract vs > $1000 ===")
    rows = []
    for name, mask in [("<=1000", fil["entry_prem"] <= 1000), (">1000", fil["entry_prem"] > 1000)]:
        sub = fil[mask]
        n, tgt, stp, tmo, trl, ev, lo, hi = outcomes(sub)
        rows.append([name, n, round(tgt,3), round(stp,3), round(tmo,3), round(trl,3),
                     round(ev,3), f"[{lo:.3f},{hi:.3f}]"])
    print(pd.DataFrame(rows, columns=["group","N","P_TARGET","P_STOP","P_TIMEOUT",
                                      "P_TRAIL","mean_ret","EV_90CI"]).to_string(index=False))

    # difference in EV bootstrap
    a = fil.loc[fil["entry_prem"] <= 1000, "ret"].values
    b = fil.loc[fil["entry_prem"] > 1000, "ret"].values
    diffs = [np.mean(np.random.choice(a, len(a))) - np.mean(np.random.choice(b, len(b))) for _ in range(2000)]
    print(f"  EV diff (<=1000 minus >1000): point={a.mean()-b.mean():.3f}  "
          f"90% CI [{np.percentile(diffs,5):.3f}, {np.percentile(diffs,95):.3f}]  "
          f"P(diff<=0)={np.mean(np.array(diffs)<=0):.3f}")

    # ---- 3. CONTROL FOR MONEYNESS + DTE (within-moneyness premium comparison) ----
    print("\n=== 3. CONTROL: premium effect WITHIN moneyness bucket ===")
    def mbucket(m):
        if pd.isna(m):   return None
        if m < 0:        return "ITM(<0)"
        if m < 0.05:     return "ATM(0-5%)"
        if m <= 0.10:    return "BAND(5-10%)"
        if m <= 0.15:    return "OTM(10-15%)"
        return "DEEP(>15%)"
    fil["mb"] = fil["m"].apply(mbucket)
    print("Within each moneyness bucket, compare cheap (<=median prem) vs expensive (>median):")
    rows = []
    for mb in ["ITM(<0)","ATM(0-5%)","BAND(5-10%)","OTM(10-15%)","DEEP(>15%)"]:
        sub = fil[fil["mb"] == mb]
        if len(sub) < 10:
            rows.append([mb, len(sub), "n<10", "", "", "", "", ""])
            continue
        med = sub["entry_prem"].median()
        cheap = sub[sub["entry_prem"] <= med]
        exp = sub[sub["entry_prem"] > med]
        rows.append([mb, len(sub), round(med,0),
                     len(cheap), round(cheap["ret"].mean(),3), round((cheap["exit_reason"]=="TARGET").mean(),3),
                     len(exp), round(exp["ret"].mean(),3), round((exp["exit_reason"]=="TARGET").mean(),3)])
    print(pd.DataFrame(rows, columns=["mbucket","N","med_prem","n_cheap","cheap_EV","cheap_tgt",
                                      "n_exp","exp_EV","exp_tgt"]).to_string(index=False))

    # ---- 3b. premium bucket within the production BAND (5-10%) only ----
    print("\n=== 3b. premium buckets WITHIN production moneyness band (5-10% OTM) ===")
    band = fil[fil["mb"] == "BAND(5-10%)"]
    rows = []
    for b in order:
        sub = band[band["pb"] == b]
        if len(sub) == 0: continue
        n, tgt, stp, tmo, trl, ev, lo, hi = outcomes(sub)
        rows.append([b, n, round(tgt,3), round(stp,3), round(ev,3),
                     f"[{lo:.3f},{hi:.3f}]" if not np.isnan(lo) else "n<5"])
    print(pd.DataFrame(rows, columns=["prem_bucket","N","P_TARGET","P_STOP","mean_ret","EV_90CI"]).to_string(index=False))

    # correlation: premium vs moneyness, dte (mechanical confound evidence)
    print("\n=== confound evidence: premium correlations ===")
    cc = fil[["entry_prem","m","dte","recommended_spread_pct"]].copy()
    cc["recommended_spread_pct"] = pd.to_numeric(cc["recommended_spread_pct"], errors="coerce")
    print(cc.corr(method="spearman")["entry_prem"].round(3).to_string())

    # ---- 4. CHRONOLOGICAL STABILITY of the <=1000 filter EV ----
    med_day = fil["entry_day"].median()
    print(f"\n=== 4. CHRONOLOGICAL SPLIT at {med_day.date()} ===")
    rows = []
    for name, mask in [("<=1000", fil["entry_prem"] <= 1000), (">1000", fil["entry_prem"] > 1000)]:
        sub = fil[mask]
        h1 = sub[sub["entry_day"] < med_day]["ret"]
        h2 = sub[sub["entry_day"] >= med_day]["ret"]
        rows.append([name, len(h1), round(h1.mean(),3) if len(h1) else None,
                     len(h2), round(h2.mean(),3) if len(h2) else None])
    print(pd.DataFrame(rows, columns=["group","n_H1","H1_EV","n_H2","H2_EV"]).to_string(index=False))

    # ---- 5. FUNNEL IMPACT: fraction of candidate-days retaining >=1 candidate under <=1000 ----
    print("\n=== 5. FUNNEL IMPACT of <=1000 filter (per scan-day) ===")
    # use the full attempted cohort (FILLED) keyed by scan_date for day-level retention
    fil["scan_date"] = pd.to_datetime(fil["scan_date"]).dt.date
    days = fil.groupby("scan_date")
    n_days = days.ngroups
    days_with_cheap = sum((g["entry_prem"] <= 1000).any() for _, g in days)
    print(f"  scan-days with >=1 FILLED candidate: {n_days}")
    print(f"  scan-days retaining >=1 candidate <= $1000: {days_with_cheap} ({days_with_cheap/n_days:.3f})")
    # also on the full enriched candidate set (not just FILLED) using recommended_mid_price*100 as a proxy
    full = r.copy()
    full["mid_prem"] = pd.to_numeric(full["recommended_mid_price"], errors="coerce") * 100
    full["scan_date"] = pd.to_datetime(full["scan_date"]).dt.date
    fdays = full.dropna(subset=["mid_prem"]).groupby("scan_date")
    nfd = fdays.ngroups
    fd_cheap = sum((g["mid_prem"] <= 1000).any() for _, g in fdays)
    print(f"  [all enriched, scan-day mid_prem proxy] days: {nfd}, retain <=1000: {fd_cheap} ({fd_cheap/nfd:.3f})")
    print(f"  [all enriched] candidate share <= $1000 (mid proxy): {(full['mid_prem']<=1000).mean():.3f}")


if __name__ == "__main__":
    main()
