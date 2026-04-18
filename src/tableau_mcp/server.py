"""FastMCP server exposing Tableau REST API tools."""

from __future__ import annotations

import base64
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from .client import TableauClient
from .config import TableauConfig


@dataclass
class AppContext:
    """Request-scoped context carrying the connected Tableau client."""

    client: TableauClient


@asynccontextmanager
async def lifespan(_mcp: FastMCP) -> AsyncIterator[AppContext]:
    """Sign in on startup, sign out on shutdown."""

    config = TableauConfig()
    client = TableauClient(config)
    await client.connect()
    try:
        yield AppContext(client=client)
    finally:
        await client.close()


mcp = FastMCP("tableau-mcp", lifespan=lifespan)


def _client(ctx: Context) -> TableauClient:
    app_ctx: AppContext = ctx.request_context.lifespan_context
    return app_ctx.client


@mcp.tool()
async def list_sites(ctx: Context) -> dict[str, Any]:
    """List all sites accessible to the authenticated user."""
    return await _client(ctx).list_sites()


@mcp.tool()
async def list_projects(ctx: Context, site_id: str | None = None) -> dict[str, Any]:
    """List projects on the specified site (defaults to the signed-in site)."""
    return await _client(ctx).list_projects(site_id=site_id)


@mcp.tool()
async def list_workbooks(
    ctx: Context,
    site_id: str | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    """List workbooks, optionally filtered by project name."""
    return await _client(ctx).list_workbooks(site_id=site_id, project_name=project_name)


@mcp.tool()
async def list_views(
    ctx: Context,
    site_id: str | None = None,
    workbook_id: str | None = None,
) -> dict[str, Any]:
    """List views on a site or inside a specific workbook."""
    return await _client(ctx).list_views(site_id=site_id, workbook_id=workbook_id)


@mcp.tool()
async def list_datasources(ctx: Context, site_id: str | None = None) -> dict[str, Any]:
    """List data sources published on a site."""
    return await _client(ctx).list_datasources(site_id=site_id)


@mcp.tool()
async def query_view_data(
    ctx: Context,
    view_id: str,
    filters: dict[str, str] | None = None,
    site_id: str | None = None,
) -> str:
    """Return view data as CSV. ``filters`` maps field names to value filters."""
    return await _client(ctx).query_view_data(view_id=view_id, filters=filters, site_id=site_id)


@mcp.tool()
async def query_view_image(
    ctx: Context,
    view_id: str,
    resolution: str | None = None,
    site_id: str | None = None,
) -> dict[str, Any]:
    """Return the view rendered as a PNG image (base64 encoded)."""
    data = await _client(ctx).query_view_image(
        view_id=view_id, resolution=resolution, site_id=site_id
    )
    return {
        "view_id": view_id,
        "content_type": "image/png",
        "base64": base64.b64encode(data).decode("ascii"),
    }


@mcp.tool()
async def refresh_datasource(
    ctx: Context,
    datasource_id: str,
    site_id: str | None = None,
) -> dict[str, Any]:
    """Trigger an extract refresh on a data source."""
    return await _client(ctx).refresh_datasource(datasource_id=datasource_id, site_id=site_id)


@mcp.tool()
async def refresh_workbook(
    ctx: Context,
    workbook_id: str,
    site_id: str | None = None,
) -> dict[str, Any]:
    """Trigger an extract refresh on a workbook."""
    return await _client(ctx).refresh_workbook(workbook_id=workbook_id, site_id=site_id)


@mcp.tool()
async def download_workbook(
    ctx: Context,
    workbook_id: str,
    include_extract: bool = False,
    site_id: str | None = None,
) -> dict[str, Any]:
    """Download a workbook's .twb/.twbx content (base64 encoded)."""
    data = await _client(ctx).download_workbook(
        workbook_id=workbook_id, include_extract=include_extract, site_id=site_id
    )
    return {
        "workbook_id": workbook_id,
        "include_extract": include_extract,
        "size_bytes": len(data),
        "base64": base64.b64encode(data).decode("ascii"),
    }


def main() -> None:
    """Entry point for the ``tableau-mcp`` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
