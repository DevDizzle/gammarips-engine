# GammaRips — Google Ads launch brief

**Created 2026-07-09. Owner decisions (this session): fork = MCP-direct primary; budget = $20/day (~$600/mo); geo = US only.**
Source of truth for what's in the account. If you edit in the Google Ads UI, reconcile back to these files.

## Campaign settings (set these exactly)
| Setting | Value | Why |
|---|---|---|
| Objective | **Website traffic** (NOT Sales/conversions) | Cold account + tiny volume can't feed Smart Bidding's ~15-30-conversion learning phase. Buy clean clicks, measure the rate yourself. |
| Campaign type | **Search only** | — |
| Networks | **Uncheck Search Partners AND Display** | Non-negotiable. They leak budget to junk placements. |
| Bidding | **Maximize Clicks + a hard max-CPC cap** | Never open-ended. Start the cap at **~$3.50** and re-estimate from Keyword Planner before launch. |
| Budget | **$20/day** | — |
| Geo | **United States only** | Avoids EU finance-ad verification enforcement (rolling out Jul 23, 2026). |
| Personalized/sensitive-category ads | **OFF** | Finance category hygiene. |
| Advertiser verification | **Complete same-day if Google prompts** | Identity/business verification; ads pause if you stall. |

## Ad groups (see `keywords.txt`)
- **AG1 — MCP/agentic category (Exact) -> /developers.** The category you're staking. Near-zero volume today; treat its impression count as the read on whether the category exists yet.
- **AG2 — options-data/flow API for builders (Phrase) -> /developers.** Where the budget actually finds clicks. The technical data-buyer is the closest real match to the MCP buyer. Still MCP-direct (dev landing), not the retail web UI.
- **AG3 — brand (Exact+Phrase) -> /.** Cheap defense.

Landing pages verified live (200) on 2026-07-09: `/developers`, `/pricing`, `/how-it-works`, `/methodology`, `/lab`, `/scorecard`, `/`.

## Compliance posture (READ before launch)
- **Certification is very likely NOT required.** You're a data/software vendor, not a broker or adviser. Verified 2026-07-09 against Google's "Complex speculative financial products" and "Financial products and services" policies — both target *providers* of the instruments / money-managers, not analytics vendors.
- **The signals trap is the real line.** Google prohibits ad destinations that provide "trading signals, tips, or speculative trading information." Copy + landing must read as **pure data/tooling, never a signals service** — which is your owner-locked "data not advice, no pick endpoint" rule. `/developers` (not a "get today's pick" page) is the safe destination.
- **Expect a possible first-pass disapproval + appeal.** Options ads get auto-flagged even when compliant. If disapproved, appeal and state plainly: data/software vendor, no brokering, no advice, no signals. Budget a day for it.
- **No returns/win/profit/guarantee/"signal" language, ever.** All copy in `rsa-ad-copy.txt` obeys this.

> ✅ **`gammarips-review` SIGN-OFF — 2026-07-09: SHIP.** First pass returned FIX (track-record sitelink optics, premature self-certification, "Claude" vs claude.ai-web overreach, missing named negatives); all four fixed; clean re-review confirmed no new issues and all char limits/factual claims accurate. Assets are compliance-cleared. Re-run `gammarips-review` if any copy, keyword, or landing page changes.

## Measurement (for reading the test, NOT for bidding)
- Import a **trial-start / signup** conversion from GA4 (`G-ZF0DQVQEKJ`) + Stripe.
- Watch `mcp_analytics` `subscription_required` touches (paywall hits) and `/developers` sessions.
- Negatives cadence: strong list day one; **scrub the Search Terms report on day 3-4 and day 10** (at $20/day you spend real money before the first scrub).

## The honest CAC math (what this probe can and can't prove)
At a ~$3.50 CPC, $20/day ≈ **5-6 clicks/day ≈ ~170 clicks/mo**. At a generous 2% click->paid rate that's ~3 trials -> maybe **1 paying sub/mo at a CAC near $600** for a $39/mo ($468/yr) product. **That does not pencil as ROI month one, and it isn't supposed to.** The probe's real job: find out whether the "agentic/MCP trading data" category has *any* searchers yet. Read AG1's impression volume as that answer.

## Kill metric (tie to the GTM gate)
- **Day 14:** if AG1 (exact category) has **< ~20 impressions**, the category has no search volume yet — that's the finding. Shift the budget to AG2 adjacency, or reopen the free-surface fork (fork A) you passed on.
- **Full-month probe (~$600):** if **zero trial starts**, do not keep spending on MCP-direct search. Options on the table: pivot to fork A (ads -> free web UI, cheaper/higher-volume, convert downstream), lean back on the free MCP directories, or pause paid entirely until the Oct 5 GTM gate.
- Feeds the master gate in `docs/GTM-MCP-DIRECTORY-PLAN.md`: **Oct 5, 2026 — reevaluate ad spend with real CAC math only if >=1 paying sub exists.**

## Open items before you hit "Publish"
1. **Pull Keyword Planner CPCs** for the AG1/AG2 terms. If top-of-page bids make $39/mo CAC impossible, that itself is the finding — say so before spending.
2. Set the max-CPC cap from those numbers (start ~$3.50).
3. Confirm the GA4/Stripe trial-start conversion import is live.
4. Complete Google advertiser verification if prompted.
