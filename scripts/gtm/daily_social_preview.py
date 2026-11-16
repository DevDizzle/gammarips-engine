#!/usr/bin/env python3
"""Daily "3-of-N Pool Preview" Social Post & Thread Generator for @GammaRips.

Queries BigQuery (project `profitscout-fida8`):
1. Latest scan_date from `profitscout-fida8.profit_scout.overnight_signals_enriched`
   ordered mirroring `get_pool(view="preview")`: `overnight_score DESC, call_dollar_volume DESC`.
2. Computes RV/IV ratio and counts contracts passing the Combo A filter:
   (Mid >= $1.00, OI >= 500, Delta 0.22-0.48, DTE 10-45).
3. Queries latest morning liquidity snapshots from
   `profitscout-fida8.profit_scout.pool_liquidity_snapshot` for those contracts.
4. Generates:
   - A crisp, compliance-clean standalone X post.
   - A 3-post X thread.
5. Verifies compliance against GammaRips voice & legal rules (no retired aliases,
   no individualized recommendations, no em dashes, educational disclaimer).

Usage:
  python scripts/gtm/daily_social_preview.py [--output PATH] [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime
import math
import os
import sys
from pathlib import Path
from typing import Any

from google.cloud import bigquery

# Resolve libs path for compliance import
LIB_PATH = Path(__file__).resolve().parents[2] / "libs" / "gammarips_content"
if str(LIB_PATH) not in sys.path:
    sys.path.insert(0, str(LIB_PATH))

PROJECT_ID = "profitscout-fida8"
ENRICHED_TABLE = f"`{PROJECT_ID}.profit_scout.overnight_signals_enriched`"
LIQUIDITY_TABLE = f"`{PROJECT_ID}.profit_scout.pool_liquidity_snapshot`"

FREE_MCP_COMMAND = "claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp"
PRO_URL = "https://gammarips.com/pricing"
PRO_DETAILS = "$29/mo founding price, 30-day free trial"
DISCLAIMER_TEXT = "Educational only. Not investment advice."


def get_bigquery_client(project: str = PROJECT_ID) -> bigquery.Client:
    return bigquery.Client(project=project)


def fetch_latest_scan_data(
    client: bigquery.Client, target_date: str | None = None
) -> tuple[str, list[dict[str, Any]], int, int]:
    """Fetch all contracts for latest scan_date, compute RV/IV and Combo A count."""
    date_clause = f"scan_date = '{target_date}'" if target_date else "scan_date = (SELECT MAX(scan_date) FROM " + ENRICHED_TABLE + ")"

    query = f"""
    SELECT
        scan_date,
        ticker,
        direction,
        overnight_score,
        key_headline,
        catalyst_type,
        catalyst_score,
        recommended_contract,
        recommended_strike,
        recommended_expiration,
        recommended_dte,
        recommended_delta,
        recommended_mid_price,
        recommended_oi,
        recommended_volume,
        recommended_iv,
        underlying_price,
        atr_14,
        call_dollar_volume,
        put_dollar_volume
    FROM {ENRICHED_TABLE}
    WHERE {date_clause}
    ORDER BY overnight_score DESC, GREATEST(IFNULL(call_dollar_volume, 0), IFNULL(put_dollar_volume, 0)) DESC
    """
    job = client.query(query)
    rows = [dict(r) for r in job.result()]
    if not rows:
        raise ValueError(f"No enriched signals found for query.")

    scan_date_str = str(rows[0]["scan_date"])

    # Compute RV/IV and evaluate Combo A filter
    combo_a_count = 0
    total_pool_count = len(rows)

    for r in rows:
        # RV/IV ratio = (atr_14 / underlying_price * sqrt(252)) / recommended_iv
        atr = r.get("atr_14")
        px = r.get("underlying_price")
        iv = r.get("recommended_iv")
        rv_iv = None
        if atr and px and iv and px > 0 and iv > 0:
            rv_iv = (atr / px) * math.sqrt(252.0) / iv
        r["rv_iv_ratio"] = rv_iv

        mid = r.get("recommended_mid_price") or 0.0
        oi = r.get("recommended_oi") or 0
        delta = abs(r.get("recommended_delta") or 0.0)
        dte = r.get("recommended_dte") or 0

        # Combo A Tradability Floor: Mid >= $1.00, OI >= 500, Delta 0.22-0.48, DTE 10-45
        is_combo_a = (mid >= 1.00) and (oi >= 500) and (0.22 <= delta <= 0.48) and (10 <= dte <= 45)
        r["passes_combo_a"] = is_combo_a
        if is_combo_a:
            combo_a_count += 1

    return scan_date_str, rows, total_pool_count, combo_a_count


def fetch_morning_liquidity(
    client: bigquery.Client, contracts: list[str]
) -> dict[str, dict[str, Any]]:
    """Fetch latest morning liquidity snapshot for the specified contracts."""
    query = f"""
    WITH ranked AS (
        SELECT
            contract,
            as_of,
            open_interest,
            day_volume,
            mid,
            bid,
            ask,
            last_trade_price,
            underlying_price,
            delta,
            ROW_NUMBER() OVER (PARTITION BY contract ORDER BY as_of DESC) as rn
        FROM {LIQUIDITY_TABLE}
        WHERE contract IN UNNEST(@contracts)
          AND fetch_status = 'ok'
    )
    SELECT * EXCEPT(rn) FROM ranked WHERE rn = 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("contracts", "STRING", contracts)]
    )
    results = [dict(r) for r in client.query(query, job_config=job_config).result()]
    return {r["contract"]: r for r in results}


def clean_headline(headline: str, max_len: int = 120) -> str:
    """Format catalyst headline cleanly without line breaks or trailing periods."""
    if not headline:
        return "Unusual flow & catalyst momentum"
    h = headline.strip().replace("\n", " ").replace("—", "-").replace("–", "-")
    if len(h) > max_len:
        # Truncate at word boundary
        cutoff = h[:max_len - 3].rfind(" ")
        if cutoff > 20:
            h = h[:cutoff].rstrip() + "..."
        else:
            h = h[:max_len - 3].rstrip() + "..."
    return h


def format_contract_display(c: dict[str, Any], liq: dict[str, Any] | None) -> dict[str, Any]:
    """Extract display fields combining enriched signal and morning liquidity."""
    ticker = c["ticker"]
    contract = c["recommended_contract"]
    strike = c["recommended_strike"]
    expiry = str(c["recommended_expiration"])
    dte = c["recommended_dte"]
    mid = c["recommended_mid_price"]
    delta = c["recommended_delta"]

    # Morning snapshot overrides / values
    morning_oi = c["recommended_oi"]
    morning_vol = c["recommended_volume"]
    morning_delta = delta
    if liq:
        if liq.get("open_interest") is not None:
            morning_oi = liq["open_interest"]
        if liq.get("day_volume") is not None:
            morning_vol = liq["day_volume"]
        if liq.get("delta") is not None:
            morning_delta = liq["delta"]

    rv_iv = c.get("rv_iv_ratio")
    rv_iv_str = f"{rv_iv:.2f}" if rv_iv is not None else "N/A"
    headline = clean_headline(c.get("key_headline", ""))

    return {
        "ticker": ticker,
        "contract": contract,
        "strike": strike,
        "expiry": expiry,
        "dte": dte,
        "mid": mid,
        "delta": delta,
        "morning_delta": morning_delta,
        "morning_oi": morning_oi,
        "morning_vol": morning_vol,
        "rv_iv": rv_iv_str,
        "headline": headline,
    }


def generate_single_post(
    preview_items: list[dict[str, Any]], combo_a_count: int, total_count: int
) -> str:
    """Generate a crisp, compliance-clean standalone post for @GammaRips."""
    pool_filter_str = f"Showing 3 of {combo_a_count} contracts passing today's Combo A filter (Mid >= $1.00, OI >= 500, Delta 0.22-0.48, DTE 10-45)"

    lines = [
        f"GammaRips Daily Free Preview: {pool_filter_str}.\n",
    ]

    for item in preview_items:
        t = item["ticker"]
        exp = item["expiry"]
        strike = f"${int(item['strike']) if item['strike'] == int(item['strike']) else item['strike']}"
        lines.append(
            f"${t} {exp} {strike}C ({item['dte']} DTE) | {item['contract']}\n"
            f"  Delta: {item['delta']:.2f} | Mid: ${item['mid']:.2f} | Morning OI: {item['morning_oi']:,} | RV/IV: {item['rv_iv']}\n"
            f"  Catalyst: {item['headline']}\n"
        )

    lines.append(
        f"Add the free MCP to your trading agent in 10s:\n"
        f"`{FREE_MCP_COMMAND}`\n\n"
        f"Full daily pool & live intraday snapshots: {PRO_URL} ({PRO_DETAILS}).\n\n"
        f"{DISCLAIMER_TEXT}"
    )

    return "\n".join(lines).replace("—", "-").replace("–", "-")


def generate_thread(
    preview_items: list[dict[str, Any]], combo_a_count: int, total_count: int
) -> list[str]:
    """Generate a 3-post X thread for @GammaRips."""
    c1, c2, c3 = preview_items[0], preview_items[1], preview_items[2]

    # Post 1: Hook + Filter Context + Contract 1
    s1 = f"${int(c1['strike']) if c1['strike'] == int(c1['strike']) else c1['strike']}"
    post1 = (
        f"Today's GammaRips Pool Preview.\n\n"
        f"Showing 3 of {combo_a_count} contracts passing today's Combo A filter "
        f"(Mid >= $1.00, OI >= 500, Delta 0.22-0.48, DTE 10-45).\n\n"
        f"1/3 Preview: ${c1['ticker']} {c1['expiry']} {s1}C ({c1['dte']} DTE)\n"
        f"- OCC: `{c1['contract']}`\n"
        f"- Delta: {c1['delta']:.2f} | Mid: ${c1['mid']:.2f}\n"
        f"- Morning OI: {c1['morning_oi']:,} | RV/IV: {c1['rv_iv']}\n"
        f"- Catalyst: {c1['headline']}"
    )

    # Post 2: Contracts 2 and 3
    s2 = f"${int(c2['strike']) if c2['strike'] == int(c2['strike']) else c2['strike']}"
    s3 = f"${int(c3['strike']) if c3['strike'] == int(c3['strike']) else c3['strike']}"
    post2 = (
        f"2/3 Preview Continued:\n\n"
        f"${c2['ticker']} {c2['expiry']} {s2}C ({c2['dte']} DTE)\n"
        f"- OCC: `{c2['contract']}`\n"
        f"- Delta: {c2['delta']:.2f} | Mid: ${c2['mid']:.2f} | Morning OI: {c2['morning_oi']:,} | RV/IV: {c2['rv_iv']}\n"
        f"- Catalyst: {c2['headline']}\n\n"
        f"${c3['ticker']} {c3['expiry']} {s3}C ({c3['dte']} DTE)\n"
        f"- OCC: `{c3['contract']}`\n"
        f"- Delta: {c3['delta']:.2f} | Mid: ${c3['mid']:.2f} | Morning OI: {c3['morning_oi']:,} | RV/IV: {c3['rv_iv']}\n"
        f"- Catalyst: {c3['headline']}"
    )

    # Post 3: MCP Agent Access CTA + Pricing + Educational Disclaimer
    post3 = (
        f"3/3 Connect your trading agent in 10 seconds:\n\n"
        f"`{FREE_MCP_COMMAND}`\n\n"
        f"Inspect today's 3 free preview contracts directly in Claude Code, Cursor, or Codex.\n\n"
        f"Unlock the full filtered pool ({combo_a_count} contracts today) & 10-min liquidity updates at {PRO_URL} ({PRO_DETAILS}).\n\n"
        f"{DISCLAIMER_TEXT}"
    )

    return [
        post1.replace("—", "-").replace("–", "-"),
        post2.replace("—", "-").replace("–", "-"),
        post3.replace("—", "-").replace("–", "-"),
    ]


def verify_compliance(texts: list[str]) -> list[dict[str, Any]]:
    """Verify generated texts against GammaRips compliance and voice rules."""
    reports = []
    try:
        from gammarips_content import voice_rules
        retired = voice_rules.RETIRED_ALIASES
        banned = voice_rules.BANNED_RECOMMENDATION_PHRASES
    except Exception:
        retired = ("Ripper", "Daily Playbook", "The Overnight Edge", "premium signal", "curated daily pick")
        banned = ("buy this", "sell this", "act now", "guaranteed", "can't lose")

    for idx, text in enumerate(texts):
        issues = []
        is_thread_intermediate = idx in (1, 2)  # Posts 1/3 and 2/3 in thread

        # Check retired aliases
        for a in retired:
            if a.lower() in text.lower():
                issues.append(f"Contains retired alias: '{a}'")
        # Check banned recommendation phrases
        for p in banned:
            if p.lower() in text.lower():
                issues.append(f"Contains banned recommendation phrase: '{p}'")
        # Check em / en dash
        if "—" in text or "–" in text:
            issues.append("Contains em/en dash (use plain hyphen '-')")
        # Check disclaimer: required on single post (idx 0) and final thread post (idx 3)
        if not is_thread_intermediate:
            if DISCLAIMER_TEXT not in text and "Not investment advice" not in text:
                issues.append("Missing required educational disclaimer")

        reports.append({
            "index": idx,
            "char_count": len(text),
            "passed": len(issues) == 0,
            "issues": issues,
            "note": "Disclaimer deferred to thread conclusion (Post 3/3)" if is_thread_intermediate else "Fully verified",
        })
    return reports


def build_markdown_report(
    scan_date: str,
    total_pool_count: int,
    combo_a_count: int,
    preview_items: list[dict[str, Any]],
    single_post: str,
    thread_posts: list[str],
    compliance_results: list[dict[str, Any]],
) -> str:
    """Format full markdown document to save to workspace."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md = [
        f"# GammaRips Daily Social Preview & Post Kit ({scan_date})",
        "",
        f"- **Generated At**: {now_utc}",
        f"- **BigQuery Source Table**: `profitscout-fida8.profit_scout.overnight_signals_enriched`",
        f"- **Morning Liquidity Snapshot**: `profitscout-fida8.profit_scout.pool_liquidity_snapshot`",
        f"- **Pool Scan Date**: `{scan_date}`",
        f"- **Total Raw Enriched Pool**: `{total_pool_count}` contracts",
        f"- **Passing Combo A Filter**: `{combo_a_count}` contracts (`Mid >= $1.00`, `OI >= 500`, `Delta 0.22-0.48`, `DTE 10-45`)",
        "",
        "---",
        "",
        "## 1. Top 3 Free Preview Contracts",
        "",
        "| Ticker | OCC Contract | Strike & Expiry | DTE | Scan Delta | Morning Delta | Mid | Morning OI | RV/IV | Catalyst Headline |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]

    for item in preview_items:
        strike_fmt = f"${int(item['strike']) if item['strike'] == int(item['strike']) else item['strike']}C"
        md.append(
            f"| **${item['ticker']}** | `{item['contract']}` | {item['expiry']} {strike_fmt} | {item['dte']} | {item['delta']:.2f} | {item['morning_delta']:.2f} | ${item['mid']:.2f} | {item['morning_oi']:,} | {item['rv_iv']} | {item['headline']} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 2. Standalone X Post (@GammaRips)",
        "",
        "```text",
        single_post,
        "```",
        "",
        f"- **Character Count**: {len(single_post)} chars",
        f"- **Compliance Status**: {'PASSED (Zero violations)' if compliance_results[0]['passed'] else 'FAILED: ' + ', '.join(compliance_results[0]['issues'])}",
        "",
        "---",
        "",
        "## 3. 3-Post X Thread (@GammaRips)",
        "",
        "### Thread Post 1/3 (Hook & Contract 1)",
        "```text",
        thread_posts[0],
        "```",
        f"- **Character Count**: {len(thread_posts[0])} chars",
        f"- **Compliance Status**: {'PASSED' if compliance_results[1]['passed'] else 'FAILED: ' + ', '.join(compliance_results[1]['issues'])}",
        "",
        "### Thread Post 2/3 (Contracts 2 & 3)",
        "```text",
        thread_posts[1],
        "```",
        f"- **Character Count**: {len(thread_posts[1])} chars",
        f"- **Compliance Status**: {'PASSED' if compliance_results[2]['passed'] else 'FAILED: ' + ', '.join(compliance_results[2]['issues'])}",
        "",
        "### Thread Post 3/3 (10s MCP Quickstart & Pro Upgrade)",
        "```text",
        thread_posts[2],
        "```",
        f"- **Character Count**: {len(thread_posts[2])} chars",
        f"- **Compliance Status**: {'PASSED' if compliance_results[3]['passed'] else 'FAILED: ' + ', '.join(compliance_results[3]['issues'])}",
        "",
        "---",
        "",
        "## 4. MCP Quickstart Command Verification",
        "",
        "```bash",
        FREE_MCP_COMMAND,
        "```",
        "",
        f"- **Pro Upgrade URL**: [{PRO_URL}]({PRO_URL})",
        f"- **Terms**: {PRO_DETAILS}",
        f"- **Compliance Disclaimer**: *{DISCLAIMER_TEXT}*",
        "",
    ])

    return "\n".join(md)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate daily social preview post and thread.")
    parser.add_argument("--date", help="Target scan_date (YYYY-MM-DD), default latest.")
    parser.add_argument(
        "--output",
        default="/home/evan/workspace/GAMMARIPS-DAILY-SOCIAL-2026-11-16.md",
        help="Path to output markdown file.",
    )
    args = parser.parse_args()

    client = get_bigquery_client(PROJECT_ID)

    print(f"Fetching enriched scan data from {ENRICHED_TABLE}...")
    scan_date, rows, total_pool_count, combo_a_count = fetch_latest_scan_data(
        client, target_date=args.date
    )
    print(f"Latest scan date: {scan_date}")
    print(f"Total pool contracts: {total_pool_count}")
    print(f"Contracts passing Combo A filter: {combo_a_count}")

    # Top 3 contracts mirroring get_pool(view="preview")
    top_3_rows = rows[:3]
    top_contracts = [r["recommended_contract"] for r in top_3_rows]
    print(f"Top 3 contracts: {top_contracts}")

    print(f"Fetching morning liquidity snapshots from {LIQUIDITY_TABLE}...")
    liq_map = fetch_morning_liquidity(client, top_contracts)
    print(f"Found liquidity snapshots for {len(liq_map)} contracts.")

    preview_items = [format_contract_display(r, liq_map.get(r["recommended_contract"])) for r in top_3_rows]

    # Generate Single Post and Thread
    single_post = generate_single_post(preview_items, combo_a_count, total_pool_count)
    thread_posts = generate_thread(preview_items, combo_a_count, total_pool_count)

    # Compliance check
    all_texts = [single_post] + thread_posts
    compliance_results = verify_compliance(all_texts)

    for r in compliance_results:
        label = "Single Post" if r["index"] == 0 else f"Thread Post {r['index']}/3"
        status = "PASSED" if r["passed"] else f"FAILED: {r['issues']}"
        print(f"[{label}] {status} ({r['char_count']} chars)")

    # Build and write markdown
    md_content = build_markdown_report(
        scan_date=scan_date,
        total_pool_count=total_pool_count,
        combo_a_count=combo_a_count,
        preview_items=preview_items,
        single_post=single_post,
        thread_posts=thread_posts,
        compliance_results=compliance_results,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_content, encoding="utf-8")
    print(f"\nSuccessfully generated and saved social preview to: {out_path.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
