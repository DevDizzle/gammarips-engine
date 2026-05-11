# 2026-05-09 — overnight-report-generator promoted to `report_v2`

## Decision

The `overnight-report-generator` service ships a literature-grounded `report_v2`
prompt + payload. The Firestore doc at `daily_reports/{scan_date}` keeps its
existing top-level fields (`title`, `headline`, `content`, count rollups) for
backwards compatibility with `signal-ranker`, `x-poster`, and the webapp, and
adds:

- `prompt_version: "report_v2"` (also stamped in trace logs via `inputs_raw`)
- `sentiment_shift` (today's bullish share, 14d trailing mean + std, z-score, classification)
- `sector_concentration` (top sectors of the top-10 candidates)
- `themes` (top 5 catalyst_type tags across all enriched signals)
- `divergences` (deterministic flags per top candidate: flow-direction
  mismatch, hedge flow, move-overdone, mean-reversion-risk ≥ 0.5)
- `change_vs_yesterday` (set diff of top tickers vs the prior trading day's
  daily_reports doc)
- `per_candidate_calls` (LLM-generated forced binary BULLISH/BEARISH/UNCLEAR
  + one-sentence rationale per top candidate)
- `seoMetadata` (LLM-generated `seoTitle`, `seoDescription`, `keywords` for the
  webapp `/reports/{date}` schema.org Article + OG tags)

## Why

The report is now load-bearing: the V5.4 Scorer + Picker (`signal-ranker/`)
read the full markdown as `report_md`, the webapp `/reports/{date}` page is
the SEO-critical public surface, and `x-poster` quotes title/headline on @gammarips.
v1 was editorial prose composed from the same `overnight_signals_enriched`
payload the Scorer/Picker already read — circular evidence, no net-new signal
for the ranker, and no SEO metadata for the webapp.

The redesign is grounded in five papers, not vibes:

1. **Tetlock 2007** — pessimism *level* in the WSJ "Abreast of the Market" column
   predicts next-day DJIA returns, mean-reverting within ~5 trading days. We
   surface today's bullish share with a z-score against the trailing 14-day
   baseline so the Picker sees a Tetlock-shift in absolute units.
2. **Ke, Kelly, Xiu 2021 (SESTM)** — sparse sentiment-charged tokens beat
   dense topic prose because most words are noise. The v2 prompt forces the
   LLM to use a whitelist of institutional-flow vocabulary verbatim (block
   trade, sweep, rolled up-and-out, delta-hedged, OI build, V/OI spike,
   hedging tape, dealer short gamma) instead of paraphrasing.
3. **Cohen, Malloy, Nguyen 2020 (Lazy Prices)** — *fact of change* is itself a
   signal; markets under-react when language evolves. The
   `change_vs_yesterday` field is a deterministic set diff of top tickers vs
   the prior trading day's report.
4. **Lopez-Lira & Tang 2023** — forced binary (YES/NO/UNKNOWN) headline
   judgments beat open-ended prose for next-day return prediction, with the
   strongest effect on small caps. v2 adds `per_candidate_calls`: a forced
   BULLISH/BEARISH/UNCLEAR call plus one-sentence rationale per top candidate,
   citing a specific load-bearing datum.
5. **Bybee, Kelly, Manela, Xiu 2023** — supervised topic structure carries
   regime information at monthly horizons. We don't trade off it directly, but
   `themes` (top catalyst_type counts across the day) gives the Picker a
   regime overlay.

Researcher caveat: every cited paper operates at longer horizons than our 3-day
hold and on broad equities, not 5-15% OTM short-dated single-name options.
Direction of the design is supported; effect-size transfer is not measured.

## Counts and flags are pre-computed in Python, not the LLM

`sentiment_shift`, `sector_concentration`, `themes`, `divergences`, and
`change_vs_yesterday` are deterministic. The LLM writes prose *around* these
authoritative values. This prevents a recurrence of the v1 failure mode where
the Gemini call could re-state counts and contradict the structured payload
the Picker also has access to.

## Backwards compatibility

`title`, `headline`, `content`, `bullish_count`, `bearish_count`,
`total_signals`, `scan_date`, `underlying_scan_date`, `published` remain at the
doc root with the same types. All existing consumers continue to work unchanged.
New consumers can pivot on `prompt_version` to detect v2 docs.

## Out of scope (deliberately)

- **No charged-token enforcement** — the whitelist is an instruction in the
  prompt, not a post-hoc validator. If a future eval shows charged-token
  density correlates with picker accuracy, we add a check then.
- **No VAPO run on the v2 prompt** — locking the literature-grounded shape
  first; VAPO is the *next* step after we have ≥30 closed V5.4 trades and a
  fitness signal that distinguishes good vs bad reports.
- **No retroactive backfill of prior reports** — first v2 doc is the next
  scheduled run; older reports stay v1.

## Files

- `overnight-report-generator/main.py` — payload, prompt, Firestore write.
- `docs/DECISIONS/2026-05-09-report-v2-literature-grounded.md` — this note.

## Audit and deploy

`gammarips-review` must audit before deploy. Specific concerns to surface:

1. The 14-day baseline lookback excludes today (`scan_date < '...'`) — confirm no
   look-ahead.
2. Sentence-level prompt-injection from `news_summary` / `thesis` strings
   landing in the Gemini context — same exposure surface as v1; no new vector.
3. The `change_vs_yesterday` Firestore lookup walks back up to 5 calendar days
   — verify it can't read a stale weekend doc as "yesterday."
4. `divergences` thresholds: `mean_reversion_risk >= 0.5` is justified by
   observed avg 0.16 / max 0.82 over 2026-04+ data; no other constants are tuned.
