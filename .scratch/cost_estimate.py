"""Measure real input/output tokens for the 3x bracket and estimate $/pick."""
from __future__ import annotations
import json, os
import google.auth
from google import genai
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
_, proj = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", proj or "profitscout-fida8")
from google.cloud import bigquery, firestore  # noqa

MODEL = "gemini-3.1-pro-preview"
SCAN = "2026-06-03"; REPORT_DOC = "2026-06-04"
COLS = open("/home/user/gammarips-engine/.scratch/tournament.py").read().split('COLS = """')[1].split('"""')[0]
HEAD = """Your goal: make money buying a single option and selling it for a profit within 3 trading days.

Today's market report:
<report>
__REPORT__
</report>

Candidate contracts (one JSON each - flow, contract, greeks, technicals, news):
"""
TAIL = '\nRank the contracts you would buy, best first. Return ONLY JSON: {"picks":["x"],"why":"y"}'

client = genai.Client(vertexai=True, location="global")
def ntok(text): return client.models.count_tokens(model=MODEL, contents=text).total_tokens

db = firestore.Client(project="profitscout-fida8")
report = ""
for did in (REPORT_DOC, SCAN):
    d = db.collection("daily_reports").document(did).get()
    if d.exists:
        for f in ("report_md","markdown","content","report"):
            if (d.to_dict() or {}).get(f) and len(str(d.to_dict()[f]))>200: report=str(d.to_dict()[f]); break
    if report: break

bq = bigquery.Client(project="profitscout-fida8")
rows = [dict(r) for r in bq.query(f"SELECT {COLS} FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` WHERE scan_date='{SCAN}'").result()]
rows = [{k:v for k,v in r.items() if v is not None} for r in rows]
contract_blobs = [json.dumps(c, default=str) for c in rows]

head_report = HEAD.replace("__REPORT__", report) + TAIL          # static per-call overhead (incl report)
overhead_tok = ntok(head_report)
report_tok = ntok(report)
all_contracts_tok = ntok("\n".join(contract_blobs))
avg_contract_tok = all_contracts_tok / len(rows)
print(f"N contracts: {len(rows)}")
print(f"report tokens:            {report_tok}")
print(f"per-call overhead (head+report+tail): {overhead_tok}")
print(f"avg contract JSON tokens: {avg_contract_tok:.0f}  (total {all_contracts_tok})")

# bracket shape per run: r1=10 calls/94 contracts, r2=2 calls/20, r3=1 call/4  -> 13 calls, 118 contract-instances
CALLS_PER_RUN = 13
CONTRACTS_PER_RUN = 94 + 20 + 4
RUNS = 3
calls = CALLS_PER_RUN * RUNS
contract_instances = CONTRACTS_PER_RUN * RUNS
in_tok = calls * overhead_tok + contract_instances * avg_contract_tok
out_tok = calls * 90  # ~small JSON
print(f"\n--- per PICK (3 runs x 13 calls = {calls} calls) ---")
print(f"input tokens:  {in_tok:,.0f}")
print(f"output tokens: {out_tok:,.0f}")
print(f"  (report resent {calls}x; if [head+report] prefix is cached, ~{calls*overhead_tok:,.0f} input tok become cache-hits)")

def cost(pin, pout, label, cached_frac=0.0, cache_price=None):
    cached_in = calls * overhead_tok * cached_frac
    fresh_in = in_tok - cached_in
    c = fresh_in/1e6*pin + (cached_in/1e6*(cache_price if cache_price else pin)) + out_tok/1e6*pout
    print(f"  {label}: ${c:.3f}/pick  -> ${c*21:.2f}/mo (21 trading days)")

print("\n--- cost @ ASSUMED pro pricing (VERIFY actual gemini-3.1-pro-preview rates) ---")
print("[A] no caching, $2.00/M in, $10.00/M out:")
cost(2.0, 10.0, "    ")
print("[B] cache the head+report prefix (~75% of overhead is the report), cached @ $0.50/M:")
cost(2.0, 10.0, "    ", cached_frac=0.75, cache_price=0.50)
print("[C] Batch API (~50% off, if latency tolerable): ")
cost(1.0, 5.0, "    ")
