"""
Part 2 analysis on /tmp/score_vs_option_return_pilot.parquet:
  1. Apply realistic friction (entry mid + half-spread, exit mid - half-spread)
     and re-bucket by score.
  2. Score x direction cross-tab (does BEARISH work at any score?)
  3. Direction split inside the current gate (score >= 6).
"""
import pandas as pd

df = pd.read_parquet("/tmp/score_vs_option_return_pilot.parquet")

# --- Friction model ----------------------------------------------------
# Assume same spread_pct on exit as on entry (conservative).
# Effective entry = mid * (1 + spread/2)
# Effective exit  = mid * (1 - spread/2)
# ret_fric_close = (next_close*(1-s/2) - entry*(1+s/2)) / (entry*(1+s/2))
s = df["spread_pct"].fillna(0).clip(lower=0, upper=0.8)
entry_eff = df["entry_mid"] * (1 + s / 2)
exit_close_eff = df["next_close"] * (1 - s / 2)
exit_high_eff  = df["next_high"]  * (1 - s / 2)
df["ret_close_fric"] = (exit_close_eff - entry_eff) / entry_eff
df["ret_high_fric"]  = (exit_high_eff  - entry_eff) / entry_eff
df["win_close_fric"] = (df["ret_close_fric"] > 0).astype(int)
df["win_high_fric"]  = (df["ret_high_fric"] > 0).astype(int)
df["hit25_fric"]     = (df["ret_high_fric"] >= 0.25).astype(int)

print(f"=== Dataset: {len(df)} contract-days ===\n")
print(f"Mean spread_pct on entries: {df['spread_pct'].mean():.3f}  "
      f"median: {df['spread_pct'].median():.3f}\n")

# --- (1) Score bucket with friction ------------------------------------
print("=" * 88)
print("FOLLOW-UP 1: Returns AFTER realistic friction (both legs crossed at mid ± half-spread)")
print("=" * 88)
print(f"{'score':>6} | {'n':>5} | {'mean_close_fric':>15} | {'median':>8} | "
      f"{'win%':>6} | {'hit25%':>7} | {'mean_high_fric':>14}")
print("-" * 88)
for score in sorted(df["overnight_score"].dropna().unique()):
    sub = df[df["overnight_score"] == score]
    if len(sub) < 5:
        continue
    print(f"{int(score):>6d} | {len(sub):>5d} | "
          f"{sub['ret_close_fric'].mean():>+14.4f}  | "
          f"{sub['ret_close_fric'].median():>+7.4f} | "
          f"{100*sub['win_close_fric'].mean():>5.1f}% | "
          f"{100*sub['hit25_fric'].mean():>6.1f}% | "
          f"{sub['ret_high_fric'].mean():>+13.4f}")

print("\n--- Gate-style buckets with friction ---")
for label, mask in [
    ("score 0            ", df["overnight_score"] == 0),
    ("score 1            ", df["overnight_score"] == 1),
    ("score <= 3  (culled)", df["overnight_score"] <= 3),
    ("score 4-5   (culled)", df["overnight_score"].between(4, 5)),
    ("score >= 6  (passed)", df["overnight_score"] >= 6),
    ("score >= 7         ", df["overnight_score"] >= 7),
]:
    sub = df[mask]
    if len(sub) == 0:
        continue
    print(
        f"{label}: n={len(sub):4d}  "
        f"mean_close_fric={sub['ret_close_fric'].mean():+.4f}  "
        f"median={sub['ret_close_fric'].median():+.4f}  "
        f"win%={100*sub['win_close_fric'].mean():5.1f}  "
        f"hit25%={100*sub['hit25_fric'].mean():5.1f}  "
        f"mean_high_fric={sub['ret_high_fric'].mean():+.4f}"
    )

# --- (2) Score x direction ---------------------------------------------
print("\n" + "=" * 88)
print("FOLLOW-UP 2: Score x Direction (friction applied)")
print("=" * 88)
for direction in ["BULLISH", "BEARISH"]:
    sub_all = df[df["direction"] == direction]
    print(f"\n{direction}  (n={len(sub_all)})")
    print(f"{'score':>6} | {'n':>5} | {'mean_close_fric':>15} | "
          f"{'median':>8} | {'win%':>6} | {'hit25%':>7}")
    print("-" * 60)
    for score in sorted(sub_all["overnight_score"].dropna().unique()):
        sub = sub_all[sub_all["overnight_score"] == score]
        if len(sub) < 5:
            continue
        print(f"{int(score):>6d} | {len(sub):>5d} | "
              f"{sub['ret_close_fric'].mean():>+14.4f}  | "
              f"{sub['ret_close_fric'].median():>+7.4f} | "
              f"{100*sub['win_close_fric'].mean():>5.1f}% | "
              f"{100*sub['hit25_fric'].mean():>6.1f}%")

# --- (3) Direction split inside current gate --------------------------
print("\n" + "=" * 88)
print("FOLLOW-UP 3: What does the current gate (score >= 6) actually pass?")
print("=" * 88)
gated = df[df["overnight_score"] >= 6]
print(f"\nTotal rows with score >= 6: {len(gated)}")
split = gated["direction"].value_counts()
print("Direction split:")
for d, n in split.items():
    print(f"  {d}: {n}  ({100*n/len(gated):.1f}%)")

print("\nPerformance of gated rows by direction (friction applied):")
for d in ["BULLISH", "BEARISH"]:
    sub = gated[gated["direction"] == d]
    if len(sub) == 0:
        continue
    print(f"  {d}: n={len(sub)}  "
          f"mean_close_fric={sub['ret_close_fric'].mean():+.4f}  "
          f"win%={100*sub['win_close_fric'].mean():5.1f}  "
          f"hit25%={100*sub['hit25_fric'].mean():5.1f}")

# --- (4) The big "what-if": direction == BULLISH, no score gate --------
print("\n" + "=" * 88)
print("FOLLOW-UP 4: Proposed replacement gate — direction == BULLISH, no score floor")
print("=" * 88)
for label, mask in [
    ("CURRENT:   score >= 6             ",
     df["overnight_score"] >= 6),
    ("PROPOSED:  direction == BULLISH   ",
     df["direction"] == "BULLISH"),
    ("COMBINED:  BULLISH AND score >= 1 ",
     (df["direction"] == "BULLISH") & (df["overnight_score"] >= 1)),
    ("COMBINED:  BULLISH AND score >= 3 ",
     (df["direction"] == "BULLISH") & (df["overnight_score"] >= 3)),
    ("COMBINED:  BULLISH AND score >= 6 ",
     (df["direction"] == "BULLISH") & (df["overnight_score"] >= 6)),
]:
    sub = df[mask]
    if len(sub) == 0:
        continue
    print(
        f"{label}: n={len(sub):4d}  "
        f"mean_close_fric={sub['ret_close_fric'].mean():+.4f}  "
        f"median={sub['ret_close_fric'].median():+.4f}  "
        f"win%={100*sub['win_close_fric'].mean():5.1f}  "
        f"hit25%={100*sub['hit25_fric'].mean():5.1f}  "
        f"mean_high_fric={sub['ret_high_fric'].mean():+.4f}"
    )
