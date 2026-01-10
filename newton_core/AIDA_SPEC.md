# AIDA_SPEC.md v1.0

## Aid-a Specification: The Constitution

This document defines the mathematical and behavioral contract for Aid-a (Assistive Intelligence for Design Autonomy), Newton's suggestion engine. It is frozen and serves as the authoritative reference for all implementation decisions.

---

## 1. Core Definitions

### 1.1 The f/g Ratio (Canonical Form)

The f/g ratio measures constraint violation relative to effort. It is **delta-based**, not absolute.

```
Let:
  x     = current state
  Δ     = attempted change (intent vector)
  P     = valid set (constraint feasible region)
  x_try = x + Δ (attempted state)
  x*    = Π_P(x_try) (projection onto valid set)

Then:
  violation = ||x_try - x*||
  effort    = ||Δ|| + ε
  f/g ratio = violation / effort
```

**Interpretation:**
- `f/g = 0`: Fully valid, no constraint violation
- `0 < f/g < 1`: Inside bounds with margin remaining
- `f/g ≈ 1`: On the boundary exactly
- `f/g > 1`: Outside bounds (finfr state)

### 1.2 FGState Enumeration

```rust
pub enum FGState {
    Valid,                    // f/g = 0, fully inside
    Slack { margin: f64 },    // 0 < f/g < 1, margin = 1 - f/g
    Exact,                    // f/g ≈ 1, on boundary
    Finfr { excess: f64 },    // f/g > 1, excess = f/g - 1
}
```

### 1.3 NTObject (Newton Object)

The universal primitive. Everything in Newton is an NTObject.

```rust
pub struct NTObject {
    pub id: Uuid,
    pub name: String,
    pub bounds: Bounds,
    pub constraints: Vec<ConstraintRef>,
}
```

### 1.4 Bounds

Axis-aligned bounding box defining the valid region for an object's position/size.

```rust
pub struct Bounds {
    pub min: Vector,
    pub max: Vector,
}
```

---

## 2. Constraint System

### 2.1 Constraint Trait

All constraints implement this trait:

```rust
pub trait Constraint: Send + Sync {
    /// Check if point satisfies constraint
    fn satisfied(&self, point: &Vector) -> bool;

    /// Compute signed distance (negative = inside, positive = outside)
    fn distance(&self, point: &Vector) -> f64;

    /// Project point onto constraint boundary (nearest valid point)
    fn project(&self, point: &Vector) -> Vector;

    /// Human-readable description
    fn describe(&self) -> String;
}
```

### 2.2 Constraint Types

**Convex (fast projection):**
- `BoxBounds`: min ≤ x ≤ max per dimension
- `LinearConstraint`: a·x ≤ b (halfspace)
- `NormBound`: ||x|| ≤ r (ball)

**Nonconvex (requires candidate search):**
- `CollisionConstraint`: no overlap with other objects
- `DiscreteConstraint`: x ∈ {v1, v2, ..., vn}
- `DisjunctionConstraint`: C1 ∨ C2 ∨ ... ∨ Cn

### 2.3 Convex vs Nonconvex Routing

```
IF all active constraints are convex:
    → Use Dykstra's algorithm (fast, exact)
ELSE:
    → Use convex relaxation + candidate search
    → Verify each candidate against all constraints
```

---

## 3. Projection Algorithms

### 3.1 Dykstra's Algorithm (Convex Projection)

Projects a point onto the intersection of convex sets.

```
Input: point p, constraints C = {C_1, ..., C_m}
Output: projection p* ∈ ∩C_i

Initialize:
  x_0 = p
  y_i = 0 for all i (increment vectors)

Repeat until convergence:
  For each constraint C_i:
    z = x + y_i
    x' = Π_{C_i}(z)           # Project onto C_i
    y_i = z - x'              # Update increment
    x = x'

  If ||x - x_prev|| < TOLERANCE:
    Return x
```

**Properties:**
- Converges for any convex constraint intersection
- O(m) per iteration, typically 10-50 iterations
- Deterministic given same input

### 3.2 Halfspace Projection

For linear constraint a·x ≤ b:

```
Π(p) = p - max(0, (a·p - b) / ||a||²) * a
```

### 3.3 Box Projection

For bounds [min, max]:

```
Π(p)_i = clamp(p_i, min_i, max_i)
```

### 3.4 Weighted Projection

Weighted Euclidean projection respects importance of dimensions.

```
Input: point p, constraints C, weights W
Output: weighted projection p*

Transform: p' = W^(1/2) * p
Project:   p'* = Π_C'(p')     # In scaled space
Untransform: p* = W^(-1/2) * p'*
```

### 3.5 Local Search Discipline

For nonconvex constraints, local search MUST be:

1. **Radial:** Candidates generated in concentric shells around convex projection
2. **Monotonic:** Each shell strictly increases distance from center
3. **Deterministic:** Within each shell, candidates ordered lexicographically
4. **Bounded:** Early exit on quota OR all shells exhausted

```rust
const SHELL_RADII: [f64; 5] = [1.0, 2.0, 4.0, 8.0, SEARCH_RADIUS];
const MAX_CANDIDATES: usize = 24;
```

---

## 4. The Aid-a Contract

Every suggestion returned by Aid-a MUST satisfy these guarantees:

### 4.1 Validity
```
∀ suggestion s ∈ response.suggestions:
    ∀ constraint c ∈ active_constraints:
        c.satisfied(s.state) == true
```

### 4.2 Determinism
```
suggest(state, intent, context) at time T₁ ==
suggest(state, intent, context) at time T₂

(Same inputs → identical ranked list, bitwise)
```

### 4.3 Termination
```
∀ inputs: suggest() completes within MAX_ITERATIONS
         AND within TIMEOUT_US microseconds
```

### 4.4 Monotonicity of Explanation
```
∀ suggestion s:
    apply(s.explanation.diff, original_state) == s.state
```

### 4.5 Non-Empty Guarantee
```
IF feasible_region(constraints) ≠ ∅:
    response.suggestions.len() ≥ 1
```

---

## 5. Numeric Policy

### 5.1 Constants

```rust
/// Machine epsilon for floating point comparisons
pub const EPSILON: f64 = 1e-10;

/// Convergence tolerance for projection algorithms
pub const TOLERANCE: f64 = 1e-8;

/// Maximum iterations for Dykstra's algorithm
pub const MAX_ITERATIONS: usize = 100;

/// Maximum candidates to generate in nonconvex search
pub const MAX_CANDIDATES: usize = 24;

/// Search radius for local candidate generation
pub const SEARCH_RADIUS: f64 = 100.0;

/// Timeout for suggestion generation (microseconds)
pub const TIMEOUT_US: u64 = 500_000; // 500ms
```

### 5.2 Tie-Breaking

When multiple points have equal distance:
1. Sort by lexicographic order of position vector
2. Use stable sort to preserve input order for truly equal elements

### 5.3 Near-Zero Handling

```rust
fn safe_divide(a: f64, b: f64) -> f64 {
    a / (b + EPSILON)
}

fn is_near_zero(x: f64) -> bool {
    x.abs() < EPSILON
}
```

---

## 6. Response Types

### 6.1 SuggestionQuality

```rust
pub enum SuggestionQuality {
    /// Exact constraint satisfaction achieved
    Exact,

    /// Near intent, required interpolation
    Near,

    /// Fell back to convex relaxation only
    Relaxed,
}
```

### 6.2 Suggestion

```rust
pub struct Suggestion {
    pub state: Vector,
    pub fg_state: FGState,
    pub intent_preserved: f64,  // 0.0 to 1.0
    pub explanation: String,
}
```

### 6.3 AidAResponse

```rust
pub struct AidAResponse {
    pub suggestions: Vec<Suggestion>,
    pub quality: SuggestionQuality,
    pub search_stats: SearchStats,
}
```

---

## 7. Stress Test Matrix

### 7.1 Property Tests (QuickCheck)

| ID | Property | Description |
|----|----------|-------------|
| P1 | Soundness | Projected point is inside constraint set |
| P2 | Nearest | No interior point is closer to original |
| P3 | Idempotent | project(project(x)) == project(x) |
| P4 | Interior Fixed | Points already inside don't move |
| P5 | Weighted | High-weight dimensions change less |
| P6 | Determinism | Same input → bitwise identical output |
| P7 | Order Independence | Constraint order doesn't affect result |

### 7.2 Adversarial Tests

| ID | Test | Purpose |
|----|------|---------|
| A1 | Thin Slab | Ill-conditioned feasible region |
| A2 | Oscillation | Detect non-convergence |
| A3 | Skewed Weights | Extreme weight ratios (1000:1) |
| A4 | Teleportation | Low-weight dims shouldn't jump |
| A5 | Near-Zero Normal | Degenerate constraint handling |
| A6 | Duplicates | No double-counting |

### 7.3 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Projection (2D) | < 0.1ms p99 | `cargo bench` |
| Projection (8D) | < 0.3ms p99 | `cargo bench` |
| Projection (32D) | < 0.5ms p99 | `cargo bench` |
| Candidate verify | < 2ms for N=24 | `cargo bench` |
| Full suggest | < 5ms p99 | `cargo bench` |

### 7.4 Scenario Tests

| Scenario | Behavior |
|----------|----------|
| Drag into wall | Smooth resistance increase |
| Resize too large | Preserve aspect ratio if semantic |
| Collision | Return relocation suggestions |
| Frame stability | No jitter in continuous interaction |

---

## 8. Exit Criteria

Phase 1 is complete when ALL of the following pass:

- [ ] All 7 property tests green (10,000 cases each)
- [ ] All 6 adversarial tests green
- [ ] p99 latency < 0.5ms for 8D projection
- [ ] CI workflow passes on all commits
- [ ] Determinism verified across 3 consecutive runs

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial frozen specification |

---

## Appendix A: Mathematical Background

### A.1 Convex Sets

A set C is convex if for all x, y ∈ C and λ ∈ [0,1]:
```
λx + (1-λ)y ∈ C
```

### A.2 Projection onto Convex Set

The projection Π_C(p) is the unique point in C closest to p:
```
Π_C(p) = argmin_{x ∈ C} ||x - p||
```

### A.3 Dykstra's Algorithm Convergence

For convex sets C_1, ..., C_m with non-empty intersection:
- Dykstra's algorithm converges to the projection onto ∩C_i
- Convergence is linear with rate dependent on angles between sets

### A.4 References

- Dykstra, R.L. (1983). "An Algorithm for Restricted Least Squares Regression"
- Boyle, J.P. & Dykstra, R.L. (1986). "A Method for Finding Projections onto the Intersection of Convex Sets in Hilbert Spaces"
- Boyd, S. & Vandenberghe, L. (2004). "Convex Optimization"
