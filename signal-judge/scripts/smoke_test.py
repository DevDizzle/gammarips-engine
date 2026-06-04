"""Smoke test for signal-ranker /rank.

Pulls real enriched candidates + daily report + 14d ledger summary from BQ +
Firestore for a given scan_date, builds a RankRequest, POSTs to /rank,
pretty-prints the response.

Phase 3 (signal-notifier wiring) will replicate this fetch logic; this script
is the throwaway scaffold that lets us exercise /rank end-to-end before the
full Phase 3 integration.

Usage:
    PROJECT_ID=profitscout-fida8 python signal-ranker/scripts/smoke_test.py \
        --scan-date 2026-05-07 \
        --url https://signal-ranker-<hash>-uc.a.run.app
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

import shutil
import subprocess

import requests
from google.cloud import bigquery, firestore

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")


def fetch_candidates(bq: bigquery.Client, scan_date: str, top_n: int = 10) -> list[dict]:
    """Pull top-N gate-clean candidates for a scan_date.

    Mirrors the V5.3 SQL ranker order so candidate_rank_static is meaningful.
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
        moneyness_pct, vix3m_at_enrich,
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
    WHERE scan_date = '{scan_date}'
      AND volume_oi_ratio > 2
      AND moneyness_pct BETWEEN 0.05 AND 0.15
    QUALIFY static_rank <= {top_n}
    ORDER BY static_rank
    """
    return [dict(r) for r in bq.query(sql).result()]


def fetch_report_md(fs: firestore.Client, scan_date: str) -> str:
    """Pull today's overnight report markdown from Firestore."""
    doc = fs.collection("daily_reports").document(scan_date).get()
    if not doc.exists:
        return f"(no daily_reports/{scan_date} doc)"
    data = doc.to_dict() or {}
    parts = []
    if data.get("title"):
        parts.append(f"# {data['title']}")
    if data.get("headline"):
        parts.append(data["headline"])
    if data.get("content"):
        parts.append(data["content"])
    return "\n\n".join(parts) or f"(empty daily_reports/{scan_date} doc)"


def fetch_ledger_summary(bq: bigquery.Client, scan_date: str, window_days: int = 14) -> dict:
    """Compute 14d ledger summary by direction and policy_version.

    forward_paper_ledger uses `scan_date` for entry-side bookkeeping (no
    separate entry_day column); WIN/LOSS is derived from realized_return_pct
    (NULL = still open). Skipped rows excluded.
    """
    target = datetime.strptime(scan_date, "%Y-%m-%d").date()
    start = target - timedelta(days=window_days)
    sql = f"""
    SELECT
        policy_version, direction,
        COUNT(*) as n,
        COUNTIF(realized_return_pct > 0) as wins,
        COUNTIF(realized_return_pct < 0) as losses,
        ROUND(AVG(realized_return_pct), 4) as avg_pct
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
    notes = (
        f"{total} closed trades in last {window_days}d. "
        f"By direction: {by_direction}. By policy: {by_policy}."
    )
    return {
        "window_days": window_days,
        "closed_trades": total,
        "by_direction": by_direction,
        "by_policy": by_policy,
        "notes": notes,
    }


def build_rank_request(scan_date: str, top_n: int = 10) -> dict:
    bq = bigquery.Client(project=PROJECT_ID)
    fs = firestore.Client(project=PROJECT_ID)

    raw_candidates = fetch_candidates(bq, scan_date, top_n=top_n)
    if not raw_candidates:
        raise SystemExit(f"No gate-clean candidates for scan_date={scan_date}")
    print(f"Fetched {len(raw_candidates)} candidates for {scan_date}")

    report_md = fetch_report_md(fs, scan_date)
    print(f"Fetched report_md ({len(report_md)} chars)")

    ledger_summary = fetch_ledger_summary(bq, scan_date)
    print(f"Fetched ledger_summary: {ledger_summary['notes']}")

    candidates = []
    for r in raw_candidates:
        c = {k: v for k, v in r.items() if v is not None}
        c["static_rank"] = r["static_rank"]
        candidates.append(c)

    target = datetime.strptime(scan_date, "%Y-%m-%d").date()
    entry_day = (target + timedelta(days=1)).isoformat()  # naive: skip weekend logic for smoke

    return {
        "scan_date": scan_date,
        "entry_day": entry_day,
        "candidates": candidates,
        "report_md": report_md,
        "ledger_summary": ledger_summary,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-date", required=True, help="YYYY-MM-DD ET")
    ap.add_argument("--url", required=True, help="signal-ranker base URL")
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--save", help="optional path to save the request payload")
    args = ap.parse_args()

    payload = build_rank_request(args.scan_date, top_n=args.top_n)
    if args.save:
        with open(args.save, "w") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"Saved payload to {args.save}")

    print(f"\n--- POST {args.url}/rank ---")
    # signal-ranker is IAM-invoker only (audit 2026-05-08 item 4). For operator
    # smoke tests we mint an ID token via gcloud — works with user creds where
    # google.oauth2.id_token.fetch_id_token only works with SA creds.
    if not shutil.which("gcloud"):
        raise SystemExit("gcloud CLI not on PATH — required to mint an ID token")
    id_token = subprocess.run(
        ["gcloud", "auth", "print-identity-token"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    headers = {"Authorization": f"Bearer {id_token}"}
    resp = requests.post(
        f"{args.url}/rank",
        json=json.loads(json.dumps(payload, default=str)),
        headers=headers,
        timeout=300,
    )
    print(f"status: {resp.status_code}")
    try:
        body = resp.json()
        print(json.dumps(body, indent=2, default=str))
    except Exception:
        print(resp.text)
    return 0 if resp.ok else 1


if __name__ == "__main__":
    sys.exit(main())
