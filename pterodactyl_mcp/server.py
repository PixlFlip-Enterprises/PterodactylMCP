from __future__ import annotations

import argparse
import inspect
import os
import re
from functools import lru_cache
from typing import Any, Literal
from urllib.parse import quote

from fastmcp import FastMCP

from .ai_tools import register_ai_tools
from .client import PterodactylClient, PterodactylConfig
from .routes import APPLICATION_ROUTES

PathParam = str | int

mcp = FastMCP("Pterodactyl Application API")


@lru_cache
def _client() -> PterodactylClient:
    return PterodactylClient(PterodactylConfig.from_env())


def _tool_name(method: str, path: str) -> str:
    suffix = path.removeprefix("/api/application/").strip("/")
    parts: list[str] = []
    for segment in suffix.split("/"):
        if segment.startswith("{") and segment.endswith("}"):
            segment = segment[1:-1]
        segment = segment.replace("-", "_")
        parts.append(segment)
    return f"ptero_app_{method.lower()}_{'_'.join(parts)}"


def _register_application_route_tools() -> None:
    path_param_re = re.compile(r"{([^}]+)}")

    for route in APPLICATION_ROUTES:
        method = route["method"]
        template_path = route["path"]
        name = _tool_name(method, template_path)
        path_params = path_param_re.findall(template_path)

        def _make_tool(
            *,
            method: str = method,
            template_path: str = template_path,
            path_params: list[str] = path_params,
            name: str = name,
        ):
            def _tool(**kwargs: Any) -> Any:
                resolved_path = template_path
                for param in path_params:
                    if param not in kwargs:
                        raise ValueError(f"Missing required path parameter: {param}")
                    resolved_path = resolved_path.replace(
                        f"{{{param}}}", quote(str(kwargs.pop(param)), safe="")
                    )

                query = kwargs.pop("query", None)
                body = kwargs.pop("body", None)
                if kwargs:
                    extra = ", ".join(sorted(kwargs.keys()))
                    raise ValueError(f"Unexpected parameters: {extra}")

                return _client().request(method, resolved_path, query=query, body=body)

            _tool.__name__ = name
            _tool.__doc__ = f"{method} {template_path}"

            parameters: list[inspect.Parameter] = [
                inspect.Parameter(
                    p,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=PathParam,
                )
                for p in path_params
            ]
            parameters.append(
                inspect.Parameter(
                    "query",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=dict[str, Any] | None,
                )
            )
            parameters.append(
                inspect.Parameter(
                    "body",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=Any | None,
                )
            )
            _tool.__signature__ = inspect.Signature(parameters)
            _tool.__annotations__ = {
                **{p: PathParam for p in path_params},
                "query": dict[str, Any] | None,
                "body": Any | None,
                "return": Any,
            }

            description = f"{method} {template_path}"
            if method == "GET" and template_path == "/api/application/users":
                description += " (raw; can be large — prefer ptero_ai_list_users / ptero_ai_search_users)"
            elif method == "GET" and template_path == "/api/application/servers":
                description += " (raw; can be large — prefer ptero_ai_list_servers / ptero_ai_search_servers)"

            mcp.tool(name=name, description=description)(_tool)

        _make_tool()


@mcp.tool(description="List all Application API endpoints exposed as tools.")
def ptero_app_list_endpoints() -> list[dict[str, str]]:
    return [
        {"tool": _tool_name(r["method"], r["path"]), "method": r["method"], "path": r["path"]}
        for r in APPLICATION_ROUTES
    ]


@mcp.tool(description="Make a raw Application API request (useful for endpoints not mapped as tools yet).")
def ptero_app_request(
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    path: str,
    query: dict[str, Any] | None = None,
    body: Any | None = None,
) -> Any:
    if not path.startswith("/api/application/"):
        raise ValueError("path must start with /api/application/")
    return _client().request(method, path, query=query, body=body)


_register_application_route_tools()
register_ai_tools(mcp, _client)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pterodactyl Application API MCP server (FastMCP).")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http", "http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="MCP transport (default: stdio).",
    )
    parser.add_argument("--host", default=os.environ.get("MCP_HOST"), help="HTTP host (sse/http only).")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ["MCP_PORT"]) if os.environ.get("MCP_PORT") else None,
        help="HTTP port (sse/http only).",
    )
    parser.add_argument("--path", default=os.environ.get("MCP_PATH"), help="HTTP path (sse/http only).")
    parser.add_argument("--no-banner", action="store_true", help="Disable FastMCP banner.")
    args = parser.parse_args(argv)

    transport_kwargs: dict[str, Any] = {}
    if args.transport != "stdio":
        if args.host:
            transport_kwargs["host"] = args.host
        if args.port:
            transport_kwargs["port"] = args.port
        if args.path:
            transport_kwargs["path"] = args.path

    mcp.run(
        transport=args.transport,
        show_banner=not args.no_banner,
        **transport_kwargs,
    )


if __name__ == "__main__":
    main()
