# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## Active workstream — Organic growth push (owner 2026-08-13)
**`docs/GTM-ORGANIC-GROWTH-PLAN.md` is the plan of record** (extends the 08-06
decision; video/HN gates unchanged). Product statement LOCKED: **MCP + harness =
agentic trading** — execution-risk data (paid MCP) + free open loop + the user's own
agent. Audience: agent-harness users who trade options (memory
`audience-is-claude-code-options-traders`). All new public copy in STE. Order:
1. **🔴 NEXT: landing rewrite (plan §A) + Grok guide (§B1).** Start with A1:
   `harness-cta.tsx:21` teaches 4 RETIRED commands; real loop is `/trade` `/review`
   `/coach`. Then hero equation, per-client connect tabs, section reorder. Branch
   (main auto-deploys), `gammarips-copywriter`, `/ship` from `~/workspace`.
2. **The video** (spec v2 unchanged, `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`;
   owner records, Gemini edit, fresh demo key, "nothing today" SHIPS) → **Show HN**
   per `docs/GTM-DISTRIBUTION-PLAYBOOK.md`. Gates: video live AND one real
   GA4-attributed checkout. Loop cannot run anonymously — never claim it can.
3. **Backlinks weekly (plan §C).** NO directories (07-07 = 30-day null, decided).
4. **Ads review ~09-01** on measured CVR, only if nonzero.
Inputs banked 08-13: GSC assistant-name footprint = ZERO (whole cluster 8
impressions/90d; seed "mcp options order flow server" pos 10); **Robinhood agentic
MCP is OFFICIAL** (memory `robinhood-agentic-trading-mcp-official`); public Grok
share demos the free-tier funnel end to end (link in plan §B1).
Harness repo pending (plan §D2): `AGENTS.md` for Codex, "your fills close the loop"
README section, hand-sync 4 wiki notes — sync tool `--apply` is UNSAFE (memory
`trader-harness-sync-apply-unsafe`). Prior-session uncommitted ste100 skill commit
rides first. **OPEN OWNER CALL: regime-rail public doctrine** — keep fail-closed
(recommended) vs adopt his private halve-and-continue.

Open verification carried from 07-30: **blog-generator deploy** — confirm revision, then
dry-run `POST /generate {"slug":"best-mcp-servers-for-trading-and-finance","dry_run":true}`
(now needs `-H "Authorization: Bearer $(gcloud auth print-identity-token)"`); check
whether the 08-03 Mon cron fired or 500'd (wk15 slug).

## SEO posture (measured 08-08)
GRADUATED to memory `reports-are-the-seo-asset-not-ticker-pages` +
`docs/GTM-DISTRIBUTION-PLAYBOOK.md`. Read one of those before any SEO/GTM decision.
Two facts too costly to rediscover: **ticker pages are a dead asset (452 pages,
3 clicks/90d) — do not build more**, and **never quote a GSC/GA4 aggregate for this
property without first stripping brand, `site:`, and bot traffic** (that is 53% of
impressions and ~97% of sessions).

## Owner queue
- ✅ **SHIPPED 08-12 — fail-soft restore fix.** `signal-judge-00010-xkc` +
  `signal-notifier-00058-fl2`, commit `1c2c60d`, `gammarips-review` PASS on the second
  pass (it BLOCKED the first: my `measured` flag proved "no exception fired", not "we
  measured", so a Polygon outage could have swept the slate on stale frozen OI and
  published a false stand-down). Live: `FAILSOFT_RESTORE_MODE=none`,
  `LIVE_FETCH_MIN_OK_FRAC=0.5`, `tournament_v1_3`/v10.
  **Cohort RESET to `LIVE_COHORT_START_DATE=2026-08-13`** (owner call): 2 of the 08-10
  cohort's 3 entries were restores the new code cannot select.
  `docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md`.
  - 🟡 **WATCH Thu 08-13 09:52 ET, the first pick under it.** Expect a slate thinner
    than 8 and no `restored` line. New log lines to grep: `Fail-soft restore
    SUPPRESSED`, `DEGRADED live read`, `EMPTY SLATE`. A `no_liquid_candidates` day is
    correct behavior, not a break, and it now emails you the counts.
- 🔴 **DEADLINE Mon 08-17 05:00 ET — cohort mirror drift (from the 08-12 reset).** The
  constant is mirrored in 4 places; 2 are updated (`signal-notifier/main.py`,
  `libs/gammarips_content`, pinned by `test_cohort_pin.py`). **Still on 08-10:**
  `gammarips-mcp/src/utils/data.py` (separate repo, own commit + review gate) and the
  vendored copies inside x-poster + blog-generator, which need a REDEPLOY to pick the
  new value up. blog-generator's Mon 05:00 ET cron would otherwise publish a cohort
  containing ALC, the -$312 restore pick this change repudiates. Also prose in the MCP's
  `historical.py` and `performance_tracker.py`.
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
- **Thu 08-13:** owner's OWN trial converts (never a subscriber count). T-3 warning email
  verified correct 08-08, so dunning is proven; what remains is `invoice.paid` firing the
  new webhook path + refreshing `proUntil`. Memory `billing-lifecycle-verified-on-real-card`.
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
- 🔴 **P3 from the trader, unfixed and not fixable in code: nothing measures spread or
  dollar depth.** OI + print count are proxies for "can a subscriber get out"; MDB passed
  both at a 44.6% spread. Wanted on the candidate row + card: `spread_pct`,
  `bid_depth_usd`. Blocked on the Polygon quote entitlement (GAP-001 / RM-001b) — owner $
  call, do not keep tuning proxies as though that closes it.
- **FALLBACK picks bypass the liquidity floor entirely** — `_liquidity_refresh_and_rank`
  runs on STRICT days only; a `POLICY_GATE_FALLBACK` day takes `df.iloc[0]` with no live-OI
  or print check. Same defect class as the 08-12 regression, deliberately not bundled.
- ✅ **DONE 08-10 — MCP `view="surface"` fix SHIPPED** (`gammarips-mcp-00043-mgz`,
  MCP commit `1c8d874`; engine half `971521c` → `dbt-runner-00009-lvd`). Row mode was
  silently returning 200 of 791 matched rows and, because the sort is `scan_date DESC,
  opp_peak_return DESC`, the cut lands mid-date keeping only that date's highest-MFE rows
  — **median MFE inflated 46%** (0.3416 vs 0.2341). Now: `aggregate_only`, `delta_min/max`,
  truncation disclosure, and a `frontier` block that VERIFIES liveness (`open_past_due`)
  instead of asserting it. Verified live through the hosted MCP. `gammarips-review`
  blocked it **twice** before passing; both times the blocker was a fix reintroducing the
  same "reconciles against itself" defect it was closing.
  `docs/DECISIONS/2026-08-10-surface-aggregate-and-truncation-disclosure.md`.
  **Still open from that review:** other row tools are unaudited for the same undeclared
  cap (`labels`, `positions`, `signal_performance`); and the frontier's session calendar
  is blind to a trailing gap under ~5 calendar days, so a stall shorter than that can
  still read as by-design (bounded, disclosed via `calendar_max_session` /
  `calendar_max_gap_days`). Memory `mcp-row-cap-silent-truncation`.
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
