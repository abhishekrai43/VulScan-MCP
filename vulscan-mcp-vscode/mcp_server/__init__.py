# E:\VulScan-MCP\mcp_server\__init__.py
import asyncio
from .server import serve

def main():
    """Entry point for the MCP server - calls async serve() function"""
    asyncio.run(serve())

__all__ = ["main"]
