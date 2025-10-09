# DigiKey MCP Server - Quick Reference Card

## 🚀 First-Time Setup

### 1. Get DigiKey Credentials
Visit https://developer.digikey.com/ → Create App → Copy CLIENT_ID & CLIENT_SECRET

### 2. Add Credentials Directly to Config Files

**For Claude Desktop:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**For Claude Code:**
```bash
nano ~/.claude.json
```

**In both files:**
- Find the "digikey" section
- Replace `YOUR_DIGIKEY_CLIENT_ID_HERE` with your actual CLIENT_ID
- Replace `YOUR_DIGIKEY_CLIENT_SECRET_HERE` with your actual CLIENT_SECRET
- These are plain text values stored in the JSON config file

### 3. Restart Claude

**Claude Desktop:** Quit and relaunch the app

**Claude Code:** Restart or run `/mcp reload`

---

## ✅ Verify It's Working

**Claude Desktop:**
- Look for 🔌 icon (bottom-right)
- Click it → "digikey" should be listed

**Claude Code:**
```
/mcp
```
Should show "digikey" with status "connected"

---

## 💬 Example Queries to Try

### Basic Search
```
Search DigiKey for 10kΩ resistors
```

### In-Stock with Filters
```
Find in-stock RoHS-compliant 100µF capacitors
```

### Price Sorting
```
Search for ESP32 modules, sort by price ascending, show 10 results
```

### Product Details
```
Get full specs for DigiKey part 296-8875-1-ND
```

### Volume Pricing
```
What's the price for 500 units of part ATMEGA328P-PU?
```

### Find Alternatives
```
Find substitute products for 2N7002
```

### Component Sourcing
```
I need a 5V LDO voltage regulator with 1A output, in stock
```

### BOM Assistance
```
Check stock levels and pricing for these parts: [list]
```

---

## 🛠 Common Troubleshooting

### Server Not Showing Up?

**Check Config Files:**
```bash
# Claude Desktop
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Claude Code
python3 -c "import json; f=open('${HOME}/.claude.json'); data=json.load(f); print(json.dumps(data.get('mcpServers', {}), indent=2))"
```

**Verify Script Exists:**
```bash
ls -la /Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh
```

### Authentication Errors?

1. Double-check CLIENT_ID and CLIENT_SECRET are correct
2. Verify USE_SANDBOX matches your credential type:
   - `"false"` = Production (real inventory)
   - `"true"` = Sandbox (test environment)
3. Regenerate credentials at https://developer.digikey.com/ if needed

### Server Not Responding?

**Test manually:**
```bash
export CLIENT_ID="your_id"
export CLIENT_SECRET="your_secret"
export USE_SANDBOX="false"
/Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh
```

Should see: `=== STARTING DIGIKEY MCP SERVER ===`

### Tools Not Available in Claude?

1. **Claude Desktop:** Fully quit and restart
2. **Claude Code:** Run `/mcp reload`
3. Try: "Search DigiKey for resistors"

---

## 📝 Available Tools at a Glance

| Tool | Purpose |
|------|---------|
| `keyword_search` | Search products with filters & sorting |
| `product_details` | Get full specs for a part number |
| `get_product_pricing` | Volume pricing for specific quantities |
| `search_manufacturers` | List all manufacturers |
| `search_categories` | List all product categories |
| `get_category_by_id` | Get details for a specific category |
| `search_product_substitutions` | Find alternative parts |
| `get_product_media` | Get datasheets, images, videos |
| `get_digi_reel_pricing` | Custom reel pricing |

---

## 🔑 Configuration File Locations

| App | Config File |
|-----|-------------|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Code** | `~/.claude.json` |

---

## 🔧 Maintenance Commands

**Update Server:**
```bash
cd /Users/jb/Auto-Deploy-Everything/digikey-MCP
git pull
uv sync
```

**Reinstall Dependencies:**
```bash
cd /Users/jb/Auto-Deploy-Everything/digikey-MCP
uv sync
```

**View Debug Logs (Claude Code):**
```bash
claude --debug
```

---

##  🔒 Security Reminders

✅ Credentials are stored locally in config files (not in git)

✅ Config files are protected by your macOS user account

❌ Never commit credentials to git repositories

❌ Never share your CLIENT_SECRET publicly

---

## 📚 Learn More

- **Full Documentation:** `README.md` in project directory
- **DigiKey API Docs:** https://developer.digikey.com/documentation
- **MCP Documentation:** https://modelcontextprotocol.io
- **Claude Code Docs:** https://docs.claude.com/en/docs/claude-code

---

## 🆘 Getting Help

1. Read the full `README.md`
2. Check DigiKey API documentation
3. Verify credentials at https://developer.digikey.com/
4. Test server manually (see "Server Not Responding?" above)

---

**Last Updated:** 2025-10-09
