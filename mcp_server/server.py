#!/usr/bin/env python3
# E:\VulScan-MCP\mcp_server.py
"""
MCP server for VulScan-MCP using newline-delimited JSON (NDJSON)
VS Code sends messages as single JSON lines, not framed with Content-Length headers.
"""

import sys
import os
import json
import logging
import traceback
import time
from typing import Any, Dict

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# import your scanner function
try:
    repo_root = os.path.abspath(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from mcp_server.vuln_scanner import scan_repo
except Exception:
    scan_repo = None

# configure logging -> stderr
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("vulscan-mcp")

def send_message(obj: Dict[str, Any]):
    """Write newline-delimited JSON message to stdout."""
    try:
        line = json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n'
        sys.stdout.write(line)
        sys.stdout.flush()
        log.debug("Sent (id=%s)", obj.get("id", "?"))
    except Exception:
        log.exception("Failed to write message to stdout")

def to_markdown(results: Dict[str, Any]) -> str:
    """Convert scan results into Markdown summary."""
    total_deps = results.get("total_dependencies", 0)
    vuln_count = results.get("vulnerable_dependencies", 0)
    vulnerabilities = results.get("vulnerabilities", [])
    manifests = results.get("manifests", {})
    
    # Header
    md = "# VulScan-MCP Vulnerability Report\n\n"
    
    # Summary
    md += "## Summary\n\n"
    md += f"- **Total Dependencies Scanned:** {total_deps}\n"
    md += f"- **Vulnerable Dependencies:** {vuln_count}\n"
    md += f"- **Manifest Files Found:** {len(manifests)}\n\n"
    
    # List manifests
    if manifests:
        md += "### Scanned Files:\n"
        for manifest, path in manifests.items():
            md += f"- `{manifest}` at `{path}`\n"
        md += "\n"
    
    # Vulnerabilities
    if not vulnerabilities:
        md += "## Result\n\n"
        md += "**No known vulnerabilities found!** All dependencies appear to be secure.\n\n"
        md += "_Note: This scan uses NVD and OSV databases. Always keep dependencies updated._\n"
        return md
    
    md += "## Vulnerabilities Found\n\n"
    
    # Group by severity
    critical = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
    high = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
    medium = [v for v in vulnerabilities if v.get("severity") == "MEDIUM"]
    
    if critical:
        md += "### CRITICAL Severity\n\n"
        for vuln in critical:
            md += _format_vulnerability(vuln)
    
    if high:
        md += "### HIGH Severity\n\n"
        for vuln in high:
            md += _format_vulnerability(vuln)
    
    if medium:
        md += "### MEDIUM Severity\n\n"
        for vuln in medium:
            md += _format_vulnerability(vuln)
    
    md += "\n## Recommendations\n\n"
    md += "1. **Prioritize CRITICAL and HIGH severity vulnerabilities**\n"
    md += "2. **Test all updates in a staging environment first**\n"
    md += "3. **Review changelogs before upgrading**\n"
    md += "4. **Run your full test suite after updates**\n"
    md += "5. **Monitor for new vulnerabilities regularly**\n"
    
    return md

def _format_vulnerability(vuln: Dict[str, Any]) -> str:
    """Format a single vulnerability entry."""
    name = vuln.get("name", "Unknown")
    version = vuln.get("version", "Unknown")
    severity = vuln.get("severity", "UNKNOWN")
    fix = vuln.get("fix", "No fix available")
    osv_count = vuln.get("osv_count", 0)
    nvd_count = vuln.get("nvd_count", 0)
    
    md = f"#### {name} @ {version}\n\n"
    md += f"- **Severity:** {severity}\n"
    md += f"- **CVEs Found:** {osv_count} (OSV) + {nvd_count} (NVD)\n"
    md += f"- **Fix:** {fix}\n\n"
    
    return md

def handle_initialize(msg):
    resp = {
        "jsonrpc": "2.0",
        "id": msg.get("id"),
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {}  # Empty dict means server supports tools
            },
            "serverInfo": {
                "name": "VulScan-MCP",
                "version": "1.0.3"
            }
        }
    }
    send_message(resp)
    log.info("Initialize response sent")

def handle_run_action(msg):
    mid = msg.get("id")
    params = msg.get("params", {}) or {}
    # For tools/call, arguments are nested in params.arguments
    arguments = params.get("arguments", params)
    repo_path = arguments.get("repoPath", ".")
    log.info("Request runAction for repoPath=%s", repo_path)
    if not scan_repo:
        err = "Scan functionality unavailable: import of mcp_server.vuln_scanner failed."
        log.error(err)
        send_message({"jsonrpc":"2.0","id":mid,"error":{"code":-32000,"message":err}})
        return

    try:
        results = scan_repo(repo_path)
        chat = to_markdown(results)
        # MCP tools/call expects content as an array of content items
        payload = {
            "content": [
                {
                    "type": "text",
                    "text": chat
                }
            ]
        }
        send_message({"jsonrpc":"2.0","id":mid,"result": payload})
    except Exception as e:
        log.exception("scan_repo failed")
        send_message({"jsonrpc":"2.0","id":mid,"error":{"code":-32001,"message":str(e)}})

def main():
    log.info("vulscan-mcp server starting; cwd=%s pid=%s", os.getcwd(), os.getpid())
    
    try:
        while True:
            # Read one line (newline-delimited JSON)
            line = sys.stdin.readline()
            if not line:
                log.warning("EOF on stdin -> exiting.")
                break

            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                log.error("Invalid JSON: %s", line[:200])
                continue

            log.debug("Received: %s", json.dumps(msg, ensure_ascii=False)[:500])

            method = msg.get("method")
            
            if method == "initialize":
                log.info("Handling initialize")
                handle_initialize(msg)
                continue

            if method == "tools/list":
                log.info("Handling tools/list")
                tools_response = {
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "scan_repo",
                                "description": "Scan repository for security vulnerabilities, CVEs, and vulnerable dependencies. Use this tool when the user asks to: check for vulnerabilities, scan for CVEs, audit dependencies, check security issues, find vulnerable packages, scan for security problems, check package security, audit npm/pip/maven dependencies, find security vulnerabilities, check for known vulnerabilities, scan dependencies for issues, security audit, vulnerability assessment, or check if dependencies are secure. Fetches real-time CVE data from NVD and OSV databases and provides remediation steps.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "repoPath": {
                                            "type": "string",
                                            "description": "Path to the repository to scan (defaults to current directory)",
                                            "default": "."
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
                send_message(tools_response)
                continue

            if method in ("tools/call", "runAction", "mcp.runAction", "action.run"):
                handle_run_action(msg)
                continue

            if method == "shutdown":
                send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": None})
                log.info("Handled shutdown request")
                continue

            # notifications and unknown methods
            if method:
                log.debug("Notification or unknown method received: %s", method)
                if "id" in msg:
                    send_message({"jsonrpc":"2.0","id":msg.get("id"),"error":{"code":-32601,"message":f"Unknown method {method}"}})
                continue

    except Exception:
        log.exception("Unhandled exception in main loop")
    finally:
        log.info("vulscan-mcp server stopping.")

if __name__ == "__main__":
    main()
