"""Exit-VELOCITY sweep (READ-ONLY research) — tests the owner's get-in-get-out thesis.

Hypothesis (2026-06-17): the +80% / -60% / 3-day-hold bracket gives back early gains
(watched live on TER, ANET). A faster policy — take a small target (+25%) and cut
quickly — recycles capital ~3x faster. Even a smaller per-trade % can WIN on
RETURN-PER-CAPITAL-DAY (velocity of capital), which is the metric we never scored.

Re-replays the SAME cached option minute-bars (realized_label.pkl, the 1,375 FILLED
fills) under a GRID of exit policies, holding the 10:00 entry constant. Production-
faithful: conservative intrabar ordering (trail/stop before target), and — the honest
part — EVERY exit pays the production 2% slippage, so high-velocity policies that do
more round-trips are charged for them. A zero-cost column is shown alongside so the
transaction-cost erosion of the velocity edge is explicit.

Metrics per policy: mean per-trade net return + DAY-LEVEL 90% CI (cluster-bootstrap by
scan_date — effective N is days, not rows); win%; avg capital-occupancy in trading days
(when did it exit); RETURN-PER-OCCUPIED-DAY (the velocity metric); a naive annualized
compounding proxy (illustrative only); and the loss tail. Ranked by velocity.

Primary universe = BULLISH (current strategy). Run:
    /home/user/gammarips-engine/.venv/bin/python backtesting_and_research/exit_velocity_sweep.py
"""
import datetime
import numpy as np
import pandas as pd
from realized_option_label import load_window_bars, nth_next_td, ts_ms, EST, TRAIL_TRIGGER_PCT, TRAIL_DRAWDOWN_PCT

np.random.seed(7)
PKL = "/home/user/gammarips-engine/backtesting_and_research/realized_label.pkl"
SLIP = 0.02  # production slippage: pay UP on entry, fill DOWN on every exit (round-trip cost)


def _d(b):
    return datetime.datetime.fromtimestamp(b["t"] / 1000, tz=EST).date()


def replay(bars, hold_days, target_pct, stop_pct, use_trail, slip=SLIP):
    """Return (net_return, occupancy_days) or None. hold_days = ordered trading days held;
    timeout = 15:50 on the last hold day. Exit fills pay `slip`."""
    entry_day = hold_days[0]
    timeout_day = hold_days[-1]
    entry_ts = ts_ms(entry_day, (10, 0))
    timeout_ts = ts_ms(timeout_day, (15, 50))
    eday = [b for b in bars if _d(b) == entry_day]
    if not eday:
        return None
    after = [b for b in eday if b["t"] >= entry_ts]
    entry_bar = after[0] if after else eday[-1]
    if not entry_bar or entry_bar.get("v", 0) == 0:
        return None
    base = entry_bar["c"] * (1 + slip)               # pay up on entry
    target = base * (1 + target_pct)
    stop = base * (1 - stop_pct) if stop_pct is not None else None
    trig = base * (1 + TRAIL_TRIGGER_PCT)
    idx = bars.index(entry_bar)
    peak = base; trail_active = False; trail_level = None
    exit_price = None; last_in = None; exit_bar = None
    for j in range(idx + 1, len(bars)):
        b = bars[j]
        if b["t"] >= timeout_ts:
            xb = last_in if last_in is not None else b
            exit_price = xb["c"] * (1 - slip); exit_bar = xb; break
        if b["h"] > peak:
            peak = b["h"]
            if peak >= trig:
                trail_active = True
            if trail_active:
                trail_level = peak * (1 - TRAIL_DRAWDOWN_PCT)
        if use_trail and trail_active and b["l"] <= trail_level:
            exit_price = trail_level * (1 - slip); exit_bar = b; break
        if stop is not None and b["l"] <= stop:
            exit_price = stop * (1 - slip); exit_bar = b; break
        if b["h"] >= target:
            exit_price = target * (1 - slip); exit_bar = b; break
        last_in = b
    if exit_price is None:
        xb = last_in if last_in is not None else entry_bar
        exit_price = xb["c"] * (1 - slip); exit_bar = xb
    ret = (exit_price - base) / base
    xdate = _d(exit_bar)
    occ = (hold_days.index(xdate) + 1) if xdate in hold_days else len(hold_days)
    return ret, occ


# FINER same-day (H1) grid to LOCK the V7 bracket: targets +30/+40/+50/none x stops -25/-30/-40.
# All H1 (10:00 entry -> target/stop -> 15:45 flat). 'none' target (9.99) = let it ride to the close.
POLICIES = [
    ("BASELINE 80/60 trail H3", 3, 0.80, 0.60, True),   # reference
    ("GIGO 30/25 H1", 1, 0.30, 0.25, False),
    ("GIGO 30/30 H1", 1, 0.30, 0.30, False),
    ("GIGO 30/40 H1", 1, 0.30, 0.40, False),
    ("GIGO 40/25 H1", 1, 0.40, 0.25, False),
    ("GIGO 40/30 H1", 1, 0.40, 0.30, False),
    ("GIGO 40/40 H1", 1, 0.40, 0.40, False),
    ("GIGO 50/25 H1", 1, 0.50, 0.25, False),
    ("GIGO 50/30 H1", 1, 0.50, 0.30, False),
    ("GIGO 50/40 H1", 1, 0.50, 0.40, False),
    ("GIGO ride/30 H1", 1, 9.99, 0.30, False),   # no target, stop -30, flat at close
    ("GIGO ride/40 H1", 1, 9.99, 0.40, False),
]


def day_ci(daily_means, B=2000):
    """Day-level cluster bootstrap 90% CI on the mean of per-day values."""
    v = np.array(daily_means, float)
    boot = [np.mean(np.random.choice(v, len(v), True)) for _ in range(B)]
    return np.percentile(boot, 5), np.percentile(boot, 95)


def run(universe_label, fil):
    # Load each fill's bars ONCE; replay every policy on it.
    per_policy = {name: [] for name, *_ in POLICIES}   # list of (scan_date, ret, occ)
    per_policy_nocost = {name: [] for name, *_ in POLICIES}
    for _, row in fil.iterrows():
        ed = pd.to_datetime(row["entry_day"]); c = row["recommended_contract"]
        if pd.isna(ed) or c is None:
            continue
        ed = ed.date()
        h3 = [d for d in [ed, nth_next_td(ed, 1), nth_next_td(ed, 2)] if d is not None]
        if not h3:
            continue
        bars, _, _ = load_window_bars(c + ".json", h3)
        if not bars:
            continue
        sd = str(row["scan_date"])
        for name, nh, tgt, stop, trail in POLICIES:
            hd = h3[:nh]
            r = replay(bars, hd, tgt, stop, trail, slip=SLIP)
            r0 = replay(bars, hd, tgt, stop, trail, slip=0.0)
            if r is not None:
                per_policy[name].append((sd, r[0], r[1]))
            if r0 is not None:
                per_policy_nocost[name].append((sd, r0[0], r0[1]))

    print(f"\n================  {universe_label}  (N={len(fil)} fills)  ================")
    print(f"{'policy':26s} {'mean':>7s} {'90%CI(day)':>18s} {'win%':>6s} {'occ_d':>6s} "
          f"{'ret/day':>8s} {'annual~':>9s} {'p5':>7s} {'mean_0cost':>10s}")
    rows = []
    for name, *_ in POLICIES:
        recs = per_policy[name]
        if not recs:
            continue
        df = pd.DataFrame(recs, columns=["sd", "ret", "occ"])
        mean = df["ret"].mean()
        win = (df["ret"] > 0).mean() * 100
        occ = df["occ"].mean()
        rpd = mean / occ if occ else float("nan")
        annual = (1 + mean) ** (252.0 / occ) - 1 if occ and mean > -1 else float("nan")
        p5 = np.percentile(df["ret"], 5)
        daily = df.groupby("sd")["ret"].mean().values   # per-day mean -> day-level stats
        lo, hi = day_ci(daily)
        df0 = pd.DataFrame(per_policy_nocost[name], columns=["sd", "ret", "occ"])
        mean0 = df0["ret"].mean()
        rows.append((name, mean, lo, hi, win, occ, rpd, annual, p5, mean0, daily))
        # clip annual display for sanity
        ann_disp = f"{annual*100:>7.0f}%" if np.isfinite(annual) and abs(annual) < 100 else "  >9900%"
        print(f"{name:26s} {mean:+7.3f} [{lo:+.3f},{hi:+.3f}] {win:5.1f}% {occ:6.2f} "
              f"{rpd:+8.4f} {ann_disp:>9s} {p5:+7.2f} {mean0:+10.3f}")

    # Paired day-level delta vs baseline on per-trade return.
    base = next((r for r in rows if r[0].startswith("BASELINE")), None)
    if base:
        base_daily = pd.Series(base[10], index=range(len(base[10])))
        print(f"\npaired day-level mean-return delta vs BASELINE (per-trade; +=beats current):")
        # rebuild per-day series keyed by scan_date for proper pairing
        base_recs = pd.DataFrame(per_policy["BASELINE 80/60 trail H3"], columns=["sd", "ret", "occ"])
        base_day = base_recs.groupby("sd")["ret"].mean()
        for name, *_ in POLICIES:
            if name.startswith("BASELINE"):
                continue
            recs = pd.DataFrame(per_policy[name], columns=["sd", "ret", "occ"])
            if recs.empty:
                continue
            pol_day = recs.groupby("sd")["ret"].mean()
            j = pd.concat([base_day.rename("b"), pol_day.rename("p")], axis=1).dropna()
            d = (j["p"] - j["b"]).values
            lo, hi = day_ci(d)
            star = "  *" if (lo > 0 or hi < 0) else ""
            print(f"  {name:26s} delta={d.mean():+.4f}  90CI=[{lo:+.4f},{hi:+.4f}]  n_days={len(d)}{star}")


def main():
    r = pd.read_pickle(PKL)
    fil = r[r["status"] == "FILLED"].copy()
    run("BULLISH only (current strategy)", fil[fil["direction"] == "BULLISH"])
    run("ALL directions (context)", fil)
    print("\nNOTES: ret/day = mean_return / avg_occupancy_days (the velocity metric). "
          "annual~ = naive (1+mean)^(252/occ)-1, ILLUSTRATIVE only (ignores variance drag/capacity). "
          "mean_0cost = same policy with zero slippage (shows transaction-cost erosion). "
          "* = day-level 90% CI on paired delta excludes 0. Single regime (2026-Q2), pre-V6 pool.")


if __name__ == "__main__":
    main()
