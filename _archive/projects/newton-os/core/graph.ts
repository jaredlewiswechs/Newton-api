/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - THE OBJECT GRAPH
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Layer 2: Object Graph
 * 
 * "Data Soup" - there are no files, only objects.
 * Objects link to objects.
 * All relationships are first-class.
 * Query by constraint, not by path.
 * 
 * The Object Graph is the entire state of the system.
 * Every mutation is verified, every change is observed.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { BehaviorSubject, Observable, Subject, map } from 'rxjs';
import { NObject, NObjectId, RelationshipKind, NValue } from './nobject';

/**
 * Constraint for querying objects
 */
export interface NConstraint {
  type?: string | string[];
  properties?: {
    [key: string]: NValue | { $gt?: number; $lt?: number; $gte?: number; $lte?: number; $contains?: string; $exists?: boolean };
  };
  relationships?: {
    kind: RelationshipKind;
    targetId?: NObjectId;
    exists?: boolean;
  }[];
}

/**
 * Query result with provenance
 */
export interface NQueryResult {
  objects: NObject[];
  constraint: NConstraint;
  timestamp: Date;
  verified: boolean;
}

/**
 * Graph mutation event
 */
export interface NGraphMutation {
  type: 'add' | 'remove' | 'update';
  objectId: NObjectId;
  object?: NObject;
  property?: { name: string; oldValue: NValue; newValue: NValue };
  timestamp: Date;
}

/**
 * The Object Graph - the universe of Newton OS
 */
export class NObjectGraph {
  private _objects: Map<NObjectId, NObject> = new Map();
  private _byType: Map<string, Set<NObjectId>> = new Map();
  
  // Rx observables for the whole graph
  private _objects$ = new BehaviorSubject<Map<NObjectId, NObject>>(this._objects);
  private _mutations$ = new Subject<NGraphMutation>();
  
  // Verification
  private _verified: boolean = true;
  
  constructor() {
    // Track all mutations for the ledger
    this._mutations$.subscribe((mutation: NGraphMutation) => {
      console.log('[Graph Mutation]', mutation.type, mutation.objectId);
    });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // OBJECT MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Add an object to the graph
   */
  add(obj: NObject): NObject {
    // Store object
    this._objects.set(obj.id, obj);
    
    // Index by type
    if (!this._byType.has(obj.type)) {
      this._byType.set(obj.type, new Set());
    }
    this._byType.get(obj.type)!.add(obj.id);
    
    // Subscribe to object changes
    obj.propertyChanged$.subscribe((change: { name: string; value: NValue }) => {
      this._mutations$.next({
        type: 'update',
        objectId: obj.id,
        property: { name: change.name, oldValue: null as any, newValue: change.value },
        timestamp: new Date(),
      });
    });
    
    obj.destroyed$.subscribe(() => {
      this.remove(obj.id);
    });
    
    // Emit mutation
    this._mutations$.next({
      type: 'add',
      objectId: obj.id,
      object: obj,
      timestamp: new Date(),
    });
    
    this._objects$.next(this._objects);
    
    return obj;
  }
  
  /**
   * Remove an object from the graph
   */
  remove(id: NObjectId): boolean {
    const obj = this._objects.get(id);
    if (!obj) return false;
    
    // Remove from type index
    const typeSet = this._byType.get(obj.type);
    if (typeSet) {
      typeSet.delete(id);
    }
    
    // Remove object
    this._objects.delete(id);
    
    // Handle cascading deletes for 'owns' relationships
    for (const otherObj of this._objects.values()) {
      const ownsRels = otherObj.getRelationships('owns')
        .filter((r: { targetId: NObjectId }) => r.targetId === id);
      for (const rel of ownsRels) {
        otherObj.removeRelationship(rel);
      }
    }
    
    // Emit mutation
    this._mutations$.next({
      type: 'remove',
      objectId: id,
      timestamp: new Date(),
    });
    
    this._objects$.next(this._objects);
    
    return true;
  }
  
  /**
   * Get an object by ID
   */
  get(id: NObjectId): NObject | undefined {
    return this._objects.get(id);
  }
  
  /**
   * Check if object exists
   */
  has(id: NObjectId): boolean {
    return this._objects.has(id);
  }
  
  /**
   * Get all objects
   */
  all(): NObject[] {
    return Array.from(this._objects.values());
  }
  
  /**
   * Get objects by type
   */
  ofType(type: string): NObject[] {
    const ids = this._byType.get(type);
    if (!ids) return [];
    return Array.from(ids).map(id => this._objects.get(id)!);
  }
  
  /**
   * Total object count
   */
  get size(): number {
    return this._objects.size;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // QUERYING - By Constraint, Not By Path
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Query objects by constraint
   * 
   * This is the core of Newton OS querying.
   * No paths. No hierarchies. Just constraints.
   */
  query(constraint: NConstraint): NQueryResult {
    let results = Array.from(this._objects.values());
    
    // Filter by type
    if (constraint.type) {
      const types = Array.isArray(constraint.type) ? constraint.type : [constraint.type];
      results = results.filter(obj => types.includes(obj.type));
    }
    
    // Filter by properties
    if (constraint.properties) {
      for (const [name, expected] of Object.entries(constraint.properties)) {
        results = results.filter(obj => {
          const value = obj.getProperty(name);
          
          // Handle special operators
          if (expected && typeof expected === 'object' && !Array.isArray(expected)) {
            const ops = expected as any;
            
            if ('$exists' in ops) {
              const exists = value !== undefined;
              return ops.$exists ? exists : !exists;
            }
            
            if (typeof value === 'number') {
              if ('$gt' in ops && !(value > ops.$gt)) return false;
              if ('$lt' in ops && !(value < ops.$lt)) return false;
              if ('$gte' in ops && !(value >= ops.$gte)) return false;
              if ('$lte' in ops && !(value <= ops.$lte)) return false;
            }
            
            if (typeof value === 'string' && '$contains' in ops) {
              return value.includes(ops.$contains);
            }
            
            return true;
          }
          
          // Direct equality
          return value === expected;
        });
      }
    }
    
    // Filter by relationships
    if (constraint.relationships) {
      for (const relConstraint of constraint.relationships) {
        results = results.filter(obj => {
          const rels = obj.getRelationships(relConstraint.kind);
          
          if (relConstraint.exists !== undefined) {
            return relConstraint.exists ? rels.length > 0 : rels.length === 0;
          }
          
          if (relConstraint.targetId) {
            return rels.some((r: { targetId: NObjectId }) => r.targetId === relConstraint.targetId);
          }
          
          return true;
        });
      }
    }
    
    return {
      objects: results,
      constraint,
      timestamp: new Date(),
      verified: true,
    };
  }
  
  /**
   * Live query - returns observable that updates when matching objects change
   */
  liveQuery(constraint: NConstraint): Observable<NQueryResult> {
    return this._objects$.pipe(
      map(() => this.query(constraint))
    );
  }
  
  /**
   * Find related objects
   */
  findRelated(id: NObjectId, kind?: RelationshipKind): NObject[] {
    const obj = this._objects.get(id);
    if (!obj) return [];
    
    const relatedIds = obj.getRelatedIds(kind);
    return relatedIds
      .map((rid: NObjectId) => this._objects.get(rid))
      .filter((o: NObject | undefined): o is NObject => o !== undefined);
  }
  
  /**
   * Find objects that relate TO this object
   */
  findReferencing(targetId: NObjectId, kind?: RelationshipKind): NObject[] {
    const results: NObject[] = [];
    
    for (const obj of this._objects.values()) {
      const rels = obj.getRelationships(kind);
      if (rels.some((r: { targetId: NObjectId }) => r.targetId === targetId)) {
        results.push(obj);
      }
    }
    
    return results;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // GRAPH TRAVERSAL
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Traverse the graph from a starting object
   */
  traverse(
    startId: NObjectId,
    direction: 'outgoing' | 'incoming' | 'both',
    maxDepth: number = 10,
    kind?: RelationshipKind
  ): Map<NObjectId, number> {
    const visited = new Map<NObjectId, number>();
    const queue: Array<{ id: NObjectId; depth: number }> = [{ id: startId, depth: 0 }];
    
    while (queue.length > 0) {
      const { id, depth } = queue.shift()!;
      
      if (visited.has(id) || depth > maxDepth) continue;
      visited.set(id, depth);
      
      const obj = this._objects.get(id);
      if (!obj) continue;
      
      // Outgoing relationships
      if (direction === 'outgoing' || direction === 'both') {
        for (const rel of obj.getRelationships(kind)) {
          if (!visited.has(rel.targetId)) {
            queue.push({ id: rel.targetId, depth: depth + 1 });
          }
        }
      }
      
      // Incoming relationships
      if (direction === 'incoming' || direction === 'both') {
        const incoming = this.findReferencing(id, kind);
        for (const inc of incoming) {
          if (!visited.has(inc.id)) {
            queue.push({ id: inc.id, depth: depth + 1 });
          }
        }
      }
    }
    
    return visited;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // OBSERVABLES
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Observable: all mutations
   */
  get mutations$(): Observable<NGraphMutation> {
    return this._mutations$.asObservable();
  }
  
  /**
   * Observable: specific object
   */
  watch(id: NObjectId): Observable<NObject | undefined> {
    return this._objects$.pipe(
      map((objects: Map<NObjectId, NObject>) => objects.get(id))
    );
  }
  
  /**
   * Observable: objects of type
   */
  watchType(type: string): Observable<NObject[]> {
    return this._objects$.pipe(
      map(() => this.ofType(type))
    );
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // VERIFICATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Verify the entire graph
   */
  async verify(): Promise<boolean> {
    for (const obj of this._objects.values()) {
      if (!await obj.verify()) {
        this._verified = false;
        return false;
      }
    }
    this._verified = true;
    return true;
  }
  
  /**
   * Is the graph verified?
   */
  get verified(): boolean {
    return this._verified;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // SERIALIZATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Export the entire graph
   */
  toJSON(): Record<string, unknown> {
    const objects: Record<string, unknown>[] = [];
    for (const obj of this._objects.values()) {
      objects.push(obj.toJSON());
    }
    
    return {
      version: 1,
      timestamp: new Date().toISOString(),
      objectCount: this._objects.size,
      objects,
    };
  }
  
  /**
   * Import a graph
   */
  static fromJSON(json: Record<string, unknown>): NObjectGraph {
    const graph = new NObjectGraph();
    const objects = json.objects as Record<string, unknown>[];
    
    for (const objJson of objects) {
      const obj = NObject.fromJSON(objJson);
      graph.add(obj);
    }
    
    return graph;
  }
  
  /**
   * Clear the graph
   */
  clear(): void {
    this._objects.clear();
    this._byType.clear();
    this._objects$.next(this._objects);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SINGLETON - The Global Object Soup
// ═══════════════════════════════════════════════════════════════════════════

/**
 * The Global Object Graph
 * 
 * In Newton OS, there's one object graph.
 * Everything lives in it.
 * "Data Soup"
 */
export const TheGraph = new NObjectGraph();

export default NObjectGraph;
