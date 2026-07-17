"""Read-only replay: would the new macro/sector + final-round quant.md priors
change the 2026-06-08 pick? Runs the DEPLOYED tournament code locally (no persist,
no email, no ledger write) in two configs x 3 runs each. NEW vs CONTROL is the
clean isolation; comparison to the actual SIRI pick is secondary (report was
regenerated + LLM is stochastic)."""
import asyncio
import os
import sys

os.environ.setdefault("PROJECT_ID", "profitscout-fida8")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "profitscout-fida8")
from collections import Counter

from google.cloud import bigquery, firestore

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "signal-judge"))
from app import agent, tools                                     # noqa: E402
from app.schemas import Candidate, RankRequest, LedgerSummary    # noqa: E402

SCAN, ENTRY = "2026-06-08", "2026-06-09"
bq = bigquery.Client(project="profitscout-fida8")
db = firestore.Client(project="profitscout-fida8")

# --- pool: rebuild from enriched (same source signal-notifier uses) ---
rows = list(bq.query(
    f"SELECT * FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` "
    f"WHERE scan_date='{SCAN}'"
).result())
cands = []
for r in rows:
    d = dict(r)
    for k, v in list(d.items()):
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    if not d.get("ticker") or d.get("direction") not in ("BULLISH", "BEARISH"):
        continue
    try:
        d["overnight_score"] = int(d.get("overnight_score") or 0)
        cands.append(Candidate(**d))
    except Exception as e:
        print("skip", d.get("ticker"), repr(e))
print(f"pool size: {len(cands)} candidates")

# --- report: enriched (NEW) vs sections-stripped (CONTROL) ---
doc = db.collection("daily_reports").document(SCAN).get().to_dict() or {}
parts = []
if doc.get("title"):
    parts.append(f"# {doc['title']}")
if doc.get("headline"):
    parts.append(doc["headline"])
if doc.get("content"):
    parts.append(doc["content"])
report_new = "\n\n".join(parts)


def strip_sections(md: str) -> str:
    for hdr in ("## Macro & Regime Backdrop", "## Sector Tape"):
        i = md.find(hdr)
        if i == -1:
            continue
        nxt = md.find("\n## ", i + 3)
        md = md[:i] + (md[nxt + 1:] if nxt > 0 else "")
    return md


report_ctrl = strip_sections(report_new)
print(f"report_new chars={len(report_new)}  report_ctrl chars={len(report_ctrl)} "
      f"(macro/sector stripped={'## Macro' not in report_ctrl and '## Sector' not in report_ctrl})")
print(f"quant.md bytes injected at final round: {len(tools.load_quant_md())}")


async def run_once(report_md: str, with_quant: bool):
    req = RankRequest(scan_date=SCAN, entry_day=ENTRY, candidates=cands,
                      report_md=report_md, ledger_summary=LedgerSummary())
    orig = tools.load_quant_md
    if not with_quant:
        tools.load_quant_md = lambda: ""
    try:
        w, why, conf, _ = await agent.run_tournament(req)
    finally:
        tools.load_quant_md = orig
    return (w.ticker if w else None, conf, (why or "")[:120])


async def main():
    actual = list(bq.query(
        "SELECT candidate_ticker, picker_confidence FROM "
        "`profitscout-fida8.profit_scout.signal_ranker_runs` "
        f"WHERE scan_date='{SCAN}' AND picker_chose=true LIMIT 1"
    ).result())
    if actual:
        print(f"\nACTUAL recorded pick (old code): {actual[0].candidate_ticker} "
              f"({actual[0].picker_confidence})\n")

    new_w, ctrl_w = [], []
    for i in range(3):
        t, c, why = await run_once(report_new, True)
        new_w.append(t)
        print(f"NEW     run {i+1}: {t}  ({c})  why={why}")
    for i in range(3):
        t, c, why = await run_once(report_ctrl, False)
        ctrl_w.append(t)
        print(f"CONTROL run {i+1}: {t}  ({c})  why={why}")

    print(f"\nNEW winners (macro/sector + quant): {Counter(new_w)}")
    print(f"CONTROL winners (old behavior):     {Counter(ctrl_w)}")


asyncio.run(main())
