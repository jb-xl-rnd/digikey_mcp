import os
import json
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# USE_SANDBOX: "true" means use sandbox, "false" or unset means use production
USE_SANDBOX = os.getenv("USE_SANDBOX", "false").lower() == "true"

# DigiKey OAuth2 token endpoint
if USE_SANDBOX:
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    API_BASE = "https://sandbox-api.digikey.com"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    API_BASE = "https://api.digikey.com"

# Initialize FastMCP server
mcp = FastMCP("DigiKey MCP Server")

# Token management with automatic refresh
class TokenManager:
    """Manages OAuth2 token lifecycle with automatic refresh."""

    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
        self.lock = Lock()

    def get_token(self):
        """Get a valid access token, refreshing if necessary."""
        with self.lock:
            # If token is missing or expired (with 5min buffer), refresh it
            if self.access_token is None or self.token_expires_at is None or \
               datetime.now() >= self.token_expires_at - timedelta(minutes=5):
                self._refresh_token()
            return self.access_token

    def _refresh_token(self):
        """Fetch a new access token from DigiKey."""
        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env file")

        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        endpoint = "SANDBOX" if USE_SANDBOX else "PRODUCTION"
        logger.info(f"Requesting token from {endpoint} with CLIENT_ID: {CLIENT_ID[:10]}...")

        resp = requests.post(TOKEN_URL, data=data, headers=headers)

        if resp.status_code != 200:
            logger.error(f"OAuth error: {resp.status_code} - {resp.text}")
            resp.raise_for_status()

        token_data = resp.json()
        self.access_token = token_data["access_token"]

        # DigiKey tokens typically expire in 3600 seconds (1 hour)
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        logger.info(f"Successfully obtained access token (expires in {expires_in}s)")

# Initialize token manager
logger.info("=== STARTING DIGIKEY MCP SERVER ===")
token_manager = TokenManager()
# Get initial token at startup
token_manager.get_token()
logger.info("=== SERVER READY ===")

def _get_headers(customer_id: str = "0"):
    """Get standard headers for DigiKey API requests."""
    return {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "X-DIGIKEY-Customer-Id": customer_id,
    }

def _make_request(method: str, url: str, headers: dict, data: dict = None, retry_count: int = 0) -> dict:
    """Make an API request with error handling, logging, and automatic retry on 401."""
    logger.info(f"Making {method} request to {url}")
    logger.debug(f"Headers: {json.dumps({k: v for k, v in headers.items() if 'Authorization' not in k}, indent=2)}")
    if data:
        logger.debug(f"Request body: {json.dumps(data, indent=2)}")

    if method.upper() == "GET":
        resp = requests.get(url, headers=headers)
    else:
        resp = requests.post(url, headers=headers, json=data)

    logger.info(f"Response status: {resp.status_code}")

    # Handle 401 Unauthorized - token might have expired
    if resp.status_code == 401 and retry_count == 0:
        logger.warning("Got 401 Unauthorized, forcing token refresh and retrying...")
        token_manager.token_expires_at = datetime.now()  # Force refresh
        new_headers = headers.copy()
        new_headers["Authorization"] = f"Bearer {token_manager.get_token()}"
        return _make_request(method, url, new_headers, data, retry_count=1)

    if resp.status_code == 404:
        logger.error(f"API 404 error: {url} not found")
        return {"error": "Not Found", "message": f"Endpoint {url} returned 404. This may be an incorrect part number or unsupported endpoint.", "status_code": 404}

    if resp.status_code != 200:
        logger.error(f"API error: {resp.status_code} - {resp.text}")
        try:
            error_data = resp.json()
            return {"error": "API Error", "message": error_data, "status_code": resp.status_code}
        except:
            return {"error": "API Error", "message": resp.text, "status_code": resp.status_code}

    return resp.json()

def _compact_product(product: dict) -> dict:
    """Extract only essential fields from a product to reduce context usage.

    Omits null/None values to save tokens and improve readability.
    """
    compact = {}

    # Extract ProductStatus - can be a string or object
    product_status = product.get("ProductStatus")
    if isinstance(product_status, dict):
        product_status = product_status.get("Status")

    # Extract DigiKey part number from ProductVariations (usually first variation)
    digikey_part = product.get("DigiKeyPartNumber")
    if not digikey_part and product.get("ProductVariations"):
        variations = product.get("ProductVariations", [])
        if variations and len(variations) > 0:
            digikey_part = variations[0].get("DigiKeyProductNumber")

    # Extract description - can be nested in Description object or at top level
    product_desc = product.get("ProductDescription")
    detailed_desc = product.get("DetailedDescription")
    if not product_desc and isinstance(product.get("Description"), dict):
        product_desc = product.get("Description", {}).get("ProductDescription")
        detailed_desc = product.get("Description", {}).get("DetailedDescription")

    # Extract fields, only include if they have a value
    fields = {
        "DigiKeyPartNumber": digikey_part,
        "ManufacturerPartNumber": product.get("ManufacturerProductNumber") or product.get("ManufacturerPartNumber"),
        "Manufacturer": product.get("Manufacturer", {}).get("Name") if isinstance(product.get("Manufacturer"), dict) else product.get("Manufacturer"),
        "ProductDescription": product_desc,
        "DetailedDescription": detailed_desc,
        "QuantityAvailable": product.get("QuantityAvailable"),
        "UnitPrice": product.get("UnitPrice"),
        "MinimumOrderQuantity": product.get("MinimumOrderQuantity"),
        "Packaging": product.get("Packaging", {}).get("Value") if isinstance(product.get("Packaging"), dict) else product.get("Packaging"),
        "ProductStatus": product_status,
        "ProductUrl": product.get("ProductUrl"),
        "DatasheetUrl": product.get("DatasheetUrl"),
        "PrimaryPhoto": product.get("PrimaryPhoto") or product.get("PhotoUrl"),
        "StandardPricing": product.get("StandardPricing"),
    }

    # Only include fields that have non-null/non-empty values
    # Keep 0 values for quantities/prices (important for out-of-stock items)
    for key, value in fields.items():
        if value is not None and value != "":
            compact[key] = value

    return compact

def _compact_search_result(result: dict, compact: bool = True) -> dict:
    """Reduce search result size by removing verbose fields and null values."""
    if not compact:
        return result

    compact_result = {}

    # Add ProductsCount if present
    if result.get("ProductsCount") is not None:
        compact_result["ProductsCount"] = result.get("ProductsCount")

    # Add ExactManufacturerProductsCount only if not null
    if result.get("ExactManufacturerProductsCount") is not None:
        compact_result["ExactManufacturerProductsCount"] = result.get("ExactManufacturerProductsCount")

    # Compact product list
    if "Products" in result and result["Products"]:
        compact_result["Products"] = [_compact_product(p) for p in result["Products"]]

    return compact_result

def _compact_media_result(result: dict, compact: bool = True) -> dict:
    """Reduce media result size by keeping only essential media info."""
    if not compact:
        return result

    compact_result = {}

    # For each media type, keep only the essential fields
    for media_type in ["Photos", "Documents", "Videos"]:
        if media_type in result and isinstance(result[media_type], list):
            compact_items = []
            for item in result[media_type]:
                compact_item = {
                    "Url": item.get("Url") or item.get("DocumentUrl") or item.get("VideoUrl"),
                    "Description": item.get("Description") or item.get("Title"),
                }
                # Only include type for documents
                if media_type == "Documents" and item.get("DocumentType"):
                    compact_item["Type"] = item.get("DocumentType")
                # Remove None values
                compact_item = {k: v for k, v in compact_item.items() if v is not None}
                compact_items.append(compact_item)
            compact_result[media_type] = compact_items

    return compact_result

@mcp.tool()
def keyword_search(keywords: str, limit: int = 5, manufacturer_id: str = None, category_id: str = None, search_options: str = None, sort_field: str = None, sort_order: str = "Ascending", compact: bool = True):
    """Search DigiKey products by keyword.

    Args:
        keywords: Search terms or part numbers
        limit: Maximum number of results (default: 5, max: 50)
        manufacturer_id: Filter by specific manufacturer ID
        category_id: Filter by specific category ID
        search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
        sort_field: Field to sort by. Options: None, Packaging, ProductStatus, DigiKeyProductNumber, ManufacturerProductNumber, Manufacturer, MinimumQuantity, QuantityAvailable, Price, Supplier, PriceManufacturerStandardPackage
        sort_order: Sort direction - Ascending or Descending (default: Ascending)
        compact: Return compact results with only essential fields to reduce context usage (default: True)
    """
    # Enforce maximum limit to prevent context flooding
    if limit > 50:
        logger.warning(f"Limit {limit} exceeds maximum of 50, capping at 50")
        limit = 50

    url = f"{API_BASE}/products/v4/search/keyword"
    headers = _get_headers()

    body = {
        "Keywords": keywords,
        "Limit": limit
    }

    if manufacturer_id:
        body["ManufacturerId"] = manufacturer_id
    if category_id:
        body["CategoryId"] = category_id
    if search_options:
        body["SearchOptionList"] = search_options.split(",")

    # Add sort options if specified
    if sort_field:
        body["SortOptions"] = {
            "Field": sort_field,
            "SortOrder": sort_order
        }

    result = _make_request("POST", url, headers, body)
    return _compact_search_result(result, compact)

@mcp.tool()
def product_details(product_number: str, manufacturer_id: str = None, customer_id: str = "0", compact: bool = False):
    """Get detailed information for a specific product.

    Args:
        product_number: DigiKey or manufacturer part number
        manufacturer_id: Optional manufacturer ID for disambiguation
        customer_id: Customer ID for pricing (default: "0")
        compact: Return only essential fields to reduce context usage (default: False)

    Note: Use compact=True for general queries. Full details include extensive
    specifications, parameters, and documents which can use significant context.
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productdetails"
    headers = _get_headers(customer_id)

    params = {}
    if manufacturer_id:
        params["manufacturerId"] = manufacturer_id

    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    result = _make_request("GET", url, headers)

    # Check if result has error
    if isinstance(result, dict) and "error" in result:
        return result

    # Check if result is empty or null
    if not result:
        logger.warning(f"Product details returned empty response for {product_number}")
        return {"error": "Empty Response", "message": f"No product details found for {product_number}. Try using the DigiKey part number (format: XXX-XXX-ND) instead of manufacturer part number."}

    if compact and isinstance(result, dict):
        compacted = _compact_product(result)
        # If compaction resulted in empty dict, return full result with warning
        if not compacted or len(compacted) == 0:
            logger.warning(f"Compaction resulted in empty dict, returning full result")
            return result
        return compacted

    return result

@mcp.tool()
def search_manufacturers(limit: int = 100):
    """Search and retrieve product manufacturers.

    Args:
        limit: Maximum number of manufacturers to return (default: 100, max: 500)

    Note: DigiKey has thousands of manufacturers. Use this for general browsing.
    For specific searches, use manufacturer_id filter in keyword_search instead.
    """
    if limit > 500:
        logger.warning(f"Limit {limit} exceeds maximum of 500, capping at 500")
        limit = 500

    url = f"{API_BASE}/products/v4/search/manufacturers"
    headers = _get_headers()
    result = _make_request("GET", url, headers)

    # Limit the results to prevent context overflow
    if isinstance(result, list) and len(result) > limit:
        logger.info(f"Limiting manufacturers from {len(result)} to {limit}")
        result = result[:limit]
    elif isinstance(result, dict) and "Manufacturers" in result and len(result["Manufacturers"]) > limit:
        logger.info(f"Limiting manufacturers from {len(result['Manufacturers'])} to {limit}")
        result["Manufacturers"] = result["Manufacturers"][:limit]

    return result

@mcp.tool()
def search_categories(limit: int = 100):
    """Search and retrieve product categories.

    Args:
        limit: Maximum number of categories to return (default: 100, max: 500)

    Note: DigiKey has thousands of categories. Use this for general browsing.
    For specific searches, use category_id filter in keyword_search instead.
    """
    if limit > 500:
        logger.warning(f"Limit {limit} exceeds maximum of 500, capping at 500")
        limit = 500

    url = f"{API_BASE}/products/v4/search/categories"
    headers = _get_headers()
    result = _make_request("GET", url, headers)

    # Limit the results to prevent context overflow
    if isinstance(result, list) and len(result) > limit:
        logger.info(f"Limiting categories from {len(result)} to {limit}")
        result = result[:limit]
    elif isinstance(result, dict) and "Categories" in result and len(result["Categories"]) > limit:
        logger.info(f"Limiting categories from {len(result['Categories'])} to {limit}")
        result["Categories"] = result["Categories"][:limit]

    return result

@mcp.tool()
def get_category_by_id(category_id: int):
    """Get specific category details by ID.
    
    Args:
        category_id: The category ID to retrieve
    """
    url = f"{API_BASE}/products/v4/search/categories/{category_id}"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def search_product_substitutions(product_number: str, limit: int = 10, search_options: str = None, exclude_marketplace: bool = False, compact: bool = True):
    """Search for product substitutions for a given product.

    Args:
        product_number: The product to get substitutions for
        limit: Number of substitutions (default: 10, max: 50)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)
        compact: Return compact results with only essential fields (default: True)
    """
    if limit > 50:
        logger.warning(f"Limit {limit} exceeds maximum of 50, capping at 50")
        limit = 50

    url = f"{API_BASE}/products/v4/search/{product_number}/substitutions"
    headers = _get_headers()

    params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
    if search_options:
        params["searchOptionList"] = search_options

    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    result = _make_request("GET", url, headers)

    # Apply compaction to substitution results
    if compact and isinstance(result, dict) and "Products" in result:
        result["Products"] = [_compact_product(p) for p in result["Products"]]

    return result

@mcp.tool()
def get_product_media(product_number: str, max_items_per_type: int = 10, compact: bool = True):
    """Get media (images, documents, videos) for a product.

    Args:
        product_number: The product to get media for
        max_items_per_type: Maximum items to return per media type (default: 10, max: 50)
        compact: Return only essential fields (URL, description) to reduce context usage (default: True)

    Note: Products can have dozens of photos, documents, and videos. This limit
    prevents context overflow by capping each media type separately.
    """
    if max_items_per_type > 50:
        logger.warning(f"max_items_per_type {max_items_per_type} exceeds 50, capping at 50")
        max_items_per_type = 50

    url = f"{API_BASE}/products/v4/search/{product_number}/media"
    headers = _get_headers()
    result = _make_request("GET", url, headers)

    # Limit each media type to prevent context bloat
    if isinstance(result, dict):
        for media_type in ["Photos", "Documents", "Videos"]:
            if media_type in result and isinstance(result[media_type], list):
                if len(result[media_type]) > max_items_per_type:
                    logger.info(f"Limiting {media_type} from {len(result[media_type])} to {max_items_per_type}")
                    result[media_type] = result[media_type][:max_items_per_type]

    return _compact_media_result(result, compact)

@mcp.tool()
def get_product_pricing(product_number: str, customer_id: str = "0", requested_quantity: int = 1):
    """Get detailed pricing information for a product.
    
    Args:
        product_number: The product to get pricing for
        customer_id: Customer ID for pricing (default: "0")
        requested_quantity: Quantity for pricing calculation (default: 1)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productpricing"
    headers = _get_headers(customer_id)
    
    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    return _make_request("GET", url, headers)

@mcp.tool()
def get_digi_reel_pricing(product_number: str, requested_quantity: int, customer_id: str = "0"):
    """Get DigiReel pricing for a product.

    Args:
        product_number: DigiKey product number (must be DigiReel compatible)
        requested_quantity: Quantity for DigiReel pricing
        customer_id: Customer ID for pricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/digireelpricing"
    headers = _get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def get_pricing_by_quantity(product_number: str, requested_quantity: int, manufacturer_id: str = None, customer_id: str = "0"):
    """Get intelligent pricing options for a product at a specific quantity.

    Returns up to 4 pricing scenarios: exact quantity, minimum order quantity,
    maximum order quantity, and better value (standard package with lower total cost).
    Essential for BOM cost optimization.

    Args:
        product_number: DigiKey or manufacturer part number
        requested_quantity: Desired quantity for pricing
        manufacturer_id: Optional manufacturer ID for disambiguation (e.g., for common parts like CR2032)
        customer_id: Customer ID for MyPricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/pricingbyquantity/{requested_quantity}"
    headers = _get_headers(customer_id)

    # Add manufacturer ID if provided for disambiguation
    if manufacturer_id:
        url += f"?manufacturerId={manufacturer_id}"

    return _make_request("GET", url, headers)

@mcp.tool()
def get_alternate_packaging(product_number: str, customer_id: str = "0", compact: bool = True):
    """Get alternate packaging options for a product.

    Returns the same product in different packaging types (e.g., Tape & Reel,
    Cut Tape, Tube, Tray, Bulk, Digi-Reel) with pricing for each option.
    Essential for procurement flexibility and cost optimization.

    Args:
        product_number: DigiKey or manufacturer part number
        customer_id: Customer ID for MyPricing (default: "0")
        compact: Return only essential fields to reduce context usage (default: True)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/alternatepackaging"
    headers = _get_headers(customer_id)

    result = _make_request("GET", url, headers)

    # Check for errors
    if isinstance(result, dict) and "error" in result:
        return result

    # Apply compaction to alternate packaging results
    # The API returns nested structure: AlternatePackagings.AlternatePackaging[]
    if compact and isinstance(result, dict):
        if "AlternatePackagings" in result and "AlternatePackaging" in result["AlternatePackagings"]:
            result["AlternatePackagings"]["AlternatePackaging"] = [_compact_product(p) for p in result["AlternatePackagings"]["AlternatePackaging"]]
        elif "AlternatePackagingProducts" in result:
            result["AlternatePackagingProducts"] = [_compact_product(p) for p in result["AlternatePackagingProducts"]]

    return result

@mcp.tool()
def get_product_associations(product_number: str, customer_id: str = "0", compact: bool = True):
    """Get associated products that are commonly used together.

    Returns products that are related or complementary to the queried product.
    Different from substitutions - associations are for mating connectors,
    required support components, etc. Valuable for complete BOM building.

    Args:
        product_number: DigiKey or manufacturer part number
        customer_id: Customer ID for MyPricing (default: "0")
        compact: Return only essential fields to reduce context usage (default: True)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/associations"
    headers = _get_headers(customer_id)

    result = _make_request("GET", url, headers)

    # Check for errors
    if isinstance(result, dict) and "error" in result:
        return result

    # Apply compaction to associations results
    # API returns: ProductAssociations.{Kits, MatingProducts, AssociatedProducts, ForUseWithProducts}
    if compact and isinstance(result, dict) and "ProductAssociations" in result:
        assoc = result["ProductAssociations"]
        for key in ["Kits", "MatingProducts", "AssociatedProducts", "ForUseWithProducts"]:
            if key in assoc and isinstance(assoc[key], list):
                assoc[key] = [_compact_product(p) for p in assoc[key]]

    return result


def main():
    mcp.run()

if __name__ == "__main__":
    main() 