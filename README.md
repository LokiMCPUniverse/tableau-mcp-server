# Tableau MCP Server

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
