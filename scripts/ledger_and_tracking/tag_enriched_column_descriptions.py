"""Tag every `enriched_option_outcomes` column with a machine-readable
classification (substrate must-fix #4).

WHY THIS EXISTS
---------------
The feature/label boundary lives in a Python docstring and a Markdown contract
today — a headless agent can't read those. This script writes the classification
into the BigQuery COLUMN DESCRIPTIONS so it is queryable from
`INFORMATION_SCHEMA.COLUMN_FIELD_PATHS` / the table metadata. An agent (or the
MCP) can then programmatically filter to `[feature ...]`-tagged columns and
physically refuse to touch anything tagged `[label ...]` / `[opportunity ...]` /
`[regime_telemetry ...]`.

Each description is prefixed with one classification token:
    feature | label | opportunity | regime_telemetry | identity
plus an as-of BOUNDARY for the point-in-time contract:
    "<= scan_date"        — known at the selection point (safe feature)
    "<= 10:00 ET entry"   — known at entry (realized-context, NOT a feature)
    "realized post-entry" — an outcome; never a feature
    "n/a"                 — metadata / key

PREFIX CONVENTION (encoded in the descriptions, adopt going forward):
    label_*  -> a label-semantics tag (the exact HOLD/STOP/TARGET behind a label)
    oc_*     -> entry-CLOSE regime telemetry (realized after the same-day trade)
    opp_*    -> opportunity-surface excursion (exit-free MFE/MAE; NOT a label)

Source of truth for names/groups:
`scripts/ledger_and_tracking/create_enriched_option_outcomes.py`.

TRANSITION NOTE
---------------
CLASSIFICATION below covers the FULL source-of-truth schema, including columns
not yet on the live table (mom_*, vix_at_scan/*, oc_*, opp_*, *_3d, label_*).
The script only tags columns that ACTUALLY EXIST on the live table; source-of-
truth columns not yet present are reported as "pending" and get tagged
automatically on a later re-run once the backfills add them. Live columns with
no CLASSIFICATION entry are reported as "UNCLASSIFIED" and left untouched (fail
loud, not silent).

SAFETY / GATING
---------------
Mutates only table METADATA (column descriptions) — no rows are read or written.
Still gated:
  - DRY-RUN by default: prints the full tagging plan, does NOT call update_table.
  - Pass --execute to write the descriptions.
REQUIRES gammarips-review before --execute. No deploy.

    python scripts/ledger_and_tracking/tag_enriched_column_descriptions.py
    python scripts/ledger_and_tracking/tag_enriched_column_descriptions.py --execute
"""

import argparse
import sys

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "enriched_option_outcomes"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# (tag, as_of_boundary, human description). Tags are the fixed 5-token vocab.
CLASSIFICATION = {
    # ---- IDENTITY / KEYS ----------------------------------------------------
    "scan_date":              ("identity", "<= scan_date", "Selection/decision date. Join key + point-in-time boundary."),
    "entry_day":              ("identity", "n/a", "First trading day after scan_date (partition key)."),
    "exit_day":               ("identity", "realized post-entry", "Realized same-day exit date. Key, but realized."),
    "ticker":                 ("identity", "<= scan_date", "Underlying symbol (cluster key)."),
    "direction":              ("identity", "<= scan_date", "Contract direction fixed at selection (BULLISH/BEARISH)."),
    "recommended_contract":   ("identity", "<= scan_date", "Selected OCC option symbol. Join key."),
    "recommended_strike":     ("identity", "<= scan_date", "Selected strike (contract spec)."),
    "recommended_expiration": ("identity", "<= scan_date", "Selected expiration (contract spec)."),
    "recommended_dte":        ("identity", "<= scan_date", "Days-to-expiration at selection (contract spec)."),

    # ---- FEATURES (point-in-time, safe as model inputs) ---------------------
    "recommended_delta":      ("feature", "<= scan_date", "Option delta at selection (1,375-trade study lever)."),
    "risk_reward_ratio":      ("feature", "<= scan_date", "Setup risk/reward at selection (study lever)."),
    "atr_normalized_move":    ("feature", "<= scan_date", "ATR-normalized expected move (study lever)."),
    "moneyness_pct":          ("feature", "<= scan_date", "|strike-underlying|/underlying at selection."),
    "recommended_gamma":      ("feature", "<= scan_date", "Option gamma at selection."),
    "recommended_theta":      ("feature", "<= scan_date", "Option theta at selection."),
    "recommended_vega":       ("feature", "<= scan_date", "Option vega at selection."),
    "recommended_iv":         ("feature", "<= scan_date", "Contract implied vol at selection."),
    "recommended_spread_pct": ("feature", "<= scan_date", "Real quoted bid/ask spread at scan (NULL if unquoted)."),
    "recommended_volume":     ("feature", "<= scan_date", "Session-frozen contract volume snapshot at scan."),
    "recommended_oi":         ("feature", "<= scan_date", "Prior-session open interest snapshot at scan."),
    "volume_oi_ratio":        ("feature", "<= scan_date", "recommended_volume / recommended_oi at scan."),
    "contract_score":         ("feature", "<= scan_date", "Contract-selection score at scan."),
    "call_dollar_volume":     ("feature", "<= scan_date", "Call-side dollar volume (flow) at scan."),
    "put_dollar_volume":      ("feature", "<= scan_date", "Put-side dollar volume (flow) at scan."),
    "overnight_score":        ("feature", "<= scan_date", "Overnight conviction score at scan."),
    "premium_score":          ("feature", "<= scan_date", "Deterministic premium-flag count at scan."),
    "is_premium_signal":      ("feature", "<= scan_date", "Premium-signal boolean at scan."),
    "catalyst_score":         ("feature", "<= scan_date", "Catalyst score; computed at the enrichment run (evening of scan_date) — as-of <= scan_date, strictly before the entry-day trade."),
    "underlying_price":       ("feature", "<= scan_date", "Underlying price at scan."),
    "atr_14":                 ("feature", "<= scan_date", "14-period ATR (lookahead-guarded to scan_date)."),
    "rsi_14":                 ("feature", "<= scan_date", "14-period RSI (lookahead-guarded to scan_date)."),
    "vix3m_at_enrich":        ("feature", "<= scan_date", "VXVCLS close at/<= scan_date (regime feature)."),
    # Regime FEATURES anchored as-of scan_date close (must-fix #2; land later):
    "vix_at_scan":            ("feature", "<= scan_date", "VIX close as-of scan_date (safe regime feature)."),
    "spy_trend_at_scan":      ("feature", "<= scan_date", "SPY trend state as-of scan_date close."),
    "vix_5d_delta_at_scan":   ("feature", "<= scan_date", "VIX 5-day delta as-of scan_date."),
    # Momentum FEATURE (must-fix #5; lands later). Anchor+lookback <= scan_date:
    "mom_60":                 ("feature", "<= scan_date", "60-day underlying momentum (flagship lever); PIT-guarded."),
    "mom_anchor_date":        ("feature", "<= scan_date", "mom_60 anchor date (<= scan_date; reproducibility)."),
    "mom_lookback_date":      ("feature", "<= scan_date", "mom_60 lookback date (<= scan_date; reproducibility)."),
    "mom_lookback_days":      ("feature", "<= scan_date", "mom_60 lookback horizon in trading days."),

    # ---- LABELS (realized same-day outcome — NEVER a feature) ---------------
    "entry_timestamp":        ("label", "realized post-entry", "Realized entry fill time."),
    "entry_price":            ("label", "realized post-entry", "Realized entry fill price."),
    "target_price":           ("label", "realized post-entry", "+80% target price (label mechanics)."),
    "stop_price":             ("label", "realized post-entry", "-60% stop price (label mechanics)."),
    "trail_trigger_price":    ("label", "realized post-entry", "Trail-activation price (label mechanics)."),
    "peak_premium":           ("label", "realized post-entry", "Peak option premium over the same-day hold."),
    "trail_activated":        ("label", "realized post-entry", "Whether the trailing stop armed."),
    "trail_stop_at_exit":     ("label", "realized post-entry", "Trailing-stop level at exit."),
    "exit_timestamp":         ("label", "realized post-entry", "Realized exit time."),
    "exit_reason":            ("label", "realized post-entry", "TARGET/STOP/TRAIL/TIMEOUT/STALE_NO_TIMEOUT_PRINT."),
    "realized_return_pct":    ("label", "realized post-entry", "CANONICAL same-day option-PnL label."),
    "exit_slippage":          ("label", "realized post-entry", "Modeled exit slippage (fill realism)."),
    "illiquid_exit":          ("label", "realized post-entry", "Exit reconstructed from illiquid book; exclude from EV."),
    "late_fill_minutes":      ("label", "realized post-entry", "Minutes between intended and actual exit bar."),
    # Benchmarking (realized-context; source-of-truth groups under OUTCOME):
    "iv_rank_entry":          ("label", "<= 10:00 ET entry", "IV rank at entry (benchmark/realized-context; not a feature)."),
    "iv_percentile_entry":    ("label", "<= 10:00 ET entry", "IV percentile at entry (benchmark; not a feature)."),
    "hv_20d_entry":           ("label", "<= 10:00 ET entry", "20d realized vol at entry (benchmark; not a feature)."),
    "underlying_entry_price": ("label", "realized post-entry", "Underlying price at entry (benchmark)."),
    "underlying_exit_price":  ("label", "realized post-entry", "Underlying price at exit (benchmark)."),
    "underlying_return":      ("label", "realized post-entry", "Signed underlying return over the window (benchmark)."),
    "spy_entry_price":        ("label", "realized post-entry", "SPY price at entry (benchmark noise floor)."),
    "spy_exit_price":         ("label", "realized post-entry", "SPY price at exit (benchmark)."),
    "spy_return_over_window": ("label", "realized post-entry", "SPY return over the window (benchmark noise floor)."),

    # ---- REGIME TELEMETRY (realized after the same-day trade) ---------------
    "oc_vix_at_close":        ("regime_telemetry", "realized post-entry", "oc_ prefix: entry-day-CLOSE VIX. Telemetry, not a feature."),
    "oc_spy_trend_at_close":  ("regime_telemetry", "realized post-entry", "oc_ prefix: entry-day-CLOSE SPY trend. Telemetry."),
    "oc_vix_5d_delta_at_close": ("regime_telemetry", "realized post-entry", "oc_ prefix: entry-day-CLOSE VIX 5d delta. Telemetry."),
    # LEGACY leaking entry-close regime (must-fix #2; being re-homed to oc_*):
    "VIX_at_entry":           ("regime_telemetry", "realized post-entry", "LEGACY LEAK: entry-CLOSE VIX. NOT a feature (must-fix #2)."),
    "SPY_trend_state":        ("regime_telemetry", "realized post-entry", "LEGACY LEAK: entry-CLOSE SPY trend. NOT a feature (must-fix #2)."),
    "vix_5d_delta_entry":     ("regime_telemetry", "realized post-entry", "LEGACY LEAK: entry-CLOSE VIX 5d delta. NOT a feature (must-fix #2)."),

    # ---- OPPORTUNITY SURFACE (exit-free MFE/MAE — NOT a label, NOT a feature)
    "opp_window_days":        ("opportunity", "realized post-entry", "opp_ prefix: excursion window length."),
    "opp_status":             ("opportunity", "realized post-entry", "opp_ prefix: excursion computation status."),
    "opp_entry_timestamp":    ("opportunity", "realized post-entry", "opp_ prefix: excursion entry stamp."),
    "opp_entry_price":        ("opportunity", "realized post-entry", "opp_ prefix: excursion entry price."),
    "opp_peak_return":        ("opportunity", "realized post-entry", "opp_ prefix: max FAVORABLE excursion (MFE). Exit-free."),
    "opp_trough_return":      ("opportunity", "realized post-entry", "opp_ prefix: max ADVERSE excursion (MAE). Exit-free."),
    "opp_minutes_to_peak":    ("opportunity", "realized post-entry", "opp_ prefix: minutes to MFE."),
    "opp_minutes_to_trough":  ("opportunity", "realized post-entry", "opp_ prefix: minutes to MAE."),
    "opp_bar_count":          ("opportunity", "realized post-entry", "opp_ prefix: bars in the excursion window."),
    "opp_sim_version":        ("opportunity", "n/a", "opp_ prefix: opportunity-surface sim version tag."),

    # ---- 3-DAY BRACKET LABEL (own horizon — NEVER mix with same-day) --------
    "realized_return_pct_3d": ("label", "realized post-entry", "3-day -60/+80/HOLD=3 bracket PnL. Distinct horizon."),
    "exit_reason_3d":         ("label", "realized post-entry", "3-day bracket exit reason."),
    "exit_day_3d":            ("label", "realized post-entry", "3-day bracket exit date."),
    "exit_timestamp_3d":      ("label", "realized post-entry", "3-day bracket exit time."),
    "entry_price_3d":         ("label", "realized post-entry", "3-day bracket entry price."),
    "peak_premium_3d":        ("label", "realized post-entry", "3-day bracket peak premium."),

    # ---- LABEL-SEMANTICS TAGS (the mechanics behind each label group) -------
    "label_sim_version":      ("label", "n/a", "label_ prefix: same-day simulator version tag."),
    "label_hold_days":        ("label", "n/a", "label_ prefix: same-day hold days."),
    "label_stop_pct":         ("label", "n/a", "label_ prefix: same-day stop %."),
    "label_target_pct":       ("label", "n/a", "label_ prefix: same-day target %."),
    "label_3d_sim_version":   ("label", "n/a", "label_ prefix: 3-day simulator version tag."),
    "label_3d_hold_days":     ("label", "n/a", "label_ prefix: 3-day hold days."),
    "label_3d_stop_pct":      ("label", "n/a", "label_ prefix: 3-day stop %."),
    "label_3d_target_pct":    ("label", "n/a", "label_ prefix: 3-day target %."),

    # ---- LINKAGE / COHORT META ---------------------------------------------
    "was_tournament_pick":    ("identity", "<= scan_date", "Cohort meta: was this row the live tournament pick."),
    "was_topscore_pick":      ("identity", "<= scan_date", "Cohort meta: was this row the top-score pick."),
    "pool_size":              ("identity", "<= scan_date", "Cohort meta: enriched-pool size for the scan_date."),
    "policy_version":         ("identity", "n/a", "Cohort meta: policy version label."),
    "labeled_at":             ("identity", "realized post-entry", "Outcome-write timestamp (row provenance)."),
}


def render_description(col: str) -> str:
    tag, boundary, desc = CLASSIFICATION[col]
    return f"[{tag} | as-of {boundary}] {desc}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Actually write the column descriptions (default: dry-run plan only).",
    )
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT_ID)
    table = client.get_table(TABLE_REF)

    live_cols = {f.name for f in table.schema}
    classified = set(CLASSIFICATION)

    to_tag = [f.name for f in table.schema if f.name in CLASSIFICATION]
    unclassified = sorted(live_cols - classified)   # on live, not in our map
    pending = sorted(classified - live_cols)         # in our map, not yet on live

    print("=" * 72)
    print(f"Table: {TABLE_REF}")
    print(f"Live columns: {len(live_cols)} | classified live: {len(to_tag)} | "
          f"unclassified live: {len(unclassified)} | pending (not yet live): {len(pending)}")
    print("=" * 72)
    print("TAGGING PLAN (live columns):")
    for name in to_tag:
        print(f"  {name:28s} -> {render_description(name)}")
    if unclassified:
        print("-" * 72)
        print("UNCLASSIFIED live columns (LEFT UNTOUCHED — add to CLASSIFICATION):")
        for name in unclassified:
            print(f"  {name}")
    if pending:
        print("-" * 72)
        print("PENDING (in CLASSIFICATION, not yet on live table — tagged on re-run):")
        for name in pending:
            print(f"  {name}")
    print("=" * 72)

    if not args.execute:
        print("DRY-RUN: no descriptions written. Re-run with --execute (after "
              "gammarips-review) to apply.")
        return 0

    new_schema = []
    for f in table.schema:
        if f.name in CLASSIFICATION:
            new_schema.append(
                bigquery.SchemaField(
                    f.name,
                    f.field_type,
                    mode=f.mode,
                    description=render_description(f.name),
                    fields=f.fields,
                )
            )
        else:
            new_schema.append(f)

    table.schema = new_schema
    client.update_table(table, ["schema"])
    print(f"WROTE descriptions for {len(to_tag)} columns on {TABLE_REF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
