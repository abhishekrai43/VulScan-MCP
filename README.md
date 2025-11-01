# VulScan-MCP 

**Security vulnerability scanner for VS Code**

Automatically scan your project dependencies for CVEs and get step-by-step remediation instructions - all powered by the Model Context Protocol (MCP).

[![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/abhishekrai43/VulScan-MCP)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## What Is This?

VulScan-MCP is a VS Code extension that:
- 🔍 Scans your dependencies for **security vulnerabilities (CVEs only)**
- 🌐 Fetches real-time data from NVD (National Vulnerability Database) and OSV (Open Source Vulnerabilities)
- 📋 Provides clear, step-by-step fix instructions
- ⚠️ **Important:** This tool finds **security vulnerabilities** - it does NOT check for deprecated packages, outdated versions, or general package health
- 🛡️ Never auto-applies fixes - always guides you safely
- 🖥️ Works on Windows, macOS, and Linux

Just ask Copilot *"Check for security vulnerabilities"* and get instant CVE reports!

---

## Quick Start

### For Users (Installing the Extension)

1. **Install from VS Code Marketplace:**
   - Open VS Code
   - Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)
   - Search for **"VulScan-MCP Security Scanner"**
   - Click Install

2. **Prerequisites:**
   - **Python 3.11+** installed **globally** ([Download](https://www.python.org/downloads/))
   - GitHub Copilot extension
   
   > ⚠️ **Important:** VulScan-MCP requires **global Python**, not a project venv.  
   > This is a system-level security tool that scans all your projects.

3. **Start Scanning:**
   ```
   Just ask Copilot: "Check for vulnerabilities"
   ```

**That's it!** The extension bundles the MCP server and auto-installs Python dependencies on first use.

---

## Example Output

```markdown
# VulScan-MCP Vulnerability Report

## Summary
- Total Dependencies Scanned: 87
- Vulnerable Dependencies: 2
- Manifest Files Found: 2

## Vulnerabilities Found

### HIGH Severity
#### lodash @ 4.17.15
- Severity: HIGH
- CVEs Found: 3 (OSV) + 2 (NVD)
- Fix: Upgrade to version 4.17.21 or later

WARNING: This fix requires a version upgrade. Test thoroughly 
in a staging environment before deploying to production.
```

---

## Supported Languages

| Language | Package Manager | Manifest Files |
|----------|----------------|----------------|
| JavaScript/TypeScript | npm/yarn | `package.json` |
| Python | pip/poetry | `requirements.txt`, `pyproject.toml` |
| Java | Maven/Gradle | `pom.xml`, `build.gradle` |
| Go | go modules | `go.mod` |
| Rust | Cargo | `Cargo.toml` |
| Ruby | Bundler | `Gemfile` |
| PHP | Composer | `composer.json` |
| C++ | vcpkg/conan | `vcpkg.json`, `conanfile.txt` |
| .NET | NuGet | `.csproj` |

---

## What Does It Check?

### ✅ What VulScan-MCP DOES Check:
- **Security Vulnerabilities (CVEs)** - Known exploitable security flaws with CVE identifiers
- **Vulnerable Dependencies** - Dependencies with reported security issues in NVD/OSV databases
- **Security Fixes** - Available patches and versions that fix security vulnerabilities

### ❌ What VulScan-MCP DOES NOT Check:
- ~~Deprecated packages~~ - Package deprecation status
- ~~Outdated versions~~ - General package freshness or latest versions
- ~~Package health~~ - Maintenance status, download counts, or popularity
- ~~License issues~~ - License compatibility or compliance
- ~~Code quality~~ - Code style, linting, or best practices

**Focus**: This tool is laser-focused on **security vulnerabilities only**. If your dependencies have no CVEs in the NVD/OSV databases, the scan will return clean results even if packages are outdated or deprecated.

---

## Features

 **Real-Time CVE Scanning**  
Fetches latest vulnerability data from NVD and OSV databases

 **Smart Auto-Detection**  
Automatically activates when you ask about security

 **Clear Remediation Steps**  
Get specific commands and version numbers to fix issues

 **Breaking Change Warnings**  
Warns you when updates might introduce breaking changes

 **Safe by Design**  
Never modifies your code - only provides guidance

 **Cross-Platform**  
Works seamlessly on Windows, macOS, and Linux

---

## How It Works

1. **Scan** - Detects all dependency files in your project
2. **Query** - Checks NVD and OSV databases for known CVEs
3. **Analyze** - Determines severity and impact
4. **Report** - Provides clear, actionable remediation steps

All locally on your machine - your code never leaves your computer!

---

## Privacy & Security

-  **100% Local Processing** - Code stays on your machine
-  **No Telemetry** - Zero data collection
-  **Open Source** - Full transparency
-  **API Queries Only** - Only queries public CVE databases

---

## For Developers

### Project Structure

```
VulScan-MCP/
├── mcp_server/          # Python MCP server
│   ├── server.py        # Main MCP protocol handler
│   ├── vuln_scanner.py  # Dependency scanner
│   ├── cve_fetcher.py   # NVD/OSV API client
│   └── dep_parser.py    # Manifest file parser
├── vulscan-mcp-vscode/  # VS Code extension
│   ├── src/             # TypeScript extension code
│   ├── mcp.json         # MCP server configuration
│   └── launcher.js      # Cross-platform Python launcher
└── requirements.txt     # Python dependencies
```

### Running Locally

```bash
# Clone the repository
git clone https://github.com/abhishekrai43/VulScan-MCP.git
cd VulScan-MCP

# Install Python dependencies
pip install -r requirements.txt

# Run MCP server directly
python -m mcp_server
```

### Testing the Extension

```bash
cd vulscan-mcp-vscode
npm install
npm run compile

# Press F5 in VS Code to launch Extension Development Host
```

---

## Troubleshooting

### "Python not found" Error

**Issue:** Extension fails to start with "Python not found"

**Solutions:**
```bash
# Windows
winget install Python.Python.3.12
# or download from: https://python.org

# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip

# RHEL/CentOS/Fedora
sudo yum install python311 python3-pip
```

After installing, **restart VS Code**.

---

### "No module named 'pip'" Error (Linux/macOS)

**Issue:** System Python doesn't include pip

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# RHEL/CentOS/Fedora  
sudo yum install python3-pip

# macOS (use Homebrew Python, not system Python)
brew install python@3.11
# Then restart VS Code to pick up the new Python
```

Or install dependencies manually:
```bash
python3 -m pip install --user mcp requests
```

---

### "ModuleNotFoundError: No module named 'mcp'" Error

**Issue:** Python dependencies failed to install automatically

**Manual Fix:**
```bash
# Navigate to extension directory
cd ~/.vscode/extensions/abhishekrai43.vulscan-mcp-vscode-*/

# Install dependencies
python3 -m pip install --user -r requirements.txt

# Or install directly
python3 -m pip install --user mcp requests
```

Then **restart VS Code**.

---

### Corporate Firewall / Proxy Issues

**Issue:** pip cannot reach PyPI due to corporate firewall

**Solutions:**

1. **Configure pip to use corporate proxy:**
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
python3 -m pip install --user mcp requests
```

2. **Use company's internal PyPI mirror:**
```bash
python3 -m pip install --user -i https://pypi.company.com/simple mcp requests
```

3. **Download wheels manually** and install offline:
```bash
# On internet-connected machine:
pip download mcp requests -d ~/Downloads/vulscan-deps/

# On restricted machine:
python3 -m pip install --user --no-index --find-links ~/Downloads/vulscan-deps/ mcp requests
```

---

### Extension Keeps Stopping (Linux Remote/WSL)

**Issue:** Server starts but immediately stops with exit code 1

**Diagnosis:**
```bash
# Check launcher log
cat /tmp/vulscan-launcher.log

# Check server log  
cat /tmp/vulscan-mcp-debug.log
```

**Common Causes:**
- ✗ Missing pip → Install: `sudo apt install python3-pip`
- ✗ Missing dependencies → Install: `python3 -m pip install --user mcp requests`
- ✗ Permission issues → Use `--user` flag with pip
- ✗ Old Python version → Upgrade to Python 3.11+

---

### Scan Returns No Results (But You Know There Are Vulnerabilities)

**This is expected!** VulScan-MCP only reports **confirmed CVEs** from NVD/OSV databases. 

**What it does NOT report:**
- ❌ Deprecated packages (still functional, just not recommended)
- ❌ Outdated versions (no known security issues)
- ❌ Unmaintained packages (no CVEs reported)

**To verify CVEs exist:**
1. Visit https://osv.dev/
2. Search for your package name + version
3. Check if any CVEs are listed

If OSV shows no CVEs, then "clean" results are **correct** ✓

---

### Debug Mode

Enable detailed logging:

```bash
# Windows
$env:VULSCAN_DEBUG="1"

# macOS/Linux
export VULSCAN_DEBUG=1
```

Then restart VS Code and check logs:
- **Windows:** `%TEMP%\vulscan-launcher.log` and `%TEMP%\vulscan-mcp-debug.log`
- **macOS/Linux:** `/tmp/vulscan-launcher.log` and `/tmp/vulscan-mcp-debug.log`

---

### Still Having Issues?

1. **Check logs:** See paths above for debug logs
2. **Verify Python:** `python3 --version` (should be 3.11+)
3. **Verify pip:** `python3 -m pip --version`
4. **Test dependencies:** `python3 -c "import mcp, requests"`
5. **Report issue:** https://github.com/abhishekrai43/VulScan-MCP/issues

Include:
- Operating System (Windows/macOS/Linux)
- Python version: `python3 --version`
- Log files: launcher.log and debug.log
- Error messages from VS Code output panel

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Issues & Support

-  [Report a Bug](https://github.com/abhishekrai43/VulScan-MCP/issues)
-  [Request a Feature](https://github.com/abhishekrai43/VulScan-MCP/issues)
-  [View Documentation](https://github.com/abhishekrai43/VulScan-MCP)

---

## Acknowledgments

Built with:
- [Model Context Protocol](https://github.com/modelcontextprotocol) by Anthropic
- [NVD API](https://nvd.nist.gov/) - National Vulnerability Database
- [OSV API](https://osv.dev/) - Open Source Vulnerabilities

---

