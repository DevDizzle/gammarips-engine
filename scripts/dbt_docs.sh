#!/usr/bin/env bash
# Generate and serve the dbt docs site (browsable data dictionary + column-level
# lineage graph). Read-only against BigQuery (needs OAuth/ADC for catalog introspect).
#
# Usage:
#   scripts/dbt_docs.sh [port]      # default port 8081
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DBT="${DBT:-$REPO_ROOT/.venv_dbt/bin/dbt}"
PORT="${1:-8081}"

cd "$REPO_ROOT/dbt"

"$DBT" deps --profiles-dir .
"$DBT" docs generate --profiles-dir .
echo "Docs generated. Serving on http://localhost:$PORT (Ctrl-C to stop)…"
"$DBT" docs serve --profiles-dir . --port "$PORT"
