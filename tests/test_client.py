import pytest

from pterodactyl_mcp.client import PterodactylConfig


def test_from_env_happy_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PANEL_URL", "https://panel.example.com/")
    monkeypatch.setenv("PANEL_TOKEN", "ptla_abc")
    monkeypatch.delenv("PANEL_CLIENT_TOKEN", raising=False)
    monkeypatch.setenv("PANEL_TIMEOUT", "45")
    monkeypatch.setenv("PANEL_VERIFY_SSL", "false")

    cfg = PterodactylConfig.from_env()
    assert cfg.panel_url == "https://panel.example.com"
    assert cfg.panel_token == "ptla_abc"
    assert cfg.panel_client_token is None
    assert cfg.timeout == 45.0
    assert cfg.verify_ssl is False


def test_from_env_parses_client_token(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PANEL_URL", "https://panel.example.com")
    monkeypatch.delenv("PANEL_TOKEN", raising=False)
    monkeypatch.setenv("PANEL_CLIENT_TOKEN", "ptlc_xyz")

    cfg = PterodactylConfig.from_env()
    assert cfg.panel_token is None
    assert cfg.panel_client_token == "ptlc_xyz"


def test_from_env_missing_url(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PANEL_URL", raising=False)
    monkeypatch.setenv("PANEL_TOKEN", "ptla_abc")
    with pytest.raises(ValueError, match="PANEL_URL"):
        PterodactylConfig.from_env()


def test_from_env_missing_both_tokens(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PANEL_URL", "https://panel.example.com")
    monkeypatch.delenv("PANEL_TOKEN", raising=False)
    monkeypatch.delenv("PANEL_CLIENT_TOKEN", raising=False)
    with pytest.raises(ValueError, match="PANEL_TOKEN"):
        PterodactylConfig.from_env()
