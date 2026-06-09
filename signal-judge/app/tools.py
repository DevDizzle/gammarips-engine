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
    JudgeOutput,
    LedgerSummary,
    PerCandidateVerdict,
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
# NOTE: inert under judge_v6 (single fused call has no per-candidate fanout);
# the partial-failure tolerance it bought is re-acquired via JUDGE_MAX_ATTEMPTS
# bounded retry in agent.run_judge. Kept for legacy code paths / replays.
MIN_SCORER_SUCCESS_FRAC = float(os.getenv("MIN_SCORER_SUCCESS_FRAC", "0.5"))

# --- judge_v6 single-call collapse (2026-06-04) -----------------------------
# One memory-aware judge replaces the Scorer fanout + Picker. The integer
# version 6 is mirrored into BOTH scorer_prompt_version and picker_prompt_version
# in signal_ranker_runs (mode=REQUIRED columns can't be nulled), so the
# post-collapse cohort is cleanly separable from the v5 two-stage cohort.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", PICKER_MODEL)
# version 7 = bracket tournament (2026-06-04); 6 = judge_v6 single call; 5 = two-stage.
# Mirrored into BOTH scorer_/picker_prompt_version (REQUIRED cols) so cohorts stay separable.
JUDGE_PROMPT_VERSION = int(os.getenv("JUDGE_PROMPT_VERSION", "8"))
JUDGE_PROMPT_LABEL = os.getenv("JUDGE_PROMPT_LABEL", "tournament_v1")
# Bounded retry for the single fused call — one malformed structured output no
# longer forfeits the whole slate (replaces the gather+MIN_SCORER_SUCCESS_FRAC
# partial-failure tolerance lost in the collapse).
JUDGE_MAX_ATTEMPTS = int(os.getenv("JUDGE_MAX_ATTEMPTS", "3"))


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
    judge_output: JudgeOutput,
    judge_latency_ms: int | None,
) -> None:
    """Write one row per (run_id, candidate_ticker) to signal_ranker_runs.

    judge_v6 single-call shape (2026-06-04). One row per ``per_candidate``
    verdict, preserving the one-row-per-candidate denominator the eval depends on.

    Column mapping (the BQ DDL is UNCHANGED — scorer/picker columns are
    mode=REQUIRED and cannot be nulled, so the single judge is MIRRORED into
    both): rubric/composite/scorer_reasoning <- per-candidate verdict;
    picker_chose/picker_runner_up/justification/confidence <- JudgeOutput
    selection; *_prompt_version=JUDGE_PROMPT_VERSION (6) and *_model=JUDGE_MODEL
    in BOTH columns so the post-collapse cohort is cleanly separable. The single
    judge latency lands in scorer_latency_ms; picker_latency_ms is NULL.

    ``judge_output.skip`` (mass-leakage) writes the audit trail with
    picker_chose/picker_runner_up all False and justification/confidence NULL.
    No-op on DRY_RUN=true (signal-notifier still gets the response).
    """
    if DRY_RUN:
        logger.info(f"DRY_RUN=true — skipping signal_ranker_runs write for {run_id}")
        return

    static_rank_by_ticker: dict[str, int | None] = {
        c.ticker: c.static_rank for c in candidates
    }
    verdicts = judge_output.per_candidate
    # in_top_5 keeps its meaning (was a finalist) on fat slates via the same
    # deterministic composite ordering the legacy two-stage used.
    top_set = {v.ticker for v in take_top_n(verdicts)}
    skipped = judge_output.skip
    pick = None if skipped else judge_output.pick
    runner_up = None if skipped else judge_output.runner_up
    weights_json = json.dumps(COMPOSITE_WEIGHTS)
    now_ts = datetime.now(timezone.utc).isoformat()

    rows: list[dict[str, Any]] = []
    for v in verdicts:
        is_picked = (not skipped) and v.ticker == pick
        is_runner = (not skipped) and v.ticker == runner_up and v.ticker != pick
        rows.append(
            {
                "run_id": run_id,
                "scan_date": scan_date,
                "entry_day": entry_day,
                "candidate_ticker": v.ticker,
                "candidate_rank_static": static_rank_by_ticker.get(v.ticker),
                "composite_score": v.composite_score(),  # recomputed, never trust model echo
                "flow_conviction": v.flow_conviction,
                "regime_alignment": v.regime_alignment,
                "narrative_coherence": v.narrative_coherence,
                "scorer_reasoning": v.reasoning,
                "in_top_5": v.ticker in top_set,
                "picker_chose": is_picked,
                "picker_runner_up": is_runner,
                "picker_justification": (
                    judge_output.justification if (is_picked or is_runner) else None
                ),
                "picker_confidence": (
                    judge_output.confidence if (is_picked or is_runner) else None
                ),
                "scorer_prompt_version": JUDGE_PROMPT_VERSION,
                "picker_prompt_version": JUDGE_PROMPT_VERSION,
                "scorer_model": JUDGE_MODEL,
                "picker_model": JUDGE_MODEL,
                "composite_weights_json": weights_json,
                "scorer_latency_ms": judge_latency_ms,
                "picker_latency_ms": None,
                "created_at": now_ts,
            }
        )

    client = bigquery.Client(project=PROJECT_ID)
    errors = client.insert_rows_json(TABLE_RUNS, rows)
    if errors:
        # Don't raise — judge result already returned to caller; log loudly.
        logger.error(f"signal_ranker_runs insert errors for {run_id}: {errors}")
    else:
        logger.info(f"signal_ranker_runs: wrote {len(rows)} rows for {run_id}")


def persist_tournament_run(
    *,
    run_id: str,
    scan_date: str,
    entry_day: str,
    candidates: list[Candidate],
    winner: str,
    runner_up: str,
    why: str,
    confidence: str,
    advancement: dict[str, int],
    latency_ms: int | None,
) -> None:
    """Write the bracket result to signal_ranker_runs (DDL unchanged).

    The tournament has no per-candidate rubric scores, so the REQUIRED rubric
    columns are populated with an ADVANCEMENT proxy (how far each ticker got in
    the bracket: round1 win=6, round2=9, final/winner=10) — flow/regime/narrative
    all carry that proxy. version 7 (`tournament_v1`) keeps the cohort separable.
    We persist only the finalists + winner + runner_up (the round-1 losers don't
    get a row — the tournament didn't evaluate them on the merits).
    """
    if DRY_RUN:
        logger.info(f"DRY_RUN=true — skipping signal_ranker_runs write for {run_id}")
        return

    def _score(rounds: int) -> int:
        return max(1, min(10, 3 + 3 * rounds))  # 0->3, 1->6, 2->9, 3+->10

    static_rank_by_ticker = {c.ticker: getattr(c, "static_rank", None) for c in candidates}
    keep = {t for t, r in advancement.items() if r >= 1} | {winner, runner_up}
    weights_json = json.dumps(COMPOSITE_WEIGHTS)
    now_ts = datetime.now(timezone.utc).isoformat()

    # Bug #14: in_top_5 must mean a GENUINE top-5, not "advanced past round 1"
    # (which flagged 9-20 rows true and made any top-5 eval meaningless). Rank the
    # kept tickers by advancement (rounds reached desc, then ticker) and flag only
    # the first 5 — the winner sorts first via a synthetic high advancement.
    top_5 = set(
        sorted(
            keep,
            key=lambda t: (-(99 if t == winner else advancement.get(t, 0)), t),
        )[:5]
    )

    rows: list[dict[str, Any]] = []
    for t in keep:
        rnd = advancement.get(t, 0)
        sc = 10 if t == winner else _score(rnd)
        is_pick = t == winner
        is_runner = t == runner_up and t != winner
        rows.append(
            {
                "run_id": run_id,
                "scan_date": scan_date,
                "entry_day": entry_day,
                "candidate_ticker": t,
                "candidate_rank_static": static_rank_by_ticker.get(t),
                "composite_score": float(sc),
                "flow_conviction": sc,
                "regime_alignment": sc,
                "narrative_coherence": sc,
                "scorer_reasoning": why if is_pick else None,
                "in_top_5": t in top_5,
                "picker_chose": is_pick,
                "picker_runner_up": is_runner,
                "picker_justification": why if (is_pick or is_runner) else None,
                "picker_confidence": confidence if (is_pick or is_runner) else None,
                "scorer_prompt_version": JUDGE_PROMPT_VERSION,
                "picker_prompt_version": JUDGE_PROMPT_VERSION,
                "scorer_model": JUDGE_MODEL,
                "picker_model": JUDGE_MODEL,
                "composite_weights_json": weights_json,
                "scorer_latency_ms": latency_ms,
                "picker_latency_ms": None,
                "created_at": now_ts,
            }
        )

    client = bigquery.Client(project=PROJECT_ID)
    errors = client.insert_rows_json(TABLE_RUNS, rows)
    if errors:
        logger.error(f"signal_ranker_runs insert errors for {run_id}: {errors}")
    else:
        logger.info(f"signal_ranker_runs: wrote {len(rows)} tournament rows for {run_id}")


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


_QUANT_MD_CACHE: str | None = None


def load_quant_md() -> str:
    """quant.md ONLY — the hand-authored, ledger-independent priors. Deliberately
    excludes exemplars.md (those are generated from a single-regime backfill).

    Injected into the tournament's FINAL round only (the championship batch that
    crowns each bracket winner), so the ~10-finalist deep decision weighs the
    rulebook while the cheap early cull rounds stay lean. Cached per deploy.

    NON-GATING and FAIL-OPEN: any read error returns "" so the picker still runs.
    NOT leakage: quant.md contains no point-in-time data — only durable priors.
    """
    global _QUANT_MD_CACHE
    if _QUANT_MD_CACHE is not None:
        return _QUANT_MD_CACHE
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "case_memory", "quant.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _QUANT_MD_CACHE = f.read().strip()
    except OSError as e:
        logger.warning(f"load_quant_md: could not read quant.md: {e}")
        _QUANT_MD_CACHE = ""
    return _QUANT_MD_CACHE
