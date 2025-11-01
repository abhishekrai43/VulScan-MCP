import os
import logging
from typing import Dict, Any, List
from mcp_server.dep_parser import parse_manifest
from mcp_server.cve_fetcher import fetch_cves

log = logging.getLogger("vulscan-mcp")

SUPPORTED_MANIFESTS = [
    "package.json", "requirements.txt", "pyproject.toml", "Pipfile", "pom.xml", "build.gradle", "go.mod", "Gemfile", "composer.json", ".csproj", "Cargo.toml", "vcpkg.json", "conanfile.txt"
]

def scan_repo(repo_path: str = ".") -> Dict[str, Any]:
    """Scan the repo for supported dependency manifests, fetch CVEs, and return vulnerability report."""
    log.info(f"Scanning repository at: {repo_path}")
    found = {}
    all_deps = []
    
    # Step 1: Find and parse all dependency manifests
    for root, dirs, files in os.walk(repo_path):
        # Skip node_modules, venv, etc.
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build']]
        
        for manifest in SUPPORTED_MANIFESTS:
            if manifest in files:
                path = os.path.join(root, manifest)
                found[manifest] = path
                log.info(f"Found manifest: {path}")
                deps = parse_manifest(path)
                if deps:
                    all_deps.extend(deps)
                    log.info(f"Parsed {len(deps)} dependencies from {manifest}")
    
    log.info(f"Total dependencies found: {len(all_deps)}")
    
    # Step 2: Fetch CVEs for all dependencies
    vulnerabilities = []
    if all_deps:
        log.info("Fetching CVEs from NVD and OSV...")
        cve_results = fetch_cves(all_deps)
        
        # Step 3: Process CVE results and generate remediation
        for cve_data in cve_results.get("cves", []):
            dep = cve_data.get("dependency", {})
            osv_vulns = cve_data.get("osv", [])
            nvd_vulns = cve_data.get("nvd", [])
            
            # Combine vulnerabilities from both sources
            if osv_vulns or nvd_vulns:
                vulnerabilities.append({
                    "name": dep.get("name"),
                    "version": dep.get("version"),
                    "osv_count": len(osv_vulns),
                    "nvd_count": len(nvd_vulns),
                    "osv_vulns": osv_vulns[:3],  # Limit to first 3 for summary
                    "nvd_vulns": nvd_vulns[:3],
                    "severity": _get_severity(osv_vulns, nvd_vulns),
                    "fix": _generate_fix(dep, osv_vulns, nvd_vulns)
                })
    
    log.info(f"Found {len(vulnerabilities)} packages with vulnerabilities")
    
    return {
        "manifests": found,
        "total_dependencies": len(all_deps),
        "vulnerable_dependencies": len(vulnerabilities),
        "vulnerabilities": vulnerabilities
    }

def _get_severity(osv_vulns: List, nvd_vulns: List) -> str:
    """Determine the highest severity from vulnerabilities."""
    # OSV severity check
    for vuln in osv_vulns:
        severity = vuln.get("database_specific", {}).get("severity", "").upper()
        if "CRITICAL" in severity:
            return "CRITICAL"
        if "HIGH" in severity:
            return "HIGH"
    
    # NVD severity check
    for vuln in nvd_vulns:
        metrics = vuln.get("cve", {}).get("metrics", {})
        cvss = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
        severity = cvss.get("baseSeverity", "").upper()
        if severity in ["CRITICAL", "HIGH"]:
            return severity
    
    return "MEDIUM"

def _generate_fix(dep: Dict, osv_vulns: List, nvd_vulns: List) -> str:
    """Generate fix recommendations based on vulnerabilities."""
    fixes = []
    
    # Check OSV for fixed versions
    for vuln in osv_vulns:
        affected = vuln.get("affected", [])
        for aff in affected:
            ranges = aff.get("ranges", [])
            for r in ranges:
                if r.get("type") == "SEMVER":
                    events = r.get("events", [])
                    for event in events:
                        if "fixed" in event:
                            fixes.append(f"Upgrade to version {event['fixed']} or later")
                            break
    
    if fixes:
        return "; ".join(fixes)
    
    return "Review vulnerability details and update to latest secure version"
