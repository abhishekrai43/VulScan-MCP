import requests
import logging
import time
from typing import List, Dict, Any

log = logging.getLogger("vulscan-mcp")

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_API = "https://api.osv.dev/v1/query"

def fetch_cves(dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
    """Fetch CVEs for a list of dependencies using NVD and OSV."""
    results = []
    if not dependencies:
        return {"cves": []}
    
    log.info(f"Fetching CVEs for {len(dependencies)} dependencies...")
    
    for idx, dep in enumerate(dependencies):
        name = dep.get("name")
        version = dep.get("version")
        if not name:
            continue
        
        log.debug(f"[{idx+1}/{len(dependencies)}] Checking {name}@{version}")
        
        # OSV query (more accurate for npm/pypi packages)
        osv_cves = []
        try:
            # Determine ecosystem based on package name patterns
            ecosystem = _detect_ecosystem(name)
            query_payload = {
                "package": {
                    "name": name,
                    "ecosystem": ecosystem
                }
            }
            if version:
                query_payload["version"] = version.strip("^~>=<")
            
            osv_resp = requests.post(OSV_API, json=query_payload, timeout=10)
            if osv_resp.ok:
                osv_cves = osv_resp.json().get("vulns", [])
                if osv_cves:
                    log.info(f"  Found {len(osv_cves)} vulnerabilities in OSV for {name}")
        except Exception as e:
            log.debug(f"  OSV query failed for {name}: {e}")
        
        # NVD query (broader but less accurate)
        nvd_cves = []
        try:
            nvd_resp = requests.get(
                NVD_API, 
                params={"keywordSearch": name},
                timeout=10
            )
            if nvd_resp.ok:
                nvd_cves = nvd_resp.json().get("vulnerabilities", [])
                if nvd_cves:
                    log.info(f"  Found {len(nvd_cves)} vulnerabilities in NVD for {name}")
        except Exception as e:
            log.debug(f"  NVD query failed for {name}: {e}")
        
        results.append({"dependency": dep, "osv": osv_cves, "nvd": nvd_cves})
        
        # Rate limiting to avoid API throttling
        if idx < len(dependencies) - 1:
            time.sleep(0.2)
    
    return {"cves": results}

def _detect_ecosystem(package_name: str) -> str:
    """Detect the package ecosystem based on name patterns."""
    # Angular/npm packages
    if package_name.startswith("@"):
        return "npm"
    # Python packages (common patterns)
    if any(pattern in package_name.lower() for pattern in ["django", "flask", "requests", "numpy", "pandas"]):
        return "PyPI"
    # Default to npm for now (can be enhanced)
    return "npm"
