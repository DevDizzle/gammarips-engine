"""Validate the DEPLOYED signal-judge on today's real candidate slate via /rank.

Read-only w.r.t. the live pick: /rank ranks + writes a signal_ranker_runs audit
row (version=6). It does NOT email, post WhatsApp, or touch todays_pick. Uses the
real daily report from Firestore for a faithful regime read.
"""
from __future__ import annotations

import json
import subprocess

import requests
from google.cloud import firestore

SCAN_DATE = "2026-06-03"
ENTRY_DAY = "2026-06-04"
URL = "https://signal-judge-406581297632.us-central1.run.app/rank"
SLATES = "/home/user/gammarips-engine/.scratch/replay_slates.json"

# --- candidates from the reconstructed slate ---
slates = json.load(open(SLATES))
slate = next(s for s in slates if s["scan_date"] == SCAN_DATE)
candidates = []
for c in slate["candidates"]:
    e = {k: v for k, v in json.loads(c["enriched_json"]).items() if v is not None}
    e.setdefault("ticker", c["ticker"])
    candidates.append(e)

# --- real daily report from Firestore (fall back to stub if absent) ---
db = firestore.Client(project="profitscout-fida8")
report_md = ""
for coll, field in [("daily_reports", "markdown"), ("daily_reports", "report_md")]:
    doc = db.collection(coll).document(SCAN_DATE).get()
    if doc.exists:
        report_md = (doc.to_dict() or {}).get(field, "") or report_md
        if report_md:
            break
if not report_md:
    report_md = f"(stub) daily report for {SCAN_DATE} unavailable in Firestore."
print(f"report_md: {len(report_md)} chars | candidates: {[c['ticker'] for c in candidates]}")

payload = {
    "scan_date": SCAN_DATE,
    "entry_day": ENTRY_DAY,
    "candidates": candidates,
    "report_md": report_md,
    "ledger_summary": {"window_days": 14, "closed_trades": 0,
                       "notes": "(validation) ledger summary omitted"},
}

token = subprocess.check_output(["gcloud", "auth", "print-identity-token"]).decode().strip()
resp = requests.post(URL, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=300)
print(f"HTTP {resp.status_code}")
body = resp.json()
print(f"pick={body.get('pick')!r} runner_up={body.get('runner_up')!r} "
      f"confidence={body.get('confidence')!r} skip={body.get('skip')}")
print(f"version(scorer/picker)={body.get('scorer_prompt_version')}/{body.get('picker_prompt_version')} "
      f"model={body.get('scorer_model')} run_id={body.get('run_id')}")
print(f"case_memory_bytes={body.get('case_memory_bytes')} latency_ms={body.get('scorer_latency_ms')}")
print("justification:", body.get("justification"))
for v in body.get("scorer_outputs", []):
    print(f"  {v['ticker']}: f={v['flow_conviction']} r={v['regime_alignment']} "
          f"n={v['narrative_coherence']} leakage={v['leakage']}")
