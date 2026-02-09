/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON GATE SERVICE v1.1.0
 * Deterministic Learning Environment Verification
 *
 * Realizing the Dynabook as a trusted learning environment, the Newton Gate
 * provides deterministic but intelligent verification that recognizes
 * educational intent.
 *
 * Fixes applied in this version:
 * - Heuristic Local Verification: Educational queries map to Phase 9 (RETURN)
 * - Phase Normalization: Gate always returns valid phases (1, 7, 8, or 9)
 * - Visual Stability: Fixed undefined/empty-string rendering in axis metrics
 * - Crystalline Alignment: Signal normalization for educational inquiries
 *
 * Author: Ada Computing Company | Houston, Texas
 * ═══════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════
// PHASE DEFINITIONS - The Crystalline Axis
// ═══════════════════════════════════════════════════════════════════════════

export enum Phase {
  /** Phase 1: ORIGIN - Initial query intake */
  ORIGIN = 1,
  /** Phase 7: REFLECTION - Processing and validation */
  REFLECTION = 7,
  /** Phase 8: SYNTHESIS - Pattern matching and integration */
  SYNTHESIS = 8,
  /** Phase 9: RETURN - Educational content verified and returned */
  RETURN = 9,
}

/** Valid phase values for type checking */
export type ValidPhase = 1 | 7 | 8 | 9;

// ═══════════════════════════════════════════════════════════════════════════
// EDUCATIONAL HEURISTICS
// ═══════════════════════════════════════════════════════════════════════════

/** Keywords indicating educational/science queries */
const SCIENCE_KEYWORDS = [
  'physics', 'chemistry', 'biology', 'astronomy', 'geology',
  'atom', 'molecule', 'cell', 'organism', 'planet', 'star',
  'energy', 'force', 'gravity', 'light', 'wave', 'particle',
  'evolution', 'ecosystem', 'photosynthesis', 'dna', 'gene',
  'element', 'compound', 'reaction', 'matter', 'mass',
  'velocity', 'acceleration', 'momentum', 'thermodynamics',
  'quantum', 'relativity', 'electron', 'proton', 'neutron',
  'newton', 'einstein', 'darwin', 'curie', 'hawking',
];

/** Keywords indicating mathematics queries */
const MATH_KEYWORDS = [
  'math', 'mathematics', 'algebra', 'geometry', 'calculus',
  'equation', 'formula', 'theorem', 'proof', 'axiom',
  'number', 'integer', 'fraction', 'decimal', 'percent',
  'addition', 'subtraction', 'multiplication', 'division',
  'derivative', 'integral', 'limit', 'function', 'graph',
  'triangle', 'circle', 'square', 'angle', 'area', 'volume',
  'pythagorean', 'fibonacci', 'prime', 'factorial', 'logarithm',
  'euclid', 'euler', 'gauss', 'turing', 'ramanujan',
];

/** Keywords indicating history queries */
const HISTORY_KEYWORDS = [
  'history', 'historical', 'ancient', 'medieval', 'modern',
  'civilization', 'empire', 'dynasty', 'kingdom', 'republic',
  'war', 'revolution', 'independence', 'constitution', 'treaty',
  'president', 'king', 'queen', 'emperor', 'leader',
  'discovery', 'invention', 'exploration', 'colonization',
  'renaissance', 'enlightenment', 'industrial', 'reformation',
  'egypt', 'rome', 'greece', 'mesopotamia', 'china', 'india',
  'washington', 'lincoln', 'churchill', 'gandhi', 'mandela',
];

/** Keywords indicating general educational content */
const EDUCATION_KEYWORDS = [
  'learn', 'study', 'explain', 'what is', 'how does', 'why do',
  'define', 'definition', 'meaning', 'concept', 'theory',
  'example', 'practice', 'exercise', 'homework', 'assignment',
  'teacher', 'student', 'school', 'university', 'education',
  'textbook', 'lesson', 'curriculum', 'course', 'class',
  'question', 'answer', 'understand', 'knowledge', 'wisdom',
];

// ═══════════════════════════════════════════════════════════════════════════
// AXIS METRICS INTERFACE - Visual Stability
// ═══════════════════════════════════════════════════════════════════════════

export interface AxisMetrics {
  /** The current phase (always a valid phase number) */
  phase: ValidPhase;
  /** Human-readable phase name (never undefined or empty) */
  phaseName: string;
  /** Signal strength normalized to 0-1 range */
  signalStrength: number;
  /** Crystalline alignment coefficient (0-1, higher = more aligned) */
  alignmentCoefficient: number;
  /** Educational confidence score (0-1) */
  educationalConfidence: number;
  /** Timestamp of verification */
  timestamp: number;
  /** Deterministic signature hash */
  signature: string;
}

export interface GateResponse {
  /** Whether the gate is open (query allowed) */
  allowed: boolean;
  /** The verification result */
  metrics: AxisMetrics;
  /** Optional message for display */
  message: string;
  /** Original query for reference */
  query: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// NEWTON GATE SERVICE
// ═══════════════════════════════════════════════════════════════════════════

export class NewtonGateService {
  private apiEndpoint: string;
  private fallbackEnabled: boolean;

  constructor(apiEndpoint?: string) {
    this.apiEndpoint = apiEndpoint || 'http://localhost:4567';
    this.fallbackEnabled = true;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // MAIN VERIFICATION METHOD
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Verify a query through the Newton Gate.
   * Educational queries are automatically mapped to Phase 9 (RETURN).
   */
  async verify(query: string): Promise<GateResponse> {
    if (!query || typeof query !== 'string') {
      return this.buildResponse(query || '', false, Phase.ORIGIN, 'Invalid query');
    }

    const normalizedQuery = query.toLowerCase().trim();

    // Heuristic check: Is this an educational query?
    const educationalScore = this.calculateEducationalScore(normalizedQuery);

    if (educationalScore >= 0.3) {
      // Educational queries bypass pseudo-random blocking
      return this.buildEducationalResponse(query, educationalScore);
    }

    // Try API verification
    try {
      const apiResponse = await this.callApi(query);
      if (apiResponse) {
        return this.normalizeApiResponse(query, apiResponse);
      }
    } catch (error) {
      // Fall through to local fallback
    }

    // Local fallback with deterministic (not pseudo-random) verification
    return this.localFallback(query, educationalScore);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // EDUCATIONAL SCORE CALCULATION - Heuristic Local Verification
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Calculate how likely a query is educational content.
   * Returns a score from 0 to 1.
   */
  private calculateEducationalScore(query: string): number {
    const words = query.split(/\s+/);
    let matchCount = 0;
    let totalWeight = 0;

    // Check science keywords (weight: 1.0)
    for (const keyword of SCIENCE_KEYWORDS) {
      if (query.includes(keyword)) {
        matchCount += 1.0;
      }
    }

    // Check math keywords (weight: 1.0)
    for (const keyword of MATH_KEYWORDS) {
      if (query.includes(keyword)) {
        matchCount += 1.0;
      }
    }

    // Check history keywords (weight: 0.9)
    for (const keyword of HISTORY_KEYWORDS) {
      if (query.includes(keyword)) {
        matchCount += 0.9;
      }
    }

    // Check general education keywords (weight: 0.7)
    for (const keyword of EDUCATION_KEYWORDS) {
      if (query.includes(keyword)) {
        matchCount += 0.7;
      }
    }

    // Question patterns are strongly educational
    if (/^(what|why|how|when|where|who|which|can you explain)\s/i.test(query)) {
      matchCount += 1.5;
    }

    // Calculate normalized score (cap at 1.0)
    const maxPossibleScore = 5.0; // Reasonable max for typical educational queries
    return Math.min(1.0, matchCount / maxPossibleScore);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE NORMALIZATION
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Normalize any phase value to a valid phase (1, 7, 8, or 9).
   * This fixes type mismatches in phase reporting.
   */
  private normalizePhase(phase: unknown): ValidPhase {
    // Handle undefined, null, or empty
    if (phase === undefined || phase === null || phase === '') {
      return Phase.ORIGIN;
    }

    // Handle string input
    if (typeof phase === 'string') {
      const parsed = parseInt(phase, 10);
      if (!isNaN(parsed)) {
        return this.mapToValidPhase(parsed);
      }
      // Handle phase names
      const upperPhase = phase.toUpperCase();
      if (upperPhase === 'RETURN') return Phase.RETURN;
      if (upperPhase === 'SYNTHESIS') return Phase.SYNTHESIS;
      if (upperPhase === 'REFLECTION') return Phase.REFLECTION;
      if (upperPhase === 'ORIGIN') return Phase.ORIGIN;
      return Phase.ORIGIN;
    }

    // Handle number input
    if (typeof phase === 'number') {
      return this.mapToValidPhase(phase);
    }

    return Phase.ORIGIN;
  }

  /**
   * Map any number to the closest valid phase.
   */
  private mapToValidPhase(value: number): ValidPhase {
    if (isNaN(value) || !isFinite(value)) {
      return Phase.ORIGIN;
    }

    // Map to closest valid phase
    if (value >= 9) return Phase.RETURN;
    if (value >= 8) return Phase.SYNTHESIS;
    if (value >= 7) return Phase.REFLECTION;
    return Phase.ORIGIN;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // VISUAL STABILITY - Safe String/Number Rendering
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Get the human-readable name for a phase.
   * Never returns undefined or empty string.
   */
  private getPhaseName(phase: ValidPhase): string {
    const names: Record<ValidPhase, string> = {
      [Phase.ORIGIN]: 'ORIGIN',
      [Phase.REFLECTION]: 'REFLECTION',
      [Phase.SYNTHESIS]: 'SYNTHESIS',
      [Phase.RETURN]: 'RETURN',
    };
    return names[phase] || 'ORIGIN';
  }

  /**
   * Safely normalize a number to prevent NaN/undefined display.
   */
  private safeNumber(value: unknown, defaultValue: number = 0): number {
    if (typeof value === 'number' && isFinite(value)) {
      return value;
    }
    if (typeof value === 'string') {
      const parsed = parseFloat(value);
      if (isFinite(parsed)) {
        return parsed;
      }
    }
    return defaultValue;
  }

  /**
   * Safely normalize a string to prevent undefined display.
   */
  private safeString(value: unknown, defaultValue: string = ''): string {
    if (typeof value === 'string' && value.length > 0) {
      return value;
    }
    if (value !== null && value !== undefined) {
      return String(value);
    }
    return defaultValue;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // CRYSTALLINE ALIGNMENT - Signal Normalization
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Calculate the crystalline alignment coefficient.
   * Educational inquiries settle near the Phase 9 (RETURN) axis.
   */
  private calculateAlignment(
    educationalScore: number,
    phase: ValidPhase
  ): number {
    // Base alignment from educational score
    let alignment = educationalScore * 0.7;

    // Phase contribution (Phase 9 is the ◉ axis)
    const phaseContribution: Record<ValidPhase, number> = {
      [Phase.ORIGIN]: 0.1,
      [Phase.REFLECTION]: 0.15,
      [Phase.SYNTHESIS]: 0.2,
      [Phase.RETURN]: 0.3,
    };
    alignment += phaseContribution[phase] || 0;

    // Normalize to 0-1 range
    return Math.min(1.0, Math.max(0.0, alignment));
  }

  /**
   * Calculate signal strength based on query characteristics.
   */
  private calculateSignalStrength(query: string, educationalScore: number): number {
    // Base signal from query length (normalized)
    const lengthSignal = Math.min(1.0, query.length / 100);

    // Educational boost
    const educationalBoost = educationalScore * 0.5;

    // Clarity bonus for well-formed questions
    let clarityBonus = 0;
    if (/\?$/.test(query.trim())) {
      clarityBonus = 0.1;
    }
    if (/^(what|why|how|explain|describe)\s/i.test(query)) {
      clarityBonus += 0.1;
    }

    return Math.min(1.0, lengthSignal + educationalBoost + clarityBonus);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // DETERMINISTIC HASH (NOT PSEUDO-RANDOM)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Generate a deterministic signature for a query.
   * Unlike pseudo-random hashes, this produces consistent results
   * for the same input, enabling reproducible verification.
   */
  private generateSignature(query: string, phase: ValidPhase): string {
    // Use a simple but consistent hash algorithm
    let hash = 0;
    const str = `${query}:${phase}:newton`;

    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }

    // Convert to uppercase hex, always 8 characters
    const hex = Math.abs(hash).toString(16).toUpperCase().padStart(8, '0');
    return hex.slice(0, 8);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // RESPONSE BUILDERS
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Build a response for educational queries - mapped to Phase 9 (RETURN).
   */
  private buildEducationalResponse(
    query: string,
    educationalScore: number
  ): GateResponse {
    const phase = Phase.RETURN; // Educational queries go to RETURN axis
    const signalStrength = this.calculateSignalStrength(query, educationalScore);
    const alignment = this.calculateAlignment(educationalScore, phase);

    const metrics: AxisMetrics = {
      phase,
      phaseName: this.getPhaseName(phase),
      signalStrength: this.safeNumber(signalStrength, 0.5),
      alignmentCoefficient: this.safeNumber(alignment, 0.5),
      educationalConfidence: this.safeNumber(educationalScore, 0.3),
      timestamp: Date.now(),
      signature: this.generateSignature(query, phase),
    };

    return {
      allowed: true,
      metrics,
      message: `Educational query verified. Phase ${phase}: ${metrics.phaseName}`,
      query: this.safeString(query, ''),
    };
  }

  /**
   * Build a standard response.
   */
  private buildResponse(
    query: string,
    allowed: boolean,
    phase: Phase,
    message: string
  ): GateResponse {
    const normalizedPhase = this.normalizePhase(phase);
    const educationalScore = this.calculateEducationalScore(query.toLowerCase());
    const signalStrength = this.calculateSignalStrength(query, educationalScore);
    const alignment = this.calculateAlignment(educationalScore, normalizedPhase);

    const metrics: AxisMetrics = {
      phase: normalizedPhase,
      phaseName: this.getPhaseName(normalizedPhase),
      signalStrength: this.safeNumber(signalStrength, 0.5),
      alignmentCoefficient: this.safeNumber(alignment, 0.5),
      educationalConfidence: this.safeNumber(educationalScore, 0),
      timestamp: Date.now(),
      signature: this.generateSignature(query, normalizedPhase),
    };

    return {
      allowed,
      metrics,
      message: this.safeString(message, 'Verification complete'),
      query: this.safeString(query, ''),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // API INTEGRATION
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Call the Newton API for verification.
   */
  private async callApi(query: string): Promise<Record<string, unknown> | null> {
    try {
      const response = await fetch(`${this.apiEndpoint}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * Normalize API response with phase mapping and visual stability fixes.
   */
  private normalizeApiResponse(
    query: string,
    apiResponse: Record<string, unknown>
  ): GateResponse {
    // Extract and normalize phase from API response
    const rawPhase = apiResponse.phase ?? apiResponse.status ?? Phase.ORIGIN;
    const phase = this.normalizePhase(rawPhase);

    // Extract other metrics with safe defaults
    const educationalScore = this.safeNumber(
      apiResponse.educationalScore ?? apiResponse.confidence,
      this.calculateEducationalScore(query.toLowerCase())
    );

    const signalStrength = this.safeNumber(
      apiResponse.signalStrength ?? apiResponse.strength,
      this.calculateSignalStrength(query, educationalScore)
    );

    const alignment = this.safeNumber(
      apiResponse.alignment ?? apiResponse.alignmentCoefficient,
      this.calculateAlignment(educationalScore, phase)
    );

    // Determine if allowed based on phase (Phase 9 is always allowed)
    const allowed = phase === Phase.RETURN ||
      (apiResponse.allowed === true) ||
      (apiResponse.status === 'VERIFIED');

    const metrics: AxisMetrics = {
      phase,
      phaseName: this.getPhaseName(phase),
      signalStrength: Math.min(1.0, Math.max(0.0, signalStrength)),
      alignmentCoefficient: Math.min(1.0, Math.max(0.0, alignment)),
      educationalConfidence: Math.min(1.0, Math.max(0.0, educationalScore)),
      timestamp: Date.now(),
      signature: this.safeString(
        apiResponse.signature as string,
        this.generateSignature(query, phase)
      ),
    };

    return {
      allowed,
      metrics,
      message: this.safeString(
        apiResponse.message as string,
        `Verification complete. Phase ${phase}: ${metrics.phaseName}`
      ),
      query: this.safeString(query, ''),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // LOCAL FALLBACK - Deterministic (Not Pseudo-Random)
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Local fallback verification when API is unavailable.
   * Uses deterministic logic instead of pseudo-random blocking.
   */
  private localFallback(query: string, educationalScore: number): GateResponse {
    // Determine phase based on query characteristics
    let phase: ValidPhase;
    let allowed: boolean;

    if (educationalScore >= 0.3) {
      // Educational content -> Phase 9 (RETURN)
      phase = Phase.RETURN;
      allowed = true;
    } else if (educationalScore >= 0.15) {
      // Somewhat educational -> Phase 8 (SYNTHESIS)
      phase = Phase.SYNTHESIS;
      allowed = true;
    } else if (query.length >= 10) {
      // Substantive query -> Phase 7 (REFLECTION)
      phase = Phase.REFLECTION;
      allowed = true;
    } else {
      // Minimal query -> Phase 1 (ORIGIN)
      phase = Phase.ORIGIN;
      allowed = query.length >= 4; // Only block very short queries
    }

    return this.buildResponse(
      query,
      allowed,
      phase,
      allowed
        ? `Local verification passed. Phase ${phase}: ${this.getPhaseName(phase)}`
        : 'Query too short for verification'
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SINGLETON EXPORT
// ═══════════════════════════════════════════════════════════════════════════

/** Default instance for immediate use */
export const newtonGate = new NewtonGateService();

/** Factory function for custom configuration */
export function createNewtonGate(apiEndpoint?: string): NewtonGateService {
  return new NewtonGateService(apiEndpoint);
}

// ═══════════════════════════════════════════════════════════════════════════
// TYPE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export type { AxisMetrics, GateResponse };
