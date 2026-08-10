#!/usr/bin/env python3
"""Manual CLI for the scan-universe refresh.

Thin wrapper over src/enrichment/core/pipelines/universe_refresh.py — the same
code the overnight-scanner /refresh_universe endpoint runs weekly. All logic,
safety guards, and the hard-won Polygon API facts live in that module.

Usage:
    POLYGON_API_KEY=... python3 scripts/universe/refresh_universe.py --dry-run
    POLYGON_API_KEY=... python3 scripts/universe/refresh_universe.py [--allow-shrink]
"""

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.enrichment.core.pipelines import universe_refresh  # noqa: E402

# Deliberately explicit: the workstation exports PROJECT_ID=profitscout-lx6bb,
# so config's env fallback would attribute the storage client to the wrong project.
PROJECT_ID = "profitscout-fida8"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="report the diff, upload nothing")
    parser.add_argument("--allow-shrink", action="store_true",
                        help="permit shrink beyond the guard (first refresh after a stale era)")
    parser.add_argument("--allow-growth", action="store_true",
                        help="permit growth beyond the guard (verified legitimate expansion)")
    args = parser.parse_args()

    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        print("POLYGON_API_KEY not set", file=sys.stderr)
        return 1
    try:
        summary = universe_refresh.run_refresh(
            api_key=api_key, dry_run=args.dry_run, allow_shrink=args.allow_shrink,
            allow_growth=args.allow_growth, project=PROJECT_ID,
        )
    except ValueError as e:
        print(f"ABORT: {e}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
