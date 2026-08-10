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
1. ✅ **DONE 08-08 — all 5 webapp PRs merged, deployed, verified live.** #21 GA4
   attribution (only fixes checkouts made AFTER deploy) · #20 lowercase-ticker 308 ·
   #22 reports archive · #23 head hygiene · #24 options-flow-API FAQ + report chain +
   ticker→report links. Verified in prod: 15/15 pages emit og:image, all titles carry
   one brand suffix, all descriptions 129-150 chars, `/signals/aapl` 308s,
   `/reports/archive` lists **116 reports back to 2026-02-13**, `/developers` carries
   FAQPage schema with "options flow api" x18, the oldest report links forward, and
   `/signals/NVDA` links its 08-03 briefing.
2. **🔴 NEXT: the video — CONCEPT CHANGED BY OWNER 08-08.** Not a trading clip: a
   **zero-to-contracts install demo**. Empty directory → `git clone` the harness → the
   one-line MCP connect → `/trade` → contract candidates out of the curated data.
   Spec rewritten to v2 in `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md` (acts, the
   start-from-nothing rule, the beats that must survive the cut). Owner records, then
   coordinates the edit with **Gemini**. Fresh demo key, revoke after the shoot. A
   "nothing today" outcome SHIPS, it does not get re-recorded. Embed: webapp
   `landing/video-led` branch (READY, iframe swap, `/ship`).
3. **Show HN — fully planned in `docs/GTM-DISTRIBUTION-PLAYBOOK.md`** (durable; the
   scratch copy at `~/workspace/HN-SUBMISSION.txt` is for copy-paste only). Title, URL,
   full submission text, gates, the ban-triggering mistakes, the 3 questions. Submit the
   **repo** `github.com/DevDizzle/gammarips-harness`, not gammarips.com — same artifact
   the video demos. Harness README fixed 08-08 (PR #2): it led with "Subscribe $39/mo"
   and never mentioned the free tier. **The harness loop genuinely CANNOT run
   anonymously** (`get_liquidity`, `get_signal`, `query_outcomes`, `replay_contract` are
   all pro) — never claim it can. FIRE ONLY AFTER THE VIDEO + the GA4 purchase check.
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
The report archive turned out to be **116 pages back to 2026-02-13**, ~2x the estimate;
43+ of them had been orphaned (no sitemap entry, no internal link) but still indexed.
Acquire on CURRENT vocabulary (`options flow api`, `unusual whales alternative`), not on
the category vocabulary — you rank 7.7 for `llm stock options data` and it drew 3
impressions in 90 days. Being early means the demand does not exist yet, not that you
are losing. LLM-mediated discovery is the compounding channel: the longest-engaged US
session of the month (379s) came from copilot.com.

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
- 🔴 **One trial checkout** to confirm `purchase` now attaches to a real session rather
  than `(not set)`. The ONLY unverified item from the 08-08 deploy: it needs a real
  Stripe checkout, cannot be curl'd. Do this before HN, or the spike is unmeasurable.
- **~08-22 (give Google 1-2 weeks to recrawl):** re-run
  `scripts/seo/gsc_inspect.py --file <orphaned reports>` to confirm the new crawl paths
  took, and re-check `options flow api` position (was 24.2 pre-FAQ).
- **08-10 Mon 07:00 ET:** first `dbt-source-freshness` run that CAN go red.
- **08-09 Sun 08:00 ET:** first scheduled universe weekly refresh — spot-check it fired.
- **Thu 08-13:** owner's own trial converts — first real-card charge. The T-3 warning email
  fired correctly 08-08 (right amount, date, sender, manage link), so the dunning path is
  proven; what remains is `invoice.paid` firing the newly-registered webhook and refreshing
  `proUntil`. NOTE: this is the owner's own subscription, never a subscriber count.
  Memory `billing-lifecycle-verified-on-real-card`.
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
- 🔴 **MCP `view="surface"` fix is written, tested, NOT deployed** (unstaged in
  `../gammarips-mcp`). Adds `aggregate_only` + `delta_min/max` + truncation disclosure
  (`matched_rows`/`truncated`/`partial_scan_date`) + a `frontier` block. Found while
  answering the 08-10 trader handoff: the row mode silently returned 200 of 791 matched
  rows and, because the sort is `scan_date DESC, opp_peak_return DESC`, the cut lands
  mid-date and keeps only that date's highest-MFE rows — **median MFE inflated 46%**
  (0.3416 vs 0.2341). Public data-exposure change: needs `gammarips-review` + owner
  deploy. Memory `mcp-row-cap-silent-truncation`. **Other row tools are unaudited for
  the same undeclared cap** (`labels`, `positions`, `signal_performance`).
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
- MCP repo (own rules + review gate): ~~`FILL_PENDING`/stale via window-close
  derivation~~ (done 08-10, the `frontier` block, in the same unstaged change above);
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
