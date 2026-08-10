"""dbt-runner — Cloud Run service that runs the GammaRips dbt project on a schedule.

Read-only over production: it materializes the semantic layer into the
`profitscout_dbt` dataset and runs the tests. It does NOT touch trading execution
or any source table. BigQuery auth is the Cloud Run default compute SA via ADC
(profiles `prod` target uses method: oauth — no key/secret).

Endpoints (all POST, invoked by Cloud Scheduler with OIDC; not public):
  POST /            -> dbt deps && dbt build   (models + tests, DAG order)
  POST /freshness   -> dbt source freshness; 500 on an error_after breach or a
                       database error so the Scheduler job goes red (2026-08-07)
  POST /digest      -> daily operator health email (2026-08-07); freshness +
                       collection coverage + job health + life surface
  GET  /healthz     -> liveness

The digest is why this service mounts Mailgun secrets — see digest.py. It stays
read-only over production: it queries and emails, it never writes.

DEPLOYED and cron'd daily: Cloud Scheduler `dbt-daily-build` -> POST / and
`dbt-source-freshness` -> POST /freshness (verified live 2026-07-28).
"""

import logging
import os
import re
import subprocess

from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DBT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbt")
DBT_TARGET = os.environ.get("DBT_TARGET", "prod")
DBT_TIMEOUT_S = int(os.environ.get("DBT_TIMEOUT_S", "1800"))

# dbt log lines look like:
#   "12:00:01  3 of 13 PASS freshness of profit_scout.overnight_signals ... [PASS in 1.2s]"
#   "12:00:01 10 of 13 ERROR freshness of profit_scout.signal_performance . [ERROR in 0.4s]"
_FRESHNESS_LINE = re.compile(r"\b(?P<state>PASS|WARN|ERROR|SKIP)\s+freshness of\s+(?P<source>\S+)")


def _summarize_freshness(out: str) -> dict:
    """Reduce the dbt log to {source: PASS|WARN|ERROR|SKIP} so the verdict is
    readable without scrolling 8KB of stdout."""
    return {m.group("source"): m.group("state") for m in _FRESHNESS_LINE.finditer(out)}


def _run_dbt(args):
    """Run a dbt subcommand in the vendored project. Returns (rc, stdout, stderr)."""
    cmd = ["dbt", *args, "--profiles-dir", ".", "--target", DBT_TARGET, "--no-use-colors"]
    proc = subprocess.run(
        cmd, cwd=DBT_DIR, capture_output=True, text=True, timeout=DBT_TIMEOUT_S
    )
    return proc.returncode, proc.stdout, proc.stderr


@app.post("/")
def build():
    rc, out, err = _run_dbt(["deps"])
    if rc != 0:
        return jsonify(status="error", step="deps", stdout=out[-4000:], stderr=err[-2000:]), 500

    rc, out, err = _run_dbt(["build", "--no-partial-parse"])
    ok = rc == 0
    return (
        jsonify(status="success" if ok else "error", step="build",
                stdout=out[-8000:], stderr=err[-2000:]),
        200 if ok else 500,
    )


@app.post("/freshness")
def freshness():
    """The pipeline's staleness canary.

    HISTORY (2026-08-07): this endpoint used to return 200 unconditionally, on
    the reasoning that "a tripped threshold is a signal, not a service failure."
    The effect was that Cloud Scheduler recorded a green run no matter what,
    nobody read the response body, and the canary became structurally incapable
    of alerting — `underlying_daily_bars` went 37 days stale and the
    `signal_performance` check hard-errored for 10 days, both invisibly. A
    canary that cannot go red is not a canary.

    Now: rc != 0 (an `error_after` breach or a database error) returns 500, so
    the `dbt-source-freshness` job goes red in Cloud Scheduler. That job has
    retryCount 0, so a red run costs exactly one failed attempt, not a retry
    storm. A `warn_after` breach leaves rc == 0 and still returns 200 — every
    weekday-written source reads ~60h old at Monday 07:00 ET, so warns must
    never page or the canary gets muted for crying weekly.
    """
    rc, out, err = _run_dbt(["source", "freshness"])
    states = _summarize_freshness(out)
    not_fresh = {s: st for s, st in states.items() if st in ("ERROR", "WARN")}
    payload = {
        "status": "ok" if rc == 0 else "stale",
        "rc": rc,
        "sources": states,
        "not_fresh": not_fresh,
        "stdout": out[-8000:],
        # stderr matters most in exactly the case this 500 exists to surface —
        # dbt dying before the freshness DAG runs (parse / connection error)
        # puts its message here and leaves `sources` empty. `/` already returns
        # it; omitting it here left the responder with nothing actionable.
        "stderr": err[-2000:],
    }
    if rc != 0:
        # No parsed states means dbt died before the freshness DAG ran (parse or
        # connection error) — say so rather than implying every source is fine.
        detail = not_fresh or states or "dbt failed before any source was checked"
        logger.error("dbt source freshness FAILED (rc=%s): %s", rc, detail)
        return jsonify(payload), 500
    if not_fresh:
        logger.warning("dbt source freshness passed with warnings: %s", not_fresh)
    return jsonify(payload), 200


@app.post("/digest")
def digest():
    """Daily operator health digest — the PUSH half of the freshness story.

    /freshness going red (2026-08-07) made staleness detectable, but only to
    someone who opens the Cloud Scheduler console. This emails one readable
    artifact every weekday morning so the operator does not have to go look.

    Runs the freshness check once per request and hands that payload to the
    digest builder, so nothing WITHIN a digest can disagree with itself. Note
    this is a SECOND, independent dbt run ~15 min after the 07:00
    `dbt-source-freshness` job — the two can legitimately differ if a threshold
    is crossed between them or one hits a transient error. That is the accepted
    cost of keeping the jobs separate so they fail independently.

    Always returns 200 when the digest was assembled and sent — a digest whose
    content says ATTENTION is a successful digest. It returns 500 only when the
    email could not be SENT, because an undelivered health report is the one
    failure that leaves the operator blind again, which is the whole thing this
    exists to prevent. Body (optional): {"send": false} to render without
    emailing (used by the post-deploy smoke test).
    """
    from flask import request

    import digest as digest_mod

    send = (request.get_json(silent=True) or {}).get("send", True)
    rc, out, err = _run_dbt(["source", "freshness"])
    states = _summarize_freshness(out)
    payload = {
        "rc": rc, "sources": states, "stderr": err[-2000:],
        "not_fresh": {s: st for s, st in states.items() if st in ("ERROR", "WARN")},
    }
    result = digest_mod.build_and_send(payload, send=send)
    html = result.pop("html", "")
    if send and result.get("sent") is False:
        logger.error("digest assembled but delivery FAILED: %s", result)
        return jsonify(status="error", reason="email_send_failed", **result), 500
    logger.info("digest %s: %s", result["overall"], result["sections"])
    return jsonify(status="success", **result,
                   **({"html": html} if not send else {})), 200


@app.get("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
