from typing import Dict, Callable, Any
from mcp_server.vuln_scanner import scan_repo
from mcp_server.cve_fetcher import fetch_cves
from mcp_server.simplify import generate_remediation

def get_tools() -> Dict[str, Callable[..., Any]]:
    return {
        "scan_repo": scan_repo,
        "fetch_cves": fetch_cves,
        "generate_remediation": generate_remediation,
    }
