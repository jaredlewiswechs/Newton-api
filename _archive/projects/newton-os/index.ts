/**
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 *    ███╗   ██╗███████╗██╗    ██╗████████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗
 *    ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██╔═══██╗████╗  ██║    ██╔═══██╗██╔════╝
 *    ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██╔██╗ ██║    ██║   ██║███████╗
 *    ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██║╚██╗██║    ██║   ██║╚════██║
 *    ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██║ ╚████║    ╚██████╔╝███████║
 *    ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝
 * 
 *    Your Computer in a Browser
 *    Built on Verified Computation
 * 
 *    "Squares and circles suck." - The Squircle Revolution
 * 
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * ARCHITECTURE
 * ────────────
 * 
 * Layer 0: NBezierObject
 *   └─ The universal shape primitive
 *   └─ Superellipse/squircle (n=5 for Apple aesthetic)
 *   └─ Continuous curves, no discontinuities
 * 
 * Layer 1: NObject  
 *   └─ The universal object
 *   └─ Reactive properties (RxJS)
 *   └─ Relationships ARE objects
 * 
 * Layer 2: NObjectGraph
 *   └─ "Data Soup" - no files, only objects
 *   └─ Query by constraint, not path
 *   └─ Everything is connected
 * 
 * Layer 3: NewtonProtocol
 *   └─ Bridge to Newton Agent
 *   └─ Verified computation
 *   └─ Immutable ledger
 * 
 * Layer 4: NShell
 *   └─ Desktop environment
 *   └─ Windows, Dock, Menu Bar
 *   └─ All squircles
 * 
 * ═══════════════════════════════════════════════════════════════════════════
 */

// Core
export * from './core';

// Shell
export * from './shell';

// Main entry point
import { Shell } from './shell';
import { Newton } from './core';

/**
 * Boot Newton OS
 */
export async function boot(container?: HTMLElement): Promise<void> {
  console.log(`
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   NEWTON OS                                                   ║
    ║   Your Computer in a Browser                                  ║
    ║                                                               ║
    ║   "The constraint IS the instruction"                         ║
    ║   "The verification IS the computation"                       ║
    ║   "The network IS the processor"                              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
  `);
  
  // Get or create container
  const rootContainer = container || document.getElementById('newton-os') || document.body;
  rootContainer.className = 'nshell-container';
  rootContainer.style.cssText = `
    position: fixed;
    inset: 0;
    overflow: hidden;
  `;
  
  // Initialize shell
  await Shell.init(rootContainer);
  
  // Create welcome window
  const welcomeWindow = Shell.createWindow('Welcome to Newton OS', {
    x: 200,
    y: 150,
    width: 500,
    height: 350,
  });
  
  welcomeWindow.setContent(`
    <div style="padding: 16px; font-family: -apple-system, sans-serif;">
      <h1 style="margin: 0 0 16px; font-size: 24px; font-weight: 600;">
        🍎 Newton OS
      </h1>
      <p style="color: #666; line-height: 1.6;">
        Welcome to Newton OS - your computer in a browser, built on verified computation.
      </p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 16px 0;">
      <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">
        Core Principles
      </h3>
      <ul style="color: #666; line-height: 1.8; padding-left: 20px;">
        <li><strong>Everything is an NObject</strong> - reactive, verified</li>
        <li><strong>Relationships are objects</strong> - first-class citizens</li>
        <li><strong>Squircles everywhere</strong> - continuous curves, no corners</li>
        <li><strong>Query by constraint</strong> - not by path</li>
        <li><strong>Verified by Newton</strong> - trusted computation</li>
      </ul>
      <hr style="border: none; border-top: 1px solid #eee; margin: 16px 0;">
      <div style="display: flex; gap: 8px; align-items: center;">
        <span style="font-size: 12px; color: ${Newton.state === 'connected' ? '#28c840' : '#ff5f57'};">
          ● Newton Agent: ${Newton.state === 'connected' ? 'Connected' : 'Offline'}
        </span>
      </div>
    </div>
  `);
  
  console.log('[Newton OS] Boot complete');
}

// Auto-boot if in browser
if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    // Only auto-boot if newton-os element exists
    const container = document.getElementById('newton-os');
    if (container) {
      boot(container);
    }
  });
}

export default { boot, Shell, Newton };
