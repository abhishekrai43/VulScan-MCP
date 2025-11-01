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

/**
 * Check if all required Python modules are installed
 * Tests each module individually for better error reporting
 */
function checkDependencies(pythonCmd) {
  const requiredModules = ['mcp', 'requests'];
  const missing = [];
  
  for (const module of requiredModules) {
    try {
      debugLog(`Checking if ${module} is installed`);
      execSync(`${pythonCmd} -c "import ${module}"`, { stdio: 'ignore' });
      debugLog(`✓ ${module} is installed`);
    } catch {
      debugLog(`✗ ${module} is NOT installed`);
      missing.push(module);
    }
  }
  
  return missing;
}

/**
 * Try to install pip if it's not available
 * Uses ensurepip module (part of standard library since Python 3.4)
 */
function ensurePip(pythonCmd) {
  try {
    debugLog('Attempting to bootstrap pip using ensurepip...');
    console.error('[VulScan-MCP] Installing pip...');
    execSync(`${pythonCmd} -m ensurepip --default-pip`, { stdio: 'ignore' });
    debugLog('✓ pip bootstrapped successfully');
    return true;
  } catch (error) {
    debugLog(`✗ ensurepip failed: ${error.message}`);
    return false;
  }
}

/**
 * Try multiple methods to install dependencies
 * FAANG-level: Exhaustive fallback strategy with clear error messages
 */
function installDependencies(pythonCmd) {
  const installMethods = [
    // Method 1: Standard pip module (most reliable)
    {
      name: 'python -m pip',
      cmd: `${pythonCmd} -m pip install --user -q -r "${requirementsFile}"`,
      description: 'Installing to user directory (no sudo required)'
    },
    // Method 2: Direct pip3 command
    {
      name: 'pip3',
      cmd: `pip3 install --user -q -r "${requirementsFile}"`,
      description: 'Trying pip3 command directly'
    },
    // Method 3: Direct pip command  
    {
      name: 'pip',
      cmd: `pip install --user -q -r "${requirementsFile}"`,
      description: 'Trying pip command directly'
    },
    // Method 4: System-wide install (may need permissions)
    {
      name: 'python -m pip (system)',
      cmd: `${pythonCmd} -m pip install -q -r "${requirementsFile}"`,
      description: 'Attempting system-wide install'
    }
  ];

  for (const method of installMethods) {
    try {
      debugLog(`Trying installation method: ${method.name}`);
      console.error(`[VulScan-MCP] ${method.description}...`);
      
      execSync(method.cmd, { 
        stdio: 'pipe',  // Capture output for logging
        timeout: 60000  // 60 second timeout
      });
      
      debugLog(`✓ Installation successful using ${method.name}`);
      console.error(`[VulScan-MCP] ✓ Dependencies installed successfully`);
      return true;
      
    } catch (error) {
      debugLog(`✗ ${method.name} failed: ${error.message}`);
      // Continue to next method
    }
  }
  
  return false;
}

/**
 * FAANG-level dependency management with comprehensive fallback strategy
 * Returns: { success: boolean, error: string | null }
 */
function checkAndInstallDependencies(pythonCmd) {
  try {
    debugLog('=== Dependency Check Started ===');
    console.error('[VulScan-MCP] Checking dependencies...');
    
    // Step 1: Check what's missing
    let missing = checkDependencies(pythonCmd);
    
    if (missing.length === 0) {
      debugLog('✓ All dependencies already installed');
      console.error('[VulScan-MCP] ✓ All dependencies satisfied');
      return { success: true, error: null };
    }
    
    debugLog(`Missing modules: ${missing.join(', ')}`);
    console.error(`[VulScan-MCP] Missing modules: ${missing.join(', ')}`);
    
    // Step 2: Check if pip is available
    try {
      execSync(`${pythonCmd} -m pip --version`, { stdio: 'ignore' });
      debugLog('✓ pip is available');
    } catch {
      debugLog('✗ pip not found, attempting to bootstrap...');
      if (!ensurePip(pythonCmd)) {
        const error = 
          '✗ DEPENDENCY ERROR: pip is not installed and could not be bootstrapped.\n\n' +
          'Please install pip manually:\n' +
          '  • Ubuntu/Debian: sudo apt-get install python3-pip\n' +
          '  • RHEL/CentOS:   sudo yum install python3-pip\n' +
          '  • macOS:         brew install python3\n' +
          '  • Windows:       Download from python.org\n\n' +
          `Or install dependencies manually:\n` +
          `  ${pythonCmd} -m pip install mcp requests\n\n` +
          'Then restart VS Code.';
        
        debugLog(error);
        console.error(`[VulScan-MCP] ${error}`);
        return { success: false, error };
      }
    }
    
    // Step 3: Try multiple installation methods
    console.error('[VulScan-MCP] Installing Python dependencies...');
    
    if (installDependencies(pythonCmd)) {
      // Verify installation
      missing = checkDependencies(pythonCmd);
      if (missing.length === 0) {
        debugLog('✓ All dependencies installed and verified');
        return { success: true, error: null };
      } else {
        debugLog(`✗ Installation reported success but modules still missing: ${missing.join(', ')}`);
      }
    }
    
    // Step 4: All methods failed - provide detailed error
    const error =
      '✗ DEPENDENCY ERROR: Failed to install required Python modules.\n\n' +
      `Missing: ${missing.join(', ')}\n\n` +
      'Please install manually:\n' +
      `  ${pythonCmd} -m pip install --user mcp requests\n\n` +
      'Or:\n' +
      `  pip3 install --user mcp requests\n\n` +
      'Common issues:\n' +
      '  • Corporate firewall blocking PyPI\n' +
      '  • Python installation is incomplete\n' +
      '  • Insufficient permissions\n\n' +
      'After installing, restart VS Code.';
    
    debugLog(error);
    console.error(`[VulScan-MCP] ${error}`);
    return { success: false, error };
    
  } catch (error) {
    debugLog(`✗ Unexpected error in dependency check: ${error.message}`);
    const errorMsg = `Unexpected error checking dependencies: ${error.message}`;
    console.error(`[VulScan-MCP] ${errorMsg}`);
    return { success: false, error: errorMsg };
  }
}

async function main() {
  try {
    debugLog('=== VulScan-MCP Launcher Started ===');
    
    // Step 1: Find Python
    const pythonCmd = await findPython();
    debugLog(`✓ Found Python: ${pythonCmd}`);
    console.error(`[VulScan-MCP] ✓ Using Python: ${pythonCmd}`);
    
    // Step 2: Check and install dependencies (CRITICAL - must succeed)
    debugLog('Checking dependencies...');
    const depResult = checkAndInstallDependencies(pythonCmd);
    
    if (!depResult.success) {
      // FAIL FAST: Don't start server without dependencies
      debugLog('✗✗✗ FATAL: Dependencies not satisfied, aborting launch');
      console.error('[VulScan-MCP] ✗✗✗ FATAL ERROR: Cannot start server without required dependencies');
      console.error('[VulScan-MCP]');
      console.error(depResult.error);
      console.error('[VulScan-MCP]');
      console.error('[VulScan-MCP] Debug log: ' + logFile);
      
      // Exit with error code to signal VS Code that initialization failed
      process.exit(1);
    }
    
    debugLog('✓ All dependencies satisfied');
    
    // Step 3: Setup Python environment
    const pythonPath = process.env.PYTHONPATH || '';
    const newPythonPath = pythonPath ? `${extensionDir}${path.delimiter}${pythonPath}` : extensionDir;
    
    debugLog(`Spawning MCP server: ${pythonCmd} -u -m mcp_server`);
    debugLog(`  cwd: ${extensionDir}`);
    debugLog(`  PYTHONPATH: ${newPythonPath}`);
    
    // Step 4: Launch MCP server
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
    
    if (!mcpServer.pid) {
      debugLog('✗✗✗ FATAL: Failed to spawn MCP server process');
      console.error('[VulScan-MCP] ✗✗✗ FATAL: Failed to spawn Python process');
      process.exit(1);
    }
    
    debugLog(`✓ MCP server spawned with PID: ${mcpServer.pid}`);
    console.error(`[VulScan-MCP] ✓ Server started (PID: ${mcpServer.pid})`);
    
    // Step 5: Pipe stdin/stdout for MCP protocol
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
    
    // Handle termination signals gracefully
    process.on('SIGTERM', () => {
      debugLog('Received SIGTERM, shutting down gracefully...');
      if (mcpServer && !mcpServer.killed) {
        mcpServer.kill('SIGTERM');
      }
    });
    
    process.on('SIGINT', () => {
      debugLog('Received SIGINT, shutting down gracefully...');
      if (mcpServer && !mcpServer.killed) {
        mcpServer.kill('SIGINT');
      }
    });
    
    debugLog('✓ MCP server launch complete, waiting for messages...');
    console.error('[VulScan-MCP] ✓ Ready for requests');
    
  } catch (error) {
    debugLog(`✗✗✗ FATAL ERROR in main(): ${error.message}`);
    debugLog(`Stack trace: ${error.stack}`);
    
    console.error('[VulScan-MCP] ✗✗✗ FATAL ERROR: ' + error.message);
    console.error('[VulScan-MCP]');
    
    if (error.message.includes('Python not found')) {
      console.error('[VulScan-MCP] Python 3.11+ is required but not found.');
      console.error('[VulScan-MCP]');
      console.error('[VulScan-MCP] Install Python:');
      console.error('[VulScan-MCP]   • Windows: https://python.org or Microsoft Store');
      console.error('[VulScan-MCP]   • macOS:   brew install python@3.11');
      console.error('[VulScan-MCP]   • Ubuntu:  sudo apt install python3.11 python3-pip');
      console.error('[VulScan-MCP]   • RHEL:    sudo yum install python311 python3-pip');
    } else {
      console.error('[VulScan-MCP] Unexpected error during startup.');
      console.error('[VulScan-MCP] Please report this issue: https://github.com/abhishekrai43/VulScan-MCP/issues');
    }
    
    console.error('[VulScan-MCP]');
    console.error('[VulScan-MCP] Debug log: ' + logFile);
    process.exit(1);
  }
}

// Catch unhandled errors
process.on('uncaughtException', (error) => {
  debugLog(`✗✗✗ Uncaught exception: ${error.message}`);
  debugLog(`Stack trace: ${error.stack}`);
  console.error('[VulScan-MCP] ✗✗✗ Uncaught exception:', error.message);
  console.error('[VulScan-MCP] Debug log: ' + logFile);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  debugLog(`✗✗✗ Unhandled rejection: ${reason}`);
  console.error('[VulScan-MCP] ✗✗✗ Unhandled rejection:', reason);
  console.error('[VulScan-MCP] Debug log: ' + logFile);
  process.exit(1);
});

main();
