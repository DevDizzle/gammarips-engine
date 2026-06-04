"""Pydantic schemas for V5.4 signal-ranker.

Wire format (RankRequest / RankResponse) and structured agent outputs
(ScorerOutput / PickerOutput).

Locked decisions (2026-05-08, see docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md):
- Composite formula: weighted sum (0.6*flow + 0.25*regime + 0.15*narrative)
- Picker confidence: enum "high" | "medium" | "low"
- Picker input: Scorer reasoning prose only, no raw rubric scores

Schema for the BQ persistence table is in
scripts/ledger_and_tracking/create_signal_ranker_runs.py.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# Composite weights v0 — anchored to literature (Pan-Poteshman 2006, Hu 2014,
# Tetlock 2007). Re-weight after N=30 V5.4 closed trades via IC decomposition.
# Stored alongside each run for time-travel attribution.
COMPOSITE_WEIGHTS: dict[str, float] = {"flow": 0.60, "regime": 0.25, "narrative": 0.15}

# Top-N cut to Picker. ≤5 candidates → all go through.
TOP_N = 5


def composite(flow: int, regime: int, narrative: int) -> float:
    """Weighted-sum composite per locked spec. Inputs are 1-10 ints."""
    w = COMPOSITE_WEIGHTS
    return w["flow"] * flow + w["regime"] * regime + w["narrative"] * narrative


class Candidate(BaseModel):
    """One enriched candidate row passed by signal-notifier.

    Mirrors the relevant subset of `overnight_signals_enriched`. Extra fields
    are tolerated (forward compat) — Scorer prompt only references the keys
    it cares about. All inputs MUST be dated <= scan_date close (leakage
    assertion enforced in tools.assert_no_leakage before scoring).
    """

    model_config = {"extra": "allow"}

    ticker: str
    direction: Literal["BULLISH", "BEARISH"]
    overnight_score: int
    sector: str | None = None

    # V5.3 ranker tier
    static_rank: int | None = None  # SQL ranker position 1..10, None if not ranked

    # Flow features
    call_dollar_volume: float | None = None
    put_dollar_volume: float | None = None
    call_vol_oi_ratio: float | None = None
    put_vol_oi_ratio: float | None = None
    volume_oi_ratio: float | None = None  # focal-strike V/OI

    # Contract
    recommended_contract: str | None = None
    recommended_strike: float | None = None
    recommended_expiration: str | None = None
    recommended_dte: int | None = None
    recommended_mid_price: float | None = None
    recommended_spread_pct: float | None = None
    moneyness_pct: float | None = None

    # Regime context (already on the enriched row)
    vix3m_at_enrich: float | None = None

    # Narrative inputs (already produced by enrichment-trigger)
    catalyst_score: float | None = None
    catalyst_type: str | None = None
    flow_intent: str | None = None
    flow_intent_reasoning: str | None = None
    thesis: str | None = None
    news_summary: str | None = None
    key_headline: str | None = None

    # Risk
    mean_reversion_risk: float | None = None
    move_overdone: bool | None = None
    reversal_probability: float | None = None
    risk_reward_ratio: float | None = None


class LedgerSummary(BaseModel):
    """14d ledger summary for the Picker. signal-notifier computes from
    forward_paper_ledger split by direction AND policy_version."""

    model_config = {"extra": "allow"}

    window_days: int = 14
    closed_trades: int = 0
    by_direction: dict[str, dict[str, Any]] = Field(default_factory=dict)
    by_policy: dict[str, dict[str, Any]] = Field(default_factory=dict)
    notes: str | None = None  # human-readable summary string


class RankRequest(BaseModel):
    scan_date: str  # YYYY-MM-DD ET
    entry_day: str  # YYYY-MM-DD ET (next session, computed by caller)
    candidates: list[Candidate]
    report_md: str  # daily_reports/{scan_date}.markdown
    ledger_summary: LedgerSummary

    @field_validator("candidates")
    @classmethod
    def _at_least_one(cls, v: list[Candidate]) -> list[Candidate]:
        if not v:
            raise ValueError("candidates must be non-empty (gate-cleared upstream)")
        return v


class ScorerOutput(BaseModel):
    """Per-candidate Scorer LLM output. 1-10 bounds enforced via Field constraints."""

    ticker: str
    flow_conviction: int = Field(ge=1, le=10)
    regime_alignment: int = Field(ge=1, le=10)
    narrative_coherence: int = Field(ge=1, le=10)
    reasoning: str = Field(
        description="2-3 sentences explaining the three rubric scores. "
        "This is the ONLY Scorer output the Picker sees — write it as standalone evidence, "
        "not as score-justification."
    )

    def composite_score(self) -> float:
        return composite(self.flow_conviction, self.regime_alignment, self.narrative_coherence)


class PickerOutput(BaseModel):
    """Final ranker output. Must select one ticker from the top-5 set; no abstain.

    LEGACY (pre-judge_v6). Retained for typecheck + replay of pre-collapse runs.
    The live pipeline uses JudgeOutput (single-call collapse, 2026-06-04).
    """

    pick: str  # ticker
    runner_up: str  # ticker (must differ from pick when len(top_5) > 1)
    justification: str = Field(
        description="2-3 sentences explaining why this beat the runner-up. "
        "Reference the Scorer reasoning prose and the daily report; "
        "do NOT recite raw rubric scores (Picker did not see them)."
    )
    confidence: Literal["high", "medium", "low"]


# --- judge_v6: single-call collapse (2026-06-04) ----------------------------
# Scorer + Picker collapsed into one memory-aware judge. See
# docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md.
# The three component scores are preserved (same 0.60/0.25/0.15 weighting) so
# signal_ranker_runs stays one-row-per-candidate and the N=30 IC re-weighting
# still has separable rubric dimensions to work with.


class PerCandidateVerdict(BaseModel):
    """One judge verdict per gated candidate. Maps 1:1 onto the legacy
    ScorerOutput rubric fields for persist_run column stability."""

    ticker: str
    flow_conviction: int = Field(ge=1, le=10)
    regime_alignment: int = Field(ge=1, le=10)
    narrative_coherence: int = Field(ge=1, le=10)
    # The model echoes its own composite for transparency, but persistence and
    # ordering ALWAYS recompute via composite_score() — never trust model math.
    composite: float | None = None
    leakage: bool = False
    reasoning: str = Field(
        description="Standalone 2-3 sentence evidence-based view of THIS candidate "
        "(absolute, not relative to the slate). Top flow datum, contract structure, "
        "bracket hittability, regime/report fit, narrative/memory note. No score recitation."
    )

    def composite_score(self) -> float:
        return composite(self.flow_conviction, self.regime_alignment, self.narrative_coherence)


class JudgeOutput(BaseModel):
    """Single-call judge output: per-candidate verdicts + final selection.

    Two terminal states mirror the legacy RankResponse contract:
    - happy path: ``skip=False``, ``pick``/``runner_up`` populated, confidence set.
    - mass-leakage skip: ``skip=True``, ``skip_reason="mass_leakage"``, pick fields
      empty (``""``), confidence ``None``.
    """

    prompt_version: str = "judge_v6"
    per_candidate: list[PerCandidateVerdict]
    pick: str = ""
    runner_up: str = ""
    justification: str = ""
    confidence: Literal["high", "medium", "low"] | None = None
    skip: bool = False
    skip_reason: str | None = None


class RankResponse(BaseModel):
    """Returned to signal-notifier. Picker output + provenance.

    Two terminal states:
    - happy path: ``skip=False``, ``pick`` and ``runner_up`` populated.
    - mass-leakage skip: ``skip=True``, ``skip_reason="mass_leakage"``, pick
      fields empty. Caller (signal-notifier) must fail-closed in this state.
    """

    pick: str = ""
    runner_up: str = ""
    justification: str = ""
    confidence: Literal["high", "medium", "low"] | None = None
    # judge_v6: per-candidate verdicts (was list[ScorerOutput] pre-collapse).
    # signal-notifier does not iterate this; fast_api_app only reads len().
    scorer_outputs: list[PerCandidateVerdict]
    top_5_tickers: list[str]
    scorer_prompt_version: int
    picker_prompt_version: int
    scorer_model: str
    picker_model: str
    # Bytes of case-memory injected into the judge this run. 0 means the
    # case_memory/ block did not ship — judge_v6 is load-bearing on memory, so
    # run_pipeline fails closed before reaching here; a persisted run always has >0.
    case_memory_bytes: int | None = None
    composite_weights: dict[str, float] = Field(default_factory=lambda: dict(COMPOSITE_WEIGHTS))
    run_id: str  # UUID, persisted to signal_ranker_runs
    scorer_latency_ms: int | None = None
    picker_latency_ms: int | None = None
    dry_run: bool = False
    skip: bool = False
    skip_reason: str | None = None
