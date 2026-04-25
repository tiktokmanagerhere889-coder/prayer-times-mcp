"""Entry point for running the MCP server as a module."""

import asyncio
import sys

from prayer_times_mcp.server import main as server_main

if __name__ == "__main__":
    sys.exit(asyncio.run(server_main()))
