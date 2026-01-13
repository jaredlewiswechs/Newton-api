# Constraint-First Computation: Formal Lineage Map

**Document Classification:** Computer Science Grade
**Author:** Jared Lewis
**Date:** January 13, 2026
**Status:** Reference Document

---

## Purpose

This document answers one question:

> "What is this, in the language computer science already understands?"

Not what it's called. Not why it's useful. Just where it sits in the intellectual map.

---

## Table of Contents

1. [Core Claim](#1-core-claim)
2. [Primary Ancestry](#2-primary-ancestry)
3. [Formal Mapping: System Components to CS Theory](#3-formal-mapping-system-components-to-cs-theory)
4. [The Constraint Definition Language (CDL)](#4-the-constraint-definition-language-cdl)
5. [Reversible State Machine](#5-reversible-state-machine)
6. [The Forge: Verification as Computation](#6-the-forge-verification-as-computation)
7. [Ratio Constraints (f/g)](#7-ratio-constraints-fg)
8. [Topological Language Machine (TLM)](#8-topological-language-machine-tlm)
9. [Proof-Carrying Computation](#9-proof-carrying-computation)
10. [What This Is Not](#10-what-this-is-not)
11. [Formal Classification](#11-formal-classification)
12. [Component-by-Component Mapping](#12-component-by-component-mapping)
13. [References](#13-references)

---

## 1. Core Claim

**Claim (Neutral, Review-Safe):**

> Computation can be structured so that validity is enforced by construction, not checked after execution, by defining execution as motion within a constraint-defined state space.

This places the work in **semantics + verification**, not "AI" or "tools."

The fundamental equation:

```
newton(current, goal) = current == goal
  → 1 == 1: execute
  → 1 != 1: halt (state does not exist)
```

This is not a runtime check. It is an ontological claim: states violating constraints are not values in the system's domain.

---

## 2. Primary Ancestry

### 2.1 Operational Semantics (Inverted)

**Standard view:**
Programs define transitions; semantics checks whether transitions are legal.

**Newton's view:**
Constraints define the space of possible transitions; execution is selecting a path already guaranteed to be legal.

| Traditional | Newton |
|-------------|--------|
| `State × Instruction → State' → validate(State')` | `Constraint → Admissible(State → State')` |

This is an **inversion of small-step operational semantics**. Semantics becomes primary; execution becomes secondary.

**Closest prior work:**
- Plotkin's Structural Operational Semantics (1981)
- But with the evaluation relation defined by constraint satisfaction rather than inference rules

### 2.2 Type Theory (Lifted to States)

There is a precise analogy:

| Type Theory | Newton |
|-------------|--------|
| Ill-typed programs don't compile | Ill-constrained states don't exist |
| Types restrict expressions | Laws restrict transitions |
| Dependent types encode invariants | Laws encode global invariants |
| Type inhabitation = term exists | Constraint satisfaction = state exists |

**Key distinction:**
- Dependent types still allow runtime proofs
- Newton precludes representability entirely

This aligns most closely with **refinement types over state transitions**, but applied globally, not locally.

**Closest prior work:**
- Liquid Types (Rondon, Kawaguchi, Jhala, 2008)
- Refinement Types (Freeman & Pfenning, 1991)
- But operating on the state-transition level, not expression level

### 2.3 Constraint Logic Programming

Newton is explicitly a **Constraint Logic Programming (CLP)** system.

**Standard CLP:**
```prolog
?- X > 0, X < 10, X mod 2 =:= 0.
X = 2 ; X = 4 ; X = 6 ; X = 8.
```

**Newton CLP:**
```python
law positive_even:
    when value:
        and value > 0
        and value < 10
        and value % 2 == 0
fin valid_value
```

The difference: Newton doesn't search for solutions. It **projects** the request onto the constraint manifold and returns the valid portion (or halts if empty).

**Closest prior work:**
- CLP(R) (Jaffar & Lassez, 1987)
- CHR (Frühwirth, 1991)
- But with projection semantics rather than search semantics

### 2.4 Design by Contract (Strengthened)

Newton implements Design by Contract where:
- Contracts are **unskippable**
- Contracts are **non-recoverable** (no exception handling for constraint violations)
- Preconditions define state existence, not just call validity

| DbC (Meyer) | Newton |
|-------------|--------|
| Precondition failure → exception | Precondition failure → state non-existence |
| Can be disabled in production | Cannot be disabled (is the semantics) |
| Documentation + runtime check | Definitional constraint |

**Closest prior work:**
- Eiffel (Meyer, 1986)
- But stronger: contracts define the domain, not just check inputs

---

## 3. Formal Mapping: System Components to CS Theory

### Overview Table

| Newton Component | CS Domain | Theoretical Foundation |
|------------------|-----------|------------------------|
| **CDL (Constraint Definition Language)** | Formal Languages | Context-free grammar with semantic predicates |
| **Forge** | Abstract Machines | Constraint automaton with verification semantics |
| **Vault** | Cryptography | Authenticated encryption with identity-derived keys |
| **Ledger** | Distributed Systems | Append-only log with Merkle authentication |
| **Bridge** | Consensus | PBFT-style Byzantine fault tolerance |
| **Robust Statistics** | Statistics | Median Absolute Deviation estimators |
| **Policy Engine** | Access Control | Attribute-based access control (ABAC) |
| **Negotiator** | Workflow | Human-in-the-loop approval automata |
| **Merkle Anchor** | Cryptographic Commitments | Merkle tree commitment schemes |
| **TLM** | Process Algebra | ACID-compliant symbolic kernel |
| **Newton Geometry** | Topology | Constraint manifolds in topological spaces |
| **Newton Core (Rust)** | Optimization | Dykstra's alternating projection algorithm |
| **Reversible Shell** | Reversible Computing | Bijective state machine |
| **tinyTalk** | DSL Design | Minimal constraint specification language |

---

## 4. The Constraint Definition Language (CDL)

### 4.1 Language Classification

CDL is a **domain-specific language** for constraint specification.

**Grammar class:** Context-free with semantic predicates

**Core constructs:**
```
LAW     ::= 'law' IDENTIFIER ':' WHEN_CLAUSE 'fin' IDENTIFIER
WHEN    ::= 'when' EXPR ':' CONDITION*
CONDITION ::= 'and' EXPR | 'and not' EXPR
RATIO   ::= 'finfr' (forbidden) | numeric ratio
```

### 4.2 Theoretical Positioning

CDL sits between:
- **Temporal Logic** (LTL/CTL): Can express temporal constraints via `history` predicates
- **First-Order Logic**: Can express quantified constraints
- **Linear Arithmetic**: Supports ratio constraints (f/g)

**Decidability:** CDL constraints over finite domains are decidable (reduces to SAT). CDL with linear arithmetic reduces to linear programming feasibility.

### 4.3 Formal Semantics

A CDL law defines a **characteristic function**:

```
⟦law L: when P: C₁ ∧ C₂ ∧ ... ∧ Cₙ fin⟧ : State → {⊤, ⊥}
```

Where:
- `⊤` means state is in the admissible region
- `⊥` means state is ontologically excluded

The operational semantics:

```
        ∀i. ⟦Cᵢ⟧(σ) = ⊤
─────────────────────────────────
    ⟦law L: when P: C* fin⟧(σ) = ⊤
```

---

## 5. Reversible State Machine

### 5.1 Theoretical Foundation

The Newton Shell implements a **reversible state machine** based on:

- **Reversible Computing** (Bennett, 1973; Landauer, 1961)
- **Bijective Automata** (Angluin, 1982)

**Definition:** A state machine is reversible iff every transition function is bijective.

### 5.2 Command Pairs

Every command has an inverse:

| Forward | Reverse | Semantics |
|---------|---------|-----------|
| `try` | `untry` | Attempt/rollback |
| `split` | `join` | Divide/merge |
| `lock` | `unlock` | Acquire/release |
| `take` | `give` | Transfer/return |
| `push` | `pop` | Stack operations |
| `mark` | `unmark` | Labeling |
| `step` | `unstep` | State advancement |

### 5.3 Formal Properties

**Theorem (Bijectivity):** For all command pairs (f, f⁻¹) and states σ:
```
f⁻¹(f(σ)) = σ
f(f⁻¹(σ)) = σ
```

**Theorem (Information Conservation):** Reversible transitions preserve Shannon entropy of the state space.

**Implication:** Perfect rollback without information loss. This enables:
- Speculative execution with guaranteed undo
- Time-travel debugging
- Transaction semantics without logging

### 5.4 Prior Work

- **Janus** (Yokoyama & Glück, 2007): Reversible programming language
- **RWHILE** (Glück & Yokoyama, 2016): Reversible structured programming
- Newton differs by making reversibility a **shell property**, not a language property

---

## 6. The Forge: Verification as Computation

### 6.1 Core Insight

The Forge implements: **verification IS the computation**.

This is not post-hoc checking. The verification step produces the result:

```python
result = forge.verify(constraint, object)
# result is not "was it valid?"
# result is "the valid projection of the request"
```

### 6.2 Theoretical Model

The Forge is an **abstract machine** with:

- **State:** Current constraint context Γ
- **Input:** Object to verify + constraint set
- **Transition:** Either produce valid result or halt (⊥)

```
         Γ ⊢ constraint(object) = ⊤
─────────────────────────────────────────
    Γ ⊢ forge(constraint, object) → object

         Γ ⊢ constraint(object) = ⊥
─────────────────────────────────────────
    Γ ⊢ forge(constraint, object) → ⊥
```

### 6.3 Constraint Projection (Newton Core / AIDA)

For requests that partially satisfy constraints, Newton Core implements **Dykstra's alternating projection algorithm**:

Given:
- Point `p` (the request)
- Convex constraint sets `C₁, C₂, ..., Cₙ`

Find the closest point in ∩Cᵢ to `p`.

```rust
// From newton_core/src/projection/
fn dykstra_project(point: &[f64], constraints: &[Constraint]) -> Option<Vec<f64>> {
    // Alternating projections onto constraint sets
    // Returns closest feasible point or None if infeasible
}
```

This enables the **GREEN/YELLOW/RED** state model:
- **GREEN:** Request fully within constraints (f/g < 0.9)
- **YELLOW:** Request near boundary (0.9 ≤ f/g < 1.0)
- **RED:** Request outside constraints (f/g ≥ 1.0) → project or halt

### 6.4 Complexity

**Verification complexity:** O(k · c · d) where:
- k = number of steps
- c = constraints per step
- d = maximum domain size

For typical parameters (k~10, c~5, d~100): **O(5000) = constant time**

---

## 7. Ratio Constraints (f/g)

### 7.1 Definition

Every constraint in Newton is expressed as a ratio:

```
f/g = demand / capacity
```

Where:
- `f` (forge): Resources/permissions/values requested
- `g` (ground): Resources/permissions/values available

### 7.2 Theoretical Significance

This is **dimensional analysis** applied to constraint specification.

| Domain | f | g | Interpretation |
|--------|---|---|----------------|
| Finance | spending | budget | Budget utilization |
| Compute | CPU requested | CPU available | Resource allocation |
| Probability | risk taken | risk budget | Risk management |
| Physics | force applied | force limit | Safety margin |

### 7.3 Properties

**Scale-invariance:** Ratios are dimensionless; constraints compose across scales.

**Compositionality:** `(f₁/g₁) × (f₂/g₂) = (f₁f₂)/(g₁g₂)`

**Physical interpretability:** Directly maps to engineering safety factors.

### 7.4 Prior Work

- **Units-of-measure type systems** (Kennedy, 1994)
- **Dimensional analysis** (Buckingham π theorem)
- **Control theory** safety margins

Newton's contribution: applying dimensional analysis to **computational constraints**, not just physical units.

---

## 8. Topological Language Machine (TLM)

### 8.1 Overview

The TLM is an **ACID-compliant symbolic kernel** with a 10-phase state machine.

### 8.2 Phase System

```
Phase 0: GROUND (initial state)
Phase 1: PARSE (input processing)
Phase 2: VALIDATE (constraint checking)
Phase 3: PLAN (execution planning)
Phase 4: EXECUTE (state modification)
Phase 5: VERIFY (post-condition check)
Phase 6: COMMIT (state persistence)
Phase 7: NOTIFY (event dispatch)
Phase 8: CLEANUP (resource release)
Phase 9: CRYSTALLIZE (final state)
Phase 0: GROUND (cycle complete)
```

### 8.3 ACID Properties

The TLM guarantees ACID semantics:

| Property | Implementation |
|----------|----------------|
| **Atomicity** | Bijective transitions; complete rollback on failure |
| **Consistency** | Constraint verification at phases 2, 5 |
| **Isolation** | Phase locking; no concurrent mutation |
| **Durability** | Ledger commit at phase 6 |

### 8.4 PARADOX Detection

Phase transitions include **contradiction detection**:

```python
class ParadoxDetector:
    def detect(self, state: State) -> Optional[Paradox]:
        # Returns contradiction if constraints are unsatisfiable
        # Detected BEFORE propagation
```

This is **static analysis at runtime**: contradictions are caught before they propagate.

### 8.5 Theoretical Positioning

The TLM combines:
- **Process algebra** (phase transitions as actions)
- **Transaction processing** (ACID semantics)
- **Abstract interpretation** (invariant checking)

**Closest prior work:**
- CSP (Hoare, 1978): Communicating Sequential Processes
- But with ACID guarantees and constraint semantics

---

## 9. Proof-Carrying Computation

### 9.1 Traditional PCC

**Proof-Carrying Code** (Necula, 1997) attaches explicit proof objects to code.

```
Code + Proof → Verify(Proof) → Execute(Code)
```

### 9.2 Newton's Approach

Newton implements **implicit PCC**:

```
Request → Constraint Check → (Execute if pass, ⊥ if fail)
```

The "proof" is embedded in the fact that execution occurred.

**Key insight:** A value exists iff it satisfies the constraint. The existence of the value IS the proof.

### 9.3 Formal Equivalence

This is equivalent to:
- **Realizability semantics:** A type is inhabited iff there exists a term
- **Curry-Howard:** Proofs are programs; programs are proofs

But implemented at runtime with rollback rather than compile-time with type checking.

### 9.4 Merkle Proofs

For external verification, Newton exports **Merkle proofs**:

```python
class MerkleAnchorScheduler:
    def generate_proof(self, entry_index: int) -> MerkleProof:
        # Returns cryptographic proof of entry inclusion
```

This converts implicit proof (execution occurred) to explicit proof (Merkle certificate).

---

## 10. What This Is Not

Explicit non-claims (important for positioning):

### 10.1 Not Model Checking

Model checking exhaustively explores state spaces. Newton does not explore; it projects.

### 10.2 Not Theorem Proving

Theorem provers construct proofs. Newton does not construct proofs; it defines domains.

### 10.3 Not Symbolic Execution

Symbolic execution explores paths with symbolic values. Newton operates on concrete values with constraint filtering.

### 10.4 Not SAT/SMT Solving

SAT/SMT solvers search for satisfying assignments. Newton projects requests onto constraint manifolds (no search).

### 10.5 Not "AI Safety"

This is not about making language models safer. This is about making **computation verifiable by construction**.

### 10.6 What It IS

> A computation model for domains where **invariants matter more than freedom**.

Application domains:
- Finance (transaction constraints)
- Safety-critical systems (physical limits)
- Education (curriculum standards)
- Infrastructure (deployment quotas)
- Compliance (regulatory requirements)

---

## 11. Formal Classification

### 11.1 One-Sentence Summary

> We present a constraint-first execution model in which program execution is defined as motion within a law-governed state space, making invalid states unrepresentable by construction rather than detectable by verification.

### 11.2 ACM Classification

- **D.3.1:** Formal Definitions and Theory
- **D.2.4:** Software/Program Verification
- **F.3.1:** Specifying and Verifying and Reasoning about Programs
- **F.4.1:** Mathematical Logic - Lambda calculus and related systems

### 11.3 Contribution Type

If submitted to a PL venue, this would be classified as:

1. **Semantics contribution:** Inversion of operational semantics (constraints primary)
2. **Verification contribution:** Verification as execution semantics
3. **Language design contribution:** Minimal constraint specification DSL

---

## 12. Component-by-Component Mapping

### 12.1 Core Modules

| File | CS Theory | Key Insight |
|------|-----------|-------------|
| `core/cdl.py` | Formal languages, Logic | Constraint specification as grammar |
| `core/logic.py` | Computability theory | Turing-complete with bounded execution |
| `core/forge.py` | Abstract machines | Verification automaton |
| `core/vault.py` | Cryptography | AEAD with identity derivation |
| `core/ledger.py` | Authenticated data structures | Merkle-authenticated append-only log |
| `core/bridge.py` | Distributed consensus | PBFT (Practical Byzantine Fault Tolerance) |
| `core/robust.py` | Robust statistics | MAD (Median Absolute Deviation) |
| `core/shell.py` | Reversible computing | Bijective state machine |
| `core/policy_engine.py` | Access control | ABAC (Attribute-Based Access Control) |
| `core/negotiator.py` | Workflow systems | Human-in-the-loop automata |
| `core/merkle_anchor.py` | Commitment schemes | Merkle tree commitments |

### 12.2 Advanced Subsystems

| Module | CS Theory | Key Insight |
|--------|-----------|-------------|
| `newton_core/` (Rust) | Optimization theory | Dykstra's alternating projections |
| `newton_tlm/` | Process algebra + ACID | Phase-structured symbolic kernel |
| `newton_geometry/` | Algebraic topology | Constraint manifolds |
| `construct-studio/` | Domain modeling | Ontological state exclusion |
| `newton-trace-engine/` | Program visualization | Constraint satisfaction as graph traversal |

### 12.3 tinyTalk Language

| Construct | CS Theory | Semantics |
|-----------|-----------|-----------|
| `Blueprint` | Record types | Named product type with constraints |
| `field()` | Refinement types | Value with domain restriction |
| `law` | Invariant specification | Global constraint assertion |
| `when/and/fin` | Guarded commands | Conditional constraint activation |
| `finfr` | Bottom type (⊥) | Ontological exclusion |
| `forge` | Constructors | Constraint-checked value creation |
| `ratio (f/g)` | Dimensional types | Scale-invariant constraint |

### 12.4 Cartridge System

| Cartridge | CS Theory | Specification Type |
|-----------|-----------|-------------------|
| Visual | Constraint satisfaction | SVG bounds (4096×4096, 1000 elements) |
| Sound | Signal processing | Audio limits (5 min, 22kHz) |
| Sequence | Multimedia | Video bounds (10 min, 8K, 120fps) |
| Data | Database theory | Tabular limits (100K rows) |
| Rosetta | Code generation | Multi-language output |

---

## 13. References

### Foundational

1. Plotkin, G. D. (1981). "A Structural Approach to Operational Semantics." DAIMI Report FN-19.

2. Jaffar, J. & Lassez, J-L. (1987). "Constraint Logic Programming." POPL '87.

3. Meyer, B. (1986). "Design by Contract." Technical Report TR-EI-12/CO.

4. Necula, G. C. (1997). "Proof-Carrying Code." POPL '97.

5. Hoare, C. A. R. (1978). "Communicating Sequential Processes." CACM 21(8).

### Reversible Computing

6. Landauer, R. (1961). "Irreversibility and Heat Generation in the Computing Process." IBM Journal.

7. Bennett, C. H. (1973). "Logical Reversibility of Computation." IBM Journal.

8. Yokoyama, T. & Glück, R. (2007). "A Reversible Programming Language and its Invertible Self-Interpreter." PEPM '07.

### Type Theory

9. Freeman, T. & Pfenning, F. (1991). "Refinement Types for ML." PLDI '91.

10. Rondon, P., Kawaguchi, M., & Jhala, R. (2008). "Liquid Types." PLDI '08.

### Optimization

11. Dykstra, R. L. (1983). "An Algorithm for Restricted Least Squares Regression." JASA 78(384).

### Cryptography

12. Bellare, M. & Namprempre, C. (2000). "Authenticated Encryption." ASIACRYPT 2000.

13. Merkle, R. C. (1987). "A Digital Signature Based on a Conventional Encryption Function." CRYPTO '87.

### Distributed Systems

14. Castro, M. & Liskov, B. (1999). "Practical Byzantine Fault Tolerance." OSDI '99.

### Robust Statistics

15. Hampel, F. R. et al. (1986). "Robust Statistics: The Approach Based on Influence Functions." Wiley.

---

## Appendix A: Theoretical Gaps and Open Questions

Areas where Newton's theoretical positioning could be strengthened:

1. **Completeness:** Is CDL complete for its intended domain? What is the expressive power relative to established constraint languages?

2. **Decidability boundaries:** What are the exact decidability boundaries for CDL with various extensions (temporal, probabilistic)?

3. **Compositionality:** Formal proof that constraint composition preserves invariants.

4. **Complexity bounds:** Tight complexity bounds for the projection algorithm under various constraint classes.

5. **Semantic equivalence:** Formal proof of equivalence between Newton's operational semantics and denotational specification.

---

## Appendix B: Suggested Formalization Path

For academic publication, the recommended formalization would be:

1. **Core calculus:** Extract minimal λ-calculus with constraint primitives
2. **Type system:** Define refinement type system for constraints
3. **Operational semantics:** Small-step semantics with constraint guards
4. **Soundness proof:** Type soundness (well-typed programs don't get stuck)
5. **Completeness proof:** All valid states are reachable

---

**Document Status:** CRYSTALLIZED
**Verification:** Mapped against codebase and existing documentation
**f/g ratio:** 1.0
**Fingerprint:** CS-THEORY-MAP-2026-01-13

---

*"We present a constraint-first execution model in which program execution is defined as motion within a law-governed state space, making invalid states unrepresentable by construction rather than detectable by verification."*

This is the door that opens first.
