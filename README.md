# Tableau MCP Server

<div align="center">

# Tableau Mcp Server

[![GitHub stars](https://img.shields.io/github/stars/LokiMCPUniverse/tableau-mcp-server?style=social)](https://github.com/LokiMCPUniverse/tableau-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LokiMCPUniverse/tableau-mcp-server?style=social)](https://github.com/LokiMCPUniverse/tableau-mcp-server/network)
[![GitHub watchers](https://img.shields.io/github/watchers/LokiMCPUniverse/tableau-mcp-server?style=social)](https://github.com/LokiMCPUniverse/tableau-mcp-server/watchers)

[![License](https://img.shields.io/github/license/LokiMCPUniverse/tableau-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/tableau-mcp-server/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/LokiMCPUniverse/tableau-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/tableau-mcp-server/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/LokiMCPUniverse/tableau-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/tableau-mcp-server/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/LokiMCPUniverse/tableau-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/tableau-mcp-server/commits)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-DC143C?style=for-the-badge)](https://modelcontextprotocol.io)

[![Commit Activity](https://img.shields.io/github/commit-activity/m/LokiMCPUniverse/tableau-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/tableau-mcp-server/pulse)
[![Code Size](https://img.shields.io/github/languages/code-size/LokiMCPUniverse/tableau-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/tableau-mcp-server)
[![Contributors](https://img.shields.io/github/contributors/LokiMCPUniverse/tableau-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/tableau-mcp-server/graphs/contributors)

</div>

A Model Context Protocol (MCP) server for integrating Tableau with GenAI applications.

## Overview

Data visualization and analytics platform

## Features

- Comprehensive Tableau API coverage
- Multiple authentication methods
- Enterprise-ready with rate limiting
- Full error handling and retry logic
- Async support for better performance

## Installation

```bash
pip install tableau-mcp-server
```

Or install from source:

```bash
git clone https://github.com/asklokesh/tableau-mcp-server.git
cd tableau-mcp-server
pip install -e .
```

## Configuration

Create a `.env` file or set environment variables according to Tableau API requirements.

## Quick Start

```python
from tableau_mcp import TableauMCPServer

# Initialize the server
server = TableauMCPServer()

# Start the server
server.start()
```

## License

MIT License - see LICENSE file for details
