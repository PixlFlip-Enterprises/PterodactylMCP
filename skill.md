# PterodactylMCP

MCP server for the **Pterodactyl Panel Application API**. Provides admin-level control over users, servers, nodes, locations, nests, eggs, and server databases via the Model Context Protocol.

## Install

```bash
uvx pterodactyl-mcp
# or
pip install pterodactyl-mcp && pterodactyl-mcp
```

## Required configuration

| Env var | Required | Description |
| --- | --- | --- |
| `PANEL_URL` | yes | Base URL of your Pterodactyl panel (e.g. `https://panel.example.com`). |
| `PANEL_TOKEN` | yes | Application API key (usually starts with `ptla_`). |
| `PANEL_TIMEOUT` | no | HTTP timeout in seconds (default `30`). |
| `PANEL_VERIFY_SSL` | no | `true`/`false` (default `true`). |
| `PANEL_USER_AGENT` | no | Custom User-Agent. |

## MCP client configuration

```json
{
  "mcpServers": {
    "pterodactyl": {
      "command": "uvx",
      "args": ["pterodactyl-mcp"],
      "env": {
        "PANEL_URL": "https://panel.example.com",
        "PANEL_TOKEN": "ptla_REPLACE_ME"
      }
    }
  }
}
```

## Capabilities

- **Tools (50)** — one per Application API route plus AI-friendly helpers and a generic raw-request escape hatch.
  - Groups: Users, Servers, Nodes, Locations, Nests/Eggs, Server Databases.
  - AI helpers (`ptero_ai_*`): fuzzy search, compact list, summary, panel totals.
- **Prompts (2)**
  - `troubleshoot_server` — guided diagnostic walkthrough for a server.
  - `provision_user_and_server` — guided create-user-then-server workflow.
- **Resources (2)**
  - `pterodactyl://panel/overview` — counts of users/servers/nodes/locations/nests.
  - `pterodactyl://servers/{server_id}/summary` — compact server summary.

## Transports

- `stdio` (default) — for desktop MCP clients (Claude Desktop, etc.).
- `sse` / `streamable-http` — `pterodactyl-mcp --transport sse --host 127.0.0.1 --port 8000 --path /mcp`.

## Links

- Source: https://github.com/PixlFlip-Enterprises/PterodactylMCP
- Pterodactyl Application API docs: https://pterodactyl-api-docs.netvpx.com/docs/api/application
