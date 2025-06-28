# DigiKey MCP Server

A Model Context Protocol (MCP) server for DigiKey's Product Search API using FastMCP.

## Requirements

- Python 3.10+
- DigiKey API credentials (CLIENT_ID and CLIENT_SECRET)

## Setup

### 1. Install dependencies
```bash
pip install fastmcp requests python-dotenv
```

### 2. Set up environment variables
Create a `.env` file in the project root:
```
CLIENT_ID=your_digikey_client_id
CLIENT_SECRET=your_digikey_client_secret
USE_SANDBOX=false
```

Set `USE_SANDBOX=true` to use DigiKey's sandbox environment for testing.

### 3. Run the server
```bash
python digikey_mcp_server.py
```

## Available Tools

### Search Methods
- `keyword_search(keywords, limit=5, manufacturer_id=None, category_id=None, search_options=None, sort_field=None, sort_order="Ascending")` - Search DigiKey products by keyword with sorting and filtering
- `search_manufacturers()` - Get all product manufacturers
- `search_categories()` - Get all product categories
- `search_product_substitutions(product_number, limit=10, search_options=None, exclude_marketplace=False)` - Find substitute products

### Product Details
- `product_details(product_number, manufacturer_id=None, customer_id="0")` - Get detailed product information
- `get_category_by_id(category_id)` - Get specific category details
- `get_product_media(product_number)` - Get product images, documents, and videos
- `get_product_pricing(product_number, customer_id="0", requested_quantity=1)` - Get detailed pricing information
- `get_digi_reel_pricing(product_number, requested_quantity, customer_id="0")` - Get DigiReel pricing

### Sort Options for keyword_search
Available sort fields:
- `Packaging` - Sort by packaging type
- `ProductStatus` - Sort by product status
- `DigiKeyProductNumber` - Sort by DigiKey part number
- `ManufacturerProductNumber` - Sort by manufacturer part number
- `Manufacturer` - Sort by manufacturer name
- `MinimumQuantity` - Sort by minimum order quantity
- `QuantityAvailable` - Sort by available quantity
- `Price` - Sort by price
- `Supplier` - Sort by supplier
- `PriceManufacturerStandardPackage` - Sort by manufacturer standard package price

Sort orders: `Ascending` or `Descending`

### Search Options
Available filters for search methods:
- `LeadFree` - Lead-free products only
- `RoHSCompliant` - RoHS compliant products only
- `InStock` - In-stock products only
- `HasDatasheet` - Products with datasheets
- `HasProductPhoto` - Products with photos
- `Has3DModel` - Products with 3D models
- `NewProduct` - New products only

## Example Usage

The server exposes MCP tools that can be used by MCP clients like Claude Desktop, or programmatically via FastMCP clients.

### Search Examples
```python
# Basic keyword search
keyword_search("resistor", limit=10)

# Search with sorting by price (lowest first)
keyword_search("capacitor", limit=5, sort_field="Price", sort_order="Ascending")

# Search with filters
keyword_search("LED", limit=10, search_options="InStock,RoHSCompliant")

# Get product details
product_details("296-8875-1-ND")

# Get pricing for specific quantity
get_product_pricing("296-8875-1-ND", requested_quantity=100)
```

## Claude Desktop Integration

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "digikey": {
      "command": "python",
      "args": ["/path/to/digikey_mcp_server.py"],
      "cwd": "/path/to/project"
    }
  }
}
``` 