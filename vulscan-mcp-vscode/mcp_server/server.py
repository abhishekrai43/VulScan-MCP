#!/usr/bin/env python3
"""VulScan-MCP Server using official MCP Python SDK."""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import scanner
try:
    from .vuln_scanner import scan_repo
except ImportError:
    from vuln_scanner import scan_repo

# Configure logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vulscan-mcp")

# Create MCP server
app = Server("VulScan-MCP")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="scan_repo",
            description="Scan repository for security vulnerabilities, CVEs, and vulnerable dependencies. Fetches real-time CVE data from NVD and OSV databases.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repoPath": {
                        "type": "string",
                        "description": "Path to repository (defaults to current directory)",
                        "default": "."
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name != "scan_repo":
        raise ValueError(f"Unknown tool: {name}")
    
    logger.info(f"Scanning repository: {arguments}")
    repo_path = arguments.get("repoPath", ".")
    
    try:
        results = scan_repo(repo_path)
        markdown = to_markdown(results)
        logger.info("Scan completed")
        return [TextContent(type="text", text=markdown)]
    except Exception as e:
        logger.exception(f"Scan error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def to_markdown(results: dict[str, Any]) -> str:
    lines = ["# VulScan-MCP Vulnerability Report\n"]
    lines.append("## Summary")
    lines.append(f"- Total Dependencies: {results.get('total_dependencies', 0)}")
    lines.append(f"- Vulnerable: {results.get('vulnerable_dependencies', 0)}\n")
    
    vulnerabilities = results.get("vulnerabilities", [])
    if vulnerabilities:
        lines.append("## Vulnerabilities\n")
        for vuln in vulnerabilities:
            pkg = vuln.get("package", "unknown")
            ver = vuln.get("version", "unknown")
            sev = vuln.get("severity", "UNKNOWN")
            fix = vuln.get("fix", "No fix available")
            lines.append(f"### {pkg} @ {ver}")
            lines.append(f"- **Severity:** {sev}")
            lines.append(f"- **Fix:** {fix}\n")
    else:
        lines.append("## ✅ No Vulnerabilities Found\n")
    
    return "\n".join(lines)


async def serve():
    """Run the MCP server using stdio transport"""
    logger.info("Starting VulScan-MCP server")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
    logger.info("VulScan-MCP server stopped")


if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
