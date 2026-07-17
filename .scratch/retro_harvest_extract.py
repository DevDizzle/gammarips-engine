"""READ-ONLY extraction #3 (harvest/target-exit study). SELECT only. Seed n/a (pull)."""
from google.cloud import bigquery
import pandas as pd

SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
client = bigquery.Client(project="profitscout-fida8")

# (1) full outcomes table — everything needed for universe accounting + cohorts
out = client.query("""
SELECT scan_date, entry_day, ticker, direction, recommended_contract,
       recommended_delta, mom_60, overnight_score, pool_size,
       was_tournament_pick, was_topscore_pick, policy_version,
       opp_window_days, opp_status, opp_entry_timestamp, opp_entry_price,
       opp_peak_return, opp_trough_return, opp_minutes_to_peak,
       opp_minutes_to_trough, opp_bar_count, opp_sim_version,
       realized_return_pct_3d, exit_reason_3d, exit_day_3d, entry_price_3d,
       label_3d_sim_version, label_3d_hold_days, label_3d_stop_pct, label_3d_target_pct,
       realized_return_pct, exit_reason, illiquid_exit
FROM `profitscout-fida8.profit_scout.enriched_option_outcomes`
""").to_dataframe()
print("outcomes rows:", len(out))
print("scan_date range:", out.scan_date.min(), "->", out.scan_date.max())
print("\nopp_status counts:\n", out.opp_status.value_counts(dropna=False))
print("\nopp_window_days:\n", out.opp_window_days.value_counts(dropna=False))
print("\nopp_sim_version:\n", out.opp_sim_version.value_counts(dropna=False))
print("\ndirection:\n", out.direction.value_counts(dropna=False))
print("\nlabel_3d sim:\n", out.label_3d_sim_version.value_counts(dropna=False))
print("dupes on (scan_date,ticker,contract):",
      out.duplicated(["scan_date","ticker","recommended_contract"]).sum())
out.to_parquet(f"{SP}/retro_harvest_outcomes.parquet")

# (2) ledger pick identities — ALL eras
led = client.query("""
SELECT scan_date, ticker, recommended_contract, direction, policy_version, is_skipped
FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
""").to_dataframe()
print("\nledger rows:", len(led), "| skipped:", led.is_skipped.sum())
print("ledger policy versions:\n", led.policy_version.value_counts(dropna=False))
print("ledger scan range:", led.scan_date.min(), "->", led.scan_date.max())
led.to_parquet(f"{SP}/retro_harvest_ledger.parquet")
