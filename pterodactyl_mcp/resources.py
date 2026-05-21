from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastmcp import FastMCP

from .ai_tools import get_panel_totals, get_server_summary
from .client import PterodactylClient


def register_resources(mcp: FastMCP, client_factory: Callable[[], PterodactylClient]) -> None:
    @mcp.resource(
        "pterodactyl://panel/overview",
        name="panel_overview",
        description="Counts of common Pterodactyl resources (users, servers, nodes, locations, nests).",
        mime_type="application/json",
    )
    def panel_overview() -> dict[str, int]:
        return get_panel_totals(client_factory())

    @mcp.resource(
        "pterodactyl://servers/{server_id}/summary",
        name="server_summary",
        description="Compact summary for a single Pterodactyl server (by numeric id, identifier, or uuid).",
        mime_type="application/json",
    )
    def server_summary(server_id: str) -> dict[str, Any]:
        return get_server_summary(client_factory(), server_id)
