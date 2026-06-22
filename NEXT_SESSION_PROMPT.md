# Next Session Prompt

**▶ 2026-06-22 — V7.1 "TILTED GIGO" COHORT RESET + this morning's missed-email fix (LIVE).**
- **MISSED EMAIL (root cause, fixed):** Mon 06-22's pick email didn't fire. NOT the tilt — the pipeline picked TTWO fine. The dedup-send guard keyed its claim on `scan_date`; Friday's pre-holiday-guard Juneteenth cron sent + claimed `email_sends/2026-06-18` (07:31 ET 06-19), and Monday re-processed the SAME scan_date (no scan over the holiday) → stale claim suppressed the real send. **Resent TTWO surgically** (`.scratch/resend_2026-06-22.py`, reuses prod email builder, NO re-pick) — operator + 1/1 sub fan-out at 09:50 ET pre-entry. **Durable fix:** re-keyed `claim_email_send` on the ET **run-day** (signal-notifier, folded into rev `00049-6x9`); `gammarips-review` SHIP. Doc: `docs/DECISIONS/2026-06-22-dedup-claim-rekey-runday.md`. OPERATOR: force a resend by deleting `email_sends/{TODAY_ET}` (not `{scan_date}`).
- **V7.1 TILTED GIGO RESET (owner-directed):** `forward_paper_ledger` TRUNCATED (12 rows dumped to `.scratch/forward_paper_ledger_pre_v7_1_truncate_2026-06-22.json`); `policy_version` relabeled `V7_INTRADAY` → **`V7_1_TILTED_GIGO`** across all 5 services; `LIVE_COHORT_START_DATE` → **2026-06-23**. EXECUTION UNCHANGED — ".1 Tilted" = the 60-day momentum enrichment tilt only. **Cohort starts 06-23, NOT today:** TTWO (scan 06-18, entry 06-22) is a CONFIRMED pre-tilt pick — its 06-18 pool was enriched 06-19 AM before the tilt deploy, and Mon's 05:30 enrichment skipped re-enriching it (">3 days stale") — so it's excluded by the 06-23 floor. `gammarips-review` SHIP. cohort_stats/current = V7_1 / cohort_start 2026-06-23 / 0 trades. Revs: forward-paper-trader-00047-zsc, signal-notifier-00049-6x9, win-tracker-00014-9gn, x-poster-00040-kzl, blog-generator-00027-2x9. Doc: `docs/DECISIONS/2026-06-22-v7-1-tilted-gigo-cohort-reset.md`. **First V7.1 trade = the 06-23 entry (tonight's scan, first tilt-enriched pick).**
- **OPEN:** (a) webapp "V7.1 Tilted GIGO" display copy (separate repo, owner pushes; live numbers already flow from cohort_stats); (b) optional purge of the lone floor-excluded TTWO/06-22 `V7_1` row after its 16:30 write (cosmetic — excluded everywhere by the floor); (c) engine working tree still uncommitted on `gate-changes-2026-06-02` (now also the dedup fix + V7.1 relabel + 2 new decision docs).

**▶ NEXT TOUCH = monitor the live MOMENTUM-TILT cohort toward N≥15 (first tilted pick Mon 2026-06-22) + decide the pool-cap 50→25 flip (coverage says safe; flip AFTER the tilt earns a clean read, OR now for the cost win — owner's call). Branding "V7.1 Tilted GIGO" PARKED for next session (owner likes it; do NOT rename policy_version yet). Still open: intraday entry-window features (#2 below) + re-run edge-test at ~85–90 effective days/new regime. No urgent action — daily crons run end-to-end; momentum tilt is live in enrichment.**

**▶ 2026-06-19 — MOMENTUM EDGE FOUND + SHIPPED (the session's headline), + market-holiday guard, + pool-cap coverage.**
- **🎯 60-DAY MOMENTUM IS A REAL, ADDITIVE SELECTION LEVER — the first thing to beat the bullish baseline AND survive walk-forward.** Owner's instinct ("stocks ripping are the options to trade") CONFIRMED, but the tradeable horizon is the **1–3 month rip, NOT literal year-over-year** (252d clears zero in-sample but collapses out-of-sample). On the frozen 1,375 option-PnL set: bullish baseline +4.11%/47% → **60-day top-quintile (mom_60 ≥ +0.35) ~+11.4%/55.9%, marginal +8.4pp (CI clears zero), stable in BOTH walk-forward halves** (+16.9%→+7.5%). Pure momentum at all horizons {20,60,126,189,252}, NO reversal; win-rate effect not tails; not redundant with overnight_score (corr +0.29). Decision: `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`. Memory: `project_momentum_60d_lever`.
- **DEPLOYED as a SOFT edge-rank tilt** in `enrichment-trigger` `_edge_select_top_n` (**rev `enrichment-trigger-00045-f89`**, `gammarips-review` PASS). `edge = +2.0 BULLISH +1.5 delta-band +1.25(mom_60≥0.35)`, tie-break mom_60 desc. mom_60 from 2 Polygon grouped-daily ADJUSTED calls (anchor + 60-session lookback, both ≤ scan_date — leakage-asserted), cached/run. **Kill switch:** `MOMENTUM_TILT=false` → bit-identical to old delta-only. Fail-soft (fetch fail → delta-only, never crashes). mom_60 LOGGED only (no schema change). **It tilts the POOL the tournament votes on — it does NOT touch the judge/prompt (unchanged) and does NOT guarantee the final pick is high-momentum.** Env knobs `MOMENTUM_TILT/MOM_LOOKBACK_DAYS=60/MOM_THRESHOLD=0.35`. New dep `pandas-market-calendars==4.6.1`. **First tilted pick: Mon 2026-06-22.** **N≥15 live-cohort revisit lock.**
- **"Ride recent WINNERS" exploit is FALSIFIED** (the variant the session started from) — recent option winners MEAN-REVERT (underperform non-winners in every cell; intersection never beats baseline; 0/17 comparisons clear zero). Underlying *price trend* works; our *scoreboard* does not. Memory: `project_exploit_winners_falsified`. (Stronger dials than the tilt, if the cohort pays: feed mom_60 to the judge [prompt change] or a separate deterministic Momentum-Pick sleeve — the two-picks-a-day / **"V7.1 Tilted GIGO" branding** idea the owner likes, parked for next session.)
- **POOL-CAP COVERAGE: 25 is the floor; 50 is overkill (only 4/46 days ever had >50 candidates).** Best-name capture N=10 56% / N=20 89% / **N=25 93.5% (ceiling CI touches zero)**; 10 drops the winner 43% of days. Cutting `TOURNEY_POOL_CAP`+`ENRICH_TOP_N` 50→25 ~halves grounded-enrichment + tournament LLM cost with no demonstrated ceiling loss, and makes the tilt more decisive. **PENDING owner decision** (ceiling test, not LLM-pick-quality): flip to 25 AFTER the tilt gets a clean N≥15 read (clean attribution), OR now for the cost win (accept confounding). Env knob, instantly reversible. Finding/decision: `docs/DECISIONS/2026-06-19-pool-cap-coverage.md`. Memory: `project_pool_cap_coverage`.
- **NEW DATA ASSET:** 686-ticker adjusted underlying daily-bar cache `backtesting_and_research/cache/poly_daily_underlying/{TICKER}.parquet` (Dec2024–Jun2026, 262K rows — the input the momentum research needed). Built by `backtesting_and_research/fetch_underlying_daily_bars.py` (resumable; pulls POLYGON_API_KEY from Secret Manager at runtime — never to disk).
- **SUBSTRATE AUDIT (corrects the 06-17 handoff):** `enriched_option_outcomes` is actually backfilled CONTINUOUS Apr10–Jun17 (NO May→Jun gap) but has **145 dup rows** (concentrated 06-10), inconsistent daily counts (clean 50/day only from Jun11), and there is **NO standalone `market_regime_daily` table** (regime folded inline; the keystone snapshot was never built — still job #2). Memory: `project_substrate_quality_2026_06_19`. Cleanup (dedup + regime table) = review-gated BQ writes, NOT done.
- **MARKET-HOLIDAY STAND-DOWN guard SHIPPED** (Juneteenth fired an email + trade on a closed market — looked amateur). On any NYSE non-trading day both entry-day services stand down: `signal-notifier` (rev `00047-w6n`) sends NO email/WhatsApp + writes a `market_holiday` skip doc keyed to the PRIOR session (so the next real run cleanly overwrites it; webapp shows "markets closed"); `forward-paper-trader` (rev `00046-fml`) writes one `MARKET_HOLIDAY` skip row, no sim. Webapp `market_holiday` copy pushed (`082eb7d4`). Uses the already-present NYSE calendar (`is_trading_day`); `gammarips-review` PASS. Decision: `docs/DECISIONS/2026-06-19-market-holiday-standdown.md`. NOTE: forward-only — did NOT fix today's already-sent 06-19 display (Monday's run overwrites it); next holiday is July 3.
- **Git:** all on `gate-changes-2026-06-02`, engine working tree NOT committed (enrichment momentum tilt, holiday guards in signal-notifier+forward-paper-trader, 3 new decision notes, TRADING-STRATEGY momentum+holiday paragraphs, new fetch script + 686-ticker bar cache). Webapp commits pushed live (`082eb7d4`). **OPEN:** commit the engine working tree; push/merge `gate-changes-2026-06-02` → master when ready.

**▶ 2026-06-18 — late-session additions (V7 cohort grown + two research arcs).**
- **CVE + PLD loaded into the V7 ledger.** They were the actual tournament picks for 06-15 (CVE BULLISH $29C, medium) and 06-16 (PLD BULLISH $150C, **high/3-3 consensus**); loaded under V7 same-day. **Cohort now 8 trades: 3W/5L (37.5% win), ROI +0.8%, net +$46** (CVE −2.0%, PLD −36.2% STOP). PLD = the highest-confidence pick AND the worst trade — confidence/score/flow do NOT predict the winner (matches the edge-test). Still net-positive even absorbing a −36% (V7 contained it same-day). N=8 = NOISE; do not over-read.
- **#1 DONE — substrate fully RE-LABELED under V7.** `enriched_option_outcomes` re-backfilled under V7 same-day mechanics: verified **100% V7_INTRADAY (2,789 rows / 45 dates, 0 V6 remaining, 68% fill, 0 errors)**. Raw same-day pool ≈ 564W/1342L (~30% win — lower than the 3-day label's 44%, since same-day hits the +40 target less; most are TIMEOUT flats). Ready for #2.
- **#2 SCOPED — INTRADAY ENTRY-WINDOW FEATURES (the live next research arc).** V7 trades intraday but 100% of our features are OVERNIGHT. A same-day edge most likely lives in the **9:30–10:00 ET entry tape**: overnight gap, open-30min return, open range/ATR, relative volume, price-vs-VWAP at 10:00, the option's open-window move. **Build:** compute from the bars `_simulate_contract` ALREADY fetches → add columns to `enriched_option_outcomes` → backfill → run the edge-test lever-screen on intraday features vs the V7 outcome. **LEAKAGE RULE (gates it):** features use ONLY data with ts ≤ 10:00 ET entry_day (≥10:00 = trade window = outcome); assert + `gammarips-review`. **Prize:** a leakage-safe ENTRY GATE — the first V7-aligned selection lever. Still day-power-limited, but the one place we've never looked.

**▶ 2026-06-17 (LATE) — V6 IS DEAD; V7 "GIGO" (Get In, Get Out) IS LIVE. Owner-directed full cutover.** V7 keeps the V6 bracket-tournament SELECTION unchanged and replaces the exit with a **same-day intraday OCO bracket**: 10:00 ET entry → **+40% take-profit / −30% stop / flat 15:45 ET**, no trail, no overnight. `policy_version='V7_INTRADAY'`. Rationale (velocity backtest `backtesting_and_research/exit_velocity_sweep.py`, 846 bullish fills, 2% slippage, day-level CIs): same-day exit is ~tied per-trade with the 3-day hold but **~3× return-per-capital-day** and **halves the disaster tail (−34% vs −61%)**; per-trade improvement NOT significant (the case is velocity + tail). Lever within H1 is noise; −30 stop best tail. Decision: `docs/DECISIONS/2026-06-17-v7-intraday-bracket.md`. `gammarips-review` PASS (twice — mechanics + doc-discipline).

**SHIPPED (all deployed):** forward-paper-trader `00045-6qq` (V7 constants: HOLD_DAYS=1, STOP 0.30, TARGET 0.40, EXIT 15:45, USE_TRAIL=False), signal-notifier `00045-m6w` (cohort→V7; LIVE_COHORT_START_DATE=2026-06-08 = first V7 entry), win-tracker `00013-hlr`, blog-generator `00026-rl8`, x-poster `00039-2vz` (callback timing verified V7-safe — 16:45 cron after 16:30 same-day close, newest-first QRT pairs the morning signal; "3-day exit" label→"same-day close"). Webapp V7/GIGO copy pushed (`gammarips-webapp` `d47e75ec`, auto-deploying). The 6 V6 picks were **re-simulated under V7** (idempotent re-run) — ledger + Scorecard now V7. **V7 cohort: 3W/3L (50%), mean +1.8%/trade, worst −21.4%** (TER −24%→+9%, SMMT −62%→−2% tail-saves; SPG +76%→+15%, HON +16%→−21% give-backs).

**EDGE-TEST WORKFLOW — RAN 2026-06-17 (run `wf_f43a1c3d-99a`), verdict = UNDERPOWERED.** 11 levers screened on `enriched_option_outcomes` (43 days, single regime), 0 survived walk-forward; pool baseline −0.63% (day-level 90% CI brackets 0). delta/ATR had the right sign but decayed early→late half (recency rot); score≥7 "EV inversion" = folklore (sign flips); catalyst was the lone CI-excludes-0 but wrong-signed (the expected false positive). **Re-run the SAME workflow (it's a reusable harness) at ~85–90 effective days + a new regime** — that's the gate for any selection-lever tilt. Script: the Workflow `edge-test-enriched-outcomes`. Memory: `project_agent_data_readiness`.

---

**▶ 2026-06-17 session — DATA SUBSTRATE BUILT (the session's main deliverable) + scorecard fixed. The blockage was never domain expertise — it was reading edge off N=5 live picks (statistically impossible). Now there's a real substrate to answer "is there edge?" — including conclusively proving NO.**

**Honest edge read (owner aligned — do NOT sugarcoat next session):** ROI at N=5–8 is NOISE not verdict (per-trade SD ~50% → SE at N=8 ≈ 18%; observed −4.5% is consistent with true edge of +5%, −5%, or 0 — indistinguishable). Our own research (`project_narrative_vs_physics_roi`) confirmed only ONE weak lever (delta/trap-escape); prior is weak-to-no durable edge. Finding edge in short-dated options off retail-observable flow is one of the hardest problems in the field — expertise mostly prevents self-deception, doesn't conjure alpha. Hold "there may be no edge" openly; the value of what we built is to DECIDE this with power, not keep tweaking.

**NEW — `enriched_option_outcomes` (the keystone, DEPLOYED + BACKFILLED).** RESEARCH-ONLY BQ table (`profitscout-fida8.profit_scout.enriched_option_outcomes`, 63 cols, partition `entry_day`, cluster `ticker`) replaying the live +80/-60/trail bracket over the FULL enriched BULLISH pool (~50/day post-06-12, ~170/day pre-cap) — one outcome row per candidate, not just the 1 daily tournament pick. Leakage-safe option-PnL counterfactual; grows ~50x faster than `forward_paper_ledger`. **Reuses production `_simulate_contract` (pick_doc=None)** via new isolated `POST /label_enriched_pool` + lagged 17:00 ET cron (`forward-paper-trader-label-pool`, after the 16:30 exit cron). Writes ONLY to the research table — HARD-walled from `forward_paper_ledger`/Scorecard/website. `gammarips-review` PASS. Mechanics-match PROVEN: SPG 2026-06-09 row == ledger (entry 3.162, TARGET, +0.764). **Backfill state: COMPLETE — 43 dated pools (2026-04-10→06-12, every closed window; 06-15/06-16 correctly pending as future hold-windows), 2,689 rows, 1,808 with realized PnL (67.2% fill; rest no-bars/INVALID_LIQUIDITY, heavier on pre-cap illiquid contracts). Raw pool ≈ 801W/1,007L = 44.3% win rate (≈ +80/-60 break-even). GATEWAY-TIMEOUT GOTCHA: 06-10's 290-contract pool 504'd at the Cloud Run gateway during the backfill BUT the server completed the write (all 290 landed) — so a logged 504 on a big pool does NOT mean missing rows; VERIFY in the table before re-POSTing. Going forward the daily cron labels ~50-row post-cap pools (~60-90s), well under timeout.** Regenerates the frozen 1,375-trade study (`realized_label.pkl`, dead 2026-05-29) on CURRENT V6 data + extends it. Driver: `scripts/ledger_and_tracking/{create,backfill}_enriched_option_outcomes.py` (HTTP backfill re-mints ID token per date). Decision: `docs/DECISIONS/2026-06-17-enriched-option-outcomes.md`. Memories: `project_agent_data_readiness`, `project_autonomous_edge_regime_agent`.

**Bigger vision this serves (owner):** dedicated Claude-Code-headless-in-a-VM running scheduled read-only BQ loops to (a) detect regime shifts (build FIRST — robust, low overfit risk; needs a `market_regime_daily` snapshot table, NOT yet built — job #2) and (b) find edge (review-gated PROPOSER, never auto-deploy — small-N self-deceives). Real-money = scale position size but CAP ~$10k/contract → income engine (~$7k/mo gross IF edge holds), not infinite compounding (capacity wall + edge decay make the naive compound curve a fantasy). Gated per `project_deferred_alpaca_agent`.

**Scorecard fixed this session (DONE, live):** (1) deleted 6 stale pre-V6 `V5_4_AGENT_RANKER` docs from Firestore `ledger_trades` (orphans the merge-only sync can't prune — OKTA/HTZ/BBY/ADI/PAAS/CIEN); collection now = 5 V6 picks. (2) Added `n_contracts` + `exit_value_usd` to the `ledger_trades` sync (`signal-notifier` deployed `00044-crg`, `/refresh_stats` run) + rebuilt the webapp scorecard table → #/Invested/Exit Value/Profit/ROI (exit_reason → sub-label); `gammarips-webapp` commit `b2ce3a24` pushed to main (auto-deployed). Sizing recap: trader is %-based/contract-agnostic; the $500-target sizing (`GREATEST(1, ROUND(500/(entry*100)))`) lives only in the display layer → 1 contract once entry > $5 (TER's single $1,913 contract distorts the dollar ROI; ROI is capital-weighted, not equal-weighted).

**Git:** committed `13e5339` on `gate-changes-2026-06-02` (local, NOT pushed) — enriched-outcomes feature + deployed-but-uncommitted companions (scorecard, edge-rank, intraday/topscore shadows, 3 prior decision docs). Left uncommitted: `blog-generator/deploy.sh`, `.scratch/`, `analysis_option_pnl.parquet`. **OPEN:** push/merge `gate-changes-2026-06-02` → master when ready; build job #2 (`market_regime_daily`).

---

**▶ 2026-06-10 (superseded) — read the first top-score shadow pair after the 16:30 ET exit cron (`python scripts/ledger_and_tracking/shadow_topscore_compare.py`); otherwise monitor+park until the N≥15 checkpoint.**

**2026-06-08 — DONE: pipeline confirmed back online + top-score deterministic shadow tracker built, reviewed, and DEPLOYED.**

**The engine is no longer dark.** The Monday verification (checklist below) PASSED. The 06-05 scan surfaced a clean pick — **TER BULLISH $380C exp 06-18** (entry 06-08 10:00 ET, exits 06-10). Read-only verify confirmed: real contract priced off last-trade (full greeks; `recommended_spread_pct=NULL` as designed — NOT a fake-spread artifact), no leakage (forward fields NULL), regime rail held (VIX 15.4 ≤ VIX3M 19.23), full **81-signal** tournament pool, HAS_PICK (not a skip), consensus **LOW (1/3 brackets)**. The 06-04 scan had no candidates; the 06-05 scan produced a valid priced pick → the quote-outage fix took. Two amber flags on the pick itself (not the engine): `overnight_score=8` sits in the documented EV-inversion band (≥7), and it's long 94.6% IV bought right after a −13.6% one-day crash.

**NEW — top-score deterministic shadow tracker (DEPLOYED, rev `forward-paper-trader-00041-cs7`).** Owner question: does the LLM tournament earn its tokens vs just trading the top signal? A free retrospective baseline showed blindly trading the top `overnight_score` returned **−6.09% mean option PnL / 33% win over 33 labeled days — worse than random (−1.36%)** (score-inversion). So we forward-track it: each HAS_PICK day the trader now ALSO simulates the pure deterministic top-`overnight_score` pick (tie-break = max directional UOA) under IDENTICAL mechanics and writes BOTH arms to a NEW isolated BQ table **`paper_shadow_topscore`**. **HARD-walled from the Scorecard + website** — writes ONLY to that table, never `forward_paper_ledger` / `current_ledger_stats` / Firestore `todays_pick` / `signal_performance` / any webapp surface; `gammarips.com/scorecard` still shows ONLY the V6 cohort (verified: the scorecard is fed by `signal-notifier compute_and_write_ledger_trades` reading `forward_paper_ledger` WHERE `policy_version='V6_TOURNAMENT'`). `gammarips-review` PASS. Built via a pure `_simulate_contract` extraction (live ledger record byte-identical); shadow is best-effort and can NEVER raise into the live path. **v1 is PAIRED-ONLY** (runs on HAS_PICK days only — not regime/no-candidate skip days). First pair = **TER (tournament, score 8) vs SU (top-score 9, tie-broken over LYB $55.3M / BBWI $7.3M by UOA $58.2M)** — lands at the **06-10 16:30 ET exit cron**. **Decision threshold: N≥15 paired closes.** Doc: `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`. Memory: `project_topscore_shadow_tracker`.

**✅ The Monday verification checklist below — ALL PASSED. Kept for reference:**

The engine had been dark (0 picks/day since scan 2026-06-04); the quote-outage fix + gate recalibration (score≥4 floor, spread gate retired, `_best_contract` prices off last-trade/day-close) was **deployed 2026-06-05** (block below). **Monday's single job: verify the full chain actually surfaces a tradeable pick end-to-end** now that the fix has had Thu/Fri 23:00-ET scans to run. Concretely, check:
1. **Enrichment pool is non-empty with contracts** — `overnight_signals_enriched` for scan 2026-06-04/05 has rows at `score≥4`, `UOA>$500K`, and a **non-NULL `recommended_contract`** (the `has_contract` rate vs the ~58% pre-outage baseline — the open WATCH; no-quote strikes now price off last-trade, so this is the number that proves the fix took).
2. **Tournament produced a pick** — `todays_pick/{scan_date}` has `has_pick=true` (not a `no_candidates_passed_gates` skip), and `signal_ranker_runs` has a `tournament_v1` / version=7 row.
3. **Trader is writing** — `forward_paper_ledger` gets a row at the day-3 exit (writes in arrears; don't misread an empty-today ledger). Ledger health: `python scripts/ledger_and_tracking/current_ledger_stats.py`.
4. **Subscriber email/WhatsApp fired** at 07:30 ET (the operator-facing proof).

If the pool is still empty/`has_contract` collapsed → the last-trade fallback isn't catching; consider the deferred PIT day-bar fix or the Polygon quote-plan upgrade (owner-owned spend decision). If picks ARE surfacing → resume monitor+park; next return trigger is the N≥15 checkpoint.

**SEO — DONE this session, no follow-up needed (archive idea PARKED).** Owner flagged that daily signal pages weren't building SEO. Dogfooded the live site (raw HTTP + browser) + pulled GSC/GA4: the ephemerality fear was wrong (per-ticker pages already persist + rank page-1), the real disease was **CTR collapse from mis-targeted redirects** — `/{TICKER}` (357 indexed) 308'd to `/signals` and `/stocks/{ticker}` (200) to `/` (homepage), discarding the ticker = soft-404 = ~0 clicks on ~5,500 impr/90d. **Fixed + pushed + verified live** in `gammarips-webapp` (commit `ce9db742` on `origin/main`, auto-deployed): retargeted both redirects to `/signals/:ticker` (1:1, ticker-preserving); killed the `| GammaRips | GammaRips` title doubling on ticker + index pages; replaced the generic boilerplate meta with a dynamic per-ticker description built from signal fields when no engine `seoMetadata` exists; added 286 `/signals/{ticker}` URLs to the sitemap (were 0). Verified live: `/MSFT`→308→`/signals/MSFT`, title `HTZ Unusual Options Flow — Bearish | GammaRips`, meta pulls the real thesis. **PARKED (owner decision):** the "accumulate dated history on the ticker page + interlink with `/reports/{date}`" archive idea (the SEO analyst's #4) — real but small/compounding lift, not worth building now; the redirect+meta fix was the 80%. The bigger lever from here is content/off-site, not more ticker-page features. **Watch in GSC over 2–4 wks:** CTR on ticker pages (the number that should move) + the old `/{TICKER}`/`/stocks/` URLs consolidating into `/signals/:ticker`. Memory: `project_seo_ticker_redirect_fix_2026_06_05`.

**Also now resolved:** the prior block's "OWNER ACTION: push `gammarips-webapp` main" is **DONE** — `origin/main` now carries both the V6 reconciliation (`b9032aca`) and the SEO fix (`ce9db742`); both auto-deployed and live. (Still OPEN from that block: `cd x-poster && bash deploy.sh` to pick up the shared `voice_rules.py` fix.)

---

**▶ 2026-06-05 (later) — WEBAPP + BLOG RECONCILED TO V6. Webapp PUSHED + live (origin/main `b9032aca`); blog-generator deployed; 3 stale blog posts archived, 3 regenerated.**

The "TOMORROW'S JOB" below (bring the public SITE to V6) is **DONE** this session. Summary:

- **Webapp (`/home/user/gammarips-webapp`, branch `main`, NOW 2 commits ahead of origin — NOT pushed; owner pushes):** commit `b9032aca`, 19 files. The big stale narrative (5-model Agent Arena debate / Scorer→Picker / V5.4 gate stack / "deterministic selection") is replaced with V6 reality. **The highest-priority empty-state banner is fixed** (`todays-pick-card.tsx`: no-pick copy → empty-pool / safety-rail / fail-closed; dropped 5–13% OTM + OI/vol floors; gate-pass badges → 3-bracket consensus badge via new `v5_4_confidence` field). **methodology + how-it-works** rewritten: enrichment bar + 2 safety rails + a new tournament section, and the now-false "deterministic / no-LLM-in-selection" spine reframed (selection = leakage-checked LLM tournament; only execution is fixed code). Arena retired honestly + dead `arena-client.tsx` deleted + `/arena` dropped from sitemap. V5.4→V6 across faq/about/disclosures/scorecard/reports/developers/signals/pricing/home/auth-dialog/mailgun (+ go-live date → 2026-06-04). `tsc`: **zero new errors** (28 pre-existing, untouched). **→ OWNER ACTION: push `gammarips-webapp` main (auto-deploys).**
- **blog-generator (engine repo):** its BQ filters were already V6, but its **prompt/forbidden-list narrative was two eras stale** (would re-draft V5.4 / Agent Arena / "gate stack" / "9:00 AM" on the Mon 05:00 cron). Reconciled (commit `2b031b0`) + **DEPLOYED rev `blog-generator-00024-xmb`** (`DRY_RUN=false`). The shared `libs/gammarips_content/voice_rules.py` was also de-staled → **x-poster runs the OLD vendored copy until redeployed** (low-risk: a "V5.4 cohort≥30" do-not guardrail, not user copy). **→ OPEN: `cd x-poster && bash deploy.sh` to pick up the shared-lib fix.**
- **Blog posts (Firestore `blog_posts`): final = 9 published (all V6-clean), 3 archived.** Archived (premise-dead under V6; `status='archived'`, reversible, `prev_status` saved): `moneyness-5-15-otm` (moneyness gate gone), `first-30-v53-trades` (V5.3 cohort wiped), `engine-post-mortem-first-30-days` (retro of wiped cohort). Regenerated clean (reviewer 10.0): `systems-problem-not-pick-problem`, `whatsapp-group-tag-the-agent`, `whats-pushed-to-my-phone-at-9am` (slot title fixed 9:00 AM→**7:30 AM ET** in live schedule + `seed_schedule.py` commit `c77b572`; `/9am` slug kept as URL artifact; regen succeeded after 2 flaky rubric retries — writer overshoots length/wraps in ```` ```markdown ```` fences on this recap slot, so future regens of it may need a retry). **→ OPTIONAL: re-topic the 3 archived posts via `seed_schedule.py` once V6 has history.** Archived URLs now 404 + self-drop from sitemap (sitemap reads status-filtered).

---

**▶ 2026-06-05 — ENGINE QUOTE-OUTAGE FIXED + REDEPLOYED; enrichment gate recalibrated (score≥4 floor, ALL directions); option-PnL gate study RESOLVED. LIVE.**

The engine had been producing **0 picks/day since scan_date 2026-06-04** — a silent production stop. **Root cause:** this Polygon plan serves **NO options NBBO quotes** (v3 snapshot returns no `last_quote`; bid/ask always NULL). The 2026-06-04 bug-fix correctly removed `polygon_client`'s fake day-low/high spread synthesis, but `_best_contract` still hard-rejected on `bid<=0 or ask<=0` → None for EVERY ticker → 0 enriched. (The `overnight_score`/webapp 8/10 was UNAFFECTED — pure pre-enrichment flow; only contract *selection* broke.) **Fix (deployed 2026-06-05):** `_best_contract` prices off last-trade/day-close + leaves `spread_pct` NULL (no synthesis); enrichment dropped the `spread IS NOT NULL` fail-closed and raised the score floor `>=1 → >=4` (drops proven-bad score≤3 dregs; floor NOT ceiling — EV inverts at >=7). UOA>$500K + ALL directions kept. **Spread is permanently retired as a gate** on this plan. Decision: `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`.

**Option-PnL gate study RESOLVED (workflow `wf_16b5c00d-347`, N=1375 FILLED, 33 days):** the **only** robust, leakage-clean, breadth-viable lever is **DIRECTION** — bullish-only EV +0.0411 (win 0.470) vs bearish -0.0771. **Owner decision: do NOT bake in bullish-only** — bearish penalty is almost certainly regime-conditional (single war-chop window, vix3m near-zero variance → untestable here). Kept ALL directions; shelved "exclude bearish" to N≥15. 5 new dead-ends recorded (trend overlays, vix3m conditioner, moneyness>5%-keep-null, catalyst exclusion, active-strikes≥10 — see `FINDINGS_LEDGER.md`).

**OPEN FOLLOW-UPS:** (a) **re-validate the direction tilt at N≥15** live closes (bullish-only +0.0411 vs bearish -0.0771; is the bearish penalty regime-conditional?); (b) **consider a Polygon quote-plan upgrade** — the only path to a real spread signal (and the H20 trades-feed sweep classification); spend decision, owner-owned; (c) watch the enriched-pool/`has_contract` size after tonight's scan now that no-quote strikes price off last-trade. Plus the still-open webapp-V6 reconciliation below.

**RESOLVED ARCHITECTURE Q (2026-06-05) — KEEP the night-before scan; do NOT re-architect to a 9:30→10:00 market-open sprint.** Rationale: this is a 3-day-hold positional strategy on PRIOR-day flow → the signal is complete at the prior close and gains nothing from sub-day latency; running at open computes the same yesterday's-flow numbers later with no buffer. The cadence's real value is the ~11h buffer for a slow, LLM-heavy, retry-prone pipeline (scan ~10min + per-candidate Gemini enrichment + 3-bracket tournament) — a 30-min window misses entry on any hiccup. The 10:00 entry is a deliberate "let the open settle" choice, independent of compute timing. The ONLY genuinely-fresher-at-open input is **settled OI** (overnight, prior-day sweep volume settles into OI — the deferred #3/#4 stale-snapshot issue); if pursued, that's a small targeted ~09:00 OI re-fetch feeding enrichment, NOT a pipeline move. Spend engineering on signal quality (direction lever, option-PnL validation), not latency a 3-day hold can't use.

---

**▶ TOMORROW'S JOB (run from `gammarips-engine`, edit the SEPARATE repo `/home/user/gammarips-webapp`): bring the public SITE to the V6 reality.**
The webapp still markets the OLD pipeline. Go through the gammarips-webapp code + Firestore content and reconcile:
- **The big stale narrative:** README + pricing tiers + how-it-works + methodology still describe a *"5-model Agent Arena adversarial debate"* and *Scorer→Picker* — that's two eras out of date. Replace with the **V6 bracket tournament** (3 randomized brackets, batches ≤10, top-2 advance, consensus pick; no memory/rubric/weights). Agent Arena is DEAD; there is no "debate transcript."
- **Gates copy:** the site still implies selection gates. V6 = **no selection gates**; only enrichment (`overnight_score≥4` floor, `UOA>$500K` directional, ALL directions — **spread gate RETIRED 2026-06-05**, this Polygon plan serves no options quotes so there is no spread to gate or display) + two safety rails (no-earnings-in-hold, `VIX≤VIX3M`). (We already fixed the V/OI-gate copy + moneyness numbers earlier this session; this is the deeper ranker-narrative pass.)
- **THE "No trade today" EMPTY-STATE BANNER (owner hit this 2026-06-05 — highest-priority copy fix):** it currently reads *"No signals cleared today's gate stack (5–13% OTM, VIX ≤ VIX3M, no earnings overlap, OI/volume floors)."* — that is **retired V5 copy** describing gates that no longer exist (moneyness band, OI/vol floors). Rewrite to V6 reality: a no-pick day means **either** the enrichment pool was empty (no signal with `score≥4` + `>$500K` directional UOA) **or** a safety rail blocked (earnings in the 3-day hold, or `VIX>VIX3M` backwardation) **or** the tournament fail-closed. Do NOT list moneyness/OI/spread gates — they're gone. Find the string in the webapp repo (likely a hardcoded empty-state component) and in any Firestore-driven copy.
- **Stale BLOG POSTS** in Firestore `blog_posts/*` — many describe old gates / V5.4 / Agent Arena. Audit them; regenerate via `blog-generator` or edit. Also check the FAQ's "deterministic, no judgment" claim (now an LLM tournament).
- **Cohort label** already done: `cohort_stats/current` = `V6_TOURNAMENT`, cohort_start 2026-06-04 (webapp `EMPTY_STATS` default already committed-local in the webapp repo — push it).
- Webapp is Next.js, **auto-deploys on push to `main`** — edit + commit locally, the OWNER pushes (don't push the webapp without confirming).
- Canonical V6 facts to copy from: `docs/TRADING-STRATEGY.md` / `CHEAT-SHEET.md` (both reconciled today).

**Also still open from today:** (a) the `has_contract` rate WATCH below (check after tonight's scan), (b) PIT-data fix for frozen OI/volume (#3/#4), (c) merge `gate-changes-2026-06-02` → master when ready (pushed, not merged).

**LESSON (2026-06-04, owner-stated — bake into how we work):** the pipeline had **silent code/data bugs that "build and work" but corrupt the pick** (fake 0% spreads on ~43% of picks, suppressed divergence signals, lookahead). We'd been eval'ing the **LLM text output** and assuming the surrounding code was fine because it ran. It wasn't. The owner's gut ("it's off") was right. Going forward: **eval the DATA and the CODE paths, not just the model output** — sanity-check field values against reality (the spread 0.5%-vs-35% catch), not just whether it compiles. See `feedback_eval_the_data_not_just_llm_text` memory.

---

**2026-06-04 (late) — PIPELINE BUG-HUNT: 13 silent data bugs fixed + deployed; all living docs reconciled to V6. LIVE.**

An adversarial multi-agent audit (every finding re-verified vs code+BQ) found **16 silent bugs corrupting picks since day one**. 13 fixed (confirm-pass = GO, 0 blockers), 3 deferred. Trigger: the OKTA $127 untradeable-ghost pick. Decision: `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.

**Root cause + key fixes (committed `6b2a6dc`, deployed all 5 services):**
- **#1 CRITICAL** `polygon_client._extract_best_price_fields` substituted day LOW/HIGH for a missing bid/ask → fake/exactly-0% spreads on **~43% of picks** (718/1815 rows = 0.0). Now: missing quote → NULL spread; real otherwise. Enrichment spread gate loosened `0.08→0.30` (was filtering fake 0s). Judge now SEES the real spread (#5 un-blocked it).
- **#2** divergence-flip scoring reordered BEFORE conviction signals (was scoring flipped names on the abandoned side → ~87% of the best setups suppressed below MIN_SCORE).
- **#8** technicals lookahead: window bounded to `scan_date` (was `date.today()`).
- Scanner contract selection now **liquidity-aware** (OI-primary, real spread, no-quote strikes dropped) — picks the $130 not the $127 ghost.
- Judge: stale `volume`/`OI`/`V-OI` stripped from prompt (#5); batch-loss re-queue (#11); real top-5 (#14). Trader: fill-realism (#9/#12/#13). Notifier: dead gates/docs cleaned (#6/#7/#10).

**Deployed:** overnight-scanner-00011-kzh, enrichment-trigger-00042-9n4, signal-judge-00003-rgc, signal-notifier-00039-9ml, forward-paper-trader-00039-qfp.

**WATCH (the one open risk):** #1 ghost-removal could shrink the pool if post-close quotes are sparse. **Tomorrow after the 23:00-ET scan, check the `has_contract` rate vs the ~58% baseline (41,156/71,167).** If it collapses below ~40%, add a point-in-time day-bar VWAP/close fallback (NOT day low/high) — which is ALSO the proper fix for the deferred items.

**DEFERRED (need PIT data / schema):** #3 OI + #4 volume = session-frozen snapshots, walled off from the judge (used only in scanner relative ranking); real fix = Polygon flat files / day-bars per scan_date — **next data task**. #15-full = `under_enriched` flag (schema add). Stats: exclude `illiquid_exit=TRUE`/`STALE_NO_TIMEOUT_PRINT` from the ledger.

**Docs:** all living docs reconciled to V6 (CLAUDE.md, GEMINI.MD, CHEAT-SHEET, TRADING-STRATEGY, ARCHITECTURE, MODELS, GLOSSARY, DATA-CONTRACTS). Historical DECISIONS/EXEC-PLANS left as record.

---

**2026-06-04 session — V6 "TOURNAMENT" LAUNCHED; V5.4 retired + ledger TRUNCATED. LIVE.**

The gated single-judge (V5.4) was a dud — **13 live closes, avg 0.0%**. Replaced it with a **randomized bracket tournament over ALL enriched signals** (no selection gates) and relabeled the cohort V6.

**What's live:**
- `signal-judge` (`tournament_v1`, version 7): 3 brackets × (≤10/call, top-2 advance, 94→20→4→1) → consensus winner (3/3 high, 2/3 med, 1/3 low). Simple prompt + daily report + per-contract JSON. No memory/rubric/weights. Verified live (`/rank` on 94 → MSFT). See `docs/DECISIONS/2026-06-04-bracket-tournament.md`.
- `signal-notifier` (rev `00038-7wx`): candidate query **ungated** (moneyness/OI/vol/DTE/V-OI removed, LIMIT 200, rich feature cols added, active-days gate bypassed). Kept ONLY: no-earnings-in-hold + regime fail-closed. `policy_version='V6_TOURNAMENT'`, `LIVE_COHORT_START_DATE='2026-06-04'`.
- `forward-paper-trader` (rev `00038-fd5`): `POLICY_VERSION='V6_TOURNAMENT'`.
- `forward_paper_ledger` TRUNCATED (13 rows; dumped to `.scratch/v5_4_ledger_final.json`). `cohort_stats/current` refreshed → V6, 0 trades. App is clean of V5.4.
- `gammarips-review` (leakage): SHIP. Committed `deff6cd` (tournament) + this turn's V6 relabel.

**OPEN / NEXT:**
- (a) **Deploy win-tracker / x-poster / blog-generator** — their `policy_version` read-filters were switched to `V6_TOURNAMENT` in code but NOT redeployed. Harmless now (V5.4 truncated, no V6 closes yet) but MUST deploy before the first V6 closed trade surfaces (~3+ trading days out).
- (b) **First live V6 cron** is tomorrow 07:30 ET (full chain untested end-to-end — fails closed if it errors). Watch it.
- (c) **Webapp** `cohort-stats-row.tsx` default → V6 (committed LOCAL in /home/user/gammarips-webapp, NOT pushed). Push when ready.
- (d) **Doc sweep follow-up:** TRADING-STRATEGY.md / GEMINI.MD / MODELS.md / GLOSSARY.md still say "V5.4 / judge_v6 / Scorer-Picker" in many places — CLAUDE.md is updated; the rest is a follow-up rename to V6/tournament.
- (e) The real test: does the V6 cohort make money? Selection is a weak lever (bull EV ~flat); watch realized PnL forward.

---

# Next Session Prompt (prior)

**2026-06-04 session — SCORER→PICKER COLLAPSED into one memory-aware judge (`judge_v6`) + renamed `signal-ranker`→`signal-judge`. SHIPPED: committed `0dd21c8`, `gammarips-review`=SHIP, DEPLOYED (`signal-judge-00001-4kn`, `signal-notifier-00035-bvh` repointed), live `/rank` validated (pick BBWI, version=6 row persisted), old `signal-ranker` service DELETED. Owner waived the G-Stack 30-day-OOS ceremony; leakage audit (the non-negotiable) passed.**

**STATE:** judge_v6 is LIVE. Tomorrow's 07:30 ET cron is the first production judge_v6 pick. Today's live pick (scan 2026-06-03 = BBWI) was LEFT AS-IS — the deployed judge produces the identical pick, so re-triggering would only re-email subscribers a duplicate (no no-send mode). A version=6 validation row exists for scan_date 2026-06-03 (`run_id v5_4_2026-06-03_955a37a8`) alongside the version=5 cron row — harmless, cohort-separable, deletable. **ROLLBACK** (old service deleted): `git revert 0dd21c8` restores the `signal-ranker` dir + 2-stage code → redeploy → repoint `signal-notifier` `SIGNAL_JUDGE_URL`→old `SIGNAL_RANKER_URL`.

**FOLLOW-UPS (none blocking):** docs/MODELS.md still describes the old Scorer/Picker (content rewrite, not a rename — update to single judge); older NEXT_SESSION blocks + historical docs/DECISIONS keep "signal-ranker" as record; eval gaps from the workflow (poisoned-slate mass-leakage fixture, fat-day N>5 anti-anchoring A/B, optional first-class `judge_prompt_version` BQ column). The original V5.5 relabel below remains independent + open.

---

**2026-06-04 (earlier) — pre-deploy notes (superseded by the SHIPPED block above):**

Owner-directed simplification. A multi-agent workflow (16 agents) evaluated the 2-stage ranker: across 13 V5.4-era slates the single judge agreed 9/13 with the logged baseline and was structurally sounder 4-to-1 on the divergences (every divergence was the judge REJECTING a two-label-trap the 2-stage fell into — OKTA→BX, KBR→MCO, EQIX-LEAP→RDDT, CIEN-theta-cliff→GE). The Scorer's top-5 cut was a no-op on ~80% of days (slates ≤5); structural rules were triple-encoded (gates + scorer + picker). Decision: `docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md`.

**What shipped (code, branch `gate-changes-2026-06-02`, NOT committed yet):**
- `signal-judge/prompts/judge_v6.md` — single-call rubric: trusts upstream gates (no re-litigating ITM/earnings/spread), anti-anchoring ("score each candidate as if it were the only one"), absolute leakage discipline + mass-leakage skip, per-candidate verdict array, deterministic composite/tiebreak.
- `app/schemas.py` — `PerCandidateVerdict` + `JudgeOutput` (composite weights 60/25/15 unchanged). `ScorerOutput`/`PickerOutput` kept for typecheck/replay. `RankResponse.scorer_outputs` re-typed.
- `app/agent.py` — removed Scorer fanout + ADK Picker; added `run_judge` (leakage-assert all → ONE structured call → `JUDGE_MAX_ATTEMPTS=3` bounded retry, replacing the lost `MIN_SCORER_SUCCESS_FRAC` partial-failure tolerance); rewired `run_pipeline` (deterministic mass-leakage decision; off-list/poisoned pick fails closed). `root_agent` now a degenerate judge for ADK discovery.
- `app/tools.py` — `persist_run` writes one row per verdict, **mirrors the judge into both scorer/picker REQUIRED columns** (`*_prompt_version=6`, `*_model=gemini-3.1-pro-preview`) → **BQ DDL UNCHANGED**, cohort separable. New `JUDGE_*` constants.
- `deploy.sh` env → `JUDGE_*` (legacy `SCORER_*`/`PICKER_*` retained-but-inert). Case-memory now **load-bearing** (`run_pipeline` fails closed if absent).
- **Wire contract preserved → ZERO signal-notifier changes** (verified: `call_signal_ranker` only guards on `pick`+`confidence`; v5_4_meta fields all present).
- Docs: TRADING-STRATEGY (lines 4 + 47), CLAUDE.md + GEMINI.MD policy line, this file. Live smoke harness at `.scratch/smoke_judge_v6.py` (reads `.scratch/replay_slates.json`).

**OPEN / NEXT:**
- (a) **`gammarips-review` leakage audit** of the diff — DONE, verdict SHIP (serial pre-pass assert, deterministic skip, fail-closed all confirmed).
- (b) Service+dir+code renamed `signal-ranker` → `signal-judge` (2026-06-04). Deploy: `cd signal-judge && bash deploy.sh`. Then live smoke + verify a `signal_ranker_runs` row writes with version=6. **BQ table `signal_ranker_runs` + Firestore `v5_4_*` keys deliberately KEPT (migration/webapp landmines, no payoff).**
- (c) Commit (working tree has the diff; `.scratch/` is untracked — don't commit it).
- (d) The V5.5 relabel below is INDEPENDENT and still open — judge_v6 emits the same provenance fields, so it doesn't conflict.
- Optional follow-ups (from the eval's gaps): poisoned-slate fixture for mass-leakage, fat-day (N>5) anti-anchoring A/B, optional `ALTER` for first-class `judge_prompt_version` column.

Memory: `feedback_dont_gate_owner_innovation`, `feedback_simplicity`, `project_picker_memory_harness`.

---

**2026-06-03 session — PICKER CASE-MEMORY HARNESS built + wired + DEPLOYED + verified live (`signal-ranker` rev `00011-pw9`, `picker_v5`). Owner-directed; owner WAIVED the N≥15/30-day-OOS/DoD ceremony for this (it's advisory/non-gating). Leakage was NOT waived — audited by `gammarips-review` = SHIP-WITH-FIXES, all fixed.**

Owner's idea: give the LLM Picker a *curated, causally-labeled memory* of past option winners/losers ("cleaner than RAG") so it reasons by analogy. Two deep-research workflows (the first over-constrained by my own prompt — it banned post-entry "why" tokens and reduced to a moneyness-CI test, killing the idea; the second, correctly framed, delivered it). **Key reframe that unlocked it:** leakage protects only TODAY's live pick — explaining a CLOSED past trade with full hindsight is allowed and is the whole point.

**What shipped:**
- `scripts/ledger_and_tracking/build_case_memory.py` (read-only) joins `realized_label.pkl` (FILLED option outcome + underlying path) ⨝ `overnight_signals_enriched` (greeks/IV/catalyst/flow) on `(recommended_contract, scan_date)`, overlays the 6 matched live `forward_paper_ledger` closes → emits `signal-ranker/case_memory/{bull.md (846), bear.md (529), exemplars.md (~50 curated, the injection block), case_index.parquet, build_manifest.json}`. `quant.md` (12 priors Q1–Q12) is hand-authored, NOT regenerated.
- **Outcome keyed on `realized_ret>0` (option PnL), NOT `is_win` (stock direction) — they disagree 44.2%.** That "two-label trap" (stock moved your way, option still lost — short-DTE theta cliff) is the central lesson. WHY is **deterministic option physics** (theta drag / delta capture / inferred IV residual), no LLM-authored cause.
- Wired into the Picker the house way: fenced `{case_memory_block}` in `_build_picker_instruction` (agent.py), renderer `tools.render_case_memory_for_picker()` (cached, ~46.7KB), `picker_v5.md` (v4 + §1a "how to use case memory"), `Dockerfile` ships `case_memory/`, `PICKER_PROMPT_VERSION=5`. **NOT ADK MemoryService** (that's session-recall RAG — wrong tool).
- Review fixes: (1) **fail CLOSED** if v5 ships w/o memory (no silent v4 degrade), `RankResponse.case_memory_bytes`; (2) `deploy.sh` preflight assert; (3) decision note `docs/DECISIONS/2026-06-03-picker-case-memory.md` naming the accepted+bounded **same-ticker outcome-import** vector.
- Verified: smoke test `case_memory_bytes=46673` live, clean pick, no guard trip; 25/25 unit tests pass. Picker latency ~39s now (bigger context, fine vs 540s timeout).

**DONE 2026-06-03/04:** docs updated (TRADING-STRATEGY, CHEAT-SHEET, DECISIONS note, this file) + **COMMITTED** `f5bd0df` on branch `gate-changes-2026-06-02` (working tree clean; `uv.lock` + `case_memory/*.parquet` gitignored). Prompt alignment DONE (picker_v5 §1a). **LEDGER DECISION MADE: TAG, do NOT truncate** — keep the 13 V5.4 rows as the pre-memory baseline; new rows get `policy_version='V5_5_CASE_MEMORY'`; webapp filters to V5.5 for a clean public view. (Truncate rejected: would wipe the only live track record + the 6 live case-memory exemplars + the A/B baseline for "did memory help".)

**OPEN / NEXT — V5.5 relabel (NOT started; only the site map below was pulled). Take a step at a time.**
Note: **V5.5 is already LIVE behaviorally** (picker_v5, `signal-ranker` rev `00011-pw9`); this is cohort-LABELING only, not a behavior change.

**(a) WRITE sites — change the emitted tag `'V5_4_AGENT_RANKER'` → `'V5_5_CASE_MEMORY'` for NEW rows:**
- `forward-paper-trader/main.py:66` — `POLICY_VERSION = "V5_4_AGENT_RANKER"` constant (used at 238, 462, 1041). **Single constant — change here.**
- `signal-notifier/main.py:430, 471, 1220, 1327` — literal `"policy_version": "V5_4_AGENT_RANKER"` writes (todays_pick + ledger). Consider hoisting to a module constant while here.

**(b) READ-FILTER sites — CRITICAL coupling. These filter `policy_version = "V5_4_AGENT_RANKER"`; if left as-is they will MISS the new V5.5 rows:**
- `signal-notifier/main.py:1198, 1291` — feed the picker's 14d ledger summary / stats. **Recommend: filter to BOTH `IN ('V5_4_AGENT_RANKER','V5_5_CASE_MEMORY')`** so the rolling 14d window + track record stay continuous across the relabel (the column still segments cohorts for analysis). The summary builder at 918-949 GROUPs BY policy_version (no filter) — already fine, will show both split out.
- Downstream consumers that filter V5_4 and would silently drop V5.5 — **decide per surface**: `win-tracker/main.py:165`, `blog-generator/app/tools.py:217,674,741,1189`, `x-poster/app/tools.py:173,439`. For public-facing stats (x-poster/blog/webapp) owner wants a clean **V5.5** view → those can filter V5_5-only OR both; pick deliberately. win-tracker = performance tracking → both.

**(c) Deploy + review:** relabel touches `forward-paper-trader` (rule: ALWAYS `gammarips-review` before deploy) + `signal-notifier` (+ optionally win-tracker/blog/x-poster). Sequence: edit → `gammarips-review` → deploy the touched services. No trader-mechanics change (label only).

**(d) Webapp** — separate repo `/home/user/gammarips-webapp` (Next.js, auto-deploys). Show "V5.5" label + filter public stats to the V5.5 cohort. Do AFTER engine side. It reads `todays_pick` (has `v5_4_*` provenance fields — note the field-name prefix is `v5_4_*` even post-relabel unless we also rename those, which the webapp reads — check before renaming Firestore keys).

**Optional later:** flash-narrative prose pass over the deterministic case WHY (A/B for readability); Phase-2 graph from `case_index.parquet`.

**Housekeeping:** smoke test wrote one stray audit row to `signal_ranker_runs` (`run_id v5_4_2026-05-28_eaaa64c9`) — harmless, deletable.

Memory: `project_picker_memory_harness`, `feedback_dont_gate_owner_innovation`.

---

**2026-06-02 session — THREE signal-quality changes SHIPPED to `signal-notifier` + deep-research triage. Owner-directed; overrode the N≥15 lock for gate-*removals/selection* (NOT trader mechanics).** Operator was frustrated with a thin picker slate (~2 candidates/day) and weak picks (CIEN BEARISH entered 05-29, underlying +8%). Goal: *more good options for the picker.*

**NEW: first leak-free realized-option-PnL backtest infrastructure (reusable, the new arbiter).** Backfilled full 3-day option **minute** bars for all labeled candidates from live Polygon (`backtesting_and_research/fetch_hold_window_bars.py`; the cache previously held only entry-day bars, which had made an earlier replay 99% day-1 truncations), replayed the exact +80/−60/trail bracket → `realized_label.pkl` (**1,375 fills**). Analysis scripts: `realized_option_label.py`, `gate_recall.py`, `gate_validity_checks.py`, `moneyness_band_study.py`, `exit_design_study.py`. **Lesson reinforced all session: literature/AI is for framing; our realized option bars are the arbiter.**

**SHIPPED to `signal-notifier` (rev `00028-pm7`), all live for the 2026-06-02+ 07:30 cron:**
1. **`V/OI > 2` gate REMOVED.** Realized PnL: dropped ~55–63% of real winners for precision lift statistically ≤ 0 (90% CI [−0.061,−0.001]); not fillability-confounded (gap +0.057); stable across chrono halves. Folklore conviction gate. `gammarips-review` = SAFE. Decision: `docs/DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md`.
2. **STRICT `ORDER BY` re-ranked** from directional-V/OI-DESC → `overnight_score DESC, recommended_oi DESC, spread ASC, ticker` (now identical to FALLBACK). V/OI is a poor *filter* and a poor *ranker*; supersedes the 2026-05-01 V/OI-DESC primary.
3. **Moneyness cap WIDENED `0.10 → 0.13`** (STRICT only; **`FALLBACK_MONEYNESS_MAX` decoupled + pinned at 0.10** — was `= MONEYNESS_MAX`, a real footgun). Realized PnL: 10-13% increment +8.9% (90% CI [+.014,+.163]); current 5-10% band was breakeven; (0.14,0.15] bin toxic (−15%, excluded → cap at 0.13 not 0.15). **Mechanism correction, NOT a literature reversal:** the H12 deep-OTM-cliff lit (Aretz/Augustin) is HOLD-TO-EXPIRY; our 3-day bracket on UOA flow isn't that trade. `gammarips-review` = SAFE (correctness). Decision: `docs/DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md`. Floor unchanged (0.05). **Thin evidence (N=87, one regime), can't cost-validate in paper — reversible, monitor closely.**

Every tradeability gate kept (OI≥10, vol≥50, DTE 7-45, regime, earnings, active-days). **No trader-mechanics change.** Also re-ran the notifier once for scan 06-01 (no real subscribers) → DINO BULLISH (same pick; 06-01 wasn't V/OI-bound — slate was 123→5 via SQL gates → 2 via downstream Python gates).

**Deep-research (external Gemini Deep Research) triaged against our data → `INTELLIGENCE_BRIEF.md` H18–H21:**
- **H18 (kill the −60% premium stop — the report's #1 lever, = our old H13): TESTED → FALSIFIED.** `exit_design_study.py`: removing the hard stop = paired mean delta **−0.001** (CI [−0.004,+0.003]), zero EV change, just fatter left tail (−0.60 → −0.97). The "wick-out" is a HTE artifact — over 3 days the option is down 60% only when the underlying genuinely failed. **Keep the −60% stop.** Trail earns its keep (TARGET_ONLY −0.012 worse). TIME_ONLY higher *mean* but right-tail mirage (lower median/win%, fatter losers). Memory: `project_exit_design_backtest`.
- **H19 (restrict DTE 7-45 → 21-45): untested** — would shrink the slate; stratify our PnL before adopting.
- **H20 (sweep/ISO detection): PARKED — blocked on data tier.** Taxonomy exists (Polygon id 219 ISO, 228/230 single-leg ISO, 232-247 multi-leg) but `/v3/trades` returns **403 on our Polygon plan**. Needs an Options-Advanced (trades-feed) upgrade — spend + vendor decision. **Defer until EV proven at N≥15–30**; highest-value future signal-quality lever. Probe: `backtesting_and_research/probe_sweep_feasibility.py`.
- **H21 (exit by Day-2 if stalled): untested.**
- **REJECTED:** "VOI > 1.25 predictive" (contradicts our measured V/OI null); "anchor moneyness to 5%" (contradicts our 10-13% data; same HTE lottery argument we discounted).

**Monitoring the new changes (no tag fields added — measure by JOIN):** slate size should climb; INVALID_LIQUIDITY rate should hold (fillability gates kept); the 10-13% moneyness cohort = `forward_paper_ledger` rows `scan_date ≥ 2026-06-02` ⨝ `overnight_signals_enriched` on (ticker, scan_date) WHERE `moneyness_pct` ∈ (0.10, 0.13]. **All three changes are one-line reverts** (`MONEYNESS_MAX`→0.10; re-add 2 V/OI lines; restore old ORDER BY). Memories: `project_option_pnl_relabel_blocked`, `project_moneyness_band_study`, `project_exit_design_backtest`.

**⚠️ Not committed to git.** This session's working-tree changes (`signal-notifier/main.py`, `CLAUDE.md`, `CHEAT-SHEET.md`, `docs/TRADING-STRATEGY.md`, `docs/research_reports/INTELLIGENCE_BRIEF.md`, two new `docs/DECISIONS/2026-06-02-*.md`, and `backtesting_and_research/*.py` + `realized_label.pkl`) were **deployed but NOT committed** — same pattern as prior sessions. Commit when convenient (branch off `master`).

---

**2026-06-01 (later session) — Per-signal SEO metadata SHIPPED; organic-content gap identified.** Ran `gammarips-seo` to find organic-click opportunities. Key correction: the agent worked blind to the webapp source and assumed weak titles — the **webapp is a SEPARATE repo** (`/home/user/gammarips-webapp`, Next.js, auto-deploys live) and its `/signals` + `/how-it-works` titles are **already optimized** (keyword-rich, canonical, SSR'd ticker table). The ONE real gap: per-ticker pages (`/signals/{ticker}`) read `signal.seoMetadata` from Firestore but nothing populated it → all fell back to thin `"{TICKER} Signal"`. **Fix shipped:** `overnight-report-generator` now generates per-signal SEO via an **isolated** Gemini call (`generate_per_signal_seo`, `SEO_PROMPT_VERSION="signal_seo_v1"`) — separate from the report-markdown call so `report_md`/the V5.4 ranker is byte-for-byte unaffected — with a deterministic per-ticker fallback, writing `seoMetadata` onto the top-10 candidates' `overnight_signals/{report_date}_{ticker}` docs via `.update()` (Stage 5, non-blocking, skip-on-miss). `gammarips-review` = **SHIP**. Deployed `overnight-report-generator 00017-h6c`; verified by force-run on 2026-05-29 (10 docs) and backfilled today 2026-06-01 (10 docs). Going forward the 08:15 ET report cron populates it daily. Memory: `project_webapp_separate_repo_and_seo`.

**Blog/EEAT pipeline FIXED end-to-end (Part A + B shipped).** Foundational content was entirely missing — `blog_posts` empty, no webapp `/blog` route — despite `blog-generator` being "live." **Root cause (Part A):** the Publisher couldn't resolve a slug. The planner embeds `schedule_slot` *nested* in `post_outline` (a JSON string under output_key), but Publisher read top-level `state["schedule_slot"]` (never set) and `outline["slug"]` (wrong nesting) → `slug=""` → `publish_to_firestore("")` returned `error` → endpoint returned **200** (masking it) → nothing written. **Fix:** parse the writer's YAML front matter (authoritative — has slug/title/description/keywords/cta; schedule row lacks `description`) as the primary metadata source + strip it from the stored body; loud-fail on empty slug; `/generate` now returns **500** on `error`/`rejected` so failures surface + Scheduler retries. Deployed `blog-generator 00021-285`; real `/generate` published `blog_posts/why-uoa-is-mostly-noise` (status=published, clean body, 7-min read); schedule now 1 published / **12 pending**. **Part B (webapp `gammarips-webapp` repo):** the Firestore reader was stale — targeted a non-existent `blogPosts` camelCase collection with wrong fields. Reconciled `BlogPost` + `getBlogPostsAdmin`/`getBlogPostAdmin` to the real `blog_posts` schema; built `/blog` (index) + `/blog/[slug]` (Article + BreadcrumbList schema, canonical, OG, ISR 300s); added `/blog` to sitemap. **Blog is LIVE with 12 foundational posts** at gammarips.com/blog (+ `/blog/[slug]`). Drained all pending via `/generate`; all passed the compliance rubric at score 10.0. Three more deploy-time bugs caught by verification + fixed: (1) `blog-generator` slug regression on a post whose front matter wasn't position-0 → added a **deterministic schedule fallback** (`f1beea1`, redeployed `00022-qf9`); (2) doubled `<title>` (`| GammaRips | GammaRips`) — root layout already templates the suffix → dropped it (`a0164c29`); (3) `/blog` index 308-redirected to `/signals` because the `/:ticker([a-zA-Z]{1,5})` catch-all swallowed 4-letter "blog" → excluded it in `next.config.ts` (`89e6293d`). Sitemap includes all post URLs. **One post HELD, not a bug:** `19-per-month-signal-service` is `status=rejected` (compliance rubric hard-fails the retired alias "premium signal", which the writer reintroduced across all 3 revision passes) — leave it; the topic is also stale (founder pricing is $29/mo, not $19), so it needs an editorial/title decision before retry. **Re-run `gammarips-seo` ~90 days out (early Sept 2026), not 30** — at ~10 organic clicks/28d a 30-day delta is noise; the blog needs weeks to crawl+index. The weekly Mon 05:00 cron now publishes reliably going forward (it was silently failing on empty-slug before today). **No trader-mechanics change this thread.**

---

**2026-06-01 session — Daily-cadence fallback SHIPPED + verified; lock-in/Alpaca decisions made (design-only, no trader-mechanics change).** Two threads this session:

**(A) Daily-cadence fallback — DEPLOYED to prod.** Problem: cadence is the bottleneck (~6 trades in ~13 trading days vs ≥10/mo target); the strict conviction funnel empties on too many days even in a rip (scan 2026-05-26 skipped with 24 score-7/8 names in the pool). Fix: when the strict stack leaves **zero** candidates, `signal-notifier` no longer skips — it re-queries with **only conviction gates relaxed** (drops `volume_oi_ratio > 2`; moneyness floor `0.05 → 0.0`) and surfaces the single **best fillable** candidate (`ORDER BY overnight_score DESC, recommended_oi DESC, spread ASC, ticker`). **Every tradeability/literature gate stays** (OI≥10, vol≥50, DTE 7-45, regime VIX≤VIX3M, earnings-overlap, active_days_20d≥5 — all run on the fallback pool). On fallback days the **V5.4 ranker is BYPASSED** (deterministic top row, `confidence=LOW`, email subject `[FALLBACK]`). Strict days unchanged. Tagged `policy_gate=FALLBACK` in `todays_pick` → propagated to `forward_paper_ledger.policy_gate` so fallback EV is separable. Verified on real data: scan 05-26 (was a skip) → surfaces ADBE BEARISH (OI 109, vol 322); scan 05-27 strict → PAAS unchanged. `gammarips-review` verdict **GO**. Deployed: `signal-notifier 00025-xxg`, `forward-paper-trader 00036-8jt` (both booted clean). Decision: [`docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`](docs/DECISIONS/2026-06-01-daily-cadence-fallback.md). **Revisit trigger: N≥10 closed FALLBACK trades** → compare FALLBACK vs STRICT EV (`GROUP BY policy_gate`; treat legacy `ENRICHMENT_ONLY_NO_TRADER_GATE` + `STRICT` as one non-fallback baseline); kill or tighten the fallback if it loses. **NOT a V5.3 fallback** — this is conviction-relaxation within V5.4, not a strategy fallback; does not violate the "no V5.3 fallback" rule.

**(B) Lock-in gains ("issue #2") — DECISION: leave it alone until N≥15.** Operator wanted to lock gains after the PAAS give-back (peaked +31%, timed out flat). Resolved with data: a **ratcheting** trail provably does NOT kill the +80% winners (HTZ ran $0.40→$0.74 and filled the +80% target *on the way up*; a trailing stop only fires on a drop, so it never threatens a trade that reaches target). BUT the current −25%-off-peak trail is too loose to lock much (on PAAS's $3.00 peak it sits at ~break-even), and with only **2 trades** ever reaching the +30% zone you cannot calibrate arm/trail levels. So: **keep clean +80/−60, no trail change now**; revisit the ratchet at N≥15 with a real peak distribution. (A +25% scalp target was rejected earlier — it would have ~halved cohort return by clipping the HTZ tail.)

**(C) Alpaca platform constraints (verified for the eventual agent) — design-only, nothing built.** Alpaca **options** support market / limit / **stop / stop-limit**; they do **NOT** support trailing-stop, bracket, OCO, or OTO (all equity-only). Consequences for the future agent: (1) lock-in must be **agent-coded** (a ratcheting native *stop*, not a trailing-stop order type); (2) **no OCO** → cannot rest the −60% stop AND +80% limit simultaneously on one contract — the agent holds ONE resting protective stop and fires the target via a poll loop. Capital/velocity: Alpaca accounts are **margin/limited-margin by default and float settlement**, so unsettled proceeds recycle immediately (same as Robinhood Instant) — velocity is NOT a blocker (confirm options-proceeds behavior via paper test). Real capital need is **overlap** (daily entry × 3-day hold = ~3 concurrent positions = ~$1.5–2k working capital), inherent to the strategy, not a settlement problem. 3-day holds are NOT day trades, so the $25k PDT floor doesn't bind. The agent ("Gemini Spark" — operator's term; clarify the specific runtime/framework next time) stays **DEFERRED** per the unchanged 3-part go-live trigger (N≥30 + EV≥0 + 15 manual matches). Next step when signal is good: draft the agent exit state-machine spec (poll loop, one-resting-order constraint, target-fire logic) so paper-sim == live-execution. **No code for this thread this session.**

**⚠️ Not committed to git.** This session's working-tree changes (`signal-notifier/main.py`, `forward-paper-trader/main.py`, `docs/TRADING-STRATEGY.md`, new `docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`) were **deployed but NOT committed** — same pattern as prior sessions' uncommitted state. Commit when convenient (branch off `master`).

---

**2026-05-28 session — Gemini model migration SHIPPED + verified.** Migrated every text-generation Gemini call `gemini-3-flash-preview` → `gemini-3.5-flash` across the engine. Voluntary quality upgrade — `profitscout-fida8` calls the old model daily so it keeps access past the 2026-06-15 deprecation regardless (NOT a forced migration). **Deployed + verified on 3.5-flash:** `overnight-report-generator` (00016-txd, trace ok), `gammarips-eval` (00006-t8p, judge logs ok + `config.yaml` bug fixed), `x-poster` (00036-kj6, dry-run APPROVE; DRY_RUN restored false), `enrichment-trigger` (00038-6xf — verified by its live 05:30 ET cron: 79 ok grounded calls on 3.5-flash), `signal-ranker` (00010-bmt — verified via `/rank` smoke: `scorer_model=gemini-3.5-flash`). **Untouched (deliberate):** Picker (`gemini-3.1-pro-preview`), x-poster image model (`gemini-3-pro-image-preview`), VAPO (`gemini-2.5-pro`), agent-arena (dead). **Behavioral:** Scorer `temperature=0.2` dropped (response_schema enforces structure); enrichment sampling knobs incl `seed=42` dropped; report temp dropped; **eval judges keep temp=0.0**. `thinking_level` NOT set — deployed `google-genai==1.22.0` rejects the field (caught live by smoke test, a green build hid it); thinking stays at 3.x server default. **Cohort:** segmented by `v5_4_scorer_model` — the 3 pre-migration closed trades (`gemini-3-flash-preview`) are NOT pooled with new-model trades for the 15/30-trade EV gates. `gammarips-review` PASSED. Decision: [`docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md`](docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md). Model→function registry: [`docs/MODELS.md`](docs/MODELS.md). Committed + pushed (`3fa3cea` on `origin/master`); CLAUDE.md / GEMINI.MD / CHEAT-SHEET synced.

---

**Last session wrapped:** 2026-05-27 (Wednesday) — **diagnostic + decision session, no code shipped.** Answered "why only 3 trades on the app," traced the recurring INVALID_LIQUIDITY no-fills to their root cause, backtested a proposed fix, and **rejected it** on the evidence. Operator decision: accept INVALID_LIQUIDITY as a paper-only artifact and leave liquidity gating untouched. Set the go-forward plan: a **15-closed-trade interim checkpoint** (evals + diagnostic GO/NO-GO) ahead of the unchanged formal real-money DoD. Decision file: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md).

**State at handoff time (2026-05-27):**
- `forward_paper_ledger` — **3 closed/counted trades**: OKTA (scan 05-12, BEARISH, TIMEOUT **−1.96%**), HTZ (scan 05-14, BEARISH, TARGET **+80%**), BBY (scan 05-18, BULLISH, TIMEOUT **+15.28%**). Plus 2 `INVALID_LIQUIDITY` no-fills (KBR 05-13, EQIX 05-20) and 2 `SKIPPED` no-candidate days (05-15, 05-19). App tile: **3 trades / +31.8% ROI / 67% win / $1.5K invested**.
- **In flight (deferred reporting — see below):** BLK (scan 05-21, BULLISH) lands **today 05-27 16:30 ET**; ADI (scan 05-22, BULLISH) lands 05-28; scan 05-26 was a no-pick → writes a SKIPPED row on 05-29. ⚠️ BLK's contract showed "no bars" in the MTM log — it may land as another INVALID_LIQUIDITY.
- **Deferred-reporting mechanic (clarified this session):** the trader is NOT real-time. The 16:30 ET cron processes exactly ONE scan_date = `get_canonical_scan_date()` = **today − 3 trading days** (one cohort per day, **no catch-up loop**). So the ledger always trails real-time by ~3 trading days, and a single missed cron permanently drops that scan_date. The "3 trades" is correct given this lag + heavy gating + the 2 INVALID/2 SKIP days + Memorial Day (05-25).
- Production: `forward-paper-trader` `00035-72h` (unchanged since 2026-05-15). `signal-notifier` `00024-xh7` (active-days gate + fixed-$500 sizing). All services healthy.

**Prior sessions:** 2026-05-27 diagnostic + liquidity decision (this session); 2026-05-19 active-days liquidity gate + fixed-$500 sizing; 2026-05-15 trader resurrection + EOD MTM; 2026-05-12 V5.4 pipeline alignment; 2026-05-09 V5.4 promotion; 2026-05-08 V5.4 spec lock.

**Current policy:** V5.4 Agent Ranker — sole live strategy. Trader mechanics **unchanged** (entry 10:00 ET, −60% stop, +80% target, trail, 3-day hold). Selection changed 2026-06-01 (**daily-cadence fallback**) and 2026-06-02 (**`V/OI>2` removed; `overnight_score`-led ORDER BY; moneyness cap 0.10→0.13 STRICT / 0.10 FALLBACK**) — see top block. Decision lock: [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md) + [`docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`](docs/DECISIONS/2026-06-01-daily-cadence-fallback.md).

---

## TL;DR for the next session

**Default mode is monitor + park.** Code work is paused while the ledger accumulates closed trades. Return triggers:

1. **15-closed-trade interim checkpoint** (operator plan, set 2026-05-27). When `forward_paper_ledger` reaches **15 closed/counted trades** (distinct scan_date with a realized exit — excludes SKIPPED and INVALID_LIQUIDITY), run the **evals + a diagnostic** as a GO/NO-GO health check. Currently **4/15** closed (PAAS + CIEN land 06-01/06-02 → ~6/15 mid-week). At ~1-2 counted trades/week this lands roughly **mid-to-late July 2026**. This is a checkpoint, NOT the real-money gate. **Add to the diagnostic: FALLBACK-vs-STRICT EV split (`GROUP BY policy_gate`) once N≥10 fallback closes, and the trailing-stop ratchet calibration (N≥15).**
2. The 30-trade DoD email (`evan@gammarips.com`, subject `[GammaRips] 30-trade gate reached — return trigger active`).
3. The Phase 4 trigger (N ≥ 10 V5.4 closes) — flip `signal-ranker DRY_RUN=false` so per-row Scorer/Picker provenance lands in `signal_ranker_runs`, then build the IC join in `gammarips-eval`. Close at current pace.
4. The "5 consecutive V5.4 losses with no skipped days" rule (`docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md`).
5. The operator surfacing a specific issue.

**Real-money go-live trigger (UNCHANGED — `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`):** all three must fire, PLUS CLAUDE.md's mandatory 30-day OOS + `gammarips-review` audit. The 15-trade checkpoint above does **not** replace this.
- N ≥ 30 closed V5.4 paper trades
- Cohort EV ≥ 0
- ≥ 15 operator-confirmed manual trades match the picker's signal

Until those fire, the system is paper-only. Founder pricing $29/mo continues as the only commercial surface.

**What to put in the 15-trade diagnostic:** cohort EV + win rate; eval/IC health (once Phase 4 lands provenance); fill rate (INVALID_LIQUIDITY %); **and a review of whether the `active_days_20d >= 5` gate should stay** — this session found it may be net-harmful (it would have rejected HTZ, the +80% winner, and did NOT catch EQIX/BLK). See the liquidity decision doc.

---

## What this session did (2026-05-27) — diagnosis only, NO code shipped

1. **"Why only 3 trades?"** — confirmed correct: deferred 3-trading-day reporting lag + heavy upstream gating + 2 INVALID_LIQUIDITY + 2 SKIPPED + Memorial Day. Not a bug.
2. **INVALID_LIQUIDITY root cause** — the contracts V5.4 picks (5–10% OTM, short-DTE, single-name, UOA-spike) are uniformly thin; `recommended_volume` is the scan-day spike that doesn't persist; entry-day fill is near-random. Verified EQIX/BLK printed zero entry-day bars (genuine, not a fetch bug).
3. **Tested a fix (H15: per-day volume floor on the active-days gate) → REJECTED.** Backtest (`backtesting_and_research/2026-05-27_active_day_volume_floor.py`): any floor that rejects EQIX/BLK also rejects OKTA + BBY (real fills), HTZ fails even the current gate, BLK (most trailing activity) never printed, and floor 5 darkens 42% of days. Quote-based fill model blocked (no Polygon NBBO on our tier).
4. **Decision: accept it.** No gate change. INVALID_LIQUIDITY overstates real-world un-fillability (it fires when no one *else* traded; a real buyer crosses the ask). Decision: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md). Research brief updated (H15 resolved). Memory: `project_invalid_liquidity_root_cause`.

**Uncommitted working-tree state (carried from prior sessions, NOT this session's):** `forward-paper-trader/main.py` + `requirements.txt` + `docs/DATA-CONTRACTS.md` + `docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md` (the 05-15 MTM/trader work) and an `enrichment-trigger/main.py` thesis-prompt tweak. These were deployed-from-working-tree but never committed. This session adds: the liquidity decision doc, the INTELLIGENCE_BRIEF H15 entry, and the backtest script/results.

**Locked decisions (don't relitigate):**
- V5.3 is RETIRED. No fallback. signal-ranker uptime is the SLO.
- `LIVE_COHORT_START_DATE = "2026-05-08"`.
- Trader mechanics: entry 10:00 ET, stop −60% initial, trail +30% gain / 25% off peak, target +80%, 3-day hold, exit 15:50 ET day-3. STOP/TRAIL wins on ambiguous bars.
- Composite weights 60/25/15 flow/regime/narrative. `scorer_v5` + `picker_v4`.
- **INVALID_LIQUIDITY accepted as a paper-only artifact (2026-05-27). Do NOT build another trailing-liquidity gate — tested and dead.**
- **Daily-cadence fallback LIVE (2026-06-01).** Relaxes ONLY conviction gates on strict-skip days; all tradeability gates kept; ranker bypassed; tagged FALLBACK. Revisit at N≥10 fallback closes. Do NOT relitigate or "tidy" it before then. NOT a V5.3 fallback.
- **Lock-in / trailing stop: LEAVE IT ALONE until N≥15 (2026-06-01).** Keep clean +80/−60. A ratcheting trail doesn't kill +80% winners (target fills on the way up) but can't be calibrated on the 2 trades that reached +30%. +25% scalp target REJECTED (halves return by clipping the HTZ tail). Revisit the ratchet at N≥15.
- **`V/OI > 2` gate REMOVED 2026-06-02** (realized-PnL: dropped ~60% of winners, lift ≤0). Do NOT reinstate it. V/OI is retained only as data, not a gate or a ranking key.
- **STRICT `ORDER BY` is `overnight_score`-led 2026-06-02** (supersedes the 2026-05-01 V/OI-DESC primary). Don't revert to V/OI-DESC.
- **Moneyness cap is 0.10→0.13 (STRICT), FALLBACK pinned 0.10, 2026-06-02.** Mechanism-corrected (the deep-OTM cliff lit is hold-to-expiry, not our 3-day bracket). Thin evidence — monitor the 10-13% cohort; revert to 0.10 if it underperforms. Do NOT reverse to 5% on the literature argument alone (our realized PnL beats it).
- **−60% premium stop: KEEP (2026-06-02).** Tested removing it on 1,375 fills → ZERO EV change (delta −0.001), just fatter tails. The "wick-out" critique is a hold-to-expiry artifact. Do NOT drop the stop. (Exit mechanics still locked until N≥15 regardless.)
- **Alpaca options order facts (verified 2026-06-01):** market/limit/stop/stop-limit supported; trailing-stop, bracket, OCO, OTO NOT (equity-only). Lock-in must be agent-coded (ratcheting native stop); no OCO → one resting exit order at a time. Margin/float = velocity preserved; ~$1.5–2k overlap capital; 3-day holds don't trip PDT. Agent ("Gemini Spark") deferred per the 3-part trigger.
- No real-money trading until the three-part go-live trigger fires (see above).
- No new trader-side gates. Ever.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `signal-notifier` | `00028-pm7` | LIVE V5.4-only fail-closed. `active_days_20d >= 5` gate + fixed-$500 sizing. Daily-cadence fallback (2026-06-01). **2026-06-02: `V/OI>2` gate REMOVED; STRICT `ORDER BY` re-ranked to `overnight_score`-led; moneyness cap `0.10→0.13` (STRICT only, FALLBACK pinned 0.10).** Cron `30 7 * * 1-5` ET. Refreshes `cohort_stats/current` per run. |
| `signal-ranker` | `00010-bmt` | Scorer fanout (`gemini-3.5-flash` since 2026-05-27) + Picker (`gemini-3.1-pro-preview`). IAM-only. `DRY_RUN=false` (live; table previously mis-stated `true`). |
| `forward-paper-trader` | `00036-8jt` | Deferred simulator (today − 3 trading days). Two crons + `/mark_to_market`. **Propagates `policy_gate` (STRICT/FALLBACK) from `todays_pick` into the ledger (2026-06-01).** |
| `win-tracker` | `00011-5l9` | 30-trade DoD gate. Cron `30 16 * * 1-5` ET. |
| `x-poster` | `00036-kj6` | LIVE, DRY_RUN=false. 5 schedulers active. Text on `gemini-3.5-flash` (2026-05-27). |
| `enrichment-trigger` | `00038-6xf` | gates: score≥1, spread≤8%, UOA>$500K. Thesis on `gemini-3.5-flash` (2026-05-27). |
| `overnight-report-generator` | `00017-h6c` | writes `daily_reports/{date}`. On `gemini-3.5-flash`. **Stage 5 (2026-06-01): isolated `generate_per_signal_seo` writes per-ticker `seoMetadata` onto `overnight_signals/{date}_{ticker}` for top-10 candidates — non-blocking, never touches `report_md`.** |
| `gammarips-eval` | `00006-t8p` | monitoring-only. Rubric IC hookup is Phase 4. Judge on `gemini-3.5-flash` (2026-05-27). |
| `reddit-poster` | `00004-2qd` | LIVE DRY_RUN=true. Reddit creds not wired. |
| `blog-generator` | `00022-qf9` | LIVE, DRY_RUN=false. **Slug fix (2026-06-01): Publisher resolves slug/title/description/keywords/cta from front matter + deterministic `fetch_next_schedule_slot` fallback; `/generate` 500s on error/rejected. Publishes `blog_posts/{slug}`.** 12 posts published & live at /blog; `19-per-month-signal-service` held (compliance: "premium signal" alias). |
| `gammarips-mcp` | `00027-mcl` | 18 tools. |
| `agent-arena` | DEPRECATED 2026-05-04 | service exists; propose deletion if touched. |
| `webapp` (`gammarips-webapp` repo) | Firebase App Hosting auto-deploys main | LIVE **V6** copy (origin/main `ce9db742`). 2026-06-01: per-ticker `seoMetadata` on `/signals/{ticker}`; `/blog` + `/blog/[slug]` (Article+Breadcrumb, ISR 300s). 2026-06-05: V6 reconciliation (`b9032aca`) pushed+live. **SEO redirect fix (`ce9db742`): `/{TICKER}` + `/stocks/{ticker}` now 308→`/signals/:ticker` (was →`/signals`,`/` — soft-404s); title-doubling killed; dynamic per-ticker meta fallback; 286 ticker pages added to sitemap.** |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `signal-notifier-job` | 07:30 | signal-notifier | V5.4 pick → `todays_pick` + email + WhatsApp + `cohort_stats/current` refresh. |
| `x-poster-signal-0800` | 08:00 | x-poster `/post {signal}` | Path B anchor. |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | |
| `x-poster-watchlist-0905` | 09:05 | x-poster `/post {watchlist}` | |
| `forward-paper-trader-mtm` | 16:15 | forward-paper-trader `/mark_to_market` | EOD snapshot of open V5.4 positions → `forward_paper_ledger_intraday`. |
| `polygon-iv-cache-daily` | 16:30 | forward-paper-trader `/cache_iv` | |
| `forward-paper-trader-trigger` | 16:30 | forward-paper-trader | Closes the trade whose `exit_day = today` (1 row/fire; today − 3 trading days). |
| `track-signal-performance` | 16:30 | win-tracker | 30-trade DoD gate. |
| `x-poster-callback-1645` | 16:45 | x-poster `/post {callback}` | |
| `backfill-signal-performance` | 17:30 | win-tracker backfill | |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | N≥5 guard. |
| `x-poster-report-0830` | Mon 06:30 | x-poster `/post {report}` | |
| `overnight-scanner-trigger` | 23:00 | overnight-scanner | |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly | |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | |
| `content-drafter-weekly-email` | Sun 17:00 | blog-generator `/draft_email` | operator preview |
| `content-blast-mon-0530` | Mon 05:30 | blog-generator `/blast_latest` | auto-blast (kill via `blast_killswitch/<date>`) |
| `weekly-intel-mon-0700` | Mon 07:00 | blog-generator `/weekly_intel` | |
| `content-drafter-weekly-reddit` | Thu 10:00 | blog-generator `/draft_reddit` | manual-copy drafter |

> **Scheduler hardening (2026-05-20):** 19/22 jobs retry 3× with 30–120s backoff. The 2 trader jobs were skipped pending `gammarips-review`. A single DNS hiccup lost scan_date 2026-05-19 — relevant because the trader has no catch-up loop.

## Firestore schemas relevant to monitoring

| Collection | Schema | Writer | Reader |
|---|---|---|---|
| `todays_pick/{date}` | scan_date, decided_at, has_pick, ticker, direction, contract, score, vix3m_at_enrich, vix_now_at_decision, policy_version, v5_4_run_id, v5_4_justification, v5_4_confidence, v5_4_runner_up | signal-notifier (dual-write under scan_date AND entry_day) | webapp, MCP, x-poster, gamma-bot, `/mark_to_market` |
| `cohort_stats/current` | cohort_start, policy_version, as_of, trades_closed, trades_won, win_rate, total_invested_usd, total_pl_usd, roi_pct | signal-notifier (recomputes from `forward_paper_ledger` once per daily cron) | webapp landing tile |
| `daily_reports/{date}` | scan_date, title, headline, content, bullish_count, bearish_count, total_signals, seoMetadata | overnight-report-generator | x-poster report planner, blog-generator newsletter, webapp `/reports/[date]` |
| `x_posts/{date}_{type}` | scan_date, post_type, text, tweet_id, image_url, iterations, error, dry_run, posted_at | x-poster Publisher | callback / win / loss QRT lookup |
| `blog_posts/{slug}` | slug, title, description, markdown, keywords, cta, reviewer_score, iterations, status, reading_time_min, published_at | blog-generator Publisher | webapp `/blog/[slug]`, newsletter |
| `users` | email, displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId | webapp signups | content-drafter `read_email_audience` |
| `park_watchdog/gate_30_alerted` | one-shot flag (created when V5.4 hits 30 closes) | win-tracker | win-tracker (idempotency) |

## BigQuery tables

| Table | Notes |
|---|---|
| `profit_scout.forward_paper_ledger` | One row per scan_date (V5.4-only). ticker/recommended_contract/direction NULLABLE. 16:30 ET cron writes the exit row for scan_date = today − 3 trading days. |
| `profit_scout.forward_paper_ledger_intraday` | Daily EOD MTM snapshots of open V5.4 positions. Partitioned by `snapshot_date`. 16:15 ET cron. Observability only. |
| `profit_scout.overnight_signals_enriched` | Enrichment output (per-ticker). Gate stack applied. |
| `profit_scout.signal_ranker_runs` | Per-row Scorer/Picker provenance. **Empty until Phase 4 trigger flips `DRY_RUN=false`** (N ≥ 10 closes). |
| `profit_scout.signal_performance` | win-tracker output. Drives the 30-trade DoD gate. |
| `profit_scout.polygon_iv_history` | IV cache. Populated daily at 16:30 ET. |

## What's left to do (as of 2026-05-27)

**Priority 1 — passive monitoring (no action unless something breaks):**
1. Watch BLK (lands 05-27 16:30 ET) and ADI (05-28). If a cron fails, check `gcloud run services logs read forward-paper-trader --project=profitscout-fida8 --region=us-central1 --limit=50`. No catch-up loop, so a missed day is lost.

**Priority 2 — Phase 4 (deferred to ~N≥10 closes, close at current pace):**
2. Flip `signal-ranker DRY_RUN=false`. Per-row Scorer/Picker provenance lands in `signal_ranker_runs`.
3. Build the `signal_ranker_runs ⨝ forward_paper_ledger ON (candidate_ticker, scan_date)` IC join in `gammarips-eval`. Spec: `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#phase-4`.

**Priority 3 — 15-closed-trade interim checkpoint (~mid-to-late July):**
4. Run evals + diagnostic GO/NO-GO. Include the `active_days_20d >= 5` gate review (see liquidity decision doc), cohort EV, fill rate, IC health.

**Priority 4 — pending operator-side items (none blocking):**
5. Reddit creds; GA4 + GSC for `/weekly_intel`; email-list consolidation + unsubscribe; propose `agent-arena` deletion if touched.

**Priority 5 — real-money go-live (deferred until full 3-part trigger fires):**
6. When N ≥ 30 closes AND cohort EV ≥ 0 AND ≥ 15 operator-confirmed matches: open the Alpaca-agent conversation per `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` (subject `[GammaRips] 30-trade gate reached — return trigger active`) when V5.4 closed-trade count (DISTINCT scan_date) ≥ 30. Before that, the **15-closed-trade interim checkpoint** is the first scheduled wake-up for an evals + diagnostic pass.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`** — most recent decision; why liquidity gating is parked.
2. **`docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md`** — the gate this session flagged as possibly net-harmful.
3. **`docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md`** — trader fixes + EOD MTM.
4. **`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`** — V5.4 promotion lock.
5. **`docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`** — real-money go-live trigger (unchanged).
6. `docs/TRADING-STRATEGY.md` — canonical V5.4 execution policy.
7. `docs/DATA-CONTRACTS.md` — BQ + Firestore schemas.
8. `CHEAT-SHEET.md` — operator V5.4 routine.

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## DO NOT do

- Do NOT modify V5.4 trader mechanics. Entry 10:00 ET / stop −60% / trail +30% gain / 25% off peak / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- **Do NOT build another trailing-liquidity gate (volume floor, OI floor, day-before-scan, etc.) — tested and rejected 2026-05-27. INVALID_LIQUIDITY is accepted as paper-only.**
- **Do NOT reinstate the `V/OI > 2` gate, revert the `overnight_score`-led ORDER BY, reverse moneyness to 5%, or drop the −60% premium stop** — all decided/tested 2026-06-02 on realized option PnL (see locked decisions).
- **Do NOT buy a Polygon Options-Advanced (trades-feed) upgrade for sweep/ISO detection (H20) before the strategy shows positive EV at N≥15–30.** Taxonomy confirmed, endpoint 403 on our tier, parked — premature spend on an unvalidated strategy we can't forward-validate at this N.
- Do NOT add a V5.3 fallback path to signal-notifier. Fail-closed on signal-ranker *error* is the SLO. (The 2026-06-01 **daily-cadence fallback** is unrelated — it relaxes conviction gates on zero-candidate days and is allowed/live; it is NOT a V5.3 strategy fallback and NOT a ranker-error fallback.)
- Do NOT relitigate or refactor the daily-cadence fallback before N≥10 closed FALLBACK trades. Let it run and collect EV.
- Do NOT change the trailing stop / add a tighter lock-in before N≥15. Decision 2026-06-01: keep +80/−60 clean; the ratchet can't be calibrated on 2 data points and a mis-tuned trail risks the convex tail.
- Do NOT use FMP in forward-paper-trader. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT add NOT NULL constraints back to `ticker / recommended_contract / direction` on `forward_paper_ledger`.
- Do NOT add execution-side logic to `/mark_to_market`. Observability-only.
- Do NOT treat the 15-trade interim checkpoint as the real-money gate — the full 3-part DoD + 30-day OOS + gammarips-review still applies.
- Do NOT start real-money trading until all three triggers fire.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27.
- Do NOT add a customer-facing chat agent in V1. Bot is sandboxed to `gammarips-mcp`.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record.
- Do NOT add MCP tools without `safe_error` / `clamp` / schema whitelist.
- Do NOT re-add editorial images to x-poster. Text-only.
- Do NOT add the `⚠️ Paper-trade. Not advice.` disclaimer to watchlist/signal/standby/teaser/report posts. Only on realized-P&L recap posts.
- Do NOT name a new ADK service endpoint `/run`. Use `/post`, `/generate`, `/draft_*`, etc.
- Do NOT run any seed/migration script without `PROJECT_ID=profitscout-fida8` prefix.
- Do NOT deploy a new Cloud Run service with a custom service account unless there's a hard isolation requirement.
- Do NOT post the V5.4 paid daily pick on X. Watchlist posts must EXCLUDE the official pick.
- Do NOT broadcast the V5.4 contract on X SIGNAL posts. Path B is anchor-only.
- Do NOT write Reddit posts longer than ~250 chars.
- Do NOT include a multi-row "trades that closed" table in the newsletter — featured-trade-only design (locked 4/30).
- Do NOT flip signal-ranker `DRY_RUN=false` before Phase 4 IC hookup is built.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier / signal-ranker deploys.**

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest additions:
- **2026-06-02** `project_option_pnl_relabel_blocked.md` — built realized-option-PnL label (1,375 fills); V/OI>2 removed (no edge); foundation for all 2026-06-02 changes.
- **2026-06-02** `project_moneyness_band_study.md` — moneyness cap widened 0.10→0.13 (10-13% best bucket); mechanism-corrected (H12 lit is hold-to-expiry).
- **2026-06-02** `project_exit_design_backtest.md` — dropping the −60% premium stop = ZERO EV change; keep it; "wick-out" is a hold-to-expiry artifact. H20 (sweep/ISO) parked on data tier.
- **2026-06-01** `project_daily_cadence_fallback.md` — daily-cadence fallback LIVE; relax conviction, keep tradeability, ranker bypassed, tagged FALLBACK; revisit at N≥10 fallback closes.
- **2026-06-01** `project_ledger_written_in_arrears.md` — `forward_paper_ledger` rows appear only at day-3 exit (~16:30 ET); emitted/emailed in-flight signals look "missing" but aren't — don't misread an empty ledger.
- **2026-05-27** `project_invalid_liquidity_root_cause.md` — INVALID_LIQUIDITY is a thin-contract artifact; trailing-liquidity gating tested and rejected; accepted as paper-only.
- **2026-05-20** `project_first_v5_4_win_and_callback_2026_05_20.md` — HTZ +80% win + callback loop verified.
- **2026-05-20** `project_scheduler_retry_hardening_2026_05_20.md` — 19/22 jobs retry; trader jobs pending review; no catch-up loop.
- **2026-05-15** `project_v5_4_trader_observability_2026_05_15.md` — trader resurrection + EOD MTM.
- **2026-05-12** `project_v5_4_funnel_starvation.md` — picker is starved post-gates; revisit at N ≥ 15.

---

*End of handoff (2026-06-01). The engine is rolling: **4 closed trades** (OKTA, HTZ +80%, BBY, ADI) + **PAAS lands 06-01, CIEN lands 06-02** on the natural 3-day-lag cadence → ~6 closed by mid-week. This session shipped the **daily-cadence fallback** (surfaces a trade on strict-skip days, tagged FALLBACK) and **decided to leave the lock-in/trail alone until N≥15**. Alpaca platform constraints are documented for the eventual (deferred) agent. **Default mode is monitor + park — let trades build, evaluate ROI at the N≥10 (fallback EV) / N≥15 (checkpoint + trail calibration) / N≥30 (go-live) milestones.** Next scheduled wake-up: the 15-closed-trade interim checkpoint, or earlier if a cron breaks, Phase 4 (N≥10) lands, or the operator surfaces an issue. Working tree is deployed-but-uncommitted.*
