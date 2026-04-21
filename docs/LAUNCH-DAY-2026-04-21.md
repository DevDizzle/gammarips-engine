# Launch-day checklist — 2026-04-21

End-of-day goal: Evan pays $39 through Stripe, Firestore provisions the sub,
Mailgun sends the welcome email, WhatsApp group gets the daily push. Payment
flow testable end-to-end.

## Code shipped this session (what Claude did)

### Webapp (`/home/user/gammarips-webapp`)
- **Pricing page** — collapsed to single $39/mo Pro tier. Product JSON-LD
  now reports `price = "39.00"` (was `"0.00"` — active SERP damage pre-fix).
  `src/app/pricing/page.tsx` + `src/app/pricing/pricing-client.tsx`.
- **Hero** rewritten to One Promise ("One options trade a day. Scored before
  you wake up. Pushed to your phone at 9 AM.").
- **Root layout metadata** — `title.default`, `description`, `openGraph`,
  `twitter`, and `organizationSchema` all retired the "Overnight Edge" alias.
  Single most-impactful JSON-LD fix on the site (propagates to Google
  Knowledge Graph).
- **FAQ** — full 10-item replacement with FAQPage JSON-LD.
- **llms.txt + mcp.json + ai-plugin.json** — AI-discoverability cluster
  rewritten spec-compliantly; 15 tools named, pricing synced, disclaimers
  baked in. Mirrored across webapp + MCP repo.
- **/developers page** — 15-tool list, primary_tool flagged as
  `get_todays_pick`, pricing block updated.
- **/war-room + /history killed** — page dirs removed, 301 redirects added
  to `next.config.ts` (`/war-room → /pricing`, `/history → /reports`).
- **Stripe checkout + webhook** — single-tier `pro` plan, 7-day trial,
  `allow_promotion_codes: true` (for founder coupon). Webhook writes
  `whatsapp_allowlist/{uid}` Firestore doc on `checkout.session.completed`
  (the source-of-truth for OpenClaw paywall).
- **Mailgun welcome email** — rewritten to V5.3 / WhatsApp routine, uses
  `MAILGUN_DOMAIN` env var and `ceo@gammarips.com` default sender.
- **/reports/[date]** — OG suffix dropped, `Article.about` + `disclaimer`
  added, `Dataset.variableMeasured` expanded with V5.3 variables, footer
  disclaimer added.
- **Legal pages** — /privacy and /terms scrubbed of "Overnight Edge" and
  /terms §5 rewritten for free-MCP reality.
- **Email unification** — `support@gammarips.com` → `ceo@gammarips.com`
  across footer, contact form, mailgun sender, layout schema.
- **Home page title + signals/[ticker] + scorecard** — metadata swept.

### Engine (`/home/user/gammarips-engine`)
- **signal-notifier → OpenClaw POST** — non-blocking fire-and-forget HTTP
  POST to `${OPENCLAW_GATEWAY_URL}/hooks/agent` after every daily decision
  (pick + all 3 skip paths). Activates the moment the 3 secrets are mounted.
- **OpenClaw integration bundle** — 3 files in `tools/openclaw/`:
  - `whatsapp_allowlist_sync.py` — reads Firestore `whatsapp_allowlist`,
    emits `groupAllowFrom` config patch for OpenClaw
  - `agent-system-prompt.md` — compliance-guarded system prompt for the
    @mention chat agent (Claude Haiku 4.5 recommended)
  - `INTEGRATION.md` — step-by-step config changes for
    `~/.openclaw/config.json` + launch-day test checklist

## What Evan does (in any order)

### 1. WhatsApp group + OpenClaw (30 min)
- Create the private WhatsApp group.
- Add OpenClaw's linked WhatsApp number to the group. Make it an admin so it
  can post.
- Copy the `GROUP_JID` (looks like `1203...@g.us`).
- Edit `~/.openclaw/config.json`:
  - Enable `hooks`: `{"enabled": true, "token": "<random>", "path": "/hooks"}`
  - Set `channels.whatsapp.groupPolicy: "allowlist"`
  - Set `channels.whatsapp.groupAllowFrom: ["+1YOURNUMBER"]` (just you for
    launch test)
  - Add the group to `channels.whatsapp.groups` with `requireMention: true`
- Reload OpenClaw.
- Mount 3 secrets on the signal-notifier Cloud Run service:
  ```bash
  gcloud secrets create OPENCLAW_GATEWAY_URL --data-file=- <<< "http://<gateway>:18789"
  gcloud secrets create OPENCLAW_HOOKS_TOKEN --data-file=- <<< "<your-token>"
  gcloud secrets create OPENCLAW_GROUP_JID --data-file=- <<< "<group-jid>"
  ```
  Update `signal-notifier/deploy.sh` to mount them, then
  `cd signal-notifier && bash deploy.sh`.

### 2. Stripe (45 min)
- Create product "GammaRips Pro" — $39/mo recurring, no trial at the product
  level (trial is handled by the checkout session).
- Copy the Price ID (`price_...`).
- Create a 25%-off coupon "Founder $29" — discount brings $39 → $29/mo
  forever (use `percent_off: 25.64%` or set up a fixed-price alt for $29).
- Create webhook endpoint pointing at
  `https://gammarips.com/api/stripe/webhook` listening to:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- Copy the webhook signing secret (`whsec_...`).

### 3. Mailgun (15 min — likely already done)
- Confirm `mg.gammarips.com` verified.
- Confirm `MAILGUN_DOMAIN=mg.gammarips.com` and `MAILGUN_SENDING_KEY` / 
  `MAILGUN_API_KEY` are set in the webapp `.env`.

### 4. .env additions (webapp)
Add/confirm these in `/home/user/gammarips-webapp/.env`:

```env
# --- Stripe (new / may already exist) ---
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...              # from the webhook you just created
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_STRIPE_PRICE_ID=price_...        # the Pro $39/mo price
# optional: NEXT_PUBLIC_STRIPE_BILLING_PORTAL_CONFIG_ID=bpc_...  (for the
# manage-subscription link on /account)

# --- WhatsApp welcome email ---
WHATSAPP_GROUP_INVITE_URL=https://chat.whatsapp.com/...   # invite link

# --- Mailgun (confirm existing) ---
MAILGUN_DOMAIN=mg.gammarips.com
MAILGUN_API_KEY=...
MAILGUN_SENDING_KEY=...
```

## E2E smoke test (run after Evan's 4 steps above)

1. **Deploy webapp** (Firebase Hosting or whatever the pipeline is).
2. Sign out, visit `/pricing`, confirm page renders with single $39 tier,
   Product JSON-LD valid, `Start 7-Day Free Trial` button present.
3. Sign in with your personal email. Click `Start 7-Day Free Trial`.
4. Stripe checkout loads with the "Founder $29" coupon field (from
   `allow_promotion_codes: true`).
5. Enter card + apply coupon. Submit.
6. Redirect lands on `/account?session_id=...`.
7. **Stripe Dashboard**: confirm the subscription has `status: trialing`,
   trial ends in 7 days, $0.00 charged today.
8. **Firestore**:
   - `users/{your_uid}` has `isSubscribed: true, plan: "pro", subscribedAt: <now>`
   - `whatsapp_allowlist/{your_uid}` exists with `status: "provisioned"`
9. **Mailgun logs**: welcome email delivered to your address with WhatsApp
   invite link + 4-step routine.
10. **WhatsApp**: join the group via invite link, set your `senderId` in
    Firestore `whatsapp_allowlist/{your_uid}`, run
    `python tools/openclaw/whatsapp_allowlist_sync.py --project profitscout-fida8`,
    paste `groupAllowFrom` into OpenClaw config, reload.
11. @mention the agent in the group. Confirm reply with disclaimer footer.
12. **Monday 09:00 ET**: confirm daily pick (or skip message) appears in
    the group — end-to-end validation of the signal-notifier → OpenClaw
    POST path.

## Deferred (Tier 2, post-launch)

- `/how-it-works` body rewrite (metadata is fine; body still has "Overnight
  Edge" and 8:30 AM refs).
- `/about` body rewrite + founder-story paragraph (open question #3 in copy
  plan).
- `todays-pick-card.tsx` "YOUR 10:00 AM TRADE" eyebrow rewrite (card is
  functionally correct).
- `agent-arena` Phase 4 Option C (pre-entry verdict debate at 09:15 ET).
- Exit-reminder cron service (15:50 ET day-3 WhatsApp ping).
- Automate `whatsapp_allowlist_sync.py` as a 15-min Cloud Run cron (do this
  at ≥50 paid subs).
- Ledger `INVALID_LIQUIDITY` hygiene.

## Files changed

### Webapp (24 files)
- `src/app/pricing/page.tsx` — rewrite
- `src/app/pricing/pricing-client.tsx` — rewrite
- `src/components/landing/hero.tsx` — rewrite
- `src/app/layout.tsx` — metadata + organizationSchema
- `src/components/landing/faq.tsx` — rewrite + JSON-LD
- `public/llms.txt` — rewrite
- `public/mcp.json` — rewrite
- `public/.well-known/ai-plugin.json` — rewrite
- `src/app/developers/page.tsx` — rewrite (9 → 15 tools)
- `src/app/war-room/` — deleted
- `src/app/history/` — deleted
- `next.config.ts` — 2 new redirects
- `src/app/api/checkout/route.ts` — single-plan rewrite
- `src/app/api/stripe/webhook/route.ts` — pro plan + whatsapp_allowlist
- `src/lib/stripe.ts` — trial_period_days + allow_promotion_codes
- `src/lib/firebase-admin.ts` — plan type 'pro'
- `src/hooks/use-auth.tsx` — Pro gate
- `src/lib/firebase.ts` — default plan
- `src/lib/config.ts` — APP_NAME
- `src/lib/types/overnight-edge.ts` — PlanType includes 'pro'
- `src/lib/mailgun.ts` — welcome email rewrite + ceo@
- `src/components/layout/footer.tsx` — ceo@ + new tagline
- `src/app/about/contact-form.tsx` — ceo@
- `src/app/privacy/page.tsx` — alias scrub
- `src/app/terms/page.tsx` — §1 + §5 rewrite
- `src/app/reports/[date]/page.tsx` — OG + JSON-LD + footer disclaimer
- `src/app/reports/page.tsx` — metadata scrub
- `src/app/page.tsx` — home metadata + JSON-LD headlines
- `src/app/signals/[ticker]/page.tsx` — title alias scrub
- `src/app/scorecard/page.tsx` — metadata scrub

### Engine (4 files + 1 dir created)
- `signal-notifier/main.py` — OpenClaw post_to_openclaw() + 4 call sites
- `tools/openclaw/whatsapp_allowlist_sync.py` — new
- `tools/openclaw/agent-system-prompt.md` — new
- `tools/openclaw/INTEGRATION.md` — new

### MCP (1 file)
- `mcp.json` — unified rewrite
