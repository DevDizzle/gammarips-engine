"""Cost/usage trace rows for the bracket tournament (2026-08-17).

The tournament was the last uninstrumented LLM caller in the pipeline: it wrote
no `llm_traces_v1` rows, so "what does the daily pick cost" could only be
answered from Cloud Monitoring token counts. These tests pin the three
properties that make the row trustworthy and harmless:

1. thinking tokens are folded into output_tokens (they BILL as output, and here
   they are ~99% of it — the same trap enrichment hit on 2026-06-12),
2. every attempt is logged, failures included, because a retry bills too,
3. a broken trace logger can never break a pick.

    .venv/bin/python -m pytest signal-judge/tests/unit/test_trace_logging.py -q
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types

_JUDGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_JUDGE_ROOT, ".."))
sys.path.insert(0, _JUDGE_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "libs", "trace_logger"))

# app.agent pulls in google.adk and resolves ADC at import; stub both so the
# module is importable headless (mirrors test_prompt_v1_3).
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
from trace_logger import TraceRecord  # noqa: E402  — the REAL record shape

from app import agent, tools  # noqa: E402
from app.schemas import Candidate  # noqa: E402

CTX = agent._TraceCtx(run_id="v5_4_2026-08-14_abc123", scan_date="2026-08-14", seed=7, rnd=2)
BATCH = [
    Candidate(ticker="PATH", direction="BULLISH", overnight_score=6),
    Candidate(ticker="TEAM", direction="BULLISH", overnight_score=5),
]


class _Recorder:
    """Stands in for TraceLogger. Records what the service would have written."""

    def __init__(self, boom: bool = False):
        self.rows: list[TraceRecord] = []
        self.boom = boom

    def log(self, record: TraceRecord) -> None:
        if self.boom:
            raise RuntimeError("BigQuery is down")
        self.rows.append(record)


class _Usage:
    prompt_token_count = 14_300
    candidates_token_count = 90
    thoughts_token_count = 3_600


class _Response:
    def __init__(self, text: str, usage: object | None = _Usage()):
        self.text = text
        self.usage_metadata = usage


def _client(*, response=None, error: Exception | None = None):
    """Minimal stand-in for genai.Client — only .aio.models.generate_content."""

    async def generate_content(**kwargs):
        if error is not None:
            raise error
        return response

    models = types.SimpleNamespace(generate_content=generate_content)
    return types.SimpleNamespace(aio=types.SimpleNamespace(models=models))


@pytest.fixture
def recorder(monkeypatch):
    rec = _Recorder()
    monkeypatch.setattr(agent, "_trace_logger", rec)
    monkeypatch.setattr(agent, "TraceRecord", TraceRecord)
    return rec


def test_ok_call_logs_one_row_with_thinking_folded_in(recorder):
    body = json.dumps({"picks": ["PATH"], "why": "early_volume 2045"})
    out = asyncio.run(
        agent._judge_batch(_client(response=_Response(body)), "report", BATCH, "", CTX)
    )

    assert out["picks"] == ["PATH"]
    assert len(recorder.rows) == 1
    row = recorder.rows[0]
    assert row.status == "ok"
    assert row.service == "signal_judge"
    assert row.model_id == agent.JUDGE_MODEL
    assert row.run_id == CTX.run_id and row.scan_date == CTX.scan_date
    assert row.input_tokens == 14_300
    # 90 answer tokens + 3600 thinking tokens. Logging 90 would understate the
    # bill ~40x on this call.
    assert row.output_tokens == 3_690
    assert "seed=7" in row.inputs_raw and "round=2" in row.inputs_raw
    assert "attempt=1" in row.inputs_raw and "PATH,TEAM" in row.inputs_raw


def test_every_failed_attempt_is_logged(monkeypatch, recorder):
    monkeypatch.setattr(tools, "JUDGE_MAX_ATTEMPTS", 2)
    monkeypatch.setattr(agent.asyncio, "sleep", lambda *_a, **_k: _noop())

    out = asyncio.run(
        agent._judge_batch(_client(error=RuntimeError("503 backend")), "report", BATCH, "", CTX)
    )

    assert out == {"picks": [], "why": ""}
    assert [r.status for r in recorder.rows] == ["api_error", "api_error"]
    assert "attempt=1" in recorder.rows[0].inputs_raw
    assert "attempt=2" in recorder.rows[1].inputs_raw
    assert recorder.rows[0].input_tokens is None  # no usage on a transport failure


def test_off_list_pick_logs_a_parse_error(monkeypatch, recorder):
    monkeypatch.setattr(tools, "JUDGE_MAX_ATTEMPTS", 1)
    body = json.dumps({"picks": ["NVDA"], "why": "not in this batch"})

    out = asyncio.run(
        agent._judge_batch(_client(response=_Response(body)), "report", BATCH, "", CTX)
    )

    assert out == {"picks": [], "why": ""}
    assert [r.status for r in recorder.rows] == ["parse_error"]


def test_a_broken_trace_logger_never_breaks_the_pick(monkeypatch):
    monkeypatch.setattr(agent, "_trace_logger", _Recorder(boom=True))
    monkeypatch.setattr(agent, "TraceRecord", TraceRecord)
    body = json.dumps({"picks": ["TEAM"], "why": "ok"})

    out = asyncio.run(
        agent._judge_batch(_client(response=_Response(body)), "report", BATCH, "", CTX)
    )

    assert out["picks"] == ["TEAM"]


def test_no_context_means_no_row(recorder):
    """_judge_batch is also called from replay/backfill scripts with no run_id."""
    body = json.dumps({"picks": ["PATH"], "why": "ok"})

    out = asyncio.run(agent._judge_batch(_client(response=_Response(body)), "report", BATCH))

    assert out["picks"] == ["PATH"]
    assert recorder.rows == []


async def _noop():
    return None
