from typing import Dict, Any

def generate_remediation(cve: Dict[str, Any], dependency: Dict[str, str]) -> Dict[str, Any]:
    """
    Given a CVE and dependency, return step-by-step mitigation instructions.
    If a version upgrade is required, prepend the warning and append best practices.
    """
    fix_type = cve.get("fix_type")  # e.g., "version_upgrade" or "manual_patch"
    changelog_url = cve.get("changelog_url", "")
    steps = cve.get("remediation_steps", [])
    if fix_type == "version_upgrade":
        steps.insert(0, "WARNING: This fix requires a version upgrade. This may introduce breaking changes. Test thoroughly in a staging environment before deploying to production.")
        if changelog_url:
            steps.append(f"Review changelog: {changelog_url}")
        steps.append("Run full test suite")
        steps.append("Deploy to staging and monitor")
    return {"steps": steps}
