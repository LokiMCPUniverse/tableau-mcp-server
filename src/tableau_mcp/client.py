"""Async HTTP client for the Tableau REST API."""

from __future__ import annotations

from typing import Any

import httpx

from .auth import TableauSession, sign_in, sign_out
from .config import TableauConfig
from .exceptions import APIError, NotFoundError


class TableauClient:
    """Thin async wrapper over the Tableau REST API.

    Handles the signed-in header, JSON decoding, and typed errors. All paths
    passed to ``_request`` are appended to :pyattr:`TableauConfig.api_base`.
    """

    def __init__(self, config: TableauConfig) -> None:
        self.config = config
        self._http: httpx.AsyncClient | None = None
        self.session: TableauSession | None = None

    # ------------------------------------------------------------------ lifecycle

    async def connect(self) -> TableauSession:
        """Open the underlying HTTP client and sign in."""

        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.config.timeout)
        self.session = await sign_in(self.config, self._http)
        return self.session

    async def close(self) -> None:
        """Sign out and release the HTTP client."""

        if self._http is None:
            return
        if self.session is not None:
            await sign_out(self.config, self._http, self.session.token)
            self.session = None
        await self._http.aclose()
        self._http = None

    # ------------------------------------------------------------------ helpers

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("TableauClient is not connected. Call connect() first.")
        return self._http

    @property
    def default_site_id(self) -> str:
        if self.session is None:
            raise RuntimeError("TableauClient is not signed in.")
        return self.session.site_id

    def _site(self, site_id: str | None) -> str:
        return site_id or self.default_site_id

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        if self.session is None:
            raise RuntimeError("TableauClient is not signed in.")
        headers = {
            "X-Tableau-Auth": self.session.token,
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        accept: str = "application/json",
    ) -> httpx.Response:
        url = f"{self.config.api_base}{path}"
        response = await self.http.request(
            method,
            url,
            params=params,
            json=json,
            headers=self._headers({"Accept": accept}),
        )
        if response.status_code == 404:
            raise NotFoundError(
                f"Not found: {method} {path}",
                status_code=404,
                body=response.text,
            )
        if response.status_code >= 400:
            raise APIError(
                f"Tableau API error {response.status_code}: {response.text}",
                status_code=response.status_code,
                body=response.text,
            )
        return response

    async def _json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        response = await self._request(method, path, params=params, json=json)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise APIError(f"Tableau API returned non-JSON body: {exc}") from exc

    # ------------------------------------------------------------------ endpoints

    async def list_sites(self) -> dict[str, Any]:
        return await self._json("GET", "/sites")

    async def list_projects(self, site_id: str | None = None) -> dict[str, Any]:
        return await self._json("GET", f"/sites/{self._site(site_id)}/projects")

    async def list_workbooks(
        self,
        site_id: str | None = None,
        project_name: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if project_name:
            params["filter"] = f"projectName:eq:{project_name}"
        return await self._json(
            "GET",
            f"/sites/{self._site(site_id)}/workbooks",
            params=params or None,
        )

    async def list_views(
        self,
        site_id: str | None = None,
        workbook_id: str | None = None,
    ) -> dict[str, Any]:
        site = self._site(site_id)
        if workbook_id:
            return await self._json("GET", f"/sites/{site}/workbooks/{workbook_id}/views")
        return await self._json("GET", f"/sites/{site}/views")

    async def list_datasources(self, site_id: str | None = None) -> dict[str, Any]:
        return await self._json("GET", f"/sites/{self._site(site_id)}/datasources")

    async def query_view_data(
        self,
        view_id: str,
        filters: dict[str, str] | None = None,
        site_id: str | None = None,
    ) -> str:
        params: dict[str, Any] = {}
        if filters:
            for key, value in filters.items():
                params[f"vf_{key}"] = value
        response = await self._request(
            "GET",
            f"/sites/{self._site(site_id)}/views/{view_id}/data",
            params=params or None,
            accept="text/csv",
        )
        return response.text

    async def query_view_image(
        self,
        view_id: str,
        resolution: str | None = None,
        site_id: str | None = None,
    ) -> bytes:
        params: dict[str, Any] = {}
        if resolution:
            params["resolution"] = resolution
        response = await self._request(
            "GET",
            f"/sites/{self._site(site_id)}/views/{view_id}/image",
            params=params or None,
            accept="image/png",
        )
        return response.content

    async def refresh_datasource(
        self,
        datasource_id: str,
        site_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"/sites/{self._site(site_id)}/datasources/{datasource_id}/refresh",
            json={},
        )

    async def refresh_workbook(
        self,
        workbook_id: str,
        site_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"/sites/{self._site(site_id)}/workbooks/{workbook_id}/refresh",
            json={},
        )

    async def download_workbook(
        self,
        workbook_id: str,
        include_extract: bool = False,
        site_id: str | None = None,
    ) -> bytes:
        params = {"includeExtract": "true" if include_extract else "false"}
        response = await self._request(
            "GET",
            f"/sites/{self._site(site_id)}/workbooks/{workbook_id}/content",
            params=params,
            accept="application/octet-stream",
        )
        return response.content
