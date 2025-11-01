#!/usr/bin/env node
/**
 * Cross-platform Python launcher for VulScan-MCP
 * Tries python3 first (macOS/Linux), falls back to python (Windows)
 * Auto-installs Python dependencies if needed
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Debug logging
const logFile = path.join(require('os').tmpdir(), 'vulscan-launcher.log');
function debugLog(msg) {
  const timestamp = new Date().toISOString();
  fs.appendFileSync(logFile, `${timestamp} - ${msg}\n`);
}

debugLog('='.repeat(50));
debugLog('Launcher started');
debugLog(`__dirname: ${__dirname}`);
debugLog(`cwd: ${process.cwd()}`);

const extensionDir = __dirname;
const requirementsFile = path.join(extensionDir, 'requirements.txt');
const mcpServerDir = path.join(extensionDir, 'mcp_server');

debugLog(`extensionDir: ${extensionDir}`);
debugLog(`requirementsFile: ${requirementsFile}`);
debugLog(`mcpServerDir: ${mcpServerDir}`);

function findPython() {
  debugLog('Starting findPython()');
  return new Promise((resolve, reject) => {
    // Try python3 first (preferred on macOS/Linux)
    debugLog('Trying python3...');
    const python3 = spawn('python3', ['--version']);
    
    let python3Failed = false;
    
    python3.on('error', (err) => {
      debugLog(`python3 error: ${err.message}`);
      python3Failed = true;
      // python3 not found, try python
      debugLog('Trying python...');
      const python = spawn('python', ['--version']);
      
      python.on('error', (err2) => {
        debugLog(`python error: ${err2.message}`);
        reject(new Error('Python not found. Please install Python 3.11+'));
      });
      
      python.on('close', (code) => {
        debugLog(`python close with code: ${code}`);
        if (code === 0) {
          debugLog('Using python');
          resolve('python');
        } else {
          reject(new Error('Python not found or not working'));
        }
      });
    });
    
    python3.on('close', (code) => {
      debugLog(`python3 close with code: ${code}`);
      if (!python3Failed && code === 0) {
        debugLog('Using python3');
        resolve('python3');
      } else if (!python3Failed) {
        // python3 exists but returned non-zero, try python
        debugLog('python3 failed, trying python...');
        const python = spawn('python', ['--version']);
        
        python.on('error', (err) => {
          debugLog(`python error: ${err.message}`);
          reject(new Error('Python not found. Please install Python 3.11+'));
        });
        
        python.on('close', (code2) => {
          debugLog(`python close with code: ${code2}`);
          if (code2 === 0) {
            debugLog('Using python');
            resolve('python');
          } else {
            reject(new Error('Python not found or not working'));
          }
        });
      }
    });
  });
}

function checkAndInstallDependencies(pythonCmd) {
  try {
    debugLog('checkAndInstallDependencies() started');
    console.error('[VulScan-MCP] Checking dependencies...');
    
    // Check if requests is installed
    try {
      debugLog(`Checking if requests is installed: ${pythonCmd} -c "import requests"`);
      execSync(`${pythonCmd} -c "import requests"`, { stdio: 'ignore' });
      debugLog('requests is already installed');
      console.error('[VulScan-MCP] Dependencies already installed');
      return true;
    } catch {
      debugLog('requests not found, installing...');
      console.error('[VulScan-MCP] Installing dependencies...');
      
      // Install from requirements.txt
      try {
        debugLog(`Installing: ${pythonCmd} -m pip install -q -r "${requirementsFile}"`);
        execSync(`${pythonCmd} -m pip install -q -r "${requirementsFile}"`, {
          stdio: 'inherit'
        });
        debugLog('Dependencies installed successfully');
        console.error('[VulScan-MCP] Dependencies installed successfully');
        return true;
      } catch (installError) {
        debugLog(`Installation failed: ${installError.message}`);
        console.error('[VulScan-MCP] Failed to install dependencies:', installError.message);
        console.error('[VulScan-MCP] Please run manually: pip install -r requirements.txt');
        return false;
      }
    }
  } catch (error) {
    debugLog(`checkAndInstallDependencies() error: ${error.message}`);
    console.error('[VulScan-MCP] Error checking dependencies:', error.message);
    return false;
  }
}

async function main() {
  try {
    debugLog('main() started');
    const pythonCmd = await findPython();
    debugLog(`Found Python: ${pythonCmd}`);
    console.error(`[VulScan-MCP] Using Python: ${pythonCmd}`);
    
    // Check and install dependencies
    debugLog('Checking dependencies...');
    if (!checkAndInstallDependencies(pythonCmd)) {
      debugLog('WARNING: Dependencies check failed');
      console.error('[VulScan-MCP] WARNING: Running without all dependencies. Some features may not work.');
    }
    debugLog('Dependencies OK');
    
    // Add mcp_server directory to Python path
    const pythonPath = process.env.PYTHONPATH || '';
    const newPythonPath = pythonPath ? `${extensionDir}${path.delimiter}${pythonPath}` : extensionDir;
    
    debugLog(`Spawning MCP server: ${pythonCmd} -u -m mcp_server`);
    debugLog(`cwd: ${extensionDir}`);
    debugLog(`PYTHONPATH: ${newPythonPath}`);
    
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
    
    debugLog(`MCP server spawned with PID: ${mcpServer.pid}`);
    
    // Pipe stdin/stdout for MCP protocol
    // Keep stdin/stdout connected for bidirectional JSON-RPC communication
    process.stdin.pipe(mcpServer.stdin);
    mcpServer.stdout.pipe(process.stdout);
    
    mcpServer.on('error', (err) => {
      debugLog(`MCP server error: ${err.message}`);
      console.error('[VulScan-MCP] Failed to start MCP server:', err);
      process.exit(1);
    });
    
    mcpServer.on('close', (code) => {
      debugLog(`MCP server closed with code: ${code}`);
      process.exit(code || 0);
    });
    
    // Handle termination signals
    process.on('SIGTERM', () => {
      debugLog('Received SIGTERM');
      mcpServer.kill('SIGTERM');
    });
    
    process.on('SIGINT', () => {
      debugLog('Received SIGINT');
      mcpServer.kill('SIGINT');
    });
    
    debugLog('MCP server launch complete, waiting for messages...');
    
  } catch (error) {
    debugLog(`main() error: ${error.message}`);
    console.error('[VulScan-MCP] Error:', error.message);
    console.error('[VulScan-MCP] Please install Python 3.11+ from:');
    console.error('  - Windows: https://python.org or Microsoft Store');
    console.error('  - macOS: brew install python@3.11');
    console.error('  - Linux: sudo apt install python3.11');
    process.exit(1);
  }
}

main();
