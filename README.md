# Tableau MCP Server

A Model Context Protocol (MCP) server for Tableau Server and Tableau Cloud, built on the
official `mcp` Python SDK (FastMCP). It authenticates via a Personal Access Token (PAT) and
exposes read/write tools backed by the Tableau REST API.

## Features

- PAT-based sign-in with automatic sign-out on shutdown (via FastMCP `lifespan`)
- Async `httpx` client with typed exceptions (`TableauError`, `AuthenticationError`, `APIError`, `NotFoundError`)
- Tools for sites, projects, workbooks, views, data sources
- View data (CSV) and image (PNG) retrieval
- Extract refresh and workbook download helpers

## Installation

```bash
git clone https://github.com/asklokesh/tableau-mcp-server.git
cd tableau-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

All settings are read from environment variables with the `TABLEAU_` prefix (a `.env`
file next to the working directory is also supported).

| Variable | Default | Description |
| --- | --- | --- |
| `TABLEAU_SERVER_URL` | *(required)* | Base URL, e.g. `https://10ax.online.tableau.com` or `https://tableau.example.com` |
| `TABLEAU_API_VERSION` | `3.22` | Tableau REST API version |
| `TABLEAU_SITE_CONTENT_URL` | `""` | Site content URL; empty string targets the default site |
| `TABLEAU_PAT_NAME` | *(required)* | Personal Access Token name |
| `TABLEAU_PAT_SECRET` | *(required)* | Personal Access Token secret |
| `TABLEAU_TIMEOUT` | `60` | HTTP request timeout (seconds) |

## Running

```bash
tableau-mcp
# or
python -m tableau_mcp.server
```

## Claude Desktop configuration

```json
{
  "mcpServers": {
    "tableau": {
      "command": "tableau-mcp",
      "env": {
        "TABLEAU_SERVER_URL": "https://10ax.online.tableau.com",
        "TABLEAU_SITE_CONTENT_URL": "mysite",
        "TABLEAU_PAT_NAME": "my-pat",
        "TABLEAU_PAT_SECRET": "xxxxxxxxxxxx"
      }
    }
  }
}
```

## Tools

| Tool | Description |
| --- | --- |
| `list_sites` | List all sites reachable with the current PAT |
| `list_projects` | List projects on a site |
| `list_workbooks` | List workbooks, optionally filtered by project name |
| `list_views` | List views on a site or for a specific workbook |
| `list_datasources` | List published data sources |
| `query_view_data` | Return view data as CSV (optional `vf_*` filters) |
| `query_view_image` | Return view rendering as a base64-encoded PNG |
| `refresh_datasource` | Trigger an extract refresh for a data source |
| `refresh_workbook` | Trigger an extract refresh for a workbook |
| `download_workbook` | Download a workbook as base64-encoded `.twb`/`.twbx` |

## Development

```bash
pip install -e ".[dev]"
pytest -x --tb=short
ruff check src tests
```

## License

MIT License - see LICENSE file for details.
