"""
MCP client factory for gammarips-mcp connection.

Phase-2 convenience. `x-poster` and `blog-generator` prefer direct Firestore/BQ
tools for phase 1; this module exists so the `planner` agent can graduate to
MCP-based dynamic queries once the MCP tool surface stabilizes.

Usage (in an ADK agent):

    from gammarips_content.mcp_client import build_mcp_toolset

    toolset = build_mcp_toolset()
    agent = Agent(name="planner", tools=[fetch_todays_pick, toolset], ...)
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

MCP_URL_ENV = "GAMMARIPS_MCP_URL"


def build_mcp_toolset(url: str | None = None):
    """Build an ADK McpToolset for the gammarips-mcp server.

    Args:
        url: SSE endpoint URL. Defaults to env var GAMMARIPS_MCP_URL.

    Returns:
        McpToolset instance, or None if URL is not configured or ADK is unavailable.
    """
    url = url or os.getenv(MCP_URL_ENV, "").strip()
    if not url:
        logger.warning("GAMMARIPS_MCP_URL not set — MCP toolset disabled.")
        return None

    try:
        from google.adk.tools.mcp_tool import McpToolset  # noqa: WPS433
        from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams  # noqa: WPS433
    except ImportError as exc:
        logger.warning(f"ADK MCP toolset not available: {exc}")
        return None

    return McpToolset(connection_params=SseConnectionParams(url=url))
