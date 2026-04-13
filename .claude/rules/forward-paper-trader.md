# Rules for forward-paper-trader/

This is the production paper-trading service. Changes here directly affect data quality.

- ALWAYS invoke `gammarips-review` before deploying changes to this service.
- NEVER remove or rename benchmarking columns in ledger writes — downstream analysis depends on column stability.
- NEVER add FMP dependencies — FMP was deliberately removed from this service (2026-04-08).
- The benchmarking layer (`benchmark_context.py`) is deliberately non-blocking. Every fetch returns `None` on failure. Do not add error-raising behavior.
- Deploy command: `cd forward-paper-trader && bash deploy.sh`
- Two endpoints on one Cloud Run service: `POST /` (paper trading) and `POST /cache_iv` (IV cache refresh).
- Secret mounts: only `POLYGON_API_KEY`. No FMP key.
