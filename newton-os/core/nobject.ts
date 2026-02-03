/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - THE UNIVERSAL OBJECT
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Layer 1: NObject
 * 
 * Everything is an NObject.
 * Every relationship IS an NObject.
 * All properties are reactive (Rx).
 * All mutations are verified by Newton.
 * 
 * "Objects all the way down."
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { BehaviorSubject, Observable, Subject } from 'rxjs';

/**
 * Unique identifier for objects
 */
export type NObjectId = string;

/**
 * Property types that can be stored
 */
export type NValue = 
  | string 
  | number 
  | boolean 
  | null 
  | NObject 
  | NValue[] 
  | { [key: string]: NValue };

/**
 * Relationship kinds
 */
export type RelationshipKind = 
  | 'owns'       // Strong ownership - target deleted when source deleted
  | 'references' // Weak reference - can become dangling
  | 'contains'   // Containment - spatial/logical grouping
  | 'views'      // View relationship - observer pattern
  | 'extends'    // Inheritance/prototype
  | 'implements' // Interface implementation
  | string;      // Custom relationship types

/**
 * A reactive property - observable value with verification
 */
export class NProperty<T extends NValue = NValue> {
  private _value$: BehaviorSubject<T>;
  private _verified: boolean = false;
  private _constraint?: (value: T) => boolean;
  
  constructor(
    public readonly name: string,
    initialValue: T,
    constraint?: (value: T) => boolean
  ) {
    this._value$ = new BehaviorSubject<T>(initialValue);
    this._constraint = constraint;
    
    // Verify initial value
    if (constraint) {
      this._verified = constraint(initialValue);
    } else {
      this._verified = true;
    }
  }
  
  /**
   * Current value
   */
  get value(): T {
    return this._value$.getValue();
  }
  
  /**
   * Set value - verifies against constraint
   */
  set value(newValue: T) {
    if (this._constraint) {
      this._verified = this._constraint(newValue);
    }
    this._value$.next(newValue);
  }
  
  /**
   * Observable stream of values
   */
  get value$(): Observable<T> {
    return this._value$.asObservable();
  }
  
  /**
   * Is the current value verified?
   */
  get verified(): boolean {
    return this._verified;
  }
  
  /**
   * Subscribe to changes
   */
  subscribe(observer: (value: T) => void): () => void {
    const subscription = this._value$.subscribe(observer);
    return () => subscription.unsubscribe();
  }
}

/**
 * NObject - The Universal Object
 * 
 * The fundamental unit of Newton OS.
 * Everything is built from this.
 */
export class NObject {
  readonly id: NObjectId;
  readonly type: string;
  readonly created: Date;
  
  private _properties: Map<string, NProperty> = new Map();
  private _relationships: Map<string, NRelationship[]> = new Map();
  private _verified: boolean = true;
  
  // Rx subjects for observation
  private _propertyChanged$ = new Subject<{ name: string; value: NValue }>();
  private _relationshipChanged$ = new Subject<{ kind: string; relationship: NRelationship; action: 'add' | 'remove' }>();
  private _destroyed$ = new Subject<void>();
  
  constructor(type: string, id?: NObjectId) {
    this.id = id || crypto.randomUUID();
    this.type = type;
    this.created = new Date();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // PROPERTIES
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Set a property value
   */
  setProperty<T extends NValue>(name: string, value: T, constraint?: (v: T) => boolean): void {
    let prop = this._properties.get(name) as NProperty<T> | undefined;
    
    if (prop) {
      prop.value = value;
    } else {
      prop = new NProperty<T>(name, value, constraint);
      this._properties.set(name, prop as unknown as NProperty);
    }
    
    this._propertyChanged$.next({ name, value });
    this._updateVerification();
  }
  
  /**
   * Get a property value
   */
  getProperty<T extends NValue>(name: string): T | undefined {
    const prop = this._properties.get(name);
    return prop?.value as T | undefined;
  }
  
  /**
   * Get property as observable
   */
  getProperty$<T extends NValue>(name: string): Observable<T> | undefined {
    const prop = this._properties.get(name);
    return prop?.value$ as Observable<T> | undefined;
  }
  
  /**
   * Check if property exists
   */
  hasProperty(name: string): boolean {
    return this._properties.has(name);
  }
  
  /**
   * Get all property names
   */
  get propertyNames(): string[] {
    return Array.from(this._properties.keys());
  }
  
  /**
   * Observable: property changed
   */
  get propertyChanged$(): Observable<{ name: string; value: NValue }> {
    return this._propertyChanged$.asObservable();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // RELATIONSHIPS
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Add a relationship to another object
   */
  addRelationship(targetId: NObjectId, kind: RelationshipKind): NRelationship {
    const rel = new NRelationship(this.id, targetId, kind);
    
    if (!this._relationships.has(kind)) {
      this._relationships.set(kind, []);
    }
    this._relationships.get(kind)!.push(rel);
    
    this._relationshipChanged$.next({ kind, relationship: rel, action: 'add' });
    
    return rel;
  }
  
  /**
   * Remove a relationship
   */
  removeRelationship(rel: NRelationship): boolean {
    const rels = this._relationships.get(rel.kind);
    if (!rels) return false;
    
    const index = rels.findIndex(r => r.id === rel.id);
    if (index === -1) return false;
    
    rels.splice(index, 1);
    this._relationshipChanged$.next({ kind: rel.kind, relationship: rel, action: 'remove' });
    
    return true;
  }
  
  /**
   * Get relationships by kind
   */
  getRelationships(kind?: RelationshipKind): NRelationship[] {
    if (kind) {
      return this._relationships.get(kind) || [];
    }
    
    // All relationships
    const all: NRelationship[] = [];
    for (const rels of this._relationships.values()) {
      all.push(...rels);
    }
    return all;
  }
  
  /**
   * Get related object IDs
   */
  getRelatedIds(kind?: RelationshipKind): NObjectId[] {
    return this.getRelationships(kind).map(r => r.targetId);
  }
  
  /**
   * Observable: relationship changed
   */
  get relationshipChanged$(): Observable<{ kind: string; relationship: NRelationship; action: 'add' | 'remove' }> {
    return this._relationshipChanged$.asObservable();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // VERIFICATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Is this object in a verified state?
   */
  get verified(): boolean {
    return this._verified;
  }
  
  /**
   * Update verification status based on all properties
   */
  private _updateVerification(): void {
    this._verified = Array.from(this._properties.values())
      .every(prop => prop.verified);
  }
  
  /**
   * Verify the object against Newton constraints
   * (Will call out to Newton Agent)
   */
  async verify(): Promise<boolean> {
    // TODO: Call Newton Agent for verification
    this._updateVerification();
    return this._verified;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // LIFECYCLE
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Destroy this object
   */
  destroy(): void {
    this._destroyed$.next();
    this._destroyed$.complete();
    this._propertyChanged$.complete();
    this._relationshipChanged$.complete();
  }
  
  /**
   * Observable: object destroyed
   */
  get destroyed$(): Observable<void> {
    return this._destroyed$.asObservable();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // SERIALIZATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Convert to plain object for persistence/transfer
   */
  toJSON(): Record<string, unknown> {
    const properties: Record<string, NValue> = {};
    for (const [name, prop] of this._properties) {
      properties[name] = prop.value;
    }
    
    const relationships: Record<string, NObjectId[]> = {};
    for (const [kind, rels] of this._relationships) {
      relationships[kind] = rels.map(r => r.targetId);
    }
    
    return {
      id: this.id,
      type: this.type,
      created: this.created.toISOString(),
      properties,
      relationships,
      verified: this._verified,
    };
  }
  
  /**
   * Create from plain object
   */
  static fromJSON(json: Record<string, unknown>): NObject {
    const obj = new NObject(json.type as string, json.id as string);
    
    // Restore properties
    const properties = json.properties as Record<string, NValue>;
    if (properties) {
      for (const [name, value] of Object.entries(properties)) {
        obj.setProperty(name, value);
      }
    }
    
    // Restore relationships
    const relationships = json.relationships as Record<string, NObjectId[]>;
    if (relationships) {
      for (const [kind, targetIds] of Object.entries(relationships)) {
        for (const targetId of targetIds) {
          obj.addRelationship(targetId, kind);
        }
      }
    }
    
    return obj;
  }
}

/**
 * NRelationship - Relationships ARE Objects
 * 
 * This is key: a relationship between A and B is itself an object.
 * It can have properties, constraints, be observed, be verified.
 */
export class NRelationship extends NObject {
  constructor(
    public readonly sourceId: NObjectId,
    public readonly targetId: NObjectId,
    public readonly kind: RelationshipKind,
    id?: NObjectId
  ) {
    super('relationship', id);
    this.setProperty('sourceId', sourceId);
    this.setProperty('targetId', targetId);
    this.setProperty('kind', kind);
  }
  
  /**
   * Inverse relationship (if bidirectional)
   */
  private _inverse?: NRelationship;
  
  get inverse(): NRelationship | undefined {
    return this._inverse;
  }
  
  setInverse(rel: NRelationship): void {
    this._inverse = rel;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// OBJECT FACTORY
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Standard Newton OS object types
 */
export const NObjectTypes = {
  // Core
  Object: 'object',
  Relationship: 'relationship',
  
  // Documents
  Document: 'document',
  Text: 'text',
  Image: 'image',
  
  // UI
  Window: 'window',
  View: 'view',
  Button: 'button',
  
  // System
  User: 'user',
  Session: 'session',
  Query: 'query',
  
  // Application
  App: 'app',
  Service: 'service',
} as const;

/**
 * Create standard objects
 */
export const NObjectFactory = {
  /**
   * Create a document object
   */
  document(title: string, content?: string): NObject {
    const doc = new NObject(NObjectTypes.Document);
    doc.setProperty('title', title, (t: string) => t.length > 0 && t.length < 256);
    doc.setProperty('content', content || '');
    doc.setProperty('modified', new Date().toISOString());
    return doc;
  },
  
  /**
   * Create a user object
   */
  user(name: string, email?: string): NObject {
    const user = new NObject(NObjectTypes.User);
    user.setProperty('name', name, (n: string) => n.length > 0);
    if (email) {
      user.setProperty('email', email, (e: string) => e.includes('@'));
    }
    return user;
  },
  
  /**
   * Create an app object
   */
  app(name: string, version: string): NObject {
    const app = new NObject(NObjectTypes.App);
    app.setProperty('name', name);
    app.setProperty('version', version);
    app.setProperty('running', false);
    return app;
  },
  
  /**
   * Create a window object
   */
  window(title: string, x: number, y: number, width: number, height: number): NObject {
    const win = new NObject(NObjectTypes.Window);
    win.setProperty('title', title);
    win.setProperty('x', x);
    win.setProperty('y', y);
    win.setProperty('width', width, (w: number) => w > 0);
    win.setProperty('height', height, (h: number) => h > 0);
    win.setProperty('visible', true);
    win.setProperty('minimized', false);
    return win;
  },
};

export default NObject;
