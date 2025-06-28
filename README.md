# DigiKey MCP Server

A Model Context Protocol (MCP) server for DigiKey's Product Search API using FastMCP.

## Requirements

- Python 3.10+

## Setup with uv

### 1. Install uv (if you haven't already)
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Initialize the project
```bash
# Create and enter virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### 3. Set up environment variables
Make sure your `.env` file contains:
```
CLIENT_ID=your_digikey_client_id
CLIENT_SECRET=your_digikey_client_secret
```

### 4. Run the server
```bash
# Run the server (it will start on localhost:8000)
uv run python digikey_mcp_server.py

# In another terminal, test with the client
uv run python test_client.py
```

## Available Tools

- `keyword_search(keywords: str, limit: int = 5)` - Search DigiKey products by keyword

## Example Usage

The server exposes MCP tools that can be used by MCP clients like Claude Desktop, or programmatically via FastMCP clients. 