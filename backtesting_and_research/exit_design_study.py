"""Exit-design study (READ-ONLY research). Tests the deep-research / H13 claim
that the -60% PREMIUM stop wicks out on IV-crush/gamma noise and hurts EV.

Re-replays all FILLED fills under 4 exit policies on the SAME cached option bars,
holding entry cost constant (flat 1.02) so only the EXIT differs:
  BASELINE   : -60% stop + +80% target + 25%/+30% trail + day-3 time   (current prod)
  NO_HARDSTOP: drop the -60% stop, keep target + trail + time          (fix wick-outs)
  TARGET_ONLY: +80% target or day-3 close, no stop/trail
  TIME_ONLY  : pure 3-day hold, exit day-3 close (laissez-faire)
Underlying-based stop is NOT tested here (needs an underlying-minute fetch) — noted.
"""
import datetime
import numpy as np
import pandas as pd
from realized_option_label import (
    load_window_bars, nth_next_td, ts_ms, EST, HOLD_DAYS,
    STOP_PCT, TARGET_PCT, TRAIL_TRIGGER_PCT, TRAIL_DRAWDOWN_PCT,
)
np.random.seed(7)
PKL = "/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl"
SLIP = 1.02


def replay(bars, entry_day, exit_day, use_stop, use_target, use_trail):
    entry_ts = ts_ms(entry_day, (10, 0)); timeout_ts = ts_ms(exit_day, (15, 50))
    eday = [b for b in bars if datetime.datetime.fromtimestamp(b["t"]/1000, tz=EST).date() == entry_day]
    if not eday:
        return None
    after = [b for b in eday if b["t"] >= entry_ts]
    entry_bar = after[0] if after else eday[-1]
    if not entry_bar or entry_bar.get("v", 0) == 0:
        return None
    base = entry_bar["c"] * SLIP
    stop = base*(1-STOP_PCT); target = base*(1+TARGET_PCT); trig = base*(1+TRAIL_TRIGGER_PCT)
    idx = bars.index(entry_bar); peak = base; trail_active = False; trail_level = None
    exit_price = None; last_in = None
    for j in range(idx+1, len(bars)):
        b = bars[j]
        if b["t"] >= timeout_ts:
            exit_price = (last_in if last_in is not None else b)["c"]; break
        if b["h"] > peak:
            peak = b["h"]
            if peak >= trig: trail_active = True
            if trail_active: trail_level = peak*(1-TRAIL_DRAWDOWN_PCT)
        # conservative: stop/trail before target
        if use_trail and trail_active and b["l"] <= trail_level:
            exit_price = trail_level; break
        if use_stop and b["l"] <= stop:
            exit_price = stop; break
        if use_target and b["h"] >= target:
            exit_price = target; break
        last_in = b
    if exit_price is None:
        exit_price = (last_in if last_in is not None else entry_bar)["c"]
    return (exit_price - base)/base


def main():
    r = pd.read_pickle(PKL)
    fil = r[r["status"] == "FILLED"].copy()
    policies = {
        "BASELINE(stop+tgt+trail)": (True, True, True),
        "NO_HARDSTOP(tgt+trail)":   (False, True, True),
        "TARGET_ONLY":              (False, True, False),
        "TIME_ONLY(pure 3d)":       (False, False, False),
    }
    cols = {}
    for name, (us, ut, utr) in policies.items():
        rets = []
        for _, row in fil.iterrows():
            ed = pd.to_datetime(row["entry_day"]); c = row["recommended_contract"]
            if pd.isna(ed) or c is None: rets.append(np.nan); continue
            ed = ed.date(); xd = nth_next_td(ed, HOLD_DAYS-1)
            hold = [d for d in [ed, nth_next_td(ed,1), nth_next_td(ed,2)] if d is not None]
            bars, _, _ = load_window_bars(c+".json", hold)
            rets.append(replay(bars, ed, xd, us, ut, utr) if (xd and bars) else np.nan)
        cols[name] = pd.Series(rets, index=fil.index)

    print(f"FILLED fills: {len(fil)}\n")
    print(f"{'policy':28s} {'mean':>7s} {'median':>7s} {'win%':>6s} {'+25%':>6s} {'min':>7s} {'p5':>7s} {'meanCI_90':>20s}")
    for name, s in cols.items():
        v = s.dropna().values
        boot = [np.mean(np.random.choice(v, len(v), True)) for _ in range(2000)]
        ci = f"[{np.percentile(boot,5):+.3f},{np.percentile(boot,95):+.3f}]"
        print(f"{name:28s} {v.mean():+7.3f} {np.median(v):+7.3f} {(v>0).mean()*100:5.1f}% "
              f"{(v>=0.25).mean()*100:5.1f}% {v.min():+7.2f} {np.percentile(v,5):+7.2f} {ci:>20s}")
    # paired delta vs baseline (same fills)
    base = cols["BASELINE(stop+tgt+trail)"]
    print("\npaired mean delta vs BASELINE (positive = policy beats current):")
    for name, s in cols.items():
        if name.startswith("BASELINE"): continue
        d = (s - base).dropna().values
        boot = [np.mean(np.random.choice(d, len(d), True)) for _ in range(2000)]
        print(f"  {name:28s} delta={d.mean():+.3f}  90CI=[{np.percentile(boot,5):+.3f},{np.percentile(boot,95):+.3f}]")


if __name__ == "__main__":
    main()
