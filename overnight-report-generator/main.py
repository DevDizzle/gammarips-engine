import os
import json
import logging
import math
import time as _time
from datetime import date as _date, datetime, timedelta, timezone
from flask import Flask, request, jsonify
from google.cloud import bigquery, firestore
from google import genai
from google.genai import types

# Prompt version stamped on every report doc + trace log so downstream eval /
# cohort attribution can pivot on it. Bump when prompt or payload contract
# changes materially. v1 = original GammaMolt prose. v2 = literature-grounded:
# pre-computed sector concentration, 14d sentiment shift (Tetlock), divergence
# flags, change-vs-yesterday diff (Lazy Prices), forced per-candidate binary
# directional calls (Lopez-Lira), structured theme tags (Bybee), seoMetadata.
PROMPT_VERSION = "report_v2.1"

# Independent version label for the per-signal SEO call (writes seoMetadata onto
# the public /signals/{ticker} pages). Deliberately ISOLATED from PROMPT_VERSION:
# the SEO call never touches the report markdown the V5.4 ranker reads, so its
# prompt can evolve without re-cohorting the trading-relevant report eval.
SEO_PROMPT_VERSION = "signal_seo_v1"

try:
    from trace_logger import TraceLogger, TraceRecord
    _trace_logger = TraceLogger()
except Exception:
    _trace_logger = None
    TraceRecord = None  # type: ignore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PROJECT_ID = os.environ.get("PROJECT_ID", "profitscout-fida8")
DATASET = os.environ.get("DATASET", "profit_scout")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip() or None

try:
    bq_client = bigquery.Client(project=PROJECT_ID)
    db = firestore.Client(project=PROJECT_ID)
except Exception as e:
    logger.error(f"Failed to initialize GCP clients: {e}")

# Use Vertex AI backend for google-genai
try:
    ai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI client: {e}")
    ai_client = None

def _validate_iso_date(s: str) -> str:
    """Validate that s is a YYYY-MM-DD string. Raises ValueError otherwise.
    Boundary check: dates from request JSON flow into BQ SQL via f-string
    interpolation; reject anything that isn't an ISO date before it gets there."""
    parsed = datetime.strptime(s, "%Y-%m-%d")
    return parsed.strftime("%Y-%m-%d")


def get_report_dates(req_data):
    if "report_date" in req_data:
        report_date = _validate_iso_date(req_data["report_date"])
        underlying_scan_date = req_data.get("underlying_scan_date")
        if underlying_scan_date:
            underlying_scan_date = _validate_iso_date(underlying_scan_date)
        else:
            rd = datetime.strptime(report_date, "%Y-%m-%d")
            days_to_subtract = 3 if rd.weekday() == 0 else 1
            underlying_scan_date = (rd - timedelta(days=days_to_subtract)).strftime("%Y-%m-%d")
    else:
        now = datetime.now()
        report_date = now.strftime("%Y-%m-%d")
        days_to_subtract = 3 if now.weekday() == 0 else 1
        underlying_scan_date = (now - timedelta(days=days_to_subtract)).strftime("%Y-%m-%d")
    return report_date, underlying_scan_date

def fetch_signals(underlying_scan_date):
    # Sector lives on the pre-enrichment table; LEFT JOIN keeps the report
    # robust if a row is missing from overnight_signals.
    query = f"""
        SELECT
            e.ticker, e.direction, e.key_headline, e.thesis, e.news_summary,
            e.overnight_score, e.is_premium_signal, e.recommended_contract,
            e.recommended_strike,
            CAST(e.recommended_expiration AS STRING) AS recommended_expiration,
            e.premium_high_rr, e.premium_high_atr, e.recommended_spread_pct,
            e.recommended_mid_price,
            e.catalyst_type, e.flow_intent,
            e.premium_bull_flow, e.premium_bear_flow, e.premium_hedge,
            e.move_overdone, e.mean_reversion_risk,
            COALESCE(s.sector, 'Unknown') AS sector
        FROM `{PROJECT_ID}.{DATASET}.overnight_signals_enriched` e
        LEFT JOIN `{PROJECT_ID}.{DATASET}.overnight_signals` s
          ON e.ticker = s.ticker AND e.scan_date = s.scan_date
        WHERE e.scan_date = '{underlying_scan_date}'
    """
    logger.info(f"Running query: {query}")
    query_job = bq_client.query(query)
    results = query_job.result()
    signals = [dict(row) for row in results]
    return signals


def fetch_baseline_split(underlying_scan_date: str, lookback_days: int = 14):
    """14-day trailing baseline of bullish-share-of-signals.

    Tetlock 2007: tone level (here, bullish share) carries a 1-5 day signal that
    mean-reverts. Lazy Prices (Cohen et al. 2020): the *fact of change* — today
    vs trailing window — is itself an information signal. We compute today's
    bullish share, the trailing mean and std, and a z-score so the LLM (and
    Picker) can see the shift in absolute units, not vibes.
    """
    query = f"""
        SELECT
            scan_date,
            COUNTIF(direction = 'BULLISH') AS n_bull,
            COUNTIF(direction = 'BEARISH') AS n_bear,
            COUNT(*) AS n_total
        FROM `{PROJECT_ID}.{DATASET}.overnight_signals_enriched`
        WHERE scan_date < '{underlying_scan_date}'
          AND scan_date >= DATE_SUB(DATE '{underlying_scan_date}', INTERVAL {lookback_days * 2} DAY)
        GROUP BY scan_date
        ORDER BY scan_date DESC
        LIMIT {lookback_days}
    """
    rows = list(bq_client.query(query).result())
    if not rows:
        return None
    bull_shares = []
    for r in rows:
        n_total = r["n_total"] or 0
        if n_total == 0:
            continue
        bull_shares.append((r["n_bull"] or 0) / n_total)
    if len(bull_shares) < 3:
        return None
    mean = sum(bull_shares) / len(bull_shares)
    var = sum((x - mean) ** 2 for x in bull_shares) / max(len(bull_shares) - 1, 1)
    std = math.sqrt(var)
    return {"baseline_bull_share": mean, "baseline_std": std, "n_days": len(bull_shares)}


def fetch_recent_titles(report_date: str, n: int = 3):
    """Pull the last `n` distinct prior daily_reports titles to feed back into
    the prompt as an anti-repetition signal. Walks back up to 14 calendar days
    to skip weekends/holidays. Dedupes the dual-write twins (entry-day +
    underlying-scan-date docs share a title) by collecting unique titles in
    walk-back order. Returns a list[str], possibly empty."""
    titles: list[str] = []
    seen: set[str] = set()
    try:
        rd = datetime.strptime(report_date, "%Y-%m-%d")
        for back in range(1, 15):
            if len(titles) >= n:
                break
            prior = (rd - timedelta(days=back)).strftime("%Y-%m-%d")
            doc = db.collection("daily_reports").document(prior).get()
            if not doc.exists:
                continue
            data = doc.to_dict() or {}
            t = (data.get("title") or "").strip()
            if not t or t in seen:
                continue
            seen.add(t)
            titles.append(t)
    except Exception as e:
        logger.warning(f"recent-titles lookup failed: {e}")
    return titles


def fetch_yesterday_top_tickers(report_date: str):
    """Read prior trading day's daily_reports doc to compute Lazy-Prices set diff
    on top tickers. Returns the set of bullish + bearish top tickers from the
    most recent prior v2-format report doc, or None if none exists.

    A "prior doc" only counts if it has the v2 ticker-list fields; v1 docs are
    skipped (they lack `top_bullish_tickers`/`top_bearish_tickers`), so the
    first v2 run after a v1 run correctly reports "no prior report" rather
    than fabricating an empty diff. Self-heals after two consecutive v2 runs.
    """
    try:
        rd = datetime.strptime(report_date, "%Y-%m-%d")
        # Walk back up to 5 calendar days to skip weekends / holidays.
        for back in range(1, 6):
            prior = (rd - timedelta(days=back)).strftime("%Y-%m-%d")
            doc = db.collection("daily_reports").document(prior).get()
            if not doc.exists:
                continue
            data = doc.to_dict() or {}
            if "top_bullish_tickers" not in data and "top_bearish_tickers" not in data:
                # v1 doc — has no ticker lists to diff against. Skip back further.
                continue
            prior_top = set()
            for ticker_list_field in ("top_bullish_tickers", "top_bearish_tickers"):
                prior_top.update(data.get(ticker_list_field, []) or [])
            return {"prior_report_date": prior, "tickers": prior_top}
    except Exception as e:
        logger.warning(f"yesterday lookup failed: {e}")
    return None


def compute_sector_concentration(top_signals):
    """Top sectors among top candidates. Returns [] when sector data is
    missing upstream — the scanner has been writing NULL sector since at least
    2026-04-01, so the prompt is instructed to skip this section when empty
    rather than fabricate sectors. Self-heals if upstream is fixed."""
    counts: dict[str, int] = {}
    for s in top_signals:
        sec = s.get("sector")
        if not sec or sec == "Unknown":
            continue
        counts[sec] = counts.get(sec, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [{"sector": sec, "count": n} for sec, n in ranked]


def compute_themes(signals):
    """Bybee-style theme tags from catalyst_type. Aggregated across the full
    enriched candidate set, not just top-N, to capture the day's regime."""
    counts: dict[str, int] = {}
    for s in signals:
        ct = s.get("catalyst_type") or "Uncategorized"
        counts[ct] = counts.get(ct, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [{"catalyst": ct, "count": n} for ct, n in ranked[:5]]


def compute_divergences(signals):
    """Deterministic divergence flags. The Picker reads these to override
    naive 'flow says BULLISH so bullish trade is fine' reasoning.

    Four flag types:
    - flow_direction_mismatch: trade direction disagrees with the flow polarity
      classification (premium_bull_flow / premium_bear_flow).
    - hedge_flow: premium_hedge=True — flow looks like institutional hedging,
      not directional conviction.
    - move_overdone: trade direction is BULLISH/BEARISH but underlying has
      already exhausted the move per the scanner's exhaustion flag.
    - mean_reversion_risk_high: mean_reversion_risk >= 0.5 — empirical
      threshold (avg 0.16, max 0.82 over 2026-04+ data).
    """
    out = []
    for s in signals:
        ticker = s.get("ticker")
        direction = s.get("direction")
        flags = []
        if direction == "BULLISH" and s.get("premium_bear_flow"):
            flags.append("flow_direction_mismatch: bullish trade with bearish premium flow")
        if direction == "BEARISH" and s.get("premium_bull_flow"):
            flags.append("flow_direction_mismatch: bearish trade with bullish premium flow")
        if s.get("premium_hedge"):
            flags.append("hedge_flow: premium pattern reads as institutional hedge, not conviction")
        if s.get("move_overdone"):
            flags.append("move_overdone: underlying exhaustion flagged by scanner")
        mrr = s.get("mean_reversion_risk")
        if mrr is not None and mrr >= 0.5:
            flags.append(f"mean_reversion_risk: {mrr:.2f} (≥0.5 threshold)")
        if flags:
            out.append({"ticker": ticker, "direction": direction, "flags": flags})
    return out

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CandidateCall(BaseModel):
    ticker: str
    direction: str = Field(description='Forced binary call: "BULLISH", "BEARISH", or "UNCLEAR".')
    rationale: str = Field(description='Single sentence explaining the call. Cite a specific load-bearing fact (flow datum, catalyst, divergence flag).')

class SeoMetadata(BaseModel):
    seoTitle: str = Field(description='SEO-optimized page title, ≤60 chars. Include a charged keyword + the date.')
    seoDescription: str = Field(description='SEO meta description, 140-160 chars. Lead with the day\'s thematic bias and the bull/bear split.')
    keywords: List[str] = Field(description='5-8 search-relevant keywords. Mix evergreen ("options flow", "unusual options activity") with day-specific themes.')

class ReportResponse(BaseModel):
    title: str = Field(description='A punchy, thematic title (e.g., "The Tariff Shakeout"). Quotable on X.')
    headline: str = Field(description='A 2-3 sentence summary of the market split and key directional plays.')
    content: str = Field(description='The full markdown body of the report.')
    per_candidate_calls: List[CandidateCall] = Field(description='One forced directional call per top candidate (bull and bear lists combined). Lopez-Lira & Tang 2023 binary forcing.')
    seoMetadata: SeoMetadata = Field(description='Structured metadata for the public webapp /reports/{date} surface (schema.org Article + OG tags).')

class PerSignalSeo(BaseModel):
    ticker: str = Field(description='Ticker symbol, UPPERCASE, must match one of the input candidates.')
    seoTitle: str = Field(description='Evergreen SEO page title for gammarips.com/signals/{ticker}, <=60 chars. Front-load "{TICKER} Unusual Options Flow" then the direction (Bullish/Bearish) and/or catalyst. NO date — these pages rank over time.')
    seoDescription: str = Field(description='Meta description, 140-160 chars. Lead with the ticker + direction + the load-bearing datum (flow, catalyst, or key headline). Plain and specific, no hype.')
    keywords: List[str] = Field(description='5-8 keywords mixing evergreen ("unusual options activity", "options flow") with "{TICKER}" + its catalyst/theme.')

class PerSignalSeoResponse(BaseModel):
    items: List[PerSignalSeo] = Field(description='One SEO block per input candidate ticker.')

def _truncate(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    if len(s) <= n:
        return s
    return s[: n - 3].rstrip() + "..."

def _fallback_signal_seo(sig: dict, report_date: str) -> dict:
    """Deterministic per-ticker SEO metadata. Used as the baseline for every
    candidate and as the safety net when the LLM call fails or returns malformed
    output, so a top-candidate page never silently regresses to the thin
    "{TICKER} Signal" webapp default. Free, deterministic, no LLM dependency."""
    ticker = (sig.get("ticker") or "").upper()
    direction = (sig.get("direction") or "").upper()
    dir_word = "Bullish" if direction == "BULLISH" else "Bearish" if direction == "BEARISH" else ""
    catalyst = (sig.get("catalyst_type") or "").strip()

    title = f"{ticker} Unusual Options Flow"
    if dir_word:
        title = f"{title} — {dir_word} Signal"
    title = _truncate(title, 60)

    thesis = (sig.get("thesis") or "").strip()
    if thesis:
        desc = thesis
    else:
        strike = sig.get("recommended_strike")
        exp = sig.get("recommended_expiration")
        lead = f"{ticker} flagged for unusual options activity with {dir_word.lower() or 'directional'} institutional flow."
        tail = f" Recommended contract: strike {strike}, exp {exp}." if strike else ""
        desc = lead + tail
    desc = _truncate(desc, 160)

    keywords = [ticker, f"{ticker} options", "unusual options activity", "options flow", "institutional options flow"]
    if dir_word:
        keywords.append(f"{ticker} {dir_word.lower()}")
    if catalyst:
        keywords.append(catalyst)
    # de-dupe preserving order, cap at 8
    seen = set()
    keywords = [k for k in keywords if k and not (k in seen or seen.add(k))][:8]

    return {"seoTitle": title, "seoDescription": desc, "keywords": keywords}

def generate_per_signal_seo(candidates: list[dict], report_date: str) -> dict:
    """Per-ticker SEO metadata for the public /signals/{ticker} pages.

    ISOLATED from generate_report_content on purpose: the daily report markdown
    is consumed verbatim by the V5.4 Scorer/Picker as report_md. This call does
    NOT feed the ranker and does NOT touch that text — it only enriches the
    public per-ticker pages. Returns {TICKER: {seoTitle, seoDescription,
    keywords}}. Every ticker starts with deterministic fallback metadata; the
    LLM only UPGRADES entries it returns cleanly, so any failure degrades to the
    deterministic baseline rather than to the thin webapp default."""
    result = {}
    for s in candidates:
        t = (s.get("ticker") or "").upper()
        if t:
            result[t] = _fallback_signal_seo(s, report_date)

    if not ai_client or not result:
        return result

    # Only the SEO-relevant fields. This output never feeds the ranker, so there
    # is no leakage surface — but we still keep the context tight and factual.
    compact = [{
        "ticker": (s.get("ticker") or "").upper(),
        "direction": s.get("direction"),
        "catalyst_type": s.get("catalyst_type"),
        "key_headline": s.get("key_headline"),
        "thesis": s.get("thesis"),
        "recommended_strike": s.get("recommended_strike"),
        "recommended_expiration": str(s.get("recommended_expiration")) if s.get("recommended_expiration") else None,
    } for s in candidates if s.get("ticker")]

    prompt = f"""You write SEO metadata for GammaRips per-ticker pages at
gammarips.com/signals/{{ticker}}. Each page shows ONE stock's overnight unusual
options activity. Generate metadata that wins organic clicks from traders
searching a ticker alongside "unusual options flow" / "options activity".

RULES (do not violate):
- These pages are EVERGREEN — NO date in the title; they accrue rank over time.
- GammaRips is paper-trading / educational. NO performance promises, NO "buy",
  "profit", "guaranteed", or advice language. NO clickbait. Factual flow-structure
  framing only.
- seoTitle: <=60 chars. Front-load "{{TICKER}} Unusual Options Flow", then the
  direction (Bullish/Bearish) and/or the catalyst.
- seoDescription: 140-160 chars. Lead with ticker + direction + the load-bearing
  datum (flow, catalyst, or key headline). Plain and specific.
- keywords: 5-8, mixing evergreen ("unusual options activity", "options flow")
  with "{{TICKER}}" + its catalyst/theme.

Return one item per input candidate, ticker UPPERCASED to match the input.

CANDIDATES:
{json.dumps(compact, indent=2, default=str)}

prompt_version: {SEO_PROMPT_VERSION}
"""

    _t0 = _time.monotonic()
    _model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    try:
        response = ai_client.models.generate_content(
            model=_model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PerSignalSeoResponse,
            ),
        )
        parsed = response.parsed.model_dump() if response.parsed else json.loads(response.text)
        for it in (parsed.get("items") or []):
            t = (it.get("ticker") or "").upper()
            if not t or t not in result:
                continue
            title = _truncate(it.get("seoTitle") or "", 60)
            desc = _truncate(it.get("seoDescription") or "", 160)
            kws = [k for k in (it.get("keywords") or []) if k][:8]
            if title and desc:
                result[t] = {
                    "seoTitle": title,
                    "seoDescription": desc,
                    "keywords": kws or result[t]["keywords"],
                }
        if _trace_logger is not None and TraceRecord is not None:
            try:
                _um = getattr(response, "usage_metadata", None)
                _trace_logger.log(TraceRecord(
                    service="report_generator",
                    call_site="generate_per_signal_seo",
                    run_id=f"signal_seo_{report_date}",
                    scan_date=_date.fromisoformat(report_date) if report_date else _date.today(),
                    model_provider="vertex_gemini",
                    model_id=_model_id,
                    prompt=prompt,
                    response_text=getattr(response, "text", None),
                    response_parsed=parsed,
                    input_tokens=getattr(_um, "prompt_token_count", None) if _um else None,
                    output_tokens=getattr(_um, "candidates_token_count", None) if _um else None,
                    latency_ms=int((_time.monotonic() - _t0) * 1000),
                    status="ok",
                    inputs_raw=f"prompt_version={SEO_PROMPT_VERSION}|signal_seo|{report_date}|{len(compact)}",
                ))
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Per-signal SEO LLM call failed; using deterministic fallback: {e}")
        if _trace_logger is not None and TraceRecord is not None:
            try:
                _trace_logger.log(TraceRecord(
                    service="report_generator",
                    call_site="generate_per_signal_seo",
                    run_id=f"signal_seo_{report_date}",
                    scan_date=_date.fromisoformat(report_date) if report_date else _date.today(),
                    model_provider="vertex_gemini",
                    model_id=_model_id,
                    prompt=prompt,
                    response_text=None,
                    latency_ms=int((_time.monotonic() - _t0) * 1000),
                    status="api_error",
                    error=str(e)[:500],
                ))
            except Exception:
                pass

    return result

def generate_report_content(payload, report_date: str | None = None):
    # Charged-token whitelist (SESTM 2021): these are the institutional-flow
    # phrases the literature finds carry signal. The LLM is instructed to USE
    # them rather than paraphrase to flowery synonyms, which dilutes the
    # sparse signal the Picker is trying to read.
    charged_tokens = (
        "block trade, sweep, rolled up-and-out, rolled down-and-out, "
        "delta-hedged, gamma squeeze, OI build, V/OI spike, premium cluster, "
        "directional UOA, hedging tape, unwind, dealer short gamma"
    )
    prompt = f"""
You are GammaMolt, the AI CEO and quantitative editor for GammaRips. You are
writing the 'Overnight Edge' daily report. The report has DOUBLE DUTY:

1. INTERNAL: it is consumed verbatim by our V5.4 Scorer + Picker LLM ranker as
   `report_md` to corroborate or contradict each candidate's narrative. The
   Picker reads it for regime fit, divergence cross-checks, and theme overlay.
2. PUBLIC: the same markdown is rendered on gammarips.com/reports/{{scan_date}}
   for SEO + human readers, and the title/headline are quoted on X by the
   x-poster service.

Tone: intelligent, market-structure aware, concise but rich. NO hedging
language ("may", "could potentially"). Evidence-led. Quotable.

LITERATURE-GROUNDED CONTENT RULES (do not violate):

- SESTM 2021: use specific institutional-flow vocabulary verbatim — do NOT
  paraphrase. Whitelist of charged tokens to lean on: {charged_tokens}.
  Synonyms ("buyers showed up in size", "bulls pushed through") dilute signal.
- Lopez-Lira & Tang 2023: each top candidate gets a forced binary direction
  (BULLISH / BEARISH / UNCLEAR) with a one-sentence rationale citing a specific
  load-bearing datum (flow, catalyst, or divergence flag). UNCLEAR is allowed
  but only when the divergence flags actively contradict the flow.
- Tetlock 2007 / Lazy Prices 2020: the bullish-share delta vs the 14-day
  baseline is in the payload. Surface it explicitly with the z-score; do NOT
  re-compute or restate it as vibes.
- Bybee et al. 2023: the `themes` list (catalyst_type counts) is the regime
  overlay. Use it for the Key Themes section. Do not invent themes the data
  does not support.

PRE-COMPUTED PAYLOAD (counts and flags here are authoritative — do not
recompute, do not contradict, do not omit):

{json.dumps(payload, indent=2, default=str)}

OUTPUT — produce a single JSON object with these keys:

- "title": punchy thematic title, quotable on X. e.g., "The Tariff Shakeout"
  or "Hedges Outnumber Bets". HARD RULES:
    a) MUST cite or directly evoke one of the catalyst names from the
       structured `themes` list in the payload (e.g. "Sector Rotation",
       "Earnings Beat", "Technical Breakout", "Guidance Raise",
       "Analyst Upgrade", "Macro"). Do NOT invent a theme — in particular
       do NOT default to "AI Infrastructure" / "AI Re-Rating" / "Data Center"
       phrasing unless that exact phrase appears in `themes` or in a top
       candidate's `catalyst_type`. Ticker news prose is not a theme source.
    b) MUST NOT repeat or paraphrase any title in the payload's
       `previous_titles` list. Same anchor noun phrase counts as a repeat
       (e.g. if a previous title was "The Infrastructure Re-Rating", you
       cannot ship "AI Infrastructure Re-Rating", "The Infrastructure Pivot",
       or "Infrastructure Re-Pricing"). Pick a different theme angle.
    c) Tie the title to today's sentiment_shift direction when the z-score
       is outside [-1, 1] — e.g. an outlier_bearish day should read as a
       cooling/de-risking title, not a euphoric one.
- "headline": 2-3 sentence summary leading with the bull/bear split + the
  shift_z direction (today vs trailing 14d), then the dominant theme.
- "content": full markdown body. REQUIRED sections in this order:
    # {{title}} — Overnight Edge, {{report_date}}
    ## Market Pulse
       Total signals + bull/bear split + bullish_share_today and shift_z vs
       baseline (cite the numbers from sentiment_shift in the payload).
    ## Cross-Sectional Concentration
       Top 3 sectors from sector_concentration. Note single-name vs broad. If
       sector_concentration is empty, write a single line: "Sector tags
       unavailable for this scan; concentration check skipped." Do NOT
       fabricate sectors.
    ## Sentiment Shift vs 14-Day Baseline
       One paragraph framing today's bullish share against trailing mean +
       std. Tetlock-shift framing: is today an outlier (|z| > 1) or in band?
    ## Key Themes
       Top 3-5 catalysts from `themes`. Tie to the candidates that carry them.
    ## Top Bullish Signals
       Brief table or bullets, 2-3 sentence color per top_bullish entry. Use
       charged tokens.
    ## Top Bearish Signals
       Same structure for top_bearish.
    ## Per-Candidate Directional Calls
       Render the per_candidate_calls list as a markdown table with columns
       Ticker | Call | Rationale. Calls must match what you also output in
       the structured `per_candidate_calls` field.
    ## Divergence Watch
       For each entry in `divergences`: ticker + flag list + 1-line
       interpretation. If `divergences` is empty, write a single line saying so.
    ## What Changed Since Yesterday
       From change_vs_yesterday: list tickers_added and tickers_dropped vs
       prior_report_date. If no prior report, say so in one line.
    ## Summary / Bias
       2-3 sentences synthesizing the day's bias for the Picker. End with one
       declarative sentence — no hedge language.
- "per_candidate_calls": forced binary direction + rationale per top candidate
  (top_bullish + top_bearish, deduped). UNCLEAR allowed only when divergence
  flags contradict the flow.
- "seoMetadata": seoTitle (≤60 chars, includes a charged keyword + date),
  seoDescription (140-160 chars, leads with bias + split), keywords (5-8
  mixing evergreen + day-specific themes).

CRITICAL FORMATTING:
- Preserve newlines in "content" using explicit `\\n` escaping. Use `\\n\\n`
  between sections. Do NOT collapse to a single line.
- JSON must be strictly formatted and conform to the schema.
- prompt_version for this run is "{PROMPT_VERSION}".
"""
    
    _t0 = _time.monotonic()
    _model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    _scan_date_obj = None
    if report_date:
        try:
            _scan_date_obj = _date.fromisoformat(report_date)
        except Exception:
            _scan_date_obj = _date.today()
    else:
        _scan_date_obj = _date.today()

    try:
        response = ai_client.models.generate_content(
            model=_model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReportResponse,
                # Gemini 3.x migration (2026-05-27): dropped temperature=0.7 —
                # response_schema enforces structure. Thinking left at SDK/server
                # default (explicit thinking_level needs google-genai >= 1.74; pinned 1.22).
            )
        )
    except Exception as e:
        if _trace_logger is not None and TraceRecord is not None:
            try:
                _trace_logger.log(TraceRecord(
                    service="report_generator",
                    call_site="generate_report_content",
                    run_id=f"report_{_scan_date_obj.isoformat()}",
                    scan_date=_scan_date_obj,
                    model_provider="vertex_gemini",
                    model_id=_model_id,
                    prompt=prompt,
                    response_text=None,
                    latency_ms=int((_time.monotonic() - _t0) * 1000),
                    status="api_error",
                    error=str(e)[:500],
                ))
            except Exception:
                pass
        raise

    try:
        if response.parsed:
            parsed = response.parsed.model_dump()
        else:
            parsed = json.loads(response.text)

        # --- Trace log (fire-and-forget) ---
        if _trace_logger is not None and TraceRecord is not None:
            try:
                _um = getattr(response, "usage_metadata", None)
                _in = getattr(_um, "prompt_token_count", None) if _um else None
                _out = getattr(_um, "candidates_token_count", None) if _um else None
                _trace_logger.log(TraceRecord(
                    service="report_generator",
                    call_site="generate_report_content",
                    run_id=f"report_{_scan_date_obj.isoformat()}",
                    scan_date=_scan_date_obj,
                    model_provider="vertex_gemini",
                    model_id=_model_id,
                    prompt=prompt,
                    response_text=getattr(response, "text", None),
                    response_parsed=parsed,
                    input_tokens=_in,
                    output_tokens=_out,
                    latency_ms=int((_time.monotonic() - _t0) * 1000),
                    status="ok",
                    inputs_raw=f"prompt_version={PROMPT_VERSION}|report|{_scan_date_obj.isoformat()}|{payload.get('total_signals', 0)}",
                ))
            except Exception:
                pass

        return parsed
    except Exception as e:
        logger.error(f"Failed to parse JSON response. Raw text: {response.text}")
        if _trace_logger is not None and TraceRecord is not None:
            try:
                _trace_logger.log(TraceRecord(
                    service="report_generator",
                    call_site="generate_report_content",
                    run_id=f"report_{_scan_date_obj.isoformat()}",
                    scan_date=_scan_date_obj,
                    model_provider="vertex_gemini",
                    model_id=_model_id,
                    prompt=prompt,
                    response_text=getattr(response, "text", None),
                    latency_ms=int((_time.monotonic() - _t0) * 1000),
                    status="parse_error",
                    error=str(e)[:500],
                ))
            except Exception:
                pass
        raise e

@app.route("/", methods=["POST", "GET"])
def generate_report():
    if request.method == "GET":
        return "Overnight Report Generator is running", 200

    req_data = request.get_json(silent=True) or {}
    try:
        report_date, underlying_scan_date = get_report_dates(req_data)
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid date in request: {e}"}), 400
    force = req_data.get("force", False)

    # Idempotency check — both keys must exist before we skip, otherwise a
    # partially-written prior run (or a v1 single-key doc) leaves the scan-key
    # mirror missing and signal-notifier reads empty report_md.
    public_exists = db.collection("daily_reports").document(report_date).get().exists
    scan_exists = (
        db.collection("daily_reports").document(underlying_scan_date).get().exists
        if underlying_scan_date and underlying_scan_date != report_date
        else True
    )
    if not force and public_exists and scan_exists:
        return jsonify({"status": "skipped", "message": f"Report for {report_date} already exists at both keys"}), 200

    logger.info(f"Generating report for {report_date} (underlying: {underlying_scan_date})")

    # Stage 1: Data aggregation
    signals = fetch_signals(underlying_scan_date)
    
    if not signals:
        return jsonify({"status": "error", "message": f"No signals found for underlying_scan_date: {underlying_scan_date}"}), 404

    total_signals = len(signals)
    bullish_signals = [s for s in signals if s['direction'] == 'BULLISH']
    bearish_signals = [s for s in signals if s['direction'] == 'BEARISH']
    bullish_count = len(bullish_signals)
    bearish_count = len(bearish_signals)

    # Get top signals by score
    sorted_signals = sorted(signals, key=lambda x: x.get('overnight_score') or 0, reverse=True)
    top_bullish = [s for s in sorted_signals if s['direction'] == 'BULLISH'][:5]
    top_bearish = [s for s in sorted_signals if s['direction'] == 'BEARISH'][:5]
    top_combined = top_bullish + top_bearish
    premium_signals = [s for s in signals if s.get('is_premium_signal')]

    # --- Pre-computed structured fields (literature-grounded; deterministic) ---
    bullish_share_today = bullish_count / total_signals if total_signals else 0.0
    baseline = fetch_baseline_split(underlying_scan_date)
    sentiment_shift = {
        "bullish_share_today": round(bullish_share_today, 4),
        "baseline_bull_share": None,
        "baseline_std": None,
        "shift_z": None,
        "baseline_n_days": None,
        "classification": "no_baseline",
    }
    if baseline:
        std = baseline["baseline_std"] or 0.0
        z = (bullish_share_today - baseline["baseline_bull_share"]) / std if std > 1e-6 else 0.0
        sentiment_shift.update({
            "baseline_bull_share": round(baseline["baseline_bull_share"], 4),
            "baseline_std": round(std, 4),
            "shift_z": round(z, 2),
            "baseline_n_days": baseline["n_days"],
            "classification": (
                "outlier_bullish" if z >= 1.0 else
                "outlier_bearish" if z <= -1.0 else
                "in_band"
            ),
        })

    sector_concentration = compute_sector_concentration(top_combined)
    themes = compute_themes(signals)
    divergences = compute_divergences(top_combined)

    yesterday = fetch_yesterday_top_tickers(report_date)
    today_top_set = {s.get("ticker") for s in top_combined if s.get("ticker")}
    if yesterday:
        change_vs_yesterday = {
            "prior_report_date": yesterday["prior_report_date"],
            "tickers_added": sorted(today_top_set - yesterday["tickers"]),
            "tickers_dropped": sorted(yesterday["tickers"] - today_top_set),
        }
    else:
        change_vs_yesterday = {
            "prior_report_date": None,
            "tickers_added": [],
            "tickers_dropped": [],
        }

    top_bullish_tickers = [s.get("ticker") for s in top_bullish if s.get("ticker")]
    top_bearish_tickers = [s.get("ticker") for s in top_bearish if s.get("ticker")]

    previous_titles = fetch_recent_titles(report_date, n=3)

    payload = {
        "report_date": report_date,
        "underlying_scan_date": underlying_scan_date,
        "prompt_version": PROMPT_VERSION,
        "total_signals": total_signals,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "top_bullish": top_bullish,
        "top_bearish": top_bearish,
        "premium_signals": premium_signals,
        "sentiment_shift": sentiment_shift,
        "sector_concentration": sector_concentration,
        "themes": themes,
        "divergences": divergences,
        "change_vs_yesterday": change_vs_yesterday,
        "previous_titles": previous_titles,
    }

    # Stage 2: Editorial composition
    if not ai_client:
        return jsonify({"status": "error", "message": "Vertex AI Client not configured"}), 500
        
    try:
        generated = generate_report_content(payload, report_date=report_date)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({"status": "error", "message": "Failed to generate content", "details": str(e)}), 500

    # Stage 3: Validation
    title = generated.get("title")
    headline = generated.get("headline")
    content = generated.get("content")

    if not title or not headline or not content:
        return jsonify({"status": "error", "message": "Generated content missing required fields"}), 500

    # Clean up escaped newlines that the model sometimes returns when using JSON schemas
    title = title.replace('\\n', '\n').replace('\\"', '"')
    headline = headline.replace('\\n', '\n').replace('\\"', '"')
    content = content.replace('\\n', '\n').replace('\\"', '"')

    per_candidate_calls = generated.get("per_candidate_calls") or []
    seo_metadata = generated.get("seoMetadata") or {}

    # Stage 4: Firestore publication
    doc_data = {
        # Backwards-compat fields (consumed by signal-ranker, x-poster, webapp)
        "title": title,
        "headline": headline,
        "content": content,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "total_signals": total_signals,
        "scan_date": report_date,
        "underlying_scan_date": underlying_scan_date,
        "published": True,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        # v2 additions
        "prompt_version": PROMPT_VERSION,
        "top_bullish_tickers": top_bullish_tickers,
        "top_bearish_tickers": top_bearish_tickers,
        "sentiment_shift": sentiment_shift,
        "sector_concentration": sector_concentration,
        "themes": themes,
        "divergences": divergences,
        "change_vs_yesterday": change_vs_yesterday,
        "per_candidate_calls": per_candidate_calls,
        "seoMetadata": seo_metadata,
    }

    # Dual-write under both keys. Mirrors the todays_pick dual-write pattern.
    # The webapp + x-poster + blog-generator key off `report_date` (entry day,
    # public-facing). The signal-notifier ranker call at 07:30 ET keys off
    # `underlying_scan_date` (signal-notifier/main.py:556). Without the
    # second write, V5.4 runs with empty report_md and the Picker's
    # regime_alignment leans neutral — the report v2 work would be wasted.
    #
    # The underlying-scan_date doc gets a date-stamped variant: the Scorer
    # enforces scan_date >= all input dates per scorer_v4.md:29, so any
    # entry-day-stamped reference in title/headline/content trips a leakage
    # flag and forces 1/1/1 scores. Stamping the body with underlying_scan_date
    # keeps the contract aligned. The public doc is unchanged.
    underlying_doc_data = {
        **doc_data,
        "scan_date": underlying_scan_date,
        "title": title.replace(report_date, underlying_scan_date),
        "headline": headline.replace(report_date, underlying_scan_date),
        "content": content.replace(report_date, underlying_scan_date),
    }
    try:
        db.collection("daily_reports").document(report_date).set(doc_data)
        if underlying_scan_date and underlying_scan_date != report_date:
            db.collection("daily_reports").document(underlying_scan_date).set(underlying_doc_data)
            logger.info(
                f"Dual-wrote report to daily_reports/{report_date} (entry-day) "
                f"and daily_reports/{underlying_scan_date} (scan_date-stamped)"
            )
        else:
            logger.info(f"Saved report to daily_reports/{report_date} (single key)")
    except Exception as e:
        logger.error(f"Failed to save to Firestore: {e}")
        return jsonify({"status": "error", "message": "Failed to save to Firestore", "details": str(e)}), 500

    # Stage 5: per-signal SEO metadata for the public /signals/{ticker} pages.
    # Runs AFTER the trading-critical report is already persisted, and is fully
    # non-blocking — the report's success does not depend on it. Writes ONLY the
    # seoMetadata field onto the enrichment-written
    # overnight_signals/{report_date}_{ticker} docs via update(); update() no-ops
    # the field-set on an existing doc and raises (caught per-ticker) if the doc
    # is absent, so we never create a partial signal doc that would break the
    # webapp's getSignalByTicker render.
    seo_written = 0
    try:
        seo_map = generate_per_signal_seo(top_combined, report_date)
        for ticker, seo in seo_map.items():
            try:
                db.collection("overnight_signals").document(f"{report_date}_{ticker}").update({
                    "seoMetadata": seo,
                    "seo_prompt_version": SEO_PROMPT_VERSION,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                })
                seo_written += 1
            except Exception as e:
                logger.warning(f"Skipped seoMetadata write for {report_date}_{ticker} (doc absent or update failed): {e}")
        logger.info(f"Wrote per-signal seoMetadata to {seo_written}/{len(seo_map)} overnight_signals docs")
    except Exception as e:
        logger.error(f"Per-signal SEO stage failed (non-blocking, report already saved): {e}")

    return jsonify({
        "status": "success",
        "message": f"Report generated and saved to daily_reports/{report_date}",
        "seo_signals_written": seo_written,
        "report_date": report_date,
        "data": {
            "title": title,
            "headline": headline
        }
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
