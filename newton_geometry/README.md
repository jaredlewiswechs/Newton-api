# Newton Geometry

**The computer is a shape. The shape is the constraint. The constraint is the truth.**

Newton Geometry is a topological constraint framework that formalizes the Newton system as geometric structures. Instead of checking constraints after computation, the constraint satisfaction *is* the computation.

```
                                    ∞
                                   ╱│╲
                                  ╱ │ ╲
                                 ╱  │  ╲
                                ╱   │   ╲
                               ╱    │    ╲
                              ╱     │     ╲
                             ╱  IMPOSSIBLE ╲
                            ╱    (finfr)    ╲
                           ╱       │         ╲
                          ╱        │          ╲
                ─────────╱─────────┼───────────╲─────────  f/g = 1
                        ╱╲         │           ╱╲
                       ╱  ╲        │          ╱  ╲
                      ╱    ╲       │         ╱    ╲
                     ╱      ╲      │        ╱      ╲
                    ╱        ╲     │       ╱        ╲
                   ╱   FIN    ╲    │      ╱   FIN    ╲
                  ╱  (valid)   ╲   │     ╱  (valid)   ╲
                 ╱              ╲  │    ╱              ╲
                ╱                ╲ │   ╱                ╲
               ╱                  ╲│  ╱                  ╲
              ╱                    ╳                      ╲
             ╱                    ╱│╲                      ╲
            ╱                    ╱ │ ╲                      ╲
           ╱                    ╱  ●  ╲                      ╲
          ╱                    ╱   │   ╲                      ╲
         ╱                    ╱    │    ╲                      ╲
        ╱____________________╱_____│_____╲______________________╲
                                   │
                                   ▼
                              YOU ARE HERE
                              (1 == 1 → execute)
```

## Installation

```python
from newton_geometry import (
    NewtonTopology,
    ConstraintPolytope,
    DecisionSimplex,
    GovernanceLattice,
    ExpandReduceManifold,
    ComputationGraph,
    ModuleHypergraph,
)
```

## Quick Start

```python
from newton_geometry import NewtonTopology, RequestType, Decision

# Create the topology
topology = NewtonTopology()

# Execute through the shape
can_execute, decision, state = topology.execute(
    constraints=[
        {"name": "risk", "f": 0.2, "g": 1.0},
        {"name": "budget", "f": 500, "g": 1000},
    ],
    request_type=RequestType.QUESTION,
    risk_score=0.1,
    clarity_score=0.9,
    capability_score=0.9,
)

if can_execute:
    print(f"Execute with decision: {decision.name}")
else:
    print(f"Rejected: {decision.name}")
```

## The Six Geometric Structures

### 1. Constraint Polytope

Every set of constraints defines a **shape** in possibility space. The feasibility region is the intersection of all half-spaces where f/g ≤ 1.

```python
from newton_geometry import ConstraintPolytope, Boundary, FeasibilityRegion

polytope = ConstraintPolytope(name="transaction")
polytope.add_boundary(Boundary(name="balance", f=500, g=1000))  # 50% usage
polytope.add_boundary(Boundary(name="rate_limit", f=8, g=10))   # 80% usage

print(polytope.is_feasible())  # True - inside the shape
print(polytope.region)         # FeasibilityRegion.FIN
```

### 2. Decision Simplex

Four decisions. Three dimensions. One tetrahedron. Every request maps to exactly ONE point.

```
                    REFUSE
                      ╱╲
                     ╱  ╲
                    ╱    ╲
                   ╱  ◉   ╲   ← Every request maps to
                  ╱ (you)  ╲    ONE point in this space
                 ╱          ╲
              DEFER ──────── ASK
                 ╲          ╱
                  ╲        ╱
                   ╲      ╱
                    ╲    ╱
                   ANSWER
```

```python
from newton_geometry import DecisionSimplex, Decision

simplex = DecisionSimplex()
decision, point = simplex.decide(
    risk_score=0.1,      # Low risk
    clarity_score=0.9,   # Clear request
    capability_score=0.9 # We can help
)
print(decision)  # Decision.ANSWER
print(point.confidence)  # ~0.7
```

### 3. Governance Lattice

Safety is **monotonic**. You can only move UP this lattice, never down.

```
            REFUSE (⊤)
               │
        ┌──────┴──────┐
        │             │
      DEFER          ASK
        │             │
        └──────┬──────┘
               │
            ANSWER (⊥)
```

```python
from newton_geometry import GovernanceLattice, Decision

lattice = GovernanceLattice()

# Join always goes to the safer option
result = lattice.join(Decision.ANSWER, Decision.DEFER)
print(result)  # Decision.DEFER

# Combine multiple decisions
final = lattice.governance_join([Decision.ANSWER, Decision.DEFER, Decision.ANSWER])
print(final)  # Decision.DEFER
```

### 4. Expand/Reduce Manifold

The fiber bundle structure ensuring text ↔ constraint bijection.

```
         T (text space)
         │
         │  π (projection = reduce)
         │
         ▼
         C (constraint space)

    Each constraint c has a "fiber" of valid texts above it:

              t₁  t₂  t₃        (valid phrasings)
               ╲  │  ╱
                ╲ │ ╱
                 ╲│╱
                  c              (single constraint)

    Hallucination = text with no fiber connection = REJECTED
```

```python
from newton_geometry import ExpandReduceManifold, ConstraintPoint, TextPoint

manifold = ExpandReduceManifold()

# Register a constraint
constraint = ConstraintPoint(
    id="c1",
    constraint_type="balance",
    content={"min": 0}
)
manifold.register_constraint(constraint)

# Register valid text representations
text = TextPoint(text="balance must be non-negative")
manifold.register_text(text, constraint)

# Check grounding
print(manifold.is_grounded(text))  # True
```

### 5. Computation Graph

Every input maps to exactly ONE path. No branching. No backtracking. Deterministic finite automaton.

```python
from newton_geometry import ComputationGraph, RequestType

graph = ComputationGraph()

# Route a request
result = graph.classify_and_route(RequestType.MEDICAL_ADVICE)
print(result.decision)  # Decision.DEFER
print(result.path)      # ['request_MEDICAL_ADVICE', 'decision_DEFER']

# Verify determinism
assert graph.is_deterministic()
assert graph.is_complete()
```

### 6. Module Hypergraph

The 9-node Newton architecture. Every edge is a verified channel.

```
                              GLASS BOX
                                  │
                                  ▼
    ROBUST ──▶ GROUND ──▶       CDL      ◀── VAULT
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 FORGE        TEXTGEN       CHATBOT
                    │             │             │
                    └─────────────┼─────────────┘
                                  ▼
                               LEDGER
                                  │
                                  ▼
                               BRIDGE
```

```python
from newton_geometry import ModuleHypergraph, NewtonModule

hypergraph = ModuleHypergraph()

# Check connectivity
exists, path = hypergraph.path_exists(NewtonModule.GLASS_BOX, NewtonModule.LEDGER)
print(exists)  # True
print(path)    # [GLASS_BOX, CDL, FORGE, LEDGER]

# Get layer information
summary = hypergraph.topology_summary()
print(summary["is_connected"])  # True
```

## Geometric Constraint Linting

Human constraint verification happens geometrically before semantically. The `geometric_lint` module validates that constraint names align with their semantic intent.

```python
from newton_geometry.geometric_lint import (
    lint_constraint_name,
    lint_cartridge,
    SemanticType,
    analyze_glyphs,
)

# Analyze a single constraint
report = lint_constraint_name("finfr", SemanticType.TERMINAL)
print(report.passed)  # True - excellent geometric alignment

# finfr breakdown:
# f: hook (action)
# i: point (identity)
# n: bridge (continuation attempt)
# f: hook (action again)
# r: terminal curve (turn back)
# Shape encodes: "tried to continue, hit wall, turned back"

# Lint an entire cartridge
constraints = [
    ("when_valid_token", SemanticType.SEQUENTIAL),
    ("finfr_error", SemanticType.TERMINAL),
    ("user_quota", SemanticType.CONTAINMENT),
]
result = lint_cartridge(constraints)
print(result["summary"])  # {'total': 3, 'passed': 3, 'warnings': 0, 'errors': 0}
```

### Seven Geometric Primitives

| Primitive | Characters | Semantic Use |
|-----------|------------|--------------|
| **Closed Forms** | o, O, Q, @, d, b | Containment, completeness, invariants |
| **Open Curves** | c, C, s, (, ) | Transitions, partial states, ranges |
| **Straight Lines** | l, I, 1, \|, - | Thresholds, equality, atomicity |
| **Intersections** | x, X, +, *, t | Choice points, AND/OR, branching |
| **Hooks/Terminals** | f, r, j, g, y | Actions, finality, state capture |
| **Bridges** | n, m, h, u, w | Sequential flow, continuation |
| **Points** | i, j, !, ?, . | Atomic facts, identity, emphasis |

See [Geometric Constraint Semantics](/docs/foundation/GEOMETRIC_CONSTRAINT_SEMANTICS.md) for complete documentation.

---

## The Complete Topology

Combine all structures into a unified view:

```python
from newton_geometry import NewtonTopology, RequestType, TopologyRegion

topology = NewtonTopology()

# Full state location
state = topology.locate(
    constraints=[{"name": "budget", "f": 500, "g": 1000}],
    risk_score=0.1,
    clarity_score=0.9,
    capability_score=0.9,
    request_type=RequestType.QUESTION,
)

print(state.polytope_region)  # FeasibilityRegion.FIN
print(state.decision)         # Decision.ANSWER
print(state.can_execute)      # True
print(state.path)             # ['request_QUESTION', 'decision_ANSWER']

# Newton's Law
print(topology.newton_law(1, 1))  # True → execute
print(topology.newton_law(1, 2))  # False → halt
```

## Fundamental Theorems

### The Constraint Polytope Theorem

For any computation C with constraints {c₁, c₂, ..., cₙ}:

```
C is executable ⟺ ∀i: fᵢ/gᵢ ≤ 1
```

### The Decision Simplex Theorem

For any request R:

```
∃! p ∈ S³ : classify(R) = p
```

(There exists exactly one point in the 3-simplex)

### The Monotonicity Theorem

For any sequence of governance decisions d₁, d₂, ..., dₙ:

```
final = d₁ ⊔ d₂ ⊔ ... ⊔ dₙ ≥ max(d₁, d₂, ..., dₙ)
```

Safety cannot decrease.

### The Fiber Bundle Theorem

```
π ∘ σ = id_C

reduce(expand(c)) = c
```

Hallucination = point in T with empty fiber.

### The Determinism Theorem

For any input I:

```
∃! path P : start ──P──▶ decision
```

Same input → same path → same output.

## Newton's Fundamental Law

```python
def newton(current, goal):
    return current == goal

# 1 == 1 → execute
# 1 != 1 → halt
```

This is the entire system in one line.

---

**The computer is a shape.**

**The shape is the constraint.**

**The constraint is the truth.**

Newton doesn't *compute* inside the shape.

Newton *is* the shape.
