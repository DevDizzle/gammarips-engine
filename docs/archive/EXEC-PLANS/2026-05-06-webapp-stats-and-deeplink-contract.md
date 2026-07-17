# Webapp contract: live-stats panel + signal-page deep links

> **Hand this doc to a webapp-repo session.** Self-contained. The engine-side work (Firestore writer, email/whatsapp deep-links, `cohort_stats/current` seed) is already deployed and verified. This file specifies what the webapp needs to render.

## Scope
Three changes, all on the public landing page (the page that shows today's pick):

1. **Live-stats row** — five tiles above today's-pick card. Visible to ALL users (logged-out included).
2. **Today's-pick card click target** — wrap the existing card in a link to `/signals/{TICKER}`.
3. **Empty-state behavior** — render zeros honestly, no hedge copy.

The per-ticker page at `/signals/{TICKER}` already exists (operator-confirmed via `https://gammarips.com/signals/CDW`). No new route needed; just wire the card to it.

## Live-stats row

### Data source: Firestore doc `cohort_stats/current`

Single document, single source of truth. Read on page load. Re-read on focus / pull-to-refresh if the framework supports it (otherwise daily refresh is acceptable — backend writes once per day at 09:00 ET).

**Schema** (all fields always present; empty-state values are zeros, not nulls):

| Field | Type | Meaning |
|---|---|---|
| `cohort_start` | string | ISO date — currently `"2026-05-07"`. Display as "Since May 7, 2026" or similar. |
| `policy_version` | string | `"V5_3_TARGET_80"`. Internal — don't render. |
| `as_of` | timestamp | Server timestamp of last refresh. Display as "Updated <relative time>" if you want a freshness signal. |
| `trades_closed` | integer | Tile #1 (Trades). |
| `trades_won` | integer | Internal — used to derive win_rate, don't render directly. |
| `win_rate` | float, 0.0–1.0 | Tile #3 (Win Rate). Multiply by 100 for display. |
| `total_invested_usd` | float | Tile #4 (Total Invested). Display as USD currency. |
| `total_pl_usd` | float | Could be negative. Used internally to derive ROI. |
| `roi_pct` | float | Tile #2 (ROI). Multiply by 100 for display. Color green if positive, red if negative. |

### Five tiles (left → right)

| # | Tile | Source field | Format | Empty-state (when `trades_closed = 0`) |
|---|---|---|---|---|
| 1 | **Trades** | `trades_closed` | integer | `0` |
| 2 | **ROI** | `roi_pct × 100` | `+12.4%` / `-3.1%` (sign + 1dp + %, color-coded) | `0.0%` (neutral color) |
| 3 | **Win Rate** | `win_rate × 100` | `64%` (rounded to nearest integer) | `—` |
| 4 | **Total Invested** | `total_invested_usd` | `$2,400` (USD, no cents at scale, with `$` and thousand separators) | `$0` |
| 5 | **Disclosure** | static | _"Paper-traded · Educational only · Not investment advice"_ | static (always shown) |

**Empty-state rationale:** When `trades_closed = 0` (the state immediately post-deploy), tiles 1, 2, 4 should still render the literal zero values. Tile 3 (Win Rate) is the only exception — `0/0` is undefined, so render `—`. Do NOT use copy like "Building track record" or "Coming soon." The user explicitly opted for honest reporting: if the numbers look bad, the funnel correctly does not convert.

### Visual hierarchy
Above the today's-pick card, full-width. Tile 5 (disclosure) styled smaller / lower-emphasis than tiles 1–4 — it's a legal note, not a stat. Mobile-responsive: tiles 1–4 in a 2×2 grid; disclosure spans the full width below.

### Color coding
- **ROI**: green (`#0a8f3c`) if positive, red (`#c62828`) if negative, neutral gray if zero. Match the BULLISH/BEARISH palette already used in `format_email_html`.
- **Win Rate**: neutral. Don't color-code — 50% isn't visually "neutral" and we don't want to imply that's the bar.
- **Trades, Total Invested, Disclosure**: neutral.

## Today's-pick card click target

Existing today's-pick card (renders ticker, direction, contract, strike, etc.) becomes a link to `/signals/{TICKER}` where TICKER is the ticker string from the Firestore doc `todays_pick/{scan_date or entry_day}`.

### Implementation
```jsx
<a href={`/signals/${pick.ticker}`} className="todays-pick-card-link">
  {/* existing card content */}
</a>
```

Add a small affordance — bottom-right of the card, e.g., `Read the full rationale →` in muted blue (`#1a73e8`). The email already uses this exact phrasing — keep it consistent.

### Hover state
Subtle elevation / border highlight. Cursor: pointer. The whole card is hot.

### Empty-state (no pick today)
The existing `has_pick: false` skip-state UI stays as-is. No link wrapping needed — there's no ticker to link to.

## Signal-page (`/signals/{TICKER}`) requirements

This page already exists; verifying it can handle the link from the email/webapp:
- Must accept any uppercase ticker symbol in the URL path.
- Must render gracefully if the ticker has no current scan / no current rationale (e.g., user manually visits an old ticker page after the signal expired).
- Should ideally surface: thesis paragraph, gate evidence (V/OI, moneyness, score, VIX state, earnings-clear status), full contract spec, the operator routine, and link back to the today's-pick card.
- For paid users, the rationale is the value-add. For free users (who land here from email forwards or social shares), the page should still render the gate evidence + thesis (since the pick itself is already public via the today's-pick card).

If the page does not yet handle deep-links from external referrers (email clients), audit Open Graph tags so social shares get a proper preview card.

## Visibility / auth

| Element | Logged-out | Logged-in (free) | Logged-in (paid) |
|---|---|---|---|
| Live-stats row (5 tiles) | ✅ Visible | ✅ Visible | ✅ Visible |
| Today's-pick card | ✅ Visible | ✅ Visible | ✅ Visible |
| Card click → `/signals/{ticker}` | ✅ Works | ✅ Works | ✅ Works |
| Signal-page rationale content | ✅ Public | ✅ Public | ✅ Public + paid badges |
| Email + WhatsApp delivery | ❌ | ❌ (unless they upgrade) | ✅ |

Per `project_email_only_delivery.md`: webapp shows the haystack free; paid users get the curated single pick via email + WhatsApp. The pick itself (the card content) is NOT a paywall — that's been public since 2026-04-30. Paid is the *delivery channel* (push to inbox + WhatsApp), not the *information*.

## Disclosure copy

Where it lives:
- **Stats panel tile #5:** `Paper-traded · Educational only · Not investment advice`
- **Today's-pick card footer (existing):** unchanged
- **Signal-page footer (existing):** unchanged

Per `feedback_no_disclaimer_no_images.md`: disclaimer goes on perf surfaces only, not on every page. The stats panel IS a perf surface, so the disclosure tile is correct here.

## Refresh cadence

Backend writes `cohort_stats/current` once per day at 09:00 ET (signal-notifier daily cron). Webapp can:
- Read on every page load (cheap, fresh-enough)
- OR read once on session start and rely on the daily cadence
- Either is fine; the 09:00 ET update is the only meaningful refresh window.

For developer testing, the `POST /refresh_stats` endpoint at `https://signal-notifier-406581297632.us-central1.run.app/refresh_stats` triggers an immediate refresh without sending email. Use it after manually inserting test rows into `forward_paper_ledger` if you want to validate the panel with non-zero values.

## Open questions for the webapp session
- Does the today's-pick card already read from Firestore `todays_pick/{scan_date}` or `todays_pick/{entry_day}`? Per `project_todays_pick_dual_write.md`, both keys are populated — the card should read whichever fires the entry-day cron.
- Are Open Graph tags configured for `/signals/{TICKER}`? The email link will be the most common click-source for paid users — make sure WhatsApp/email-client previews render cleanly.
- Is there a path to display the `as_of` timestamp from `cohort_stats/current` as relative time ("updated 4h ago") for trust? Optional but helps; the panel feels more alive.

## Done criteria
- Live-stats row renders all five tiles with values from `cohort_stats/current`.
- Today's-pick card click navigates to `/signals/{ticker}` for the current pick.
- Empty-state renders honestly (zeros, `—` for win rate, no hedge copy).
- Mobile-responsive (2×2 tiles + disclosure span).
- All visible to logged-out users.
