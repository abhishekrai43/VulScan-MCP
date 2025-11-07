import os
import logging
from typing import Dict, Any, List
try:
    from .dep_parser import parse_manifest
    from .cve_fetcher import fetch_cves
except ImportError:
    from dep_parser import parse_manifest
    from cve_fetcher import fetch_cves

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
                fix_data = _generate_fix(dep, osv_vulns, nvd_vulns)
                # Build plain-English summary and remediation steps so the calling UI/LLM
                # doesn't need to generate them and we keep format consistent.
                what_text = _summarize_vulnerability(osv_vulns, nvd_vulns, dep.get("name", "package"))
                remediation = _build_remediation_list(fix_data, osv_vulns, nvd_vulns)

                vulnerabilities.append({
                    "name": dep.get("name"),
                    "version": dep.get("version"),
                    "osv_count": len(osv_vulns),
                    "nvd_count": len(nvd_vulns),
                    "osv_vulns": osv_vulns,  # include all fetched OSV entries
                    "nvd_vulns": nvd_vulns,  # include all fetched NVD entries
                    "severity": _get_severity(osv_vulns, nvd_vulns),
                    "fix": fix_data,
                    "what": what_text,
                    "remediation_steps": remediation
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

def _generate_fix(dep: Dict, osv_vulns: List, nvd_vulns: List) -> Dict[str, Any]:
    """Generate fix recommendations based on vulnerabilities."""
    fixes: List[str] = []
    is_version_upgrade = False

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
                            is_version_upgrade = True
                            break

    if not fixes:
        fixes.append("Review vulnerability details and update to latest secure version")

    return {
        "fix_type": "version_upgrade" if is_version_upgrade else "manual_review",
        "steps": fixes
    }


def _summarize_vulnerability(osv_vulns: List, nvd_vulns: List, pkg: str) -> str:
    """Create a short, plain-English summary of what the vulnerability does."""
    # Prefer OSV summary if present
    summary = ""
    if osv_vulns:
        s = osv_vulns[0].get("summary", "").strip()
        if s:
            summary = s

    # Otherwise fall back to NVD description
    if not summary and nvd_vulns:
        desc = nvd_vulns[0].get("cve", {}).get("descriptions", [{}])[0].get("value", "").strip()
        summary = desc

    if not summary:
        return f"A vulnerability was reported for {pkg}. Review CVE details for more information."

    # Simplify wording a bit for readability
    summary = summary.replace("An issue was discovered in", f"A security issue exists in {pkg} that")
    summary = summary.replace("allows", "lets attackers")
    summary = summary.replace("attacker", "attacker/hacker")
    summary = summary.replace("attackers to", "hackers to")
    # Trim to a reasonable length
    summary = summary.replace("\n", " ").strip()
    if len(summary) > 600:
        summary = summary[:600].rsplit(" ", 1)[0] + "..."
    return summary


def _build_remediation_list(fix_data: Dict[str, Any], osv_vulns: List, nvd_vulns: List) -> List[str]:
    """Normalize and expand remediation guidance into a numbered list of steps."""
    steps: List[str] = []
    if not fix_data:
        return ["Review vulnerability details and update to a secure version"]

    raw_steps = fix_data.get("steps", []) if isinstance(fix_data.get("steps", []), list) else [fix_data.get("steps", "Review and remediate")]
    # Copy raw steps
    for s in raw_steps:
        steps.append(s)

    # If version upgrade, prepend explicit warning and append test/staging guidance
    if fix_data.get("fix_type") == "version_upgrade":
        warning = "WARNING: This fix requires a version upgrade. This may introduce breaking changes. Test thoroughly in a staging environment before deploying to production."
        # Ensure warning is first
        if not steps or steps[0] != warning:
            steps.insert(0, warning)

        # Append common best-practices if not already present
        if not any("Run full test suite" in s for s in steps):
            steps.append("Run full test suite")
        if not any("Deploy to staging" in s for s in steps):
            steps.append("Deploy to staging and monitor")

    return steps
