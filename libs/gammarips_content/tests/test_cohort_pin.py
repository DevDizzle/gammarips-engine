"""Pin the publishers' mirrored cohort constant to the engine's own.

`gammarips_content.cohort.LIVE_COHORT_START_DATE` is a MIRROR of
`signal-notifier/main.py::LIVE_COHORT_START_DATE`. x-poster and blog-generator
run as separate Cloud Run services and cannot import the notifier, so the value
is re-typed — and re-typed constants drift. That drift IS the 2026-08-07 defect:
`gammarips-mcp` claimed "since 2026-06-26" through two cohort resets and served
a disowned cohort as live receipts, while blog-generator's 30-trade unlock gate
read 30 closes against a repudiated cohort and would have published a
"30 trades in the books" milestone.

This test fails the moment the engine resets its cohort and the publishers are
not updated with it. Precedent: the signal-judge deploy.sh/code-default pin test
added the same day (docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md).

    .venv/bin/python -m pytest libs/gammarips_content/tests/test_cohort_pin.py -q
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gammarips_content import cohort  # noqa: E402

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_NOTIFIER = os.path.join(_REPO_ROOT, "signal-notifier", "main.py")


def _engine_cohort_start() -> str:
    with open(_NOTIFIER) as f:
        src = f.read()
    m = re.search(r'^LIVE_COHORT_START_DATE\s*=\s*"(\d{4}-\d{2}-\d{2})"', src, re.M)
    assert m, "could not find LIVE_COHORT_START_DATE in signal-notifier/main.py"
    return m.group(1)


def test_mirrored_cohort_start_matches_the_engine():
    engine = _engine_cohort_start()
    assert cohort.LIVE_COHORT_START_DATE == engine, (
        f"gammarips_content.cohort says {cohort.LIVE_COHORT_START_DATE}, the engine "
        f"says {engine}. The publishers would report a cohort the engine has moved "
        f"past. Update cohort.py AND redeploy blog-generator + x-poster; the MCP "
        f"repo mirrors this too (src/utils/data.py)."
    )


def test_sql_fragments_carry_the_pinned_date_and_label():
    """The fragments are what actually reach BigQuery — pin those, not just the
    constant they are built from."""
    for frag in (cohort.LIVE_COHORT_SQL, cohort.LIVE_COHORT_SQL_BY_SCAN_DATE):
        assert cohort.LIVE_COHORT_START_DATE in frag
        assert cohort.LIVE_POLICY_VERSION in frag


def test_live_cohort_sql_is_a_conjunction_of_both_halves():
    """A fragment that lost its date half would silently restore the exact bug
    this module exists to prevent."""
    frag = cohort.LIVE_COHORT_SQL
    assert "policy_version" in frag
    assert "entry_timestamp" in frag
    assert "America/New_York" in frag, "cohort membership must be ET-dated"
    assert " AND " in frag


def test_sql_fragments_interpolate_no_caller_input():
    """These are concatenated into SQL without binding, so they must contain
    only module constants — never a placeholder that a caller could fill."""
    for frag in (cohort.LIVE_COHORT_SQL, cohort.LIVE_COHORT_SQL_BY_SCAN_DATE):
        assert "{" not in frag and "}" not in frag
        assert "%s" not in frag and "@" not in frag
