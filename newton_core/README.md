# Newton Core - Rust Projection Engine

**Aid-a: Assistive Intelligence for Design Autonomy**

The mathematical bedrock for Newton's constraint-aware suggestion system.

```
┌─────────────────────────────────────────────────────────────────┐
│  Newton Core provides mathematically-proven constraint          │
│  projection using Dykstra's algorithm. Every suggestion is     │
│  guaranteed to satisfy all active constraints.                  │
│                                                                 │
│  The constraint IS the instruction.                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
cd newton_core

# Run all tests
cargo test

# Run property tests (10K+ cases each)
cargo test --release

# Run benchmarks
cargo bench

# Build library
cargo build --release
```

---

## The Aid-a Contract

Every suggestion returned by Aid-a MUST satisfy these guarantees:

### 1. Validity
```
∀ suggestion s ∈ response.suggestions:
    ∀ constraint c ∈ active_constraints:
        c.satisfied(s.state) == true
```

### 2. Determinism
```
suggest(state, intent, context) at time T₁ ==
suggest(state, intent, context) at time T₂

(Same inputs → identical ranked list, bitwise)
```

### 3. Termination
```
∀ inputs: suggest() completes within MAX_ITERATIONS
         AND within TIMEOUT_US microseconds
```

### 4. Non-Empty Guarantee
```
IF feasible_region(constraints) ≠ ∅:
    response.suggestions.len() ≥ 1
```

---

## Core Concepts

### The f/g Ratio

The f/g ratio measures constraint violation relative to effort:

```rust
pub enum FGState {
    Valid,                    // f/g = 0, fully inside
    Slack { margin: f64 },    // 0 < f/g < 1, margin = 1 - f/g
    Exact,                    // f/g ≈ 1, on boundary
    Finfr { excess: f64 },    // f/g > 1, excess = f/g - 1
}
```

### Constraint Types

**Convex (fast projection):**
- `BoxBounds`: min ≤ x ≤ max per dimension
- `LinearConstraint`: a·x ≤ b (halfspace)
- `NormBound`: ||x|| ≤ r (ball)

**Nonconvex (requires candidate search):**
- `CollisionConstraint`: no overlap with other objects
- `DiscreteConstraint`: x ∈ {v1, v2, ..., vn}

### Projection Algorithms

**Dykstra's Algorithm** — Projects onto convex constraint intersections:
- O(m) per iteration, typically 10-50 iterations
- Deterministic given same input
- Converges for any convex constraint intersection

**Halfspace Projection** — For linear constraints:
```
Π(p) = p - max(0, (a·p - b) / ||a||²) * a
```

**Box Projection** — For bounds:
```
Π(p)_i = clamp(p_i, min_i, max_i)
```

---

## Architecture

```
newton_core/
├── Cargo.toml           # Package config
├── AIDA_SPEC.md         # Frozen specification (v1.0)
├── src/
│   ├── lib.rs           # Public API
│   ├── linalg.rs        # Vector operations
│   ├── primitives.rs    # NTObject, Bounds, FGState
│   ├── constants.rs     # EPSILON, TOLERANCE, MAX_ITERATIONS
│   ├── constraints/
│   │   ├── mod.rs
│   │   ├── trait.rs     # Constraint trait
│   │   ├── box_bounds.rs
│   │   ├── linear.rs
│   │   ├── collision.rs
│   │   └── discrete.rs
│   ├── projection/
│   │   ├── mod.rs
│   │   ├── dykstra.rs   # Main algorithm
│   │   ├── halfspace.rs
│   │   ├── weighted.rs
│   │   └── relaxation.rs
│   ├── candidates.rs    # Local search
│   ├── rank.rs          # Suggestion ranking
│   ├── explain.rs       # Human-readable explanations
│   ├── intent.rs        # Intent parsing
│   ├── aida.rs          # Main entry point
│   └── tests/
│       ├── mod.rs
│       ├── property.rs  # QuickCheck-style tests
│       └── adversarial.rs
└── benches/
    ├── projection_bench.rs
    └── candidate_bench.rs
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Projection (2D) | < 0.1ms p99 | `cargo bench` |
| Projection (8D) | < 0.3ms p99 | `cargo bench` |
| Projection (32D) | < 0.5ms p99 | `cargo bench` |
| Candidate verify | < 2ms for N=24 | `cargo bench` |
| Full suggest | < 5ms p99 | `cargo bench` |

---

## Testing

### Property Tests (proptest)

| ID | Property | Description |
|----|----------|-------------|
| P1 | Soundness | Projected point is inside constraint set |
| P2 | Nearest | No interior point is closer to original |
| P3 | Idempotent | project(project(x)) == project(x) |
| P4 | Interior Fixed | Points already inside don't move |
| P5 | Weighted | High-weight dimensions change less |
| P6 | Determinism | Same input → bitwise identical output |
| P7 | Order Independence | Constraint order doesn't affect result |

### Adversarial Tests

| ID | Test | Purpose |
|----|------|---------|
| A1 | Thin Slab | Ill-conditioned feasible region |
| A2 | Oscillation | Detect non-convergence |
| A3 | Skewed Weights | Extreme weight ratios (1000:1) |
| A4 | Teleportation | Low-weight dims shouldn't jump |
| A5 | Near-Zero Normal | Degenerate constraint handling |
| A6 | Duplicates | No double-counting |

```bash
# Run all tests
cargo test

# Run specific property test
cargo test property::

# Run adversarial tests
cargo test adversarial::
```

---

## Numeric Constants

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

---

## Usage Example

```rust
use newton_core::{
    Vector, Bounds, NTObject,
    constraints::{BoxBounds, LinearConstraint},
    projection::dykstra_project,
    aida::suggest,
};

// Create bounds constraint
let bounds = BoxBounds::new(
    Vector::new(vec![0.0, 0.0]),
    Vector::new(vec![100.0, 100.0])
);

// Create linear constraint: x + y <= 150
let linear = LinearConstraint::new(
    Vector::new(vec![1.0, 1.0]),
    150.0
);

// Project a point onto constraint intersection
let point = Vector::new(vec![80.0, 90.0]);  // Outside: x + y = 170
let projected = dykstra_project(&point, &[&bounds, &linear]);
// projected ≈ (75.0, 75.0) — on the line x + y = 150, inside box
```

---

## CI/CD

The `.github/workflows/aida-contract.yml` workflow enforces:

1. All property tests pass (10K+ cases each)
2. All adversarial tests pass
3. p99 latency within targets
4. Determinism verified across 3 consecutive runs

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial Phase 1 release |

---

## Mathematical Background

### Dykstra's Algorithm

For convex sets C_1, ..., C_m with non-empty intersection, Dykstra's algorithm converges to the projection onto ∩C_i.

**References:**
- Dykstra, R.L. (1983). "An Algorithm for Restricted Least Squares Regression"
- Boyle, J.P. & Dykstra, R.L. (1986). "A Method for Finding Projections onto the Intersection of Convex Sets in Hilbert Spaces"
- Boyd, S. & Vandenberghe, L. (2004). "Convex Optimization"

---

## License

Part of Newton Supercomputer. See root LICENSE file.

---

© 2026 Jared Nashon Lewis · Jared Lewis Conglomerate · Newton · Ada Computing Company

*"The constraint IS the instruction. 1 == 1."*
