# DigiKey MCP Server

A Model Context Protocol (MCP) server for DigiKey's Product Search API using FastMCP. Search for electronic components, get pricing, check stock levels, and access product specifications directly from Claude Desktop or Claude Code.

## ✨ Fork Improvements

This fork extends the original implementation with production-ready features for professional BOM management:

### 🔧 Critical Bug Fixes

**Fixed OAuth Token Expiration (BREAKING BUG):**
- **Original Issue**: Server would fail after ~1 hour when OAuth token expired
- **Our Fix**: Automatic token refresh with 5-minute buffer before expiration
- **Impact**: Server now runs reliably 24/7 without authentication failures
- Thread-safe token management with retry logic for 401 errors

**Enhanced Error Handling:**
- Graceful 404 handling with helpful error messages
- Automatic retry on token expiration (401)
- Better validation for empty API responses

### 🎯 Enhanced API Coverage (86% of DigiKey API)

**New Endpoints:**
- `get_pricing_by_quantity` - Intelligent pricing optimization with 4 scenarios (exact qty, min order, max order, better value)
- `get_alternate_packaging` - Compare packaging options (Tape & Reel, Cut Tape, Tube, Digi-Reel, etc.)
- `get_product_associations` - Discover mating connectors and complementary components

### 🚀 Context Optimization

**Smart Token Management:**
- **Compact mode** (enabled by default for ALL endpoints) - 90% reduction in response size
  - Strips verbose fields, flattens nested objects, removes null values
  - Extracts only essential info: part numbers, pricing, stock, URLs
  - Now available on: `keyword_search`, `product_details`, `search_product_substitutions`, `get_product_media`, `get_alternate_packaging`, `get_product_associations`
- **Enforced limits** on all endpoints to prevent context flooding
  - Search: max 50 results (default 5)
  - Manufacturers/Categories: max 500 (default 100)
  - Media: max 50 per type (default 10)
- **Intelligent field extraction** from nested DigiKey API responses

---

## 🔐 Security-First Approach

**IMPORTANT:** Credentials are stored directly in Claude's configuration files (standard MCP approach).

**How it works:**
- Add `CLIENT_ID` and `CLIENT_SECRET` to config JSON files
- Claude passes credentials to MCP server at startup
- Config files are local, never committed to git
- Protected by your macOS user account permissions

**Never commit API credentials to git repositories.**

---

## 📋 Quick Start

1. [Get DigiKey API Credentials](#getting-digikey-api-credentials)
2. [Install](#installation)
3. [Configure Claude](#configuration)
4. [Try Example Queries](#example-queries)

---

## Requirements

- Python 3.10+
- **uv** package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- DigiKey API credentials (CLIENT_ID and CLIENT_SECRET)
- Claude Desktop or Claude Code

---

## Getting DigiKey API Credentials

1. Visit https://developer.digikey.com/
2. Sign in or create account
3. Create New Application:
   - **Name:** "Claude MCP Integration"
   - **API Access:** Product Search API
   - **Redirect URI:** `http://localhost` (not used)
4. Copy your **CLIENT_ID** and **CLIENT_SECRET**
5. Choose environment:
   - **Sandbox:** Free testing with test data
   - **Production:** Real inventory and pricing

---

## Installation

```bash
# Clone repository
git clone <your-fork-url>
cd digikey-MCP

# Install dependencies
uv sync

# Make run script executable
chmod +x run_digikey.sh
```

---

## Configuration

Add the DigiKey MCP server to your Claude configuration:

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "digikey": {
      "command": "/absolute/path/to/digikey-MCP/run_digikey.sh",
      "env": {
        "CLIENT_ID": "your_actual_client_id",
        "CLIENT_SECRET": "your_actual_secret",
        "USE_SANDBOX": "false"
      }
    }
  }
}
```

### Claude Code

Edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "digikey": {
      "command": "/absolute/path/to/digikey-MCP/run_digikey.sh",
      "env": {
        "CLIENT_ID": "your_actual_client_id",
        "CLIENT_SECRET": "your_actual_secret",
        "USE_SANDBOX": "false"
      }
    }
  }
}
```

**Notes:**
- Replace `/absolute/path/to/` with your actual installation path
- Set `USE_SANDBOX` to `"true"` for testing, `"false"` for production
- Restart Claude after saving configuration
- Verify in Claude Code with `/mcp` command

---

## Available Tools

### 🔍 Search & Discovery
- **`keyword_search`** - Search products with filters (InStock, RoHSCompliant, LeadFree, etc.)
- **`search_manufacturers`** - Browse all manufacturers
- **`search_categories`** - Browse product categories
- **`search_product_substitutions`** - Find alternative parts
- **`get_category_by_id`** - Get category details

### 📦 Product Information
- **`product_details`** - Full specifications and datasheets
- **`get_product_media`** - Images, datasheets, 3D models, videos

### 💰 Pricing & Procurement (Fork Extensions)
- **`get_product_pricing`** - Volume pricing and quantity breaks
- **`get_pricing_by_quantity`** ⭐ - Intelligent pricing optimization (4 scenarios)
- **`get_alternate_packaging`** ⭐ - Compare packaging options (T&R, Cut Tape, etc.)
- **`get_product_associations`** ⭐ - Find mating connectors and support components
- **`get_digi_reel_pricing`** - Custom reel quantities

⭐ = New in this fork

---

## Example Queries

### Basic Usage
```
Search DigiKey for 10kΩ resistors
Find in-stock RoHS-compliant 100µF capacitors
Get detailed specs for part 296-8875-1-ND
```

### Advanced (Fork Features)
```
Compare pricing for 1000 units of ATMEGA328P-PU across packaging options
Find mating connectors for part JST-B2B-XH-A
Show me alternate packaging options for 296-8875-1-ND
```

### BOM Management
```
Check stock and pricing for these parts at qty 100: [part list]
Find substitutes for ATMEGA328P-PU that are in stock
Optimize pricing for my BOM: [part numbers with quantities]
```

---

## Troubleshooting

### Verify Connection
- **Claude Desktop:** Check 🔌 icon (bottom-right) for "digikey" server
- **Claude Code:** Run `/mcp` to see connected servers

### Common Issues

**Server not appearing:**
```bash
# Verify paths and credentials in config file
cat ~/.claude.json  # or ~/Library/Application Support/Claude/claude_desktop_config.json

# Check run script exists
ls -la /path/to/digikey-MCP/run_digikey.sh

# Test manually
export CLIENT_ID="your_id" CLIENT_SECRET="your_secret" USE_SANDBOX="false"
./run_digikey.sh
```

**Authentication errors:**
- Verify `CLIENT_ID` and `CLIENT_SECRET` are correct
- Match `USE_SANDBOX` setting to your credential type (sandbox vs production)
- Regenerate credentials at https://developer.digikey.com/

**Dependencies:**
```bash
cd digikey-MCP
uv sync
```

**Not detecting tools:**
- Restart Claude Desktop/Code after configuration changes
- Try `/mcp reload` in Claude Code

**Debug logs:**
- Claude Code: `claude --debug`
- Claude Desktop: `~/Library/Logs/Claude/`

---

## Context Optimization (Fork Feature)

**Compact mode** (enabled by default) reduces response size by ~90%:
- Returns only essential fields: part numbers, pricing, stock, URLs
- Strips verbose specs and nested objects
- Omits null/empty fields

**Usage:**
```
# Compact mode (default)
Search for 10kΩ resistors

# Full details when needed
Get full specs for part 296-8875-1-ND with compact=False
```

**Best practices:**
- Use specific filters (`manufacturer_id`, `category_id`) over broad searches
- Keep search limits reasonable (5-10 results)
- Request full details only when specifications are needed

---

## API Rate Limits

DigiKey enforces rate limits (more lenient in sandbox). If you hit limits:
- Use more specific queries
- Reduce result limits
- Space out requests
- Consider upgrading your DigiKey developer account

---

## Updating

```bash
cd digikey-MCP
git pull
uv sync
# Restart Claude
```

---

## Resources

- [DigiKey API Docs](https://developer.digikey.com/documentation)
- [MCP Documentation](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code)

---

## License

Licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

This project:
- Uses FastMCP (Apache License 2.0)
- Accesses the DigiKey API under their [Terms of Service](https://developer.digikey.com/terms-and-conditions)
