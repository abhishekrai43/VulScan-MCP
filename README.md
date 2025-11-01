# VulScan-MCP 🔒

**Enterprise-grade security vulnerability scanner for VS Code**

Automatically scan your project dependencies for CVEs and get step-by-step remediation instructions - all powered by the Model Context Protocol (MCP).

[![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/abhishekrai43/VulScan-MCP)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## What Is This?

VulScan-MCP is a VS Code extension that:
- 🔍 Scans your dependencies for known vulnerabilities (CVEs)
- 📊 Fetches real-time data from NVD and OSV databases
- 📝 Provides clear, step-by-step fix instructions
- 🚫 Never auto-applies fixes - always guides you safely
- 🌍 Works on Windows, macOS, and Linux

Just ask Copilot *"Check for vulnerabilities"* and get instant security insights!

---

## Quick Start

### For Users (Installing the Extension)

1. **Install from VS Code Marketplace:**
   - Open VS Code
   - Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS)
   - Search for **"VulScan-MCP Security Scanner"**
   - Click Install

2. **Prerequisites:**
   - Python 3.11+ ([Download](https://www.python.org/downloads/))
   - GitHub Copilot extension

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

## Features

✨ **Real-Time CVE Scanning**  
Fetches latest vulnerability data from NVD and OSV databases

🎯 **Smart Auto-Detection**  
Automatically activates when you ask about security

📝 **Clear Remediation Steps**  
Get specific commands and version numbers to fix issues

⚠️ **Breaking Change Warnings**  
Warns you when updates might introduce breaking changes

🚫 **Safe by Design**  
Never modifies your code - only provides guidance

🌍 **Cross-Platform**  
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

- 🐛 [Report a Bug](https://github.com/abhishekrai43/VulScan-MCP/issues)
- 💡 [Request a Feature](https://github.com/abhishekrai43/VulScan-MCP/issues)
- 📖 [View Documentation](https://github.com/abhishekrai43/VulScan-MCP)

---

## Acknowledgments

Built with:
- [Model Context Protocol](https://github.com/modelcontextprotocol) by Anthropic
- [NVD API](https://nvd.nist.gov/) - National Vulnerability Database
- [OSV API](https://osv.dev/) - Open Source Vulnerabilities

---

**Made with ❤️ by [@abhishekrai43](https://github.com/abhishekrai43)**

*Keeping your code secure, one dependency at a time.*