import logging
import os
from flask import Flask, jsonify, request
from src.enrichment.core.pipelines import overnight_scanner, universe_refresh

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/scan", methods=["POST"])
def run_scanner():
    """Trigger the overnight scanner pipeline."""
    try:
        results = overnight_scanner.run_pipeline()
        count = len(results) if results else 0
        return jsonify({"status": "success", "signals_found": count}), 200
    except Exception as e:
        # Unauthenticated service: never echo exception text into the response —
        # library errors can embed request internals (a header error leaked the
        # Polygon key on 2026-08-05). Details go to logs only.
        logger.error("Overnight scanner failed: %s", e, exc_info=True)
        return jsonify({"status": "error"}), 500


@app.route("/refresh_universe", methods=["POST"])
def run_universe_refresh():
    """Regenerate the scan-universe file (weekly Cloud Scheduler; ~9 min)."""
    body = request.get_json(silent=True) or {}
    try:
        summary = universe_refresh.run_refresh(
            dry_run=bool(body.get("dry_run", False)),
            allow_shrink=bool(body.get("allow_shrink", False)),
            allow_growth=bool(body.get("allow_growth", False)),
        )
        return jsonify({"status": "success", **summary}), 200
    except Exception as e:
        # Surface only OUR guard messages (exactly ValueError); library errors can
        # subclass ValueError (requests.InvalidHeader did, leaking the key 2026-08-05).
        if type(e) is ValueError:
            logger.error("Universe refresh aborted: %s", e)
            return jsonify({"status": "aborted", "message": str(e)}), 500
        logger.error("Universe refresh failed: %s", e, exc_info=True)
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
