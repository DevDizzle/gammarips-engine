# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## Active workstream — Growth sequence (DECIDED 08-06)
`docs/DECISIONS/2026-08-06-growth-sequence-video-hn-ads.md` is the plan of record.
07-07 directory sprint = 30-day null result; passive listings don't move this, don't
re-propose. Steps, in order:
1. **Merge + deploy the 5 webapp PRs (owner merges; `main` auto-deploys).** All five
   test-merged CLEAN in sequence, combined tree builds, combined smoke test passes.
   **#21 GA4 attribution** (purchases land `(not set)`; pre-traffic blocker, only fixes
   checkouts made after deploy) · **#20** lowercase-ticker 308 · **#22** reports archive
   hub · **#23** head hygiene (og:image on 11 pages, title dupes, 12 SERP-truncated
   descriptions) · **#24** options-flow-API FAQ + report chain + ticker→report links.
   Post-deploy checks are written into each PR body (see Watch below).
2. **Video: "How to Trade Options Using Claude"** — outline/script/compliance rails in
   `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`. Owner review → webapp
   `gammarips-copywriter` pass → record (fresh demo key, revoke after shoot).
   Embed: webapp `landing/video-led` branch (READY, iframe swap, merges via `/ship`).
3. **Show HN timed with the video** — the one unfired $0 channel. Draft to write.
   Lead with the zero-friction line, not a site link:
   `claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp`
   (anonymous tier: no card, no key). That one-liner is the demo.
4. **Ads review ~09-01** on measured CVR from video+HN traffic; $10-20/day on the exact
   "claude mcp options trading" cluster only if CVR nonzero.

Open verification carried from 07-30: **blog-generator deploy** — confirm revision, then
dry-run `POST /generate {"slug":"best-mcp-servers-for-trading-and-finance","dry_run":true}`
(now needs `-H "Authorization: Bearer $(gcloud auth print-identity-token)"`); check
whether the 08-03 Mon cron fired or 500'd (wk15 slug).

## SEO posture (measured 08-08, memory `reports-are-the-seo-asset-not-ticker-pages`)
Real external organic demand is **~2 impressions/day** (75 queries / 184 impr per 90d
after stripping brand + `site:`). GA4 is ~97% bot (Singapore, 1.001 sessions/user).
**Ticker pages are a dead asset: 452 pages, 3 clicks/90d — do not build more.** Dated
report pages are the surface that ranks (pos 3.0, 9.0, 9.3 on analyst-shaped queries).
`options flow api` at pos 24 is the one query with real buyer intent (#24 targets it).
Never quote a GSC/GA4 aggregate here without stripping brand, `site:`, and bot traffic.

## Owner queue
- 🟡 **WATCH Mon 08-10 09:52 ET — first pick under a print floor that actually fires.**
  Shipped 08-07; cohort RESET to `LIVE_COHORT_START_DATE=2026-08-10`, `cohort_stats` 0
  closed. Check the `Early-print floor: dropped N/12` and `Fail-soft floor: restored N`
  log lines + the email's Liquidity line. Replay: fail-soft carries the slate ~11/15
  sessions and hands zero-print names back to the judge 8/15 (max 6), so
  `tournament_v1_2`'s "early_volume 0 = untradeable" sentence is the ONLY wall most days.
  If picks return with `early_volume: 0`, raise `PRINT_FLOOR_MIN` or lower `TOURNEY_MIN`
  — do NOT widen the floor. `docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md`.
- 🔴 **Rotate `POLYGON_API_KEY`** (leaked 07-06, echoed 08-05 in an error body, contained,
  endpoint hotfixed `00015-t78`). Regenerate → update secret → redeploy all mounting
  services (grep deploy.sh).
- 🔴 **Restate the public life-surface headline before the next Fri 12:00 ET
  `x-poster-life-stats` post.** 08-07 post said "1495 contracts tracked"; cohort is now
  2,192 and x-poster reads BQ live. Three causes mixed, only one needs a restatement
  sentence: 23 rows **retracted** (fabricated −100% from a split/strike unit mismatch,
  inside the published 1,495); +720 stranded rows healed; compositional drift.
  `docs/DECISIONS/2026-08-07-freshness-canary-and-bars-loader.md` §Consequences.
- **Revoke + regenerate the 08-06 test MCP key** (pasted in chat during e2e).
- **Restore clobbered SEO post (one status flip):**
  `blog_posts/building-options-flow-pipeline-ai-agents` → `status: published` in console.
- **win-tracker NOT deployed** — park watchdog removal is in the working tree alongside
  unrelated uncommitted changes from a prior session; review before shipping. Safe to
  leave: `park_watchdog/gate_30_alerted` is set so it cannot re-fire.
- **Cohort constant is pinned across repos.** `libs/gammarips_content/cohort.py` +
  `tests/test_cohort_pin.py`; MCP mirrors it in `src/utils/data.py`. **On the next cohort
  reset that test fails until you update it AND redeploy both publishers.**
- **Compliance substring misfires:** `'for you'` matches "for your agent",
  `'guaranteed'` kills negations (`libs/gammarips_content/compliance.py:125`). Killed 2
  posts, will bite MCP-cluster topics. `$19`/`Starter tier` absent from `RETIRED_ALIASES`.
- **Organic Social halved** (67→35 sessions/28d) — x-poster lane needs its own look.
- **lx6bb stray docs** (`blog_schedule`/`blog_config`): delete or ignore, owner call.
- Small: Cursor plugin listing refresh to v4. X: unpin 03-14, pin distribution draft, bio
  refresh. Stripe MCP not installed (hosted OAuth, owner action).

## Watch / dated checkpoints
- **After the webapp deploy:** `/reports/archive` lists ~90 reports back to ~2026-04;
  an April report shows prev/next; `/signals/NVDA` links its scan-date briefing; one
  trial checkout confirms `purchase` attaches to a real session, not `(not set)`.
  Then (give Google 1-2 weeks) re-run `scripts/seo/gsc_inspect.py` on the orphaned
  reports to confirm the new crawl paths took.
- **08-10 Mon 07:00 ET:** first `dbt-source-freshness` run that CAN go red.
- **08-09 Sun 08:00 ET:** first scheduled universe weekly refresh — spot-check it fired.
- **~08-13:** owner's trial converts — first real-card charge; verify `invoice.paid` fires
  the newly-registered webhook path and proUntil refreshes.
- **08-17 / 10-05 kill-switch gates** — memory `mcp-monetization-killswitch`.
- **~08-27:** re-fit print/liq thresholds on ~30 more days of `pool_liquidity_snapshot`
  (review hard requirement — 15-day in-sample fits). NOT a re-run of the 07-28 study,
  which used non-stale `day_volume` and is correct; only production diverged.
- **~Late Aug (≥15 fresh closed-label days):** pre-committed re-test of cap-50-era
  `contract_score` lead (AUC 0.552 / day-demeaned 0.564) — lead, not edge. Catalyst/ATR
  inversions REFUTED same entry, do not re-run.
- Verify the 08-07 `load-underlying-bars` cron chain held: `life_status` OK 2192 /
  PARTIAL_NO_EXPIRY 2 / PARTIAL_SPLIT_ADJUSTED 27.
- Mid-Aug: post-06-12-era ITM check (needs ≥200 expired era rows).

## Open engineering
- 🟡 **x-poster not audited for public mutating routes** — same shape as the
  blog-generator hole closed 08-07 (`docs/DECISIONS/2026-08-07-blog-generator-iam-lockdown.md`).
  Gotcha recorded there: `gcloud run deploy --no-allow-unauthenticated` does NOT revoke an
  existing `allUsers` binding; verify the live IAM policy, don't trust the flag.
- `iv_rank_entry`/`iv_percentile_entry` post-entry leakage — permanent fix (tag as
  telemetry + exclude from `enriched_features_v1`) still undone; memory
  `iv-rank-entry-post-entry-leakage`.
- signal-notifier: stamp pick notification with earnings-rail clearance window + expiry
  re-check note — judge overclaimed on CSCO 08-05 (GAP-014).
- Audit `next_url` pagination on remaining endpoints (`polygon_client.py:215`,
  `benchmark_context.py`); memory `polygon-next-url-cursor-skips-rows`.
- MCP repo (own rules + review gate): `FILL_PENDING`/stale via window-close derivation;
  QUALIFY dedup; `market_snapshot.py` `freshness_note` calls `day_volume` "the live
  (delayed) session", false on a stale bar (copy fix, not a defect).
- Blog non-blocking (review 07-30): swallowed schedule-row-flip failure repeats Monday
  500s until console flip; DESIGN_SPEC edge case 7 claims a nonexistent publish lock.
- Filler edge case (07-28): transient NO_BARS opp fetch + good 3d fetch = row never
  re-qualifies; warn or extend re-select predicate.
- MCP smoke-test scrub covers only 26 methodology pages — extend to all `content/playbooks/`.
- Webapp `src/ai/**` + legacy script reference the old MCP host.
- Service-auth hardening not executed (`docs/DECISIONS/2026-07-02-service-auth-hardening.md`).
- Substrate: 41 `recommended_delta`=0.0 ITM-at-scan rows; 7 pick rows NO_BARS.
- RM-001b BLOCKED: `pool_liquidity_snapshot` quote cols 100% NULL — quote entitlement,
  owner $ call.
- 3 pre-existing tsc errors in webapp `src/app/signals/page.tsx` (`underlying_scan_date`
  on `OvernightSummary`) — reproduce on clean `main`, unrelated to this session's PRs.

## Live posture
- Policy: V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + `docs/wiki/_index/REGISTRY.md` + `CHEAT-SHEET.md`.
- Owner trades LIVE (Robinhood since 07-09); bankroll in gammarips-trader memory.
- Daily crons run end-to-end; MCP paywall ENFORCE.
- **GSC/GA4 auth is SOLVED** — service-account impersonation, `SEO_IMPERSONATE_SA` in
  `~/.bashrc`. Interactive ADC login is DEAD (Google blocks the shared gcloud client ID
  for these scopes). Invoke the **`seo-auth` skill**, never re-derive it.
- **Health monitoring real since 08-07** — operator digest 07:15 ET weekdays
  (`freshness-digest` → dbt-runner `/digest`). POST `/freshness` 500s on `error_after` by
  design; never revert to 200, never let an unchecked section render OK.
