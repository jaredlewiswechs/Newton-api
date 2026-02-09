/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - NEWTON CONSOLE
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The Newton Console - direct interface to the Newton Agent.
 * Ask questions, verify claims, run calculations.
 * 
 * Everything is verified. Everything is logged to the ledger.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { Newton } from '../core/protocol';
import { NWindow } from '../shell/window';
import { Shell } from '../shell/shell';

/**
 * Console message
 */
interface ConsoleMessage {
  type: 'input' | 'output' | 'error' | 'system';
  content: string;
  timestamp: Date;
  verified?: boolean;
}

/**
 * NConsole - The Newton Console App
 */
export class NConsole {
  private _window?: NWindow;
  private _history: ConsoleMessage[] = [];
  private _inputHistory: string[] = [];
  private _historyIndex: number = -1;
  
  constructor() {
    // Welcome message
    this._history.push({
      type: 'system',
      content: 'Newton Console v0.1.0',
      timestamp: new Date(),
    });
    this._history.push({
      type: 'system',
      content: `Connected to Newton Agent: ${Newton.state}`,
      timestamp: new Date(),
    });
    this._history.push({
      type: 'system',
      content: 'Commands: ask, verify, calculate, ground, help',
      timestamp: new Date(),
    });
  }
  
  /**
   * Open the console
   */
  open(): NWindow {
    if (this._window) {
      this._window.bringToFront();
      return this._window;
    }
    
    this._window = Shell.createWindow('Newton Console', {
      x: 100,
      y: 300,
      width: 700,
      height: 450,
    });
    
    this.refresh();
    
    return this._window;
  }
  
  /**
   * Process a command
   */
  async process(input: string): Promise<void> {
    const trimmed = input.trim();
    if (!trimmed) return;
    
    // Add to history
    this._inputHistory.push(trimmed);
    this._historyIndex = -1;
    
    // Log input
    this._history.push({
      type: 'input',
      content: trimmed,
      timestamp: new Date(),
    });
    
    this.refresh();
    
    // Parse command
    const parts = trimmed.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1).join(' ');
    
    try {
      switch (cmd) {
        case 'ask':
          await this._handleAsk(args);
          break;
        case 'verify':
          await this._handleVerify(args);
          break;
        case 'calculate':
        case 'calc':
          await this._handleCalculate(args);
          break;
        case 'ground':
          await this._handleGround(args);
          break;
        case 'ledger':
          await this._handleLedger();
          break;
        case 'health':
          await this._handleHealth();
          break;
        case 'clear':
          this._history = [];
          break;
        case 'help':
          this._showHelp();
          break;
        default:
          // Treat as ask by default
          if (trimmed.endsWith('?')) {
            await this._handleAsk(trimmed);
          } else {
            this._output(`Unknown command: ${cmd}. Type 'help' for commands.`, 'error');
          }
      }
    } catch (error) {
      this._output(`Error: ${(error as Error).message}`, 'error');
    }
    
    this.refresh();
  }
  
  /**
   * Handle ask command
   */
  private async _handleAsk(question: string): Promise<void> {
    if (!question) {
      this._output('Usage: ask <question>', 'error');
      return;
    }
    
    this._output('Thinking...', 'system');
    this.refresh();
    
    try {
      const result = await Newton.ask(question);
      
      this._history.pop(); // Remove "Thinking..."
      this._history.push({
        type: 'output',
        content: result.answer,
        timestamp: new Date(),
        verified: result.verified,
      });
      
      this._output(`Confidence: ${(result.confidence * 100).toFixed(1)}% | Ledger: #${result.ledgerIndex}`, 'system');
      
      if (result.sources.length > 0) {
        this._output(`Sources: ${result.sources.join(', ')}`, 'system');
      }
    } catch (e) {
      this._history.pop();
      this._output(`Failed to get answer: ${(e as Error).message}`, 'error');
    }
  }
  
  /**
   * Handle verify command
   */
  private async _handleVerify(args: string): Promise<void> {
    // Parse: verify "content" against "claim"
    const match = args.match(/"([^"]+)"\s+against\s+"([^"]+)"/);
    
    if (!match) {
      this._output('Usage: verify "content" against "claim"', 'error');
      return;
    }
    
    const [, content, claim] = match;
    
    this._output('Verifying...', 'system');
    this.refresh();
    
    try {
      const result = await Newton.verify(content, claim);
      
      this._history.pop();
      this._history.push({
        type: 'output',
        content: result.verified ? '✓ VERIFIED' : '✗ NOT VERIFIED',
        timestamp: new Date(),
        verified: result.verified,
      });
      
      if (result.confidence !== undefined) {
        this._output(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 'system');
      }
    } catch (e) {
      this._history.pop();
      this._output(`Verification failed: ${(e as Error).message}`, 'error');
    }
  }
  
  /**
   * Handle calculate command
   */
  private async _handleCalculate(expr: string): Promise<void> {
    if (!expr) {
      this._output('Usage: calculate <expression>', 'error');
      this._output('Example: calculate {"op": "+", "args": [2, 3]}', 'system');
      return;
    }
    
    try {
      const expression = JSON.parse(expr);
      const result = await Newton.calculate(expression);
      
      this._history.push({
        type: 'output',
        content: `= ${JSON.stringify(result.result)}`,
        timestamp: new Date(),
        verified: result.verified,
      });
      
      this._output(`Elapsed: ${result.elapsed_us}μs`, 'system');
    } catch (e) {
      if ((e as Error).message.includes('JSON')) {
        this._output('Invalid JSON expression', 'error');
      } else {
        this._output(`Calculation failed: ${(e as Error).message}`, 'error');
      }
    }
  }
  
  /**
   * Handle ground command
   */
  private async _handleGround(claim: string): Promise<void> {
    if (!claim) {
      this._output('Usage: ground <claim>', 'error');
      return;
    }
    
    this._output('Grounding in external sources...', 'system');
    this.refresh();
    
    try {
      const result = await Newton.ground(claim);
      
      this._history.pop();
      this._history.push({
        type: 'output',
        content: result.grounded ? '✓ GROUNDED' : '✗ NOT GROUNDED',
        timestamp: new Date(),
        verified: result.grounded,
      });
      
      this._output(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 'system');
      
      if (result.sources.length > 0) {
        this._output(`Sources: ${result.sources.join(', ')}`, 'system');
      }
    } catch (e) {
      this._history.pop();
      this._output(`Grounding failed: ${(e as Error).message}`, 'error');
    }
  }
  
  /**
   * Handle ledger command
   */
  private async _handleLedger(): Promise<void> {
    try {
      const entries = await Newton.getLedger(0, 5);
      
      this._output(`Ledger (last ${entries.length} entries):`, 'system');
      
      for (const entry of entries) {
        this._output(`#${entry.index} ${entry.operation} - ${entry.hash.slice(0, 16)}...`, 'output');
      }
    } catch (e) {
      this._output(`Failed to fetch ledger: ${(e as Error).message}`, 'error');
    }
  }
  
  /**
   * Handle health command
   */
  private async _handleHealth(): Promise<void> {
    try {
      const health = await Newton.health();
      
      this._output(`Status: ${health.status}`, 'output');
      this._output(`Version: ${health.version}`, 'system');
      this._output(`Uptime: ${health.uptime}s`, 'system');
    } catch (e) {
      this._output(`Newton Agent not available: ${(e as Error).message}`, 'error');
    }
  }
  
  /**
   * Show help
   */
  private _showHelp(): void {
    this._output('Newton Console Commands:', 'system');
    this._output('  ask <question>          Ask Newton a question', 'output');
    this._output('  verify "x" against "y"  Verify content against claim', 'output');
    this._output('  calculate <json>        Run verified calculation', 'output');
    this._output('  ground <claim>          Ground claim in sources', 'output');
    this._output('  ledger                  View recent ledger entries', 'output');
    this._output('  health                  Check Newton Agent status', 'output');
    this._output('  clear                   Clear console', 'output');
    this._output('  help                    Show this help', 'output');
  }
  
  /**
   * Add output message
   */
  private _output(content: string, type: 'output' | 'error' | 'system' = 'output'): void {
    this._history.push({
      type,
      content,
      timestamp: new Date(),
    });
  }
  
  /**
   * Refresh display
   */
  refresh(): void {
    if (!this._window) return;
    
    this._window.setContent(this._render());
    
    // Scroll to bottom
    setTimeout(() => {
      const output = this._window?.contentElement?.querySelector('.console-output');
      if (output) {
        output.scrollTop = output.scrollHeight;
      }
    }, 0);
  }
  
  /**
   * Render the console
   */
  private _render(): string {
    return `
      <div style="
        height: 100%;
        display: flex;
        flex-direction: column;
        background: #1e1e1e;
        color: #d4d4d4;
        font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        font-size: 13px;
      ">
        <!-- Output -->
        <div class="console-output" style="flex: 1; overflow: auto; padding: 12px;">
          ${this._history.map(msg => this._renderMessage(msg)).join('')}
        </div>
        
        <!-- Input -->
        <div style="
          display: flex;
          align-items: center;
          padding: 8px 12px;
          background: #252526;
          border-top: 1px solid #333;
        ">
          <span style="color: #569cd6; margin-right: 8px;">newton></span>
          <input 
            type="text" 
            id="console-input"
            placeholder="Type a command or question..."
            style="
              flex: 1;
              background: transparent;
              border: none;
              color: #d4d4d4;
              font-family: inherit;
              font-size: inherit;
              outline: none;
            "
            onkeydown="if(event.key==='Enter'){window.NewtonOS?.Console?.process?.(this.value);this.value='';}"
          >
        </div>
      </div>
    `;
  }
  
  /**
   * Render a message
   */
  private _renderMessage(msg: ConsoleMessage): string {
    const colors: Record<string, string> = {
      input: '#569cd6',
      output: '#d4d4d4',
      error: '#f14c4c',
      system: '#6a9955',
    };
    
    const prefix = msg.type === 'input' ? '> ' : '';
    const verifiedBadge = msg.verified !== undefined 
      ? `<span style="color: ${msg.verified ? '#4ec9b0' : '#f14c4c'}; margin-left: 8px;">
           ${msg.verified ? '✓' : '✗'}
         </span>`
      : '';
    
    return `
      <div style="margin-bottom: 4px; color: ${colors[msg.type]};">
        ${prefix}${this._escapeHtml(msg.content)}${verifiedBadge}
      </div>
    `;
  }
  
  /**
   * Escape HTML
   */
  private _escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

// Singleton
export const Console = new NConsole();

export default NConsole;
