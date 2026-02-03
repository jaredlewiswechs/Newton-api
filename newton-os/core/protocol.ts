/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - THE NEWTON PROTOCOL
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Layer 3: Verification Bridge
 * 
 * Connects the Object Graph to the Newton Agent.
 * Every mutation can be verified.
 * Every query can be proven.
 * Every constraint is enforced.
 * 
 * The Protocol is the nervous system of Newton OS.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { Subject, Observable, BehaviorSubject } from 'rxjs';
import { NObject } from './nobject';
import { NObjectGraph, NConstraint, NQueryResult } from './graph';

/**
 * Connection state
 */
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

/**
 * Newton Agent request types
 */
export interface NewtonRequest {
  id: string;
  type: 'verify' | 'calculate' | 'constraint' | 'ask' | 'ground';
  payload: Record<string, unknown>;
  timestamp: Date;
}

/**
 * Newton Agent response
 */
export interface NewtonResponse {
  id: string;
  requestId: string;
  success: boolean;
  verified?: boolean;
  result?: unknown;
  error?: string;
  elapsed_us?: number;
  timestamp: Date;
}

/**
 * Ledger entry (from Newton)
 */
export interface LedgerEntry {
  index: number;
  hash: string;
  previousHash: string;
  timestamp: string;
  operation: string;
  data: Record<string, unknown>;
}

/**
 * Verification result with provenance
 */
export interface VerificationResult {
  verified: boolean;
  confidence?: number;
  sources?: string[];
  ledgerIndex?: number;
  timestamp: Date;
}

/**
 * The Newton Protocol - Bridge to Verified Computation
 */
export class NewtonProtocol {
  private _baseUrl: string;
  private _ws?: WebSocket;
  private _state$ = new BehaviorSubject<ConnectionState>('disconnected');
  private _responses$ = new Subject<NewtonResponse>();
  private _pendingRequests = new Map<string, (response: NewtonResponse) => void>();
  
  constructor(baseUrl: string = 'http://localhost:8000') {
    this._baseUrl = baseUrl;
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // CONNECTION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Connection state observable
   */
  get state$(): Observable<ConnectionState> {
    return this._state$.asObservable();
  }
  
  /**
   * Current connection state
   */
  get state(): ConnectionState {
    return this._state$.getValue();
  }
  
  /**
   * Connect to Newton Agent via WebSocket
   */
  async connect(): Promise<void> {
    if (this._ws) {
      this._ws.close();
    }
    
    this._state$.next('connecting');
    
    return new Promise((resolve, reject) => {
      const wsUrl = this._baseUrl.replace('http', 'ws') + '/ws';
      
      try {
        this._ws = new WebSocket(wsUrl);
        
        this._ws.onopen = () => {
          this._state$.next('connected');
          resolve();
        };
        
        this._ws.onclose = () => {
          this._state$.next('disconnected');
        };
        
        this._ws.onerror = (error) => {
          this._state$.next('error');
          reject(error);
        };
        
        this._ws.onmessage = (event) => {
          const response = JSON.parse(event.data) as NewtonResponse;
          response.timestamp = new Date();
          
          // Resolve pending request
          const resolver = this._pendingRequests.get(response.requestId);
          if (resolver) {
            resolver(response);
            this._pendingRequests.delete(response.requestId);
          }
          
          this._responses$.next(response);
        };
      } catch (error) {
        this._state$.next('error');
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from Newton Agent
   */
  disconnect(): void {
    if (this._ws) {
      this._ws.close();
      this._ws = undefined;
    }
    this._state$.next('disconnected');
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // HTTP API
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Make HTTP request to Newton Agent
   */
  private async httpRequest<T>(
    method: 'GET' | 'POST',
    endpoint: string,
    body?: Record<string, unknown>
  ): Promise<T> {
    const url = `${this._baseUrl}${endpoint}`;
    
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`Newton Agent error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // VERIFICATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Verify content against a claim
   */
  async verify(content: string, claim: string): Promise<VerificationResult> {
    const response = await this.httpRequest<{
      verified: boolean;
      confidence: number;
      sources?: string[];
      elapsed_us: number;
    }>('POST', '/verify', { content, claim });
    
    return {
      verified: response.verified,
      confidence: response.confidence,
      sources: response.sources,
      timestamp: new Date(),
    };
  }
  
  /**
   * Verify an NObject satisfies constraints
   */
  async verifyObject(obj: NObject, constraints: Record<string, unknown>): Promise<VerificationResult> {
    const response = await this.httpRequest<{
      verified: boolean;
      all_passed: boolean;
      elapsed_us: number;
    }>('POST', '/constraint', {
      data: obj.toJSON(),
      constraints,
    });
    
    return {
      verified: response.verified || response.all_passed,
      timestamp: new Date(),
    };
  }
  
  /**
   * Batch verify multiple items
   */
  async verifyBatch(items: Array<{ content: string; claim: string }>): Promise<VerificationResult[]> {
    const response = await this.httpRequest<{
      results: Array<{
        verified: boolean;
        confidence: number;
      }>;
      elapsed_us: number;
    }>('POST', '/verify/batch', { items });
    
    return response.results.map(r => ({
      verified: r.verified,
      confidence: r.confidence,
      timestamp: new Date(),
    }));
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // CALCULATION
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Perform verified calculation
   */
  async calculate(expression: Record<string, unknown>): Promise<{
    result: unknown;
    verified: boolean;
    elapsed_us: number;
  }> {
    return this.httpRequest('POST', '/calculate', { expression });
  }
  
  /**
   * Evaluate CDL constraint against data
   */
  async evaluateConstraint(
    data: Record<string, unknown>,
    constraints: Record<string, unknown>
  ): Promise<{
    verified: boolean;
    results: Record<string, { passed: boolean; actual: unknown }>;
  }> {
    const response = await this.httpRequest<{
      all_passed: boolean;
      results: Record<string, { passed: boolean; actual: unknown }>;
      elapsed_us: number;
    }>('POST', '/constraint', { data, constraints });
    
    return {
      verified: response.all_passed,
      results: response.results,
    };
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // ASK (FULL PIPELINE)
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Ask Newton a question (full verification pipeline)
   */
  async ask(question: string): Promise<{
    answer: string;
    verified: boolean;
    confidence: number;
    sources: string[];
    ledgerIndex: number;
  }> {
    return this.httpRequest('POST', '/ask', { question });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // GROUNDING
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Ground a claim in external evidence
   */
  async ground(claim: string): Promise<{
    grounded: boolean;
    sources: string[];
    evidence: string[];
    confidence: number;
  }> {
    return this.httpRequest('POST', '/ground', { claim });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // LEDGER
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Get ledger entries
   */
  async getLedger(start?: number, end?: number): Promise<LedgerEntry[]> {
    let endpoint = '/ledger';
    if (start !== undefined || end !== undefined) {
      const params = new URLSearchParams();
      if (start !== undefined) params.set('start', start.toString());
      if (end !== undefined) params.set('end', end.toString());
      endpoint += '?' + params.toString();
    }
    
    const response = await this.httpRequest<{ entries: LedgerEntry[] }>('GET', endpoint);
    return response.entries;
  }
  
  /**
   * Get ledger entry with Merkle proof
   */
  async getLedgerEntry(index: number): Promise<{
    entry: LedgerEntry;
    proof: string[];
    valid: boolean;
  }> {
    return this.httpRequest('GET', `/ledger/${index}`);
  }
  
  /**
   * Export verification certificate
   */
  async getCertificate(index: number): Promise<{
    certificate: string;
    valid: boolean;
  }> {
    return this.httpRequest('GET', `/ledger/certificate/${index}`);
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // VAULT (ENCRYPTED STORAGE)
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Store encrypted data
   */
  async vaultStore(key: string, value: unknown, identity: string): Promise<{
    stored: boolean;
    hash: string;
  }> {
    return this.httpRequest('POST', '/vault/store', { key, value, identity });
  }
  
  /**
   * Retrieve encrypted data
   */
  async vaultRetrieve(key: string, identity: string): Promise<{
    value: unknown;
    verified: boolean;
  }> {
    return this.httpRequest('POST', '/vault/retrieve', { key, identity });
  }
  
  // ═══════════════════════════════════════════════════════════════════════
  // HEALTH & METRICS
  // ═══════════════════════════════════════════════════════════════════════
  
  /**
   * Check Newton Agent health
   */
  async health(): Promise<{
    status: string;
    version: string;
    uptime: number;
  }> {
    return this.httpRequest('GET', '/health');
  }
  
  /**
   * Get performance metrics
   */
  async metrics(): Promise<{
    requests: number;
    verifications: number;
    calculations: number;
    avgLatencyUs: number;
  }> {
    return this.httpRequest('GET', '/metrics');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GRAPH INTEGRATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Connect an Object Graph to Newton for verification
 */
export class VerifiedGraph {
  private _graph: NObjectGraph;
  private _protocol: NewtonProtocol;
  
  constructor(graph: NObjectGraph, protocol: NewtonProtocol, autoVerify: boolean = true) {
    this._graph = graph;
    this._protocol = protocol;
    
    // Auto-verify mutations
    if (autoVerify) {
      this._graph.mutations$.subscribe(async (mutation: { type: string; objectId: string }) => {
        if (mutation.type === 'add' || mutation.type === 'update') {
          const obj = this._graph.get(mutation.objectId);
          if (obj) {
            // Verify object constraints
            await this.verifyObject(obj);
          }
        }
      });
    }
  }
  
  /**
   * Verify an object against its constraints
   */
  async verifyObject(obj: NObject): Promise<VerificationResult> {
    const constraints: Record<string, unknown> = {};
    
    // Build constraints from properties
    for (const name of obj.propertyNames) {
      constraints[name] = { exists: true };
    }
    
    return this._protocol.verifyObject(obj, constraints);
  }
  
  /**
   * Query with verification
   */
  async verifiedQuery(constraint: NConstraint): Promise<NQueryResult & { verification: VerificationResult }> {
    const result = this._graph.query(constraint);
    
    // Verify each result object
    const verifications = await Promise.all(
      result.objects.map(obj => this.verifyObject(obj))
    );
    
    const allVerified = verifications.every(v => v.verified);
    
    return {
      ...result,
      verified: allVerified,
      verification: {
        verified: allVerified,
        timestamp: new Date(),
      },
    };
  }
  
  /**
   * Add object with verification
   */
  async addVerified(obj: NObject): Promise<{ object: NObject; verified: boolean }> {
    this._graph.add(obj);
    const verification = await this.verifyObject(obj);
    
    if (!verification.verified) {
      // Remove if verification fails
      this._graph.remove(obj.id);
      throw new Error('Object failed verification');
    }
    
    return { object: obj, verified: true };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SINGLETON
// ═══════════════════════════════════════════════════════════════════════════

/**
 * The global Newton Protocol instance
 */
export const Newton = new NewtonProtocol();

export default NewtonProtocol;
