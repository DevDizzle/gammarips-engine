#!/usr/bin/env python3
"""Build fresh, verified outbound prospect list for GammaRips MCP outbound outreach.

Searches active developers who have created, pushed to, or forked repositories matching:
- options trading MCP (alpacahq/alpaca-mcp-server, erikmaday/unusual-whales-mcp)
- agentic trading (JakeNesler/OpenProphet, TauricResearch/TradingAgents, caiovicentino/polymarket-mcp-server)
- finance MCP (Alex2Yang97/yahoo-finance-mcp, wshobson/maverick-mcp)
- options flow (NavnoorBawa/Options-Flow-Predictor, aaryansinha16/AI-trader)
- claude-code finance tools (tradesdontlie/tradingview-mcp, Spoofkapoof/TradingViewMCPServer)

Fetches public profiles using `gh api` and crafts tailored 2-sentence DMs.
"""
from __future__ import annotations

import csv
import json
import subprocess
import time
from pathlib import Path
from typing import Any

FREE_CMD = "claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp"

SEED_AUTHORS = [
    ("JakeNesler", "JakeNesler/OpenProphet", "Autonomous AI trading agent with MCP tools"),
    ("jackson-cmd", "jackson-cmd/zeus-options-terminal", "Zeus self-hosted options terminal & MCP"),
    ("DuFanYin", "DuFanYin/optra", "Optra C++23 options trading engine & MCP"),
    ("merjua14", "merjua14/ai-momentum-trader", "Robinhood momentum trading agent via Claude/OpenAI"),
    ("KrishnaMurali177", "KrishnaMurali177/options-algo-trader", "Robinhood options trading agent via MCP"),
    ("Oft3r", "Oft3r/agentic-trading-desk", "Agentic trading desk via Robinhood MCP"),
    ("erikmaday", "erikmaday/unusual-whales-mcp", "Unusual Whales MCP options flow server"),
    ("Alex2Yang97", "Alex2Yang97/yahoo-finance-mcp", "Yahoo Finance MCP server"),
    ("wshobson", "wshobson/maverick-mcp", "Maverick stock market & backtesting MCP"),
    ("caiovicentino", "caiovicentino/polymarket-mcp-server", "Polymarket MCP trading agent server"),
    ("ryanfrigo", "ryanfrigo/kalshi-ai-trading-bot", "Kalshi agent-native trading toolkit & MCP"),
    ("tradesdontlie", "tradesdontlie/tradingview-mcp", "TradingView desktop MCP for Claude Code"),
    ("Spoofkapoof", "Spoofkapoof/TradingViewMCPServer", "TradingView multi-asset MCP server"),
    ("tedlikeskix", "tedlikeskix/alpaca-mcp-server", "Alpaca options MCP server"),
    ("NavnoorBawa", "NavnoorBawa/Options-Flow-Predictor", "Options flow feature predictor"),
    ("aaryansinha16", "aaryansinha16/AI-trader", "AI options trading & institutional flow"),
    ("gadicc", "gadicc/yahoo-finance2", "Yahoo Finance CLI and MCP agent skill"),
    ("simonlin1212", "simonlin1212/TradingAgents-astock", "TradingAgents multi-agent investment research"),
    ("daviddme", "daviddme/tradingview-indicator-search-mcp-server", "TradingView indicator MCP server for Claude Code"),
    ("chrisleekr", "chrisleekr/binance-trading-bot", "Binance trading bot with MCP support"),
    ("ariadng", "ariadng/metatrader-mcp-server", "MetaTrader MCP server for AI LLMs"),
    ("robcerda", "robcerda/monarch-mcp-server", "Monarch Money personal finance MCP server"),
]

FORK_SOURCES = [
    ("alpacahq/alpaca-mcp-server", 35, "Alpaca options trading MCP server"),
    ("erikmaday/unusual-whales-mcp", 25, "Unusual Whales options flow MCP server"),
    ("caiovicentino/polymarket-mcp-server", 25, "prediction market agentic execution via MCP"),
    ("Alex2Yang97/yahoo-finance-mcp", 25, "Yahoo Finance options & market data MCP server"),
    ("TauricResearch/TradingAgents", 20, "TradingAgents multi-agent trading framework"),
]


def gh_api(endpoint: str) -> Any:
    res = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    try:
        return json.loads(res.stdout)
    except Exception:
        return None


def craft_dm(name: str, login: str, source_repo: str) -> str:
    if name.lower() in ("anonymous", "none", "null", ""):
        disp_name = login
    else:
        disp_name = name.split()[0]
        disp_name = "".join(c for c in disp_name if c.isalnum() or c in "-_") or login

    repo_short = source_repo.split("/")[-1]

    if "alpaca" in source_repo.lower():
        s1 = f"Hi {disp_name}, noticed you're building with the Alpaca MCP server for automated trading - thought you might find pre-filtered overnight options flow and morning liquidity snapshots useful for your strategy stack."
        s2 = f"You can plug GammaRips' free candidate pool directly into Claude Code or Cursor in 10 seconds: `{FREE_CMD}`."
    elif "whales" in source_repo.lower() or "flow" in source_repo.lower():
        s1 = f"Hi {disp_name}, saw your work around {repo_short} - we built an overnight options edge engine that screens institutional flow and filters contracts by real tradeability and volatility edge (RV/IV)."
        s2 = f"You can test today's free 3-contract preview directly in your agent via MCP: `{FREE_CMD}`."
    elif "tradingview" in source_repo.lower():
        s1 = f"Hi {disp_name}, loved your work on {repo_short} - thought you'd appreciate having an overnight options candidate pool with morning liquidity snapshots directly in your Claude Code workflow."
        s2 = f"You can plug in the free GammaRips MCP server in 10 seconds: `{FREE_CMD}`."
    elif "zeus" in source_repo.lower() or "optra" in source_repo.lower() or "momentum" in source_repo.lower() or "algo" in source_repo.lower():
        s1 = f"Hi {disp_name}, saw your work building {repo_short} - thought you might find our pre-filtered overnight options candidate pool and morning liquidity snapshots valuable for your execution models."
        s2 = f"You can test today's free preview in Claude Code or Cursor in 10 seconds: `{FREE_CMD}`."
    elif "polymarket" in source_repo.lower() or "kalshi" in source_repo.lower() or "binance" in source_repo.lower():
        s1 = f"Hi {disp_name}, saw your work on {repo_short} - thought you might find our structured, catalyst-grounded options signals valuable for multi-market agentic trading."
        s2 = f"You can inspect today's free 3-contract preview in Claude Code or Cursor right now: `{FREE_CMD}`."
    else:
        s1 = f"Hi {disp_name}, saw your work with {repo_short} - thought you might find our pre-filtered overnight options candidate pool useful for your agentic finance workflows."
        s2 = f"You can plug the free GammaRips MCP server into Claude or Cursor in 10 seconds: `{FREE_CMD}`."

    return f"{s1} {s2}"


def main() -> int:
    candidates = []
    seen = set()

    for login, repo, desc in SEED_AUTHORS:
        if login not in seen:
            seen.add(login)
            candidates.append((login, repo))

    for repo, count, desc in FORK_SOURCES:
        forks = gh_api(f"/repos/{repo}/forks?per_page={count}")
        if forks and isinstance(forks, list):
            for f in forks:
                owner = f.get("owner", {})
                login = owner.get("login")
                user_type = owner.get("type", "User")
                if login and user_type == "User" and login not in seen:
                    seen.add(login)
                    candidates.append((login, repo))

    records = []
    target_count = 60

    for login, repo in candidates:
        if len(records) >= target_count:
            break
        profile = gh_api(f"/users/{login}")
        if not profile or "login" not in profile:
            continue
        name = profile.get("name") or ""
        twitter = profile.get("twitter_username") or ""
        blog = profile.get("blog") or ""
        email = profile.get("email") or ""
        bio = (profile.get("bio") or "").strip().replace("\r", " ").replace("\n", " ")

        dm = craft_dm(name, login, repo)

        records.append({
            "login": login,
            "name": name,
            "twitter_username": twitter,
            "blog": blog,
            "email": email,
            "bio": bio,
            "source_repo": repo,
            "personalized_dm": dm,
        })
        time.sleep(0.05)

    out_file = Path("/home/evan/workspace/GAMMARIPS-PROSPECTS-2026-11-16.csv")
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "login", "name", "twitter_username", "blog", "email", "bio", "source_repo", "personalized_dm"
        ])
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} prospects to {out_file}")
    return 0


if __name__ == "__main__":
    main()
