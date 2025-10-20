# DigiKey MCP Server

A Model Context Protocol (MCP) server for DigiKey's Product Search API using FastMCP. Search for electronic components, get pricing, check stock levels, and access product specifications directly from Claude Desktop or Claude Code.

## 🔐 Security-First Approach

**IMPORTANT:** This setup stores credentials directly in Claude's configuration files. This is the standard approach for MCP servers.

**How it works:**
- You add your `CLIENT_ID` and `CLIENT_SECRET` directly to the config JSON files
- Claude passes these credentials to the MCP server when it starts
- Config files are local to your machine and never committed to git
- Files are protected by your macOS user account permissions

**Never commit API credentials to git repositories.**

---

## 📋 Table of Contents

- [Requirements](#requirements)
- [Getting DigiKey API Credentials](#getting-digikey-api-credentials)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Claude Desktop](#claude-desktop-configuration)
  - [Claude Code](#claude-code-configuration)
- [Available Tools](#available-tools)
- [Example Queries](#example-queries)
- [Troubleshooting](#troubleshooting)

---

## Requirements

- **Python 3.10+**
- **uv package manager** (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **DigiKey API credentials** (CLIENT_ID and CLIENT_SECRET)
- **Claude Desktop** or **Claude Code**

---

## Getting DigiKey API Credentials

1. **Visit the DigiKey Developer Portal:**

   https://developer.digikey.com/

2. **Create an Account or Sign In**
   - Click "Sign In" or "Get Started"
   - Use your existing DigiKey account or create a new one

3. **Create a New Application:**
   - Navigate to "My Apps" or "Applications"
   - Click "Create New Application"
   - Fill in the application details:
     - **Application Name:** Something like "Claude MCP Integration"
     - **Description:** "MCP server for Claude Desktop/Code"
     - **Redirect URI:** Can use `http://localhost` (not used for client credentials flow)
     - **API Access:** Select "Product Search API"

4. **Get Your Credentials:**
   - After creating the app, you'll receive:
     - **CLIENT_ID** - Your application's client identifier
     - **CLIENT_SECRET** - Your application's secret key (keep this secure!)

5. **Choose Your Environment:**
   - **Sandbox** (for testing): Free, with test data
   - **Production**: Real DigiKey inventory and pricing

---

## Installation

### 1. Clone and Set Up the Repository

The repository should already be cloned. If not:

```bash
cd /Users/jb/Auto-Deploy-Everything/digikey-MCP
```

### 2. Install Dependencies

Install Python dependencies using uv:

```bash
uv sync
```

This creates a virtual environment (`.venv`) and installs all required packages.

### 3. Verify the Run Script

The `run_digikey.sh` script should already be executable:

```bash
chmod +x run_digikey.sh
```

---

## Configuration

### Claude Desktop Configuration

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the DigiKey MCP server to your existing configuration:

```json
{
  "mcpServers": {
    "digikey": {
      "command": "/Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh",
      "env": {
        "CLIENT_ID": "your_actual_client_id_here",
        "CLIENT_SECRET": "your_actual_secret_here",
        "USE_SANDBOX": "false"
      }
    }
  }
}
```

**To add your credentials:**

1. Open the config file:
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Find the "digikey" section and replace the placeholder text with your actual credentials:
   - Change `YOUR_DIGIKEY_CLIENT_ID_HERE` to your actual CLIENT_ID
   - Change `YOUR_DIGIKEY_CLIENT_SECRET_HERE` to your actual CLIENT_SECRET
   - These are plain text values in the JSON file

3. Set `USE_SANDBOX`:
   - `"false"` for production (real DigiKey inventory and pricing)
   - `"true"` for sandbox (test environment with fake data)

4. **Save the file and restart Claude Desktop** to load the new configuration

### Claude Code Configuration

**File:** `~/.claude.json`

The configuration file should already exist. To add your credentials:

1. Add the DigiKey server to the `mcpServers` section in your `~/.claude.json` file:
   ```json
   {
     "mcpServers": {
       "digikey": {
         "command": "/Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh",
         "env": {
           "CLIENT_ID": "your_actual_client_id_here",
           "CLIENT_SECRET": "your_actual_secret_here",
           "USE_SANDBOX": "false"
         }
       }
     }
   }
   ```

   - Change `your_actual_client_id_here` to your actual CLIENT_ID
   - Change `your_actual_secret_here` to your actual CLIENT_SECRET
   - These are plain text strings in the JSON file
   - **Note:** Your `~/.claude.json` may already have other MCP servers configured (like GitHub). Simply add the `digikey` entry to the existing `mcpServers` object.

2. **Save the file, then restart Claude Code** and verify with `/mcp` command

---

## Available Tools

The DigiKey MCP server exposes the following tools to Claude:

### Search Methods

#### `keyword_search`
Search DigiKey products by keyword with advanced filtering and sorting.

**Parameters:**
- `keywords` (string) - Search terms or part numbers
- `limit` (int, default: 5) - Maximum results
- `manufacturer_id` (string, optional) - Filter by manufacturer
- `category_id` (string, optional) - Filter by category
- `search_options` (string, optional) - Comma-separated filters:
  - `LeadFree` - Lead-free products only
  - `RoHSCompliant` - RoHS compliant products
  - `InStock` - In-stock products only
  - `HasDatasheet` - Products with datasheets
  - `HasProductPhoto` - Products with photos
  - `Has3DModel` - Products with 3D models
  - `NewProduct` - New products only
- `sort_field` (string, optional) - Sort by field:
  - `Price`, `QuantityAvailable`, `Manufacturer`, `DigiKeyProductNumber`, etc.
- `sort_order` (string, default: "Ascending") - `Ascending` or `Descending`

#### `search_manufacturers`
Get all product manufacturers.

#### `search_categories`
Get all product categories.

#### `search_product_substitutions`
Find substitute products for a given part.

**Parameters:**
- `product_number` (string) - The product to find substitutes for
- `limit` (int, default: 10)
- `search_options` (string, optional) - Filters
- `exclude_marketplace` (bool, default: false)

### Product Details

#### `product_details`
Get detailed information for a specific product.

**Parameters:**
- `product_number` (string) - DigiKey or manufacturer part number
- `manufacturer_id` (string, optional)
- `customer_id` (string, default: "0")

#### `get_category_by_id`
Get specific category details by ID.

#### `get_product_media`
Get product images, documents, datasheets, and videos.

#### `get_product_pricing`
Get detailed pricing information including volume pricing.

**Parameters:**
- `product_number` (string)
- `customer_id` (string, default: "0")
- `requested_quantity` (int, default: 1)

#### `get_digi_reel_pricing`
Get DigiReel pricing for custom reel quantities.

---

## Example Queries

Try these queries with Claude Desktop or Claude Code once the MCP server is configured:

### Basic Search
```
Search DigiKey for 10kΩ resistors
```

### Filtered Search
```
Find in-stock RoHS-compliant capacitors with 100µF capacitance
```

### Price Comparison
```
Search for Arduino-compatible microcontrollers and sort by price ascending
```

### Product Details
```
Get detailed specifications for DigiKey part number 296-8875-1-ND
```

### Pricing for Quantity
```
What's the pricing for 1000 units of part 296-8875-1-ND?
```

### Find Substitutes
```
Find substitute products for part number ATMEGA328P-PU
```

### Component Sourcing
```
I need an op-amp with rail-to-rail output, single supply, and in stock. Find options.
```

### Bill of Materials (BOM) Help
```
I have a BOM with these part numbers: [list]. Check stock and pricing for quantities of 100.
```

---

## Troubleshooting

### Verify MCP Server is Connected

**In Claude Desktop:**
- Look for the 🔌 icon in the bottom-right corner
- Click it to see connected MCP servers
- "digikey" should appear in the list

**In Claude Code:**
- Run the command: `/mcp`
- You should see "digikey" listed with its available tools
- Check the status (should be "connected" or "enabled")

### Common Issues

#### 1. **MCP Server Not Appearing**

**Check Claude Desktop config:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Check Claude Code config:**
```bash
python3 -c "import json; f=open('${HOME}/.claude.json'); data=json.load(f); print(json.dumps(data.get('mcpServers', {}), indent=2))"
```

**Verify absolute paths are correct and the run script exists:**
```bash
ls -la /Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh
```

#### 2. **"Required environment variables are not set" Error**

This means credentials aren't being passed correctly.

**Solution:** Open the config file and ensure `CLIENT_ID` and `CLIENT_SECRET` are filled in with your actual credentials (not the placeholder text).

#### 3. **OAuth/Authentication Errors**

**Common causes:**
- Invalid CLIENT_ID or CLIENT_SECRET
- Using sandbox credentials with `USE_SANDBOX=false` (or vice versa)
- Credentials expired or revoked

**Solution:**
- Double-check credentials from https://developer.digikey.com/
- Verify `USE_SANDBOX` matches your credential type
- Regenerate credentials if needed

#### 4. **"Server Not Responding" or Timeout Errors**

**Check if uv is installed:**
```bash
which uv
```

**Test the server manually:**
```bash
# Set credentials temporarily
export CLIENT_ID="your_id_here"
export CLIENT_SECRET="your_secret_here"
export USE_SANDBOX="false"

# Run the script
/Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh
```

You should see:
```
SUCCESS: Environment variables are set
  CLIENT_ID: your_clien...
  USE_SANDBOX: false (production mode)

Starting DigiKey MCP server...
=== STARTING DIGIKEY MCP SERVER ===
...
```

Press Ctrl+C to stop.

#### 5. **Dependencies Not Installed**

**Reinstall dependencies:**
```bash
cd /Users/jb/Auto-Deploy-Everything/digikey-MCP
uv sync
```

#### 6. **Can't Find DigiKey Tools in Claude**

After configuring, you may need to:
- **Claude Desktop:** Fully quit and restart the app
- **Claude Code:** Run `/mcp reload` or restart Claude Code

Then try a simple query like:
```
Search DigiKey for resistors
```

Claude should automatically use the `keyword_search` tool.

### Debug Mode

To see detailed logs:

**Claude Code:**
```bash
claude --debug
```

**Claude Desktop:**
- Check logs at: `~/Library/Logs/Claude/`

---

## Context Optimization

The MCP server includes built-in context optimization to prevent flooding Claude with large responses:

### Automatic Limits
- **Search results:** Max 50 products (default: 5)
- **Manufacturers/Categories:** Max 500 items (default: 100)
- **Substitutions:** Max 50 products (default: 10)
- **Media items:** Max 50 per type (default: 10)

### Compact Mode
Most search tools include a `compact` parameter (default: `True`) that returns only essential fields:
- Part numbers and manufacturer
- Description and pricing
- Stock availability and URLs
- Excludes verbose specifications and nested objects
- Automatically omits null/empty fields to save tokens

**Enable compact mode** (default for searches):
```
Search for 10kΩ resistors
```

**Disable for full details when needed**:
```
Search for 10kΩ resistors with compact=False
Get full details for part 296-8875-1-ND with compact=False
```

### Best Practices
1. Use compact mode for general searches (enabled by default)
2. Use specific filters (`manufacturer_id`, `category_id`) instead of browsing all
3. Request full details only when specifications are needed
4. Keep search limits reasonable (5-10 for most queries)

## API Rate Limits

DigiKey's API has rate limits:
- **Sandbox:** More lenient, for testing
- **Production:** Limits vary by account type

If you hit rate limits, consider:
- Reducing search result `limit` parameters
- Using more specific search queries
- Spacing out requests
- Upgrading your DigiKey developer account

---

## Updating the Server

To update to the latest version:

```bash
cd /Users/jb/Auto-Deploy-Everything/digikey-MCP
git pull
uv sync
```

Then restart Claude Desktop or Claude Code.

---

## Security Best Practices

✅ **DO:**
- Store credentials in local config files
- Keep `CLIENT_SECRET` private
- Use `.gitignore` to exclude config files from git
- Regenerate credentials if compromised

❌ **DON'T:**
- Commit credentials to git repositories
- Share your `CLIENT_SECRET` publicly
- Store credentials in `.env` files in the project directory
- Hardcode credentials in source code

---

## Support

- **DigiKey API Docs:** https://developer.digikey.com/documentation
- **MCP Documentation:** https://modelcontextprotocol.io
- **FastMCP:** https://github.com/jlowin/fastmcp
- **Claude Code Docs:** https://docs.claude.com/en/docs/claude-code

---

## License

This project uses the DigiKey API under their terms of service. Please review:
https://developer.digikey.com/terms-and-conditions
