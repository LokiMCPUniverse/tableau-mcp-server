"""Tests for TableauConfig."""

from __future__ import annotations

from tableau_mcp.config import TableauConfig


def test_defaults() -> None:
    config = TableauConfig(
        server_url="https://tableau.example.com",
        pat_name="n",
        pat_secret="s",
    )
    assert config.api_version == "3.22"
    assert config.site_content_url == ""
    assert config.timeout == 60.0
    assert config.api_base == "https://tableau.example.com/api/3.22"


def test_api_base_strips_trailing_slash() -> None:
    config = TableauConfig(server_url="https://tableau.example.com/", api_version="3.21")
    assert config.api_base == "https://tableau.example.com/api/3.21"


def test_env_prefix(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("TABLEAU_SERVER_URL", "https://env.example.com")
    monkeypatch.setenv("TABLEAU_PAT_NAME", "env-pat")
    monkeypatch.setenv("TABLEAU_PAT_SECRET", "env-secret")
    monkeypatch.setenv("TABLEAU_API_VERSION", "3.20")
    monkeypatch.setenv("TABLEAU_SITE_CONTENT_URL", "mysite")
    monkeypatch.setenv("TABLEAU_TIMEOUT", "12")

    config = TableauConfig()
    assert config.server_url == "https://env.example.com"
    assert config.pat_name == "env-pat"
    assert config.pat_secret == "env-secret"
    assert config.api_version == "3.20"
    assert config.site_content_url == "mysite"
    assert config.timeout == 12.0
