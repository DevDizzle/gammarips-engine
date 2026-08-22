# 2026-08-22 — Go plan: outbound first, plugin, founding offer, Show HN without the video

## Status
DECIDED (owner, 2026-08-22: "Yes on everything. Go."). Amends
`2026-08-06-growth-sequence-video-hn-ads.md` and `docs/GTM-ORGANIC-GROWTH-PLAN.md`.

## Evidence at decision time (measured this session)
- Paid subs: 1 (the owner). External trials: 0, ever. MCP keys: 4, all internal.
- GA4, 28 days: 1,585 sessions, 1,544 direct at 15 s average (bot sweeps). About
  40 human sessions. 1 `begin_checkout`, 0 `purchase`.
- MCP `/mcp` POSTs, 7 days: about 2,700, all monitors and crawlers (SentinelOracle,
  mcpbeat, zevruna, MCPScoringEngine). The only `claude-code` user agent is our own
  GCP box. No external human has run the free one-liner.
- Repo stars: harness 0, mcp 0. chatgpt.com + copilot.com referrals: 9 sessions,
  more than Google organic (8).
- Firestore `users`: 220 accounts, 180 from Oct-Nov 2025, 16 with a paid or trial
  plan history. Never emailed about the pivot.
- The owner has no bandwidth to record videos.

Read: a distribution failure, not a conversion failure. Nobody has seen the product.

## Decisions
1. **The video gate on Show HN is dropped.** A real terminal recording of the free
   tier (asciinema, rendered to GIF, no key, no fabricated output) replaces it in the
   README and the HN post. The attribution gate stays: one incognito test checkout
   must show a real session source on the GA4 purchase.
2. **Outbound before inbound.** A GitHub-derived prospect list (harness users who
   care about options) and 10 personal DMs a day from the owner's accounts.
3. **Email the dormant list once.** Script `scripts/gtm/relaunch_email.py`, dry run by
   default, owner sends. Draft in `~/workspace/GAMMARIPS-RELAUNCH-EMAIL.txt`.
4. **Founding offer.** $29/mo for the first 100 subscribers, locked while subscribed,
   30-day trial, optional $299/yr. Webapp branch `offer/founding-100`. The 7-day trial
   covered 5 trading days, too short for a data product to prove itself.
5. **Claude Code plugin.** The harness repo installs as plugin `gammarips` from a
   same-repo marketplace. Install is the funnel. Submit to the community plugin
   directory after merge. Branch `feat/claude-code-plugin`.
6. **Backlinks reframed.** A link counts only when a human clicks it. Measure by
   referral sessions and by human MCP initializes (claude-code / cursor / codex user
   agents from non-cloud IPs), never by link count. First batch: awesome-mcp-servers,
   awesome-claude-skills, awesome-claude-code (issue form), syndication, Reddit after HN.
7. **Directories.** The owner chose one pass over the passive directories despite the
   07-07 null result. It is one pass, logged, then closed. The two in-product
   directories (Claude Code community plugins, claude.ai Connectors Directory) are the
   ones with a real audience. The Connectors Directory needs a Team or Enterprise
   claude.ai org and `title` + `readOnlyHint` on every MCP tool (today: 0 titles, 1
   hint). MCP repo task.
8. **Creators make the videos.** 3-5 MCP-savvy trading creators get free Pro and a
   promo code with revenue share. The owner records nothing.
9. **Cut.** Guides B3-B6 (SEO content for a category with about 2 impressions a
   day). B2 stays (the HN landing). B7 later.

## Measure
External trials. Weekly: referral sessions by source, human MCP initializes, trials,
paid. The 10-05 paying-subs checkpoint stands.

## Gotcha found on the way
The free-tier demo exposed a data inconsistency: the daily report narrative cited
VIX 14.89 "risk-on" while `get_regime_context` returned VIX 16.01 and SPY trend
BEARISH for the same date. The regime tool is the leakage-safe reading. The report
generator reads a different as-of. Open engineering item.

## References
`~/workspace/GAMMARIPS-GO-RUNSHEET.txt` (owner steps) · `docs/GTM-DISTRIBUTION-PLAYBOOK.md`
(Show HN mechanics) · memory `owner-goal-100-paid-subs-eoy2026`.
