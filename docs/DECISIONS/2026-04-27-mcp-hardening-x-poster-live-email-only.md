# 2026-04-27 — Decision Bundle

Single doc covering four meaningful calls landed in one session. Each is a
small entry in its own right — bundled here because they're causally linked.

---

## Decision 1 — `gammarips-mcp` is now the SOLE attack surface for paying-customer interactions

**Trigger.** OpenClaw `gammarips-bot` agent shipped with isolated workspace
(no filesystem, no exec, 17 tools denied). Every paid-group `@gamma` mention
routes through this bot, which can ONLY interact with the world via
`gammarips-mcp` tools. Prompt-injection blast-radius is therefore bounded
by whatever the MCP exposes.

**Action.** Hardened the MCP server (`gammarips-mcp`, repo
`github.com/DevDizzle/gammarips-mcp`):

- **Sanitized errors** — `utils.safety.safe_error()` redacts BQ table paths,
  GCP project IDs, service-account emails, googleapis URLs, Polygon API
  keys from any exception surfaced to callers. Full traceback still logs
  server-side at WARNING.
- **Bounded query inputs** — `utils.safety.clamp()` enforces tight ranges
  on every caller-controlled `limit` / `days` / `lookback_days` (BQ
  cost-attack defense).
- **Per-IP rate limit middleware** — token bucket. 60 req/min default,
  10 req/min for the paid Google CSE-backed `web_search`. Verified live
  (20 of 25 rapid requests returned 429).
- **Whitelisted schema introspection** — `get_enriched_signal_schema` no
  longer dumps raw `INFORMATION_SCHEMA`. Only 18 explicitly-whitelisted
  public-safe columns. Future internal columns can't auto-leak.

**3 new tools** added to support the bot's chat surface:

| Tool | Purpose |
|---|---|
| `get_market_calendar_status` | NYSE calendar via `pandas_market_calendars`. Eliminates the "is the market open?" hallucination class. |
| `get_signal_explainer` | Hardcoded plain-English lookup for 18 GammaRips field names. Deterministic — no LLM in the path. |
| `get_historical_performance` | V5.3 ledger aggregate over a lookback (`forward_paper_ledger`, distinct from `signal_performance`). |

Total tools: **18** (was 15). Trust model documented in
`gammarips-mcp/SECURITY.md`. Deployed revisions: `gammarips-mcp-00026-x2j`
(commit `097accd`) → `gammarips-mcp-00027-mcl` (added `GOOGLE_CSE_ID`
secret mount).

**Why this matters.** The MCP is now treated as a public API. Every new
tool added in the future MUST go through `safe_error` / `clamp` and add
to `_PUBLIC_SCHEMA_COLUMNS` if it surfaces BQ schema. Documented in
`SECURITY.md` so future contributors don't drift.

---

## Decision 2 — `x-poster` is LIVE on @gammarips. 5 schedulers, Option B overlay

**Trigger.** Prior session shipped `x-poster` DRY_RUN=true with 4 smoke
scenarios passing. Today: ship Option B (PIL ticker overlay) + flip to live
posting.

**Action.**
- `_composite_ticker_overlay()` in `x-poster/app/tools.py` — 180pt `$TICKER`
  white + 60pt direction badge in lime `#a4e600` (BULLISH) / red `#cc3333`
  (BEARISH), drop-shadow for legibility on any backdrop.
- Bundled Space Grotesk variable TTF into `x-poster/assets/`. Dockerfile
  now copies `./assets` into the runtime image.
- Writer prompt now emits `ticker` + `direction` in draft JSON.
- `generate_image()` accepts both args; applies overlay only on
  `signal/win/loss/callback` post types.
- DRY_RUN flipped to `false`. Live revision `x-poster-00017-ggj`.
- 5 Cloud Scheduler jobs created:

| ET Time | Job | Type |
|---|---|---|
| Mon-Fri 08:30 | `x-poster-report-0830` | report |
| Mon-Fri 09:05 | `x-poster-signal-0905` | signal (or standby fallback) |
| Mon-Fri 12:30 | `x-poster-teaser-1230` | teaser |
| Mon-Fri 16:45 | `x-poster-callback-1645` | callback (win/loss; skip-on-empty) |
| Fri 17:00 | `x-poster-scorecard-fri-1700` | scorecard (3-tweet thread) |

**Why 16:45 not 16:00 for callback:** `forward-paper-trader-trigger` writes
today's exits at 16:30 ET. Posting at 16:00 would have read a stale
ledger every day. 15-min buffer.

**Skip-on-empty guard.** If `callback` fires on a no-closes day, Publisher
detects writer ticker=null and skips publishing entirely (no hollow
"called it" recap). Verified live this afternoon.

**First live tweet posted.** `2048829378331558255` —
"🛑 GammaRips Standby — 2026-04-27" (no V5.3 pick cleared overnight).

---

## Decision 3 — Email-only delivery for paid product. WhatsApp deprecated.

**Trigger.** A test trial-end email got Proofpoint-stripped at Evan's
work tenant. Surface diagnosis exposed broader question: do we keep the
WhatsApp signal-delivery channel or simplify to email?

**Action.** Locked email-only as the V1 distribution surface for paid
subscribers. WhatsApp is no longer part of the paid funnel.

**Why.** Three inter-locking reasons:

1. **WhatsApp can't programmatically de-provision on cancel.** Stripe
   `customer.subscription.deleted` would have to email Evan to manually
   kick the user. Unworkable at scale.
2. **OpenClaw bot in the paid group introduces prompt-injection blast
   radius the brand can't survive at 100 followers.** Even with
   sandboxing + the hardened MCP above, the failure mode of a
   public jailbreak Twitter screenshot is asymmetric.
3. **Email already works, with deliverability nearly fixed.** Mailgun
   is wired, DMARC `p=none` is live (Mailgun-managed),
   `mg.gammarips.com` was added to Evan's Proofpoint allow-list today.

**Implication.** The paid-tier "differentiator" is no longer "talk to
the agent." It's "the deterministic engine + the email cadence + the
methodology transparency." Phase 2 may re-introduce a chat surface
post-track-record (≥30 closed V5.3 trades) once the failure-mode
calculus is favorable.

---

## Decision 4 — Webapp `/signals/[ticker]` route killed for SEO hygiene

**Trigger.** Audited remaining "Tomorrow Morning, Know What Smart Money
Did Tonight" copy across the webapp during a footer cleanup. Found
`src/app/signals/[ticker]/signal-client.tsx` rendering it via the
default `EmailCapture` variant. Investigation: the per-ticker route
served 200 only for tickers in TODAY's overnight scan, 404'd otherwise
— URLs flickered 200↔404 daily.

**Action.**
- Deleted `src/app/signals/[ticker]/` directory entirely (page + client).
- Added `Disallow: /signals/` to `robots.ts` (belt-and-suspenders).
- Stripped dead `/signals/{ticker}` URLs from JSON-LD `ItemList` schemas
  on `/` and `/signals` (URLs would have pointed to 404s).
- Unwrapped the `<Link>` wrappers in `signals-table.tsx`, dropped the
  `ArrowRight` hover icon.
- Footer: relocated `<EmailCapture variant="minimal" />` directly under
  the brand tagline column.
- Homepage: deleted the duplicate `<EmailCapture />` (default-variant)
  section.

**Why kill, not stabilize:** stabilizing would have meant building
generateStaticParams + a "last-known-signal" Firestore lookup. That's
the "build a content machine for 5,000 ticker pages" arc — pure scope
creep at this stage. If per-ticker SEO becomes a real lever post
track-record, build it properly with stable URLs then.

**Build status.** `npm run build` clean, 22 routes (was 23). Pushed.
Firebase App Hosting auto-deployed.

---

## All commits pushed today

**`gammarips-engine` (master):**
- `7186933` — Option B ticker overlay + LIVE flip + 16:45 callback
- `4eb9a80` — blog-generator: embed schedule_slot + live_context inside post_outline (state-ref fix; deploy still pending)

**`gammarips-webapp` (main):**
- `84096115` — GA4 ID swap + 4 retired email crons removed
- `d3b53241` — kill `/signals/[ticker]` + dedupe signup CTA

**`gammarips-mcp` (main):**
- `da338b4` — feat hardening + 3 new tools
- `097accd` — ruff format + lint fixes

---

*Decision-bundle authored 2026-04-27 by gammarips-engineer Claude session. Source of truth for what shipped today.*
