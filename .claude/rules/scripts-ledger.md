# Rules for scripts/ledger_and_tracking/

- `current_ledger_stats.py` is a read-only monitoring script. Do NOT add filter ranking, winner searches, or gate tuning logic to it.
- `create_*.py` and `backfill_*.py` scripts are one-shot DDL/migration scripts that have already been executed. Keep for posterity, do not re-run without explicit user approval.
- Any new EDA script must be read-only against BigQuery. NEVER write or mutate ledger data from a script in this directory.
