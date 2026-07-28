# Rules for forward-paper-trader/

This is the production paper-trading service. Changes here directly affect data quality.

- ALWAYS invoke `gammarips-review` before deploying changes to this service.
- NEVER remove or rename benchmarking columns in ledger writes — downstream analysis depends on column stability.
- NEVER add FMP dependencies — FMP was deliberately removed from this service (2026-04-08).
- The benchmarking layer (`benchmark_context.py`) is deliberately non-blocking. Every fetch returns `None` on failure. Do not add error-raising behavior.
- Deploy command: `cd forward-paper-trader && bash deploy.sh`
- One Cloud Run service, six routes: `POST /` (paper trading), `POST /cache_iv`, `POST /mark_to_market`, `POST /persist_minute_paths` (token-gated), `POST /label_life_surface`, `POST /label_enriched_pool`, `POST /fill_closed_windows` (token-gated, 2026-07-28).
- Secret mounts: `POLYGON_API_KEY`, `POOL_LIQ_REFRESH_TOKEN` (2026-07-07), `FILL_WINDOWS_TOKEN` (2026-07-28). No FMP key, ever.
