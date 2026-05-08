# 2026-05-07 — Receipt-only content strategy + FMP earnings migration

## TL;DR

- **Content pivot**: X SIGNAL post moved to **Path B (anchor-only)** — names the
  ticker + direction + score, *withholds* contract/strike/expiration. The
  paid product (curated single pick with full bracket) stays exclusive to
  email/WhatsApp. Path B exists so closing-trade callbacks have a public
  timestamped post to QRT as a *receipt*, not a claim.
- **Reddit pivot**: templates rewritten to **distraction-frame** — short
  (~230 chars), first-person voice, no methodology walk-through, no
  literature citations. Trades on entry, receipts on close. Long
  Augustin-et-al-cited posts get karma-killed; receipts compound.
- **Infrastructure fix**: FMP earnings calendar — legacy `/api/v3/*`
  endpoints retired by FMP on 2025-08-31, all returning 403. Migrated to
  `/stable/earnings-calendar` and moved API key from query param into
  `apikey:` header so it stops leaking into Cloud Logging error lines.
- **Cron restructure**: misnamed `x-poster-signal-0905` (body said
  watchlist) deleted; replaced with two correctly-named jobs.

## Why this happened today

NVAX was the cohort's first trade and was about to be born without a public
anchor. Today's morning failure (FMP 403 → signal-notifier fail-closed →
todays_pick wrote `skip_reason=earnings_calendar_unavailable` → x-poster's
9:05 ET cron read empty pick → no SIGNAL post fired) exposed two latent
issues at once:

1. The FMP migration (root cause).
2. The schedule race between signal-notifier (07:30 ET) and x-poster signal
   cron (09:05 ET) — even when signal-notifier eventually wrote the pick, the
   cron had already fired against an empty state.

Then a deeper editorial question surfaced: *should* the X SIGNAL post
publicly broadcast the V5.3 contract at all? Past posts (4/29 $MDB, 4/30
$LITE) had been leaking strike/expiration/mid into public X — directly
contradicting the "paid email/WhatsApp = curation" memory. Path B fixes the
contradiction and unlocks the receipt-callback chain.

## Decisions

### 1. SIGNAL post type → Path B

**File:** `x-poster/app/agent.py` (template lines ~237–245, writer rules ~224)

Old template (broadcasts contract):
```
🔥 GammaRips Signal — <scan_date>
$<ticker> <direction> (Score: <score>)
<contract_emoji> <contract_type> $<strike> | Exp: <expiration_display>
💰 Mid: $<mid> (~$<mid_total_cost>/contract) | <moneyness_pct>% OTM
📊 V/OI: <vol_oi> | DTE: <dte> | V5_3_TARGET_80
```

New template (Path B anchor):
```
📍 V5.3 pick today — $<ticker> <direction> (Score <score>)

Contract, entry, stop, target → email subscribers only.
https://gammarips.com
```

URL whitelist (`libs/gammarips_content/.../compliance.py`) extended to allow
`https://gammarips.com` root in addition to the existing
`/reports/<YYYY-MM-DD>` allowlist. Pure additive change; doesn't affect blog
or report post types.

### 2. Cron restructure

| Before | After |
|---|---|
| `x-poster-signal-0905` 09:05 ET, body=`{"post_type":"watchlist"}` (misnamed) | DELETED |
| — | `x-poster-signal-0800` 08:00 ET Mon-Fri, body=`{"post_type":"signal"}` |
| — | `x-poster-watchlist-0905` 09:05 ET Mon-Fri, body=`{"post_type":"watchlist"}` |

The 30-minute gap between signal-notifier (07:30 ET) and x-poster signal
(08:00 ET) gives `todays_pick` time to settle before x-poster reads it.

### 3. Reddit templates — distraction-frame

**File:** `reddit-poster/app/templates.py` (full rewrite)

**Trade idea (anchor on entry)** — ~230 chars, 4 short paragraphs:
```
Overnight options-flow scan flagged $NVAX bullish today.

Paper-trade entry at 10:00 ET. Bracket: -60% stop / +80% target / 3-day hold.

Receipt going up when it closes in 3 trading days, win or lose.

Full ledger at gammarips.com.
```

**P&L receipt (post on close)** — ~210 chars:
```
In 2026-05-07 at 10:00 ET on overnight options flow.
Out 2026-05-12 on +80% target hit.

V5.3 cohort so far: 1/1.

Paper-trade. Not advice. Past performance does not guarantee future results.

gammarips.com
```

Char floor for `trade_idea` dropped 400 → 200 in `compliance.py` so genuinely
tight posts pass the rubric. `tools.fetch_recent_close()` extended to
include `wins_so_far` + `closed_so_far` from `cohort_stats/current` so the
receipt can render the running tally.

Removed: methodology walkthroughs, literature citations (Augustin /
Muravyev / De Silva), structured stat-block lines (`Volume/OI: 3.2x`),
promotional footers ("Tracking V5.3 / Target-80 paper bracket").

DRY_RUN=true is the operating mode — drafts land in
`gs://gammarips-reddit-drafts/{date}/trade_idea_{subreddit}.md`. Manual
cross-posting from there.

### 4. FMP earnings calendar — `/stable/` migration

**File:** `signal-notifier/main.py:128`

FMP retired `/api/v3/*` on 2025-08-31. All legacy endpoints now return 403
"Legacy Endpoint" for any key. New URL `/stable/earnings-calendar` works
with the same key, same `from`/`to` params, same `{symbol, date, ...}`
response shape.

Also moved the API key out of the query string into an `apikey:` header.
Same authentication strength, but error logs no longer leak the key in URL
echoes (the old code was logging
`https://...?from=X&to=Y&apikey=H9p7Tz...` on every 4xx/5xx).

## NVAX — first cohort trade, anchor planted manually

NVAX BULLISH was today's pick, entered 10:00 ET 5/7, exits 5/12. Because
the 9:05 ET cron fired before the FMP fix landed, no signal post auto-fired.
Anchor planted manually via direct `POST /post {"post_type":"signal"}` after
the new template + URL whitelist deployed. Tweet ID `2052419298035900592`.
Receipt callback on 5/12 will QRT this tweet.

## Things NOT changed

- V5.3 execution policy: entry 10:00 ET, −60% stop, +80% target, 3-day
  hold, exit 15:50 ET day-3. Unchanged.
- Trader-side gates: still none. Quality gates remain at
  `enrichment-trigger` + `signal-notifier`.
- Disclaimer policy: unchanged. Signal/standby/watchlist/teaser/report =
  no disclaimer. Win/loss/callback/scorecard = `⚠️ Paper-trade. Not advice.`
- Park-mode: still active. 30-trade gate threshold unchanged.

## Files changed (full list)

- `signal-notifier/main.py` — FMP `/stable/` URL + header auth
- `x-poster/app/agent.py` — SIGNAL template Path B + writer URL rule
- `libs/gammarips_content/gammarips_content/compliance.py` — URL whitelist
  extended; (separately) `_enforce_one_cashtag` already deployed in earlier
  commit `e3089e8`
- `reddit-poster/app/templates.py` — full rewrite
- `reddit-poster/app/compliance.py` — char floor 400→200 for `trade_idea`
- `reddit-poster/app/tools.py` — `fetch_recent_close` enriched with cohort
  tally
- `reddit-poster/deploy.sh` — `^@^` env-var delimiter (commas in
  DEFAULT_SUBREDDITS), `--clear-secrets` to drop missing Reddit creds
  binding
- `gammarips-webapp/src/components/landing/hero.tsx` and 4 siblings —
  hero/footer/title copy `9 AM` → `7:30 AM ET`
- Deleted: Cloud Scheduler job `x-poster-signal-0905`
- Created: Cloud Scheduler jobs `x-poster-signal-0800`,
  `x-poster-watchlist-0905`
- Created: GCS bucket `gs://gammarips-reddit-drafts`

## Revisions deployed

- `signal-notifier-00015-7fp`
- `x-poster-00031-c2b`
- `reddit-poster-00004-2qd` (first deployment of this service)
- `gammarips-webapp` via Firebase App Hosting from `main` commit `5d736023`

## Pending (user-side)

- Reddit live-posting credentials (4 Secret Manager entries) — only needed
  to flip `DRY_RUN=false`. Manual cross-posting from GCS drafts is the
  current operating mode and works without these.
- FMP key rotation — leaked in Cloud Logging URL between ~11:30–14:30 UTC
  today. Free-tier key, rotation is hygiene, not crisis.
