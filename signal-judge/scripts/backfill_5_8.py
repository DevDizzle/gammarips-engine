"""One-off backfill: re-run V5.4 ranker for scan_date=2026-05-07 with v4/v3
prompts and proper ITM exclusion.

Why this exists: the 2026-05-07 enriched rows were written before the
moneyness sign-bug fix (2026-05-09), so `moneyness_pct` is stored as abs().
The smoke_test's `BETWEEN 0.05 AND 0.15` filter passes both ITM and OTM. To
get a clean V5.4 backfill on the corrected gate semantics, we use the raw
strike-vs-underlying check directly here.

After Monday 2026-05-11 23:00 ET (next scanner run with the fix), all new
enriched rows have signed moneyness and the standard smoke_test query is
fine. This script can be archived.

Usage:
    PROJECT_ID=profitscout-fida8 python signal-ranker/scripts/backfill_5_8.py \
        --url https://signal-ranker-hrhjaecvhq-uc.a.run.app
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta

import requests
from google.cloud import bigquery, firestore

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")
SCAN_DATE = "2026-05-07"


def fetch_candidates_otm_only(bq: bigquery.Client, top_n: int = 10) -> list[dict]:
    """Pull top-N gate-clean candidates EXCLUDING ITM contracts.

    ITM filter: strike must be on the OTM side of underlying_price for the
    trade direction (BULLISH call → strike > spot; BEARISH put → strike < spot).
    Distance band: 5-15% from the money (matches V5.4 gate intent).
    """
    sql = f"""
    SELECT
        ticker, direction, overnight_score,
        call_dollar_volume, put_dollar_volume,
        call_vol_oi_ratio, put_vol_oi_ratio,
        volume_oi_ratio,
        recommended_contract, recommended_strike,
        CAST(recommended_expiration AS STRING) AS recommended_expiration,
        recommended_dte, recommended_mid_price, recommended_spread_pct,
        moneyness_pct, vix3m_at_enrich, underlying_price,
        catalyst_score, catalyst_type,
        flow_intent, flow_intent_reasoning,
        thesis, news_summary, key_headline,
        mean_reversion_risk, move_overdone, reversal_probability,
        risk_reward_ratio,
        ROW_NUMBER() OVER (
            ORDER BY
                CASE WHEN direction='BULLISH' THEN call_vol_oi_ratio ELSE put_vol_oi_ratio END DESC,
                recommended_spread_pct ASC,
                overnight_score DESC,
                ticker ASC
        ) AS static_rank
    FROM `{PROJECT_ID}.{DATASET}.overnight_signals_enriched`
    WHERE scan_date = '{SCAN_DATE}'
      AND volume_oi_ratio > 2
      AND underlying_price > 0
      AND recommended_strike IS NOT NULL
      AND (
        (direction = 'BULLISH' AND recommended_strike > underlying_price
         AND (recommended_strike - underlying_price) / underlying_price BETWEEN 0.05 AND 0.15)
        OR
        (direction = 'BEARISH' AND recommended_strike < underlying_price
         AND (underlying_price - recommended_strike) / underlying_price BETWEEN 0.05 AND 0.15)
      )
    QUALIFY static_rank <= {top_n}
    ORDER BY static_rank
    """
    rows = [dict(r) for r in bq.query(sql).result()]
    # Replace abs moneyness with signed value so the v4 Scorer's ITM hard cap
    # works correctly even on the pre-fix data we're feeding here.
    for r in rows:
        if r.get("direction") == "BULLISH":
            r["moneyness_pct"] = round((r["recommended_strike"] - r["underlying_price"]) / r["underlying_price"], 4)
        else:
            r["moneyness_pct"] = round((r["underlying_price"] - r["recommended_strike"]) / r["underlying_price"], 4)
    return rows


def fetch_report_md(fs: firestore.Client) -> str:
    doc = fs.collection("daily_reports").document(SCAN_DATE).get()
    if not doc.exists:
        return ""
    d = doc.to_dict() or {}
    parts = []
    if d.get("title"):
        parts.append(f"# {d['title']}")
    if d.get("headline"):
        parts.append(d["headline"])
    if d.get("content"):
        parts.append(d["content"])
    return "\n\n".join(parts)


def fetch_ledger_summary(bq: bigquery.Client) -> dict:
    target = datetime.strptime(SCAN_DATE, "%Y-%m-%d").date()
    start = target - timedelta(days=14)
    sql = f"""
    SELECT policy_version, direction,
           COUNT(*) AS n,
           COUNTIF(realized_return_pct > 0) AS wins,
           COUNTIF(realized_return_pct < 0) AS losses
    FROM `{PROJECT_ID}.{DATASET}.forward_paper_ledger`
    WHERE scan_date >= '{start.isoformat()}'
      AND scan_date < '{target.isoformat()}'
      AND COALESCE(is_skipped, FALSE) = FALSE
      AND realized_return_pct IS NOT NULL
    GROUP BY policy_version, direction
    """
    by_direction: dict = {}
    by_policy: dict = {}
    total = 0
    for r in bq.query(sql).result():
        d = dict(r)
        total += int(d["n"])
        by_direction.setdefault(d["direction"], {"n": 0, "wins": 0, "losses": 0})
        by_direction[d["direction"]]["n"] += int(d["n"])
        by_direction[d["direction"]]["wins"] += int(d["wins"])
        by_direction[d["direction"]]["losses"] += int(d["losses"])
        by_policy.setdefault(d["policy_version"], {"n": 0, "wins": 0, "losses": 0})
        by_policy[d["policy_version"]]["n"] += int(d["n"])
        by_policy[d["policy_version"]]["wins"] += int(d["wins"])
        by_policy[d["policy_version"]]["losses"] += int(d["losses"])
    return {
        "window_days": 14,
        "closed_trades": total,
        "by_direction": by_direction,
        "by_policy": by_policy,
        "notes": f"{total} closed trades in last 14d. By direction: {by_direction}. By policy: {by_policy}.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--top-n", type=int, default=10)
    args = ap.parse_args()

    bq = bigquery.Client(project=PROJECT_ID)
    fs = firestore.Client(project=PROJECT_ID)

    raw = fetch_candidates_otm_only(bq, top_n=args.top_n)
    print(f"Fetched {len(raw)} OTM-only candidates for {SCAN_DATE}")
    for r in raw:
        print(f"  {r['ticker']:6s} {r['direction']:8s} strike={r['recommended_strike']:.1f} spot={r['underlying_price']:.2f} signed_moneyness={r['moneyness_pct']:.4f} vol_oi={r['volume_oi_ratio']:.2f}")

    candidates = []
    for r in raw:
        c = {k: v for k, v in r.items() if v is not None}
        c["static_rank"] = r["static_rank"]
        candidates.append(c)

    report_md = fetch_report_md(fs)
    print(f"\nFetched report_md ({len(report_md)} chars)")
    ledger_summary = fetch_ledger_summary(bq)
    print(f"Fetched ledger: {ledger_summary['notes']}")

    target = datetime.strptime(SCAN_DATE, "%Y-%m-%d").date()
    entry_day = (target + timedelta(days=1)).isoformat()

    payload = {
        "scan_date": SCAN_DATE,
        "entry_day": entry_day,
        "candidates": candidates,
        "report_md": report_md,
        "ledger_summary": ledger_summary,
    }

    if not shutil.which("gcloud"):
        print("gcloud not found; required for ID token", file=sys.stderr)
        return 1
    id_token = subprocess.run(
        ["gcloud", "auth", "print-identity-token"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()

    print(f"\n--- POST {args.url}/rank (v4 scorer + v3 picker, OTM-only candidates) ---")
    resp = requests.post(
        f"{args.url}/rank",
        json=json.loads(json.dumps(payload, default=str)),
        headers={"Authorization": f"Bearer {id_token}"},
        timeout=300,
    )
    print(f"status: {resp.status_code}")
    if not resp.ok:
        print(resp.text)
        return 1
    body = resp.json()
    print(f"\nPICK: {body.get('pick')}")
    print(f"RUNNER_UP: {body.get('runner_up')}")
    print(f"CONFIDENCE: {body.get('confidence')}")
    print(f"TOP_5: {body.get('top_5_tickers')}")
    print(f"RUN_ID: {body.get('run_id')}")
    print(f"DRY_RUN: {body.get('dry_run')}")
    print(f"SCORER_PROMPT_VERSION: {body.get('scorer_prompt_version')}")
    print(f"PICKER_PROMPT_VERSION: {body.get('picker_prompt_version')}")
    print(f"\nJUSTIFICATION: {body.get('justification')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
