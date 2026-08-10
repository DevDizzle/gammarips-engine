# 2026-08-06 — Growth sequence: video → Show HN → ads review (owner call)

## Status
DECIDED (owner, 2026-08-06 session). Supersedes nothing; operationalizes the
ads-deferral framework of 2026-08-05 (memory `owner-goal-100-paid-subs-eoy2026`)
with the checkout gate now cleared.

## Context
- **Checkout verified end-to-end 08-06.** Owner ran a real trial checkout
  (incognito, never-subscribed account): begin_checkout in GA4 realtime → Stripe
  webhook → welcome card/email → /account key generate → key hash matched
  `mcp_api_keys` doc → authed MCP calls succeeded → MP purchase event accepted.
  The frozen-proUntil fix (webapp PR #19) proven on real money: proUntil = trial
  end + 2-day grace, exact. Invoice events (`invoice.paid`,
  `invoice.payment_succeeded`) registered on Stripe endpoint `we_1RrrIt…` same
  day via API. Sub is `trialing`, converts ~08-13.
- **Directory channel: 30-day null result.** The 07-07 launch sprint (Cline,
  Docker MCP Catalog, mcp.so, Open Plugins/cursor.directory, server.json,
  registry click-pack, X thread — log in `docs/GTM-MCP-DIRECTORY-PLAN.md`) has
  been live ~1 month and produced zero external trials. Read: passive listings
  do not move this product; the audience must be shown the workflow.
- Goal: 100 paid subs by EOY 2026 (baseline 1 = owner). Kill-switch gates
  08-17 (trials) / 10-05 (paying) stand as set.
- GA4 purchase attribution gap found 08-06 (MP payload lacked `session_id`;
  purchases landed `(not set)`) — fix on webapp branch
  `fix/ga4-purchase-session-attribution`, merges via `/ship`.

## Decision (in order)
1. **Ship the attribution fix first** — purchase-by-source must work before any
   traffic push, or the push is unmeasurable.
2. **Produce the "How to Trade Options Using Claude" video** (outline, script
   skeleton, compliance rails: `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`).
   It is the first asset that explains the product to a human with intent, and
   the only untested lever class ($0 attention/education content). Embed on the
   webapp `landing/video-led` branch; X pin.
3. **Show HN timed WITH the video** — the one unfired $0 channel; held until it
   has a demo to point at.
4. **Ads decision ~2026-09-01**, on measured CVR from video + HN traffic. If
   that traffic converts at any nonzero rate: test $10-20/day on the exact
   high-intent cluster ("claude mcp options trading" type queries), compute
   real CAC. If a real traffic spike converts at zero: do NOT spend into the
   same message; that result feeds the 10-05 framework as set.
5. **"Let it sit" rejected.** It already sat a month with distribution live;
   that produced the null result this decision acts on.

## Measurement
GA4 (youtube/HN/organic source sessions → begin_checkout → purchase, now
attributable), Stripe trials/conversions, `mcp_api_keys` mints excluding
founder. CVR baseline definition per `owner-goal-100-paid-subs-eoy2026`.

## References
`docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md` · `docs/GTM-MCP-DIRECTORY-PLAN.md` ·
memory `owner-goal-100-paid-subs-eoy2026` · memory `mcp-monetization-killswitch` ·
webapp branch `fix/ga4-purchase-session-attribution` (`2267616c`)
