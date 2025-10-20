#!/bin/bash

# DigiKey MCP Server Runner
# This script checks for required environment variables and runs the DigiKey MCP server

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to print colored messages (all to stderr for MCP compatibility)
error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}WARNING:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}SUCCESS:${NC} $1" >&2
}

# Check for required environment variables from MCP config
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    error "DigiKey API credentials not found!"
    echo "" >&2
    echo "Credentials must be configured in your Claude config files." >&2
    echo "" >&2
    echo "📝 For Claude Desktop, edit:" >&2
    echo "   ~/Library/Application Support/Claude/claude_desktop_config.json" >&2
    echo "" >&2
    echo "📝 For Claude Code, edit:" >&2
    echo "   ~/.claude.json" >&2
    echo "" >&2
    echo "Add your credentials to the 'env' section of the digikey server:" >&2
    echo "" >&2
    echo '  "digikey": {' >&2
    echo '    "command": "/Users/jb/Auto-Deploy-Everything/digikey-MCP/run_digikey.sh",' >&2
    echo '    "env": {' >&2
    echo '      "CLIENT_ID": "your_actual_client_id_here",' >&2
    echo '      "CLIENT_SECRET": "your_actual_secret_here",' >&2
    echo '      "USE_SANDBOX": "false"' >&2
    echo '    }' >&2
    echo '  }' >&2
    echo "" >&2
    echo "🔑 To get DigiKey API credentials:" >&2
    echo "   1. Visit https://developer.digikey.com/" >&2
    echo "   2. Create an account and sign in" >&2
    echo "   3. Create a new application" >&2
    echo "   4. Copy your CLIENT_ID and CLIENT_SECRET" >&2
    echo "" >&2
    exit 1
fi

# Credentials are set (output to stderr for MCP compatibility)
if [ -n "$CLIENT_ID" ]; then
    success "Environment variables are set"
    echo "  CLIENT_ID: ${CLIENT_ID:0:10}..." >&2
    if [ -n "$USE_SANDBOX" ]; then
        echo "  USE_SANDBOX: $USE_SANDBOX" >&2
    else
        echo "  USE_SANDBOX: false (production mode)" >&2
    fi
    echo "" >&2
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the server using uv (stderr messages won't interfere with JSON-RPC)
echo "Starting DigiKey MCP server..." >&2
exec uv run python digikey_mcp_server.py
