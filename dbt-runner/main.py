"""dbt-runner — Cloud Run service that runs the GammaRips dbt project on a schedule.

Read-only over production: it materializes the semantic layer into the
`profitscout_dbt` dataset and runs the tests. It does NOT touch trading execution
or any source table. BigQuery auth is the Cloud Run default compute SA via ADC
(profiles `prod` target uses method: oauth — no key/secret).

Endpoints (all POST, invoked by Cloud Scheduler with OIDC; not public):
  POST /            -> dbt deps && dbt build   (models + tests, DAG order)
  POST /freshness   -> dbt source freshness
  GET  /healthz     -> liveness

NOT DEPLOYED. Draft pending the first live `dbt build` + a gammarips-review pass.
"""

import os
import subprocess

from flask import Flask, jsonify

app = Flask(__name__)

DBT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbt")
DBT_TARGET = os.environ.get("DBT_TARGET", "prod")
DBT_TIMEOUT_S = int(os.environ.get("DBT_TIMEOUT_S", "1800"))


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
    # `dbt source freshness` exits 1 when a warn/error threshold trips — that's a
    # signal, not a service failure, so we always return 200 with the report.
    rc, out, err = _run_dbt(["source", "freshness"])
    return jsonify(status="ok" if rc == 0 else "stale", rc=rc, stdout=out[-8000:]), 200


@app.get("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
