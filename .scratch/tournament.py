"""Robust bracket judge: full pool (bull+bear), report context, no memory.
- each call sees <=10 contracts; intermediate rounds advance TOP-2, final round picks 1
- run the whole bracket 3x with different shuffles, take the consensus winner
Leakage cols excluded."""
from __future__ import annotations
import asyncio, json, os, random
import google.auth
from google import genai
from google.genai import types as gt
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
_, proj = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", proj or "profitscout-fida8")
from google.cloud import bigquery, firestore  # noqa

MODEL = "gemini-3.1-pro-preview"
SCAN = "2026-06-03"
REPORT_DOC = "2026-06-04"
SEEDS = [7, 17, 29]

COLS = """ticker, direction, overnight_score, premium_score, underlying_price, price_change_pct,
 call_dollar_volume, put_dollar_volume, call_vol_oi_ratio, put_vol_oi_ratio, call_uoa_depth, put_uoa_depth,
 call_active_strikes, put_active_strikes, flow_intent, flow_intent_reasoning,
 recommended_contract, recommended_strike, recommended_expiration, recommended_dte, recommended_mid_price,
 recommended_spread_pct, recommended_delta, recommended_gamma, recommended_theta, recommended_iv,
 recommended_oi, recommended_volume, moneyness_pct,
 rsi_14, macd, sma_50, sma_200, atr_normalized_move, golden_cross, above_sma_50, above_sma_200,
 support, resistance, high_52w, low_52w,
 thesis, news_summary, key_headline, catalyst_type, catalyst_score,
 mean_reversion_risk, move_overdone, reversal_probability, risk_reward_ratio,
 premium_bull_flow, premium_bear_flow, premium_high_rr, premium_high_atr, premium_hedge"""

PROMPT_HEAD = """Your goal: make money buying a single option and selling it for a profit within 3 trading days.

Today's market report:
<report>
__REPORT__
</report>

Candidate contracts (one JSON each - flow, contract, greeks, technicals, news):
"""
PROMPT_TAIL = ('\nRank the contracts you would buy, best first. Return ONLY JSON: '
               '{"picks":["<ticker>","<ticker>",...],"why":"<one sentence on your #1 pick>"}')

client = genai.Client(vertexai=True, location="global")
cfg = gt.GenerateContentConfig(response_mime_type="application/json")

def get_report() -> str:
    db = firestore.Client(project="profitscout-fida8")
    for doc_id in (REPORT_DOC, SCAN):
        d = db.collection("daily_reports").document(doc_id).get()
        if d.exists:
            data = d.to_dict() or {}
            for f in ("report_md", "markdown", "content", "report"):
                if data.get(f) and len(str(data[f])) > 200:
                    return str(data[f])
    return "(report unavailable)"

async def judge(batch, report):
    prompt = PROMPT_HEAD.replace("__REPORT__", report) + \
        "\n".join(json.dumps(c, default=str) for c in batch) + PROMPT_TAIL
    for attempt in range(3):
        try:
            r = await client.aio.models.generate_content(model=MODEL, contents=prompt, config=cfg)
            d = json.loads(r.text)
            if isinstance(d, list): d = d[0] if d else {}
            picks = d.get("picks") or ([d["pick"]] if d.get("pick") else [])
            return {"picks": [p for p in picks if isinstance(p, str)], "why": d.get("why", "")}
        except Exception as e:
            if attempt == 2: return {"picks": [], "why": f"(err {e})"}
            await asyncio.sleep(1.5 * (attempt + 1))

async def run_bracket(rows, by_t, report, seed):
    rng = random.Random(seed)
    pool = rows[:]; rnd = 0; why_by = {}
    while len(pool) > 1:
        rnd += 1
        rng.shuffle(pool)
        batches = [pool[i:i+10] for i in range(0, len(pool), 10)]  # always <=10
        k = 2 if len(pool) > 10 else 1   # advance top-2 until the single final batch
        results = await asyncio.gather(*[judge(b, report) for b in batches])
        nxt, why_by = [], {}
        for w in results:
            for t in w.get("picks", [])[:k]:
                if t in by_t and t not in {x["ticker"] for x in nxt}:
                    nxt.append(by_t[t]); why_by[t] = w.get("why")
        if not nxt: break
        pool = nxt
    return (pool[0] if pool else None), why_by

async def main():
    report = get_report()
    bq = bigquery.Client(project="profitscout-fida8")
    rows = [dict(r) for r in bq.query(
        f"SELECT {COLS} FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` "
        f'WHERE scan_date="{SCAN}"').result()]
    rows = [{k: v for k, v in r.items() if v is not None} for r in rows]
    by_t = {r["ticker"]: r for r in rows}
    nb = sum(r["direction"] == "BULLISH" for r in rows)
    print(f"report {len(report)}ch | {len(rows)} contracts ({nb} bull / {len(rows)-nb} bear)")
    print(f"3 brackets x (94->20->4->1), top-2 advance, <=10/call\n")

    brk = await asyncio.gather(*[run_bracket(rows, by_t, report, s) for s in SEEDS])
    from collections import Counter
    winners = [(w["ticker"], w["direction"], wb.get(w["ticker"])) for w, wb in brk if w]
    for i, (t, d, why) in enumerate(winners):
        print(f"run {i+1} ({SEEDS[i]}): {t} [{d}] - {why}")
    tally = Counter(t for t, _, _ in winners)
    top, n = tally.most_common(1)[0]
    fp = by_t[top]
    print(f"\n=== CONSENSUS WINNER: {top} [{fp['direction']}]  ({n}/3 runs) ===")
    print(f"  score={fp.get('overnight_score')} call$={fp.get('call_dollar_volume')} put$={fp.get('put_dollar_volume')} "
          f"moneyness={fp.get('moneyness_pct')} dte={fp.get('recommended_dte')} delta={fp.get('recommended_delta')} "
          f"pxchg={fp.get('price_change_pct')} rsi={fp.get('rsi_14')} catalyst={fp.get('catalyst_type')}")
    if n == 1:
        print("  (no majority — 3 runs disagreed; tie-break by flow/judgment needed)")

asyncio.run(main())
