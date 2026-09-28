"""Client-side timeout on each tournament LLM attempt (2026-09-28).

The SDK sets no timeout by default. A hung Vertex call could outlast
signal-notifier's 480 s /rank wait and fail the day closed. These tests pin:

1. every attempt carries the JUDGE_CALL_TIMEOUT_S timeout (in ms, per the SDK),
2. JUDGE_CALL_TIMEOUT_S=0 turns it off (the env-var rollback),
3. a timed-out attempt is retried like any other transport error,
4. a stalled BigQuery trace write cannot hold the pick (TRACE_WAIT_S).

    .venv/bin/python -m pytest signal-judge/tests/unit/test_call_timeout.py -q
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types

_JUDGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _JUDGE_ROOT)

# app.agent pulls in google.adk and resolves ADC at import; stub both so the
# module is importable headless (mirrors test_trace_logging).
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

from app import agent, tools  # noqa: E402
from app.schemas import Candidate  # noqa: E402

BATCH = [
    Candidate(ticker="PATH", direction="BULLISH", overnight_score=6),
    Candidate(ticker="TEAM", direction="BULLISH", overnight_score=5),
]
OK_BODY = json.dumps({"picks": ["PATH"], "why": "ok"})


class _Client:
    """Stand-in for genai.Client. Records each config; fails the first N calls."""

    def __init__(self, fail_first: int = 0):
        self.configs = []
        self.fail_first = fail_first

        async def generate_content(**kwargs):
            self.configs.append(kwargs["config"])
            if len(self.configs) <= self.fail_first:
                raise asyncio.TimeoutError()
            return types.SimpleNamespace(text=OK_BODY, usage_metadata=None)

        self.aio = types.SimpleNamespace(
            models=types.SimpleNamespace(generate_content=generate_content)
        )


async def _noop(*_a, **_k):
    return None


def test_each_attempt_carries_the_timeout_in_ms(monkeypatch):
    monkeypatch.setattr(tools, "JUDGE_CALL_TIMEOUT_S", 150)
    client = _Client()

    out = asyncio.run(agent._judge_batch(client, "report", BATCH))

    assert out["picks"] == ["PATH"]
    assert client.configs[0].http_options.timeout == 150_000
    assert client.configs[0].response_mime_type == "application/json"


def test_zero_disables_the_timeout(monkeypatch):
    monkeypatch.setattr(tools, "JUDGE_CALL_TIMEOUT_S", 0)
    client = _Client()

    asyncio.run(agent._judge_batch(client, "report", BATCH))

    assert client.configs[0].http_options is None


def test_a_stalled_trace_write_does_not_hold_the_pick(monkeypatch):
    """BQ streaming outage: the insert retries for minutes. The pick must not wait."""
    import time

    class _StalledLogger:
        def log(self, record):
            time.sleep(1.0)

    monkeypatch.setattr(agent, "_trace_logger", _StalledLogger())
    monkeypatch.setattr(agent, "TraceRecord", lambda **kw: kw)
    monkeypatch.setattr(agent, "TRACE_WAIT_S", 0.05)
    ctx = agent._TraceCtx(run_id="r", scan_date="2026-09-28", seed=1, rnd=1)

    async def timed():
        # Time inside the loop: asyncio.run() joins worker threads at shutdown,
        # which the long-lived server loop never does.
        t0 = time.monotonic()
        res = await agent._judge_batch(_Client(), "report", BATCH, "", ctx)
        return res, time.monotonic() - t0

    out, elapsed = asyncio.run(timed())

    assert out["picks"] == ["PATH"]
    assert elapsed < 0.5


def test_a_timed_out_attempt_is_retried(monkeypatch):
    monkeypatch.setattr(tools, "JUDGE_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(agent.asyncio, "sleep", _noop)
    client = _Client(fail_first=2)

    out = asyncio.run(agent._judge_batch(client, "report", BATCH))

    assert out["picks"] == ["PATH"]
    assert len(client.configs) == 3
