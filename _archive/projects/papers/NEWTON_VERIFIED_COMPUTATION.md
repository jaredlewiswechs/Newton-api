# Newton: Verified Computation Through Constraint-First Architecture

**Technical Report**

Jared Lewis
Ada Computing Company
Houston, Texas

February 2026

---

## Abstract

We present Newton, a computational architecture that inverts the traditional relationship between execution and verification. Rather than executing operations and subsequently validating results, Newton permits only those state transitions that satisfy constraints at the moment of execution. The system combines two foundational mechanisms: Bounded Mechanical Execution (BME), which governs what computation may exist, and Constraint-Mediated Finite Knowledge (CMFK), which governs what knowledge may be trusted or acted upon. Together, these mechanisms define a class of systems where invalid states are not merely detected but are ontologically unrepresentable. We describe the architecture, its theoretical foundations, and its application to a knowledge retrieval agent that achieves deterministic behavior for equivalent inputs.

---

## 1. Introduction

Contemporary AI systems follow a generative paradigm: produce output, then verify. This ordering creates a fundamental tension. By the time verification occurs, potentially harmful or incorrect content has already been generated. The system must then decide whether to suppress, modify, or release what it has created.

Newton takes a different approach. Verification is not a phase that follows generation. Verification *is* the mechanism of execution. A computation proceeds if and only if it satisfies its constraints. If constraints are not satisfied, no state transition occurs.

This paper describes the architecture that enables this behavior and the theoretical principles underlying it.

### 1.1 The Core Principle

The fundamental operation in Newton reduces to:

```python
def newton(current, goal):
    return current == goal
```

When the result is `True`, execution proceeds. When `False`, execution halts. This is not a utility function applied to computations. It is the structure of computation itself.

### 1.2 Scope

This report covers:

1. The two foundational mechanisms (BME and CMFK) and their relationship
2. The theoretical lineage connecting Newton to prior work in constraint systems
3. A concrete implementation: a knowledge retrieval agent with verified responses
4. Empirical results demonstrating determinism, bounded execution, and safety properties

---

## 2. Foundational Mechanisms

Newton rests on two orthogonal invariants that together define its computational model.

### 2.1 Bounded Mechanical Execution (BME)

BME governs what computation may exist.

In conventional systems, computation flows from instructions to results. Errors are detected after the fact and handled through exceptions, rollbacks, or recovery procedures. The system permits illegal intermediate states and relies on subsequent mechanisms to restore consistency.

BME inverts this model:

- **The constraint is the instruction.** Constraints do not filter results; they define what operations are expressible.
- **Illegal states are unrepresentable.** The system does not detect and reject invalid states. It cannot represent them.
- **Verification equals execution.** There is no separate verification phase. The act of checking constraints *is* the act of computing.

BME introduces two ontological states beyond success and failure:

- **fin**: Computation completed within bounds
- **finfr**: Computation rejected because it would violate constraints

These are not error codes. They are fundamental states of existence within the system. A computation that would produce an invalid state does not fail—it never begins.

**Bidirectionality.** BME enforces constraints in both temporal directions:

- *Forward*: A state can only be reached if constraints permit it
- *Backward*: Every committed state has a complete, lawful derivation

A state exists if and only if it is both reachable and explainable.

### 2.2 Constraint-Mediated Finite Knowledge (CMFK)

CMFK governs what knowledge may be trusted or acted upon.

Where BME controls the mechanics of computation, CMFK controls the epistemics. It addresses a distinct question: given that a computation is mechanically valid, should its results be believed or acted upon?

CMFK treats claims as proposed state transitions rather than outputs:

- **Claims require grounding.** A statement is not output until evidence supports it.
- **Confidence is computed.** Certainty levels derive from source quality, corroboration, and recency—not from model probability distributions.
- **Provenance is mandatory.** Every claim carries its derivation history.
- **Policies execute before mutation.** Governance constraints are checked prior to state changes, not after.
- **Logs are execution gates.** The audit trail is not a record of what happened. It is a precondition for anything happening.

### 2.3 The Vertical Relationship

BME and CMFK are not parallel systems. They are vertical:

| Layer | Mechanism |
|-------|-----------|
| What computation may exist | BME |
| What knowledge may be trusted | CMFK |

A system implementing only BME can guarantee mechanical correctness but may still propagate ungrounded claims. A system implementing only CMFK can govern knowledge but may permit illegal intermediate states during computation. Newton requires both.

---

## 3. Theoretical Lineage

Newton builds on several decades of research in constraint-based systems. Understanding this lineage clarifies what Newton contributes and what it inherits.

### 3.1 Constraint Programming Origins

**Sketchpad (Sutherland, 1963).** The first system to treat constraints as persistent relationships rather than one-time computations. Users specified geometric constraints; the system maintained them through direct manipulation. Sketchpad established that constraints could be declarative specifications that the runtime is responsible for satisfying.

**ThingLab (Borning, 1981).** Extended Sketchpad's ideas into a general programming framework. Introduced constraint hierarchies and demonstrated that constraint satisfaction could be a general computational paradigm. ThingLab showed that constraints need not be solved once but can be continuously maintained.

**Constraint Logic Programming (Jaffar & Lassez, 1987).** Unified constraint satisfaction with logic programming. Established formal semantics for constraint systems and proved properties about their behavior. CLP provided the theoretical foundation for reasoning about what constraint systems can and cannot compute.

**Propagators (Radul & Sussman, 2009).** Modeled computation as autonomous agents propagating partial information through a network. Demonstrated that constraint propagation could be the *entire* computational model, not just a solving technique. Propagators showed that multi-directional information flow was computationally tractable.

### 3.2 What Newton Adds

Prior systems address pieces of the problem:

| System | Contribution | Limitation |
|--------|--------------|------------|
| Sketchpad | Persistent constraints | Limited to geometry |
| ThingLab | Constraint hierarchies | No formal execution bounds |
| CLP | Formal semantics | No epistemic governance |
| Propagators | Multi-directional flow | No ontological rejection |

Newton's contribution is the *composition*:

- Ontological rejection (finfr as a first-class state)
- Constraint-as-instruction (not constraint-as-filter)
- Ledgered execution (audit trail as gate, not receipt)
- Epistemic governance (CMFK layer)
- Verification as runtime mechanism (not post-processing)

No prior system combines these properties. The novelty lies in the architecture, not the individual components.

### 3.3 Relationship to Type Theory

Newton's architecture has structural similarities to dependent type theory:

- Constraints function as types
- Valid states are values that inhabit those types
- Invalid states are values that inhabit no type
- Execution is type-checked state transition

In a dependently-typed language, one might write:

```
transition : (s : State) → Lawful s → State
```

A transition requires a proof of lawfulness. Without the proof, the transition cannot be expressed. Newton approximates this at runtime rather than compile time.

### 3.4 Relationship to Model Checking

Bounded model checking (Clarke et al., 2001) explores system states up to a fixed depth to verify properties. Newton applies a similar principle:

- All computation is bounded (iterations, recursion, time)
- Properties are checked at each transition
- Completeness is traded for decidability

The key difference: model checking verifies a separate specification against an implementation. In Newton, the specification *is* the implementation.

---

## 4. Architecture

### 4.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         NEWTON PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input                                                          │
│    │                                                            │
│    ▼                                                            │
│  ┌──────────────────┐                                           │
│  │ Constraint Check │ ← Safety policies (BME + CMFK)            │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ Identity         │ ← Self-knowledge (defined, not retrieved) │
│  └────────┬─────────┘                                           │
│           │                                                     │
│  ┌──────────────────┐                                           │
│  │ Computation      │ ← Bounded arithmetic (BME)                │
│  └────────┬─────────┘                                           │
│           │                                                     │
│  ┌──────────────────┐                                           │
│  │ Knowledge Base   │ ← Verified facts with provenance (CMFK)   │
│  └────────┬─────────┘                                           │
│           │                                                     │
│  ┌──────────────────┐                                           │
│  │ External Ground  │ ← Source verification (CMFK)              │
│  └────────┬─────────┘                                           │
│           │                                                     │
│  ┌──────────────────┐                                           │
│  │ Ledger           │ ← Hash-chained audit (execution gate)     │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  Output {content, verified, trace, hash}                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  CONTINUOUS PROCESSES                                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────────┐                         │
│  │ Ada         │    │ Meta Newton     │                         │
│  │ (Sentinel)  │    │ (Self-Verifier) │                         │
│  │             │    │                 │                         │
│  │ Drift       │    │ Recursive       │                         │
│  │ detection   │    │ verification    │                         │
│  └─────────────┘    └─────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Execution Bounds

All computation operates within explicit bounds:

```python
@dataclass
class ExecutionBounds:
    max_iterations: int = 10000
    max_recursion_depth: int = 100
    max_operations: int = 1000000
    timeout_seconds: float = 30.0
```

These are not soft limits. They are hard constraints enforced by the runtime. A computation that would exceed them returns `finfr`—it is ontologically rejected.

### 4.3 Knowledge Retrieval

The knowledge base implements a three-tier retrieval system:

**Tier 1: Shape Matching (~0ms)**

Queries have geometric structure. "What is the capital of France?" maps to `CAPITAL(France) = ?`. Pattern matching identifies this shape and resolves it directly.

**Tier 2: Semantic Fields (~200ms)**

When patterns fail, semantic field resolution uses lexical databases to find overlapping concepts. "What city does France govern from?" shares semantic overlap with capital-related terms. The overlap is computed through set intersection, not neural embedding.

**Tier 3: Embedding Fallback (~100ms)**

Vector similarity as a fallback when discrete methods fail.

The ordering matters. Shape matching is deterministic and fast. Semantic fields are interpretable. Embeddings are a last resort.

### 4.4 The Ledger

Every operation is recorded in a hash-chained ledger:

```python
@dataclass
class LedgerEntry:
    index: int
    timestamp: datetime
    operation: str
    input_hash: str
    output_hash: str
    previous_hash: str
    entry_hash: str
```

The ledger is not a log of what happened. It is a precondition for state commitment. A state transition that cannot be recorded cannot occur.

---

## 5. Implementation: Newton Agent

We implemented these principles in a knowledge retrieval agent. The agent answers questions, performs calculations, and provides verified information.

### 5.1 Pipeline Stages

1. **Ada Sense**: Pattern detection for adversarial inputs
2. **Constraint Check**: Safety policy enforcement (before processing)
3. **Identity Check**: Self-knowledge queries (defined, not retrieved)
4. **Computation**: Bounded arithmetic evaluation
5. **Knowledge Base**: Verified fact retrieval
6. **Knowledge Mesh**: Cross-source verification
7. **LLM (optional)**: Generation for queries outside KB coverage
8. **Ada Watch**: Response monitoring
9. **Grounding**: External source verification
10. **Meta Verify**: Self-verification of all operations

### 5.2 Identity

The agent's self-knowledge is not stored or retrieved. It is defined:

```python
@dataclass
class Identity:
    name: str = "Newton"
    creator: str = "Jared Lewis"

    trust: Dict[str, bool] = field(default_factory=lambda: {
        "self": True,
        "constraints": True,
        "ledger": True,
        "llm_output": False,
        "external_claims": False,
    })
```

Questions about identity are answered from this definition. There is no retrieval, no generation, no uncertainty.

### 5.3 Safety Constraints

Safety policies are checked before any processing:

```python
SAFETY_CONSTRAINTS = {
    "harm": [...],
    "medical": [...],
    "legal": [...],
    "security": [...],
}
```

Harmful inputs are rejected at the gate. No generation occurs. There is no output to filter because there is no output.

---

## 6. Results

### 6.1 Verification Tests

We validated the system against eight properties:

| Test | Property | Result |
|------|----------|--------|
| Identity | Agent knows its own identity | Pass |
| Knowledge | Verified facts return correct answers | Pass |
| Safety | Harmful requests blocked before processing | Pass |
| Determinism | Same input produces identical output hash | Pass |
| Trust | Correct trust model (self vs. external) | Pass |
| Meta | Self-verification catches constraint violations | Pass |
| Drift | Sentinel detects baseline changes | Pass |
| Integration | Full pipeline operates correctly | Pass |

### 6.2 Performance

| Query Type | Response Time | Verified |
|------------|---------------|----------|
| Identity | <1ms | Yes |
| Arithmetic | <10ms | Yes |
| Knowledge Base | <100ms | Yes |
| Semantic Resolution | ~200ms | Yes |
| LLM Fallback | 1-5s | Post-verified |

### 6.3 Determinism

For the query "What is the capital of France?", five consecutive runs produced identical output hashes:

```
Run 1: fb0730c138117cc9
Run 2: fb0730c138117cc9
Run 3: fb0730c138117cc9
Run 4: fb0730c138117cc9
Run 5: fb0730c138117cc9
```

Equivalent inputs produce equivalent outputs.

---

## 7. Limitations

**Knowledge coverage.** The current knowledge base contains approximately 1,000 verified facts. Long-tail queries fall back to LLM generation with post-verification.

**Language support.** Currently English only.

**Static knowledge.** The knowledge base does not update in real time.

**Complex reasoning.** Multi-hop inference requires LLM fallback.

---

## 8. Related Work

**Constitutional AI (Bai et al., 2022).** Uses principles as training signal. Newton uses constraints as runtime execution control.

**Formal verification.** Coq, Agda, and similar systems prove properties at compile time. Newton enforces properties at runtime.

**Retrieval-augmented generation.** RAG systems retrieve then generate. Newton retrieves verified facts directly when possible, avoiding generation entirely.

---

## 9. Conclusion

Newton demonstrates that constraint-first computation is practical for knowledge retrieval systems. By combining Bounded Mechanical Execution (what computation may exist) with Constraint-Mediated Finite Knowledge (what knowledge may be trusted), the architecture achieves properties that are difficult to obtain in conventional systems:

- Determinism for equivalent inputs
- Bounded execution with formal termination
- Safety enforcement before processing
- Auditable state transitions

The core insight is architectural: verification is not a phase that follows execution. Verification *is* execution.

---

## References

Bai, Y., Kadavath, S., Kundu, S., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. *arXiv:2212.08073*.

Borning, A. (1981). The Programming Language Aspects of ThingLab. *ACM TOPLAS*, 3(4).

Clarke, E. M., Biere, A., Raimi, R., & Zhu, Y. (2001). Bounded Model Checking Using Satisfiability Solving. *Formal Methods in System Design*, 19(1).

Jaffar, J., & Lassez, J. L. (1987). Constraint Logic Programming. *POPL '87*.

Radul, A., & Sussman, G. J. (2009). The Art of the Propagator. *MIT CSAIL Technical Report*.

Sutherland, I. (1963). Sketchpad: A Man-Machine Graphical Communication System. *PhD Thesis, MIT*.

---

## Appendix A: Patent Architecture Summary

The two foundational mechanisms described in this paper correspond to distinct intellectual property:

**BME (Bounded Mechanical Execution)** defines what computation is allowed to exist. It covers:
- Constraint-as-instruction semantics
- Ontological rejection (finfr)
- Bidirectional state verification
- Ledgered execution gates

**CMFK (Constraint-Mediated Finite Knowledge)** defines what knowledge is allowed to matter. It covers:
- Evidence-grounded claims
- Computed confidence
- Mandatory provenance
- Pre-execution policy enforcement

These mechanisms are vertically integrated. A system that copies runtime semantics encounters BME. A system that copies governance and explainability encounters CMFK. Separating them produces either mechanical unsoundness or epistemic unreliability.

---

*Ada Computing Company. Houston, Texas. 2026.*
