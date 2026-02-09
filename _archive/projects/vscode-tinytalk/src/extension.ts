import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    console.log('TinyTalk extension activated');
    
    // Create output channel
    outputChannel = vscode.window.createOutputChannel('TinyTalk');
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('tinytalk.run', runTinyTalkFile),
        vscode.commands.registerCommand('tinytalk.runSelection', runSelection),
        vscode.commands.registerCommand('tinytalk.transpileJS', transpileToJS)
    );
    
    // Register diagnostics for linting
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('tinytalk');
    context.subscriptions.push(diagnosticCollection);
    
    // Lint on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => {
            if (doc.languageId === 'tinytalk') {
                lintDocument(doc, diagnosticCollection);
            }
        })
    );
    
    // Lint on open
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => {
            if (doc.languageId === 'tinytalk') {
                lintDocument(doc, diagnosticCollection);
            }
        })
    );
}

async function runTinyTalkFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active TinyTalk file');
        return;
    }
    
    const document = editor.document;
    if (document.languageId !== 'tinytalk') {
        vscode.window.showErrorMessage('Not a TinyTalk file');
        return;
    }
    
    // Save first
    await document.save();
    
    const config = vscode.workspace.getConfiguration('tinytalk');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const showOutput = config.get<boolean>('showOutputOnRun', true);
    
    if (showOutput) {
        outputChannel.show(true);
    }
    
    outputChannel.clear();
    outputChannel.appendLine(`Running: ${document.fileName}`);
    outputChannel.appendLine('─'.repeat(50));
    
    // Find the realTinyTalk interpreter
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    const interpreterPath = workspaceFolder 
        ? path.join(workspaceFolder, 'realTinyTalk', 'cli.py')
        : 'realTinyTalk/cli.py';
    
    const args = [interpreterPath, 'run', document.fileName];
    
    const process = cp.spawn(pythonPath, args, {
        cwd: workspaceFolder || path.dirname(document.fileName)
    });
    
    process.stdout.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.stderr.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.on('close', (code) => {
        outputChannel.appendLine('─'.repeat(50));
        if (code === 0) {
            outputChannel.appendLine('✓ Completed successfully');
        } else {
            outputChannel.appendLine(`✗ Exited with code ${code}`);
        }
    });
}

async function runSelection() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const selection = editor.selection;
    const code = editor.document.getText(selection);
    
    if (!code.trim()) {
        vscode.window.showWarningMessage('No code selected');
        return;
    }
    
    const config = vscode.workspace.getConfiguration('tinytalk');
    const pythonPath = config.get<string>('pythonPath', 'python');
    
    outputChannel.show(true);
    outputChannel.clear();
    outputChannel.appendLine('Running selection...');
    outputChannel.appendLine('─'.repeat(50));
    
    // Run via Python with -c flag
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    
    const pythonCode = `
import sys
sys.path.insert(0, '${workspaceFolder?.replace(/\\/g, '/')}')
from realTinyTalk.runtime import Runtime
from realTinyTalk.parser import Parser
from realTinyTalk.lexer import Lexer

code = '''${code.replace(/'/g, "\\'")}'''
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
runtime = Runtime()
runtime.execute(ast)
`;
    
    const process = cp.spawn(pythonPath, ['-c', pythonCode], {
        cwd: workspaceFolder
    });
    
    process.stdout.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.stderr.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.on('close', (code) => {
        outputChannel.appendLine('─'.repeat(50));
        outputChannel.appendLine(code === 0 ? '✓ Done' : `✗ Error (${code})`);
    });
}

async function transpileToJS() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const document = editor.document;
    const code = document.getText();
    
    const config = vscode.workspace.getConfiguration('tinytalk');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    
    const pythonCode = `
import sys
sys.path.insert(0, '${workspaceFolder?.replace(/\\/g, '/')}')
from realTinyTalk.backends.js import compile_to_js

code = '''${code.replace(/'/g, "\\'")}'''
js = compile_to_js(code, include_runtime=True)
print(js)
`;
    
    const process = cp.spawn(pythonPath, ['-c', pythonCode], {
        cwd: workspaceFolder
    });
    
    let output = '';
    process.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    process.on('close', async (exitCode) => {
        if (exitCode === 0 && output) {
            // Open new document with JS code
            const jsDoc = await vscode.workspace.openTextDocument({
                content: output,
                language: 'javascript'
            });
            await vscode.window.showTextDocument(jsDoc, { viewColumn: vscode.ViewColumn.Beside });
            vscode.window.showInformationMessage('Transpiled to JavaScript');
        } else {
            vscode.window.showErrorMessage('Transpilation failed');
        }
    });
}

function lintDocument(document: vscode.TextDocument, diagnostics: vscode.DiagnosticCollection) {
    const config = vscode.workspace.getConfiguration('tinytalk');
    if (!config.get<boolean>('enableLinting', true)) {
        diagnostics.delete(document.uri);
        return;
    }
    
    const pythonPath = config.get<string>('pythonPath', 'python');
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    const code = document.getText();
    
    const pythonCode = `
import sys
import json
sys.path.insert(0, '${workspaceFolder?.replace(/\\/g, '/')}')
from realTinyTalk.lexer import Lexer
from realTinyTalk.parser import Parser

code = '''${code.replace(/'/g, "\\'")}'''
errors = []
try:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    parser.parse()
except SyntaxError as e:
    msg = str(e)
    # Extract line number if present
    import re
    match = re.search(r'Line (\\d+)', msg)
    line = int(match.group(1)) - 1 if match else 0
    errors.append({'line': line, 'message': msg, 'severity': 'error'})
except Exception as e:
    errors.append({'line': 0, 'message': str(e), 'severity': 'error'})
print(json.dumps(errors))
`;
    
    const process = cp.spawn(pythonPath, ['-c', pythonCode], {
        cwd: workspaceFolder
    });
    
    let output = '';
    process.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    process.on('close', () => {
        try {
            const errors = JSON.parse(output || '[]');
            const diags: vscode.Diagnostic[] = errors.map((err: any) => {
                const line = Math.max(0, Math.min(err.line, document.lineCount - 1));
                const range = document.lineAt(line).range;
                const severity = err.severity === 'error' 
                    ? vscode.DiagnosticSeverity.Error 
                    : vscode.DiagnosticSeverity.Warning;
                return new vscode.Diagnostic(range, err.message, severity);
            });
            diagnostics.set(document.uri, diags);
        } catch {
            diagnostics.delete(document.uri);
        }
    });
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
}
