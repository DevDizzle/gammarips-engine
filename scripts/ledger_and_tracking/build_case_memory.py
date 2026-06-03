#!/usr/bin/env python3
# ruff: noqa
"""Build the picker case-memory library (bull.md / bear.md) from closed trades.

READ-ONLY against BigQuery and the realized-label pickle. Writes only local MD +
provenance artifacts under signal-ranker/case_memory/. Per .claude/rules/scripts-ledger.md
this script NEVER mutates ledger data.

What it does
------------
Joins the option-PnL backfill (realized_label.pkl: option-level outcome + underlying
path) with overnight_signals_enriched (ex-ante greeks / IV / catalyst / flow) on
(recommended_contract, scan_date), overlays the true live closes from
forward_paper_ledger, and emits one forensic CASE per closed trade.

The "WHY" is DETERMINISTIC option physics computed from the data — first-order
decomposition of the realized option return into theta drag, delta capture, and an
inferred IV residual. No LLM authors a cause here (a later narrative pass may render
prose from these blocks; this file is the faithful ground truth).

Outcome is keyed on OPTION PnL (realized_ret > 0 == WON), NOT is_win (did the stock
move our way) — the two disagree ~44% of the time, which is the whole point.

Leakage note: every case is a CLOSED trade explained with hindsight. That is correct
and intended — the library is read later for a *future* contract whose outcome is
unknown. Nothing here is injected into a live decision; wiring is a separate step.

Usage:
    python scripts/ledger_and_tracking/build_case_memory.py
    python scripts/ledger_and_tracking/build_case_memory.py --out signal-ranker/case_memory
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

PROJECT = "profitscout-fida8"
DATASET = "profit_scout"
PICKLE = "backtesting_and_research/realized_label.pkl"
DEFAULT_OUT = "signal-ranker/case_memory"

REGIME_NOTE = (
    "Backtest cases span 2026-04-10 → 2026-06-01 — a single 2026-Q2 war-chop regime "
    "(vix3m ~20-21). Treat distilled PATTERNS as signal and individual case outcomes "
    "as anecdote. Live cases supersede backtest on the same contract."
)

# Columns pulled from the enriched table (ex-ante + greeks).
ENRICHED_COLS = [
    "recommended_contract", "scan_date", "ticker", "direction",
    "recommended_mid_price", "underlying_price",
    "recommended_delta", "recommended_gamma", "recommended_theta", "recommended_vega",
    "recommended_iv", "recommended_dte", "moneyness_pct", "volume_oi_ratio",
    "recommended_oi", "recommended_volume", "recommended_spread_pct",
    "overnight_score", "catalyst_type", "catalyst_score", "key_headline",
    "flow_intent", "rsi_14", "atr_normalized_move", "enriched_at",
]


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def _norm_date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce").dt.strftime("%Y-%m-%d")


def load_backfill() -> pd.DataFrame:
    df = pd.read_pickle(PICKLE)
    df = df[df["realized_ret"].notna()].copy()  # FILLED only
    df["scan_date"] = _norm_date(df["scan_date"])
    df["join_key"] = df["recommended_contract"].astype(str) + "|" + df["scan_date"]
    return df


def load_enriched(client: bigquery.Client) -> pd.DataFrame:
    cols = ", ".join(ENRICHED_COLS)
    sql = f"SELECT {cols} FROM `{PROJECT}.{DATASET}.overnight_signals_enriched`"
    e = client.query(sql).to_dataframe()
    e["scan_date"] = _norm_date(e["scan_date"])
    # Dedupe to one enriched row per (contract, scan_date): keep latest enrichment.
    e = e.sort_values("enriched_at").drop_duplicates(
        subset=["recommended_contract", "scan_date"], keep="last"
    )
    e["join_key"] = e["recommended_contract"].astype(str) + "|" + e["scan_date"]
    return e


def load_live(client: bigquery.Client) -> pd.DataFrame:
    sql = (
        f"SELECT scan_date, recommended_contract, realized_return_pct, exit_reason, "
        f"underlying_return, policy_version FROM `{PROJECT}.{DATASET}.forward_paper_ledger` "
        f"WHERE realized_return_pct IS NOT NULL"
    )
    try:
        L = client.query(sql).to_dataframe()
    except Exception as ex:  # noqa: BLE001
        print(f"[warn] live ledger read failed ({ex}); proceeding backtest-only")
        return pd.DataFrame(columns=["join_key"])
    if L.empty:
        return pd.DataFrame(columns=["join_key"])
    L["scan_date"] = _norm_date(L["scan_date"])
    L["join_key"] = L["recommended_contract"].astype(str) + "|" + L["scan_date"]
    return L


# --------------------------------------------------------------------------- #
# Physics (first-order, deterministic)
# --------------------------------------------------------------------------- #
def _f(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def physics(row) -> dict:
    """First-order decomposition of the realized option return.

    All values are explanatory estimates from entry greeks + underlying path; the
    realized_ret is the ground truth. IV residual is inferred from the gap.
    """
    prem = _f(row.get("recommended_mid_price"))
    S = _f(row.get("underlying_price"))
    delta = _f(row.get("recommended_delta"))
    gamma = _f(row.get("recommended_gamma"))
    theta = _f(row.get("recommended_theta"))
    d1 = _f(row.get("next_day_pct")); d2 = _f(row.get("day2_pct")); d3 = _f(row.get("day3_pct"))
    peak = _f(row.get("peak_return_3d"))
    ret = _f(row.get("realized_ret"))
    dir_sign = 1.0 if str(row.get("direction", "")).upper().startswith("BULL") else -1.0

    out = {"d1": d1, "d2": d2, "d3": d3, "peak_fav": peak, "ret_pct": (ret * 100 if ret is not None else None)}
    # Favorable underlying move at the close of the hold.
    out["fav_move_d3"] = (dir_sign * d3) if d3 is not None else None
    if prem and prem > 0 and theta is not None:
        out["theta_drag_pct"] = abs(theta) * 3.0 / prem * 100.0
    else:
        out["theta_drag_pct"] = None
    if prem and prem > 0 and delta is not None and S is not None and d3 is not None:
        fav_dollar = dir_sign * (d3 / 100.0) * S
        out["delta_capture_pct"] = abs(delta) * fav_dollar / prem * 100.0
    else:
        out["delta_capture_pct"] = None
    # Inferred IV residual = realized - (delta_capture - theta_drag).
    if out["ret_pct"] is not None and out["delta_capture_pct"] is not None and out["theta_drag_pct"] is not None:
        out["iv_residual_pct"] = out["ret_pct"] - (out["delta_capture_pct"] - out["theta_drag_pct"])
    else:
        out["iv_residual_pct"] = None
    out["convexity"] = (gamma * S) if (gamma is not None and S is not None) else None
    return out


def takeaway(row, p: dict) -> str:
    """Deterministic, mechanism-grounded one-liner from the physics + features."""
    won = _f(row.get("realized_ret")) is not None and float(row["realized_ret"]) > 0
    dte = _f(row.get("recommended_dte"))
    fav = p.get("fav_move_d3")
    exit_r = str(row.get("exit_reason", "") or "")
    theta_drag = p.get("theta_drag_pct")
    dir_sign = 1.0 if str(row.get("direction", "")).upper().startswith("BULL") else -1.0
    d1 = _f(row.get("next_day_pct"))
    fav_d1 = (dir_sign * d1) if d1 is not None else None  # favorable day-1 move

    if won:
        if dte is not None and dte <= 10 and (p.get("peak_fav") or 0) >= 10:
            return "Fast convex move outran a short-DTE theta cliff — speed was the edge."
        # Genuinely wrong early but won anyway: convexity + cheap carry did the work.
        if fav_d1 is not None and fav_d1 <= 0 and (theta_drag is not None and theta_drag < 15):
            return "Was wrong on day 1; low theta + convexity let it win late on a single sharp move."
        if (p.get("peak_fav") or 0) >= 12:
            return "Large favorable move cleared the +80% target net of decay."
        return "Modest favorable move, but enough to finish green net of spread + theta."
    # LOST
    if fav is not None and fav > 1.0:
        return ("TWO-LABEL TRAP: underlying moved our way but the option still lost — "
                "decay / insufficient delta ate the move.")
    if fav is not None and fav < -1.0:
        return "Directional miss — underlying went against the position."
    if exit_r == "TIMEOUT":
        return "Chop: underlying never moved enough either way; theta bled it out over the hold."
    return "Lost to decay with no decisive underlying move."


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _fmt(x, pct=False, dp=1):
    if x is None:
        return "n/a"
    return f"{x:+.{dp}f}%" if pct else f"{x:.{dp}f}"


def _int(x):
    v = _f(x)
    return f"{v:.0f}" if v is not None else "n/a"


def _s(x):
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x)


def render_case(row, p: dict, source: str) -> str:
    cid = f"{row.get('ticker','?')}-{row.get('scan_date','?')}-{'B' if str(row.get('direction','')).upper().startswith('BULL') else 'S'}"
    outcome = "WON" if float(row["realized_ret"]) > 0 else "LOST"
    cat = _s(row.get("catalyst_type")) or "—"
    cscore = _f(row.get("catalyst_score"))
    head = _s(row.get("key_headline")).strip().replace("\n", " ")
    if len(head) > 110:
        head = head[:107] + "…"

    feat = (
        f"  moneyness {_fmt(_f(row.get('moneyness_pct')),pct=True)} · DTE {_int(row.get('recommended_dte'))} "
        f"· V/OI {_fmt(_f(row.get('volume_oi_ratio')),dp=2)} · spread {_fmt(_f(row.get('recommended_spread_pct')),pct=True)}\n"
        f"  greeks Δ{_fmt(_f(row.get('recommended_delta')),dp=3)} Γ{_fmt(_f(row.get('recommended_gamma')),dp=4)} "
        f"Θ{_fmt(_f(row.get('recommended_theta')),dp=3)} · IV {_fmt(_f(row.get('recommended_iv')),dp=3)} "
        f"· mid {_fmt(_f(row.get('recommended_mid_price')),dp=2)}\n"
        f"  overnight_score {_int(row.get('overnight_score'))} · flow {_s(row.get('flow_intent')) or '—'} "
        f"· catalyst {cat} ({_fmt(cscore,dp=2) if cscore is not None else '—'}) · RSI {_fmt(_f(row.get('rsi_14')),dp=0)}"
    )
    if head:
        feat += f'\n  headline "{head}"'

    why = (
        f"  underlying {_fmt(p['d1'],pct=True)}/{_fmt(p['d2'],pct=True)}/{_fmt(p['d3'],pct=True)} "
        f"(favorable peak {_fmt(p['peak_fav'],pct=True)}); position move {_fmt(p['fav_move_d3'],pct=True)}.\n"
        f"  decomp [first-order]: theta drag ~{_fmt(p['theta_drag_pct'],dp=0)}% of premium / 3d · "
        f"delta capture ~{_fmt(p['delta_capture_pct'],dp=0)}% · IV residual ~{_fmt(p['iv_residual_pct'],dp=0)}% [inferred].\n"
        f"  convexity Γ·S = {_fmt(p['convexity'],dp=2)}. exit {row.get('exit_reason','?')} → realized {_fmt(p['ret_pct'],pct=True,dp=0)}."
    )

    return (
        f"CASE {cid}  ·  {str(row.get('direction','')).upper()}  ·  {outcome}  ·  [{source}]\n"
        f"FEATURES (ex-ante)\n{feat}\n"
        f"WHY\n{why}\n"
        f"TAKEAWAY: {takeaway(row, p)}\n"
    )


def render_file(direction_label: str, cases_df: pd.DataFrame, live_keys: set, generated: str) -> str:
    rows = []
    for _, r in cases_df.iterrows():
        src = "live_ledger" if r["join_key"] in live_keys else "backtest_replay"
        rows.append((src, "WON" if float(r["realized_ret"]) > 0 else "LOST", float(r["realized_ret"]), r))

    n = len(rows)
    n_won = sum(1 for x in rows if x[1] == "WON")
    n_live = sum(1 for x in rows if x[0] == "live_ledger")
    mean_ret = cases_df["realized_ret"].mean() * 100 if n else 0.0

    head = [
        f"# {direction_label} case-memory",
        "",
        f"_Generated {generated} by build_case_memory.py — DO NOT hand-edit; regenerate._",
        "",
        f"**Corpus:** {n} closed {direction_label.lower()} trades · {n_won} WON / {n - n_won} LOST "
        f"· mean option return {mean_ret:+.1f}% · {n_live} live / {n - n_live} backtest.",
        "",
        f"> {REGIME_NOTE}",
        "",
        "> Outcome = realized option PnL (`realized_ret>0`), NOT `is_win` (stock direction). "
        "They disagree ~44% of the time — the gap is the lesson.",
        "",
        "---",
        "",
    ]

    def section(title, items):
        out = [f"## {title}  ({len(items)})", ""]
        for _src, _oc, _ret, r in items:
            out.append("```")
            out.append(render_case(r, physics(r), _src).rstrip())
            out.append("```")
            out.append("")
        return out

    body = []
    live = sorted([x for x in rows if x[0] == "live_ledger"], key=lambda x: -x[2])
    if live:
        body += section("LIVE (V5.4 ledger — authoritative)", live)
        body += ["---", ""]

    bt = [x for x in rows if x[0] == "backtest_replay"]
    bt_won = sorted([x for x in bt if x[1] == "WON"], key=lambda x: -x[2])
    bt_lost = sorted([x for x in bt if x[1] == "LOST"], key=lambda x: x[2])
    body += section("BACKTEST · WON", bt_won)
    body += ["---", ""]
    body += section("BACKTEST · LOST", bt_lost)

    return "\n".join(head + body)


def _exemplar_section(label: str, df: pd.DataFrame, live_keys: set, per_pattern: int) -> list[str]:
    """All live cases + up to `per_pattern` backtest cases per takeaway pattern,
    chosen by largest |realized_ret| (most instructive). Bounded by construction."""
    out = [f"## {label} exemplars", ""]
    rows = list(df.iterrows())
    live = [(i, r) for i, r in rows if r["join_key"] in live_keys]
    bt = [(i, r) for i, r in rows if r["join_key"] not in live_keys]

    if live:
        out += ["### LIVE (authoritative)", ""]
        for _i, r in sorted(live, key=lambda x: -abs(float(x[1]["realized_ret"]))):
            src = "live_ledger"
            out += ["```", render_case(r, physics(r), src).rstrip(), "```", ""]

    # Group backtest by takeaway pattern, take the most extreme few per pattern.
    by_pat: dict[str, list] = {}
    for _i, r in bt:
        pat = takeaway(r, physics(r))
        by_pat.setdefault(pat, []).append(r)
    out += ["### REPRESENTATIVE PATTERNS (backtest)", ""]
    for pat in sorted(by_pat, key=lambda p: -len(by_pat[p])):
        chosen = sorted(by_pat[pat], key=lambda r: -abs(float(r["realized_ret"])))[:per_pattern]
        out += [f"_{pat}  (n={len(by_pat[pat])} in corpus)_", ""]
        for r in chosen:
            out += ["```", render_case(r, physics(r), "backtest_replay").rstrip(), "```", ""]
    return out


def render_exemplars(bull, bear, live_keys, generated, per_pattern: int = 3) -> str:
    head = [
        "# Picker case-memory — exemplars (injection block)",
        "",
        f"_Generated {generated} by build_case_memory.py — curated subset of the full "
        f"bull.md/bear.md library, bounded for prompt injection._",
        "",
        "These are CLOSED past trades explained with hindsight, grouped by the lesson "
        "they teach. They are PRIORS for analogical reasoning about today's candidates — "
        "not predictions, and not proof of edge (single 2026-Q2 regime).",
        "",
        "> Outcome = option PnL (`realized_ret>0`), NOT stock direction (`is_win`). "
        "A trade where the stock moved your way but the option lost is the canonical lesson.",
        "",
        "---",
        "",
    ]
    body = _exemplar_section("BULLISH", bull, live_keys, per_pattern)
    body += ["---", ""]
    body += _exemplar_section("BEARISH", bear, live_keys, per_pattern)
    return "\n".join(head + body)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")

    client = bigquery.Client(project=PROJECT)
    bf = load_backfill()
    enr = load_enriched(client)
    live = load_live(client)
    live_keys = set(live["join_key"]) if not live.empty else set()

    # Join: backfill (outcome + path) LEFT JOIN enriched (greeks + features).
    merged = bf.merge(
        enr.drop(columns=["scan_date", "ticker", "direction", "recommended_contract"]),
        on="join_key", how="left", suffixes=("", "_enr"),
    )

    # Live overlay: replace realized_ret / exit_reason with the true live close.
    if live_keys:
        live_idx = live.set_index("join_key")
        for i, r in merged.iterrows():
            if r["join_key"] in live_keys:
                merged.at[i, "realized_ret"] = live_idx.loc[r["join_key"], "realized_return_pct"]
                merged.at[i, "exit_reason"] = live_idx.loc[r["join_key"], "exit_reason"]

    have_greeks = merged["recommended_delta"].notna().mean()
    print(f"[info] merged {len(merged)} cases; greeks coverage {have_greeks:.0%}")

    bull = merged[merged["direction"].str.upper().str.startswith("BULL")].copy()
    bear = merged[merged["direction"].str.upper().str.startswith("BEAR")].copy()

    (out_dir / "bull.md").write_text(render_file("BULLISH", bull, live_keys, generated))
    (out_dir / "bear.md").write_text(render_file("BEARISH", bear, live_keys, generated))
    (out_dir / "exemplars.md").write_text(
        render_exemplars(bull, bear, live_keys, generated)
    )

    # Provenance: per-case index + run manifest.
    idx_cols = [
        "join_key", "ticker", "scan_date", "direction", "recommended_contract",
        "recommended_dte", "moneyness_pct", "volume_oi_ratio", "recommended_delta",
        "recommended_gamma", "recommended_theta", "recommended_iv", "exit_reason",
        "realized_ret", "is_win", "peak_return_3d",
    ]
    idx = merged[[c for c in idx_cols if c in merged.columns]].copy()
    idx["source"] = idx["join_key"].map(lambda k: "live_ledger" if k in live_keys else "backtest_replay")
    idx["outcome"] = (idx["realized_ret"] > 0).map({True: "WON", False: "LOST"})
    idx.to_parquet(out_dir / "case_index.parquet", index=False)

    manifest = {
        "generated_utc": generated,
        "n_cases": int(len(merged)),
        "n_bull": int(len(bull)), "n_bear": int(len(bear)),
        "n_won": int((merged["realized_ret"] > 0).sum()),
        "n_lost": int((merged["realized_ret"] <= 0).sum()),
        "n_live": len(live_keys), "n_backtest": int(len(merged) - len(live_keys)),
        "greeks_coverage": round(float(have_greeks), 3),
        "scan_date_min": str(bf["scan_date"].min()), "scan_date_max": str(bf["scan_date"].max()),
        "label_disagreement_is_win_vs_option": round(
            float(((merged["is_win"].fillna(False).astype(bool)) != (merged["realized_ret"] > 0)).mean()), 3
        ) if "is_win" in merged.columns else None,
        "source_pickle": PICKLE,
        "note": "READ-ONLY build; deterministic physics WHY; outcome keyed on option PnL.",
    }
    (out_dir / "build_manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"[done] wrote bull.md ({len(bull)}), bear.md ({len(bear)}), case_index.parquet, build_manifest.json -> {out_dir}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
