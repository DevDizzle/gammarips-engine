"""Unit smoke tests for V5.4 signal-ranker deterministic helpers.

Covers what the EXEC-PLAN Phase 2 acceptance calls out:
- ScorerOutput enforces 1-10 bounds via Pydantic Field constraints
- composite math (weighted sum) returns the expected values per locked weights
- take_top_n sorts deterministically including tie-breaks
- assert_no_leakage rejects post-scan-date fields and outcome-side keys

No live BigQuery / Vertex AI in these tests — pure functions only.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import (
    COMPOSITE_WEIGHTS,
    TOP_N,
    Candidate,
    JudgeOutput,
    PerCandidateVerdict,
    PickerOutput,
    ScorerOutput,
    composite,
)
from app.tools import assert_no_leakage, take_top_n


# -- ScorerOutput bounds -----------------------------------------------------


def _scorer(ticker: str, flow: int, regime: int, narrative: int, reasoning: str = "ok") -> ScorerOutput:
    return ScorerOutput(
        ticker=ticker,
        flow_conviction=flow,
        regime_alignment=regime,
        narrative_coherence=narrative,
        reasoning=reasoning,
    )


def test_scorer_output_accepts_in_range():
    s = _scorer("AAA", 1, 5, 10)
    assert s.flow_conviction == 1
    assert s.regime_alignment == 5
    assert s.narrative_coherence == 10


@pytest.mark.parametrize(
    "field,bad",
    [
        ("flow_conviction", 0),
        ("flow_conviction", 11),
        ("regime_alignment", 0),
        ("regime_alignment", 11),
        ("narrative_coherence", -3),
        ("narrative_coherence", 99),
    ],
)
def test_scorer_output_rejects_out_of_range(field: str, bad: int):
    kwargs = {"ticker": "AAA", "flow_conviction": 5, "regime_alignment": 5,
              "narrative_coherence": 5, "reasoning": "x"}
    kwargs[field] = bad
    with pytest.raises(ValidationError):
        ScorerOutput(**kwargs)


# -- Composite math ----------------------------------------------------------


def test_composite_weights_sum_to_one():
    assert abs(sum(COMPOSITE_WEIGHTS.values()) - 1.0) < 1e-9


def test_composite_known_values():
    # 10/3/3 → 0.6*10 + 0.25*3 + 0.15*3 = 6 + 0.75 + 0.45 = 7.20
    assert composite(10, 3, 3) == pytest.approx(7.20)
    # 7/7/7 → 7 (any equal vector returns the equal value)
    assert composite(7, 7, 7) == pytest.approx(7.00)
    # 10/3/3 must beat 7/7/7 — flow dominates by design (locked spec)
    assert composite(10, 3, 3) > composite(7, 7, 7)


def test_composite_via_method():
    assert _scorer("X", 10, 3, 3).composite_score() == pytest.approx(7.20)


# -- take_top_n --------------------------------------------------------------


def test_take_top_n_basic_ordering():
    s = [
        _scorer("AAA", 5, 5, 5),
        _scorer("BBB", 9, 9, 9),
        _scorer("CCC", 1, 1, 1),
    ]
    out = take_top_n(s, n=3)
    assert [x.ticker for x in out] == ["BBB", "AAA", "CCC"]


def test_take_top_n_truncates_to_n():
    s = [_scorer(f"T{i}", 10 - i, 5, 5) for i in range(10)]
    out = take_top_n(s, n=TOP_N)
    assert len(out) == TOP_N
    # T0 has flow=10 (highest composite), T1=9, ..., T4=6
    assert [x.ticker for x in out] == ["T0", "T1", "T2", "T3", "T4"]


def test_take_top_n_short_list_pass_through():
    s = [_scorer("AAA", 5, 5, 5), _scorer("BBB", 7, 7, 7)]
    out = take_top_n(s, n=TOP_N)
    assert [x.ticker for x in out] == ["BBB", "AAA"]


def test_take_top_n_single_candidate():
    """Degenerate case: only one candidate scored. Picker prompt explicitly
    handles this (picker_v1.md:33), so take_top_n must pass it through cleanly."""
    s = [_scorer("ONLY", 7, 6, 5)]
    out = take_top_n(s, n=TOP_N)
    assert len(out) == 1
    assert out[0].ticker == "ONLY"


def test_take_top_n_empty_list():
    """Defensive: zero scorer outputs returns empty top-5. The pipeline catches
    this upstream (raises scorer_all_failed) but take_top_n itself must not crash."""
    out = take_top_n([], n=TOP_N)
    assert out == []


def test_take_top_n_tiebreak_flow_then_ticker():
    # Same composite (7.0): all 7/7/7 vs 10/3/3 — 10/3/3 wins on composite.
    # Then 7/7/7 across multiple tickers tie on composite & flow → ticker A→Z.
    s = [
        _scorer("ZED", 7, 7, 7),
        _scorer("ABC", 7, 7, 7),
        _scorer("MID", 7, 7, 7),
        _scorer("DOMINANT", 10, 3, 3),  # composite 7.20 > 7.00
    ]
    out = take_top_n(s, n=4)
    assert [x.ticker for x in out] == ["DOMINANT", "ABC", "MID", "ZED"]


def test_take_top_n_tiebreak_flow_first():
    # Two with composite 6.5: flow=10/regime=2/narrative=0 → wait that's invalid.
    # Use composite 7.0 from different vectors to test the flow tiebreaker.
    # 7/7/7 = 7.0; 10/2/2 = 6.30 (different). Build true ties on composite:
    # 8/4/4 = 0.6*8+0.25*4+0.15*4 = 4.8+1.0+0.6 = 6.4
    # 7/7/2 = 0.6*7+0.25*7+0.15*2 = 4.2+1.75+0.3 = 6.25 (no tie)
    # Easier: same vector, different tickers — already covered.
    # For flow-tiebreak: same composite, different flow.
    # 4/10/10 = 0.6*4+0.25*10+0.15*10 = 2.4+2.5+1.5 = 6.4
    # 8/4/4   = 6.4 → flow tie-break: 8 beats 4
    s = [
        _scorer("LOWFLOW", 4, 10, 10),  # composite 6.4
        _scorer("HIFLOW", 8, 4, 4),    # composite 6.4, higher flow
    ]
    out = take_top_n(s, n=2)
    assert [x.ticker for x in out] == ["HIFLOW", "LOWFLOW"]


# -- Leakage assertion -------------------------------------------------------


def _candidate(**overrides) -> Candidate:
    base = {"ticker": "AAA", "direction": "BULLISH", "overnight_score": 7}
    base.update(overrides)
    return Candidate(**base)


def test_leakage_clean_candidate_passes():
    c = _candidate(catalyst_score=0.8, thesis="bull thesis")
    assert_no_leakage("2026-05-08", c)  # no raise


def test_leakage_outcome_field_blocks():
    # Pydantic `extra=allow` lets us inject arbitrary post-scan field names.
    c = _candidate(realized_pnl_pct=0.42)
    with pytest.raises(ValueError, match="leakage_block"):
        assert_no_leakage("2026-05-08", c)


def test_leakage_exit_field_blocks():
    c = _candidate(exit_price=12.50)
    with pytest.raises(ValueError, match="leakage_block"):
        assert_no_leakage("2026-05-08", c)


def test_leakage_winner_flag_blocks():
    c = _candidate(winner=True)
    with pytest.raises(ValueError, match="leakage_block"):
        assert_no_leakage("2026-05-08", c)


def test_leakage_future_dated_field_blocks():
    # A datetime field whose date is post-scan_date is a leakage bug.
    future = datetime(2026, 5, 20, tzinfo=timezone.utc)
    c = _candidate(some_dt=future)
    with pytest.raises(ValueError, match="leakage_block"):
        assert_no_leakage("2026-05-08", c)


def test_leakage_same_day_field_passes():
    same = date(2026, 5, 8)
    c = _candidate(some_date=same)
    assert_no_leakage("2026-05-08", c)  # no raise


# -- PickerOutput shape ------------------------------------------------------


def test_picker_output_confidence_enum():
    p = PickerOutput(pick="A", runner_up="B", justification="x", confidence="high")
    assert p.confidence == "high"


def test_picker_output_rejects_freeform_confidence():
    with pytest.raises(ValidationError):
        PickerOutput(pick="A", runner_up="B", justification="x", confidence="0.74")  # type: ignore


# -- judge_v6: PerCandidateVerdict / JudgeOutput -----------------------------


def _verdict(ticker: str, flow: int, regime: int, narrative: int, leakage: bool = False) -> PerCandidateVerdict:
    return PerCandidateVerdict(
        ticker=ticker,
        flow_conviction=flow,
        regime_alignment=regime,
        narrative_coherence=narrative,
        leakage=leakage,
        reasoning="standalone view",
    )


def test_verdict_bounds_and_composite_match_legacy_scorer():
    v = _verdict("AAA", 10, 3, 3)
    # Same 0.60/0.25/0.15 weighting as the legacy ScorerOutput — cohort comparability.
    assert v.composite_score() == pytest.approx(7.20)
    assert v.composite_score() == _scorer("AAA", 10, 3, 3).composite_score()


@pytest.mark.parametrize("field,bad", [("flow_conviction", 0), ("regime_alignment", 11), ("narrative_coherence", -1)])
def test_verdict_rejects_out_of_range(field: str, bad: int):
    kwargs = {"ticker": "AAA", "flow_conviction": 5, "regime_alignment": 5,
              "narrative_coherence": 5, "reasoning": "x"}
    kwargs[field] = bad
    with pytest.raises(ValidationError):
        PerCandidateVerdict(**kwargs)


def test_take_top_n_works_on_verdicts():
    """take_top_n is duck-typed (composite_score/flow_conviction/ticker) — the
    judge_v6 path reuses it over PerCandidateVerdict for in_top_5 + ordering."""
    vs = [_verdict("AAA", 5, 5, 5), _verdict("BBB", 9, 9, 9), _verdict("CCC", 1, 1, 1)]
    out = take_top_n(vs, n=3)
    assert [x.ticker for x in out] == ["BBB", "AAA", "CCC"]


def test_judge_output_happy_path():
    j = JudgeOutput(
        per_candidate=[_verdict("AAA", 8, 7, 6), _verdict("BBB", 5, 5, 5)],
        pick="AAA",
        runner_up="BBB",
        justification="AAA has cleaner OTM structure",
        confidence="high",
    )
    assert j.prompt_version == "judge_v6"
    assert j.skip is False
    assert j.skip_reason is None


def test_judge_output_mass_leakage_skip_shape():
    """Skip state: empty pick/runner_up, null confidence, skip_reason set."""
    j = JudgeOutput(
        per_candidate=[_verdict("AAA", 1, 1, 1, leakage=True)],
        skip=True,
        skip_reason="mass_leakage",
    )
    assert j.pick == "" and j.runner_up == ""
    assert j.confidence is None
    assert all(v.leakage for v in j.per_candidate)
