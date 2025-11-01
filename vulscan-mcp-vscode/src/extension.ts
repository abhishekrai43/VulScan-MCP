import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  // Register MCP server definition provider
  const provider = new VulScanMcpProvider(context.extensionPath);
  const disposable = vscode.lm.registerMcpServerDefinitionProvider('vulscan-mcp-server', provider);
  
  context.subscriptions.push(disposable);
  
  vscode.window.showInformationMessage(
    'VulScan-MCP Security Scanner is ready! Ask Copilot: "Check for vulnerabilities"'
  );
}

class VulScanMcpProvider implements vscode.McpServerDefinitionProvider<vscode.McpStdioServerDefinition> {
  constructor(private extensionPath: string) {}
  
  provideMcpServerDefinitions(): vscode.ProviderResult<vscode.McpStdioServerDefinition[]> {
    const launcherPath = this.extensionPath + '/launcher.js';
    
    // McpStdioServerDefinition constructor: (label, command, args?, env?, version?)
    return [
      new vscode.McpStdioServerDefinition(
        'VulScan-MCP Security Scanner',
        'node',
        [launcherPath],
        {
          PYTHONIOENCODING: 'utf-8'
        }
      )
    ];
  }
}

export function deactivate() {}


