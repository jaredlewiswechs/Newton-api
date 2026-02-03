/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - NWINDOW
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Layer 4: The Shell
 * 
 * Windows in Newton OS are:
 * - Squircles (continuous curves, no sharp corners)
 * - NObjects (reactive, verified)
 * - Beautiful (Aqua-inspired, but evolved)
 * 
 * Every window is a squircle. Every squircle is a bezier.
 * "Squares and circles suck."
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { NBezierObject, NShapes, Point } from '../core/bezier';
import { NObject, NObjectFactory, NObjectId } from '../core/nobject';
import { TheGraph } from '../core/graph';

/**
 * Window state
 */
export type WindowState = 'normal' | 'minimized' | 'maximized' | 'fullscreen';

/**
 * Window decoration style
 */
export interface WindowStyle {
  // Shape
  cornerRadius: number;      // Squircle corner radius
  superellipseN: number;     // Superellipse parameter (5 = Apple squircle)
  
  // Colors
  backgroundColor: string;
  borderColor: string;
  shadowColor: string;
  titleBarColor: string;
  
  // Effects
  shadowBlur: number;
  shadowOffset: Point;
  opacity: number;
  blur: number;             // Background blur (vibrancy)
  
  // Title bar
  titleBarHeight: number;
  buttonSize: number;
  buttonSpacing: number;
}

/**
 * Default window style - Aqua-inspired but evolved
 */
export const DefaultWindowStyle: WindowStyle = {
  cornerRadius: 10,
  superellipseN: 5,         // Apple's squircle
  
  backgroundColor: 'rgba(255, 255, 255, 0.85)',
  borderColor: 'rgba(0, 0, 0, 0.1)',
  shadowColor: 'rgba(0, 0, 0, 0.3)',
  titleBarColor: 'rgba(246, 246, 246, 0.9)',
  
  shadowBlur: 30,
  shadowOffset: { x: 0, y: 10 },
  opacity: 1,
  blur: 20,
  
  titleBarHeight: 28,
  buttonSize: 12,
  buttonSpacing: 8,
};

/**
 * NWindow - A window in Newton OS
 */
export class NWindow {
  readonly id: NObjectId;
  readonly object: NObject;
  
  private _shape: NBezierObject;
  private _element?: HTMLElement;
  private _style: WindowStyle;
  
  // Drag state
  private _isDragging: boolean = false;
  private _dragOffset: Point = { x: 0, y: 0 };
  
  constructor(
    title: string,
    x: number,
    y: number,
    width: number,
    height: number,
    style: Partial<WindowStyle> = {}
  ) {
    // Create the NObject
    this.object = NObjectFactory.window(title, x, y, width, height);
    this.id = this.object.id;
    
    // Add to the graph
    TheGraph.add(this.object);
    
    // Merge style
    this._style = { ...DefaultWindowStyle, ...style };
    
    // Create the squircle shape
    this._shape = NShapes.window(
      x + width / 2,
      y + height / 2,
      width,
      height
    );
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // PROPERTIES (reactive via NObject)
  // ═══════════════════════════════════════════════════════════════════════
  
  get title(): string {
    return this.object.getProperty<string>('title') || '';
  }
  
  set title(value: string) {
    this.object.setProperty('title', value);
    this._updateElement();
  }
  
  get x(): number {
    return this.object.getProperty<number>('x') || 0;
  }
  
  set x(value: number) {
    this.object.setProperty('x', value);
    this._updateShape();
    this._updateElement();
  }
  
  get y(): number {
    return this.object.getProperty<number>('y') || 0;
  }
  
  set y(value: number) {
    this.object.setProperty('y', value);
    this._updateShape();
    this._updateElement();
  }
  
  get width(): number {
    return this.object.getProperty<number>('width') || 400;
  }
  
  set width(value: number) {
    this.object.setProperty('width', Math.max(200, value));
    this._updateShape();
    this._updateElement();
  }
  
  get height(): number {
    return this.object.getProperty<number>('height') || 300;
  }
  
  set height(value: number) {
    this.object.setProperty('height', Math.max(100, value));
    this._updateShape();
    this._updateElement();
  }
  
  get visible(): boolean {
    return this.object.getProperty<boolean>('visible') ?? true;
  }
  
  set visible(value: boolean) {
    this.object.setProperty('visible', value);
    this._updateElement();
  }
  
  get minimized(): boolean {
    return this.object.getProperty<boolean>('minimized') ?? false;
  }
  
  get state(): WindowState {
    return this.object.getProperty<WindowState>('state') || 'normal';
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // SHAPE
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Update the squircle shape
   */
  private _updateShape(): void {
    this._shape = NShapes.window(
      this.x + this.width / 2,
      this.y + this.height / 2,
      this.width,
      this.height
    );
  }
  
  /**
   * Get the window's SVG path (squircle)
   */
  get svgPath(): string {
    return this._shape.toSVGPath();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // RENDERING
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Render the window to DOM
   */
  render(container: HTMLElement): HTMLElement {
    if (this._element) {
      this._element.remove();
    }
    
    // Create window element
    const el = document.createElement('div');
    el.className = 'nwindow';
    el.id = `nwindow-${this.id}`;
    el.setAttribute('data-nobject-id', this.id);
    
    // Apply styles
    el.style.cssText = `
      position: absolute;
      left: ${this.x}px;
      top: ${this.y}px;
      width: ${this.width}px;
      height: ${this.height}px;
      background: ${this._style.backgroundColor};
      border-radius: ${this._style.cornerRadius}px;
      box-shadow: ${this._style.shadowOffset.x}px ${this._style.shadowOffset.y}px ${this._style.shadowBlur}px ${this._style.shadowColor};
      border: 1px solid ${this._style.borderColor};
      overflow: hidden;
      display: ${this.visible ? 'flex' : 'none'};
      flex-direction: column;
      backdrop-filter: blur(${this._style.blur}px);
      -webkit-backdrop-filter: blur(${this._style.blur}px);
    `;
    
    // Title bar
    const titleBar = this._renderTitleBar();
    el.appendChild(titleBar);
    
    // Content area
    const content = document.createElement('div');
    content.className = 'nwindow-content';
    content.style.cssText = `
      flex: 1;
      overflow: auto;
      padding: 8px;
    `;
    el.appendChild(content);
    
    // Make draggable
    this._setupDrag(el, titleBar);
    
    // Make resizable
    this._setupResize(el);
    
    container.appendChild(el);
    this._element = el;
    
    return el;
  }
  
  /**
   * Render the title bar
   */
  private _renderTitleBar(): HTMLElement {
    const titleBar = document.createElement('div');
    titleBar.className = 'nwindow-titlebar';
    titleBar.style.cssText = `
      height: ${this._style.titleBarHeight}px;
      background: ${this._style.titleBarColor};
      display: flex;
      align-items: center;
      padding: 0 8px;
      user-select: none;
      cursor: default;
      border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    `;
    
    // Traffic lights (close, minimize, maximize)
    const buttons = document.createElement('div');
    buttons.className = 'nwindow-buttons';
    buttons.style.cssText = `
      display: flex;
      gap: ${this._style.buttonSpacing}px;
    `;
    
    const colors = ['#ff5f57', '#febc2e', '#28c840'];
    const actions = ['close', 'minimize', 'maximize'];
    
    colors.forEach((color, i) => {
      const btn = document.createElement('div');
      btn.className = `nwindow-btn nwindow-btn-${actions[i]}`;
      btn.style.cssText = `
        width: ${this._style.buttonSize}px;
        height: ${this._style.buttonSize}px;
        border-radius: 50%;
        background: ${color};
        cursor: pointer;
      `;
      
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (actions[i] === 'close') this.close();
        else if (actions[i] === 'minimize') this.minimize();
        else if (actions[i] === 'maximize') this.maximize();
      });
      
      buttons.appendChild(btn);
    });
    
    // Title
    const title = document.createElement('div');
    title.className = 'nwindow-title';
    title.textContent = this.title;
    title.style.cssText = `
      flex: 1;
      text-align: center;
      font-size: 13px;
      font-weight: 500;
      color: rgba(0, 0, 0, 0.85);
    `;
    
    titleBar.appendChild(buttons);
    titleBar.appendChild(title);
    
    return titleBar;
  }
  
  /**
   * Update the DOM element
   */
  private _updateElement(): void {
    if (!this._element) return;
    
    this._element.style.left = `${this.x}px`;
    this._element.style.top = `${this.y}px`;
    this._element.style.width = `${this.width}px`;
    this._element.style.height = `${this.height}px`;
    this._element.style.display = this.visible ? 'flex' : 'none';
    
    const titleEl = this._element.querySelector('.nwindow-title');
    if (titleEl) {
      titleEl.textContent = this.title;
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // INTERACTION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Setup drag behavior
   */
  private _setupDrag(el: HTMLElement, handle: HTMLElement): void {
    handle.addEventListener('mousedown', (e) => {
      if ((e.target as HTMLElement).classList.contains('nwindow-btn')) return;
      
      this._isDragging = true;
      this._dragOffset = {
        x: e.clientX - this.x,
        y: e.clientY - this.y,
      };
      
      el.style.zIndex = '1000';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!this._isDragging) return;
      
      this.x = e.clientX - this._dragOffset.x;
      this.y = e.clientY - this._dragOffset.y;
    });
    
    document.addEventListener('mouseup', () => {
      this._isDragging = false;
    });
  }
  
  /**
   * Setup resize behavior
   */
  private _setupResize(el: HTMLElement): void {
    const resizeHandle = document.createElement('div');
    resizeHandle.className = 'nwindow-resize';
    resizeHandle.style.cssText = `
      position: absolute;
      right: 0;
      bottom: 0;
      width: 15px;
      height: 15px;
      cursor: nwse-resize;
    `;
    
    let isResizing = false;
    
    resizeHandle.addEventListener('mousedown', (e) => {
      isResizing = true;
      e.stopPropagation();
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      
      this.width = e.clientX - this.x;
      this.height = e.clientY - this.y;
    });
    
    document.addEventListener('mouseup', () => {
      isResizing = false;
    });
    
    el.appendChild(resizeHandle);
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // ACTIONS
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Close the window
   */
  close(): void {
    this.visible = false;
    if (this._element) {
      this._element.remove();
      this._element = undefined;
    }
    TheGraph.remove(this.id);
  }
  
  /**
   * Minimize the window
   */
  minimize(): void {
    this.object.setProperty('minimized', true);
    this.object.setProperty('state', 'minimized');
    if (this._element) {
      this._element.style.display = 'none';
    }
  }
  
  /**
   * Restore from minimized
   */
  restore(): void {
    this.object.setProperty('minimized', false);
    this.object.setProperty('state', 'normal');
    if (this._element) {
      this._element.style.display = 'flex';
    }
  }
  
  /**
   * Maximize the window
   */
  maximize(): void {
    if (this.state === 'maximized') {
      // Restore
      this.object.setProperty('state', 'normal');
      // TODO: restore previous size
    } else {
      this.object.setProperty('state', 'maximized');
      this.x = 0;
      this.y = 0;
      this.width = window.innerWidth;
      this.height = window.innerHeight;
    }
  }
  
  /**
   * Bring to front
   */
  bringToFront(): void {
    if (this._element) {
      this._element.style.zIndex = '1000';
    }
  }
  
  /**
   * Get the content element
   */
  get contentElement(): HTMLElement | null {
    return this._element?.querySelector('.nwindow-content') || null;
  }
  
  /**
   * Set content
   */
  setContent(content: HTMLElement | string): void {
    const contentEl = this.contentElement;
    if (!contentEl) return;
    
    if (typeof content === 'string') {
      contentEl.innerHTML = content;
    } else {
      contentEl.innerHTML = '';
      contentEl.appendChild(content);
    }
  }
}

export default NWindow;
