"""Tests for TableauClient REST wrappers."""

from __future__ import annotations

import pytest

from tableau_mcp.client import TableauClient
from tableau_mcp.exceptions import APIError, NotFoundError

BASE = "https://tableau.example.com/api/3.22"


async def test_list_sites(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    payload = {"sites": {"site": []}}
    httpx_mock.add_response(method="GET", url=f"{BASE}/sites", json=payload)
    result = await client.list_sites()
    assert result == payload
    request = httpx_mock.get_request()
    assert request.headers["X-Tableau-Auth"] == "tok-123"
    assert request.headers["Accept"] == "application/json"


async def test_list_projects_uses_session_site(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    payload = {"projects": {"project": [{"id": "p1", "name": "Default"}]}}
    httpx_mock.add_response(method="GET", url=f"{BASE}/sites/site-abc/projects", json=payload)
    result = await client.list_projects()
    assert result == payload


async def test_list_projects_override_site(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/sites/other/projects", json={"projects": {"project": []}}
    )
    result = await client.list_projects(site_id="other")
    assert result == {"projects": {"project": []}}


async def test_list_workbooks_with_filter(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/workbooks?filter=projectName:eq:Marketing",
        json={"workbooks": {"workbook": []}},
    )
    result = await client.list_workbooks(project_name="Marketing")
    assert "workbooks" in result


async def test_list_views_for_workbook(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/workbooks/wb-1/views",
        json={"views": {"view": [{"id": "v1"}]}},
    )
    result = await client.list_views(workbook_id="wb-1")
    assert result["views"]["view"][0]["id"] == "v1"


async def test_list_views_site_level(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views",
        json={"views": {"view": []}},
    )
    result = await client.list_views()
    assert "views" in result


async def test_list_datasources(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/datasources",
        json={"datasources": {"datasource": []}},
    )
    result = await client.list_datasources()
    assert "datasources" in result


async def test_query_view_data_returns_csv(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views/v1/data?vf_Region=West",
        text="a,b\n1,2\n",
    )
    csv = await client.query_view_data("v1", filters={"Region": "West"})
    assert csv == "a,b\n1,2\n"
    req = httpx_mock.get_request()
    assert req.headers["Accept"] == "text/csv"


async def test_query_view_image_returns_bytes(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/views/v1/image?resolution=high",
        content=b"PNGDATA",
    )
    image = await client.query_view_image("v1", resolution="high")
    assert image == b"PNGDATA"


async def test_refresh_datasource(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/sites/site-abc/datasources/ds-1/refresh",
        json={"job": {"id": "j1"}},
    )
    assert (await client.refresh_datasource("ds-1"))["job"]["id"] == "j1"


async def test_refresh_workbook(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/sites/site-abc/workbooks/wb-1/refresh",
        json={"job": {"id": "j2"}},
    )
    assert (await client.refresh_workbook("wb-1"))["job"]["id"] == "j2"


async def test_download_workbook(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/workbooks/wb-1/content?includeExtract=false",
        content=b"TWBX-BYTES",
    )
    content = await client.download_workbook("wb-1")
    assert content == b"TWBX-BYTES"


async def test_not_found_raises(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites/site-abc/projects",
        status_code=404,
        text="nope",
    )
    with pytest.raises(NotFoundError):
        await client.list_projects()


async def test_api_error_raises(client: TableauClient, httpx_mock) -> None:  # type: ignore[no-untyped-def]
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/sites",
        status_code=500,
        text="boom",
    )
    with pytest.raises(APIError) as exc:
        await client.list_sites()
    assert exc.value.status_code == 500
