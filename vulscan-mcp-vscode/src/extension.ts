import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  // No activation code needed; MCP server is registered via package.json
  vscode.window.showInformationMessage('VulScan MCP Server extension is active.');
}

export function deactivate() {}
