"""Live end-to-end test of the deployed signal-judge tournament: post the full
ungated pool + report to /rank, confirm winner + version=7 persistence. No email."""
import json, subprocess, os
import requests
from google.cloud import bigquery, firestore

URL = "https://signal-judge-406581297632.us-central1.run.app/rank"
SCAN, ENTRY, REPORT_DOC = "2026-06-03", "2026-06-04", "2026-06-04"
# same columns signal-notifier now selects (leakage-safe, no outcome cols)
COLS = """ticker, scan_date, direction, underlying_price, price_change_pct,
 recommended_contract, recommended_strike, recommended_expiration, recommended_dte, recommended_volume,
 recommended_oi, recommended_mid_price, recommended_spread_pct, recommended_delta, recommended_gamma,
 recommended_theta, recommended_iv, overnight_score, premium_score, call_dollar_volume, put_dollar_volume,
 call_uoa_depth, put_uoa_depth, call_active_strikes, put_active_strikes, volume_oi_ratio, call_vol_oi_ratio,
 put_vol_oi_ratio, moneyness_pct, vix3m_at_enrich, flow_intent, flow_intent_reasoning, rsi_14, macd,
 sma_50, sma_200, atr_normalized_move, golden_cross, above_sma_50, above_sma_200, support, resistance,
 high_52w, low_52w, thesis, news_summary, key_headline, catalyst_type, catalyst_score, mean_reversion_risk,
 move_overdone, reversal_probability, risk_reward_ratio, premium_bull_flow, premium_bear_flow,
 premium_high_rr, premium_high_atr, premium_hedge"""

bq = bigquery.Client(project="profitscout-fida8")
rows = [dict(r) for r in bq.query(f"SELECT {COLS} FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` WHERE scan_date='{SCAN}'").result()]
cands = [{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items() if v is not None} for r in rows]

db = firestore.Client(project="profitscout-fida8")
report = ""
for did in (REPORT_DOC, SCAN):
    d = db.collection("daily_reports").document(did).get()
    if d.exists:
        for f in ("report_md","markdown","content","report"):
            if (d.to_dict() or {}).get(f) and len(str(d.to_dict()[f]))>200: report=str(d.to_dict()[f]); break
    if report: break

payload = {"scan_date": SCAN, "entry_day": ENTRY, "candidates": cands, "report_md": report,
           "ledger_summary": {"window_days": 14, "closed_trades": 0, "notes": "test"}}
token = subprocess.check_output(["gcloud","auth","print-identity-token"]).decode().strip()
print(f"POST /rank  candidates={len(cands)}  report={len(report)}ch ...")
r = requests.post(URL, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=520)
print("HTTP", r.status_code)
b = r.json()
print(f"pick={b.get('pick')} runner_up={b.get('runner_up')} confidence={b.get('confidence')} "
      f"version={b.get('scorer_prompt_version')} run_id={b.get('run_id')} latency_ms={b.get('scorer_latency_ms')}")
print("justification:", b.get("justification"))
print("top_5/advanced:", b.get("top_5_tickers"))
