# VulScan-MCP Security Scanner 🔒

**Find and fix security vulnerabilities in your project dependencies - right inside VS Code!**

[![VS Code](https://img.shields.io/badge/VS%20Code-1.85%2B-blue.svg)](https://code.visualstudio.com/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/abhishekrai43/VulScan-MCP)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## What Does It Do?

VulScan-MCP automatically scans your project dependencies for known security vulnerabilities (CVEs) and provides clear, step-by-step instructions to fix them. Just ask Copilot about security, and it handles the rest!

### ✨ Key Features

- 🔍 **Real-Time CVE Scanning** - Checks NVD and OSV databases for latest vulnerabilities
- 📦 **Multi-Language Support** - npm, pip, Maven, Go, Cargo, Composer, and more
- 🎯 **Smart & Automatic** - No commands to remember, just ask naturally
- 📝 **Clear Fix Instructions** - Get step-by-step remediation guidance
- 🚫 **Safe by Design** - Never modifies your code automatically
- 🌍 **Cross-Platform** - Works on Windows, macOS, and Linux

---

## Quick Start

### 1. Install the Extension

Open VS Code and install:
1. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)
2. Search for **"VulScan-MCP Security Scanner"**
3. Click **Install**

### 2. Prerequisites

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **GitHub Copilot** - Required for MCP integration

**That's it!** The extension automatically:
-  Detects your Python installation
-  Installs required dependencies on first use
-  Registers the MCP server with Copilot
-  Works immediately - no configuration needed!

### 3. Start Scanning!

Simply ask Copilot Chat about security:

```
"Check for vulnerabilities"
"Scan my dependencies"
"Any security issues?"
```

The first time you use it, it may take a few seconds to install dependencies (requests library). After that, it's instant!

---

## Example Output

After scanning, you'll get a detailed report like this:

```markdown
# VulScan-MCP Vulnerability Report

## Summary
- Total Dependencies Scanned: 87
- Vulnerable Dependencies: 2
- Manifest Files Found: 2

### Scanned Files:
- `package.json` at `/frontend/package.json`
- `requirements.txt` at `/backend/requirements.txt`

## Vulnerabilities Found

### HIGH Severity

#### lodash @ 4.17.15
- **Severity:** HIGH
- **CVEs Found:** 3 (OSV) + 2 (NVD)
- **Fix:** Upgrade to version 4.17.21 or later

WARNING: This fix requires a version upgrade. Test thoroughly 
in a staging environment before deploying to production.

### MEDIUM Severity

#### tslib @ ^2.3.0
- **Severity:** MEDIUM
- **CVEs Found:** 1 (NVD)
- **Fix:** Upgrade to version 2.6.0 or later

## Recommendations

1. **Prioritize HIGH and CRITICAL severity vulnerabilities**
2. **Test all updates in a staging environment first**
3. **Review changelogs before upgrading**
4. **Run your full test suite after updates**
5. **Monitor for new vulnerabilities regularly**
```

---

## Supported Package Managers

| Language/Framework | Manifest Files |
|-------------------|----------------|
| **Node.js/npm** | `package.json` |
| **Python** | `requirements.txt`, `pyproject.toml`, `Pipfile` |
| **Java** | `pom.xml`, `build.gradle` |
| **Go** | `go.mod` |
| **Ruby** | `Gemfile` |
| **PHP** | `composer.json` |
| **Rust** | `Cargo.toml` |
| **C++** | `vcpkg.json`, `conanfile.txt` |
| **.NET** | `.csproj` |

---

## How to Use

### Simple Questions That Work

Just ask Copilot Chat naturally:

 **"Check for vulnerabilities"**  
 **"Scan my dependencies"**  
 **"Any security issues?"**  
 **"Check for CVEs"**  
 **"Is my project secure?"**  
 **"Audit my packages"**  

The extension automatically activates - no need to mention "MCP" or "tool"!

### What Happens

1. **Scan** - Finds all dependency files in your project
2. **Check** - Queries NVD and OSV databases for CVEs
3. **Report** - Shows vulnerabilities grouped by severity
4. **Fix** - Provides clear remediation instructions

---

## Platform Support

###  Windows
- Windows 10, 11
- PowerShell or Command Prompt
- Python from Microsoft Store or python.org

###  macOS  
- macOS 10.15+
- Intel and Apple Silicon (M1/M2/M3)
- Python via Homebrew or system Python

###  Linux
- Ubuntu, Debian, Fedora, Arch
- All major distributions
- Python 3.11+ from package manager

---

## Privacy & Security

-  **100% Local** - All scanning happens on your machine
-  **No Telemetry** - Your code stays private
-  **Open Source** - Full transparency
-  **API Queries Only** - Only checks public CVE databases

Your code never leaves your computer!

---

## Troubleshooting

### "MCP server not available in Copilot"
1. Ensure you have **version 1.0.3+** of this extension installed
2. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")
3. The server registers automatically - no settings.json configuration needed!

### "Python not found"
Install Python 3.11+ from [python.org](https://www.python.org/downloads/)

Make sure `python` or `python3` command works in your terminal:
```bash
python --version  # or python3 --version
```

### "Extension not working"
1. Ensure GitHub Copilot is installed and active
2. Reload VS Code (`Ctrl+Shift+P` → "Reload Window")
3. Check Python version: `python --version` (should be 3.11+)
4. First scan may take 10-20 seconds while installing dependencies

### "No results returned"
- Check your internet connection (needed for CVE databases)
- Ensure you have dependency files (package.json, requirements.txt, etc.)
- Try scanning again - APIs may have rate limits

---

## Need Help?

- 🐛 [Report a Bug](https://github.com/abhishekrai43/VulScan-MCP/issues)
- 💡 [Request a Feature](https://github.com/abhishekrai43/VulScan-MCP/issues)
- 📖 [Documentation](https://github.com/abhishekrai43/VulScan-MCP)

---

## License

MIT License - See [LICENSE](LICENSE) file

---

**Built with ❤️ by [@abhishekrai43](https://github.com/abhishekrai43)**

*Powered by NVD, OSV, and the Model Context Protocol*


