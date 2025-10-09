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

# Check for required environment variables or .env file
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    # Check if .env file exists
    if [ -f "$SCRIPT_DIR/.env" ]; then
        success "Using credentials from .env file"
    else
        error "DigiKey API credentials not found!"
        echo ""
        echo "Credentials should be configured in your Claude config files or .env file."
        echo ""
        echo "📝 For Claude Desktop, edit:"
        echo "   ~/Library/Application Support/Claude/claude_desktop_config.json"
        echo ""
        echo "📝 For Claude Code, edit:"
        echo "   ~/.claude.json"
        echo ""
        echo "Add your credentials to the 'env' section:"
        echo ""
        echo '  "digikey": {'
        echo '    "command": "/path/to/run_digikey.sh",'
        echo '    "env": {'
        echo '      "CLIENT_ID": "your_actual_client_id_here",'
        echo '      "CLIENT_SECRET": "your_actual_secret_here",'
        echo '      "USE_SANDBOX": "false"'
        echo '    }'
        echo '  }'
        echo ""
        echo "Or create a .env file in the project directory:"
        echo "   $SCRIPT_DIR/.env"
        echo ""
        echo "🔑 To get DigiKey API credentials:"
        echo "   1. Visit https://developer.digikey.com/"
        echo "   2. Create an account and sign in"
        echo "   3. Create a new application"
        echo "   4. Copy your CLIENT_ID and CLIENT_SECRET"
        echo ""
        echo "⚠️  SECURITY: Credentials are stored locally and never committed to git."
        echo ""
        exit 1
    fi
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
