"""Offline smoke for judge_v6: reconstruct one historical slate and run the
real single-judge call end-to-end (DRY_RUN, no BQ write).

Validates: leakage assert over all candidates, prompt assembly, the live gemini
structured-output call parsing into JudgeOutput, deterministic mass-leakage /
selection validation, and RankResponse assembly. NOT a unit test — needs Vertex
creds + judge model access.

Usage:  PYTHONPATH=. DRY_RUN=true .venv/bin/python scripts/smoke_judge_v6.py [SCAN_DATE]
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

os.environ.setdefault("DRY_RUN", "true")  # never write BQ from a smoke

from app import agent  # noqa: E402
from app.schemas import Candidate, LedgerSummary, RankRequest  # noqa: E402

SLATES = os.path.join(os.path.dirname(__file__), "replay_slates.json")


def build_request(scan_date: str) -> RankRequest:
    with open(SLATES) as f:
        slates = json.load(f)
    slate = next((s for s in slates if s["scan_date"] == scan_date), None)
    if slate is None:
        raise SystemExit(f"scan_date {scan_date} not in {SLATES}")
    candidates = []
    for c in slate["candidates"]:
        enriched = json.loads(c["enriched_json"])
        # enriched mirrors overnight_signals_enriched; Candidate has extra=allow.
        # Pin the required keys; drop nulls so render stays clean.
        enriched = {k: v for k, v in enriched.items() if v is not None}
        enriched.setdefault("ticker", c["ticker"])
        candidates.append(Candidate(**enriched))
    return RankRequest(
        scan_date=scan_date,
        entry_day=scan_date,  # smoke only; not persisted
        candidates=candidates,
        report_md=f"(smoke) Daily report for {scan_date}. Market regime context omitted in offline smoke.",
        ledger_summary=LedgerSummary(window_days=14, closed_trades=0, notes="(smoke) empty ledger"),
    )


async def main() -> None:
    scan_date = sys.argv[1] if len(sys.argv) > 1 else "2026-06-03"
    req = build_request(scan_date)
    print(f"scan_date={scan_date}  n_candidates={len(req.candidates)}  "
          f"tickers={[c.ticker for c in req.candidates]}")
    resp = await agent.run_pipeline(req)
    print(f"\n=== RankResponse ===")
    print(f"pick={resp.pick!r}  runner_up={resp.runner_up!r}  confidence={resp.confidence!r}")
    print(f"skip={resp.skip}  skip_reason={resp.skip_reason}")
    print(f"top_5_tickers={resp.top_5_tickers}")
    print(f"prompt_version(scorer/picker)={resp.scorer_prompt_version}/{resp.picker_prompt_version}  "
          f"model={resp.scorer_model}")
    print(f"latency_ms={resp.scorer_latency_ms}  case_memory_bytes={resp.case_memory_bytes}")
    print(f"n_verdicts={len(resp.scorer_outputs)}")
    print(f"justification={resp.justification!r}")
    print(f"\n=== per-candidate verdicts ===")
    for v in resp.scorer_outputs:
        print(f"  {v.ticker}: f={v.flow_conviction} r={v.regime_alignment} n={v.narrative_coherence} "
              f"composite={v.composite_score():.2f} leakage={v.leakage}")
        print(f"      {v.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
