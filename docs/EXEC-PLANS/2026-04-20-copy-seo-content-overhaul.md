# EXEC-PLAN: GammaRips Copy + SEO + Content Overhaul

**Date:** 2026-04-20
**Status:** Reference plan. Do not execute until V5.3 surface + monetization build wraps (Phase 1.0/1 done; Phase 3a done; Phase 2 + pricing launch remain).
**Owner:** Evan. Claude drafts; Evan reviews and publishes. No code changes in this doc.
**Companion docs:**
- Strategy: [`docs/TRADING-STRATEGY.md`](../TRADING-STRATEGY.md)
- Monetization plan: [`docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md`](./2026-04-20-v5-3-surface-and-monetization.md)
- Decision record: [`docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md`](../DECISIONS/2026-04-20-v5-3-surface-and-monetization.md)
- Operator one-pager: [`CHEAT-SHEET.md`](../../CHEAT-SHEET.md)
- Glossary: [`docs/GLOSSARY.md`](../GLOSSARY.md)

**Skills consulted:**
- Ogilvy Copywriting (boraoztunc/skills) — positioning + big-idea + headline framework, "go the whole hog," brand-name-in-headline rule.
- Stop Slop (boraoztunc/skills) — filler elimination, active voice, rhythm scoring.
- Copywriting (boraoztunc/skills) — specificity over vagueness, CTA patterns.
- SEO Audit (boraoztunc/skills) — E-E-A-T signals, meta hierarchy, Rich Results Test invariant.
- Schema Markup (boraoztunc/skills) — JSON-LD invariants, `@graph` pattern, accuracy-over-cleverness rule.
- Content Strategy (boraoztunc/skills) — searchable vs shareable, hub-and-spoke, 4-dimension prioritization.
- Evan's 7 Rules (primary) + Brian Moran's 7 Rules (format inspiration, via MoneyScout prompt).

---

## 1. The One Clear Promise (Rule 7)

> **"One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM."**

Everything ladders to this. The promise: **open your phone at 9:00 AM, read one message, place one trade, go back to your day job.** The engine does the watching. Specific (one, one, 9 AM), benefit-framed, and deliverable — V5.3 produces at most one pick per day by construction.

**Candidates rejected:**
- "See what institutions are buying before the market opens." — describes mechanism, not outcome.
- "The AI that tells you what to trade tomorrow." — too close to tip-service framing; regulatorily risky.
- "Know what smart money did last night." — current hero. Past-tense and observational.

**Pro-tier sub-promise:** *"Ask the AI anything about today's trade — inside the private WhatsApp group."* The moat. Converts "I see the pick on the webapp, why pay?" into "I want to ask why."

---

## 2. Voice Rules (GammaRips-specific)

### DO
- Write for a working professional with a full-time job and a $2K–$20K options account. "When your 10:00 AM meeting runs over and you already placed the trade at 9:58."
- Use specific dollar amounts and specific times. `$500/trade`, `10:00 AM ET`, `-60%/+80%`, `3 trading days`. Concrete beats abstract (Ogilvy: *"Facts sell."*).
- Use the operator's own language. "Set your stop. Set your target. Go back to work."
- Show the routine, not the dashboard. GammaRips is not a terminal; it's a morning habit.
- Disclaim every public performance claim: "Paper-trading performance, educational only. Not investment advice." This is non-negotiable for the *SEC v. Lowe* publisher exclusion.
- Ship benefit-framed headlines before feature lists. "Wake up knowing" > "5,230 tickers scanned."
- Use the brand name in headlines when the surface is SEO-indexable (Ogilvy headline rule).
- Prefer short, declarative sentences. One idea per sentence.

### DON'T
- Don't say "signal service." Say "one pick a day" or "overnight options scanner." "Signal service" is regulatorily loaded and associated with Discord scams.
- Don't say "AI-powered," "game-changer," "unlock," "leverage," "empower," "ecosystem," "institutional-grade," or "proprietary edge." Every one of these is slop (Stop Slop Rule).
- Don't make win-rate claims above N=30 closed V5.3 trades. We currently don't have enough sample to market with specific numbers — use *structural* confidence ("stop pre-defined, target pre-defined, exit pre-scheduled") until the scorecard fills in.
- Don't imply personalized advice. Never use "you should," "we recommend for your account," "is this right for you?" — all outside the publisher exclusion.
- Don't blur the free webapp. Paid is convenience (push + chat), free is information. The paywall copy stays honest about this.
- Don't sell timing. Free users and WhatsApp subs see the pick at the same second. Copy about "get the trade first" is false and legally unsafe.
- Don't use "GammaMolt" as a user-facing marketing character outside the About page. It confuses buyers — the product is a trade routine, not an AI personality. (Keep the About/brand lore optional.)
- Don't promise earnings. "Make $X a month" is regulator bait.

### TONE
- Calm, competent, slightly boring. Think "commercial pilot explaining turbulence," not "day-trader on TikTok."
- Direct, not cute. "One trade a day" beats "your morning edge awaits."
- Honest about paper-trading posture. We gain credibility by admitting the limitation, not hiding it.
- Routine-focused, not adrenaline-focused. The pitch is: this frees up your day, not that it maxes your portfolio.
- Warm when the user is nervous (pricing page, risk disclaimers). Cold when the user wants data (scorecard, methodology).

---

## 3. Target-audience pain catalog

Buyer's pains in their language, not ours.

**Segment A — "Part-time retail with a full-time job" (core persona, ~70% of projected Pro buyers):**
- "I don't have time to watch charts all day."
- "I took a losing options trade a few weeks ago and still don't know what I did wrong."
- "By the time I pull up a UOA alert from Twitter, the move is already done."
- "My last Discord group posted 40 tickers a day. I couldn't tell which to take."
- "I can place one trade in the morning. I can't sit on my phone 9:30–4:00."

**Segment B — "Burned by a signal service" (retention risk):**
- "I paid $199/mo for alerts and most were garbage."
- "The guy screenshots only his winners."
- "There's no stop, no target, no exit plan. Just 'buy this.'"

**Segment C — "Options-curious, options-skeptical" (top of funnel, free-tier readers):**
- "I know options can blow up. I don't want to YOLO."
- "I want to learn how institutions position, not day-trade SPY."
- "If I lose $2,000 my wife will kill me."

**Segment D — "Data geeks who will never pay" (referrals + social content):**
- "Show me the backtest. What's the sample size?"
- "How is this not just a repackaged Unusual Whales scraper?"

**Cross-cutting pains to name directly:** herding fear (getting the last fill), alert fatigue, exit confusion, cognitive load (rule > dashboard), social-proof gap ("how do I know you're not another Discord guy?"). These map onto V5.3's mechanical strengths: one pick, structural exits, deterministic tiebreakers, auditable paper ledger. Point at the mechanics, don't shout about them.

---

## 4. Page-by-page audit + rewrites

Ordered by conversion criticality. All page paths relative to `/home/user/gammarips-webapp/src/app/` unless noted.

### Page: Homepage (`src/app/page.tsx`)

#### Hero (`src/components/landing/hero.tsx`)

**CURRENT:**
```
H1: Wake Up Knowing What Smart Money Did Last Night
Subhead: Every morning by 8:30 AM, you get the trades institutions placed overnight —
         scored, analyzed, with specific contracts to consider. While 99% of traders
         check the news, you already know where the money moved.
Micro:   5,230+ tickers scanned · Signals scored 1-10 · Delivered before market open
```

**PROBLEMS:**
- ❌ Rule 7: two promises competing ("know what smart money did" + "specific contracts"). Ogilvy: *"One promise."*
- ❌ Rule 5: no buyer says "I want to know what smart money did last night." They say "Tell me what to trade."
- ❌ Rule 3: observational scene, not routine. No 10:00 AM entry moment.
- ⚠️ Rule 4: "5,230+ tickers" is a feature flex. Buyer cares about output, not denominator.
- ⚠️ Stop Slop: "While 99% of traders check the news" is an invented stat. Cut.
- ❌ V5.3: "8:30 AM" wrong — canonical is 09:00 ET publication, 10:00 ET entry.
- ❌ V5.3: "Specific contracts to consider" is weaker than what V5.3 delivers (one contract, one direction, −60%/+80% bracket).

**REWRITE:**
```jsx
<h1>
  One options trade. Scored before you wake up.
  <span className="gradient block mt-2">Pushed to your phone at 9 AM.</span>
</h1>

<p className="subhead">
  GammaRips watches institutional options flow overnight and mechanically
  picks one contract each morning — stop, target, and exit all pre-set.
  You place the trade at 10:00 ET and go back to your day.
</p>

<p className="micro">
  V5.3 engine · 5,230 tickers scanned nightly · One pick or none ·
  Paper-trading, educational only
</p>

<div className="cta-row">
  <Button primary href="/signals">See Today's Pick</Button>
  <Button ghost href="/how-it-works">How the Engine Picks</Button>
</div>
```

**WHY:**
- H1 lands the promise in three beats the buyer cares about — *quantity, preparation, delivery time* (Rule 7).
- Subhead paints the routine: stop set, target set, back to your day (Moran Rule 3).
- "One pick or none" is the honest differentiator vs every other signal service.
- Micro retains 5,230 tickers as proof of breadth, but contextualized.
- Disclaimer baked in — *Lowe* publisher-exclusion floor.
- Two CTAs: conversion ("See Today's Pick") + education fallback. Buyer self-selects.

---

#### Today's V5.3 Pick card (`src/components/landing/todays-pick-card.tsx`)

**CURRENT copy (has-pick path):**
```
Eyebrow:  TODAY'S V5.3 PICK
H2 (ticker + direction + contract + 4-stat grid)
Caption:  Why this pick cleared V5.3 gates
Chips:    V/OI 4.50 > 2.0 ✓
          7.8% OTM (5–15%) ✓
          VIX 18.92 ≤ VIX3M 20.51 ✓
          Engine score 4
Footer:   Entry 10:00 ET day-1 · Stop −60% · Target +80% · Hold 3 trading days ·
          Paper-trading performance, educational only. Not investment advice.
```

**PROBLEMS:**
- ✅ This component is the strongest copy on the site. Most of it stays.
- ⚠️ Rule 3 (feel): The 4-stat grid (Strike / DTE / Mid / Call $ Vol) is accurate but feels like a terminal. A retail buyer reads this and thinks "do I buy 1 contract or 2?" The card doesn't answer that.
- ⚠️ Rule 1 (audience pain): No mention of the "go back to your day" payoff. The card is all data, no routine.
- ⚠️ "V/OI 4.50 > 2.0 ✓" is jargon. Needs a tooltip or a plain-English mirror.
- ✅ Footer disclaimer is perfect. Keep verbatim.

**REWRITE (targeted patches, not a full rewrite — this card is mostly good):**

Add a "Your morning with this pick" line above the gate chips:

```
Eyebrow: YOUR 10:00 AM TRADE
  (replace "TODAY'S V5.3 PICK" — clearer benefit framing)

H2: FIX · BULLISH
    FIX $580C 2026-05-22

4-stat grid: unchanged

[NEW line below grid]
At 10:00 ET: buy one contract, set a GTC stop 60% below fill, set a GTC
limit target 80% above. Close by 3:50 ET day-3 if neither fires.

Caption: Why the engine picked it (replaces "Why this pick cleared V5.3 gates")
Chips:   Fresh flow (vol/OI 4.5)
         Near the money (7.8% OTM)
         Calm regime (VIX 18.92 ≤ VIX3M 20.51)
         Scanner score 4/10

Footer:  unchanged
```

**WHY:**
- "YOUR 10:00 AM TRADE" is buyer-language; "V5.3 PICK" is internal.
- Routine line tells the buyer what to *do* — data without action otherwise.
- Plain-English gate chips decode jargon ("Fresh flow" > "V/OI 4.5") without losing the number.
- Score stays visible and non-premium-coded — FAQ explains score-is-not-pick.

---

#### How It Works four-card grid (`src/app/page.tsx` lines 117-128)

**CURRENT:**
```
1. See Everything — Institutional moves across 5,230+ tickers — not just the
   popular 50 everyone watches
2. Know What Matters — Each signal scored 1-10 so you focus on high-conviction
   setups, not noise
3. Get the Trade — Specific contracts, strikes, and the AI thesis explaining
   why institutions are positioned
4. Act First — In your hands before 9:30 AM — while everyone else is still
   reading headlines
```

**PROBLEMS:**
- ❌ Rule 1: describes engine activities, not buyer actions.
- ❌ Rule 5: "Act First" is adrenaline-speak. V5.3 buyer doesn't want to be first; they want to not miss the fill.
- ⚠️ V5.3: "Act First — before 9:30 AM" collides with the 10:00 ET entry; buyer expects to trade at open.
- ❌ Rule 7: four cards, four different promises.

**REWRITE:**
```
1. 09:00 ET — Open your phone
   "One message. One ticker. One contract. Pre-set stop at −60%,
    target at +80%, exit at 3:50 ET day-3."

2. 10:00 ET — Place the trade
   "Buy one contract at market. Arm both exit orders on Robinhood.
    Total time: under two minutes."

3. 10:01 ET – 3:50 ET day-3 — Go live your life
   "Both orders are working. Your broker fills or cancels. You don't
    watch charts. You don't check quotes."

4. When the trade closes — We log it publicly
   "Every V5.3 pick and outcome goes into the paper-trading ledger.
    No hindsight edits. Scorecard is the receipt."
```

**WHY:**
- Timestamped titles = routine the buyer can picture.
- "One message. One ticker. One contract." = big idea in nine words.
- Step 3 is the conversion line: this is what the buyer actually buys — their time back.
- Step 4 names the scorecard without cherry-picking claims.
- Verbs are buyer actions; the engine is never the subject — inverse of current "we do X" framing.

---

#### "Stop Trading Blind" section (`src/app/page.tsx` lines 257-273)

**CURRENT:**
```
H2: Stop Trading Blind
P:  Most retail traders find out about institutional moves after the stock
    already popped. You'll see the positions at 8:30 AM — hours before the
    move. Every signal timestamped, every call tracked publicly. No
    cherry-picking, no hindsight.
CTA: Explore Signals / See How It Works
```

**PROBLEMS:**
- ❌ "8:30 AM" implies timing advantage — timing is NOT the value (both tiers see pick at 09:00 ET). Selling timing is legally risky.
- ❌ V5.3: "8:30 AM" wrong — 09:00 ET.
- ⚠️ "Stop Trading Blind" is a decent hook; body doesn't deliver. "Blind to what?" isn't answered.
- ✅ "Every signal timestamped, every call tracked publicly" is the right line. Keep.

**REWRITE:**
```
H2: Stop Collecting Alerts. Start Taking a Trade.

P:  Most UOA services fire a dozen alerts a day and leave you to pick. You
    pick wrong and blame yourself. GammaRips does the opposite. One pick a
    day or none. Entry, stop, target, and exit all pre-defined. Every signal
    timestamped to the second. Every outcome logged to the public scorecard.
    No cherry-picking. No hindsight.

CTA: See Today's Pick (primary) / Read the Methodology (ghost)
```

**WHY:**
- Reframes the competitor (UOA firehose) as the problem, not the buyer's literacy (MoneyScout Rule 1: don't blame the buyer).
- "One pick a day or none" = the structural differentiator nobody else offers.
- Structural mechanics (entry/stop/target/exit pre-defined) is a proof point we can use pre-scorecard.
- Removes timing-advantage language — buyer doesn't want first-look, they want not-missing-the-fill.
- Primary CTA goes to the pick, not the signals list.

---

#### FAQ (`src/components/landing/faq.tsx`)

**CURRENT:** 8 items, all stale — reference retired $49/$149 pricing, "8:30 AM EST" times, the War Room construct, and the score-6 enrichment gate.

**PROBLEMS:**
- ❌ Every pricing reference obsolete.
- ❌ Every time reference obsolete (8:30 → 09:00 ET publish, 10:00 ET entry).
- ❌ "Score 6+ gets enrichment" stale (V5.3 enriches at >= 1; gates do the work).
- ❌ Questions are our-phrased, not buyer-phrased.
- ⚠️ Missing the two Pro-buyer questions: "What do I get that free users don't?" and "Why $39 when other groups charge $99?"
- ⚠️ Missing the conversion-gating objection: "What if the trade hits −60% right after I buy?"

**REWRITE (full FAQ replacement — 10 items):**

1. **Q: What exactly lands on my phone every morning?**
   A: By 09:00 ET you get one pick or none. A ticker, a direction (call or put), a specific contract with strike and expiration, a recommended mid price, a −60% stop, and a +80% target. Some days the engine stays out — when VIX closes above VIX3M (backwardation) or nothing clears the filter stack, nothing is sent. On those days, do nothing. That's the routine.

2. **Q: How does the engine pick which one?**
   A: Four mechanical filters, in order. (1) Overnight score >= 1 — any level of unusual activity qualifies. (2) Bid-ask spread <= 10%. (3) Directional dollar volume > $500K. (4) Volume/open-interest ratio > 2.0 at the focal strike, moneyness 5–15% OTM, and VIX <= VIX3M. Whatever clears all four, the pick is whichever has the highest directional dollar volume. Five deterministic tiebreakers after that — no judgment, no override.

3. **Q: What's free, what's paid, what do you actually charge for?**
   A: Free: the full webapp. Today's pick, full signals list, daily report, per-ticker deep dive, methodology, FAQ, and public scorecard. Starter ($19/mo): WhatsApp push of the entry and the exit, so you don't have to check the webapp at 09:00 ET. Pro ($39/mo): everything in Starter plus access to an AI agent inside the private WhatsApp group — tag it with a question and it answers using live engine data (open position, win rate, today's pick evidence). Pro Annual: $399/yr. First 500 Pro subscribers lock $29/mo for life.

4. **Q: Why is the webapp free if you charge for WhatsApp?**
   A: We charge for convenience, not information. Paying subscribers get the push to their phone so they don't have to check the webapp at 09:00 ET. They also get the chat agent. Free users see the same pick on the same page at the same second. No information is behind a paywall. We think that's the honest model.

5. **Q: What if the trade hits −60% right after I buy it?**
   A: Then the stop fills and you lose up to $300 on a $500 position. That is the engineered maximum per-trade loss, and it's the whole point. The trade either hits −60%, +80%, or closes at 3:50 ET on day-3 — nothing else. No "should I hold one more day" decisions. A −60% fill is a win for the routine; you closed cleanly and moved on.

6. **Q: Are you telling me what to trade?**
   A: No. GammaRips is educational content about what one mechanical engine picked, based on public overnight options-flow data. You decide whether to take the trade in your account, at what size, and whether to deviate. We never see your account, never manage your money, and never personalize the pick. If you want personalized investment advice, work with a licensed advisor.

7. **Q: Where's the track record?**
   A: On the [Scorecard](/scorecard) page, updated as the engine's paper trades close. We started V5.3 paper-trading on April 17, 2026, so sample size is small — we will publish specific win-rate numbers when at least 30 V5.3 trades have closed. In the meantime, every signal is timestamped, every outcome is logged, and nothing is edited after the fact. That's the receipt.

8. **Q: Why one trade a day? Everyone else sends dozens.**
   A: Because you can't take dozens and keep a job. And because most "more signals" services are firehoses with no exit rules, and the user ends up cherry-picking the ones that worked in hindsight. We'd rather be wrong one time a day than right-in-retrospect twelve times a day.

9. **Q: Who runs this?**
   A: Evan Parra (founder, ML engineer, data architect) built the engine. An autonomous AI operator named GammaMolt runs the daily pipeline — scanning, scoring, enriching, publishing, posting. Every decision is logged to BigQuery. Nothing is human-curated in the pick path. You can read about the stack on the [About](/about) page.

10. **Q: What happens if I cancel?**
    A: You lose WhatsApp access at the end of your billing cycle. The webapp stays free forever. No retention tricks, no downgraded experience. Your pick appears on the home page the same as it did before you subscribed.

**WHY (FAQ summary):**
- All pricing + time references now match V5.3 and v2.4 monetization.
- Questions are buyer-phrased, not ours.
- Q5 names the conversion-gating objection openly — Ogilvy: "Treat the reader as intelligent."
- Q3/Q4 split "what do you charge for" from "why webapp free" — different questions in the buyer's head.
- Q7 is the disciplined win-rate answer — receipt promise without a number we don't yet own.
- Q10 defangs the "trap me in a subscription" fear.

---

### Page: Pricing (`src/app/pricing/pricing-client.tsx` + `page.tsx`)

**CURRENT:** Single "All Access 100% Free" card with an 11-item feature list that references WhatsApp, War Room, GammaMolt Q&A, etc. Metadata says "GammaRips is Free."

**PROBLEMS:**
- ❌ Completely obsolete. Free / Starter $19 / Pro $39 / Pro Annual $399 per v2.3 plan. Most conversion-critical page on the site, furthest out of date.
- ❌ JSON-LD `Product.offers.price = "0.00"` becomes an SEO lie the day paid tiers launch.
- ❌ "GammaRips is Free" in an indexed title tag will haunt post-launch rankings.
- ❌ No founder-pricing language, no 7-day trial copy, no grandfathering, no annual value framing. All approved.
- ❌ No social proof, no scarcity, no pricing-specific FAQ.
- ❌ CTAs go to `/signals` and `/auth/action`, not Stripe checkout.

**REWRITE:**

Three-tier pricing card layout. Card 1 = Free (no "get started" friction), Card 2 = Starter $19 (ladder rung), Card 3 = Pro $39 with "MOST POPULAR" badge and founder-pricing callout.

```
Eyebrow:  PRICING

H1:       One trade a day. Three ways to get it.

Subhead:  The webapp is always free. Pay for the push to your phone
          and, on Pro, the AI agent inside the private WhatsApp group.

[3-column card grid]

CARD 1: Free
  $0 forever
  "See the pick at 09:00 ET. Browse every signal. Read the full report.
   Everything on gammarips.com, no login, no card."
  ✓ Today's V5.3 pick at 09:00 ET
  ✓ Full signals list across 5,230+ tickers
  ✓ Daily market report with AI-authored thesis
  ✓ Per-ticker deep dive + recommended contract
  ✓ Public scorecard (paper-trading ledger)
  ✓ Methodology, FAQ, and all disclaimers
  CTA: [See Today's Pick]

CARD 2: Starter
  $19/mo · cancel anytime
  "Everything in Free, plus a WhatsApp push when the pick is
   decided and when the exit fires — so you don't have to
   open your phone at the top of the hour."
  ✓ Everything in Free
  ✓ WhatsApp entry push at ~09:00 ET
  ✓ WhatsApp exit reminder at 15:50 ET on day-3
  ✓ Private WhatsApp group
  × No AI chat agent
  CTA: [Start Starter]

CARD 3: Pro  [MOST POPULAR badge]
  $39/mo · 7-day free trial · cancel anytime
  "Everything in Starter, plus an AI agent inside the private
   WhatsApp group. @mention it to ask about today's pick, your
   open position, the 30-day track record, or the enriched data
   on any ticker. The whole group sees the exchange — one ask
   benefits everyone."
  ✓ Everything in Starter
  ✓ AI agent in the private WhatsApp group (@mention to ask)
  ✓ Live open-position tracker via chat
  ✓ 30-day win-rate queries on demand
  ✓ Historical ledger queries ("show me all bearish picks")
  CTA: [Start 7-Day Free Trial]

  Founder pricing: first 500 Pro subscribers lock $29/mo for life.
  Pro Annual: $399/yr (effective $33/mo).
```

Below the card grid:

```
Section: "What you're actually paying for"
Three short paragraphs, each leading with a reassurance:

"Not a timing advantage." Free users and Pro subscribers see the
exact same pick at the same second. No paid-first tier. Ever.

"Not a signal firehose." One pick per day or none. If the engine
skips, the push says so and you do nothing.

"Not personalized advice." GammaRips is educational content about
a mechanical engine's output. Every push and page carries the
paper-trading disclaimer. You trade your own account.

Section: "Founder pricing — first 500 Pro subscribers"
A short paragraph: "We're pricing Pro at $39/mo at public launch.
The first 500 subscribers lock in $29/mo for life — no price
changes, no grandfather exceptions. When 500 is hit, the founder
rate closes. If you're reading this and the rate is still showing,
it's open."

Section: "Frequently asked"
[Mini-FAQ: 5 questions tailored to pricing — "can I switch tiers,"
 "what's the refund policy," "how does the 7-day trial work,"
 "what if I cancel mid-month," "do annual subscribers get the
 AI chat agent?" Each answer is 2-3 sentences.]

Footer disclaimer:
"Paper-trading performance, educational content only. Not
investment advice. You trade your own account; GammaRips does
not manage your money. Past performance is not a guarantee of
future results."
```

**WHY:**
- Three cards force a comparison (Starter = decoy/ladder; the $20 gap makes Pro feel like the obvious choice).
- "Free forever" + 7-day trial on Pro removes the two biggest friction points.
- "MOST POPULAR" badge on Pro anchors the default.
- Founder pricing captures Evan's $29 anchor as scarcity without compromising future ARPU.
- "What you're actually paying for" section states what we're *not* selling — counters the "paid = timing" misread.
- When 500 founder seats fill, that section flips to "Founder pricing closed on [date]" — instant post-launch social proof.
- Tier-specific CTA verbs: "See Today's Pick" (discovery), "Start Starter," "Start 7-Day Free Trial."
- Disclaimer footer is non-negotiable.

Required metadata rewrite:

```
title:       Pricing — GammaRips
description: Free webapp forever. $19/mo for WhatsApp entry/exit pushes.
             $39/mo for the Pro tier with an AI chat agent inside the
             private WhatsApp group. 7-day free trial on Pro.
```

No more "GammaRips is Free" anywhere indexed. Replace immediately when this rewrite ships — Google cache lag makes this URL's title a liability for months.

---

### Page: How It Works (`src/app/how-it-works/page.tsx`)

**CURRENT:** Long-form explainer. Strong in parts (the "Your Morning With The Overnight Edge" hypothetical, the scoring breakdown) but contains several outdated pillars.

**PROBLEMS:**
- ❌ "Three tickers are highlighted" — V5.3 surfaces ONE pick. "6:15 AM" is before publication (09:00 ET).
- ❌ "Score 6+ flagged for enrichment" stale (V5.3: >= 1).
- ⚠️ Morning hypothetical reads like pitch deck. Replace with real FIX-vs-OKLO 2026-04-17 case.
- ⚠️ Missing gate-stack section (V/OI > 2, moneyness 5-15%, VIX <= VIX3M) — single most under-documented + over-differentiating part of methodology.
- ⚠️ FSLY "Reading a Signal" uses fabricated 9/10 + $12.4M. Replace with real FIX.
- ✅ Bottom disclaimer block excellent. Keep.

**REWRITE (section-by-section patches):**

Replace "Your Morning With The Overnight Edge" with:

```
Your 9 AM With GammaRips

It's 09:00 ET. Your WhatsApp ping fires.

"Today's trade at 10:00 ET — FIX $580C 2026-05-22, BULLISH.
 Stop −60%, target +80%, exit 3:50 ET on day-3. Paper-trading,
 educational only."

You glance at the webapp — same pick, same second. You pull up
your broker at 09:58, buy one contract at market at 10:00 ET,
arm the two GTC exit orders, and put your phone down.

Between 10:01 ET day-1 and 15:50 ET day-3, one of three things
happens: the target fills, the stop fills, or you close at 3:50 ET
day-3. Either way, the trade closes itself. You don't watch.

That's the whole product.
```

Replace the scoring section rewrite:

```
How the engine picks exactly one trade

Score first — a conviction rank 1-10 built from positioning size,
strike breadth, volume/OI, and directional flow imbalance.

But score alone doesn't pick. On 2026-04-17, the highest-scored
ticker was OKLO at 8/10 — and the engine skipped it, because
its volume/open-interest ratio was 1.5 (we require > 2.0). Stale
flow. Roll activity, not new positioning.

The engine shipped FIX at 4/10 instead, because FIX cleared
every gate: V/OI 4.5, moneyness 7.8% OTM, VIX 18.92 ≤ VIX3M 20.51.
A 4/10 that clears the gates beats an 8/10 that doesn't. Score
tells you what's interesting. Gates tell you what's tradeable today.
```

Add a new section after "Our Scoring System":

```
The V5.3 Gate Stack

Every signal that makes it to your phone has cleared five
mechanical filters, in order:

1. Overnight score >= 1 (any level of unusual activity)
2. Bid-ask spread <= 10% (so you can actually fill)
3. Directional dollar volume > $500K (directional, not hedging)
4. Volume/open-interest ratio > 2.0 (fresh positioning, not rolls)
5. Moneyness 5–15% OTM (not ATM gamma plays, not deep lottery)
6. VIX <= VIX3M (skip backwardation days entirely)

Then one final sort: whichever surviving ticker has the highest
directional dollar volume wins. Five deterministic tiebreakers
after that — score, V/OI, spread, ticker alphabetical. No judgment,
no override, no cherry-picking.

If nothing clears all six, nothing is sent. Some days that happens.
That's a feature — you only trade when the engine sees a clean
setup.
```

Replace the FSLY "Reading a Signal" example with a real FIX example using the actual 2026-04-17 numbers pinned in the v2.4 plan Section 1.

**WHY:**
- "Your 9 AM With GammaRips" replaces the three-ticker fantasy with the real V5.3 routine.
- The OKLO-over-FIX anecdote teaches "score is not pick" in 40 words — the most educational thing on the site.
- Gate-stack section fills the biggest methodology gap — the answer to "how is this different from Unusual Whales?"
- Replacing FSLY-fabricated data with real FIX data raises E-E-A-T signals.

---

### Page: About (`src/app/about/page.tsx`)

**CURRENT:** Founder story (Evan + GammaMolt), how-it-works recap, six differentiators, pricing summary, trust/YMYL disclosure, contact form.

**PROBLEMS:**
- ❌ Times stale (4:00/4:25/4:30 AM schedule doesn't match V5.3).
- ❌ "100% Free" copy contradicts paid tiers.
- ❌ Pricing card ("100% Free All Access") dead on arrival.
- ⚠️ GammaMolt "I don't talk about trading. I trade. Results over rhetoric." quote is cringe-adjacent for core persona. Mute.
- ✅ Evan's "Let the AI cook" — ownable and short, keep.
- ✅ Trust/YMYL disclaimer solid, keep.

**REWRITE (targeted patches):**

Replace the 4-step engine description times:

```
04:00 ET — SCAN (unchanged)
05:30 ET — ENRICH (was "4:30 AM ENRICH") — gate stack applies
08:15 ET — REPORT (new step — editorial synthesis)
09:00 ET — PUBLISH (was "Before Market Open DELIVER") — one pick
           or skip reason to all surfaces simultaneously
```

Replace "Pricing Summary" with a redirect to the new pricing page:

```
Ready to see how the engine thinks?

Free webapp forever. One pick at 09:00 ET, one pick or none.
Or skip the webapp and get the push to your phone with Starter
or Pro.

[See Pricing]  [Read the Methodology]
```

Keep the founder section. Keep GammaMolt as Chief Intelligence Officer but trim the "results over rhetoric" quote — replace with:

```
"Every pick is logged. Every exit is logged. The scorecard
 is the receipt." — GammaMolt
```

**WHY:**
- Current time grid (4:00/4:25/4:30) confuses — buyer wonders what happens at 6/7/8 AM. Actual V5.3 schedule teaches: 04:00 scan → 05:30 enrich → 08:15 report → 09:00 publish.
- "Scorecard is the receipt" reinforces the trust thread.
- Pricing card replacement future-proofs the page against tier changes.

---

### Page: Scorecard (`src/app/scorecard/page.tsx`)

**CURRENT:** Placeholder page with four stat cards showing "—" and a "Win Tracking Begins February 2026" message. No actual data rendered.

**PROBLEMS:**
- ⚠️ Highest-trust page on the site, shows no data. Even pre-N=30 we can render something (trade count, open position, last-closed outcome).
- ⚠️ "Win Tracking Begins February 2026" is past-tense as of April 2026.
- ⚠️ Missing full paper-trading disclaimer. This is where a regulator lands first.
- ⚠️ Missing V5.3 labeling ("paper, full-coverage" vs "arena-filtered") per v2.4 Section 4 transparency rule.

**REWRITE (structure):**

```
H1: Scorecard

Subhead: Every V5.3 pick is logged to BigQuery before the market
         opens. Every outcome is logged when the trade closes.
         Nothing is edited after the fact. When the ledger has 30+
         closed V5.3 trades, this page shows win rate. Until then,
         it shows the mechanism.

[Top strip: large numeric display]
Paper trades since V5.3 cutover (2026-04-17): N
  Closed: X
  Open: Y
  Skipped (no pick days): Z

[Current open position card]
(If exit_timestamp IS NULL: render ticker, entry time, entry price,
 current mark, unrealized P&L, days-to-timeout, disclaimer)
(If no open: "No open position. Next pick decision at 09:00 ET.")

[Closed-trade timeline]
(Latest 10 closed V5.3 trades, most recent first. Each row:
 scan_date, ticker, direction, entry, exit, realized %, outcome
 (target-hit / stop-hit / timeout))

[Pre-N=30 note]
Labeled: "Sample size: N closed trades. We publish aggregate win
rate when N >= 30 V5.3 closed trades. Until then, this page shows
individual outcomes without aggregation."

[Post-N=30 hero stat — rendered only when N >= 30]
X% win rate, Y avg winner %, Z avg loser %, W avg hold days
labeled "Paper trading, V5.3 full-coverage, N trades"

[Full disclaimer block, same wording as pricing page]
```

**WHY:**
- Individual rows are legally safer pre-N=30 than aggregates (small-N aggregates mislead).
- "Mechanism first, numbers second" = we sell discipline, not past performance.
- Every number labeled with filter used ("V5.3 full-coverage") pre-empts Phase 4 arena-vs-paper divergence transparency.
- Skipped-days count = proof of discipline. Most services hide their skip rate.
- "Next pick decision at 09:00 ET" empty state turns a dead page into a live clock.

---

### Page: Signals list (`src/app/signals/page.tsx`) and per-ticker detail (`src/app/signals/[ticker]/signal-client.tsx`)

**CURRENT:** List page renders bullish and bearish signals as plain tables. Detail page renders score, move, flow, engine flags, thesis, contract, etc.

**PROBLEMS:**
- ✅ V5.3-aligned since 2026-04-17 cleanup. Engine Flags correctly labeled diagnostic.
- ⚠️ List metadata is our-language ("Full list of institutional options flow signals").
- ⚠️ "AI Trade Thesis" title invites personalized-advice misread. Consider "Why the engine flagged this."
- ⚠️ Detail page lacks V5.3-gate-status badge — users can't tell if ticker is today's pick vs browsable-only.

**REWRITE (targeted patches):**

List page header:
```
H1 (current):   Overnight Signals
H1 (rewrite):   Every Ticker the Engine Flagged Last Night

Subhead (current):  Institutional options flow reported on {date}
Subhead (rewrite):  {date}. {N} tickers showed unusual flow. {M} cleared
                    the V5.3 gates. One was picked. The rest are here
                    for your own research.
```

Detail page patches:
- Add a prominent chip at the top: "Today's V5.3 pick" / "Cleared V5.3 gates, not ranked #1" / "Flagged by scanner, did not clear V5.3 gates." This single chip sets buyer expectations and explains *why* this specific ticker is on the page.
- Rename "AI Trade Thesis" card title to "Why the engine flagged this."
- Rename "Recommended Setup" card title to "Contract the engine would pick here." This is language discipline — we don't recommend; we surface what the engine would pick.

**WHY:**
- V5.3-status chip is the single biggest UX addition — resolves "is this today's pick or just browsable?" in two words.
- New signals-list headline is buyer-phrased and better SEO (long-tail specificity).
- "Why the engine flagged this" is phrasing-neutral; "AI Trade Thesis" invites personalized-advice misread.
- "Contract the engine would pick here" — the subjunctive matters legally; "Recommended setup" implies personal recommendation.

---

### Page: Arena (`src/app/arena/page.tsx`)

**CURRENT:** Renders multi-model debate. Metadata says "7 AI Models (Claude, GPT, Grok, Gemini, DeepSeek, Llama, Mistral)."

**PROBLEMS:**
- ❌ Arena under v2.4 is 3 agents voting TAKE/CAUTION/SKIP at 09:15 ET on today's deterministic pick. Current metadata obsolete.
- ❌ "7 AI Models" becomes false when Phase 4 ships (3 agents).
- ⚠️ Arena-as-spectacle has no buyer outcome; Option C gives it one ("Is today's pick worth taking?").
- ⚠️ Slop-flavored description ("argue over the best trade," "watch the fight").

**REWRITE (for Phase 4 Option C — staged for when arena reshape ships):**

```
Metadata title:        Arena — Three AI Agents Vote on Today's Trade | GammaRips
Metadata description:  Every trading day at 09:15 ET, three independent AI agents
                       (Claude, Grok, Gemini) vote TAKE, CAUTION, or SKIP on
                       GammaRips' deterministic V5.3 pick. See how they reasoned
                       and why.

H1:    Today's Verdict Debate
H2:    {verdict label — e.g., "TAKE 3/3" or "CAUTION 2/1" or "SKIP 2/1"}

Subhead: At 09:15 ET, three AI agents voted on today's V5.3 pick. Their
         reasoning lives below. The paper-trading ledger takes every V5.3
         pick regardless of vote — so future performance can be split by
         "all V5.3 picks" vs "only TAKE-votes." Transparency over
         optimization.
```

Soft-gating: per Phase 3b, paid subscribers see the full transcript immediately. Free users see the headline verdict and the first sentence of each agent's reasoning, with an "Unlock full debate" overlay after 2 read-throughs (localStorage counter).

**WHY:**
- Current metadata is legal scope creep — "7 AI Models Debate Today's Best Trade" implies independent picking; Option C only votes on the deterministic pick.
- Headline verdict with vote count = news in the headline (Ogilvy rule).
- "Transparency over optimization" wins the argument with Segment D data geeks.
- Soft-gate respects the freemium contract — information stays free, full transcript is a feature.

---

### Page: Reports index (`src/app/reports/page.tsx`)

**CURRENT:** H1 "The Morning Briefing" — solid. Subhead decent. Not broken.

**PROBLEMS:**
- ⚠️ Minor: subhead "Every trading day, we publish what institutional money did overnight. Pick a date. See what happened." is clean. One weakness: it's descriptive, not benefit-framed.
- ⚠️ Missing: a "Today's Report" hero card above the date grid. Landing on `/reports` should show today's narrative above the archive — right now the archive grid is the whole page.

**REWRITE:**
```
H1 (unchanged):   The Morning Briefing

Subhead (rewrite):  Every trading morning at 08:15 ET, GammaRips publishes
                    a narrative report on the overnight flow. Themes, bull
                    and bear counts, the engine's pick. Browse the archive
                    or read today's below.

[NEW: Today's report hero card above the archive grid]

[Existing archive grid — unchanged]
```

**WHY:** Naming 08:15 ET sets reader expectation and is search-discoverable. Hero-above-archive is a standard content pattern — current design buries today's report in a 50-card grid.

---

### Page: 404 (`src/app/not-found.tsx`)

**CURRENT:**
```
Not Found
Could not find requested resource
Return Home
```

**PROBLEMS:**
- ⚠️ Standard boilerplate. Missed opportunity to route the user to the most valuable next action.
- ⚠️ No brand voice.

**REWRITE:**
```
H1: This page got stopped at −60%.

P:  The URL didn't exist, or the ticker wasn't on our scan, or the
    report isn't published yet.

CTA primary:  See Today's Pick
CTA ghost:    Back to Reports Archive
```

**WHY:** On-brand joke (−60% is our stop, memorable not tryhard). Two CTAs capture 90% of 404 intent (today's pick or a historical report). Negligible effort, measurable bounce-recovery.

---

### Metadata / layout `src/app/layout.tsx` + `src/app/page.tsx`

**CURRENT:**
```
Default title:  GammaRips | The Overnight Edge — Know What Smart Money Did Last Night
Description:    Every morning before the market opens, see what institutional
                money did overnight. 5,230+ tickers scanned. Signals scored
                1-10. Specific contracts recommended.
Keywords:       overnight options flow, institutional options activity,
                unusual options activity, options flow scanner, options
                signals, smart money, options trading, AI trading analysis
```

**PROBLEMS:**
- ❌ Rule 7 + V5.3 alignment: Title still carries "The Overnight Edge" — the product name for the V3-era $49 plan. Under V5.3 we have Starter/Pro and a different promise.
- ⚠️ "5,230+ tickers scanned" in the indexed description is a flex; "one pick a day" is the actual promise. Put the promise in the description.
- ⚠️ Meta keywords tag is ignored by Google since 2009 (SEO Audit skill notes this is vestigial). Not harmful; just noise.

**REWRITE:**
```
Default title:  GammaRips — One Options Trade a Day. Scored Before You Wake Up.
Description:    GammaRips is an overnight options-flow engine that picks one
                contract per trading day and publishes it at 09:00 ET. Entry,
                stop, target, and exit all pre-defined. Free webapp, $19/mo for
                WhatsApp push, $39/mo for the AI chat agent. Paper-trading,
                educational only.
openGraph:      title + description matched to above
twitter:        title + description matched to above
```

**WHY:**
- Title leads with the promise, 62 chars (under Google's 60-char display cap, minor tail truncation acceptable).
- Description carries the offer in 230 chars; mobile-truncated version stops at "published at 09:00 ET" — still a complete thought.
- Disclaimer appears in the indexed description — the one place a regulator would land first.
- Retires "The Overnight Edge" as a marketed alias. Product is "GammaRips." Tagline is "One Options Trade a Day."

---

## 5. SEO JSON-LD audit + rewrites

Five JSON-LD schemas live in the app:

| File | Schema | Status |
|---|---|---|
| `src/app/layout.tsx` | Organization | Mostly good, minor fixes |
| `src/app/page.tsx` | WebSite | Good |
| `src/app/page.tsx` | Article (dynamic daily) | Good, minor V5.3 patch |
| `src/app/page.tsx` | FAQPage | Needs full rewrite when FAQ is rewritten |
| `src/app/pricing/page.tsx` | Product.offers.price = 0 | **Critical rewrite needed** |
| `src/app/signals/[ticker]/page.tsx` | Article + FinancialProduct | Good |
| `src/app/signals/page.tsx` | CollectionPage | Good |
| `src/app/arena/page.tsx` | DiscussionForumPosting | Needs Phase 4 rewrite |
| `src/app/reports/page.tsx` | CollectionPage | Good |
| `src/app/about/page.tsx` | AboutPage + FAQPage | Minor V5.3 patch |
| `src/app/how-it-works/page.tsx` | Article | Good |
| `src/app/scorecard/page.tsx` | — (none) | **Add Dataset or LocalBusiness-lite** |

### 5.1. Critical: pricing Product schema

**CURRENT (pricing page):**
```json
{
  "@type": "Product",
  "name": "The Overnight Edge",
  "offers": {
    "@type": "Offer",
    "price": "0.00",
    "name": "All Access Free Membership"
  }
}
```

**PROBLEMS:**
- ❌ SEO Audit skill rule: schema must accurately represent the page. Once paid tiers ship, `price: 0.00` becomes a lie and Google Rich Results Test will flag it as structured-data error, which degrades ranking.
- ❌ Only one tier; no SubscriptionOffer granularity.
- ❌ "The Overnight Edge" name is retired.

**REWRITE:** Use `@graph` to declare a `SoftwareApplication` parent with three `Offer` children, one per tier:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "@id": "https://gammarips.com/#software",
      "name": "GammaRips",
      "applicationCategory": "FinanceApplication",
      "operatingSystem": "Web, WhatsApp",
      "description": "Overnight options-flow engine. One mechanical pick per trading day with pre-defined entry, stop, target, and exit.",
      "offers": [
        {
          "@type": "Offer",
          "@id": "https://gammarips.com/#free-offer",
          "name": "GammaRips Free",
          "description": "Full webapp access forever. Daily V5.3 pick, signals list, reports, scorecard, methodology.",
          "price": "0",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock",
          "url": "https://gammarips.com/signals"
        },
        {
          "@type": "Offer",
          "@id": "https://gammarips.com/#starter-offer",
          "name": "GammaRips Starter",
          "description": "Everything in Free plus WhatsApp entry and exit push notifications.",
          "price": "19.00",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock",
          "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": "19.00",
            "priceCurrency": "USD",
            "billingDuration": "P1M",
            "unitText": "monthly"
          },
          "url": "https://gammarips.com/pricing"
        },
        {
          "@type": "Offer",
          "@id": "https://gammarips.com/#pro-offer",
          "name": "GammaRips Pro",
          "description": "Everything in Starter plus an AI agent inside the private WhatsApp group. Ask it about today's pick, your open position, or the historical ledger.",
          "price": "39.00",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock",
          "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": "39.00",
            "priceCurrency": "USD",
            "billingDuration": "P1M",
            "unitText": "monthly"
          },
          "eligibleTransactionVolume": {
            "@type": "PriceSpecification",
            "description": "7-day free trial"
          },
          "url": "https://gammarips.com/pricing"
        }
      ],
      "publisher": {
        "@id": "https://gammarips.com/#organization"
      }
    }
  ]
}
```

**WHY:** `SoftwareApplication` is the right type for subscription SaaS (Schema Markup skill, Google guidelines). Three `Offer` children with `billingDuration: "P1M"` enable tier-level rich results. `@graph` pattern links back to Organization `@id`, strengthening the entity graph. Pro's `eligibleTransactionVolume.description` is the closest native pattern for the free trial (no `hasFreeTrial` predicate exists). Founder pricing is deliberately omitted — promotional, not list — and would create cache-lag trouble when 500 seats fill.

### 5.2. Organization schema (layout.tsx)

**CURRENT:**
```json
{
  "@type": "Organization",
  "name": "GammaRips",
  "alternateName": "The Overnight Edge",
  "founder": { "@type": "Person", "name": "Evan Parra", "jobTitle": "Founder & CEO" },
  "sameAs": ["https://twitter.com/GammaRips"]
}
```

**PROBLEMS:**
- ⚠️ `alternateName: "The Overnight Edge"` ties the corporate identity to a deprecated product name. Drop.
- ⚠️ Missing `@id` — with 7+ schemas across pages referring to this org, every one needs to link back to a canonical `@id`.
- ⚠️ Missing `contactPoint`, `address` (if applicable), `sameAs` beyond X/Twitter.

**REWRITE:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://gammarips.com/#organization",
  "name": "GammaRips",
  "url": "https://gammarips.com",
  "logo": { "@type": "ImageObject", "url": "https://gammarips.com/icon.png" },
  "email": "support@gammarips.com",
  "description": "Overnight options-flow engine that publishes one mechanical trade pick per day.",
  "founder": { "@type": "Person", "name": "Evan Parra", "jobTitle": "Founder & CEO", "url": "https://evanparra.ai" },
  "contactPoint": { "@type": "ContactPoint", "contactType": "Customer Support", "email": "support@gammarips.com" },
  "sameAs": [
    "https://twitter.com/GammaRips",
    "https://www.linkedin.com/company/gammarips"
  ]
}
```

**WHY:** `@id` stabilizes the graph — every other schema can now reference `"publisher": {"@id": "https://gammarips.com/#organization"}`. Dropping `alternateName` prevents Google from co-indexing the retired alias. `contactPoint` is a minor E-E-A-T boost. LinkedIn placeholder — remove if company page not created.

### 5.3. Daily Article schema (page.tsx dynamic)

Minor patches when V5.3 is live:
- `headline` should prefer the `todays_pick` narrative over `report.title` when has_pick is true — "GammaRips Pick: FIX BULLISH 2026-04-17" is a better SEO headline than the editorial title.
- `datePublished` should be the pick's `decided_at` (09:00 ET), not `08:30Z`.
- Add `mentions` array with the picked ticker as a `Thing` — helps Google associate GammaRips with the ticker symbol.

```json
{
  "@type": "Article",
  "headline": todaysPick.has_pick
    ? `GammaRips Pick ${todaysPick.scan_date}: ${todaysPick.ticker} ${todaysPick.direction}`
    : `GammaRips ${todaysPick.scan_date}: No pick today (${todaysPick.skip_reason})`,
  "datePublished": todaysPick.decided_at,
  "mentions": todaysPick.has_pick ? [
    { "@type": "Thing", "name": todaysPick.ticker }
  ] : [],
  "publisher": { "@id": "https://gammarips.com/#organization" }
}
```

### 5.4. Scorecard schema (currently missing)

Add a `Dataset` schema to the scorecard page once the ledger renders:

```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "GammaRips V5.3 Paper-Trading Ledger",
  "description": "Every V5.3 pick and outcome since 2026-04-17. Paper-trading, educational.",
  "creator": { "@id": "https://gammarips.com/#organization" },
  "temporalCoverage": "2026-04-17/..",
  "variableMeasured": [
    "scan_date", "ticker", "direction", "entry_price",
    "exit_price", "realized_return_pct", "hold_days", "outcome"
  ],
  "license": "https://gammarips.com/terms",
  "disclaimer": "Paper-trading performance, educational content only. Not investment advice."
}
```

`Dataset` improves discoverability on Google Dataset Search and positions GammaRips as a data-publisher (defensible E-E-A-T against "signal service" SEO).

### 5.5. Arena schema rewrite (when Phase 4 Option C ships)

Replace `DiscussionForumPosting` with `Review` (since each day's arena is a structured TAKE/CAUTION/SKIP assessment of a single pick):

```json
{
  "@context": "https://schema.org",
  "@type": "Review",
  "itemReviewed": {
    "@type": "FinancialProduct",
    "name": todaysPick.recommended_contract
  },
  "author": { "@type": "Organization", "name": "GammaRips Arena Panel" },
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": arenaVerdict === "TAKE" ? "5" : arenaVerdict === "CAUTION" ? "3" : "1",
    "bestRating": "5",
    "worstRating": "1"
  },
  "reviewBody": arenaTopReasoning,
  "datePublished": arenaDecidedAt
}
```

**WHY:** `Review` is a first-class Google rich-result type with star rendering in SERP. `DiscussionForumPosting` is a weaker signal that implies user-generated content (regulatorily awkward for a financial product).

### 5.6. FAQPage schema rewrite

Direct reflection of the FAQ rewrite in Section 4. Since `faqs` is imported from `src/components/landing/faq.tsx`, updating the FAQ data auto-updates the schema. One-step fix.

### 5.7. SEO risks to flag

- **Indexed stale "GammaRips is Free" on /pricing.** Google will hold that snippet in SERP for weeks after body copy changes. Mitigation: update `<title>` and `<meta description>` *first*, then body copy. On ship day, post the update on X/LinkedIn and request re-indexing via Search Console URL Inspection.
- **"The Overnight Edge" alias.** Organization schema and multiple titles still carry it. Deindex in one coordinated PR.
- **Score-6 claim in how-it-works.** Ranks for methodology queries. Replace with the new gate-stack content — longer + more specific + internally linked = faster re-index.
- **Missing BreadcrumbList** on signals/reports/blog pages. Minor, but helps deep-page SERP.
- **No `Article.author` on editorial content.** Daily reports declare publisher but not author. Google E-E-A-T wants author even for AI-authored content (`Organization` value is acceptable). Add.

---

## 6. 90-day blog post schedule

**Objective:** drive organic acquisition + position the $39 Pro tier as the natural conversion. Weekly cadence; 13 posts over 12 weeks with one bonus mid-cycle.

**Three content pillars** (Content Strategy skill — hub-and-spoke):
1. **Methodology** (searchable — evergreen explainers that rank for "unusual options activity," "volume-to-OI ratio," "VIX3M backwardation").
2. **Weekly engine commentary** (current-market — what the engine picked this week, what it skipped, why).
3. **Track record** (social proof — unlocks at Month 3 when N≥30 V5.3 trades closed).

**Distribution (cross-channel use):** each post doubles as an X long-thread (7-10 tweets), a Reddit r/options or r/thetagang post (educational framing, never promotional), and a LinkedIn article (professional framing). Evan reviews + posts manually per the `docs/EXEC-PLANS/...` Phase 5 constraint (no Reddit automation, shadowban risk).

### The schedule

| Wk | Title (candidate) | Persona | Keywords | Primary CTA | Type | Cross-channel |
|---|---|---|---|---|---|---|
| 1 | Why "Unusual Options Activity" Is Mostly Noise (And the One Signal That Isn't) | Segment A, D | unusual options activity, UOA, volume open interest ratio | Webapp visit | Evergreen explainer | X thread, r/options, LinkedIn |
| 2 | Why Score Alone Doesn't Pick: The FIX-vs-OKLO 2026-04-17 Case Study | Segment A, D | options flow scanner, stale open interest | Webapp visit | Case study | X thread, r/options, LinkedIn |
| 3 | VIX Backwardation Is the Easiest Day-Trading Gate You're Not Using | Segment A | VIX VIX3M, volatility term structure, options risk regime | Webapp visit | Evergreen explainer | X thread, r/options |
| 4 | The Case for One Trade a Day: A Discipline Argument | Segment A, B | options swing trading, one trade a day, overtrading | Pro trial | Thought leadership | X thread, LinkedIn, r/thetagang |
| 5 | How We Detect Institutional Hedging vs Directional Positioning | Segment D | institutional options hedging, dark pool flow, call put ratio | Webapp visit | Methodology | X thread, r/options, LinkedIn |
| 6 | Moneyness 5-15% OTM: Why We Skip Both ATM Gamma and Deep Lottery | Segment A, D | OTM options moneyness, gamma exposure, theta decay | Webapp visit | Evergreen explainer | X thread, r/thetagang |
| 7 | What Gets Pushed to My Phone at 9:00 AM (Weekly Engine Recap) | Segment A | options morning alerts, 9 AM options trade | Pro trial | Recap post (ongoing series) | X thread, LinkedIn |
| 8 | A $19/mo Signal Service That Actually Skips Bad Days (And Why That Matters) | Segment A, B | options signal service review, WhatsApp trading alerts | Starter trial | Positioning | X thread, r/options |
| 9 | What Happens Inside the Private WhatsApp Group — @mention an AI Agent | Segment A | AI trading assistant, chatgpt options, claude trading | Pro trial | Paid differentiator | X thread, LinkedIn |
| 10 | The First 30 V5.3 Trades: What the Ledger Shows (Paper) | Segment A, B, D | options trading track record, paper trading performance | Pro trial | Performance post (N=30 unlock) | X thread, r/options, LinkedIn |
| 11 | What the Engine Got Wrong in the First 30 Days (Post-Mortem) | Segment B, D | options trading losses, trade review | Pro trial | Case study | X thread, r/options, LinkedIn |
| 12 | One Trade a Day Is a Systems Problem, Not a Pick Problem | Segment A, B | retail options trading systems, trading routine | Pro trial | Thought leadership | X thread, LinkedIn |
| 13 (bonus) | The GammaRips Morning: Mechanical Options Trading in 90 Seconds | Segment A | options trading routine, part time options trading | Pro trial | Video/demo script | X thread (video), LinkedIn, Reddit |

### Cluster logic

- **Month 1 (Wk 1-4)** — methodology education. Converts to webapp visits; builds topical authority in SEO. No pricing pushes; this is the trust-building floor.
- **Month 2 (Wk 5-8)** — paid-tier differentiators. Introduces the WhatsApp push and the @mention agent as the moats. Starter CTA appears at Wk 8; Pro trial CTA appears at Wk 7 and Wk 9. Still avoids win-rate claims.
- **Month 3 (Wk 10-13)** — social proof unlocks. N=30 V5.3 closed trades is the trigger — if the ledger hasn't cleared 30 closes by Wk 10, slip Wk 10 to Wk 12 and substitute another methodology post.

### Guardrails per post

- Every post carries the standard disclaimer block at the bottom: "Paper-trading performance, educational content only. Not investment advice. Past performance is not a guarantee of future results."
- Every performance number is labeled with the filter used ("paper, V5.3 full-coverage" or "arena-filtered TAKE votes only"). Non-negotiable per v2.4 plan.
- No post in Month 1-2 uses a win-rate number. If an illustration requires a number, use the structural maximum ("max per-trade loss is $300 on a $500 position" is structural, not performance-based).
- Every post links to at least one other GammaRips post and one methodology page. Internal-link density is the cheapest SEO lever.
- Every post ends with a tier-matched CTA. Month 1 = Webapp visit. Month 2 = Pro trial. Month 3 = Pro trial (with the track record as the hook).

### Content calendar tooling

No CMS needed for 13 posts. A single markdown folder in `/home/user/gammarips-webapp/src/content/blog/` + MDX routing already supported by Next.js. Scheduled publishing via commit + merge.

---

## 7. Implementation priority ladder

### Tier 1 — Do first (conversion-critical, pre-paid-launch)

1. **Pricing page rewrite** — `src/app/pricing/pricing-client.tsx` + `page.tsx`. Three-tier structure, new Product schema with three Offers, new metadata. This is the single most important rewrite in this document; shipping paid tiers with the current "100% Free" pricing page is a conversion disaster.
2. **FAQ rewrite** — `src/components/landing/faq.tsx`. All 8 current items are stale. New 10-item FAQ lands.
3. **Hero rewrite** — `src/components/landing/hero.tsx`. New H1 "One options trade. Scored before you wake up. Pushed to your phone at 9 AM." and subhead.
4. **Metadata rewrite** — `src/app/layout.tsx` + all per-route metadata exports. New title template, new description, drop "The Overnight Edge" alias from Organization schema.
5. **How It Works four-card rewrite** on home page — timestamped morning routine, `src/app/page.tsx` lines 24-29.
6. **About page time grid fix** — `src/app/about/page.tsx`, replace 4:00/4:25/4:30 schedule with V5.3 04:00/05:30/08:15/09:00 schedule.
7. **Signals detail V5.3-status chip** — `src/app/signals/[ticker]/signal-client.tsx`, add the "Today's V5.3 pick" / "Cleared gates" / "Flagged only" chip at the top.

### Tier 2 — Trust building (ships with or shortly after paid launch)

8. **Scorecard structure** — `src/app/scorecard/page.tsx`, replace placeholder with ledger-backed open-position card + last-10-closed timeline + pre-N=30 note.
9. **How It Works methodology expansion** — add the V5.3 gate-stack section, replace FSLY example with FIX case study, replace fabricated-morning with V5.3 morning routine.
10. **404 page rewrite** — `src/app/not-found.tsx`, on-brand joke + two CTAs.
11. **Signals list headline** — `src/app/signals/page.tsx`, buyer-phrased headline and subhead.
12. **Reports index "Today's report" hero card** — `src/app/reports/page.tsx`, surface today's report above the archive grid.
13. **Arena page rewrite** (depends on Phase 4 Option C shipping) — new metadata, verdict-first rendering, Review schema.

### Tier 3 — Content engine (post-launch, recurring)

14. **Blog scaffold** — `src/app/blog/[slug]/page.tsx` + MDX setup in `src/content/blog/`. One-time infra.
15. **Week 1 post draft** — "Why 'Unusual Options Activity' Is Mostly Noise."
16. **Subsequent weekly posts** — per the 90-day schedule.
17. **Organization schema enrichment** — add LinkedIn once company page created, add BreadcrumbList schema to deep pages.

---

## 8. Open questions for Evan

1. **Founder pricing seat count** — v2.4 plan says 500. You mentioned this is negotiable. Sticking with 500 for the pricing page copy, but confirm before we index it. Lowering to 250 tightens scarcity; raising to 1,000 dilutes it.
2. **"GammaMolt" character scope** — keep on About page as the AI operator, but should it appear in marketing copy outside the About page? Recommendation: no. The Pro buyer is not paying for a bot personality; they're paying for a morning routine. GammaMolt as brand lore on About + product bio works. GammaMolt as frontpage character does not.
3. **Founder-story depth on About** — the current About page has Evan in two paragraphs (ML engineer + evanparra.ai). A longer founder story ("built this to solve my own problem with losing options trades") would raise E-E-A-T and Rule 6 (social proof) signals. Do you want to draft 200-300 words of founder backstory for the About page? Recommend yes.
4. **Weekly engine recap — which week is week 1?** — Proposing the blog schedule starts the week after Pro tier launches publicly. Confirm or propose a different start week.
5. **Reddit sub targets** — r/options, r/thetagang, r/wallstreetbets. WSB is a coin flip (high traffic, low conversion, shadowban risk). Recommend skipping WSB for Month 1-2, trying one post in Month 3 after the scorecard is public. Confirm.
6. **Hero CTA text** — current proposal is "See Today's Pick" (free-funnel) + "How the Engine Picks" (education). Alternative: A/B test "Start 7-Day Free Trial" as a second primary CTA in Month 2+ once Pro is live. Decision needed before Month 2 Tier 1 work is finalized.

---

*End of plan. This document is the source of truth for copy rewrites and SEO updates. Revisit at the end of Month 3 once N≥30 V5.3 closed trades are in the ledger and social proof content can cite specifics.*

---

## §9 Addendum — surfaces missed in the first pass (2026-04-20)

**Status:** extends §4 to full webapp coverage. §1–§3 rules apply unchanged. Every surface below re-read in full.

**Cross-cutting finding (§9.2–§9.5):** `llms.txt`, `ai-plugin.json`, `mcp.json`, and the root `<meta>` block are a single positioning system. They get cross-referenced by agents within hours of each other; today all four disagree on name, pricing, tool count, tagline — agents surface the lowest-common-denominator summary. Unifying them is the single highest-leverage MCP-positioning move without shipping code.

### §9.1 Developers page (`src/app/developers/page.tsx`)

**CURRENT:** H1 *"Build with Overnight Edge Data"*; metadata title *"GammaRips MCP API — Options Flow Intelligence for AI Agents"*; 9 tools listed (missing 6); pricing block *"MCP API — 100% FREE — All 9 tools unlocked"*; tool description for `get_enriched_signals` claims *"AI-enriched signals (score ≥ 6)"* (stale gate); one Python client example only.

**PROBLEMS:**
- ❌ **Tool count wrong:** lists 9, server exposes 15. Missing: `get_todays_pick`, `list_todays_picks`, `get_freemium_preview`, `get_open_position`, `get_position_history`, `get_enriched_signal_schema`. `get_todays_pick` is literally the One Promise as an API call.
- ❌ **"Overnight Edge" alias** in H1 — retired per §2.
- ❌ **"Score ≥ 6" is a stale gate.** Current enrichment is `score >= 1 AND spread <= 10% AND UOA > $500K`. Developers writing to this spec filter incorrectly.
- ❌ **"100% FREE" framing** conflates free MCP endpoint with free product. Paid tiers ship soon; copy contradicts §1 Pro sub-promise.
- ⚠️ **No One Promise mention.** Current copy is generic-data-API pitch; misses the pro-tier moat ("GammaRips can be the first thing a user-facing AI agent asks about today's trade").
- ⚠️ **Only one client example (Python `fastmcp`).** Claude Desktop + ChatGPT Custom Connector are the dominant MCP audiences today.
- ⚠️ **Footer links to stale `ai-plugin.json` and `mcp.json`** (§9.3, §9.4).
- ✅ Authless endpoint is a genuine moat — keep that framing.

**REWRITE (key pieces — full copy in implementation PR):**
- **`<title>`:** *"Ask your AI agent about today's options trade — GammaRips MCP"*
- **H1:** *"Ask your AI agent what GammaRips picked today."*
- **Subhead:** *"One options trade a day, scored overnight, exposed as 15 MCP tools. Connect Claude, ChatGPT, or your own agent — no API key, no sign-up."*
- **Connect block:** unchanged endpoint + *"Pro-tier customers get the same data pushed to WhatsApp at 9:00 ET and can @mention an agent inside the group."*
- **Tools section — all 15, grouped by use case:** *Today's Trade* (`get_todays_pick`, `list_todays_picks`, `get_freemium_preview`), *Signal Data* (`get_overnight_signals`, `get_enriched_signals`, `get_signal_detail`, `get_enriched_signal_schema`), *Track Record* (`get_signal_performance`, `get_win_rate_summary`, `get_open_position`, `get_position_history`), *Daily Report* (`get_daily_report`, `get_report_list`, `get_available_dates`), *Search* (`web_search`).
- **Pricing section:** *"MCP endpoint — free forever. Paid tiers are convenience: Starter $19, Pro $39, Founder $29 lifetime (first 500)."* Frame free vs paid as *delivery*, not *access*.
- **Quick Start:** three client examples — Claude Desktop config snippet, ChatGPT Custom Connector URL, Python `fastmcp` calling `get_todays_pick`.
- **Bottom CTA:** *"Try it in 60 seconds. Paste the endpoint into Claude Desktop, ask 'what did GammaRips pick today?', watch the pick come back with gate reasoning."* CTAs: Copy Endpoint / See Pro Pricing.
- **JSON-LD WebAPI schema:** replace `description` with 15-tool version; drop "Overnight Edge."

**WHY:** H1 + subhead land the One Promise and name the Pro-tier distribution moat in two beats; 15 tools grouped by use case lets devs skim; three client quickstarts open funnel to Claude Desktop + ChatGPT Custom Connector (dominant MCP audiences); pricing framed as *delivery not access* matches §4; kills "Overnight Edge" + "score ≥ 6" in one sweep.

---

### §9.2 llms.txt (`public/llms.txt`)

**CURRENT (full re-read):** prose-heavy, 97 lines, claims *"Everything is free. No paywall,"* cites *"8:30 AM EST,"* references *"premium signals matching 80%+ win rate patterns,"* lists 5 `premium_score` patterns with specific win rates (81.4% / 80.0% / 81.3% / 84.6% / 80.0%), reports *"Performance (287 Tracked Signals) — Overall win rate: 73.2%,"* lists 9 MCP tools, documents a schema full of retired V3 fields.

llms.txt is the canonical file AI crawlers look for (per https://llmstxt.org).

**PROBLEMS:**
- ❌ **Pricing claim "Everything is free. No paywall"** — contradicts the pinned three-tier pricing. Ship a paid product behind this and every AI agent will say *"I thought this was free?"*
- ❌ **Retired aliases everywhere:** "Overnight Edge," "8:30 AM," `premium_score ≥ 2` framing, "score 6+" gate.
- ❌ **Retired performance claims with specific win rates** we cannot substantiate on V5.3 (N<30). Legal risk per §2; contradicted by memory `project_hedge_flag_is_the_alpha`.
- ❌ **9-tool list (missing 6).**
- ❌ **Data schema lists `premium_score`, `premium_hedge`, etc.** — V5.3 does not use these gates.
- ⚠️ **Spec-compliance:** llms.txt spec wants terse H1 + blockquote + `## Section` bullets. Current file is prose-heavy and under-linked.
- ⚠️ **"Agent Arena: multiple AI models debate"** — retired aliased "7 AI Models Debate Today's Best Trade" (now 3–5 models). Perplexity and ChatGPT do cite specific numbers.

**REWRITE (proposed file contents — full replacement):**

```
# GammaRips

> One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM.

GammaRips is a paper-trading options engine for working professionals. Every weeknight it scans 5,230+ US equities for institutional overnight options flow, applies deterministic quality gates, and publishes at most one trade idea by 9:00 AM ET. The trade has pre-set stop (−60% on option), target (+80%), and scheduled exit (3:50 PM ET on trading day 3). Free users see the pick on the webapp; paid users get it pushed to WhatsApp and can @mention an AI agent in the group.

Paper-trading, educational only. Not investment advice.

## Core docs

- [Trading strategy (V5.3)](https://gammarips.com/how-it-works)
- [Today's pick](https://gammarips.com/signals)
- [Scorecard (paper ledger)](https://gammarips.com/scorecard)
- [Pricing — Free / Starter $19 / Pro $39 / Founder $29 lifetime](https://gammarips.com/pricing)
- [Developer docs — 15 MCP tools, no auth](https://gammarips.com/developers)

## Gate stack (V5.3)

1. **Scanner** — overnight signals across 5,230 tickers.
2. **Enrichment** — `overnight_score >= 1 AND spread <= 10% AND directional_uoa_usd > 500000`.
3. **Signal-notifier** — `V/OI > 2`, `moneyness 5–15% OTM`, `VIX <= VIX3M`, `LIMIT 1`.
4. **Forward paper-trader** — enters 10:00 ET day-1, −60% stop, +80% target, exits 15:50 ET day-3. Stop wins over target on ambiguous bars.

## MCP server (free, no auth)

- Endpoint: `https://gammarips-mcp-406581297632.us-central1.run.app/sse`
- Transport: SSE
- Tools (15): `get_todays_pick` (primary), `list_todays_picks`, `get_freemium_preview`, `get_overnight_signals`, `get_enriched_signals`, `get_signal_detail`, `get_enriched_signal_schema`, `get_signal_performance`, `get_win_rate_summary`, `get_open_position`, `get_position_history`, `get_daily_report`, `get_report_list`, `get_available_dates`, `web_search`.

## Pricing

- **Free** — daily pick on webapp, scorecard, all 15 MCP tools.
- **Starter $19/mo** — daily email with the pick + 3-day outcome.
- **Pro $39/mo** — WhatsApp push at 9:00 ET + @mention an AI agent in the private group.
- **Founder $29/mo** — lifetime rate, first 500 customers.

## Disclaimers

Paper-trading performance, educational only. Not investment advice. Past performance is not a guarantee of future results. Options trading involves substantial risk of loss. GammaRips does not make personalized recommendations.

## Contact

- https://gammarips.com
- ceo@gammarips.com
- https://x.com/GammaRips
```

**WHY:** spec-compliant llms.txt format, One Promise is the first crawlable line, V5.3 gate stack stated deterministically (no retired premium_score framing), 15 tools named, zero win-rate claims (respects N<30 floor), disclaimers baked in.

---

### §9.3 AI Plugin manifest (`public/.well-known/ai-plugin.json`)

**CURRENT:** standard ChatGPT-plugin v1 manifest. `description_for_human`: *"Institutional options flow intelligence. Daily overnight signals scored and enriched by AI."* `description_for_model` is generic data-API framing, mentions "4 AM EST" update. `api.type: "openapi"` → `https://gammarips.com/api/openapi.json`. `contact_email: "support@gammarips.com"`. `auth.type: "none"`.

**PROBLEMS:**
- ⚠️ **`description_for_human`** is feature-framed. Crawlers surface this verbatim; should carry the One Promise.
- ⚠️ **`description_for_model`** buries the primary entry point. LLMs have to infer that `get_todays_pick` is the main tool.
- ❌ **`api.type: "openapi"` → `https://gammarips.com/api/openapi.json`** — needs verification (likely 404). ChatGPT-plugin/OpenAPI format was superseded by MCP mid-2024. Drop the ChatGPT-plugin OpenAPI path; repoint to MCP.
- ⚠️ **`contact_email: "support@gammarips.com"`** — inconsistent with rest of codebase (`ceo@gammarips.com`).
- ⚠️ **File assumes the ChatGPT-plugin era.** Modern agents read `mcp.json` or SSE directly.

**REWRITE:** replace with a minimal MCP-pointer version.

```json
{
  "schema_version": "v1",
  "name_for_human": "GammaRips",
  "name_for_model": "gammarips",
  "description_for_human": "One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM. Free MCP endpoint with 15 tools.",
  "description_for_model": "GammaRips is a paper-trading options engine. It produces at most one trade idea per weekday, published by 9:00 AM ET, with pre-set stop (-60% on the option), pre-set target (+80%), and pre-scheduled exit (3:50 PM ET on trading day 3). Primary tool: get_todays_pick returns the single V5.3 pick for today or null. Secondary tools: get_enriched_signals, get_signal_detail, get_win_rate_summary, get_open_position, get_daily_report. Full tool list at https://gammarips.com/mcp.json. Paper-trading performance, educational only. Not investment advice.",
  "auth": { "type": "none" },
  "api": {
    "type": "mcp",
    "url": "https://gammarips-mcp-406581297632.us-central1.run.app/sse",
    "manifest": "https://gammarips.com/mcp.json"
  },
  "logo_url": "https://gammarips.com/logo.png",
  "contact_email": "ceo@gammarips.com",
  "legal_info_url": "https://gammarips.com/terms"
}
```

**WHY:** `description_for_human` carries the One Promise; `description_for_model` names `get_todays_pick` as primary entry point and disclaimer-floors the output; `api.type: "mcp"` aligns with how the product is actually consumed. **Follow-up:** verify `/api/openapi.json` serves something — if 404, ship the MCP-pointer version above.

---

### §9.4 MCP manifest (`public/mcp.json`)

**CURRENT (webapp `public/mcp.json`):** `name: "GammaRips Overnight Edge"`, description feature-framed with "5,000+ tickers" and "0-10 scored," uses non-standard `capabilities` array (`["overnight_signals", "technicals", "news_analysis", "contract_recommendations", "market_themes", "chat"]`), `data_freshness: "Daily by 06:00 EST"` (wrong — should be 9:00 ET), `universe: "5,000+"` (should be 5,230), no `tools` list.

**CROSS-REFERENCE (`gammarips-mcp/mcp.json`):** same stale name "GammaRips Overnight Edge", but uses spec-compliant `tools` array with **9 tool names** (missing 6), `universe: "5,230+"`, `tags: [...]`. No `capabilities` field.

**PROBLEMS:**
- ❌ **The two files disagree.** Webapp uses `capabilities` (non-standard); MCP-repo uses `tools` (spec-compliant). Webapp version is non-compliant with the MCP spec.
- ❌ **Both use "GammaRips Overnight Edge" as `name`** — retired alias.
- ❌ **Webapp lists 0 tools; MCP-repo lists 9 tools** — ground truth is 15.
- ❌ **"6:00 EST" (webapp) is wrong.** V5.3 publishes at 9:00 ET.
- ❌ **"5,000+ tickers" (webapp) vs "5,230+" (MCP repo)** — canonical is 5,230.
- ⚠️ **`capabilities: ["chat"]`** in webapp is misleading — no chat tool exists.
- ⚠️ **Neither file links to pricing.** Agent crawlers that want to recommend upgrade paths have no pointer.

**REWRITE (proposed unified `mcp.json` — write to BOTH locations, identical contents):**

```json
{
  "name": "GammaRips",
  "description": "One options trade a day, scored before you wake up. Free MCP endpoint exposing 15 tools over the V5.3 paper-trading engine. Paper-trading, educational only. Not investment advice.",
  "url": "https://gammarips-mcp-406581297632.us-central1.run.app/sse",
  "auth": { "type": "none" },
  "tools": [
    "get_overnight_signals",
    "get_enriched_signals",
    "get_signal_detail",
    "get_todays_pick",
    "list_todays_picks",
    "get_freemium_preview",
    "get_signal_performance",
    "get_win_rate_summary",
    "get_open_position",
    "get_position_history",
    "get_daily_report",
    "get_report_list",
    "get_available_dates",
    "get_enriched_signal_schema",
    "web_search"
  ],
  "primary_tool": "get_todays_pick",
  "publication_time": "09:00 ET weekdays",
  "universe": "5,230 US equities",
  "tags": ["options", "institutional-flow", "overnight", "paper-trading",
           "signals", "mcp", "free"],
  "links": {
    "home": "https://gammarips.com",
    "pricing": "https://gammarips.com/pricing",
    "developers": "https://gammarips.com/developers",
    "llms_txt": "https://gammarips.com/llms.txt"
  },
  "creator": { "name": "GammaRips", "url": "https://gammarips.com" },
  "license": "https://gammarips.com/terms"
}
```

**WHY:** single canonical file written to both paths ends cross-repo drift; 15-tool list matches `gammarips-mcp/src/server.py:52-66`; `primary_tool: "get_todays_pick"` tells MCP-aware agents what to call first (One Promise as metadata); `links` block gives crawlers deep-link targets.

---

### §9.5 Root layout metadata (`src/app/layout.tsx`)

**CURRENT:** `title.default: 'GammaRips | The Overnight Edge — Know What Smart Money Did Last Night'`; `description` feature-framed with "5,230+ tickers" + "Signals scored 1-10"; `openGraph.title` + `twitter.title`: `'GammaRips | The Overnight Edge'`; `organizationSchema` has `alternateName: "The Overnight Edge"` and `description: "Know what smart money did last night — before the market opens."`; `email: "support@gammarips.com"`.

**PROBLEMS:**
- ❌ **"The Overnight Edge" retired alias appears in 5 fields:** `title.default`, `openGraph.title`, `twitter.title`, `organizationSchema.alternateName`, `organizationSchema.description`. Largest single source of stale-alias SEO drift — every indexed page + every social share inherits this.
- ❌ **`title.default` is the global fallback.** Title still reads "Know What Smart Money Did Last Night" (past-tense, observational, off-promise).
- ❌ **`description` is feature-framed** (5,230 tickers, scored 1-10). §4 hero ships the outcome frame but metadata doesn't.
- ⚠️ **No mention of V5.3, one-trade-a-day, or 9:00 ET** in any metadata field.
- ✅ `template: "%s | GammaRips"` + `metadataBase` are correct. Keep.

**REWRITE (key changes):**
- `title.default`: *"GammaRips — One options trade a day, pushed to your phone at 9 AM"*
- `description`: *"GammaRips scans institutional options flow overnight and mechanically picks one contract each morning — with stop, target, and exit all pre-set. See today's pick on the webapp or get it pushed to WhatsApp. Paper-trading, educational only."*
- `openGraph.title` + `twitter.title`: *"GammaRips — One options trade a day"*
- `openGraph.description` + `twitter.description`: *"Scored before you wake up. Pushed to your phone at 9 AM."*
- OG image: bump `og-image.png?v=2` → `v=3`
- `keywords`: add `"one trade a day"`, `"paper trading options"`, `"MCP options API"`
- `organizationSchema`: **delete `alternateName: "The Overnight Edge"`**, change `description` to *"One options trade a day. Scored before you wake up. Pushed to your phone at 9 AM."*, change `email` from `support@gammarips.com` → `ceo@gammarips.com`.

**WHY:** `title.default` carries the One Promise, so every un-overridden page inherits it; outcome-framed `description` lifts SERP snippet quality; `alternateName` deletion propagates to Google Knowledge Graph — single most important JSON-LD fix on the site.

---

### §9.6 Per-date report page (`src/app/reports/[date]/page.tsx`)

**CURRENT (key facts):**
- Uses `generateMetadata` to produce per-date titles, description, canonical, OG.
- Pulls `report.seoMetadata.seoTitle` and `report.seoMetadata.seoDescription` from Firestore if present; falls back to `"Report ${date} | GammaRips"` + feature-framed description.
- Emits two JSON-LD blocks: `Article` schema + `Dataset` schema.
- `Article.headline` falls back to `"GammaRips Overnight Report ${date}"`.
- `Dataset.name` and `description` reference "5,230+ tickers" and "institutional options flow scan."
- OG `title` appends "— Overnight Edge" — **stale alias leaks into article OG tags.**

**PROBLEMS:**
- ❌ **OG title suffix `"— Overnight Edge"`** (line 27) — retired alias leaks into every per-date report's social card. Reports are the most-linked-to pages after home.
- ❌ **Fallback `Article.headline`** uses "Overnight Report" framing, not "V5.3 daily pick." If `report.title` is missing, Article schema publishes the wrong story to Google.
- ⚠️ **No `Article.about` pointing at the pick.** Report is about one ticker + one contract + one bracket; schema doesn't say that.
- ⚠️ **`Dataset.variableMeasured`** misses V5.3-specific variables (`V5.3 gate pass`, `3-day bracket outcome`).
- ⚠️ **No disclaimer in the rendered page.** Body relies on upstream report carrying it — publisher-exclusion gap if the report-generator regresses.
- ✅ Canonical link, Article + Dataset dual-schema: correct per SEO Audit skill.

**REWRITE (targeted patches — page is mostly good):**

1. **Drop "— Overnight Edge" from OG title** (line 27): change `title: \`${title} — Overnight Edge\`` → `title: title`.
2. **Fix Article.headline fallback:** `report.title || \`GammaRips V5.3 pick for ${date}\``.
3. **Add `Article.about`** with `@type: "Thing"` + ticker/direction + description *"Single V5.3 daily pick with pre-set stop, target, and exit."* Add `Article.disclaimer` field with the paper-trading line.
4. **Add persistent footer disclaimer** below the `<ReactMarkdown>` body: *"Paper-trading performance, educational only. Not investment advice. Past performance is not a guarantee of future results."*
5. **Expand `Dataset.variableMeasured`** with `overnight_score`, `V/OI ratio`, `moneyness`, `VIX-VIX3M regime`, `V5.3 gate status`, `3-day bracket outcome`.

**WHY:** stale-alias removal is highest-value (every social share inherits it); `Article.about` lifts pages from "generic report" to "article about [ticker] options" in Google's entity graph; footer disclaimer protects publisher-exclusion posture if upstream regresses.

---

### §9.7 War Room (`src/app/war-room/page.tsx`) — **VERDICT: KILL**

**WHAT IT IS:**
- Route: `/war-room`
- Purpose: Gated landing page for a "live institutional flow alerts via WhatsApp" tier priced at **$149/mo** per current copy.
- Auth-walled: redirects to login; then checks for `plan === 'warroom'` or `subscriptionStatus === 'founder_lifetime'`.
- Metadata title: "The War Room — Live Institutional Flow Alerts via WhatsApp"
- Features listed: "8:30 AM EST Daily Overnight Edge report," "9:30 AM EST Pre-market enriched picks," "Intraday high-conviction alerts," "4:30 PM EST Win tracker results," and "GammaMolt is our AI-powered institutional flow analyst."

**PROBLEMS:**
- ❌ **Pricing is $149/mo** — retired tier. Current structure is Free / Starter $19 / Pro $39 / Founder $29 lifetime.
- ❌ **"Overnight Edge" alias** in metadata title and in-page copy.
- ❌ **"8:30 AM EST" and "9:30 AM EST" timestamps** — stale; canonical is 9:00 ET.
- ❌ **"Pre-market enriched picks + Intraday high-conviction alerts"** — V5.3 produces ONE pick per day, not multiple streams. Invented copy.
- ❌ **GammaMolt as user-facing character** violates §2 DON'T rule.
- ❌ **Purpose overlaps 100% with Pro tier** (WhatsApp push + @mention agent). War Room is the V3-era name for this same concept at a 4× markup.

**VERDICT: KILL.**

**Proposed action:**
1. **301 redirect** `/war-room` → `/pricing#pro`.
2. **Delete** `src/app/war-room/page.tsx` and `war-room-client.tsx`.
3. **Audit Firestore** for `plan === 'warroom'` users. If active billers exist on $149/mo, customer-service escalation: cancel Stripe sub, comp 3mo Pro, email from `ceo@gammarips.com`. Do not silently downgrade.
4. **Update `sitemap.ts`** to remove `/war-room`.
5. **Search repo** for `war-room` references (imports, links, redirects) and purge.

**WHY KILL not REWRITE:** "War Room" as a brand asset signals adrenaline-trader tone (§2 DON'T: commercial-pilot voice). Pro tier is the mechanical, calm version of the same product. Two names for one thing confuses buyers; clean kill is less tech debt long-term.

---

### §9.8 History (`src/app/history/page.tsx`) — **VERDICT: KILL**

**WHAT IT IS:**
- Route: `/history`
- Purpose: "Historical Performance" page with a date-picker calendar.
- On click: shows an `alert()` dialog `"Would load signals for YYYY-MM-DD"` with a code comment `// In a real app, this would route to a page fetching that date's data`.
- Right-hand card: empty-state "Track Record (Coming Soon) — We are building a comprehensive performance dashboard..."

**PROBLEMS:**
- ❌ **It is literally a stub.** Button triggers `window.alert()`, not a route. Worst credibility signal on the webapp.
- ❌ **"Coming Soon"** placeholder with no date/what violates §2 Moran Rule 4.
- ❌ **Functional overlap** with `/scorecard` (canonical V5.3 ledger) and `/reports` (dated archive). `/history` is a third, worse version.
- ⚠️ Calendar legacy cutoff `< 2024-01-01`; V5.3 started 2026-04-17.

**VERDICT: KILL.**

**Proposed action:** 301 `/history` → `/reports`; delete `src/app/history/page.tsx`; update `sitemap.ts`; audit nav + footer for links and repoint.

**WHY KILL not REWRITE:** scorecard is the canonical historical surface; `/reports` is the canonical date-indexed archive. Third version adds confusion. `window.alert()` on a live route is actively damaging to conversion — kill + redirect is minutes of work.

---

### §9.9 Legal pages tone-consistency check

**`/privacy/page.tsx`** — 3 × "The Overnight Edge" alias hits (lines 3, 15, 23). "Last updated: February 13, 2026" stale. No pricing issues. Disclaimer posture fine. **Fix:** global replace `The Overnight Edge` → `GammaRips`, bump last-updated to pricing-launch date.

**`/terms/page.tsx`** — 2 × alias hits (lines 3, 15). **Section 5 "API Usage"** references "API keys are for your use only" — contradicts the authless MCP product. **Section 6** uses "proprietary" (fine for legal copy, just note §2 retires it as a marketing word). "Last updated" stale. **Section 2 "Not Financial Advice"** is load-bearing for *Lowe* publisher exclusion — keep verbatim. **Fix:** alias replace, rewrite Section 5 to *"You may not redistribute or resell the raw data output of our MCP endpoint without written permission,"* bump last-updated.

**`/unsubscribe/page.tsx`** — functional UI, no aliases, no stale pricing. **Fix:** tighten vague error toast (*"We couldn't process your request. Please try again or contact support"*) to name the failure mode ("email not found or link expired") + add `ceo@gammarips.com`.

---

### §9.10 Account / auth screens

**`/account/page.tsx`** — **VERDICT: KEEP.** Tone fine. Issues: (1) MCP API section says "free and open" without clarifying that paid tiers buy *delivery*, not MCP access — confusing once Pro ships. (2) No tier-status section (user cannot see Free/Starter/Pro/Founder + renewal). (3) No billing-portal link once paid. **Fix:** add tier-status + Stripe Customer Portal link section on paid-launch day.

**`/auth/processing/page.tsx`** — **VERDICT: KEEP.** Calm tone correct. Issue: error toast *"Could not initiate subscription. Please contact support"* is vague and lacks email. **Fix:** add `ceo@gammarips.com` + real failure reason.

**`/auth/action/page.tsx`** — **VERDICT: KEEP.** `verifyEmail` flow clean. Issues: (1) error *"An error occurred during verification. Please try again"* is vague — tighten to "The verification link has expired. Request a new one from your account page." (2) "Please create an account to continue" — drop "Please" for calm-pilot voice: "Create your GammaRips account to continue."

---

### §9.11 Updated implementation ladder

The §7 ladder needs these additions. Re-ranking where relevant:

**New Tier 1 items (conversion-critical, ship with or before paid launch):**

- **1a. llms.txt rewrite** — highest-leverage AI-discovery fix; cheap, irreversible leverage once crawlers cache.
- **1b. Root layout metadata + organizationSchema rewrite** — drop `alternateName: "The Overnight Edge"`, repoint title/OG/Twitter to One Promise. Propagates globally.
- **1c. Developers page rewrite** — 15-tool listing, three MCP-client quickstarts, pricing-delivery-not-access framing.
- **1d. mcp.json unified rewrite** — single canonical file for both repos, `primary_tool: get_todays_pick`, 15 tools.
- **1e. Kill war-room route** — delete + 301 to `/pricing#pro` + Firestore user migration if any `plan === 'warroom'` billers exist.
- **1f. Kill history route** — delete + 301 to `/reports`.

**New Tier 2 items:**

- **2a. ai-plugin.json repoint to MCP** — minimal pointer, drop OpenAPI path.
- **2b. Per-date report page patches** — drop OG "Overnight Edge" suffix, upgrade Article schema, persistent footer disclaimer.
- **2c. Account page tier-status + billing-portal** (once paid tiers live).
- **2d. Legal-pages alias sweep** — privacy + terms (5 alias hits total) + terms §5 authless MCP fix + last-updated dates.

**New Tier 3 items (polish):**

- **3a. Auth/unsubscribe error-state specificity** — tighten vague toasts + add `ceo@gammarips.com`.
- **3b. OG image refresh** — bump `v=2` → `v=3` once new copy ships.

**Retirements:** none. Existing §7 ladder intact.

**Re-ranked Tier 1 (integrated):** (1) Pricing page, (2) FAQ, (3) Hero, (4) llms.txt **new**, (5) Root layout metadata + organizationSchema, (6) Developers page **new**, (7) mcp.json **new**, (8) Kill war-room **new**, (9) Kill history **new**, (10) How It Works four-card, (11) About time grid, (12) Signals detail V5.3-status chip.

---

### §9.12 Additional open questions for Evan

1. **`/api/openapi.json` — does it exist?** ai-plugin.json references it. If 404, adopt the MCP-pointer version in §9.3.
2. **War Room user migration** — before 301, Firestore read on `users` where `plan == 'warroom'`. Any active $149/mo billers need a customer-service script (cancel + comp 3mo Pro + email). If zero, delete without ceremony.
3. **`ceo@` vs `support@gammarips.com`** — five files disagree (layout.tsx uses `support@`, all others use `ceo@`). Standardize on `ceo@` in the sweep, or spin up a real `support@` inbox first?
4. **Pro tier name** — keep "Pro" ($39) as billing name, use feature framing ("WhatsApp push + group AI agent") in marketing? Confirm.
5. **llms.txt refresh cadence** — recommend generating from `src/content/llms.md` and auto-deploying on build to prevent drift with `docs/TRADING-STRATEGY.md`.
6. **OG image v=3** — design capacity in next 30 days to ship a new image that lands the One Promise? If not, defer to Month 2 and keep v=2.

*End of §9 addendum. 10 surfaces audited; verdicts: 2 kills (`/war-room`, `/history`), 8 rewrites. AI-discoverability cluster (llms.txt + layout.tsx + developers + mcp.json) is the highest-leverage block in this plan document.*
