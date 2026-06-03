"""Deterministic helpers for V5.4 signal-ranker.

NOT ADK tools — pure functions. The agent layer (`app/agent.py`) uses these
between Scorer and Picker, and after Picker for persistence. Keeping them here
makes them unit-testable without the ADK runtime.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import date, datetime, timezone
from typing import Any

from google.cloud import bigquery

from app.schemas import (
    COMPOSITE_WEIGHTS,
    TOP_N,
    Candidate,
    LedgerSummary,
    PickerOutput,
    ScorerOutput,
)

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")
TABLE_RUNS = f"{PROJECT_ID}.{DATASET}.signal_ranker_runs"

SCORER_MODEL = os.getenv("SCORER_MODEL", "gemini-3.5-flash")
PICKER_MODEL = os.getenv("PICKER_MODEL", "gemini-3.1-pro-preview")
SCORER_PROMPT_VERSION = int(os.getenv("SCORER_PROMPT_VERSION", "5"))
PICKER_PROMPT_VERSION = int(os.getenv("PICKER_PROMPT_VERSION", "5"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Floor for partial-Scorer-failure tolerance (audit 2026-05-08 item 6). If
# fewer than this fraction of candidates produce successful Scorer outputs,
# the pipeline raises and signal-notifier fails closed (no pick today).
# Default 0.5 — a 10-candidate scan must score >=5 successfully or we bail.
MIN_SCORER_SUCCESS_FRAC = float(os.getenv("MIN_SCORER_SUCCESS_FRAC", "0.5"))


# Forbidden field-name fragments. Any candidate or ledger field whose key
# matches one of these substrings is treated as a leakage source — only the
# explicitly-allowed names below are considered safe to pass to the LLM.
#
# Aligned with .claude/agents/gammarips-researcher.md canonical list (audit
# finding 2026-05-08): substring matching `outcome` catches `outcome_tier` but
# the next_day / day2 / day3 / peak_return / *_price / is_win / *_at families
# need explicit fragments because of `extra="allow"` on Candidate.
_LEAKAGE_FIELD_BLOCKLIST: tuple[str, ...] = (
    # Exit / outcome side
    "_at_exit",
    "exit_price",
    "exit_date",
    "exit_reason",
    "exit_timestamp",
    "outcome",
    "realized_pnl",
    "realized_return",
    "winner",
    "loser",
    "is_win",
    "bars_to_exit",
    # Forward-looking price snapshots (researcher's labeled-table family)
    "next_day",
    "day2",
    "day3",
    "peak_return",
    "target_price",
    "stop_price",
    "entry_price",
    "entry_timestamp",
    # Bookkeeping that implies post-scan state
    "labeled_at",
    "performance_updated",
    "timeout_day",
    "simulator_version",
)


def assert_no_leakage(scan_date: str, candidate: Candidate) -> None:
    """Block any candidate field that smells like an exit-side outcome.

    The Scorer / Picker MUST only see information dated <= scan_date close.
    Realized exit prices, outcome flags, and exit timestamps are post-scan
    and would be leakage if surfaced. Raises ValueError on hit (caller
    fails-closed; signal-notifier publishes no pick).
    """
    raw = candidate.model_dump()
    for k in raw.keys():
        kl = k.lower()
        if any(frag in kl for frag in _LEAKAGE_FIELD_BLOCKLIST):
            raise ValueError(f"leakage_block: field '{k}' on candidate "
                             f"{candidate.ticker} is post-scan and not safe")
    # Optional explicit timestamp guard: if a `date` or `_dt` field is later
    # than scan_date, that's a bug.
    target = datetime.strptime(scan_date, "%Y-%m-%d").date()
    for k, v in raw.items():
        if isinstance(v, (date, datetime)):
            d = v.date() if isinstance(v, datetime) else v
            if d > target:
                raise ValueError(f"leakage_block: field '{k}'={d} > scan_date={target}")


def take_top_n(
    scorer_outputs: list[ScorerOutput], n: int = TOP_N
) -> list[ScorerOutput]:
    """Sort by weighted-sum composite descending. Deterministic tie-break:
    higher flow_conviction first (most expensive rubric), then ticker A→Z.

    Composite is rounded to 6 decimals before the tiebreak so float-precision
    artifacts (e.g. 6.3999999 vs 6.4000001 from `0.15 * z`) don't silently
    skip the flow tiebreaker on practically-equal composites.

    Pure function — no I/O. Agent layer calls this between Scorer and Picker.
    """
    return sorted(
        scorer_outputs,
        key=lambda s: (
            -round(s.composite_score(), 6),
            -s.flow_conviction,
            s.ticker,
        ),
    )[:n]


def build_run_id(scan_date: str) -> str:
    """Stable run_id per /rank invocation. Embeds scan_date for grep-ability."""
    return f"v5_4_{scan_date}_{uuid.uuid4().hex[:8]}"


def persist_run(
    *,
    run_id: str,
    scan_date: str,
    entry_day: str,
    candidates: list[Candidate],
    scorer_outputs: list[ScorerOutput],
    top_5: list[ScorerOutput],
    picker_output: PickerOutput | None,
    scorer_latency_ms: int | None,
    picker_latency_ms: int | None,
) -> None:
    """Write one row per (run_id, candidate_ticker) to signal_ranker_runs.

    Schema in scripts/ledger_and_tracking/create_signal_ranker_runs.py.
    No-op on DRY_RUN=true (signal-notifier still gets the response).

    ``picker_output=None`` is the mass-leakage skip path — the Picker never
    ran, so picker_chose/picker_runner_up are False for every row and the
    justification/confidence fields are NULL. Audit trail still gets written
    so forensic queries can find the run.
    """
    if DRY_RUN:
        logger.info(f"DRY_RUN=true — skipping signal_ranker_runs write for {run_id}")
        return

    static_rank_by_ticker: dict[str, int | None] = {
        c.ticker: c.static_rank for c in candidates
    }
    top_5_set = {s.ticker for s in top_5}
    pick = picker_output.pick if picker_output else None
    runner_up = picker_output.runner_up if picker_output else None
    weights_json = json.dumps(COMPOSITE_WEIGHTS)
    now_ts = datetime.now(timezone.utc).isoformat()

    rows: list[dict[str, Any]] = []
    for s in scorer_outputs:
        is_picked = picker_output is not None and s.ticker == pick
        is_runner = (
            picker_output is not None
            and s.ticker == runner_up
            and s.ticker != pick
        )
        rows.append(
            {
                "run_id": run_id,
                "scan_date": scan_date,
                "entry_day": entry_day,
                "candidate_ticker": s.ticker,
                "candidate_rank_static": static_rank_by_ticker.get(s.ticker),
                "composite_score": s.composite_score(),
                "flow_conviction": s.flow_conviction,
                "regime_alignment": s.regime_alignment,
                "narrative_coherence": s.narrative_coherence,
                "scorer_reasoning": s.reasoning,
                "in_top_5": s.ticker in top_5_set,
                "picker_chose": is_picked,
                "picker_runner_up": is_runner,
                "picker_justification": (
                    picker_output.justification
                    if picker_output and (is_picked or is_runner)
                    else None
                ),
                "picker_confidence": (
                    picker_output.confidence
                    if picker_output and (is_picked or is_runner)
                    else None
                ),
                "scorer_prompt_version": SCORER_PROMPT_VERSION,
                "picker_prompt_version": PICKER_PROMPT_VERSION,
                "scorer_model": SCORER_MODEL,
                "picker_model": PICKER_MODEL,
                "composite_weights_json": weights_json,
                "scorer_latency_ms": scorer_latency_ms,
                "picker_latency_ms": picker_latency_ms,
                "created_at": now_ts,
            }
        )

    client = bigquery.Client(project=PROJECT_ID)
    errors = client.insert_rows_json(TABLE_RUNS, rows)
    if errors:
        # Don't raise — picker result already returned to caller; log loudly.
        logger.error(f"signal_ranker_runs insert errors for {run_id}: {errors}")
    else:
        logger.info(f"signal_ranker_runs: wrote {len(rows)} rows for {run_id}")


def render_candidate_for_scorer(c: Candidate) -> str:
    """Render a candidate as a compact JSON-style block for the Scorer prompt.

    Keep deterministic — same input → same string, so traces are comparable.
    """
    fields = c.model_dump(exclude_none=True)
    # Stable key order for trace diffing
    return json.dumps(fields, indent=2, sort_keys=True, default=str)


def render_top_5_for_picker(
    top_5: list[ScorerOutput], candidates_by_ticker: dict[str, Candidate]
) -> str:
    """Render top-5 as a Picker-facing block.

    Includes Scorer reasoning prose (load-bearing per locked decision) AND
    the candidate's enriched fields. Excludes raw rubric scores and composite.
    """
    blocks: list[str] = []
    for idx, s in enumerate(top_5, start=1):
        cand = candidates_by_ticker.get(s.ticker)
        cand_block = render_candidate_for_scorer(cand) if cand else "{}"
        blocks.append(
            f"--- top_5[{idx}] {s.ticker} ---\n"
            f"scorer_reasoning: {s.reasoning}\n"
            f"candidate:\n{cand_block}"
        )
    return "\n\n".join(blocks)


def render_ledger_summary_for_picker(ledger: LedgerSummary) -> str:
    """Render the 14d ledger as a compact block for the Picker prompt."""
    return json.dumps(ledger.model_dump(exclude_none=True), indent=2, sort_keys=True)


def load_prompt(name: str) -> str:
    """Read a prompt file from the prompts/ directory."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "prompts", name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


_CASE_MEMORY_CACHE: str | None = None


def render_case_memory_for_picker() -> str:
    """Assemble the static case-memory block injected into the Picker.

    = quant.md (ledger-independent priors) + exemplars.md (bounded curated cases),
    both generated/maintained under signal-ranker/case_memory/ and deployed with
    the service. Static per deploy, so cached after first read.

    NON-GATING and FAIL-OPEN: any read error returns "" so the Picker still runs
    (it simply sees an empty memory fence). This block is advisory context only.

    NOT leakage: every case is a CLOSED past trade; nothing here is dated relative
    to today's scan_date, and it is read for a *future* contract whose outcome is
    unknown. The live decision is still gated by assert_no_leakage on candidates.
    """
    global _CASE_MEMORY_CACHE
    if _CASE_MEMORY_CACHE is not None:
        return _CASE_MEMORY_CACHE
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cm_dir = os.path.join(here, "case_memory")
    parts: list[str] = []
    for name in ("quant.md", "exemplars.md"):
        try:
            with open(os.path.join(cm_dir, name), "r", encoding="utf-8") as f:
                parts.append(f.read().strip())
        except OSError as e:  # missing file / read error — degrade gracefully
            logger.warning(f"case_memory: could not read {name}: {e}")
    _CASE_MEMORY_CACHE = "\n\n".join(parts)
    return _CASE_MEMORY_CACHE
