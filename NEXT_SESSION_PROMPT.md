# Next Session Prompt

**Last session wrapped:** 2026-04-22 (webapp launch cleanup — paid tier now live and crawlable)
**Current policy:** V5.3 "Target 80" (unchanged; no execution-policy edits in this session)
**Status:** Paid tier LIVE. E2E Stripe + Firebase Auth + WhatsApp provisioning verified end-to-end. SSR is fully crawlable for AI agents and search engines. All copy aligned to One Promise.

---

## Before you do anything

Read in this order:

1. `CHEAT-SHEET.md` — operator one-pager (unchanged; still current).
2. `docs/TRADING-STRATEGY.md` — canonical execution policy.
3. `docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md` — master monetization plan.
4. `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` — **the 90-day blog schedule is in §7. Critical for GTM planning.**
5. `docs/DECISIONS/2026-04-22-launch-cleanup.md` — **decision record for this session's webapp work.** Covers the SSR crawlability fix, the origin bug, the auth-bypass hardening, and the copy-retirement sweep.
6. `docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md` — background on the monetization decisions.

Do NOT read first: `PROMPT-*` docs, `_archive/`, or any pre-2026-04 research summaries. Those are historical, not authoritative.

---

## Evan's stated intentions for next session

Two workstreams, both in the user's zone more than the code zone:

### 1. Email flow

The welcome-email path is fully working end-to-end (Mailgun accepted, recipient MX returned 250 OK, Firestore + whatsapp_allowlist provisioned). But recipient-side quarantine is eating mail on certain corporate recipients (Proofpoint at `owenec.com` held Evan's own two welcome messages on 2026-04-22). Work to plan:

- Proofpoint allow-list for `mg.gammarips.com` (Evan's side — admin action on his owenec tenant).
- Assess whether to enable DMARC on `gammarips.com` (currently empty). Weigh trade-off: DMARC tightens legit deliverability once fully aligned, but can increase rejections if any legacy sender isn't covered.
- Warm-up plan for the sending domain — right now `mg.gammarips.com` has SPF + MX + one DKIM selector (`k1._domainkey`) but is cold reputation-wise. Gradual volume ramp, keep complaint rate near zero.
- Audit the four scheduled cron emails in `apphosting.yaml` against current V5.3 reality:
  - `send-daily-setups` (weekday 20:00 ET) — copy fixed today but the data source is probably empty under `profitscout-fida8` (the old `winners_dashboard` table is V2-era per `.claude/rules/scripts-research.md`).
  - `send-top-pick` (weekday 08:00 ET) — needs verification that it's reading the current `todays_pick` Firestore doc, not a stale table.
  - `send-midday-movers` (weekday 13:00 ET) — probably also V2-era.
  - `send-feedback-requests` (daily 10:00 ET) — copy fixed today.
- Consider retiring email crons entirely if the WhatsApp channel is the primary distribution. If we keep them, they need clear V5.3 alignment and real data.
- End-state target: a 7-email lifecycle (welcome, day-3 reminder, trial ending, trial converted, churn intent, churn completed, win-back) that fires automatically off Stripe webhook and Firestore state — not time-based crons.

### 2. 100-day GTM plan

Evan is now the distribution bottleneck, not the product. The site works, the paid tier works, the product story is clear. What's missing is traffic.

Material for next session:
- `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` §7 has a **13-post 90-day blog schedule** already drafted. That's the backbone.
- Historical distribution data: **March 2026 had 7 signups**, all clustered in a 4-day window 3/10–3/13 driven by X posts. Zero retention (all 7 hit the `/dashboard` 404 that got fixed 2026-04-22 — so the zero retention was the bug, not disinterest). One more 3/25 signup after delayed discovery of same content. **When Evan stopped X posting on 4/6, signups went to 0 immediately.** X is the proven channel.
- Search Console: **5,091 impressions / 19 clicks (0.37% CTR) in March**. Almost certainly explained by the SSR loader bug (fixed this session) — crawlers indexed a spinner, users clicked and bounced. Expect CTR to improve over 2–4 weeks as Google re-crawls with real content.
- Pricing: Free / **Pro $39/mo with 7-day trial** / Founder $29/mo lifetime for first 500 (`FOUNDER29` promo code).
- Compliance frame: *SEC v. Lowe (1985)* publisher exclusion. Cited in `docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md` §6. Don't publish real-money track record until end-of-May when V5.3 has ≥30 closed trades.

100-day GTM framework to propose (starting points):
- **Days 1–14 (launch ramp):** resume X at pre-4/6 cadence. Announcement thread pinned. 2–3 methodology posts/week. No paid tier hard sell yet — lead with paper-trading transparency.
- **Days 15–30 (blog foundation):** ship first 4 posts from the 90-day schedule. Prioritize `/how-it-works` long-form companion ("How V5.3 Works") and a "reading options flow" primer.
- **Days 31–60 (Reddit + cross-posting):** introduce r/options, r/thetagang, r/Daytrading. Methodology content, no promotion. Skip r/wallstreetbets (copy plan flags as Month 3+).
- **Days 61–90 (first track record milestone):** ≥30 closed V5.3 trades landed. Scorecard post, breakdown of hits and misses. That's the inflection point from "here's how we built it" to "here's what it's done."
- **Days 91–100 (first evaluation gate):** measure: paid conversions, trial → paid rate, churn %, top acquisition sources. Decide whether to double-down on X, move aggressively onto Reddit, or open paid acquisition.

---

## What happened in this session (2026-04-22)

### Launch-critical fixes (all shipped to production)

- **Firebase API key was quote-wrapped in the Firebase App Hosting console override**, causing every sign-up to 400 with `auth/api-key-not-valid`. Root cause: Evan's Firebase App Hosting console had `NEXT_PUBLIC_*` env overrides with YAML-literal `"` characters baked into the strings. Deleted the 11 `NEXT_PUBLIC_*` overrides (they duplicate `apphosting.yaml`) and stripped quotes on the remaining server-side secrets. Firebase sign-up now works.
- **Stripe Secret Key had the same quote bug** — Stripe SDK rejected it with `StripeAuthenticationError`. Fixed by de-quoting.
- **Checkout `/api/checkout` 500'd** because `firebase-admin` was lazy-init only and the route's side-effect `import` never triggered `initializeApp`. Exported `getAdminApp` and called `getAuth(getAdminApp())` explicitly.
- **Stripe success URL landed on `https://0.0.0.0:8080`** (Cloud Run internal address). Fixed by resolving origin via `X-Forwarded-Host` / `X-Forwarded-Proto` headers instead of `req.nextUrl.origin`.
- **SSR rendered a full-screen loader spinner for every page** because `root-layout-client.tsx` had `if (loading && !user) return <Loader/>` — and during SSR, Firebase Auth's `loading` is always true. Every AI crawler (GPTBot, ClaudeBot, PerplexityBot, Bing AI) was seeing a spinner and nothing else. **Deleted the gate.** Biggest single SEO unlock of the session.
- **`/dashboard` 404 on every sign-up** — `use-auth.tsx` defaulted redirects to `/dashboard` which doesn't exist. All 7 March users bounced here. Fixed to `/`.
- **Forced Stripe auto-redirect on signup** (`auth/processing/page.tsx` shoved every new user into Stripe after 2.5s). Killed. New users now land on `/about?welcome=1&session_id=...`.

### Onboarding + post-checkout surface

- **`/about` rewritten as dual-purpose surface.** Anonymous visitors see E-E-A-T + methodology + founder/GammaMolt cards + pricing. Post-checkout visitors hitting `?welcome=1&session_id=…` see a prepended "You're in. Here's your 09:00 ET routine" banner with the **WhatsApp invite link embedded directly** (from the `WHATSAPP_GROUP_INVITE_URL` secret). Email-in-inbox is now belt-and-suspenders, not critical path.
- `/account` left as a utility page (subscription management, password reset). Not the post-checkout landing.

### Copy / branding cleanup

- `ceo@gammarips.com` → `evan@gammarips.com` across 10 files (layout, developers, privacy, terms, footer, contact form, pricing client, llms.txt, ai-plugin.json, mailgun templates).
- Mailgun default FROM display: `GammaRips <ceo@…>` → `Evan Parra <evan@…>` (personal-name sender beats brand for transactional deliverability).
- `@mention` → `@gamma` (the actual WhatsApp tag OpenClaw listens for) across pricing pro-features, welcome banner, and all Mailgun templates. Grammar rewrapped to read natural.
- GammaMolt card on `/about` retitled to "Chief Intelligence Officer" with Evan's new copy (Claude Opus via OpenClaw, real-time BigQuery queries, not canned responses).
- **Retired `"Ripper"` and `"Daily Playbook"` zombie language** — the auth-dialog popup and three Mailgun email templates (feedback-request, daily-setups, insider-invite). One Promise aligned.
- `/signals` page got a two-paragraph intent intro — retargets SEO away from per-ticker research queries (AppLovin buyback, Hess production data were March's top indexed queries) toward product-category queries (daily options signals scanner, unusual options activity, one trade a day).
- `/how-it-works` rewritten top-to-bottom — dropped "The Overnight Edge" alias and the fabricated FSLY 9/10 signal example; now describes the real V5.3 pipeline (three-gate enrichment, 09:00 ET notifier stack, execution rules).
- `/arena` gated with a noindex placeholder — stripped "7 AI Models" / "Claude, GPT, Grok, Gemini, DeepSeek, Llama, Mistral" metadata that was SEO-poisoning launch day crawls. Removed from global nav. Phase 4 agents-vs-V5.3 scoreboard deferred to post-May when the ledger has ≥30 closed trades.

### Security hardening

- `FIREBASE_PRIVATE_KEY` was being `console.log`'d on every admin init — scrubbed.
- `/api/debug-firebase` route deleted (dead code, imported a non-exported symbol).
- `createCheckoutSession` server action now takes an ID token instead of a raw `uid` — verifies via Firebase Admin before deriving uid. Closes the auth bypass where any client could call it with any uid.
- Firebase API key restricted by HTTP referrer — `gammarips.com/*`, `*.gammarips.com/*`, `*.hosted.app/*`, `localhost:3000/*`.

### Activation / email

- `<EmailCapture />` dropped on the homepage (before FAQ, default variant) and the footer sitewide (minimal variant, form only). Low-friction activation ladder that sidesteps the Firebase-account → Stripe funnel.
- Confirmed via Mailgun Events API that welcome emails ARE delivered at the SMTP layer (250 OK from recipient MX). The gap is recipient-side quarantine (Proofpoint at `owenec.com` held both of Evan's welcome messages 2026-04-22).
- Suppression lists clean — no bounces/unsubscribes/complaints on either `eparra@owenec.com` or `eraphaelparra@gmail.com`.

### Infrastructure + deploy hygiene

- Confirmed `gammarips.com` is in Firebase Auth Authorized Domains.
- Firebase API key restriction in place.
- Identified that the existing GA4 property `G-KPGTJDBC6N` is attached to a "ProfitScout" stream pointing at `profitscout.app` (orphan domain). Decision: nuke it and create a fresh `gammarips.com` property in a Google account Evan controls long-term. **Pending on Evan.**

---

## What's still open

### Blocked on Evan (console / admin, not code)

1. **GA4 fresh property** — create in a Google account you own, add a web data stream for `gammarips.com`, mark `purchase` as a key event, create a Measurement Protocol API secret. Paste the new `G-XXXXXXXXXX` measurement ID + the MP secret to the next session; Claude swaps `apphosting.yaml` + the hardcoded `G-KPGTJDBC6N` in `src/app/layout.tsx:44,72-90` and updates the `GA_API_SECRET` console env var.
2. **Proofpoint allow-list for `mg.gammarips.com`** on your owenec.com tenant. Admin action in Proofpoint Essentials. Tracked as task #23.
3. **Google Programmable Search Engine** at `programmablesearchengine.google.com` — copy CX ID, `gcloud secrets create GOOGLE_CSE_ID --data-file=-`. Unblocks the `web_search` MCP tool. From prior session handoff, still outstanding.
4. **WhatsApp group wiring** — create private group, link OpenClaw's number, mount `OPENCLAW_GATEWAY_URL`, `OPENCLAW_HOOKS_TOKEN`, `OPENCLAW_GROUP_JID` as secrets. From prior session handoff, still outstanding (though Evan has been joining manually for testing today).

### Nice-to-have / post-launch

- **Secret Manager migration** — all remaining server-side secrets in the Firebase App Hosting console (Stripe, Mailgun, Polygon, FMP, Gemini, Firebase Admin, CRON, MCP, GA_API) should be migrated from console overrides to Google Secret Manager so `apphosting.yaml`'s `secretEnv:` block becomes the single source of truth. Tracked as task #19. Non-urgent unless secrets rotate.
- **DMARC on `gammarips.com`** — currently empty. Adding `p=none` first to monitor, then tightening to `p=quarantine` once deliverability stabilizes.
- **JSON-LD re-verify** — flagged in prior session but SSR bug was the actual cause. Likely resolved. Spot-check via `curl -s -H 'Cache-Control: no-cache' https://gammarips.com/pricing | grep 'application/ld+json'` when convenient. Tracked as task #8.

---

## Key facts to hold in memory

- **Paid tier is LIVE.** First real subscription (Evan's own) created 2026-04-22 14:44 UTC via `FOUNDER29` on a live card. Stripe webhook fired, Firestore `users/{uid}.plan = "pro"`, `whatsapp_allowlist` provisioned, Mailgun 250 OK.
- **Welcome email deliverability**: Mailgun delivers to recipient MX. Downstream quarantine (Proofpoint, Gmail Promotions) is recipient-side. `/about?welcome=1` now carries the WhatsApp invite inline, so the email is backup, not critical path.
- **SSR is now fully crawlable.** The previous root-layout-client loader gate was rendering nothing but a spinner to non-JS crawlers. That fix (commit `d78efd29`) is the single highest-leverage SEO change ever made on this project. Expect 2–4 weeks for Google to re-crawl with real content.
- **V5.3 ledger has ~0 closed trades as of launch.** Track record narrative is a 30–45 day wait. Nothing marketed as real-money P&L until ≥30 closed trades — that's end of May at earliest.
- **X is the proven distribution channel.** March 2026 = 7 signups from a 4-day X cluster (3/10–3/13); April 2026 (after X stopped 4/6) = 0 signups. Resume is the fastest lever.
- **Pricing**: Free / Pro $39/mo with 7-day trial / Founder $29/mo lifetime for first 500 (promo code `FOUNDER29`).
- **@gamma** is the WhatsApp tag for the chat agent (not `@mention`, not `@GammaMolt`). OpenClaw listens for `@gamma`.

---

## DO NOT do

- Do NOT modify V5.3 execution policy. Entry 10:00 ET / stop −60% / target +80% / 3-day hold / exit 15:50 ET day-3. Pinned in `docs/TRADING-STRATEGY.md` and `forward-paper-trader`.
- Do NOT add gates to `forward-paper-trader` (rule in `.claude/rules/forward-paper-trader.md`). Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT use FMP. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1` — frozen.
- Do NOT reference retired aliases in new copy: "The Overnight Edge", "GammaRips is Free", "7 AI Models", "score >= 6", "8:30 AM", "premium signal", "$49/$149 pricing", "Daily Playbook", "Ripper", "interactive dashboard".
- Do NOT publish real-money track record until there are ≥30 closed V5.3 trades (end of May at earliest). Paper-trader stays the only marketable source until then.
- Do NOT re-add `ceo@gammarips.com` — that's a dead-letter address now. `evan@gammarips.com` is the public contact. `GammaRips <ceo@…>` display name is also retired — use `Evan Parra <evan@gammarips.com>`.
- Do NOT re-introduce `@mention` — the chat agent only responds to `@gamma` in the WhatsApp group (OpenClaw binding).
- Do NOT paste live secrets into chat. Secret rotation debt accumulates fast. If diagnosing a secret-related issue, work from names, line numbers, and first/last 4 chars.

---

## Deployed revision sheet (webapp)

| Commit | Branch | Revision | Deployed | Summary |
|---|---|---|---|---|
| `e7c3aa0f` | main | build-2026-04-22-008 (pending rollout) | 2026-04-22 ~20:00 UTC | Retired "Ripper" / "Daily Playbook" copy across auth modal + 3 email templates |
| `d78efd29` | main | build-2026-04-22-007 | 2026-04-22 19:51 UTC | **SSR crawlability fix** — removed root-layout-client loader gate |
| `313c5765` | main | build-2026-04-22-006 | 2026-04-22 19:45 UTC | Five-task batch: signals SEO intent copy, how-it-works V5.3 rewrite, auth hardening (createCheckoutSession ID-token), EmailCapture on homepage+footer, dead /api/debug-firebase deleted |
| `d591cbe5` | main | build-2026-04-22-005 | 2026-04-22 ~17:30 UTC | Branding sweep: ceo@ → evan@, @mention → @gamma, GammaMolt copy, Mailgun default FROM → "Evan Parra" |
| `edf4b685` | main | build-2026-04-22-004 | 2026-04-22 15:18 UTC | WhatsApp invite link rendered directly on /about?welcome=1 |
| `2d56729f` | main | build-2026-04-22-003 | 2026-04-22 14:55 UTC | Origin bug fix (X-Forwarded-Host); /about rewrite with welcome banner |
| `7c1a4867` | main | build-2026-04-22-002 | 2026-04-22 14:38 UTC | Firebase Admin init fix; /dashboard → /; Stripe auto-redirect killed; /arena gated |
| `8b650b97` | main | build-2026-04-22-001 | 2026-04-21 21:30 UTC | Prior session: V5.3 copy rewrite + paid tier wiring |

Engine-side services (from prior session, no changes this session):

| Service | Revision | Deployed |
|---|---|---|
| signal-notifier | `signal-notifier-00007-pv9` | 2026-04-20 |
| enrichment-trigger | `enrichment-trigger-00032-2z4` | 2026-04-20 |
| forward-paper-trader | `forward-paper-trader-...` | 2026-04-20 |
| agent-arena | `agent-arena-...` | 2026-04-10 |
| overnight-report-generator | `overnight-report-generator-...` | 2026-04-10 |
| gammarips-mcp | `gammarips-mcp-00023-q8p` | 2026-04-20 |
| gammarips-webapp | `edf4b685` → `e7c3aa0f` (above chain) | 2026-04-22 |

Scheduler cron (unchanged since 2026-04-20):
- `overnight-scanner` — `0 23 * * 1-5` ET
- `enrichment-trigger-daily` — `30 5 * * 1-5` ET
- `agent-arena-trigger` — `0 6 * * 1-5` ET
- `overnight-report-generator-trigger` — `15 8 * * 1-5` ET
- `signal-notifier-job` — `0 9 * * 1-5` ET
- `forward-paper-trader-trigger` — `30 16 * * 1-5` ET
- `track-signal-performance` — `30 16 * * 1-5` ET
- `polygon-iv-cache-daily` — `30 16 * * 1-5` ET

---

## Subagents available in `.claude/agents/`

- **`gammarips-engineer`** — code cleanup, deployment fixes, BQ integration. Use for implementation work.
- **`gammarips-researcher`** — backtests, cohort analysis, BQ diagnostic reads. Read-only.
- **`gammarips-review`** — audits for lookahead bias, data leakage. **ALWAYS invoke before any forward-paper-trader or signal-notifier diff deploys.**

For GTM and email-flow work specifically: spawn `general-purpose` or `Explore` subagents as needed. Mailgun Events API is queryable via `MAILGUN_API_KEY` from `/home/user/gammarips-webapp/.env` if diagnostic queries are needed (e.g., "what was the delivery status for message-id X?"). See 2026-04-22 session for the shape of those queries.

---

*End of handoff. First action next session: confirm with Evan which of the two workstreams (email flow, 100-day GTM) to start on. Email flow is more code/config; GTM planning is more doc/strategy work.*
