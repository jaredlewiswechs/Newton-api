/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - OBJECT INSPECTOR
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The Inspector lets you see into the Object Graph.
 * Every NObject, every property, every relationship - visible.
 * 
 * "Glass Box Computing"
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { NObject, NObjectId, NValue, NRelationship } from '../core/nobject';
import { NObjectGraph, TheGraph } from '../core/graph';
import { NWindow } from '../shell/window';
import { Shell } from '../shell/shell';

/**
 * Inspector panel types
 */
export type InspectorPanel = 'graph' | 'object' | 'relationships' | 'history';

/**
 * NInspector - The Object Inspector App
 */
export class NInspector {
  private _window?: NWindow;
  private _selectedObjectId?: NObjectId;
  private _graph: NObjectGraph;
  private _panel: InspectorPanel = 'graph';
  
  constructor(graph: NObjectGraph = TheGraph) {
    this._graph = graph;
    
    // Listen for graph changes
    this._graph.mutations$.subscribe(() => {
      this.refresh();
    });
  }
  
  /**
   * Open the inspector
   */
  open(): NWindow {
    if (this._window) {
      this._window.bringToFront();
      return this._window;
    }
    
    this._window = Shell.createWindow('Object Inspector', {
      x: 800,
      y: 50,
      width: 400,
      height: 600,
    });
    
    this.refresh();
    
    return this._window;
  }
  
  /**
   * Close the inspector
   */
  close(): void {
    if (this._window) {
      this._window.close();
      this._window = undefined;
    }
  }
  
  /**
   * Select an object
   */
  select(objectId: NObjectId): void {
    this._selectedObjectId = objectId;
    this._panel = 'object';
    this.refresh();
  }
  
  /**
   * Refresh the display
   */
  refresh(): void {
    if (!this._window) return;
    
    const content = this._render();
    this._window.setContent(content);
  }
  
  /**
   * Render the inspector content
   */
  private _render(): string {
    return `
      <div style="height: 100%; display: flex; flex-direction: column; font-family: -apple-system, sans-serif;">
        ${this._renderToolbar()}
        ${this._renderContent()}
      </div>
    `;
  }
  
  /**
   * Render toolbar
   */
  private _renderToolbar(): string {
    const tabs: Array<{ id: InspectorPanel; label: string; icon: string }> = [
      { id: 'graph', label: 'Graph', icon: '🔮' },
      { id: 'object', label: 'Object', icon: '📦' },
      { id: 'relationships', label: 'Relations', icon: '🔗' },
      { id: 'history', label: 'History', icon: '📜' },
    ];
    
    return `
      <div style="
        display: flex;
        background: #f5f5f5;
        border-bottom: 1px solid #ddd;
        padding: 4px;
        gap: 2px;
      ">
        ${tabs.map(tab => `
          <button 
            onclick="window.NewtonOS?.Inspector?.setPanel?.('${tab.id}')"
            style="
              flex: 1;
              padding: 6px 8px;
              border: none;
              border-radius: 4px;
              background: ${this._panel === tab.id ? 'white' : 'transparent'};
              box-shadow: ${this._panel === tab.id ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'};
              cursor: pointer;
              font-size: 11px;
              font-weight: 500;
            "
          >
            ${tab.icon} ${tab.label}
          </button>
        `).join('')}
      </div>
    `;
  }
  
  /**
   * Render main content
   */
  private _renderContent(): string {
    switch (this._panel) {
      case 'graph':
        return this._renderGraphPanel();
      case 'object':
        return this._renderObjectPanel();
      case 'relationships':
        return this._renderRelationshipsPanel();
      case 'history':
        return this._renderHistoryPanel();
      default:
        return this._renderGraphPanel();
    }
  }
  
  /**
   * Render graph panel - list all objects
   */
  private _renderGraphPanel(): string {
    const objects = this._graph.all();
    const byType = new Map<string, NObject[]>();
    
    for (const obj of objects) {
      if (!byType.has(obj.type)) {
        byType.set(obj.type, []);
      }
      byType.get(obj.type)!.push(obj);
    }
    
    return `
      <div style="flex: 1; overflow: auto;">
        <div style="padding: 12px; background: #fafafa; border-bottom: 1px solid #eee;">
          <div style="font-size: 20px; font-weight: 600;">${objects.length}</div>
          <div style="font-size: 11px; color: #888;">objects in graph</div>
        </div>
        
        ${Array.from(byType.entries()).map(([type, objs]) => `
          <div style="border-bottom: 1px solid #eee;">
            <div style="
              padding: 8px 12px;
              background: #f9f9f9;
              font-size: 11px;
              font-weight: 600;
              color: #666;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            ">
              ${this._getTypeIcon(type)} ${type} (${objs.length})
            </div>
            ${objs.map(obj => this._renderObjectRow(obj)).join('')}
          </div>
        `).join('')}
      </div>
    `;
  }
  
  /**
   * Render a single object row
   */
  private _renderObjectRow(obj: NObject): string {
    const isSelected = obj.id === this._selectedObjectId;
    const name = obj.getProperty('title') || obj.getProperty('name') || obj.type;
    
    return `
      <div 
        onclick="window.NewtonOS?.Inspector?.select?.('${obj.id}')"
        style="
          padding: 10px 12px;
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          background: ${isSelected ? '#007AFF10' : 'white'};
          border-left: 3px solid ${isSelected ? '#007AFF' : 'transparent'};
        "
        onmouseover="this.style.background='${isSelected ? '#007AFF15' : '#f8f8f8'}'"
        onmouseout="this.style.background='${isSelected ? '#007AFF10' : 'white'}'"
      >
        <div style="font-weight: 500; font-size: 13px;">
          ${name}
        </div>
        <div style="font-size: 11px; color: #888; font-family: 'SF Mono', Monaco, monospace;">
          ${obj.id.slice(0, 8)}... 
          <span style="color: ${obj.verified ? '#28c840' : '#ff5f57'};">
            ${obj.verified ? '✓' : '✗'}
          </span>
        </div>
      </div>
    `;
  }
  
  /**
   * Render object detail panel
   */
  private _renderObjectPanel(): string {
    if (!this._selectedObjectId) {
      return `
        <div style="flex: 1; display: flex; align-items: center; justify-content: center; color: #888;">
          Select an object to inspect
        </div>
      `;
    }
    
    const obj = this._graph.get(this._selectedObjectId);
    if (!obj) {
      return `
        <div style="flex: 1; display: flex; align-items: center; justify-content: center; color: #888;">
          Object not found
        </div>
      `;
    }
    
    const properties = obj.propertyNames.map((name: string) => ({
      name,
      value: obj.getProperty(name),
    }));
    
    return `
      <div style="flex: 1; overflow: auto;">
        <!-- Header -->
        <div style="padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
          <div style="font-size: 11px; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">
            ${obj.type}
          </div>
          <div style="font-size: 18px; font-weight: 600; margin-top: 4px;">
            ${obj.getProperty('title') || obj.getProperty('name') || 'Untitled'}
          </div>
          <div style="font-size: 11px; opacity: 0.7; font-family: monospace; margin-top: 4px;">
            ${obj.id}
          </div>
        </div>
        
        <!-- Status -->
        <div style="display: flex; padding: 12px; gap: 12px; background: #fafafa; border-bottom: 1px solid #eee;">
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 18px; color: ${obj.verified ? '#28c840' : '#ff5f57'};">
              ${obj.verified ? '✓' : '✗'}
            </div>
            <div style="font-size: 10px; color: #888;">Verified</div>
          </div>
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 18px;">${properties.length}</div>
            <div style="font-size: 10px; color: #888;">Properties</div>
          </div>
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 18px;">${obj.getRelationships().length}</div>
            <div style="font-size: 10px; color: #888;">Relations</div>
          </div>
        </div>
        
        <!-- Properties -->
        <div style="padding: 8px 0;">
          <div style="padding: 8px 12px; font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase;">
            Properties
          </div>
          ${properties.map((prop: { name: string; value: NValue | undefined }) => `
            <div style="padding: 8px 12px; display: flex; border-bottom: 1px solid #f5f5f5;">
              <div style="width: 100px; font-size: 12px; color: #666;">${prop.name}</div>
              <div style="flex: 1; font-size: 12px; font-family: 'SF Mono', Monaco, monospace; word-break: break-all;">
                ${this._formatValue(prop.value ?? null)}
              </div>
            </div>
          `).join('')}
        </div>
        
        <!-- Created -->
        <div style="padding: 12px; font-size: 11px; color: #888; border-top: 1px solid #eee;">
          Created: ${obj.created.toLocaleString()}
        </div>
      </div>
    `;
  }
  
  /**
   * Render relationships panel
   */
  private _renderRelationshipsPanel(): string {
    if (!this._selectedObjectId) {
      return `
        <div style="flex: 1; display: flex; align-items: center; justify-content: center; color: #888;">
          Select an object to see relationships
        </div>
      `;
    }
    
    const obj = this._graph.get(this._selectedObjectId);
    if (!obj) return '';
    
    const outgoing = obj.getRelationships();
    const incoming = this._graph.findReferencing(this._selectedObjectId);
    
    return `
      <div style="flex: 1; overflow: auto;">
        <!-- Outgoing -->
        <div>
          <div style="padding: 8px 12px; font-size: 11px; font-weight: 600; color: #888; background: #fafafa; border-bottom: 1px solid #eee;">
            OUTGOING (${outgoing.length})
          </div>
          ${outgoing.length === 0 ? `
            <div style="padding: 16px; color: #888; font-size: 12px;">No outgoing relationships</div>
          ` : outgoing.map((rel: NRelationship) => this._renderRelationship(rel, 'outgoing')).join('')}
        </div>
        
        <!-- Incoming -->
        <div>
          <div style="padding: 8px 12px; font-size: 11px; font-weight: 600; color: #888; background: #fafafa; border-bottom: 1px solid #eee;">
            INCOMING (${incoming.length})
          </div>
          ${incoming.length === 0 ? `
            <div style="padding: 16px; color: #888; font-size: 12px;">No incoming relationships</div>
          ` : incoming.map(source => {
            const rels = source.getRelationships().filter((r: NRelationship) => r.targetId === this._selectedObjectId);
            return rels.map((rel: NRelationship) => this._renderRelationship(rel, 'incoming', source)).join('');
          }).join('')}
        </div>
      </div>
    `;
  }
  
  /**
   * Render a relationship
   */
  private _renderRelationship(rel: NRelationship, direction: 'outgoing' | 'incoming', source?: NObject): string {
    const targetObj = direction === 'outgoing' 
      ? this._graph.get(rel.targetId)
      : source;
    
    const name = targetObj?.getProperty('title') || targetObj?.getProperty('name') || targetObj?.type || 'Unknown';
    
    return `
      <div style="padding: 10px 12px; border-bottom: 1px solid #f5f5f5; display: flex; align-items: center; gap: 8px;">
        <div style="font-size: 16px;">
          ${direction === 'outgoing' ? '→' : '←'}
        </div>
        <div style="flex: 1;">
          <div style="font-size: 12px; font-weight: 500;">${name}</div>
          <div style="font-size: 10px; color: #888;">
            ${rel.kind} • ${(direction === 'outgoing' ? rel.targetId : rel.sourceId).slice(0, 8)}...
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Render history panel
   */
  private _renderHistoryPanel(): string {
    return `
      <div style="flex: 1; display: flex; align-items: center; justify-content: center; color: #888; flex-direction: column; gap: 8px;">
        <div style="font-size: 32px;">📜</div>
        <div>Mutation history coming soon</div>
        <div style="font-size: 11px;">All changes tracked in Newton Ledger</div>
      </div>
    `;
  }
  
  /**
   * Format a value for display
   */
  private _formatValue(value: NValue): string {
    if (value === null) return '<span style="color:#888;">null</span>';
    if (value === undefined) return '<span style="color:#888;">undefined</span>';
    if (typeof value === 'boolean') return `<span style="color:#007AFF;">${value}</span>`;
    if (typeof value === 'number') return `<span style="color:#28c840;">${value}</span>`;
    if (typeof value === 'string') {
      if (value.length > 50) {
        return `"${value.slice(0, 50)}..."`;
      }
      return `"${value}"`;
    }
    if (Array.isArray(value)) return `[${value.length} items]`;
    if (typeof value === 'object') return `{${Object.keys(value).length} keys}`;
    return String(value);
  }
  
  /**
   * Get icon for type
   */
  private _getTypeIcon(type: string): string {
    const icons: Record<string, string> = {
      document: '📄',
      user: '👤',
      window: '🪟',
      app: '📱',
      session: '🔐',
      relationship: '🔗',
    };
    return icons[type] || '📦';
  }
  
  /**
   * Set the active panel
   */
  setPanel(panel: InspectorPanel): void {
    this._panel = panel;
    this.refresh();
  }
}

// Singleton
export const Inspector = new NInspector();

export default NInspector;
