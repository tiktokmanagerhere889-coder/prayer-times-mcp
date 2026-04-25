"""MCP server entry point using stdio transport"""

import asyncio

from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .tools import create_app


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        app = create_app()
        await app.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options=app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
