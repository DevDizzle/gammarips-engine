# 2026-04-22 — Webapp launch cleanup + SSR crawlability fix

**Decision type:** Execution (deploy / infra / copy). No execution-policy changes.
**Scope:** `gammarips-webapp` only. Engine services untouched.
**Deployed:** commits `7c1a4867` → `edf4b685` (8 builds, `gammarips-webapp-build-2026-04-22-001` through `008`).
**Reviewer:** Claude (session partner) + Evan (pair programming throughout).

---

## Context

Prior session (2026-04-20) landed the V5.3 copy rewrite and paid-tier wiring in the code, but left the launch blocked on unverified end-to-end payment flow, a cluster of console env overrides the user had accumulated, and a set of copy-alignment gaps. The initial goal for this session was narrowly the E2E Stripe test. That test exposed a cascade of latent bugs that had to be fixed in order before the test could complete.

## What failed, in order

1. **Sign-up hit `auth/api-key-not-valid`.** Cause: Firebase App Hosting console env var `NEXT_PUBLIC_FIREBASE_API_KEY` had literal `"` wrappers baked into the string value. The live bundle shipped `apiKey: "AIzaSyAqZq..."` (with quotes) rather than `apiKey: AIzaSyAqZq...`. Firebase receives `%22AIzaSy...%22` and rejects.
2. **Stripe Checkout call 500'd** with `StripeAuthenticationError`. Same quote-wrap bug on `STRIPE_SECRET_KEY` (and every other server-side console entry).
3. **`/api/checkout` 500'd** even after Stripe auth worked. Cause: `firebase-admin.ts` used lazy init, the route's side-effect `import '@/lib/firebase-admin'` never triggered `initializeApp`, and `getAuth().verifyIdToken` threw "default Firebase app does not exist."
4. **Stripe success URL landed on `https://0.0.0.0:8080`.** Cause: `req.nextUrl.origin` returns Cloud Run's internal listener address; Firebase App Hosting puts the real public host in `X-Forwarded-Host`.
5. **Every new signup 404'd at `/dashboard`.** Cause: `use-auth.tsx` defaulted the post-auth redirect to `/dashboard`, which doesn't exist anywhere in the repo. Root-caused the 2026-03 zero-retention data: all 7 March signups hit this 404.
6. **Every page served a loader spinner in SSR HTML.** Cause: `root-layout-client.tsx` wrapped all children in `if (loading && !user) return <Loader/>`. During SSR, Firebase Auth's `loading` is always true. AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Bing AI) saw nothing but a spinner on every route. This is likely the real explanation for March's 0.37% CTR on 5,091 impressions — crawlers indexed a loader; users clicked and bounced on blank content.

## What shipped

### Launch blockers (must-fix for paid tier to work)

- Deleted 11 `NEXT_PUBLIC_*` env overrides from Firebase App Hosting console so `apphosting.yaml` is the single source of truth for public config.
- Stripped quote-wrappers from the remaining server-side console secrets (~14 entries).
- Exported `getAdminApp()` from `firebase-admin.ts`; `/api/checkout` now calls `getAuth(getAdminApp()).verifyIdToken(token)` explicitly.
- `req.nextUrl.origin` replaced with `X-Forwarded-Host` / `X-Forwarded-Proto` fallback. `createCheckoutSession` server action updated the same way.
- `use-auth.tsx` default redirect `/dashboard` → `/`.
- **`root-layout-client.tsx` loader gate deleted.** 9-line delete, massive SEO unlock.

### Onboarding surface

- `/about` rewritten as dual-purpose: anonymous → E-E-A-T + methodology; post-checkout (`?welcome=1&session_id=...`) → prepended welcome banner with the WhatsApp invite link rendered directly from `WHATSAPP_GROUP_INVITE_URL`. Email becomes belt-and-suspenders, not critical path.
- `auth/processing/page.tsx` no longer force-redirects new users into Stripe.
- `/account` left as a utility page (subscription mgmt, password reset) — not the post-checkout landing.

### Security

- `FIREBASE_PRIVATE_KEY` `console.log` scrubbed from `firebase-admin.ts:42-43`.
- `/api/debug-firebase` route deleted (imported non-exported symbol; dead code).
- `createCheckoutSession` server action takes an ID token now, verifies via Firebase Admin before deriving uid. Closes the auth-bypass hole where any client could call it with any uid.
- Firebase API key restricted by HTTP referrer: `gammarips.com/*`, `*.gammarips.com/*`, `*.hosted.app/*`, `localhost:3000/*`.

### Copy retirement pass (retired aliases, cleaned language)

- `ceo@gammarips.com` → `evan@gammarips.com` across 10 files.
- Mailgun default FROM display: `GammaRips <ceo@…>` → `Evan Parra <evan@…>`.
- `@mention` → `@gamma` (the actual WhatsApp tag OpenClaw listens for) across auth modal, pricing pro-features, welcome banner, Mailgun templates. Grammar rewrapped to read natural.
- `"Ripper"` / `"Daily Playbook"` / `"interactive dashboard"` retired from auth-dialog popup + 3 Mailgun email templates (feedback-request, daily-setups, insider-invite).
- `/how-it-works` rewritten: deleted fabricated FSLY 9/10 signal example; replaced with the real V5.3 pipeline (three-gate enrichment, 09:00 ET notifier filters, execution rules).
- `/signals` page: two-paragraph intent intro above the tables that retargets SEO away from per-ticker research queries (AppLovin buyback, Hess production — March's top indexed queries) toward product-category queries ("daily options signals scanner", "overnight unusual options activity", "one trade a day with pre-set stop and target").
- `/arena` gated with a noindex placeholder; stripped "7 AI Models" / "Claude, GPT, Grok, Gemini, DeepSeek, Llama, Mistral" metadata. Removed from global nav. Phase 4 deferred to post-May.
- GammaMolt card on `/about` retitled "Chief Intelligence Officer" with Evan's new copy (Claude Opus via OpenClaw; real-time BigQuery queries, not canned responses).
- `<EmailCapture />` added to homepage (before FAQ) and footer (minimal variant, sitewide).

## What was deferred

- **GA4 property migration.** Existing `G-KPGTJDBC6N` is attached to a "ProfitScout" stream pointing at `profitscout.app` (orphan). Decision: nuke it and create a fresh `gammarips.com` property in an account Evan owns. Three-step process; code side (apphosting.yaml + `layout.tsx` hardcoded IDs + `GA_API_SECRET` rotation) is ready to ship as soon as Evan creates the new property.
- **GA4 MCP install.** Subagent evaluated `github.com/googleanalytics/google-analytics-mcp`. Read-only query interface over the Data API; cannot create properties. Value is post-traffic (4+ weeks). Defer install until the new property exists and has data.
- **Arena Phase 4 (agent head-to-head vs V5.3 ledger).** Evan proposed an agent-vs-strategy scoreboard as the /arena rebuild. Correct product instinct but wrong launch-week move: V5.3 has ~0 closed trades, so the scoreboard would read all zeros for 5+ weeks. Deferred to post-May when the ledger has meaningful sample.
- **JSON-LD re-verify.** Flagged in prior session as a regression. Almost certainly explained by the SSR loader bug (crawlers couldn't see the scripts). Likely resolved by the loader gate removal; defer to spot-check post-rollout.
- **Secret Manager migration** for remaining console-stored secrets. Non-urgent unless secrets rotate. Console overrides are now de-quoted and functional.

## Rationale for key calls

- **Why delete the SSR loader instead of fixing it?** The loader gate existed as a partner to an auto-redirect from `/` → `/dashboard` for logged-in users that was already deleted (see comment in `root-layout-client.tsx:10-12`). The redirect is gone; the loader is orphan. Keeping it serves no user; deleting it unlocks crawlability for every page. Zero downside observed.
- **Why NOT Secret Manager migration today?** Two separate reasons. (a) Several secrets had just been exposed in chat history earlier in the session; Evan explicitly declined rotation. Migrating pre-rotation propagates the same values into SM. (b) Console overrides, once de-quoted, work correctly. No operational reason to rush.
- **Why did `/about` absorb the post-checkout landing rather than spinning up `/welcome`?** Two surfaces for two audiences is URL sprawl; unified `/about` with a banner-on-welcome-param gives each audience a tailored first read without diluting SEO. E-E-A-T content is onboarding for a new subscriber — they read it with higher motivation than anonymous visitors.
- **Why leave the Proofpoint quarantine alone?** It's a recipient-side corporate email filter at `owenec.com`. Not a product bug. Evan's own testing inbox was the only corp recipient hit. Future real subscribers are overwhelmingly on Gmail/iCloud/Yahoo/Outlook consumer — none of which use Proofpoint by default. The welcome banner on `/about?welcome=1` now carries the WhatsApp invite link directly, so email is no longer on the critical path even when it's quarantined.

## Outcomes / verification

- End-to-end payment flow: Evan subscribed on a live card using `FOUNDER29`. Stripe subscription created, webhook fired (2x — Stripe retry), Firestore `users/{uid}.plan = "pro"` + `isSubscribed: true`, `whatsapp_allowlist/{uid}` provisioned, Mailgun delivered welcome email to recipient MX with `250 OK`.
- SSR verification: `curl https://gammarips.com/` body content went from 2.5 KB (loader shell only) → 128 KB (full page with Hero, EmailCapture, FAQ, GammaMolt card, disclaimers). Zero `lucide-loader-circle` in the rendered HTML.
- `/signals`, `/how-it-works`, `/about` all spot-checked live with correct V5.3 / One Promise copy.
- Mailgun events API confirmed delivery to `eparra@owenec.com` (Proofpoint 250 OK) and `eraphaelparra@gmail.com` (Gmail SMTP 250 OK) — downstream filtering is recipient-side, not a Mailgun or DNS config issue.
- No suppressions on either tested address.

## Next-session pointers

See `NEXT_SESSION_PROMPT.md`. Two named priorities:

1. **Email flow** — deliverability warm-up, Proofpoint allow-list, audit of 4 scheduled cron emails against V5.3 reality (several probably reference V2-era `winners_dashboard` table that's empty under `profitscout-fida8`), consider moving from time-based crons to Stripe-webhook + Firestore-state lifecycle.
2. **100-day GTM plan** — backbone is the 13-post 90-day blog schedule in `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` §7. Distribution lever is resuming X (stopped 4/6, signups went to 0 immediately). End-of-May inflection on public track record when V5.3 has ≥30 closed trades.
