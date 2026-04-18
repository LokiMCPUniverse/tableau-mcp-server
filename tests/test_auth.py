"""Tests for authentication helpers."""

from __future__ import annotations

import httpx
import pytest

from tableau_mcp.auth import _extract_credentials, sign_in, sign_out
from tableau_mcp.config import TableauConfig
from tableau_mcp.exceptions import AuthenticationError


def _ok_payload() -> dict:
    return {
        "credentials": {
            "token": "tok-xyz",
            "site": {"id": "site-123", "contentUrl": ""},
            "user": {"id": "user-1"},
        }
    }


def test_extract_credentials_ok() -> None:
    session = _extract_credentials(_ok_payload())
    assert session.token == "tok-xyz"
    assert session.site_id == "site-123"
    assert session.user_id == "user-1"


def test_extract_credentials_missing_token() -> None:
    payload = {"credentials": {"site": {"id": "s"}}}
    with pytest.raises(AuthenticationError):
        _extract_credentials(payload)


def test_extract_credentials_missing_site() -> None:
    payload = {"credentials": {"token": "t"}}
    with pytest.raises(AuthenticationError):
        _extract_credentials(payload)


def test_extract_credentials_wrong_shape() -> None:
    with pytest.raises(AuthenticationError):
        _extract_credentials({})


async def test_sign_in_success(config: TableauConfig, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url="https://tableau.example.com/api/3.22/auth/signin",
        json=_ok_payload(),
        status_code=200,
    )
    async with httpx.AsyncClient() as client:
        session = await sign_in(config, client)
    assert session.token == "tok-xyz"
    assert session.site_id == "site-123"


async def test_sign_in_rejects_missing_config() -> None:
    config = TableauConfig(server_url="", pat_name="", pat_secret="")
    async with httpx.AsyncClient() as client:
        with pytest.raises(AuthenticationError):
            await sign_in(config, client)


async def test_sign_in_http_error(config: TableauConfig, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url="https://tableau.example.com/api/3.22/auth/signin",
        status_code=401,
        text="bad pat",
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(AuthenticationError):
            await sign_in(config, client)


async def test_sign_out_best_effort(config: TableauConfig, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url="https://tableau.example.com/api/3.22/auth/signout",
        status_code=204,
    )
    async with httpx.AsyncClient() as client:
        await sign_out(config, client, "tok-xyz")
