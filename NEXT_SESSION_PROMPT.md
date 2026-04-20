# Next Session Prompt

**Last session wrapped:** 2026-04-17
**Current policy:** V5.3 "Target 80" (deployed today, see `CHEAT-SHEET.md`)
**Status:** All three services deployed. Monitoring mode for next 4 weeks.

## Before you do anything

1. Read `CHEAT-SHEET.md` (repo root) for the operator-level view.
2. Read `docs/GLOSSARY.md` for service/table definitions in plain English.
3. Read `docs/DECISIONS/2026-04-17-v5-3-target-80.md` for the rationale.

## What happened last session (2026-04-17)

- Discovered paper ledger had 70 rows / 1 scan_date while enriched had 404 / 5 days — explained as paper-trader 4-trading-day lag, not a bug.
- Ran cohort analysis on `signals_labeled_v1` (N=1,563): full-sample EV −4.26%; **no feature cohort** passed bootstrap + walk-forward. Hedge-flag alpha claim contradicted.
- Ran Deep Research. Findings layered into V5.3: `V/OI > 2`, moneyness 5–15% OTM, `VIX <= VIX3M` regime gate, +80% option target.
- Killed V4. Deployed V5.3 across `enrichment-trigger`, `signal-notifier`, `forward-paper-trader`. Audited and approved by `gammarips-review`.
- Memory updated: hedge flag is NO LONGER treated as the alpha.

## What to expect this week

- **9:00 AM ET each weekday:** at most one signal emailed. Zero-email days are the filter working, not a bug.
- **~2–4 emails per week** is the expected steady state with V5.3 filters.
- **First V5.3 ledger rows** arrive ~4 trading days after first qualifying enrichment (paper-trader hold-window lag).
- **User is trading real money** at $500/trade in parallel with paper. Pre-set −60% stop-limit and +80% limit sell on Robinhood at 10:00 AM entry.

## What NOT to do

- Do NOT tune filters during the 4-week observation window. If EV is negative, go back to Deep Research; don't knob-twiddle.
- Do NOT modify `scripts/research/` or `signals_labeled_v1` — frozen.
- Do NOT add trader-side gates to `forward-paper-trader`. Signal-quality gates live in `enrichment-trigger` and `signal-notifier`.
- Do NOT deploy without `gammarips-review` audit first.

## Health checks to run on first V5.3 runs

1. First `enrichment-trigger` run post-deploy: check logs for `V5.2 schema ensure failed` warnings (the 3 new columns get added on first run).
2. First `signal-notifier` run: verify it either emails 1 signal OR logs a clean regime-skip / no-qualifying-signal reason.
3. First `forward-paper-trader` run on a V5.3-era scan_date: verify a `V5_3_TARGET_80` row appears in `forward_paper_ledger`.

Quick health-check query:

```sql
SELECT policy_version, COUNT(*) AS n, MIN(scan_date) AS first, MAX(scan_date) AS last
FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
GROUP BY policy_version
ORDER BY last DESC;
```

## 4-week review trigger

After ~2026-05-15, compare:
- Paper EV across V5.3 rows (mechanical baseline)
- Real P&L across your actual Robinhood trades
- If paper EV > 0 → scale real size up.
- If paper EV < 0 → pause real, rerun Deep Research with new data.
- If real >> paper → discretion is adding value.
- If real << paper → you're hurting the math.

## Open items on backlog (NOT V5.3)

- Sweep / block classification via Polygon tick-level data
- Aggressor side (bid vs ask lift)
- GEX / dealer positioning
- Trailing stop at +30% → would need underlying-price conditional logic (Robinhood doesn't support on options)
- Regime-conditional sizing

None of these ship until V5.3 has real data to justify them.
