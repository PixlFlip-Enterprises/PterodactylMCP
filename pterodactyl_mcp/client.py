from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


def _parse_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class PterodactylConfig:
    panel_url: str
    panel_token: str
    timeout: float = 30.0
    verify_ssl: bool = True
    user_agent: str = "PterodactylMCP/0.1"

    @classmethod
    def from_env(cls) -> "PterodactylConfig":
        repo_root = Path(__file__).resolve().parents[1]
        load_dotenv(repo_root / ".env", override=False)

        panel_url = os.environ.get("PANEL_URL", "").strip()
        panel_token = os.environ.get("PANEL_TOKEN", "").strip()
        if not panel_url:
            raise ValueError("Missing required env var: PANEL_URL")
        if not panel_token:
            raise ValueError("Missing required env var: PANEL_TOKEN")

        timeout_raw = os.environ.get("PANEL_TIMEOUT", "").strip()
        timeout = float(timeout_raw) if timeout_raw else 30.0
        verify_ssl = _parse_bool(os.environ.get("PANEL_VERIFY_SSL"), default=True)
        user_agent = os.environ.get("PANEL_USER_AGENT", "PterodactylMCP/0.1").strip() or "PterodactylMCP/0.1"

        return cls(
            panel_url=panel_url.rstrip("/"),
            panel_token=panel_token,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent,
        )


class PterodactylClient:
    def __init__(self, config: PterodactylConfig) -> None:
        self._http = httpx.Client(
            base_url=config.panel_url,
            timeout=config.timeout,
            verify=config.verify_ssl,
            headers={
                "Authorization": f"Bearer {config.panel_token}",
                "Accept": "Application/vnd.pterodactyl.v1+json",
                "Content-Type": "application/json",
                "User-Agent": config.user_agent,
            },
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        body: Any | None = None,
    ) -> Any:
        resp = self._http.request(method, path, params=query, json=body)
        if resp.status_code == 204:
            return {"status": 204}

        try:
            payload: Any = resp.json()
        except Exception:
            payload = resp.text

        if resp.status_code >= 400:
            raise RuntimeError(f"Pterodactyl API error {resp.status_code}: {payload}")

        return payload

