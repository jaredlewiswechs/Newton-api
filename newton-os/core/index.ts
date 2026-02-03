/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - CORE MODULE
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * The core of Newton OS.
 * 
 * Layer 0: NBezierObject - The universal shape (continuous, no discontinuities)
 * Layer 1: NObject - The universal object (reactive, verified)
 * Layer 2: NObjectGraph - The data soup (query by constraint, not path)
 * Layer 3: NewtonProtocol - The verification bridge (to Newton Agent)
 * 
 * ═══════════════════════════════════════════════════════════════════════════
 */

// Layer 0: The Bezier Primitive
export type { Point, BezierSegment, SuperellipseParams } from './bezier';
export { NBezierObject, NShapes } from './bezier';

// Layer 1: The Universal Object
export type { NObjectId, NValue, RelationshipKind } from './nobject';
export {
  NObject,
  NProperty,
  NRelationship,
  NObjectTypes,
  NObjectFactory,
} from './nobject';

// Layer 2: The Object Graph
export type { NConstraint, NQueryResult, NGraphMutation } from './graph';
export { NObjectGraph, TheGraph } from './graph';

// Layer 3: The Newton Protocol
export type { NewtonRequest, NewtonResponse, LedgerEntry, VerificationResult } from './protocol';
export { NewtonProtocol, VerifiedGraph, Newton } from './protocol';
