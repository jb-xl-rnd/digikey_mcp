# DigiKey MCP Server Extension Plan

This document provides a comprehensive analysis of the current DigiKey MCP server implementation and recommendations for extending it with additional API endpoints.

## Table of Contents
1. [Current Implementation Summary](#current-implementation-summary)
2. [Available API Endpoints](#available-api-endpoints)
3. [Missing Features Analysis](#missing-features-analysis)
4. [Implementation Recommendations](#implementation-recommendations)
5. [Code Examples](#code-examples)

---

## Current Implementation Summary

The current implementation at `digikey_mcp_server.py` includes **10 MCP tools** that wrap **9 DigiKey API endpoints**:

### Implemented Tools

1. **`keyword_search`** - POST /search/keyword
   - Search products by keywords, part numbers, with filtering options
   - Supports manufacturer/category filtering, search options, sorting

2. **`product_details`** - GET /search/{productNumber}/productdetails
   - Get detailed information for a specific product
   - Returns MyPricing if applicable

3. **`search_manufacturers`** - GET /search/manufacturers
   - Retrieve all product manufacturers
   - Used for filtering keyword searches

4. **`search_categories`** - GET /search/categories
   - Retrieve all product categories
   - Used for filtering keyword searches

5. **`get_category_by_id`** - GET /search/categories/{categoryId}
   - Get specific category details by ID

6. **`search_product_substitutions`** - GET /search/{productNumber}/substitutions
   - Find substitution products for a given part
   - Supports filtering and marketplace exclusion

7. **`get_product_media`** - GET /search/{productNumber}/media
   - Retrieve images, documents, videos for a product

8. **`get_product_pricing`** - GET /search/{productNumber}/pricing
   - Get detailed pricing information
   - Supports pagination and stock filtering
   - Returns MyPricing if applicable

9. **`get_digi_reel_pricing`** - GET /search/{productNumber}/digireelpricing
   - Get DigiReel pricing for specific quantities

### Implementation Quality
- Clean architecture with FastMCP framework
- OAuth2 token management
- Consistent error handling and logging
- Proper header management for locale/currency/customer ID
- Sandbox/production environment switching

---

## Available API Endpoints

The DigiKey Product Search API v4 provides **14 total endpoints**. Here's the complete list:

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| /search/keyword | POST | ✅ Implemented | - |
| /search/{productNumber}/productdetails | GET | ✅ Implemented | - |
| /search/manufacturers | GET | ✅ Implemented | - |
| /search/categories | GET | ✅ Implemented | - |
| /search/categories/{categoryId} | GET | ✅ Implemented | - |
| /search/{productNumber}/digireelpricing | GET | ✅ Implemented | - |
| /search/{productNumber}/substitutions | GET | ✅ Implemented | - |
| /search/{productNumber}/media | GET | ✅ Implemented | - |
| /search/{productNumber}/pricing | GET | ✅ Implemented | - |
| **/search/{productNumber}/pricingbyquantity/{requestedQuantity}** | GET | ❌ Missing | **HIGH** |
| **/search/{productNumber}/alternatepackaging** | GET | ❌ Missing | **HIGH** |
| **/search/{productNumber}/associations** | GET | ❌ Missing | **MEDIUM** |
| **/search/{productNumber}/recommendedproducts** | GET | ❌ Missing | **MEDIUM** |
| /search/packagetypebyquantity/{productNumber} | GET | ❌ Missing | LOW (Deprecated) |

---

## Missing Features Analysis

### HIGH PRIORITY Features

#### 1. GET /search/{productNumber}/pricingbyquantity/{requestedQuantity}

**Why It's Critical:**
- Provides intelligent pricing options based on requested quantity
- Returns up to 4 pricing scenarios:
  - **Exact**: Price for exact quantity requested
  - **MinimumOrderQuantity**: Price if quantity increased to MOQ
  - **MaxOrderQuantity**: Price if quantity reduced to max
  - **BetterValue**: Price for standard package quantity with lower total cost
- Essential for BOM cost optimization
- Shows MyPricing if applicable

**Use Cases:**
- Optimizing component quantities for best unit price
- Identifying quantity breaks that reduce total cost
- BOM cost analysis and procurement planning
- Finding manufacturer standard package deals

**Implementation Difficulty:** Easy (15-20 lines, follows existing pattern)

**Parameters:**
- `productNumber` (path, required): DigiKey or manufacturer part number
- `requestedQuantity` (path, required): Desired quantity
- `manufacturerId` (query, optional): For disambiguating common parts
- `customer_id` (standard header): For MyPricing

---

#### 2. GET /search/{productNumber}/alternatepackaging

**Why It's Critical:**
- Returns same product in different packaging options
- Essential for procurement flexibility and cost optimization
- Common packaging types: Tape & Reel, Cut Tape, Tube, Tray, Bulk, Digi-Reel

**Use Cases:**
- Finding lower-cost packaging alternatives
- Matching packaging to assembly equipment requirements
- Volume purchasing decisions
- Comparing packaging-specific pricing

**Implementation Difficulty:** Easy (10-15 lines, follows existing pattern)

**Parameters:**
- `productNumber` (path, required): DigiKey or manufacturer part number
- `customer_id` (standard header): For MyPricing

---

### MEDIUM PRIORITY Features

#### 3. GET /search/{productNumber}/associations

**Why It's Valuable:**
- Returns products commonly used together
- Different from substitutions (direct replacements)
- Helps discover complementary components

**Use Cases:**
- Finding mating connectors
- Discovering required support components
- Building complete solutions from single parts
- Design reference and recommendations

**Implementation Difficulty:** Easy (10-15 lines, follows existing pattern)

**Parameters:**
- `productNumber` (path, required): DigiKey or manufacturer part number
- `customer_id` (standard header): For MyPricing

---

#### 4. GET /search/{productNumber}/recommendedproducts

**Why It's Valuable:**
- Provides AI/algorithm-based product recommendations
- Cross-selling and upselling opportunities
- Helps users discover alternatives they might not find otherwise

**Use Cases:**
- Exploring alternative solutions
- Finding newer/better versions of parts
- Price/performance optimization
- Discovering parts with better availability

**Implementation Difficulty:** Easy (15-20 lines, follows existing pattern)

**Parameters:**
- `productNumber` (path, required): DigiKey or manufacturer part number
- `limit` (query, optional): Number of recommendations (default: 1)
- `searchOptionList` (query, optional): Filters like InStock, RoHSCompliant
- `excludeMarketPlaceProducts` (query, optional): Exclude marketplace

---

### LOW PRIORITY Features

#### 5. GET /search/packagetypebyquantity/{productNumber}

**Status:** DEPRECATED by DigiKey
**Replacement:** Use `pricingbyquantity` endpoint instead
**Recommendation:** Do not implement - functionality covered by endpoint #1

---

## Implementation Recommendations

### Top 3 Features to Add (in priority order)

1. **`get_pricing_by_quantity`** - Critical for cost optimization
2. **`get_alternate_packaging`** - Essential for procurement flexibility
3. **`get_product_associations`** - Valuable for complete BOM building

### Why These Three?
- All follow the existing simple GET pattern (easy implementation)
- Provide maximum value for electronic component selection workflows
- Complement existing functionality perfectly
- Cover the most common BOM management use cases

---

## Code Examples

### 1. Implementation: get_pricing_by_quantity

```python
@mcp.tool()
def get_pricing_by_quantity(product_number: str, requested_quantity: int, manufacturer_id: str = None, customer_id: str = "0"):
    """Get intelligent pricing options for a product at a specific quantity.

    Returns up to 4 pricing scenarios: exact quantity, minimum order quantity,
    maximum order quantity, and better value (standard package with lower total cost).

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
```

**Example Usage:**
```python
# Find best pricing for 1000 units
result = get_pricing_by_quantity("296-1086-1-ND", 1000)

# With manufacturer disambiguation
result = get_pricing_by_quantity("CR2032", 500, manufacturer_id="658")
```

**Example Response Structure:**
```json
{
  "Product": {...},
  "PricingOptions": {
    "Exact": {
      "Quantity": 1000,
      "UnitPrice": 0.15,
      "TotalPrice": 150.00
    },
    "BetterValue": {
      "Quantity": 1500,
      "UnitPrice": 0.12,
      "TotalPrice": 180.00,
      "Savings": "Standard package - better unit price"
    }
  }
}
```

**Implementation Difficulty:** ⭐ Easy
**Lines of Code:** ~15
**Value for BOM Work:** ⭐⭐⭐⭐⭐ Critical

---

### 2. Implementation: get_alternate_packaging

```python
@mcp.tool()
def get_alternate_packaging(product_number: str, customer_id: str = "0"):
    """Get alternate packaging options for a product.

    Returns the same product in different packaging types (e.g., Tape & Reel,
    Cut Tape, Tube, Tray, Bulk, Digi-Reel) with pricing for each option.

    Args:
        product_number: DigiKey or manufacturer part number
        customer_id: Customer ID for MyPricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/alternatepackaging"
    headers = _get_headers(customer_id)

    return _make_request("GET", url, headers)
```

**Example Usage:**
```python
# Find all packaging options for a resistor
result = get_alternate_packaging("311-10.0KHRCT-ND")

# With customer pricing
result = get_alternate_packaging("311-10.0KHRCT-ND", customer_id="12345")
```

**Example Response Structure:**
```json
{
  "Product": {...},
  "AlternatePackaging": [
    {
      "DigiKeyPartNumber": "311-10.0KHRCT-ND",
      "PackageType": "Cut Tape (CT)",
      "MinimumOrderQuantity": 1,
      "StandardPricing": [...]
    },
    {
      "DigiKeyPartNumber": "311-10.0KHRTR-ND",
      "PackageType": "Tape & Reel (TR)",
      "MinimumOrderQuantity": 5000,
      "StandardPricing": [...]
    }
  ]
}
```

**Implementation Difficulty:** ⭐ Easy
**Lines of Code:** ~12
**Value for BOM Work:** ⭐⭐⭐⭐⭐ Critical

---

### 3. Implementation: get_product_associations

```python
@mcp.tool()
def get_product_associations(product_number: str, customer_id: str = "0"):
    """Get associated products that are commonly used together.

    Returns products that are related or complementary to the queried product.
    Different from substitutions - associations are for mating connectors,
    required support components, etc.

    Args:
        product_number: DigiKey or manufacturer part number
        customer_id: Customer ID for MyPricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/associations"
    headers = _get_headers(customer_id)

    return _make_request("GET", url, headers)
```

**Example Usage:**
```python
# Find mating connector for a connector
result = get_product_associations("WM2902-ND")

# Find support components for a microcontroller
result = get_product_associations("ATMEGA328P-PU-ND")
```

**Example Response Structure:**
```json
{
  "Product": {...},
  "Associations": [
    {
      "AssociationType": "Mating Product",
      "Products": [...]
    },
    {
      "AssociationType": "For Use With",
      "Products": [...]
    }
  ]
}
```

**Implementation Difficulty:** ⭐ Easy
**Lines of Code:** ~12
**Value for BOM Work:** ⭐⭐⭐⭐ High

---

### 4. Implementation: get_recommended_products

```python
@mcp.tool()
def get_recommended_products(product_number: str, limit: int = 5, search_options: str = None, exclude_marketplace: bool = False):
    """Get recommended alternative products.

    Returns AI/algorithm-based product recommendations based on the queried product.
    Useful for finding alternatives, newer versions, or better value options.

    Args:
        product_number: DigiKey or manufacturer part number
        limit: Number of recommendations to return (default: 5)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/recommendedproducts"
    headers = _get_headers()

    params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
    if search_options:
        params["searchOptionList"] = search_options

    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)
```

**Example Usage:**
```python
# Get 5 recommended alternatives
result = get_recommended_products("296-1086-1-ND", limit=5)

# Get in-stock recommendations only
result = get_recommended_products("296-1086-1-ND", search_options="InStock", limit=10)
```

**Example Response Structure:**
```json
{
  "Product": {...},
  "RecommendedProducts": [
    {
      "Product": {...},
      "ReasonForRecommendation": "Similar specifications, better availability"
    }
  ]
}
```

**Implementation Difficulty:** ⭐ Easy
**Lines of Code:** ~15
**Value for BOM Work:** ⭐⭐⭐ Medium

---

## Implementation Priority Matrix

| Feature | Difficulty | Value | Priority | LOC | Time |
|---------|-----------|-------|----------|-----|------|
| get_pricing_by_quantity | Easy | Critical | HIGH | ~15 | 10 min |
| get_alternate_packaging | Easy | Critical | HIGH | ~12 | 10 min |
| get_product_associations | Easy | High | MEDIUM | ~12 | 10 min |
| get_recommended_products | Easy | Medium | MEDIUM | ~15 | 10 min |

**Total Implementation Time:** ~40 minutes for all 4 features

---

## Testing Recommendations

### Test Cases for New Features

1. **get_pricing_by_quantity:**
   - Test with DigiKey part number
   - Test with manufacturer part number + manufacturerId
   - Test various quantities (below MOQ, above MOQ, at quantity breaks)
   - Verify all 4 pricing options are returned when applicable

2. **get_alternate_packaging:**
   - Test with products known to have multiple packaging options
   - Test with products having only one packaging option
   - Verify pricing differences between package types

3. **get_product_associations:**
   - Test with connectors (should return mating connectors)
   - Test with ICs (should return support components)
   - Test with products having no associations

4. **get_recommended_products:**
   - Test with various limit values
   - Test with different search_options filters
   - Test exclude_marketplace parameter

---

## Conclusion

The DigiKey MCP server has excellent foundation with 9/14 endpoints implemented. Adding the 4 recommended features would:

1. **Increase API coverage to 93%** (13/14 endpoints, excluding deprecated)
2. **Provide complete BOM management capabilities**
3. **Enable advanced cost optimization workflows**
4. **Require minimal development effort** (~40 minutes total)

All recommended features follow existing patterns and can be implemented with high confidence of success.

### Next Steps

1. Implement `get_pricing_by_quantity` first (highest value)
2. Implement `get_alternate_packaging` second (complements pricing)
3. Implement `get_product_associations` third (BOM completion)
4. Optionally implement `get_recommended_products` (discovery/exploration)

Each implementation should include:
- Proper error handling (already in `_make_request`)
- Logging (already configured)
- FastMCP tool decorator with clear docstring
- Parameter validation as needed
