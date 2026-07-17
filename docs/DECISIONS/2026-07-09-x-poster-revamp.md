# 2026-07-09 — x-poster revamp: kill dead-product CTAs, pool-level receipts, agentic angle, metrics loop

**Context.** Owner call (2026-07-09): revamp the @gammarips X surface and post more.
Audit findings that forced this:

- The pinned tweet dated 2026-03-14 (V5.4 era) and the live templates still sold
  the **retired paid email pick** ("Curated daily pick → email subscribers only"
  shipped daily on the watchlist post; the pick email fan-out was retired 07-03).
- Only `watchlist` (daily) + `report` (Mondays) crons were enabled — and the
  report cron fired 06:30 ET, **before** the 07:00 ET report generator, so it
  no-op'd (`no_report_today`) every week.
- `signal`/`callback`/`scorecard` were paused 07-03 and can't simply resume:
  the daily pick is now **private** (scalping optics), and callbacks QRT'd the
  public signal post that no longer exists.
- Zero content served the actual business (free UI funnel + $39/mo MCP Agent
  Access), and nothing measured post performance.

**Decision.**

1. **CTA reset (compliance-enforced).** "email subscribers only",
   "curated daily pick", and "WhatsApp" added to `RETIRED_ALIASES` — the dead
   CTAs now hard-fail the rubric. New CTAs: free site (link in bio) / MCP
   Agent Access. Voice rules updated to match.
2. **No em dashes** in any public copy (owner rule 2026-07-08) — enforced
   deterministically in `canonicalize_draft_text` (em/en dash → hyphen) plus
   template + reviewer updates.
3. **`pool_outcomes` (new, Mon–Fri 17:45 ET).** Daily pool-level bracket
   receipts from `enriched_option_outcomes` (`entry_day = today`; the 17:00 ET
   labeler must have run): N names, targets/stops/timeouts, best peak, median.
   **Pool-level only — never selects or hints at `was_tournament_pick`.**
   Replaces the per-pick win/loss callback as the receipts loop. Realized
   same-day data posted after the close → leakage-free by construction.
   Disclaimer required. Skip-guard when no labeled rows (holiday/outage).
4. **`life_stats` (new, Fri 12:00 ET).** Weekly full-life distribution over
   `life_status='OK'` rows (median peak, % touched +40%, % doubled, median at
   expiration — the landing-page honesty stats). Min-N 300 guard. Disclaimer
   required.
5. **`agent_angle` (new, Mon/Wed/Fri 12:30 ET).** Agentic-trading education —
   deterministic 9-angle rotation (day-of-year modulo), mirrors the landing
   hero. No tickers, no invented numbers (writer constrained to the angle's
   talking points). No disclaimer (not a performance recap).
6. **Report cron fix + daily.** 06:30 Mon → **07:45 ET Mon–Fri** (generator
   runs 07:00 Mon–Fri). The report post carries the whitelisted
   `/reports/<date>` URL — it is the SEO click-through.
7. **Metrics loop.** New `POST /collect_metrics` endpoint (deterministic, no
   LLM) + nightly cron → one batched `get_tweets` call (X read quota is tiny)
   → BQ `x_post_metrics` (explicit DDL schema, **never autodetect** — the
   2026-07-02 outage class). Steers future cadence decisions with data.
   **Deploy gotcha (2026-07-09):** tweepy defaults v2 reads to app-auth
   (bearer) — with OAuth 1.0a-only creds `get_tweets` 401s until
   `user_auth=True` is passed. Verified working post-fix (17 tweets
   snapshotted, impressions populated). NOTE: `latestReadyRevisionName` turns
   ready before traffic shifts — a retest right at that moment hit the old
   revision and briefly misdiagnosed this as an API-tier limitation.
   Baseline captured at launch: ~57 impressions/watchlist post, 2 likes
   across 10 days — the quantified "posting into the void" starting point.
8. **Per-request `dry_run`** on `POST /post` — validate any post type
   end-to-end on the live service without publishing.
9. **`signal`/`callback`/`scorecard` stay PAUSED.** The signal template's CTA
   was cleaned (paper trail), but the pick stays off the public feed.

**Cadence after revamp:** ~18 auto posts/week (was ~6, half of them broken):
5 watchlist, 5 report, 5 pool_outcomes, 3 agent_angle, 1 life_stats.

**Owner-manual items (X API has no pinning endpoint):** unpin the 2026-03-14
tweet, pin the new distribution-stat tweet, refresh bio/header. The reply game
(~10/day) remains the main profile-view lever and cannot be automated (ToS).

**Not done / explicitly rejected:**
- Premarket watchlist timing — kept at 10:00 ET. Posting the pool before the
  ~09:45 pick exists would make pick-overlap possible and re-opens scalping
  optics; revisit only with owner sign-off.
- Any pick-revealing or single-ROI-headline post (GIGO pool composite is
  negative; we publish distributions, not a tradeable index).
