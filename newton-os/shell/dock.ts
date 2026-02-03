/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - DOCK
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The Dock - iconic application launcher
 * 
 * - Squircle icons (of course)
 * - Magnification on hover
 * - Running indicators
 * - Minimized windows
 * 
 * "Where NeXTSTEP meets the continuous curve."
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { NObjectId } from '../core/nobject';

/**
 * Dock item (app or minimized window)
 */
export interface DockItem {
  id: string;
  type: 'app' | 'window';
  name: string;
  icon: string;           // SVG or emoji
  running: boolean;
  objectId?: NObjectId;   // Reference to NObject
}

/**
 * Dock configuration
 */
export interface DockConfig {
  position: 'bottom' | 'left' | 'right';
  iconSize: number;
  magnification: boolean;
  magnificationScale: number;
  hideAutomatically: boolean;
  showRunningIndicators: boolean;
}

const DefaultDockConfig: DockConfig = {
  position: 'bottom',
  iconSize: 48,
  magnification: true,
  magnificationScale: 1.5,
  hideAutomatically: false,
  showRunningIndicators: true,
};

/**
 * NDock - The application dock
 */
export class NDock {
  private _items: DockItem[] = [];
  private _config: DockConfig;
  private _element?: HTMLElement;
  private _hoveredIndex: number = -1;
  
  constructor(config: Partial<DockConfig> = {}) {
    this._config = { ...DefaultDockConfig, ...config };
    
    // Default apps
    this._items = [
      { id: 'finder', type: 'app', name: 'Finder', icon: '📁', running: true },
      { id: 'inspector', type: 'app', name: 'Inspector', icon: '🔍', running: false },
      { id: 'terminal', type: 'app', name: 'Terminal', icon: '⬛', running: false },
      { id: 'newton', type: 'app', name: 'Newton', icon: '🍎', running: true },
      { id: 'settings', type: 'app', name: 'Settings', icon: '⚙️', running: false },
    ];
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // ITEMS
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Add an item to the dock
   */
  addItem(item: DockItem): void {
    this._items.push(item);
    this._updateElement();
  }
  
  /**
   * Remove an item
   */
  removeItem(id: string): void {
    this._items = this._items.filter(i => i.id !== id);
    this._updateElement();
  }
  
  /**
   * Update item state
   */
  updateItem(id: string, updates: Partial<DockItem>): void {
    const item = this._items.find(i => i.id === id);
    if (item) {
      Object.assign(item, updates);
      this._updateElement();
    }
  }
  
  /**
   * Add minimized window to dock
   */
  addMinimizedWindow(windowId: NObjectId, name: string, icon: string): void {
    this.addItem({
      id: `window-${windowId}`,
      type: 'window',
      name,
      icon,
      running: true,
      objectId: windowId,
    });
  }
  
  /**
   * Remove minimized window from dock
   */
  removeMinimizedWindow(windowId: NObjectId): void {
    this.removeItem(`window-${windowId}`);
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // RENDERING
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Render the dock
   */
  render(container: HTMLElement): HTMLElement {
    if (this._element) {
      this._element.remove();
    }
    
    const dock = document.createElement('div');
    dock.className = 'ndock';
    dock.style.cssText = this._getDockStyle();
    
    // Dock background (squircle)
    const bg = document.createElement('div');
    bg.className = 'ndock-bg';
    bg.style.cssText = `
      position: absolute;
      inset: 0;
      background: rgba(255, 255, 255, 0.3);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.5);
    `;
    dock.appendChild(bg);
    
    // Items container
    const itemsContainer = document.createElement('div');
    itemsContainer.className = 'ndock-items';
    itemsContainer.style.cssText = `
      display: flex;
      gap: 4px;
      padding: 4px 8px;
      position: relative;
      z-index: 1;
    `;
    
    // Render each item
    this._items.forEach((item, index) => {
      const itemEl = this._renderItem(item, index);
      itemsContainer.appendChild(itemEl);
    });
    
    dock.appendChild(itemsContainer);
    
    // Add separator before minimized windows
    const apps = this._items.filter(i => i.type === 'app');
    const windows = this._items.filter(i => i.type === 'window');
    
    if (apps.length > 0 && windows.length > 0) {
      const separator = document.createElement('div');
      separator.className = 'ndock-separator';
      separator.style.cssText = `
        width: 1px;
        height: ${this._config.iconSize - 16}px;
        background: rgba(0, 0, 0, 0.2);
        margin: 0 8px;
        align-self: center;
      `;
      // Insert separator at the right position
      const sepIndex = apps.length;
      itemsContainer.insertBefore(separator, itemsContainer.children[sepIndex]);
    }
    
    container.appendChild(dock);
    this._element = dock;
    
    return dock;
  }
  
  /**
   * Get dock container style
   */
  private _getDockStyle(): string {
    const base = `
      position: fixed;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    `;
    
    switch (this._config.position) {
      case 'bottom':
        return base + `
          bottom: 8px;
          left: 50%;
          transform: translateX(-50%);
        `;
      case 'left':
        return base + `
          left: 8px;
          top: 50%;
          transform: translateY(-50%);
          flex-direction: column;
        `;
      case 'right':
        return base + `
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          flex-direction: column;
        `;
    }
  }
  
  /**
   * Render a dock item
   */
  private _renderItem(item: DockItem, index: number): HTMLElement {
    const itemEl = document.createElement('div');
    itemEl.className = 'ndock-item';
    itemEl.setAttribute('data-item-id', item.id);
    itemEl.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transition: transform 0.15s ease;
    `;
    
    // Icon (squircle)
    const icon = document.createElement('div');
    icon.className = 'ndock-icon';
    icon.style.cssText = `
      width: ${this._config.iconSize}px;
      height: ${this._config.iconSize}px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: ${this._config.iconSize * 0.6}px;
      background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,240,240,0.9));
      border-radius: ${this._config.iconSize * 0.22}px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    `;
    icon.textContent = item.icon;
    
    // Magnification on hover
    if (this._config.magnification) {
      itemEl.addEventListener('mouseenter', () => {
        this._hoveredIndex = index;
        this._applyMagnification();
      });
      
      itemEl.addEventListener('mouseleave', () => {
        this._hoveredIndex = -1;
        this._resetMagnification();
      });
    }
    
    // Click handler
    itemEl.addEventListener('click', () => {
      this._onItemClick(item);
    });
    
    // Running indicator
    if (this._config.showRunningIndicators && item.running) {
      const indicator = document.createElement('div');
      indicator.className = 'ndock-running';
      indicator.style.cssText = `
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.4);
        margin-top: 2px;
      `;
      itemEl.appendChild(icon);
      itemEl.appendChild(indicator);
    } else {
      itemEl.appendChild(icon);
    }
    
    return itemEl;
  }
  
  /**
   * Apply magnification effect
   */
  private _applyMagnification(): void {
    if (!this._element) return;
    
    const items = this._element.querySelectorAll('.ndock-item');
    items.forEach((item, i) => {
      const distance = Math.abs(i - this._hoveredIndex);
      const scale = distance === 0 
        ? this._config.magnificationScale 
        : Math.max(1, this._config.magnificationScale - distance * 0.2);
      
      (item as HTMLElement).style.transform = `scale(${scale})`;
      (item as HTMLElement).style.transformOrigin = 'bottom center';
    });
  }
  
  /**
   * Reset magnification
   */
  private _resetMagnification(): void {
    if (!this._element) return;
    
    const items = this._element.querySelectorAll('.ndock-item');
    items.forEach(item => {
      (item as HTMLElement).style.transform = 'scale(1)';
    });
  }
  
  /**
   * Update the element
   */
  private _updateElement(): void {
    if (!this._element) return;
    
    const container = this._element.parentElement;
    if (container) {
      this.render(container);
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // EVENTS
  // ═══════════════════════════════════════════════════════════════════════
  
  private _onItemClick(item: DockItem): void {
    console.log('[Dock] Item clicked:', item.name);
    
    if (item.type === 'window' && item.objectId) {
      // Restore minimized window
      // TODO: emit event or call window manager
    } else {
      // Launch or focus app
      // TODO: emit event
    }
    
    // Update running state
    this.updateItem(item.id, { running: true });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════════════════
  
  get items(): readonly DockItem[] {
    return this._items;
  }
  
  get config(): DockConfig {
    return { ...this._config };
  }
  
  setConfig(config: Partial<DockConfig>): void {
    this._config = { ...this._config, ...config };
    this._updateElement();
  }
}

export default NDock;
