# PterodactylMCP

Model Context Protocol (MCP) server for the **Pterodactyl Panel Application API** (admin endpoints), built with FastMCP.

## What this provides

- MCP tools that map to Pterodactyl **Application API** routes (users, servers, nodes, locations, nests/eggs, server databases).
- A generic `ptero_app_request` tool for calling any `/api/application/...` endpoint not yet mapped.

## Supported endpoints (Application API)

This server exposes one MCP tool per route from the NETVPX Application API docs, including:

- **Users**: list/get/create/update/delete, lookup by `external_id`
- **Servers**: list/get/create/delete, lookup by `external_id`, update details/build/startup, suspend/unsuspend, reinstall
- **Nodes**: list/get/create/update/delete, list deployable nodes, get config, manage allocations
- **Locations**: list/get/create/update/delete
- **Nests/Eggs**: list nests, get nest, list eggs, get egg
- **Server databases**: list/get/create/delete, reset database password

## References

- FastMCP Quickstart: https://gofastmcp.com/getting-started/quickstart
- NETVPX Pterodactyl Application API docs: https://pterodactyl-api-docs.netvpx.com/docs/api/application
- NETVPX Authentication docs: https://pterodactyl-api-docs.netvpx.com/docs/authentication

## Requirements

- Python 3.10+
- A Pterodactyl **Application API** key (`ptla_...`) with appropriate permissions

## Getting an Application API key

You need an **Application** token (usually `ptla_...`), not a Client token (`ptlc_...`).

Typical flow in the panel:

1) Sign in with an admin account
2) Open your account’s API credentials page
3) Create an **Application API** key and copy it

If your panel UI differs, follow the Authentication reference link below.

## Setup

1) Create a virtual environment (recommended):

- Windows (PowerShell): `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`

2) Install dependencies:

`pip install -r requirements.txt`

3) Configure environment variables:

- Copy `.env.example` to `.env`
- Set:
  - `PANEL_URL` (e.g. `https://panel.example.com`)
  - `PANEL_TOKEN` (your **Application** API key, usually starts with `ptla_`)

Optional env vars:

- `PANEL_TIMEOUT` (seconds, default `30`)
- `PANEL_VERIFY_SSL` (`true`/`false`, default `true`)
- `PANEL_USER_AGENT` (default `PterodactylMCP/0.1`)

## Run the MCP server

### STDIO transport (recommended for desktop MCP clients)

From the repo root:

`python run_server.py`

Alternatively:

`python -m pterodactyl_mcp`

### HTTP transport (optional)

`python -m pterodactyl_mcp --transport sse --host 127.0.0.1 --port 8000 --path /mcp`

## Connecting from an MCP client

Most MCP desktop clients launch the server as a subprocess. Point them at:

- Command: `python`
- Args: `C:\\path\\to\\PterodactylMCP\\run_server.py` (recommended)

If your client does not run with this repo as the working directory, prefer setting `PANEL_URL` and `PANEL_TOKEN` in the client config environment instead of relying on `.env` discovery.

### Claude Desktop example (Windows)

Edit `%APPDATA%\\Claude\\claude_desktop_config.json` and add a server entry (adjust paths as needed):

```json
{
  "mcpServers": {
    "pterodactyl": {
      "command": "python",
      "args": ["C:\\\\path\\\\to\\\\PterodactylMCP\\\\run_server.py"],
      "env": {
        "PANEL_URL": "https://panel.example.com",
        "PANEL_TOKEN": "ptla_REPLACE_ME"
      }
    }
  }
}
```

## Tool naming

Route tools are generated using the pattern:

`ptero_app_{method}_{path}` (with `/api/application/` removed, `/` → `_`, `-` → `_`, `{param}` → `param`).

## Calling tools

- Each route tool takes the route path params as normal arguments (e.g. `server`, `user`, `node`), plus optional `query` and `body`.
- Use `query` for query-string parameters (pagination, filters, includes), and `body` for JSON request payloads.
- To discover all tool names and their routes, call `ptero_app_list_endpoints`.

Example query params (brackets are valid dict keys):

- `{"filter[email]": "admin@example.com", "include": "servers"}`

To list all exposed tools and their routes, call:

- `ptero_app_list_endpoints`
