# VulScan-MCP Security Scanner �️

**Scan dependencies for CVEs directly in VS Code with GitHub Copilot**

---

## What It Does

Scans your project dependencies for security vulnerabilities (CVEs) and gives you clear fix instructions.  
Ask Copilot: *"Check for vulnerabilities"* → Get instant CVE reports.

**Features:**
- 🔍 Real-time CVE scanning (NVD + OSV databases)
- 📦 Multi-language support (npm, pip, Maven, Go, Cargo, etc.)
- 📝 Step-by-step fix instructions
- 🚫 Never auto-modifies code
- 🌍 Cross-platform (Windows, macOS, Linux)

---

## Quick Start

### Install
1. Press `Ctrl+Shift+X` (`Cmd+Shift+X` on macOS)
2. Search "VulScan-MCP"
3. Click Install

### Requirements
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **GitHub Copilot** extension

Dependencies auto-install on first use.

### Use
Ask Copilot Chat:
```
"Check for vulnerabilities"
"Scan my dependencies"
"Any security issues?"
```

The first time you use it, it may take a few seconds to install dependencies (requests library). After that, it's instant!

---

## Example Output

After scanning, you'll get a detailed report like this:

"Check for vulnerabilities"
"Scan my dependencies"  
"Any security issues?"
```

---

## Example Output

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

**Supported:** JavaScript, TypeScript, Python, Java, Go, Rust, Ruby, PHP, C++, .NET

---

## Troubleshooting

**"Python not found"**  
Install Python 3.11+ from [python.org](https://www.python.org/downloads/), restart VS Code

**"No results"**  
✓ Check internet connection  
✓ Ensure you have dependency files (package.json, requirements.txt, etc.)  
✓ This tool only reports **CVEs** - clean results mean no security vulnerabilities found

**Need help?** [Report Issues →](https://github.com/abhishekrai43/VulScan-MCP/issues)

---

## License

MIT License | **Built with NVD, OSV, and Model Context Protocol**


