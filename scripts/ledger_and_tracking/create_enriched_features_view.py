"""Create `enriched_features_v1` — the leakage-safe FEATURES-ONLY view.

WHY THIS EXISTS (substrate must-fix #4)
---------------------------------------
`enriched_option_outcomes` is a flat ~64-col table that intermixes point-in-time
FEATURES with realized LABELS, an OPPORTUNITY SURFACE, regime TELEMETRY, and
LABEL-SEMANTICS tags. Today the ONLY thing keeping a headless agent / the MCP /
a research notebook out of the label columns is a DDL comment — a `SELECT *`
ingests every outcome column and silently leaks the future.

This view is the physical guard. It exposes ONLY:
  - identity / join keys (known at selection time), and
  - point-in-time FEATURE columns (leakage-safe, as-of <= scan_date), plus
  - cohort/linkage metadata that describes the SELECTION (not the outcome).

Every outcome / label / opportunity / telemetry column is EXCLUDED by an
EXPLICIT ALLOWLIST (not a denylist) — if a new column appears on the base table
it is dropped by default until someone deliberately classifies it and adds it
here. That is the safe failure mode.

>>> AGENTS / MCP / RESEARCH MUST QUERY `enriched_features_v1` FOR FEATURES. <<<
>>> The raw `enriched_option_outcomes` table is for LABEL JOINS ONLY, by a  <<<
>>> human who understands the leakage rule below.                          <<<

LEAKAGE RULE (the classification boundary)
------------------------------------------
  FEATURE   : known as-of <= scan_date (the real selection point), OR a contract
              spec fixed at selection. Safe as a model input.
  IDENTITY  : join/identity keys + cohort metadata. Safe.
  OUTCOME   : realized after entry (prices, exits, PnL, underlying/SPY returns,
              iv_rank/iv_percentile/hv "_entry" benchmarking). NEVER a feature.
  OPP       : opportunity-surface MFE/MAE (opp_*). Exit-free profit potential —
              NOT a tradeable label and NOT a feature.
  TELEMETRY : entry-day-close regime (oc_*_at_close) + the legacy leaking
              entry-close regime (VIX_at_entry / SPY_trend_state /
              vix_5d_delta_entry). Realized after the same-day trade. NOT a
              feature. See substrate must-fix #2.
  LABEL     : 3-day bracket group (*_3d) + label-semantics tags (label_*).

Source of truth for names/groups: this repo's
`scripts/ledger_and_tracking/create_enriched_option_outcomes.py` (schema) and
`docs/DATA-CONTRACTS.md` (the enriched_option_outcomes contract section).

TRANSITION NOTE (regime + momentum features not yet on the live table)
----------------------------------------------------------------------
The source-of-truth schema defines scan-date regime features (vix_at_scan /
spy_trend_at_scan / vix_5d_delta_at_scan) and the momentum features (mom_60 +
audit dates) that REPLACE the leaking entry-close regime columns. Those columns
do NOT yet exist on the live table (they land with the must-fix #2 regime-scan-
date backfill and must-fix #5 mom_60 persist). They are enumerated in
`PENDING_FEATURE_ALLOWLIST` below but commented out of the active SELECT so this
view validates against the CURRENT live schema. Uncomment them (moving each into
`FEATURE_ALLOWLIST`) once the backfills have added the columns.

SAFETY / GATING
---------------
Read-only DDL that creates a VIEW (no data is copied or mutated). Still gated:
  - DRY-RUN by default: prints the DDL and validates the SELECT against the live
    table via a BigQuery dry-run (no bytes billed, nothing created).
  - Pass --execute to actually CREATE OR REPLACE the view.
REQUIRES gammarips-review before --execute. No deploy.

    # validate only (default):
    python scripts/ledger_and_tracking/create_enriched_features_view.py
    # create the view (after review):
    python scripts/ledger_and_tracking/create_enriched_features_view.py --execute
"""

import argparse
import sys

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
BASE_TABLE = "enriched_option_outcomes"
VIEW_ID = "enriched_features_v1"

BASE_REF = f"{PROJECT_ID}.{DATASET_ID}.{BASE_TABLE}"
VIEW_REF = f"{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}"

# ---------------------------------------------------------------------------
# EXPLICIT FEATURE / IDENTITY ALLOWLIST (the ONLY columns this view exposes).
# Allowlist, NOT denylist: new base-table columns are dropped until classified.
# Every name below is verified to exist on the live table as of 2026-07-01.
# ---------------------------------------------------------------------------

# IDENTITY / JOIN KEYS — known at selection; safe to expose for joins.
IDENTITY_ALLOWLIST = [
    "scan_date",              # <= scan_date  (the decision date)
    "entry_day",              # first trading day after scan_date (calendar key)
    "ticker",
    "direction",              # contract spec, fixed at selection
    "recommended_contract",
    "recommended_strike",
    "recommended_expiration",
    "recommended_dte",
]

# FEATURES — point-in-time, leakage-safe (as-of <= scan_date). Safe model inputs.
FEATURE_ALLOWLIST = [
    # 1,375-trade study levers:
    "recommended_delta",
    "risk_reward_ratio",
    "atr_normalized_move",
    "moneyness_pct",
    # Greeks + contract liquidity (scan-time):
    "recommended_gamma",
    "recommended_theta",
    "recommended_vega",
    "recommended_iv",
    "recommended_spread_pct",
    "recommended_volume",
    "recommended_oi",
    "volume_oi_ratio",
    "contract_score",
    # Flow (scan-time):
    "call_dollar_volume",
    "put_dollar_volume",
    # Scoring + grounding (scan-time):
    "overnight_score",
    "premium_score",
    "is_premium_signal",
    "catalyst_score",
    # Underlying technicals (scan-time, lookahead-guarded to scan_date):
    "underlying_price",
    "atr_14",
    "rsi_14",
    # Regime feature that is genuinely scan-time (enrichment computes it as-of
    # scan_date close of VXVCLS):
    "vix3m_at_enrich",
]

# COHORT / LINKAGE METADATA — describes the SELECTION cohort, not the outcome.
# Safe: lets an agent stratify by cohort without touching any realized value.
COHORT_META_ALLOWLIST = [
    "was_tournament_pick",
    "was_topscore_pick",
    "pool_size",
    "policy_version",
]

# PENDING FEATURES — defined in the source-of-truth schema but NOT yet on the
# live table (land with must-fix #2 regime-scan-date + must-fix #5 mom_60
# backfills). Move each into FEATURE_ALLOWLIST once the column exists. Leaving
# them here (and OUT of the active SELECT) keeps the view valid against the
# current live schema while documenting the intended additions.
PENDING_FEATURE_ALLOWLIST = [
    "mom_60",                 # <= scan_date (anchor + lookback both <= scan_date)
    "mom_anchor_date",
    "mom_lookback_date",
    "mom_lookback_days",
    "vix_at_scan",            # regime FEATURE, as-of scan_date close
    "spy_trend_at_scan",
    "vix_5d_delta_at_scan",
]

# Documented EXCLUSIONS (never exposed by this view). Not used by the SELECT —
# kept here so the leakage boundary is greppable and reviewable in one place.
# OUTCOME / LABEL / OPP / TELEMETRY per the source-of-truth grouping:
_EXCLUDED_OUTCOME = [
    # Realized same-day exit DATE. Classed IDENTITY in the source-of-truth schema
    # (a key) but its value is realized post-entry, so it is never exposed as a
    # feature. Already functionally excluded (absent from the allowlist); listed
    # here only so the greppable boundary is complete (#4 review, rec 1).
    "exit_day",
    "entry_timestamp", "entry_price", "target_price", "stop_price",
    "trail_trigger_price", "peak_premium", "trail_activated",
    "trail_stop_at_exit", "exit_timestamp", "exit_reason",
    "realized_return_pct", "exit_slippage", "illiquid_exit",
    "late_fill_minutes",
    # Benchmarking (source-of-truth files these under OUTCOME, not FEATURE):
    "iv_rank_entry", "iv_percentile_entry", "hv_20d_entry",
    "underlying_entry_price", "underlying_exit_price", "underlying_return",
    "spy_entry_price", "spy_exit_price", "spy_return_over_window",
    "labeled_at",
]
_EXCLUDED_TELEMETRY = [
    # Entry-day-close regime — realized AFTER the same-day trade closes.
    "oc_vix_at_close", "oc_spy_trend_at_close", "oc_vix_5d_delta_at_close",
    # LEGACY leaking entry-close regime (must-fix #2). On the live table today;
    # being re-homed to oc_*_at_close. NEVER a feature.
    "VIX_at_entry", "SPY_trend_state", "vix_5d_delta_entry",
]
_EXCLUDED_OPP = [
    "opp_window_days", "opp_status", "opp_entry_timestamp", "opp_entry_price",
    "opp_peak_return", "opp_trough_return", "opp_minutes_to_peak",
    "opp_minutes_to_trough", "opp_bar_count", "opp_sim_version",
]
_EXCLUDED_LABEL = [
    "realized_return_pct_3d", "exit_reason_3d", "exit_day_3d",
    "exit_timestamp_3d", "entry_price_3d", "peak_premium_3d",
    "label_sim_version", "label_hold_days", "label_stop_pct", "label_target_pct",
    "label_3d_sim_version", "label_3d_hold_days", "label_3d_stop_pct",
    "label_3d_target_pct",
]

ALLOWLIST = IDENTITY_ALLOWLIST + FEATURE_ALLOWLIST + COHORT_META_ALLOWLIST


def build_select_sql() -> str:
    cols = ",\n    ".join(ALLOWLIST)
    return f"SELECT\n    {cols}\nFROM `{BASE_REF}`"


def build_create_ddl() -> str:
    select_sql = build_select_sql()
    description = (
        "LEAKAGE-SAFE FEATURES-ONLY view over enriched_option_outcomes "
        "(substrate must-fix #4). Exposes ONLY point-in-time features (<= "
        "scan_date), identity/join keys, and cohort metadata. Excludes every "
        "outcome/label/opportunity/telemetry column. Agents/MCP/research MUST "
        "query this view for features; the raw table is for label joins only."
    )
    return (
        f"CREATE OR REPLACE VIEW `{VIEW_REF}`\n"
        f"OPTIONS(description=\"\"\"{description}\"\"\")\n"
        f"AS\n{select_sql}\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Actually CREATE OR REPLACE the view (default: dry-run validate only).",
    )
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT_ID)
    ddl = build_create_ddl()
    select_sql = build_select_sql()

    print("=" * 72)
    print(f"View: {VIEW_REF}")
    print(f"Allowlisted columns: {len(ALLOWLIST)} "
          f"({len(IDENTITY_ALLOWLIST)} identity + {len(FEATURE_ALLOWLIST)} feature "
          f"+ {len(COHORT_META_ALLOWLIST)} cohort-meta)")
    print(f"Pending (not yet on live table): {len(PENDING_FEATURE_ALLOWLIST)}")
    print("=" * 72)
    print(ddl)
    print("=" * 72)

    if not args.execute:
        # DRY-RUN: validate the SELECT against the live table without creating
        # anything and without billing bytes.
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = client.query(select_sql, job_config=job_config)
        print("DRY-RUN OK: SELECT validated against the live table.")
        print(f"  would process ~{job.total_bytes_processed:,} bytes (0 billed).")
        print("Re-run with --execute (after gammarips-review) to create the view.")
        return 0

    client.query(ddl).result()
    print(f"CREATED/REPLACED view: {VIEW_REF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
