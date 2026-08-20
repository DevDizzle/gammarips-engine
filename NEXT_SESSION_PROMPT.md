# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## Active workstream — commit the 08-19/08-20 work
The working tree holds two coherent uncommitted lanes. Nothing is committed.
`PRINT_FLOOR_MIN=25` shipped and the score floor was accepted at 1 on 08-20
(`docs/DECISIONS/2026-08-20-score-floor-accepted-print-floor-25-shipped.md`).
1. **Commit lane A (08-19 research):** 4 `backtesting_and_research/2026-08-19_*.py`
   scripts, `docs/EXECUTION-RISK-GUIDELINES.md`, the NOT-ADOPTED decision note
   `docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md`, the pre-registered
   `docs/EXEC-PLANS/2026-08-19-pool-benchmark-test-spec.md` (amended pre-data 08-20;
   do NOT modify after data), plus ledger/brief/wiki additions.
2. **Commit lane B (08-20 scaffold cleanup):** ~70 files — docs synced to code, all
   retired-gate language scrubbed, 9 new wiki notes, archive moves (staged), memory
   maintenance, settings prune. Audit + edit trail in this session's transcript.
3. **Run the pool-vs-benchmark test** per the pre-registered spec (blocked behind the
   POLYGON_API_KEY rotation it names).
Open owner call from the 08-19 research (flagged once, do not re-raise): later
same-day entry ([[first-hour-bleed]]).

## OAuth + GTM (compressed; shipped state in memory `oauth-as-built-2026-08-19`)
- OAuth AS + `/pro` LIVE since 08-19 (e2e 24/24 on prod). Secrets owner call is
  recorded in `~/workspace/OAUTH-ROLLOUT.txt`. Next: webapp copy PR (`/developers`,
  `public/mcp.json`, `llms.txt`, connect tabs) via copywriter + `/ship`; mark
  GitGuardian 36370105 false positive.
- **Single gate for guides B4/B5, videos E4/E5, and the CONNECT-MATRIX rewrite: one
  real per-client OAuth sign-in verified against live `/pro`** (start with ChatGPT).
- Plan of record: `docs/GTM-ORGANIC-GROWTH-PLAN.md` + `GTM-CLIENT-CONNECT-MATRIX.md`
  + `GTM-VIDEO-SERIES.md`. Next drafts: guides B1 + B2, publish script B9, E2 after
  the owner's Grok UI test. Owner: Grok test, record E1, YouTube channel. Gates
  unchanged: video live AND one GA4-attributed checkout before Show HN; NO
  directories; ads review ~09-01 only if CVR is nonzero. Harness repo work pending
  (plan §D2). **OPEN OWNER CALL: regime-rail public doctrine.**
- Live-money agent lane: `docs/EXEC-PLANS/2026-08-15-live-agent-trace-surface-plan.md`
  (lane A = trader session; B/C queued behind GTM). Still unverified from 07-30:
  blog-generator deploy revision + dry-run; did the 08-03 Mon cron fire.

## Owner queue
- 🔴 Rotate `POLYGON_API_KEY` (leaked 07-06, echoed 08-05, contained). Regenerate →
  update secret → redeploy every mounting service (grep deploy.sh).
- Revoke + regenerate the 08-06 test MCP key (pasted in chat).
- Restate the public life-surface headline before the next Fri 12:00 ET
  `x-poster-life-stats` post — 08-07 freshness-canary decision note §Consequences.
- Record the disposition of the PASSED 08-17 zero-trials kill-switch gate (one answer,
  then the note settles; memory `mcp-monetization-killswitch`). The 10-05 gate stands.
- win-tracker redeploy (committed + pushed `d44a272`); verify x-poster +
  blog-generator redeployed so the vendored cohort pin carries 2026-08-21 (redeploy
  needed; blog-generator's Mon 05:00 cron exposure unchanged).
- Webapp score-claim scrub PR pending merge (copywriter + `/ship` gate).
- Compliance substring misfires (`'for you'`, `'guaranteed'` negations,
  `libs/gammarips_content/compliance.py:125`); `$19`/`Starter tier` not in aliases.
- Organic Social halved (67→35 sessions/28d) — x-poster lane needs its own look.
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to
  `status: published`; lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- First pick under `PRINT_FLOOR_MIN=25`: next 09:52 ET run. Expect a thinner slate. A
  `no_liquid_candidates` no-pick day is correct.
- 🔴 One trial checkout to confirm `purchase` attaches to a real GA4 session — the only
  unverified item from 08-08, gates Show HN.
- Owner's 08-13 trial conversion: `invoice.paid` on the new webhook path + `proUntil`
  refresh — due and unconfirmed (memory `billing-lifecycle-verified-on-real-card`).
- ~08-22: re-run `scripts/seo/gsc_inspect.py` on the orphaned reports; re-check
  `options flow api` position (was 24.2).
- ~08-27 threshold re-fit: confirm the 08-19 31-day `pool_liquidity_snapshot`
  measurement closes it; if yes, drop this line.
- Mid-Aug ITM check (needs ≥200 expired post-06-12-era rows).
- Verify the first post-08-14 pick card behaved (refusal note + no bracket = correct;
  grep lines + the ns→ms trap live in `docs/DECISIONS/2026-08-14-entry-mark-date-validation.md`).

## Open engineering
- 🔴 Deploy the LLM cost-accounting fix — `a2fb621` committed AND pushed, not deployed.
  `/deploy-service`: signal-judge (real change), then enrichment-trigger +
  overnight-report-generator (redeploy only). Verify per the query in
  `docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md` (~3 rows/day, cost_usd
  non-null, ~$0.25/day). Owner call still open: historical cost_usd recompute.
- 🔴 No spread/depth measurement exists (all 64,550 quote reads NULL —
  `docs/EXECUTION-RISK-GUIDELINES.md` §0). Blocked on Polygon NBBO entitlement, owner
  $ call (GAP-001/RM-001b). Do not tune proxies as though that closes it.
- FALLBACK picks bypass the liquidity floor (`POLICY_GATE_FALLBACK` takes `df.iloc[0]`
  with no live-OI or print check) — same defect class as the 08-12 regression.
- MCP repo (own gate): `open_past_due` daily false stall; row tools unaudited for the
  silent cap (`labels`, `positions`, `signal_performance`); frontier calendar blind to
  trailing gaps <~5d; QUALIFY dedup; `freshness_note` copy; smoke-test scrub covers
  26/all playbooks; surface EXECUTION-RISK-GUIDELINES through `get_playbook`.
- P1 live 10:00 anchor pass — ACCEPTED, not built, blocked on owner $ (Polygon cost).
- Audit remaining snapshot `day.*` readers; audit `next_url` pagination
  (`polygon_client.py:215`, `benchmark_context.py`); x-poster public-route IAM audit
  (gotcha in the 08-07 blog-generator lockdown note).
- Smaller: `iv_rank_entry` permanent view-level exclusion; earnings-rail stamp
  (GAP-014); UNDATABLE branch split (08-14 note); substrate rows (41 delta-0 ITM, 7
  NO_BARS); service-auth hardening (07-02 note); webapp old-MCP-host refs + 3 tsc
  errors; blog non-blocking pair; filler NO_BARS re-qualify edge; check
  `gammarips-eval` config scores `signal_judge` traces.

## Live posture
- V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` (rewritten lean 08-20) + wiki
  `REGISTRY.md` + `CHEAT-SHEET.md`. Cohort start: `LIVE_COHORT_START_DATE` in
  `signal-notifier/main.py` (2026-08-21; never hardcode it in docs).
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
