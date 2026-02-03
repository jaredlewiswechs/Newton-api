/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON OS - THE BEZIER PRIMITIVE
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Steve Jobs understood: everything is a bezier curve.
 * Squares have discontinuities. Circles are limited.
 * The superellipse (squircle) is the natural shape.
 * 
 * This is Layer 0 - the atomic primitive of Newton OS.
 * Everything above this is built on continuous curves.
 * ═══════════════════════════════════════════════════════════════════════════
 */

/**
 * A point in 2D space
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * A cubic bezier curve segment
 * The fundamental drawing primitive
 */
export interface BezierSegment {
  start: Point;
  control1: Point;
  control2: Point;
  end: Point;
}

/**
 * Superellipse parameters
 * n=2 → ellipse
 * n=4 → squircle (iOS icons)
 * n→∞ → rectangle
 */
export interface SuperellipseParams {
  cx: number;      // center x
  cy: number;      // center y
  rx: number;      // radius x
  ry: number;      // radius y
  n: number;       // exponent (2=ellipse, 4=squircle, higher=more rectangular)
  rotation?: number; // rotation in radians
}

/**
 * NSBezierObject - The Universal Shape
 * 
 * Not NSBezierPath - this is an OBJECT.
 * It has identity, properties, constraints.
 * It can be observed, verified, persisted.
 */
export class NBezierObject {
  readonly id: string;
  private segments: BezierSegment[] = [];
  private _closed: boolean = false;
  
  constructor(id?: string) {
    this.id = id || crypto.randomUUID();
  }
  
  /**
   * Create a superellipse (squircle)
   * This is THE shape of Newton OS
   */
  static superellipse(params: SuperellipseParams, segments: number = 32): NBezierObject {
    const { cx, cy, rx, ry, n, rotation = 0 } = params;
    const obj = new NBezierObject();
    
    // Generate points on superellipse: |x/rx|^n + |y/ry|^n = 1
    const points: Point[] = [];
    for (let i = 0; i <= segments; i++) {
      const t = (i / segments) * 2 * Math.PI;
      
      // Superellipse parametric form
      const cosT = Math.cos(t);
      const sinT = Math.sin(t);
      const signCos = Math.sign(cosT);
      const signSin = Math.sign(sinT);
      
      // |cos(t)|^(2/n) * sign(cos(t)) * rx
      const x = signCos * Math.pow(Math.abs(cosT), 2 / n) * rx;
      const y = signSin * Math.pow(Math.abs(sinT), 2 / n) * ry;
      
      // Apply rotation
      const rotX = x * Math.cos(rotation) - y * Math.sin(rotation);
      const rotY = x * Math.sin(rotation) + y * Math.cos(rotation);
      
      points.push({ x: cx + rotX, y: cy + rotY });
    }
    
    // Convert to bezier segments with smooth curve fitting
    obj.fitCurve(points);
    obj._closed = true;
    
    return obj;
  }
  
  /**
   * The iOS squircle - n ≈ 5 for that Apple look
   */
  static squircle(cx: number, cy: number, size: number, cornerRadius?: number): NBezierObject {
    // Apple uses approximately n=5 for their squircles
    // The corner radius affects the n value
    const n = cornerRadius ? 2 + (cornerRadius / size) * 6 : 5;
    return NBezierObject.superellipse({
      cx, cy,
      rx: size / 2,
      ry: size / 2,
      n
    });
  }
  
  /**
   * Fit a smooth bezier curve through points
   * No sharp corners - continuous everywhere
   */
  fitCurve(points: Point[]): void {
    if (points.length < 2) return;
    
    this.segments = [];
    
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];
      
      // Get surrounding points for tangent calculation
      const pPrev = points[i - 1] || p0;
      const pNext = points[i + 2] || p1;
      
      // Calculate smooth tangents (Catmull-Rom style)
      const tension = 0.5;
      
      const t1x = tension * (p1.x - pPrev.x);
      const t1y = tension * (p1.y - pPrev.y);
      const t2x = tension * (pNext.x - p0.x);
      const t2y = tension * (pNext.y - p0.y);
      
      // Control points for cubic bezier
      const control1: Point = {
        x: p0.x + t1x / 3,
        y: p0.y + t1y / 3
      };
      
      const control2: Point = {
        x: p1.x - t2x / 3,
        y: p1.y - t2y / 3
      };
      
      this.segments.push({
        start: p0,
        control1,
        control2,
        end: p1
      });
    }
  }
  
  /**
   * Evaluate point on curve at parameter t (0-1)
   */
  pointAt(t: number): Point {
    if (this.segments.length === 0) {
      return { x: 0, y: 0 };
    }
    
    const totalSegments = this.segments.length;
    const segmentT = t * totalSegments;
    const segmentIndex = Math.min(Math.floor(segmentT), totalSegments - 1);
    const localT = segmentT - segmentIndex;
    
    return this.evaluateBezier(this.segments[segmentIndex], localT);
  }
  
  /**
   * Cubic bezier evaluation
   */
  private evaluateBezier(seg: BezierSegment, t: number): Point {
    const mt = 1 - t;
    const mt2 = mt * mt;
    const mt3 = mt2 * mt;
    const t2 = t * t;
    const t3 = t2 * t;
    
    return {
      x: mt3 * seg.start.x + 3 * mt2 * t * seg.control1.x + 
         3 * mt * t2 * seg.control2.x + t3 * seg.end.x,
      y: mt3 * seg.start.y + 3 * mt2 * t * seg.control1.y + 
         3 * mt * t2 * seg.control2.y + t3 * seg.end.y
    };
  }
  
  /**
   * Get tangent at parameter t - always smooth, never undefined
   */
  tangentAt(t: number): Point {
    if (this.segments.length === 0) {
      return { x: 1, y: 0 };
    }
    
    const totalSegments = this.segments.length;
    const segmentT = t * totalSegments;
    const segmentIndex = Math.min(Math.floor(segmentT), totalSegments - 1);
    const localT = segmentT - segmentIndex;
    
    const seg = this.segments[segmentIndex];
    const mt = 1 - localT;
    
    // Derivative of cubic bezier
    const dx = 3 * mt * mt * (seg.control1.x - seg.start.x) +
               6 * mt * localT * (seg.control2.x - seg.control1.x) +
               3 * localT * localT * (seg.end.x - seg.control2.x);
    const dy = 3 * mt * mt * (seg.control1.y - seg.start.y) +
               6 * mt * localT * (seg.control2.y - seg.control1.y) +
               3 * localT * localT * (seg.end.y - seg.control2.y);
    
    // Normalize
    const len = Math.sqrt(dx * dx + dy * dy);
    return len > 0 ? { x: dx / len, y: dy / len } : { x: 1, y: 0 };
  }
  
  /**
   * Curvature at parameter t - continuous everywhere!
   * This is why beziers beat squares: no infinite curvature at corners
   */
  curvatureAt(t: number): number {
    if (this.segments.length === 0) return 0;
    
    const totalSegments = this.segments.length;
    const segmentT = t * totalSegments;
    const segmentIndex = Math.min(Math.floor(segmentT), totalSegments - 1);
    const localT = segmentT - segmentIndex;
    
    const seg = this.segments[segmentIndex];
    const mt = 1 - localT;
    
    // First derivative
    const dx = 3 * mt * mt * (seg.control1.x - seg.start.x) +
               6 * mt * localT * (seg.control2.x - seg.control1.x) +
               3 * localT * localT * (seg.end.x - seg.control2.x);
    const dy = 3 * mt * mt * (seg.control1.y - seg.start.y) +
               6 * mt * localT * (seg.control2.y - seg.control1.y) +
               3 * localT * localT * (seg.end.y - seg.control2.y);
    
    // Second derivative
    const ddx = 6 * mt * (seg.control2.x - 2 * seg.control1.x + seg.start.x) +
                6 * localT * (seg.end.x - 2 * seg.control2.x + seg.control1.x);
    const ddy = 6 * mt * (seg.control2.y - 2 * seg.control1.y + seg.start.y) +
                6 * localT * (seg.end.y - 2 * seg.control2.y + seg.control1.y);
    
    // Curvature formula: κ = |x'y'' - y'x''| / (x'^2 + y'^2)^(3/2)
    const cross = dx * ddy - dy * ddx;
    const denominator = Math.pow(dx * dx + dy * dy, 1.5);
    
    return denominator > 0 ? Math.abs(cross) / denominator : 0;
  }
  
  /**
   * Convert to SVG path - for rendering
   */
  toSVGPath(): string {
    if (this.segments.length === 0) return '';
    
    let path = `M ${this.segments[0].start.x} ${this.segments[0].start.y}`;
    
    for (const seg of this.segments) {
      path += ` C ${seg.control1.x} ${seg.control1.y}, ${seg.control2.x} ${seg.control2.y}, ${seg.end.x} ${seg.end.y}`;
    }
    
    if (this._closed) {
      path += ' Z';
    }
    
    return path;
  }
  
  /**
   * Get bounding box
   */
  getBounds(): { minX: number; minY: number; maxX: number; maxY: number } {
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
    // Sample the curve
    for (let t = 0; t <= 1; t += 0.01) {
      const p = this.pointAt(t);
      minX = Math.min(minX, p.x);
      minY = Math.min(minY, p.y);
      maxX = Math.max(maxX, p.x);
      maxY = Math.max(maxY, p.y);
    }
    
    return { minX, minY, maxX, maxY };
  }
  
  get closed(): boolean {
    return this._closed;
  }
  
  get segmentCount(): number {
    return this.segments.length;
  }
}

/**
 * Utility: interpolate between two bezier objects
 * Smooth morphing - no snapping
 */
export function interpolateBezier(_a: NBezierObject, _b: NBezierObject, _t: number): NBezierObject {
  const result = new NBezierObject();
  // TODO: Implement bezier interpolation
  // This enables smooth animations between any shapes
  return result;
}

/**
 * The canonical Newton OS shapes
 */
export const NShapes = {
  /**
   * Standard squircle - the default shape
   */
  squircle: (x: number, y: number, size: number) => 
    NBezierObject.squircle(x, y, size),
  
  /**
   * Window shape - slightly less round
   */
  window: (x: number, y: number, width: number, height: number) =>
    NBezierObject.superellipse({ cx: x, cy: y, rx: width/2, ry: height/2, n: 6 }),
  
  /**
   * Button shape - rounder
   */
  button: (x: number, y: number, width: number, height: number) =>
    NBezierObject.superellipse({ cx: x, cy: y, rx: width/2, ry: height/2, n: 4 }),
  
  /**
   * Icon shape - the Apple squircle
   */
  icon: (x: number, y: number, size: number) =>
    NBezierObject.superellipse({ cx: x, cy: y, rx: size/2, ry: size/2, n: 5 }),
  
  /**
   * Pill shape - very round ends
   */
  pill: (x: number, y: number, width: number, height: number) =>
    NBezierObject.superellipse({ cx: x, cy: y, rx: width/2, ry: height/2, n: 2.5 }),
};

// Export for global use
export default NBezierObject;
