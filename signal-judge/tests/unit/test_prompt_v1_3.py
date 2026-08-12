"""tournament_v1_3 prompt bump tests (2026-08-12).

Discipline mirrors every prior bump (v1 -> v1_1 -> v1_2): the ONLY permitted
changes are the sanctioned sentences. Strip all three additions and the prompt
must be byte-identical to the stored v1_1 golden
(tests/golden/tournament_v1_1_{cull,final}.txt, captured from the pre-edit code).

v1_3 adds the liquidity_floor_restored wall. See
docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md.

    .venv/bin/python -m pytest signal-judge/tests/unit/test_prompt_v1_3.py -q
"""

from __future__ import annotations

import os
import re
import sys
import types

_JUDGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _JUDGE_ROOT)

# app.agent pulls in google.adk and resolves ADC at import; stub both so the
# prompt text is testable headless (the existing smoke test dodges this by only
# importing app.schemas / app.tools).
_adk = types.ModuleType("google.adk")
_adk_agents = types.ModuleType("google.adk.agents")
_adk_models = types.ModuleType("google.adk.models")
_adk_agents.Agent = type("Agent", (), {"__init__": lambda self, **kw: None})
_adk_models.Gemini = type("Gemini", (), {"__init__": lambda self, **kw: None})
_adk.agents, _adk.models = _adk_agents, _adk_models
sys.modules.setdefault("google.adk", _adk)
sys.modules.setdefault("google.adk.agents", _adk_agents)
sys.modules.setdefault("google.adk.models", _adk_models)

import google.auth  # noqa: E402

google.auth.default = lambda *a, **k: (None, "test-project")

import pytest  # noqa: E402

from app import tools  # noqa: E402
from app.agent import STALE_FIELDS_BLOCKLIST, _build_prompt  # noqa: E402
from app.schemas import Candidate  # noqa: E402

# The v1_2 additions, verbatim.
ADD_ZERO_VOLUME_WALL = (
    " An early_volume of 0 means the contract had not printed at all as of the "
    "pick-time read; treat it as untradeable unless no candidate shows prints."
)
ADD_NUMBERS_IN_WHY = (
    ". If liquidity influenced your ranking, the why must state the "
    "early_volume and oi_build values you relied on."
)
# The v1_3 addition, verbatim.
ADD_RESTORED_WALL = (
    " A liquidity_floor_restored of true means the contract FAILED a hard "
    "liquidity floor and is on this slate only so the slate would not be "
    "empty; never rank one above a candidate whose value is false."
)

GOLDEN_DIR = os.path.join(_JUDGE_ROOT, "tests", "golden")

# Must match the fixture the golden was generated from, PLUS the new field. A
# candidate carrying liquidity_floor_restored must not perturb anything else in
# the rendered prompt beyond its own key in the JSON blob (asserted below).
CANDIDATES = [
    Candidate(ticker="AAA", direction="BULLISH", overnight_score=7,
              recommended_contract="O:AAA260918C00055000", early_volume=2045,
              oi_build=2033, expected_liquidity="CLEAN"),
    Candidate(ticker="BBB", direction="BULLISH", overnight_score=5,
              recommended_contract="O:BBB260918C00010000", early_volume=0,
              oi_build=12, expected_liquidity="THIN"),
]
REPORT_MD = "## Report\nVIX 14.2\n"
PRIORS = {"cull": "", "final": "Q1. Prefer liquid contracts."}


def _prompt(kind: str, candidates: list[Candidate] | None = None) -> str:
    return _build_prompt(REPORT_MD, candidates or CANDIDATES, PRIORS[kind])


def _golden(kind: str) -> str:
    with open(os.path.join(GOLDEN_DIR, f"tournament_v1_1_{kind}.txt")) as f:
        return f.read()


@pytest.mark.parametrize("kind", ["cull", "final"])
def test_only_the_sanctioned_sentences_changed(kind):
    """Byte-diff discipline: strip the three additions -> exactly v1_1."""
    stripped = (
        _prompt(kind)
        .replace(ADD_ZERO_VOLUME_WALL, "", 1)
        .replace(ADD_RESTORED_WALL, "", 1)
        .replace(ADD_NUMBERS_IN_WHY, "", 1)
    )
    assert stripped == _golden(kind), (
        "tournament_v1_3 diverges from tournament_v1_1 beyond the three "
        "sanctioned sentences — the bump is no longer surgical."
    )


@pytest.mark.parametrize("kind", ["cull", "final"])
def test_all_additions_present_exactly_once(kind):
    p = _prompt(kind)
    assert p.count(ADD_ZERO_VOLUME_WALL) == 1
    assert p.count(ADD_RESTORED_WALL) == 1
    assert p.count(ADD_NUMBERS_IN_WHY) == 1


def test_zero_wall_follows_the_existing_liquidity_directive():
    """The second wall must sit with the liquidity directive it backstops, not
    float loose in the prompt."""
    p = _prompt("cull")
    anchor = "prefer the one showing real early trading activity."
    assert anchor + ADD_ZERO_VOLUME_WALL in p


def test_restored_wall_follows_the_zero_wall():
    """Both walls guard the same decision; keep them adjacent."""
    assert ADD_ZERO_VOLUME_WALL + ADD_RESTORED_WALL in _prompt("cull")


def test_numbers_in_why_follows_the_json_contract():
    p = _prompt("cull")
    assert '"why":"<one sentence on your #1 pick>"}' + ADD_NUMBERS_IN_WHY in p


def test_restored_flag_reaches_the_model():
    """The whole point of the bump: the flag the notifier computes must survive
    to the rendered prompt. It was popped at the /rank boundary before 08-12 —
    computed correctly, then discarded at the one place it changes an outcome."""
    cands = [
        Candidate(ticker="AAA", direction="BULLISH", overnight_score=7,
                  early_volume=102, liquidity_floor_restored=True),
        Candidate(ticker="BBB", direction="BULLISH", overnight_score=6,
                  early_volume=4668, liquidity_floor_restored=False),
    ]
    p = _prompt("cull", cands)
    assert '"liquidity_floor_restored": true' in p
    assert '"liquidity_floor_restored": false' in p


def test_internal_restore_columns_stay_blocked():
    """The sanctioned alias is on the wire; the RAW notifier columns never are."""
    assert "_print_floor_restored" in STALE_FIELDS_BLOCKLIST
    assert "_floor_failed" in STALE_FIELDS_BLOCKLIST
    assert "liquidity_floor_restored" not in STALE_FIELDS_BLOCKLIST


def test_provenance_bumped():
    """The ledger must show which picks came from which prompt.

    Both constants are env-resolved, so an exported JUDGE_PROMPT_VERSION would
    make this pass trivially against the wrong code default. Fail loudly instead.
    """
    assert "JUDGE_PROMPT_VERSION" not in os.environ, (
        "JUDGE_PROMPT_VERSION is exported in this shell — this test would assert "
        "the env value, not the code default. Clear it and re-run."
    )
    assert "JUDGE_PROMPT_LABEL" not in os.environ
    assert tools.JUDGE_PROMPT_VERSION == 10
    assert tools.JUDGE_PROMPT_LABEL == "tournament_v1_3"


def test_deploy_sh_pins_match_the_code_defaults():
    """deploy.sh --set-env-vars OVERRIDES the code default, so a bump that
    forgets the pin never reaches production. This is a real 2026-08-07 near
    miss, not a hypothetical."""
    with open(os.path.join(_JUDGE_ROOT, "deploy.sh")) as f:
        deploy = f.read()
    version = re.search(r"JUDGE_PROMPT_VERSION=(\d+)", deploy.split("--set-env-vars")[1])
    label = re.search(r"JUDGE_PROMPT_LABEL=([\w.]+)", deploy.split("--set-env-vars")[1])
    assert version and int(version.group(1)) == tools.JUDGE_PROMPT_VERSION
    assert label and label.group(1) == tools.JUDGE_PROMPT_LABEL
