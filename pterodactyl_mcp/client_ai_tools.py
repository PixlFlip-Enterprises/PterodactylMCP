from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from fastmcp import FastMCP

from .client import PterodactylClient

PowerSignal = Literal["start", "stop", "restart", "kill"]


def register_client_ai_tools(mcp: FastMCP, client_factory: Callable[[], PterodactylClient]) -> None:
    @mcp.tool(
        description=(
            "Send a power signal to a server (start/stop/restart/kill). `server` is the "
            "short identifier (e.g. '95415e3b'). Returns {\"status\": 204} on success."
        )
    )
    def ptero_client_power(server: str, signal: PowerSignal) -> Any:
        return client_factory().request(
            "POST", f"/api/client/servers/{server}/power", body={"signal": signal}
        )

    @mcp.tool(
        description=(
            "Send a console command to a running server. `server` is the short identifier. "
            "Returns {\"status\": 204} on success — Pterodactyl does NOT return console "
            "output from this endpoint (read output via your console/websocket tooling)."
        )
    )
    def ptero_client_send_command(server: str, command: str) -> Any:
        return client_factory().request(
            "POST", f"/api/client/servers/{server}/command", body={"command": command}
        )

    @mcp.tool(
        description=(
            "Get a compact server status: current_state plus cpu/memory/disk/network/uptime "
            "(token-efficient view of GET .../resources). `server` is the short identifier."
        )
    )
    def ptero_client_server_status(server: str) -> dict[str, Any]:
        return get_server_status(client_factory(), server)

    @mcp.tool(
        description=(
            "List servers this Client API key can access (compact: identifier, name, node, "
            "current_state when present). Backed by GET /api/client."
        )
    )
    def ptero_client_list_servers() -> dict[str, Any]:
        return list_client_servers(client_factory())


def get_server_status(client: PterodactylClient, server: str) -> dict[str, Any]:
    payload = client.request("GET", f"/api/client/servers/{server}/resources")
    attributes = payload.get("attributes") if isinstance(payload, dict) else None
    if not isinstance(attributes, dict):
        attributes = payload if isinstance(payload, dict) else {}

    resources = attributes.get("resources")
    resources = resources if isinstance(resources, dict) else {}

    out: dict[str, Any] = {
        "current_state": attributes.get("current_state"),
        "is_suspended": attributes.get("is_suspended"),
        "cpu_absolute": resources.get("cpu_absolute"),
        "memory_bytes": resources.get("memory_bytes"),
        "disk_bytes": resources.get("disk_bytes"),
        "network_rx_bytes": resources.get("network_rx_bytes"),
        "network_tx_bytes": resources.get("network_tx_bytes"),
        "uptime": resources.get("uptime"),
    }
    return {k: v for k, v in out.items() if v is not None}


def list_client_servers(client: PterodactylClient) -> dict[str, Any]:
    payload = client.request("GET", "/api/client")
    data = payload.get("data") if isinstance(payload, dict) else None
    items: list[dict[str, Any]] = []
    if isinstance(data, list):
        for entry in data:
            attrs = entry.get("attributes") if isinstance(entry, dict) else None
            attrs = attrs if isinstance(attrs, dict) else (entry if isinstance(entry, dict) else {})
            compact = {
                "identifier": attrs.get("identifier"),
                "uuid": attrs.get("uuid"),
                "name": attrs.get("name"),
                "node": attrs.get("node"),
                "status": attrs.get("status"),
            }
            items.append({k: v for k, v in compact.items() if v is not None})
    return {"servers": items}
