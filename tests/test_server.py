"""Smoke tests for the FastMCP server assembly."""

from __future__ import annotations

import base64

import pytest

from tableau_mcp.client import TableauClient
from tableau_mcp.server import (
    download_workbook,
    list_datasources,
    list_projects,
    list_sites,
    list_views,
    list_workbooks,
    mcp,
    query_view_data,
    query_view_image,
    refresh_datasource,
    refresh_workbook,
)


class _StubRequestContext:
    def __init__(self, lifespan_context) -> None:  # type: ignore[no-untyped-def]
        self.lifespan_context = lifespan_context


class _StubContext:
    def __init__(self, client: TableauClient) -> None:
        from tableau_mcp.server import AppContext

        self.request_context = _StubRequestContext(AppContext(client=client))


def test_server_name() -> None:
    assert mcp.name == "tableau-mcp"


@pytest.mark.asyncio
async def test_tools_registered() -> None:
    tool_names = {t.name for t in await mcp.list_tools()}
    assert {
        "list_sites",
        "list_projects",
        "list_workbooks",
        "list_views",
        "list_datasources",
        "query_view_data",
        "query_view_image",
        "refresh_datasource",
        "refresh_workbook",
        "download_workbook",
    }.issubset(tool_names)


BASE = "https://tableau.example.com/api/3.22"


async def test_list_sites_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(method="GET", url=f"{BASE}/sites", json={"sites": {"site": []}})
    result = await list_sites(_StubContext(client))
    assert result == {"sites": {"site": []}}


async def test_list_projects_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/projects",
        json={"projects": {"project": []}},
    )
    result = await list_projects(_StubContext(client))
    assert "projects" in result


async def test_list_workbooks_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/workbooks",
        json={"workbooks": {"workbook": []}},
    )
    result = await list_workbooks(_StubContext(client))
    assert "workbooks" in result


async def test_list_views_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views",
        json={"views": {"view": []}},
    )
    result = await list_views(_StubContext(client))
    assert "views" in result


async def test_list_datasources_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/datasources",
        json={"datasources": {"datasource": []}},
    )
    result = await list_datasources(_StubContext(client))
    assert "datasources" in result


async def test_query_view_data_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views/v1/data",
        text="a,b\n1,2\n",
    )
    result = await query_view_data(_StubContext(client), view_id="v1")
    assert result.startswith("a,b")


async def test_query_view_image_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views/v1/image",
        content=b"PNG",
    )
    result = await query_view_image(_StubContext(client), view_id="v1")
    assert result["content_type"] == "image/png"
    assert base64.b64decode(result["base64"]) == b"PNG"


async def test_refresh_datasource_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/sites/site-abc/datasources/ds-1/refresh",
        json={"job": {"id": "j1"}},
    )
    result = await refresh_datasource(_StubContext(client), datasource_id="ds-1")
    assert result["job"]["id"] == "j1"


async def test_refresh_workbook_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/sites/site-abc/workbooks/wb-1/refresh",
        json={"job": {"id": "j2"}},
    )
    result = await refresh_workbook(_StubContext(client), workbook_id="wb-1")
    assert result["job"]["id"] == "j2"


async def test_download_workbook_tool(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/workbooks/wb-1/content?includeExtract=false",
        content=b"TWBX",
    )
    result = await download_workbook(_StubContext(client), workbook_id="wb-1")
    assert result["size_bytes"] == 4
    assert base64.b64decode(result["base64"]) == b"TWBX"
