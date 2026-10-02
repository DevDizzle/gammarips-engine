"""Daily site stats for gammarips.com (owner call 2026-10-02).

Computes the public pool numbers from BigQuery and writes ONE Firestore doc,
`site_stats/pool`, which the webapp reads (src/lib/receipts.ts keeps a static
fallback). Read-only against BigQuery. Writes nothing else.

Numbers (all on the liquidity-era pool, scan_date >= LIQUIDITY_START):
  * window_3d: share of pool contracts whose premium TOUCHED +X% within the
    3-trading-day opportunity window. Same query as the MCP
    query_outcomes(view="harvest"): opp_status='OK', opp_peak_return not null.
  * to_expiry: the same touch rates over the contract's whole life, for
    contracts that have expired (life_status='OK').
  * quality: median / p10 open interest and median volume of the selected
    contract, after the rule vs the fixed 60 scan days before it.

A touch is not a fill and not profit kept. The webapp writes it as
"hit +50% within 3 trading days" or "hit +50% before expiration".

Decision record: docs/DECISIONS/2026-10-02-web-revamp-positive-first-rules.md.
"""
import logging
from datetime import datetime, timezone

from google.cloud import bigquery, firestore

logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
DATASET = f"{PROJECT_ID}.profit_scout"
LIQUIDITY_START = "2026-08-24"
# The pre-rule baseline is FIXED: the 60 scan days before the rule.
BEFORE_FROM = "2026-05-27"
BEFORE_TO = "2026-08-21"
LEVELS = (0.10, 0.20, 0.25, 0.50, 1.00)

_TOUCH_SQL = f"""
WITH j AS (
  SELECT o.scan_date, o.opp_status, o.opp_peak_return, o.opp_trough_return,
         o.life_status, o.life_peak_return
  FROM `{DATASET}.enriched_features_v1` f
  JOIN `{DATASET}.enriched_option_outcomes` o
    USING (scan_date, ticker, recommended_contract)
  WHERE f.scan_date >= @start
)
SELECT
  -- 3-trading-day window (harvest)
  COUNTIF(opp_status = 'OK' AND opp_peak_return IS NOT NULL) AS n_3d,
  COUNT(DISTINCT IF(opp_status = 'OK' AND opp_peak_return IS NOT NULL, scan_date, NULL)) AS days_3d,
  MIN(IF(opp_status = 'OK' AND opp_peak_return IS NOT NULL, scan_date, NULL)) AS from_3d,
  MAX(IF(opp_status = 'OK' AND opp_peak_return IS NOT NULL, scan_date, NULL)) AS to_3d,
  {", ".join(f"COUNTIF(opp_status = 'OK' AND opp_peak_return >= {x}) AS k3d_{int(x * 100)}" for x in LEVELS)},
  COUNTIF(opp_status = 'OK' AND opp_peak_return IS NOT NULL AND opp_trough_return <= -0.30) AS k3d_stop30,
  APPROX_QUANTILES(IF(opp_status = 'OK', opp_peak_return, NULL), 100)[OFFSET(50)] AS median_peak_3d,
  -- whole life, expired contracts only
  COUNTIF(life_status = 'OK' AND life_peak_return IS NOT NULL) AS n_life,
  MIN(IF(life_status = 'OK' AND life_peak_return IS NOT NULL, scan_date, NULL)) AS from_life,
  MAX(IF(life_status = 'OK' AND life_peak_return IS NOT NULL, scan_date, NULL)) AS to_life,
  {", ".join(f"COUNTIF(life_status = 'OK' AND life_peak_return >= {x}) AS klife_{int(x * 100)}" for x in LEVELS)}
FROM j
"""

_QUALITY_SQL = f"""
SELECT
  IF(scan_date >= @start, 'after', 'before') AS era,
  COUNT(*) AS n,
  COUNT(DISTINCT scan_date) AS days,
  MIN(scan_date) AS first_scan,
  MAX(scan_date) AS last_scan,
  APPROX_QUANTILES(recommended_oi, 100)[OFFSET(50)] AS median_oi,
  APPROX_QUANTILES(recommended_oi, 100)[OFFSET(10)] AS p10_oi,
  APPROX_QUANTILES(recommended_volume, 100)[OFFSET(50)] AS median_volume
FROM `{DATASET}.overnight_signals_enriched`
WHERE direction = 'BULLISH' AND recommended_contract IS NOT NULL
  AND (scan_date >= @start OR scan_date BETWEEN @before_from AND @before_to)
GROUP BY era
"""


def _rate(k, n):
    return round(k / n, 4) if n else None


def compute_site_stats(client=None):
    """Return the stats dict. Raises on a query error or an empty result."""
    client = client or bigquery.Client(project=PROJECT_ID)
    params = [
        bigquery.ScalarQueryParameter("start", "DATE", LIQUIDITY_START),
        bigquery.ScalarQueryParameter("before_from", "DATE", BEFORE_FROM),
        bigquery.ScalarQueryParameter("before_to", "DATE", BEFORE_TO),
    ]
    cfg = bigquery.QueryJobConfig(query_parameters=params)

    t = next(iter(client.query(_TOUCH_SQL, job_config=cfg).result()))
    if not t.n_3d or not t.n_life:
        raise RuntimeError(f"empty touch result: n_3d={t.n_3d} n_life={t.n_life}")

    q = {r.era: r for r in client.query(_QUALITY_SQL, job_config=cfg).result()}
    if "after" not in q or "before" not in q:
        raise RuntimeError(f"quality result missing an era: {sorted(q)}")

    def hits(prefix, n):
        return {f"hit{int(x * 100)}": _rate(getattr(t, f"{prefix}_{int(x * 100)}"), n) for x in LEVELS}

    a, b = q["after"], q["before"]
    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "liquidity_start": LIQUIDITY_START,
        "window_3d": {
            "n": t.n_3d,
            "scan_days": t.days_3d,
            "from": t.from_3d.isoformat(),
            "to": t.to_3d.isoformat(),
            **hits("k3d", t.n_3d),
            "stop_touch30": _rate(t.k3d_stop30, t.n_3d),
            "median_peak": round(float(t.median_peak_3d), 4),
        },
        "to_expiry": {
            "n": t.n_life,
            "from": t.from_life.isoformat(),
            "to": t.to_life.isoformat(),
            **hits("klife", t.n_life),
        },
        "quality": {
            "median_oi": {"after": int(a.median_oi), "before": int(b.median_oi)},
            "median_volume": {"after": int(a.median_volume), "before": int(b.median_volume)},
            "p10_oi": {"after": int(a.p10_oi), "before": int(b.p10_oi)},
            "n_after": a.n,
            "n_before": b.n,
            "after_from": a.first_scan.isoformat(),
            "after_to": a.last_scan.isoformat(),
            "before_from": b.first_scan.isoformat(),
            "before_to": b.last_scan.isoformat(),
        },
    }


def refresh_site_stats(dry_run=False):
    """Compute and (unless dry_run) write site_stats/pool. Returns the dict."""
    stats = compute_site_stats()
    if not dry_run:
        firestore.Client(project=PROJECT_ID).collection("site_stats").document("pool").set(stats)
        logger.info(f"site_stats/pool written: n_3d={stats['window_3d']['n']} "
                    f"n_life={stats['to_expiry']['n']}")
    return stats
