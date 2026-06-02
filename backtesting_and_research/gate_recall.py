import pandas as pd, numpy as np
r = pd.read_pickle("realized_label.pkl")

# fillable cohort for the (degenerate) realized proxy
fil = r[r["status"]=="FILLED"].copy()
# leaked-label cohort (labeled rows)
lab = r[r["peak_return_3d"].notna()].copy()

def winflags(df, kind):
    if kind=="leaked":
        # leaked underlying-peak winner ~ what the audit used: peak_return_3d, sign-adjusted by direction already? peak_return_3d is underlying peak move; is_win is the trade label
        w = df["is_win"].astype(float).fillna(0).astype(bool)
    elif kind=="real80":
        w = (df["realized_ret"]>=0.80) | (df["exit_reason"]=="TARGET")
    elif kind=="real25":
        w = df["realized_ret"]>=0.25
    return w

GATES = {
 "spread<=8%":      lambda d: d["recommended_spread_pct"]<=0.08,
 "V/OI>2":          lambda d: d["volume_oi_ratio"]>2,
 "moneyness 5-10%": lambda d: d["moneyness_pct"].abs().between(0.05,0.10),
 "VIX<=VIX3M":      lambda d: d["vix3m_at_enrich"].notna(),  # placeholder; need vix vs vix3m
 "OI>=10":          lambda d: d["recommended_oi"]>=10,
 "vol>=50":         lambda d: d["recommended_volume"]>=50,
 "DTE 7-45":        lambda d: d["recommended_dte"].between(7,45),
}

def table(df, kind):
    w = winflags(df, kind)
    base = w.mean()
    n=len(df); nwin=int(w.sum())
    rows=[]
    for g,fn in GATES.items():
        try: passmask = fn(df).fillna(False)
        except Exception as e: passmask=pd.Series(False,index=df.index)
        kept_win = (passmask & w).sum()
        recall = kept_win / nwin if nwin else float("nan")
        losers = (~w)
        removed_losers = (losers & ~passmask).sum()
        loser_removal = removed_losers / losers.sum() if losers.sum() else float("nan")
        pass_wr = (w[passmask]).mean() if passmask.sum() else float("nan")
        lift = pass_wr - base if passmask.sum() else float("nan")
        mark = "HELPS" if (lift>0.01 and recall>0.5) else ("HURTS" if recall<0.5 else "NEUTRAL")
        rows.append([g,passmask.sum(),round(recall,3),round(loser_removal,3),round(pass_wr,3),round(lift,3),mark])
    print(f"\n=== {kind}  N={n}  winners={nwin}  baseline_wr={base:.3f} ===")
    print(pd.DataFrame(rows,columns=["gate","n_pass","win_recall","loser_removal","pass_wr","prec_lift","verdict"]).to_string(index=False))

table(lab,"leaked")
table(fil,"real80")
table(fil,"real25")
