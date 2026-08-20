"""Phase 0 data audit for the liquid-universe funnel study (READ-ONLY, 2026-08-20).

Spec: docs/EXEC-PLANS/2026-08-20-liquid-universe-funnel-spec.md (PRE-REGISTERED).
This run is the FIRST data pull for the study. After this run the spec is frozen.

WHAT THIS AUDITS (BigQuery SELECTs + GCS metadata and small universe-file
reads; no Polygon, no writes):
  A. The study window: 60 entry days ending 2026-08-14, scan dates = prior
     trading day, from the NYSE calendar (not from data presence).
  B. Universe as-of mapping: which universe file was live at each scan date
     (GCS universe-backups/ + live file), per the spec's nearest-earlier rule.
  C. Arm A composition per scan date (enriched_option_outcomes) + the known
     in-window composition-change timeline.
  D. Arm A minute-tape coverage (option_minute_paths join).
  E. VIX-rail skip days (vix_at_scan > vix3m_at_enrich) inside the window.
  F. Baseline-source audit of overnight_signals retention (spec erratum
     evidence: retention is ~2,000-2,500 names/day, not ~100-300).
  G. H-LU1 Arm A tradeability recompute: share of Arm A legs with 11+ real
     prints by 10:00 ET on entry day. Two denominator constructions are
     reported because the 15.8% reference (FINDINGS_LEDGER 2026-08-19) also
     required a closed V7.1 label; see tradeability().
  H. Study 2 (pool-benchmark spec 2026-08-19) prep inventory over its 87 scan
     dates, incl. the historical-OI / greeks feasibility evidence.

Run:
    .venv/bin/python backtesting_and_research/2026-08-20_liquid_universe_phase0_audit.py
"""

from __future__ import annotations

import datetime as dt

import db_dtypes  # noqa: F401  (registers BQ DATE dtype)
import pandas as pd
from google.cloud import bigquery, storage

# Hardcoded on purpose: the shell exports PROJECT_ID=profitscout-lx6bb.
PROJECT = "profitscout-fida8"
DATASET = "profit_scout"
BUCKET = "profit-scout-data"
BACKUP_PREFIX = "universe-backups/"
LIVE_UNIVERSE = "overnight-universe.txt"

LAST_ENTRY_DAY = dt.date(2026, 8, 14)
N_ENTRY_DAYS = 60

# NYSE full holidays 2026.
NYSE_HOLIDAYS_2026 = {
    dt.date(2026, 1, 1), dt.date(2026, 1, 19), dt.date(2026, 2, 16),
    dt.date(2026, 4, 3), dt.date(2026, 5, 25), dt.date(2026, 6, 19),
    dt.date(2026, 7, 3), dt.date(2026, 9, 7), dt.date(2026, 11, 26),
    dt.date(2026, 12, 25),
}

# Study 2 window (docs/EXEC-PLANS/2026-08-19-pool-benchmark-test-spec.md §3).
S2_FIRST_SCAN = dt.date(2026, 4, 10)
S2_LAST_SCAN = dt.date(2026, 8, 17)

# Known pool-composition changes inside/adjacent to the Study 1 scan window.
# Sources: docs/DECISIONS/ (per-row citation). Facts, not derived data.
COMPOSITION_TIMELINE = [
    ("2026-06-04", "V6: all per-candidate selection gates removed, LIMIT 10->200; "
                   "bracket tournament replaces judge_v6 (2026-06-04-bracket-tournament.md). "
                   "Same day: pipeline bug, NO pool rows for scan_date=2026-06-04."),
    ("2026-06-05", "Spread gate retired, recommended_spread_pct permanently NULL "
                   "(2026-06-05-engine-quote-outage-and-gate.md)."),
    ("2026-06-12", "ENRICH_TOP_N=50 BULLISH edge-rank cap created; before this there "
                   "was NO top-50 cap (2026-06-12-enrich-topN-thinking-cap.md)."),
    ("2026-06-19", "mom_60 tilt deployed; first tilted enrichment run 2026-06-22 05:30 ET; "
                   "scan_date=2026-06-18 is era-ambiguous (2026-06-19-momentum-60d-edge-tilt.md)."),
    ("2026-07-28", "LIQ_DEMOTION pool reordering + contract_score recalibration "
                   "(changes recommended_contract within ticker) "
                   "(2026-07-28-pool-tradeability-build.md)."),
    ("2026-08-05", "Universe refresh 5,230 -> 3,547 names at 19:46Z; explicit "
                   "pool-composition era boundary (2026-08-05-universe-weekly-refresh.md)."),
]

bq = bigquery.Client(project=PROJECT)


def q(sql: str) -> pd.DataFrame:
    return bq.query(sql).to_dataframe()


def is_trading_day(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in NYSE_HOLIDAYS_2026


def trading_days_back(last: dt.date, n: int) -> list[dt.date]:
    days, d = [], last
    while len(days) < n:
        if is_trading_day(d):
            days.append(d)
        d -= dt.timedelta(days=1)
    days.reverse()
    return days


# ------------------------------------------------------------------ A. window
def section_a() -> tuple[list[dt.date], list[dt.date]]:
    days = trading_days_back(LAST_ENTRY_DAY, N_ENTRY_DAYS + 1)
    entry_days = days[1:]
    scan_days = days[:-1]  # scan date = prior trading day of each entry day
    hols = sorted(h for h in NYSE_HOLIDAYS_2026
                  if scan_days[0] <= h <= entry_days[-1])
    print("A. STUDY WINDOW (from the NYSE calendar, not from data presence)")
    print(f"   entry days : {len(entry_days)}  {entry_days[0]} .. {entry_days[-1]}")
    print(f"   scan dates : {len(scan_days)}  {scan_days[0]} .. {scan_days[-1]}")
    print(f"   holidays inside: {', '.join(str(h) for h in hols)}")
    return entry_days, scan_days


# ------------------------------------------------------- B. universe as-of map
def section_b(scan_days: list[dt.date]) -> None:
    gcs = storage.Client(project=PROJECT)
    bucket = gcs.bucket(BUCKET)
    live = bucket.get_blob(LIVE_UNIVERSE)
    backups = sorted(gcs.list_blobs(BUCKET, prefix=BACKUP_PREFIX),
                     key=lambda b: b.name)

    # Filename date = the date the backed-up content went LIVE
    # (universe_refresh.py:214 names the backup after the replaced blob's
    # updated date). So content live at scan date d = the file with the
    # largest live-from date <= d.
    files = []
    for b in backups:
        live_from = dt.date.fromisoformat(b.name.split("overnight-universe-")[1][:10])
        n_lines = len(b.download_as_text().strip().splitlines())
        files.append((live_from, b.name, n_lines, b.time_created))
    live_from_live_file = live.updated.date()
    files.append((live_from_live_file, f"(live) {LIVE_UNIVERSE}",
                  len(live.download_as_text().strip().splitlines()), None))
    files.sort()

    print("\nB. UNIVERSE AS-OF MAPPING (GCS)")
    for live_from, name, n_lines, created in files:
        created_s = f"  replaced {created:%Y-%m-%dT%H:%MZ}" if created else "  (current)"
        print(f"   live from {live_from}: {name}  {n_lines} names{created_s}")

    rows = []
    for d in scan_days:
        eligible = [f for f in files if f[0] <= d]
        if not eligible:
            rows.append((d, "NO FILE", None, None))
            continue
        live_from, name, n_lines, _ = eligible[-1]
        rows.append((d, name, n_lines, (d - live_from).days))
    m = pd.DataFrame(rows, columns=["scan_date", "file", "names", "gap_days"])
    print("   scan-date -> file (ranges):")
    for name, g in m.groupby("file", sort=False):
        print(f"     {g.scan_date.min()} .. {g.scan_date.max()}  ({len(g)} dates)"
              f" -> {name}  ({g.names.iloc[0]} names, gap {g.gap_days.min()}-"
              f"{g.gap_days.max()}d)")
    unmapped = m[m.file == "NO FILE"]
    print(f"   scan dates with no as-of file: {len(unmapped)}")
    print("   NOTE: the 2026-02-13 file is EXACT (zero writes 02-13..08-05 19:46Z;"
          " the backup was cut from the live blob generation), so large gap_days"
          " = stale content the scanner truly saw, not an approximation.")
    print("   Edge case 2026-08-05: the 5,230->3,547 swap happened 19:46Z (15:46 ET),"
          " BEFORE the evening scan, so scan_date=2026-08-05 correctly maps to the"
          " new 3,547-name file.")


# --------------------------------------------------- C. Arm A composition
def section_c(scan_days: list[dt.date]) -> pd.DataFrame:
    lo, hi = scan_days[0], scan_days[-1]
    pool = q(f"""
        SELECT scan_date, COUNT(*) AS legs,
               COUNTIF(direction != 'BULLISH') AS non_bullish,
               COUNTIF(recommended_contract IS NULL) AS null_contract
        FROM `{PROJECT}.{DATASET}.enriched_option_outcomes`
        WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        GROUP BY scan_date ORDER BY scan_date
    """)
    pool["scan_date"] = pd.to_datetime(pool.scan_date).dt.date
    missing = [d for d in scan_days if d not in set(pool.scan_date)]
    over50 = pool[pool.legs > 50]
    print("\nC. ARM A COMPOSITION (enriched_option_outcomes)")
    print(f"   pool days: {len(pool)} of {len(scan_days)} scan dates"
          f" | total legs: {pool.legs.sum()}"
          f" | non-BULLISH rows: {pool.non_bullish.sum()}"
          f" | NULL contracts: {pool.null_contract.sum()}")
    print(f"   scan dates with NO pool rows: {', '.join(str(d) for d in missing) or 'none'}")
    print(f"   days over 50 legs: {len(over50)}"
          f" ({over50.scan_date.min()} .. {over50.scan_date.max()},"
          f" max {pool.legs.max()})" if len(over50) else "   days over 50 legs: 0")
    print(f"   per-day legs: min {pool.legs.min()} / median {pool.legs.median():.0f}"
          f" / max {pool.legs.max()}")
    print("   composition-change timeline inside the window (docs/DECISIONS/):")
    for date, desc in COMPOSITION_TIMELINE:
        print(f"     {date}: {desc}")
    return pool


# --------------------------------------------------- D. tape coverage
def section_d(scan_days: list[dt.date]) -> None:
    lo, hi = scan_days[0], scan_days[-1]
    cov = q(f"""
        WITH pool AS (
          SELECT scan_date, recommended_contract
          FROM `{PROJECT}.{DATASET}.enriched_option_outcomes`
          WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        ),
        tape AS (
          SELECT DISTINCT scan_date, contract
          FROM `{PROJECT}.{DATASET}.option_minute_paths`
          WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        )
        SELECT COUNT(*) AS legs,
               COUNTIF(t.contract IS NOT NULL) AS with_tape
        FROM pool p
        LEFT JOIN tape t
          ON t.scan_date = p.scan_date AND t.contract = p.recommended_contract
    """)
    legs, with_tape = int(cov.legs[0]), int(cov.with_tape[0])
    print("\nD. ARM A MINUTE-TAPE COVERAGE (option_minute_paths, join on"
          " scan_date + contract)")
    print(f"   legs {legs} | with tape {with_tape}"
          f" ({with_tape / legs * 100:.2f}%) | NO tape {legs - with_tape}"
          f" ({(legs - with_tape) / legs * 100:.2f}%)")
    print("   Spec rule: no-tape rows are counted and reported, never silently dropped.")


# --------------------------------------------------- E. VIX rail
def section_e(scan_days: list[dt.date]) -> None:
    lo, hi = scan_days[0], scan_days[-1]
    vix = q(f"""
        SELECT scan_date,
               ANY_VALUE(vix_at_scan) AS vix,
               ANY_VALUE(vix3m_at_enrich) AS vix3m,
               COUNT(DISTINCT vix_at_scan) AS n_vix,
               COUNT(DISTINCT vix3m_at_enrich) AS n_vix3m,
               COUNTIF(vix_at_scan IS NULL) > 0
                 AND COUNT(vix_at_scan) > 0 AS mixed_vix,
               COUNTIF(vix3m_at_enrich IS NULL) > 0
                 AND COUNT(vix3m_at_enrich) > 0 AS mixed_vix3m
        FROM `{PROJECT}.{DATASET}.enriched_option_outcomes`
        WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        GROUP BY scan_date ORDER BY scan_date
    """)
    assert (vix.n_vix <= 1).all() and (vix.n_vix3m <= 1).all(), \
        "intra-day VIX inconsistency: ANY_VALUE not safe"
    assert not vix.mixed_vix.any() and not vix.mixed_vix3m.any(), \
        "a scan_date mixes NULL and non-NULL VIX values: ANY_VALUE not safe"
    skip = vix[vix.vix > vix.vix3m]
    nulls = vix[vix.vix.isna() | vix.vix3m.isna()]
    print("\nE. VIX RAIL (vix_at_scan > vix3m_at_enrich => rail-skip day)")
    print(f"   dates with values: {len(vix)} | NULL either: {len(nulls)}")
    for _, r in skip.iterrows():
        print(f"   SKIP {r.scan_date}: VIX {r.vix:.2f} > VIX3M {r.vix3m:.2f}")
    print(f"   rail-skip days in window: {len(skip)}")
    print("   NOTE: pool rows EXIST on rail-skip days (the rail stands down the"
          " pick, not enrichment). Arms B and C must drop these days explicitly"
          " per the spec; Arm A treatment is reported, not decided, here.")


# --------------------------------------------------- F. baseline-source audit
def section_f(scan_days: list[dt.date]) -> None:
    lo, hi = scan_days[0], scan_days[-1]
    sig = q(f"""
        SELECT scan_date, COUNT(*) AS names,
               MIN(ABS(price_change_pct)) AS min_abs_move
        FROM `{PROJECT}.{DATASET}.overnight_signals`
        WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        GROUP BY scan_date ORDER BY scan_date
    """)
    print("\nF. BASELINE-SOURCE AUDIT (overnight_signals retention)")
    print(f"   dates: {len(sig)} | names/day: min {sig.names.min()}"
          f" / median {sig.names.median():.0f} / max {sig.names.max()}")
    print(f"   min |price_change_pct| across all days: {sig.min_abs_move.min():.2f}"
          " (the >=1%-move conditioning is real)")
    print("   SPEC ERRATUM EVIDENCE: the spec's Data-reality bullet says retention"
          " is '~100-300/day'. Actual is ~2,000-2,500/day (38-48% of the"
          " 5,230-name file live on 53 of 59 dates; ~65% of the 3,547-name"
          " file after 2026-08-05). The CONCLUSION stands: the series is"
          " conditioned on a >=1% move, so a trailing-UOA baseline built from"
          " it is activity-inflated and the baseline must come from Polygon.")


# --------------------------------------------------- G. H-LU1 Arm A recompute
def tradeability(lo: dt.date, hi: dt.date) -> dict[str, tuple[int, int]]:
    """Legs with 11+ real prints by 10:00 ET on entry day, TWO constructions.

    Numerator label is identical to 2026-08-19_selection_on_tradeable_subset
    .py::prints_by_1000: day_index=1 bars, ET minute-of-day <= 600, count >=
    11. Every stored bar is a real print (0 zero-volume / zero-transaction
    rows). The two constructions differ in the DENOMINATOR:
      - in_study: ALL pool legs with day-1 tape. This is the study's Arm A
        instrument (the spec computes on tape, with no label requirement).
      - parity_0819: adds the 08-19 substrate's closed-label filter
        (enriched_features_v1 join + realized_return_pct IS NOT NULL, its
        line 152). The 15.8% reference was computed on THIS construction, so
        only this one compares to it. Reads NULLness only, never the value.
    """
    out = {}
    for key, extra in [
        ("in_study", ""),
        ("parity_0819", f"""
          JOIN `{PROJECT}.{DATASET}.enriched_features_v1` f
            ON f.scan_date = o.scan_date
           AND f.recommended_contract = o.recommended_contract
          WHERE o.scan_date BETWEEN '{lo}' AND '{hi}'
            AND o.realized_return_pct IS NOT NULL"""),
    ]:
        where = extra or f"WHERE o.scan_date BETWEEN '{lo}' AND '{hi}'"
        t = q(f"""
            WITH pool AS (
              SELECT o.scan_date, o.recommended_contract
              FROM `{PROJECT}.{DATASET}.enriched_option_outcomes` o
              {where}
            ),
            prints AS (
              SELECT scan_date, contract,
                     COUNTIF(
                       EXTRACT(HOUR   FROM ts AT TIME ZONE 'America/New_York') * 60 +
                       EXTRACT(MINUTE FROM ts AT TIME ZONE 'America/New_York') <= 600
                     ) AS prints_by_1000
              FROM `{PROJECT}.{DATASET}.option_minute_paths`
              WHERE scan_date BETWEEN '{lo}' AND '{hi}' AND day_index = 1
              GROUP BY scan_date, contract
            )
            SELECT COUNT(*) AS legs_with_tape,
                   COUNTIF(pr.prints_by_1000 >= 11) AS tradeable
            FROM pool p
            JOIN prints pr
              ON pr.scan_date = p.scan_date
             AND pr.contract = p.recommended_contract
        """)
        out[key] = (int(t.legs_with_tape[0]), int(t.tradeable[0]))
    return out


def section_g(scan_days: list[dt.date]) -> None:
    win = tradeability(scan_days[0], scan_days[-1])
    ref = tradeability(S2_FIRST_SCAN, S2_LAST_SCAN)  # 87-day reference window
    print("\nG. H-LU1 ARM A TRADEABILITY RECOMPUTE (11+ real prints by 10:00 ET,"
          " entry day)")
    for key, label in [("in_study", "in-study (all tape-joined legs)  "),
                       ("parity_0819", "08-19 parity (closed-label filter)")]:
        (n_w, k_w), (n_r, k_r) = win[key], ref[key]
        print(f"   {label}: window {k_w}/{n_w} = {k_w / n_w * 100:.1f}%"
              f" | 87-day 2026-04-10..08-17 {k_r}/{n_r} = {k_r / n_r * 100:.1f}%")
    print("   The 15.8% FINDINGS_LEDGER reference is the 87-day PARITY"
          " construction; the parity 87-day cell above must reproduce it.")
    print("   The study's Arm A instrument is the IN-STUDY construction"
          " (no label requirement); compare Arm B's 80% pass mark to nothing"
          " here - it is Arm B's own bar.")
    print("   62.6% = PRINT_FLOOR_MIN=25 notifier-slate replay projection,"
          " snapshot instrument; that floor never ran live inside this window"
          " (deployed 2026-08-20, first cohort entry 2026-08-21).")


# --------------------------------------------------- H. Study 2 prep inventory
def section_h() -> None:
    lo, hi = S2_FIRST_SCAN, S2_LAST_SCAN
    inv = q(f"""
        WITH pool AS (
          SELECT scan_date, recommended_contract
          FROM `{PROJECT}.{DATASET}.enriched_option_outcomes`
          WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        ),
        tape AS (
          SELECT DISTINCT scan_date, contract
          FROM `{PROJECT}.{DATASET}.option_minute_paths`
          WHERE scan_date BETWEEN '{lo}' AND '{hi}'
        )
        SELECT COUNT(DISTINCT p.scan_date) AS days, COUNT(*) AS legs,
               COUNTIF(t.contract IS NOT NULL) AS with_tape
        FROM pool p
        LEFT JOIN tape t
          ON t.scan_date = p.scan_date AND t.contract = p.recommended_contract
    """)
    prof = q(f"""
        SELECT COUNT(*) AS pool_rows,
               COUNTIF(s.day_volume IS NULL) AS null_day_volume,
               COUNTIF(s.sector IS NULL OR s.sector = '') AS null_sector
        FROM `{PROJECT}.{DATASET}.enriched_option_outcomes` o
        LEFT JOIN `{PROJECT}.{DATASET}.overnight_signals` s
          ON s.scan_date = o.scan_date AND s.ticker = o.ticker
        WHERE o.scan_date BETWEEN '{lo}' AND '{hi}'
    """)
    oi = q(f"""
        SELECT MIN(scan_date) AS first_scan, COUNT(DISTINCT scan_date) AS days,
               COUNT(DISTINCT contract) AS contracts
        FROM `{PROJECT}.{DATASET}.pool_liquidity_snapshot`
    """)
    print("\nH. STUDY 2 (pool-benchmark) PREP INVENTORY, scan window"
          f" {lo}..{hi}")
    print(f"   Arm A: {int(inv.days[0])} pool days, {int(inv.legs[0])} legs,"
          f" tape on {int(inv.with_tape[0])}"
          f" ({int(inv.with_tape[0]) / int(inv.legs[0]) * 100:.1f}%)")
    print(f"   Matching inputs on pool rows (join to overnight_signals):"
          f" day_volume NULL {int(prof.null_day_volume[0])}/{int(prof.pool_rows[0])},"
          f" sector NULL {int(prof.null_sector[0])}/{int(prof.pool_rows[0])}")
    print("   FEASIBILITY EVIDENCE (matching bar / contract selection):")
    print(f"     pool_liquidity_snapshot: first scan_date {oi.first_scan[0]},"
          f" {int(oi.days[0])} days, {int(oi.contracts[0])} contracts"
          " - POOL CONTRACTS ONLY, starts 2026-07-06. No historical OI exists"
          " for control names on any study date (Polygon OI is current-state"
          " snapshot only).")
    print("     => Arm B's 'oi >= 1200' bar and _best_contract's OI/greeks/quote"
          " inputs are NOT reconstructible for controls. Pre-data amendment"
          " needed (owner call); evidence recorded here, decision NOT taken"
          " by this audit.")
    print("   AMENDMENT SEQUENCING: this inventory pulled no outcome and no"
          " matching result for the sibling study - counts and NULL rates"
          " only - and the infeasibility evidence is code-level fact. The"
          " sibling amendment is therefore not result-informed; its dated"
          " note must state this sequencing explicitly.")
    print("     Control-name day_volume coverage: overnight_signals retains only"
          " >=1%-movers (~2,000-2,500 names/day), so full-universe underlying"
          " volume needs the Polygon grouped-daily pull (shared with Study 1).")


def main() -> None:
    print("=" * 78)
    print("PHASE 0 DATA AUDIT - liquid-universe funnel study (read-only)")
    print(f"project {PROJECT} | run date {dt.date.today()}")
    print("=" * 78)
    entry_days, scan_days = section_a()
    section_b(scan_days)
    section_c(scan_days)
    section_d(scan_days)
    section_e(scan_days)
    section_f(scan_days)
    section_g(scan_days)
    section_h()
    print("\nDONE. This audit pulled data: the 2026-08-20 spec is now FROZEN.")


if __name__ == "__main__":
    main()
