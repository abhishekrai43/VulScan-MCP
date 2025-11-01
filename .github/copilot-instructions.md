## Project Conventions
## Developer Workflows- **No auto-fixes**: The server must never modify code or dependencies directly

# Copilot Instructions for VulScan-MCP

## MVP & Core Value
This tool simplifies CVE mitigation for developers:
- Scans the repo to detect project structure and languages
- Fetches latest CVEs for those languages/dependencies (NVD/OSV)
- Passes each CVE to a local LLM (Ollama) to generate clear, step-by-step mitigation instructions
- **Always lists explicit commands** for the developer to run (never auto-applies fixes)
- **Prepends a warning** only if a version upgrade is required (to highlight possible breaking changes)
- Outputs all guidance in plain English, directly in VS Code

> **Never implement the mitigation automatically.**
> If a version bump is needed, always warn the developer about possible breaking changes.

## Core Principle
> You are a senior security mentor. Explain the fix in plain English and provide exact commands for the developer to run.
> If the fix requires a version upgrade, start with the exact warning below. Otherwise, no warning. Never apply changes directly.

```
WARNING: This fix requires a version upgrade. This may introduce breaking changes. Test thoroughly in a staging environment before deploying to production.
```

## Architecture & Key Files
- **Repo Scanner**: Detects project structure, languages, and dependencies
- **CVE Fetcher**: Integrates with NVD and OSV APIs for real-time vulnerability data
- **LLM Integration**: Uses local Ollama LLM to generate step-by-step, developer-friendly mitigation instructions
- **Remediation Logic**: Core logic in `simplify.py` determines if a fix is a version upgrade and prepends a warning if so

## Critical Logic: Version Upgrade Warning
- If a fix requires a dependency version upgrade, prepend the exact warning above to the remediation steps.
- Only include this warning for version upgrades (e.g., `lodash@4.17.15 → 4.17.21`).
- For other fixes (e.g., input validation, config changes), do **not** include the warning.
- Always append: `Review changelog: {changelog_url}` and `Run full test suite` and `Deploy to staging and monitor` for version upgrades.

## Developer Workflows
- **Scan**: Run the main server to scan the repo and fetch CVEs
- **Remediation**: All fixes are returned as step-by-step instructions, never applied automatically
- **Testing**: Always recommend running the full test suite and deploying to staging after any remediation

## Project Conventions
- **No auto-fixes**: The server must never modify code or dependencies directly
- **Plain English output**: All remediation steps must be clear, safe, and human-readable
- **Explicit commands**: Always provide exact shell or package manager commands for mitigation
- **Python 3.11+**: Use modern Python features and typing

## Integration Points
- **NVD/OSV**: For live CVE data
- **Ollama LLM**: For generating remediation steps
- **Git**: For scanning local repositories

## Example: Version Upgrade Fix
```
WARNING: This fix requires a version upgrade. This may introduce breaking changes. Test thoroughly in a staging environment before deploying to production.

1. Update `package.json` to use `lodash@4.17.21`
2. Run `npm install`
3. Review changelog: https://github.com/lodash/lodash/releases/tag/4.17.21
4. Run full test suite
5. Deploy to staging and monitor
```

## Example: Non-Version Fix
```
1. Add input validation to `user_input.py`
2. Sanitize all user inputs before processing
3. Run full test suite
4. Deploy to staging and monitor
```

---

**For any unclear or incomplete sections, ask the user for clarification before proceeding.**
