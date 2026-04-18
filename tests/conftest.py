"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from tableau_mcp.auth import TableauSession
from tableau_mcp.client import TableauClient
from tableau_mcp.config import TableauConfig


@pytest.fixture
def config() -> TableauConfig:
    return TableauConfig(
        server_url="https://tableau.example.com",
        api_version="3.22",
        site_content_url="",
        pat_name="pat-name",
        pat_secret="pat-secret",
        timeout=5.0,
    )


@pytest.fixture
def session() -> TableauSession:
    return TableauSession(
        token="tok-123",
        site_id="site-abc",
        site_content_url="",
        user_id="user-1",
    )


@pytest.fixture
async def client(config: TableauConfig, session: TableauSession, httpx_mock):  # type: ignore[no-untyped-def]
    """A TableauClient with a pre-populated session and live httpx AsyncClient."""
    import httpx

    c = TableauClient(config)
    c._http = httpx.AsyncClient(timeout=config.timeout)
    c.session = session
    try:
        yield c
    finally:
        await c._http.aclose()
