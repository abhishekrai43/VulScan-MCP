#!/usr/bin/env node
/**
 * Cross-platform Python launcher for VulScan-MCP
 * Tries python3 first (macOS/Linux), falls back to python (Windows)
 * Auto-installs Python dependencies if needed
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const extensionDir = __dirname;
const requirementsFile = path.join(extensionDir, 'requirements.txt');
const mcpServerDir = path.join(extensionDir, 'mcp_server');

function findPython() {
  return new Promise((resolve, reject) => {
    // Try python3 first (preferred on macOS/Linux)
    const python3 = spawn('python3', ['--version']);
    
    python3.on('error', () => {
      // python3 not found, try python
      const python = spawn('python', ['--version']);
      
      python.on('error', () => {
        reject(new Error('Python not found. Please install Python 3.11+'));
      });
      
      python.on('close', (code) => {
        if (code === 0) {
          resolve('python');
        } else {
          reject(new Error('Python not found or not working'));
        }
      });
    });
    
    python3.on('close', (code) => {
      if (code === 0) {
        resolve('python3');
      }
    });
  });
}

function checkAndInstallDependencies(pythonCmd) {
  try {
    console.error('[VulScan-MCP] Checking dependencies...');
    
    // Check if requests is installed
    try {
      execSync(`${pythonCmd} -c "import requests"`, { stdio: 'ignore' });
      console.error('[VulScan-MCP] Dependencies already installed');
      return true;
    } catch {
      console.error('[VulScan-MCP] Installing dependencies...');
      
      // Install from requirements.txt
      try {
        execSync(`${pythonCmd} -m pip install -q -r "${requirementsFile}"`, {
          stdio: 'inherit'
        });
        console.error('[VulScan-MCP] Dependencies installed successfully');
        return true;
      } catch (installError) {
        console.error('[VulScan-MCP] Failed to install dependencies:', installError.message);
        console.error('[VulScan-MCP] Please run manually: pip install -r requirements.txt');
        return false;
      }
    }
  } catch (error) {
    console.error('[VulScan-MCP] Error checking dependencies:', error.message);
    return false;
  }
}

async function main() {
  try {
    const pythonCmd = await findPython();
    console.error(`[VulScan-MCP] Using Python: ${pythonCmd}`);
    
    // Check and install dependencies
    if (!checkAndInstallDependencies(pythonCmd)) {
      console.error('[VulScan-MCP] WARNING: Running without all dependencies. Some features may not work.');
    }
    
    // Add mcp_server directory to Python path
    const pythonPath = process.env.PYTHONPATH || '';
    const newPythonPath = pythonPath ? `${extensionDir}${path.delimiter}${pythonPath}` : extensionDir;
    
    // Launch MCP server
    // IMPORTANT: Use 'pipe' for stdin/stdout (MCP protocol communication)
    // Only stderr is inherited for logging
    const mcpServer = spawn(pythonCmd, ['-u', '-m', 'mcp_server'], {
      stdio: ['pipe', 'pipe', 'inherit'],  // stdin/stdout for MCP, stderr for logs
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8',
        PYTHONPATH: newPythonPath
      },
      cwd: extensionDir
    });
    
    // Pipe stdin/stdout for MCP protocol
    // Keep stdin/stdout connected for bidirectional JSON-RPC communication
    process.stdin.pipe(mcpServer.stdin);
    mcpServer.stdout.pipe(process.stdout);
    
    mcpServer.on('error', (err) => {
      console.error('[VulScan-MCP] Failed to start MCP server:', err);
      process.exit(1);
    });
    
    mcpServer.on('close', (code) => {
      process.exit(code || 0);
    });
    
    // Handle termination signals
    process.on('SIGTERM', () => {
      mcpServer.kill('SIGTERM');
    });
    
    process.on('SIGINT', () => {
      mcpServer.kill('SIGINT');
    });
    
  } catch (error) {
    console.error('[VulScan-MCP] Error:', error.message);
    console.error('[VulScan-MCP] Please install Python 3.11+ from:');
    console.error('  - Windows: https://python.org or Microsoft Store');
    console.error('  - macOS: brew install python@3.11');
    console.error('  - Linux: sudo apt install python3.11');
    process.exit(1);
  }
}

main();
