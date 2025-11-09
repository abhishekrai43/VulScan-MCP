# VulScan-MCP 🛡️

**Scan your dependencies for security vulnerabilities (CVEs) directly in VS Code**

Ask Copilot: *"Check for vulnerabilities"* → Get instant CVE reports with fix instructions.

---

## Quick Start

1. **Install:** Search "VulScan-MCP" in VS Code Extensions
2. **Requirement:** Python 3.11+ installed ([Download](https://www.python.org/downloads/))
3. **Use:** Ask Copilot: `"Check for security vulnerabilities"`

That's it! Dependencies auto-install on first use.

---

## What You Get

```markdown
### 1. lodash @ 4.17.15

#### 📦 Library Affected
- Package: lodash
- Current Version: 4.17.15
- Severity: HIGH

#### 🔍 CVE Details  
- CVE IDs: CVE-2021-23337, CVE-2020-28500
- What is it: Command injection vulnerability allowing attackers to execute arbitrary code

#### ✅ Mitigation Steps
⚠️ WARNING: Version upgrade required. Test in staging first.
1. Update package.json: "lodash": "^4.17.21"
2. Run: npm install
3. Run full test suite
4. Deploy to staging and monitor
```

---

## Supported

**Languages:** JavaScript, TypeScript, Python, Java, Go, Rust, Ruby, PHP, C++, .NET  
**Sources:** NVD (National Vulnerability Database) + OSV (Open Source Vulnerabilities)  
**Platforms:** Windows, macOS, Linux

### What It Checks

✅ **Security vulnerabilities (CVEs)** - Known exploitable flaws  
❌ **NOT deprecated packages** - This tool is CVE-focused only

**Note:** Clean results mean no CVEs found - packages may still be outdated but secure.

---

## Troubleshooting

**Python not found?**  
Install Python 3.11+ globally, then restart VS Code.

**"No module named 'mcp'" error?**  
```bash
python3 -m pip install --user mcp requests
```

**Still issues?** Check logs:
- Windows: `%TEMP%\vulscan-mcp-debug.log`
- macOS/Linux: `/tmp/vulscan-mcp-debug.log`

[Report issues on GitHub →](https://github.com/abhishekrai43/VulScan-MCP/issues)

---

## Developer Info

```bash
# Clone & run
git clone https://github.com/abhishekrai43/VulScan-MCP.git
cd VulScan-MCP
pip install -r requirements.txt
python -m mcp_server

# Test extension
cd vulscan-mcp-vscode
npm install && npm run compile
# Press F5 in VS Code
```

---

## License & Support

**MIT License** | [Report Issues](https://github.com/abhishekrai43/VulScan-MCP/issues)

Built with [Model Context Protocol](https://github.com/modelcontextprotocol), [NVD API](https://nvd.nist.gov/), [OSV API](https://osv.dev/)

