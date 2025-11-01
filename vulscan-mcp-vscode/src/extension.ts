import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  // Auto-register MCP server in user settings
  const config = vscode.workspace.getConfiguration();
  const mcpServers = config.get<any>('mcp.servers') || {};
  
  // Check if our server is already registered
  if (!mcpServers['VulScan-MCP']) {
    const launcherPath = context.extensionPath + '/launcher.js';
    
    mcpServers['VulScan-MCP'] = {
      type: 'stdio',
      command: 'node',
      args: [launcherPath],
      cwd: '${workspaceFolder}',
      label: 'VulScan-MCP Security Scanner',
      description: 'Scans for CVEs and security vulnerabilities in dependencies',
      autoStart: true
    };
    
    // Update settings
    config.update('mcp.servers', mcpServers, vscode.ConfigurationTarget.Global)
      .then(() => {
        vscode.window.showInformationMessage(
          '✅ VulScan-MCP Security Scanner is ready! Ask Copilot: "Check for vulnerabilities"',
          'Reload Window'
        ).then(selection => {
          if (selection === 'Reload Window') {
            vscode.commands.executeCommand('workbench.action.reloadWindow');
          }
        });
      });
  }
}

export function deactivate() {
  // Optionally remove from settings on uninstall
  const config = vscode.workspace.getConfiguration();
  const mcpServers = config.get<any>('mcp.servers') || {};
  
  if (mcpServers['VulScan-MCP']) {
    delete mcpServers['VulScan-MCP'];
    config.update('mcp.servers', mcpServers, vscode.ConfigurationTarget.Global);
  }
}


