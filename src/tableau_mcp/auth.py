"""PAT-based authentication helpers for the Tableau REST API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .config import TableauConfig
from .exceptions import AuthenticationError


@dataclass
class TableauSession:
    """Holds the session state returned by ``/auth/signin``."""

    token: str
    site_id: str
    site_content_url: str
    user_id: str


def _extract_credentials(data: dict[str, Any]) -> TableauSession:
    """Parse the Tableau JSON signin response into a :class:`TableauSession`."""

    creds = data.get("credentials")
    if not isinstance(creds, dict):
        raise AuthenticationError("Sign-in response missing 'credentials' object.")

    token = creds.get("token")
    site = creds.get("site") or {}
    user = creds.get("user") or {}

    if not token:
        raise AuthenticationError("Sign-in response missing 'token'.")
    site_id = site.get("id")
    if not site_id:
        raise AuthenticationError("Sign-in response missing 'site.id'.")

    return TableauSession(
        token=token,
        site_id=site_id,
        site_content_url=site.get("contentUrl", ""),
        user_id=user.get("id", ""),
    )


async def sign_in(config: TableauConfig, client: httpx.AsyncClient) -> TableauSession:
    """Authenticate with Tableau via Personal Access Token.

    The provided ``client`` is used for the request. The JSON variant of the
    REST API is requested via ``Accept: application/json``.
    """

    if not config.server_url:
        raise AuthenticationError("TABLEAU_SERVER_URL is not configured.")
    if not config.pat_name or not config.pat_secret:
        raise AuthenticationError("TABLEAU_PAT_NAME / TABLEAU_PAT_SECRET are not configured.")

    payload = {
        "credentials": {
            "personalAccessTokenName": config.pat_name,
            "personalAccessTokenSecret": config.pat_secret,
            "site": {"contentUrl": config.site_content_url},
        }
    }

    url = f"{config.api_base}/auth/signin"
    try:
        response = await client.post(
            url,
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
    except httpx.HTTPError as exc:
        raise AuthenticationError(f"Sign-in request failed: {exc}") from exc

    if response.status_code != 200:
        raise AuthenticationError(
            f"Sign-in failed ({response.status_code}): {response.text}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise AuthenticationError(f"Sign-in response was not JSON: {exc}") from exc

    return _extract_credentials(data)


async def sign_out(config: TableauConfig, client: httpx.AsyncClient, token: str) -> None:
    """Invalidate a Tableau session token. Errors are swallowed intentionally."""

    url = f"{config.api_base}/auth/signout"
    try:
        await client.post(
            url,
            headers={"X-Tableau-Auth": token, "Accept": "application/json"},
        )
    except httpx.HTTPError:
        # Sign-out on shutdown is best-effort.
        return
