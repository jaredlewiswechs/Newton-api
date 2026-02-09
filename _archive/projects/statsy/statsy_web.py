#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
STATSY WEB - Beautiful Browser-Based Statistical Computing
═══════════════════════════════════════════════════════════════════════════════

A clean, academic-focused web interface for Statsy.
Designed for students and professors who need statistics that just work.

Run: python statsy/statsy_web.py
Open: http://localhost:5000

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import io
import json
import traceback
from contextlib import redirect_stdout, redirect_stderr

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify
from statsy import StatsyLexer, StatsyParser, StatsyInterpreter

app = Flask(__name__)

# Store session state
sessions = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Statsy - Verified Statistical Computing</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f1419;
            --bg-secondary: #1a1f26;
            --bg-tertiary: #242b33;
            --accent-blue: #4c9eff;
            --accent-green: #3fb950;
            --accent-yellow: #d29922;
            --accent-red: #f85149;
            --accent-purple: #a371f7;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --border-color: #30363d;
            --success-bg: rgba(63, 185, 80, 0.1);
            --error-bg: rgba(248, 81, 73, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo-tagline {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 2px;
        }
        
        .header-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid var(--border-color);
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }
        
        .btn:hover {
            background: var(--bg-secondary);
            border-color: var(--accent-blue);
        }
        
        .btn-primary {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
            color: white;
        }
        
        .btn-primary:hover {
            background: #3d8bdb;
            border-color: #3d8bdb;
        }
        
        .btn-success {
            background: var(--accent-green);
            border-color: var(--accent-green);
            color: white;
        }
        
        .btn-success:hover {
            background: #2ea043;
        }
        
        /* Main Layout */
        main {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        
        .sidebar-section {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .sidebar-title {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.75rem;
        }
        
        .example-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .example-btn {
            padding: 0.625rem 0.875rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.8125rem;
            text-align: left;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        
        .example-btn:hover {
            background: var(--bg-primary);
            border-color: var(--accent-blue);
        }
        
        .example-btn .example-name {
            font-weight: 500;
            margin-bottom: 2px;
        }
        
        .example-btn .example-desc {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        /* Editor Area */
        .editor-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .toolbar {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .toolbar-group {
            display: flex;
            gap: 0.5rem;
        }
        
        .toolbar-separator {
            width: 1px;
            height: 24px;
            background: var(--border-color);
            margin: 0 0.5rem;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8125rem;
            color: var(--text-secondary);
            margin-left: auto;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
        }
        
        .status-dot.error {
            background: var(--accent-red);
        }
        
        .panels {
            flex: 1;
            display: flex;
            overflow: hidden;
        }
        
        .panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .panel-header {
            background: var(--bg-tertiary);
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .panel-content {
            flex: 1;
            overflow: auto;
        }
        
        .resizer {
            width: 4px;
            background: var(--border-color);
            cursor: col-resize;
            transition: background 0.15s ease;
        }
        
        .resizer:hover {
            background: var(--accent-blue);
        }
        
        /* Code Editor */
        #code-editor {
            width: 100%;
            height: 100%;
            background: var(--bg-primary);
            border: none;
            resize: none;
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-primary);
            outline: none;
            tab-size: 4;
        }
        
        #code-editor::placeholder {
            color: var(--text-muted);
        }
        
        /* Output */
        #output {
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            background: var(--bg-primary);
            min-height: 100%;
        }
        
        .output-success {
            color: var(--text-primary);
        }
        
        .output-error {
            color: var(--accent-red);
        }
        
        .output-info {
            color: var(--accent-blue);
        }
        
        /* Charts */
        .chart-container {
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            overflow-x: auto;
        }
        
        /* Help Panel */
        .help-section {
            padding: 1rem;
        }
        
        .help-category {
            margin-bottom: 1.5rem;
        }
        
        .help-category-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }
        
        .help-item {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            padding: 0.25rem 0;
            color: var(--text-secondary);
        }
        
        .help-item code {
            color: var(--accent-yellow);
        }
        
        /* Footer */
        footer {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-color);
            padding: 0.75rem 2rem;
            font-size: 0.75rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        footer a {
            color: var(--accent-blue);
            text-decoration: none;
        }
        
        footer a:hover {
            text-decoration: underline;
        }
        
        /* Keyboard shortcut hints */
        kbd {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 0.75rem;
            font-family: inherit;
        }
        
        /* Loading indicator */
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid var(--border-color);
            border-top-color: var(--accent-blue);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .sidebar {
                width: 220px;
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            
            header {
                padding: 0.75rem 1rem;
            }
        }
        
        /* Verification badge */
        .verified-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: var(--success-bg);
            color: var(--accent-green);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .verified-badge::before {
            content: "✓";
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <div class="logo-icon">σ</div>
            <div>
                <div class="logo-text">Statsy</div>
                <div class="logo-tagline">Verified Statistical Computing</div>
            </div>
        </div>
        <div class="header-actions">
            <span class="verified-badge">Newton Verified</span>
            <button class="btn" onclick="showHelp()">📖 Help</button>
            <button class="btn" onclick="clearAll()">🗑️ Clear</button>
        </div>
    </header>
    
    <main>
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-title">Quick Start Examples</div>
                <div class="example-list">
                    <button class="example-btn" onclick="loadExample('descriptive')">
                        <div class="example-name">📊 Descriptive Stats</div>
                        <div class="example-desc">Mean, median, std, describe</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('ttest')">
                        <div class="example-name">🧪 T-Test</div>
                        <div class="example-desc">Two-sample hypothesis test</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('regression')">
                        <div class="example-name">📈 Linear Regression</div>
                        <div class="example-desc">Fit line, R², scatter plot</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('anova')">
                        <div class="example-name">📋 ANOVA</div>
                        <div class="example-desc">Compare multiple groups</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('visualization')">
                        <div class="example-name">📉 Visualization</div>
                        <div class="example-desc">Histogram, boxplot, sparkline</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('outliers')">
                        <div class="example-name">🎯 Outlier Detection</div>
                        <div class="example-desc">Robust stats, MAD, trimmed mean</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('timeseries')">
                        <div class="example-name">⏱️ Time Series</div>
                        <div class="example-desc">Moving avg, smoothing</div>
                    </button>
                    <button class="example-btn" onclick="loadExample('newton')">
                        <div class="example-name">🧠 Newton KB</div>
                        <div class="example-desc">Query knowledge base</div>
                    </button>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Quick Reference</div>
                <div class="help-section">
                    <div class="help-category">
                        <div class="help-category-title">Statistics</div>
                        <div class="help-item"><code>mean(x)</code> median std var</div>
                        <div class="help-item"><code>describe(x)</code> full summary</div>
                        <div class="help-item"><code>t_test(a, b)</code> hypothesis</div>
                        <div class="help-item"><code>cor(x, y)</code> correlation</div>
                    </div>
                    <div class="help-category">
                        <div class="help-category-title">Visualization</div>
                        <div class="help-item"><code>histogram(x)</code></div>
                        <div class="help-item"><code>boxplot(x)</code></div>
                        <div class="help-item"><code>scatter(x, y)</code></div>
                        <div class="help-item"><code>sparkline(x)</code></div>
                    </div>
                    <div class="help-category">
                        <div class="help-category-title">Robust Stats</div>
                        <div class="help-item"><code>mad(x)</code> MAD</div>
                        <div class="help-item"><code>robust_mean(x)</code></div>
                        <div class="help-item"><code>detect_outliers(x)</code></div>
                    </div>
                </div>
            </div>
        </aside>
        
        <div class="editor-container">
            <div class="toolbar">
                <div class="toolbar-group">
                    <button class="btn btn-success" onclick="runCode()">▶ Run</button>
                    <button class="btn" onclick="runSelection()">▶ Run Selection</button>
                </div>
                <div class="toolbar-separator"></div>
                <div class="toolbar-group">
                    <button class="btn" onclick="formatCode()">Format</button>
                </div>
                <div class="status-indicator">
                    <span class="status-dot" id="status-dot"></span>
                    <span id="status-text">Ready</span>
                </div>
            </div>
            
            <div class="panels">
                <div class="panel" style="flex: 1.2;">
                    <div class="panel-header">
                        <span>📝</span> Code Editor
                        <span style="margin-left: auto; font-weight: normal;">
                            <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to run
                        </span>
                    </div>
                    <div class="panel-content">
                        <textarea id="code-editor" placeholder="# Enter your Statsy code here...
# Example:
data = [23, 45, 67, 89, 12, 34, 56, 78, 90, 11]
describe(data)
histogram(data, 5)
"></textarea>
                    </div>
                </div>
                
                <div class="resizer" id="resizer"></div>
                
                <div class="panel" style="flex: 1;">
                    <div class="panel-header">
                        <span>📤</span> Output
                        <button class="btn" style="margin-left: auto; padding: 2px 8px; font-size: 0.7rem;" onclick="copyOutput()">Copy</button>
                    </div>
                    <div class="panel-content">
                        <div id="output" class="output-success"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer>
        <div>© 2026 Jared Lewis · Ada Computing Company · Houston, Texas</div>
        <div>
            <a href="#">Documentation</a> · 
            <a href="#">GitHub</a> · 
            Version 1.0.0
        </div>
    </footer>
    
    <script>
        const editor = document.getElementById('code-editor');
        const output = document.getElementById('output');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        // Examples
        const examples = {
            descriptive: `# Descriptive Statistics
data = c(23, 45, 67, 89, 12, 34, 56, 78, 90, 11)

# Variadic syntax
print("mean(10, 20, 30) =", mean(10, 20, 30))
print("sum(1, 2, 3, 4, 5) =", sum(1, 2, 3, 4, 5))

# Stats for vector
print("Mean:", mean(data))
print("Median:", median(data))
print("Std Dev:", std(data))
print("Variance:", var(data))

describe(data)`,
            
            ttest: `# Two-Sample T-Test
control = c(23, 25, 27, 22, 24, 26, 28, 23, 25, 27)
treatment = c(30, 32, 28, 35, 31, 33, 29, 34, 30, 32)

print("Control - Mean:", mean(control), "Std:", std(control))
print("Treatment - Mean:", mean(treatment), "Std:", std(treatment))

t_test(control, treatment)`,
            
            regression: `# Linear Regression
x = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
y = c(2.1, 4.0, 5.8, 8.2, 9.9, 12.1, 14.0, 16.2, 17.8, 20.1)

model = lm(x, y)
print("Correlation:", cor(x, y))
scatter(x, y, 50, 12, "X vs Y")`,
            
            anova: `# One-Way ANOVA
group_a = c(85, 90, 88, 92, 87, 91, 89, 86)
group_b = c(78, 82, 80, 75, 79, 81, 77, 83)
group_c = c(95, 98, 92, 96, 94, 97, 93, 99)

print("Group A mean:", mean(group_a))
print("Group B mean:", mean(group_b))
print("Group C mean:", mean(group_c))

anova(group_a, group_b, group_c)`,
            
            visualization: `# Data Visualization
data = c(15, 22, 18, 25, 30, 28, 35, 32, 40, 38, 45, 42, 48, 50, 55)

histogram(data, 5, 35, "Data Distribution")
boxplot(data, 45, "Data Summary")

print(sparkline(data, "Trend"))

categories = c("Q1", "Q2", "Q3", "Q4")
values = c(125, 180, 165, 210)
bar_chart(categories, values, 30, "Quarterly Sales")`,
            
            outliers: `# Outlier Detection
data = c(10, 12, 11, 13, 10, 12, 500, 11, 10, 13, 12, 11, 600)

print("Data:", data)
print("Regular mean:", mean(data))

print("MAD:", mad(data))
print("Trimmed mean:", trimmed_mean(data, 0.1))
print("Winsorized mean:", winsorized_mean(data, 0.1))
print("Robust mean:", robust_mean(data))
print("Outliers:", detect_outliers(data, 3.5))

describe(data)`,
            
            timeseries: `# Time Series Analysis
monthly = c(100, 120, 115, 135, 140, 155, 160, 175, 170, 185, 190, 200)

print("Raw:", sparkline(monthly, ""))
ma = moving_avg(monthly, 3)
print("MA(3):", sparkline(ma, ""))
es = exp_smooth(monthly, 0.3)
print("Exp:", sparkline(es, ""))

line_chart(monthly, 50, 10, "Monthly Trend")`,
            
            newton: `# Newton Knowledge Base
newton_ask("What is the speed of light?")
newton_ask("What is standard deviation?")
newton_ask("What is photosynthesis?")
guidance("t-test")`
        };
        
        // Load example
        function loadExample(name) {
            if (examples[name]) {
                editor.value = examples[name];
                output.textContent = '# Click "Run" or press Ctrl+Enter to execute';
                output.className = 'output-info';
            }
        }
        
        // Run code
        async function runCode() {
            const code = editor.value;
            if (!code.trim()) {
                output.textContent = '# No code to run';
                output.className = 'output-info';
                return;
            }
            
            setStatus('running');
            
            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    output.textContent = '❌ Error:\\n' + result.error;
                    output.className = 'output-error';
                    setStatus('error');
                } else {
                    output.textContent = result.output || '✓ Executed successfully (no output)';
                    output.className = 'output-success';
                    setStatus('success');
                }
            } catch (err) {
                output.textContent = '❌ Connection error: ' + err.message;
                output.className = 'output-error';
                setStatus('error');
            }
        }
        
        // Run selection
        function runSelection() {
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            
            if (start === end) {
                runCode();
                return;
            }
            
            const selection = editor.value.substring(start, end);
            const originalCode = editor.value;
            editor.value = selection;
            runCode().then(() => {
                editor.value = originalCode;
                editor.setSelectionRange(start, end);
            });
        }
        
        // Set status
        function setStatus(status) {
            statusDot.className = 'status-dot';
            
            switch(status) {
                case 'running':
                    statusDot.style.background = 'var(--accent-yellow)';
                    statusText.textContent = 'Running...';
                    break;
                case 'success':
                    statusDot.style.background = 'var(--accent-green)';
                    statusText.textContent = 'Success';
                    break;
                case 'error':
                    statusDot.className = 'status-dot error';
                    statusText.textContent = 'Error';
                    break;
                default:
                    statusDot.style.background = 'var(--accent-green)';
                    statusText.textContent = 'Ready';
            }
        }
        
        // Clear all
        function clearAll() {
            editor.value = '';
            output.textContent = '# Output will appear here';
            output.className = 'output-info';
            setStatus('ready');
        }
        
        // Copy output
        function copyOutput() {
            navigator.clipboard.writeText(output.textContent);
        }
        
        // Format code (basic)
        function formatCode() {
            // Simple formatting - could be enhanced
            let code = editor.value;
            // Ensure consistent indentation
            code = code.replace(/\\t/g, '    ');
            editor.value = code;
        }
        
        // Show help
        function showHelp() {
            const helpText = `
╔═══════════════════════════════════════════════════════════════╗
║  STATSY HELP - Quick Reference                                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  DESCRIPTIVE STATISTICS                                       ║
║    mean(x), median(x), mode(x), std(x), var(x)               ║
║    min(x), max(x), sum(x), range(x), quantile(x, p)          ║
║    iqr(x), mad(x), describe(x)                               ║
║                                                               ║
║  HYPOTHESIS TESTS                                             ║
║    t_test(a, b)    - Two-sample t-test                       ║
║    cor(x, y)       - Correlation coefficient                 ║
║    cor_test(x, y)  - Correlation test                        ║
║    anova(g1, g2, g3, ...)  - One-way ANOVA                   ║
║                                                               ║
║  REGRESSION                                                   ║
║    lm(x, y)        - Linear regression                       ║
║                                                               ║
║  VISUALIZATION                                                ║
║    histogram(x, bins, width, title)                          ║
║    boxplot(x, width, title)                                  ║
║    scatter(x, y, width, height, title)                       ║
║    line_chart(x, width, height, title)                       ║
║    bar_chart(labels, values, width, title)                   ║
║    sparkline(x, label)                                       ║
║                                                               ║
║  ROBUST STATISTICS                                            ║
║    robust_mean(x), trimmed_mean(x, trim)                     ║
║    winsorized_mean(x, trim), detect_outliers(x, threshold)   ║
║    modified_zscore(x), is_outlier(val, x, threshold)         ║
║                                                               ║
║  TIME SERIES                                                  ║
║    moving_avg(x, window), exp_smooth(x, alpha)               ║
║                                                               ║
║  NEWTON INTEGRATION                                           ║
║    newton_ask(question)    - Query knowledge base            ║
║    newton_verify(claim)    - Verify a claim                  ║
║    guidance(topic)         - Get statistical guidance        ║
║                                                               ║
║  KEYBOARD SHORTCUTS                                           ║
║    Ctrl+Enter  - Run code                                    ║
║    Ctrl+L      - Clear output                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`;
            output.textContent = helpText;
            output.className = 'output-info';
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                runCode();
            }
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                clearAll();
            }
        });
        
        // Tab key in editor
        editor.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = editor.selectionStart;
                const end = editor.selectionEnd;
                editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
                editor.selectionStart = editor.selectionEnd = start + 4;
            }
        });
        
        // Resizer
        const resizer = document.getElementById('resizer');
        let isResizing = false;
        
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.body.style.cursor = 'col-resize';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            const panels = document.querySelector('.panels');
            const rect = panels.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            
            const leftPanel = panels.children[0];
            const rightPanel = panels.children[2];
            
            leftPanel.style.flex = percent;
            rightPanel.style.flex = 1 - percent;
        });
        
        document.addEventListener('mouseup', () => {
            isResizing = false;
            document.body.style.cursor = '';
        });
        
        // Load initial example
        loadExample('descriptive');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run', methods=['POST'])
def run_code():
    """Execute Statsy code and return output."""
    data = request.get_json()
    code = data.get('code', '')
    
    if not code.strip():
        return jsonify({'output': '', 'error': None})
    
    # Capture stdout
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            lexer = StatsyLexer(code)
            tokens = lexer.tokenize()
            parser = StatsyParser(tokens)
            ast = parser.parse()
            interpreter = StatsyInterpreter()
            result = interpreter.execute(ast)
        
        output = stdout_capture.getvalue()
        
        # Add final result if it's meaningful
        if result is not None and not output.strip().endswith(str(result)):
            if output:
                output += '\n'
            output += f'→ {result}'
        
        return jsonify({'output': output, 'error': None})
    
    except SyntaxError as e:
        return jsonify({'output': '', 'error': f'Syntax Error: {e}'})
    except Exception as e:
        error_msg = f'{type(e).__name__}: {e}'
        return jsonify({'output': '', 'error': error_msg})


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'statsy-web'})


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STATSY WEB - Verified Statistical Computing                                  ║
║  Beautiful browser-based interface for academia                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Starting server...                                                           ║
║                                                                               ║
║  Open your browser to:  http://localhost:5000                                 ║
║                                                                               ║
║  Press Ctrl+C to stop                                                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


if __name__ == '__main__':
    main()
