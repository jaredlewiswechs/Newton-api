/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - DESKTOP SHELL
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The complete shell environment
 * 
 * Brings together:
 * - Window Manager
 * - Dock
 * - Menu Bar
 * - Desktop
 * 
 * All built on squircles and NObjects.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { NObjectId } from '../core/nobject';
import { TheGraph } from '../core/graph';
import { Newton } from '../core/protocol';
import { NWindow } from './window';
import { NDock } from './dock';

/**
 * Shell configuration
 */
export interface ShellConfig {
  // Appearance
  wallpaper?: string;
  accentColor: string;
  darkMode: boolean;
  
  // Dock
  dockPosition: 'bottom' | 'left' | 'right';
  dockMagnification: boolean;
  
  // Menu bar
  showMenuBar: boolean;
  menuBarTranslucent: boolean;
  
  // Windows
  windowAnimation: boolean;
  
  // Newton
  newtonUrl: string;
}

const DefaultShellConfig: ShellConfig = {
  accentColor: '#007AFF',
  darkMode: false,
  dockPosition: 'bottom',
  dockMagnification: true,
  showMenuBar: true,
  menuBarTranslucent: true,
  windowAnimation: true,
  newtonUrl: 'http://localhost:8000',
};

/**
 * NShell - The Newton OS Desktop Shell
 */
export class NShell {
  private _config: ShellConfig;
  private _container?: HTMLElement;
  private _windows: Map<NObjectId, NWindow> = new Map();
  private _dock: NDock;
  private _activeWindowId?: NObjectId;
  
  // Layers
  private _desktopLayer?: HTMLElement;
  private _windowLayer?: HTMLElement;
  private _menuBarLayer?: HTMLElement;
  
  constructor(config: Partial<ShellConfig> = {}) {
    this._config = { ...DefaultShellConfig, ...config };
    this._dock = new NDock({
      position: this._config.dockPosition,
      magnification: this._config.dockMagnification,
    });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Initialize the shell
   */
  async init(container: HTMLElement): Promise<void> {
    this._container = container;
    
    // Apply global styles
    this._injectStyles();
    
    // Create layers
    this._createLayers();
    
    // Render components
    this._renderMenuBar();
    this._dock.render(this._container);
    
    // Connect to Newton
    try {
      await Newton.connect();
      console.log('[Shell] Connected to Newton Agent');
    } catch (e) {
      console.warn('[Shell] Newton Agent not available, running in offline mode');
    }
    
    // Listen for graph changes
    TheGraph.mutations$.subscribe((mutation: { type: string; objectId: string; object?: { type: string } }) => {
      if (mutation.type === 'add' && mutation.object?.type === 'window') {
        // Auto-render new windows
        // This would be handled by window creation API
      }
    });
    
    console.log('[Shell] Newton OS Shell initialized');
  }
  
  /**
   * Create shell layers
   */
  private _createLayers(): void {
    if (!this._container) return;
    
    // Desktop layer (wallpaper, icons)
    this._desktopLayer = document.createElement('div');
    this._desktopLayer.className = 'nshell-desktop';
    this._desktopLayer.style.cssText = `
      position: absolute;
      inset: 0;
      background: ${this._config.wallpaper ? `url(${this._config.wallpaper})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
      background-size: cover;
      background-position: center;
    `;
    this._container.appendChild(this._desktopLayer);
    
    // Window layer
    this._windowLayer = document.createElement('div');
    this._windowLayer.className = 'nshell-windows';
    this._windowLayer.style.cssText = `
      position: absolute;
      inset: 0;
      pointer-events: none;
    `;
    this._windowLayer.addEventListener('mousedown', (e) => {
      // Handle window focus
      const target = e.target as HTMLElement;
      const windowEl = target.closest('.nwindow');
      if (windowEl) {
        const id = windowEl.getAttribute('data-nobject-id');
        if (id) this.focusWindow(id);
      }
    });
    this._container.appendChild(this._windowLayer);
    
    // Enable pointer events on windows themselves
    const style = document.createElement('style');
    style.textContent = `.nshell-windows .nwindow { pointer-events: auto; }`;
    document.head.appendChild(style);
  }
  
  /**
   * Inject global styles
   */
  private _injectStyles(): void {
    const styles = document.createElement('style');
    styles.id = 'newton-os-styles';
    styles.textContent = `
      * {
        box-sizing: border-box;
      }
      
      body {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
        overflow: hidden;
        user-select: none;
      }
      
      .nshell-container {
        position: fixed;
        inset: 0;
        overflow: hidden;
      }
      
      /* Squircle clip path */
      .squircle {
        clip-path: url(#squircle);
      }
      
      /* Smooth animations */
      .nwindow {
        transition: ${this._config.windowAnimation ? 'transform 0.2s ease, opacity 0.2s ease' : 'none'};
      }
      
      .nwindow:active {
        transition: none;
      }
      
      /* Selection */
      ::selection {
        background: ${this._config.accentColor}40;
      }
    `;
    
    document.head.appendChild(styles);
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // MENU BAR
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Render the menu bar
   */
  private _renderMenuBar(): void {
    if (!this._container || !this._config.showMenuBar) return;
    
    this._menuBarLayer = document.createElement('div');
    this._menuBarLayer.className = 'nshell-menubar';
    this._menuBarLayer.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 24px;
      background: ${this._config.menuBarTranslucent ? 'rgba(255, 255, 255, 0.7)' : 'white'};
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      display: flex;
      align-items: center;
      padding: 0 12px;
      font-size: 13px;
      font-weight: 500;
      z-index: 10000;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    `;
    
    // Apple menu (Newton logo)
    const appleMenu = document.createElement('div');
    appleMenu.className = 'menubar-apple';
    appleMenu.textContent = '🍎';
    appleMenu.style.cssText = `
      margin-right: 16px;
      cursor: pointer;
    `;
    
    // App name
    const appName = document.createElement('div');
    appName.className = 'menubar-appname';
    appName.textContent = 'Newton OS';
    appName.style.cssText = `
      font-weight: 600;
      margin-right: 24px;
    `;
    
    // Menus
    const menus = ['File', 'Edit', 'View', 'Window', 'Help'];
    const menuContainer = document.createElement('div');
    menuContainer.style.cssText = `display: flex; gap: 16px;`;
    
    menus.forEach(menu => {
      const menuEl = document.createElement('div');
      menuEl.textContent = menu;
      menuEl.style.cssText = `cursor: pointer;`;
      menuContainer.appendChild(menuEl);
    });
    
    // Right side - clock, status
    const rightSide = document.createElement('div');
    rightSide.style.cssText = `
      margin-left: auto;
      display: flex;
      gap: 16px;
      align-items: center;
    `;
    
    // Newton status
    const newtonStatus = document.createElement('div');
    newtonStatus.className = 'menubar-newton';
    newtonStatus.innerHTML = '✓ Newton';
    newtonStatus.style.cssText = `
      color: ${Newton.state === 'connected' ? '#28c840' : '#999'};
      font-size: 12px;
    `;
    
    // Clock
    const clock = document.createElement('div');
    clock.className = 'menubar-clock';
    const updateClock = () => {
      const now = new Date();
      clock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    updateClock();
    setInterval(updateClock, 1000);
    
    rightSide.appendChild(newtonStatus);
    rightSide.appendChild(clock);
    
    this._menuBarLayer.appendChild(appleMenu);
    this._menuBarLayer.appendChild(appName);
    this._menuBarLayer.appendChild(menuContainer);
    this._menuBarLayer.appendChild(rightSide);
    
    this._container.appendChild(this._menuBarLayer);
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // WINDOW MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Create a new window
   */
  createWindow(title: string, options: {
    x?: number;
    y?: number;
    width?: number;
    height?: number;
  } = {}): NWindow {
    const x = options.x ?? 100 + this._windows.size * 30;
    const y = options.y ?? 100 + this._windows.size * 30;
    const width = options.width ?? 600;
    const height = options.height ?? 400;
    
    const window = new NWindow(title, x, y, width, height);
    this._windows.set(window.id, window);
    
    if (this._windowLayer) {
      window.render(this._windowLayer);
    }
    
    this.focusWindow(window.id);
    
    return window;
  }
  
  /**
   * Get a window by ID
   */
  getWindow(id: NObjectId): NWindow | undefined {
    return this._windows.get(id);
  }
  
  /**
   * Focus a window
   */
  focusWindow(id: NObjectId): void {
    const window = this._windows.get(id);
    if (!window) return;
    
    // Unfocus others
    for (const w of this._windows.values()) {
      if (w.id !== id) {
        // Lower z-index
      }
    }
    
    window.bringToFront();
    this._activeWindowId = id;
  }
  
  /**
   * Get all windows
   */
  get windows(): NWindow[] {
    return Array.from(this._windows.values());
  }
  
  /**
   * Get active window
   */
  get activeWindow(): NWindow | undefined {
    return this._activeWindowId ? this._windows.get(this._activeWindowId) : undefined;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // DOCK
  // ═══════════════════════════════════════════════════════════════════════
  
  get dock(): NDock {
    return this._dock;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════════════
  
  get config(): ShellConfig {
    return { ...this._config };
  }
  
  setConfig(config: Partial<ShellConfig>): void {
    this._config = { ...this._config, ...config };
    // Re-render affected components
  }
  
  /**
   * Set wallpaper
   */
  setWallpaper(url: string): void {
    this._config.wallpaper = url;
    if (this._desktopLayer) {
      this._desktopLayer.style.backgroundImage = `url(${url})`;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GLOBAL SHELL INSTANCE
// ═══════════════════════════════════════════════════════════════════════════

export const Shell = new NShell();

export default NShell;
