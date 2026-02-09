# BiggestMAMA

## The Complete Nina Verified Computation System

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗ ██████╗  ██████╗ ███████╗███████╗████████╗                    ║
║   ██╔══██╗██║██╔════╝ ██╔════╝ ██╔════╝██╔════╝╚══██╔══╝                    ║
║   ██████╔╝██║██║  ███╗██║  ███╗█████╗  ███████╗   ██║                       ║
║   ██╔══██╗██║██║   ██║██║   ██║██╔══╝  ╚════██║   ██║                       ║
║   ██████╔╝██║╚██████╔╝╚██████╔╝███████╗███████║   ██║                       ║
║   ╚═════╝ ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝                       ║
║                                                                              ║
║   ███╗   ███╗ █████╗ ███╗   ███╗ █████╗                                     ║
║   ████╗ ████║██╔══██╗████╗ ████║██╔══██╗                                    ║
║   ██╔████╔██║███████║██╔████╔██║███████║                                    ║
║   ██║╚██╔╝██║██╔══██║██║╚██╔╝██║██╔══██║                                    ║
║   ██║ ╚═╝ ██║██║  ██║██║ ╚═╝ ██║██║  ██║                                    ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝                                    ║
║                                                                              ║
║   "1 == 1. The cloud is weather. We're building shelter."                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Nina: Newton Intelligence & Natural Assistant**

A single-file (~1200 lines) verified computation substrate that preserves the complete system architecture.

---

## Table of Contents

1. [The Fundamental Law](#the-fundamental-law)
2. [What Is BiggestMAMA?](#what-is-biggestmama)
3. [Quick Start](#quick-start)
4. [Architecture Overview](#architecture-overview)
5. [The 9-Stage Pipeline](#the-9-stage-pipeline)
6. [Computer Science Foundations](#computer-science-foundations)
7. [Trust Lattice & Information Flow Control](#trust-lattice--information-flow-control)
8. [Input Sanitization (Security)](#input-sanitization-security)
9. [Knowledge Integration](#knowledge-integration)
10. [The Newton Ecosystem](#the-newton-ecosystem)
11. [Examples](#examples)
12. [Extensions](#extensions)
13. [Formal Guarantees](#formal-guarantees)
14. [API Reference](#api-reference)

---

## The Fundamental Law

```python
def newton(current, goal):
    return current == goal

# When True  → execute
# When False → halt
```

This isn't a feature. **It's the architecture.**

---

## What Is BiggestMAMA?

BiggestMAMA is a **self-contained verified computation engine** - the complete Nina system in one portable file.

### The Difference

| Traditional Chatbot | Nina (BiggestMAMA) |
|---------------------|--------------|
| "Paris is the capital of France" | "Paris" ✓ `[TRUSTED]` *Source: CIA World Factbook* |
| "2 + 2 = 4" (maybe) | `14` ✓ `[TRUSTED]` *Computed: 3 ops, 1.85ms* |
| "I think..." | "I verify..." |
| Trust the model | Trust the math |
| No audit trail | Hash-chained provenance ledger |
| Arbitrary trust | Formal trust lattice: `UNTRUSTED ⊑ VERIFIED ⊑ TRUSTED` |

### Why "BiggestMAMA"?

It's the **Mother of All Modules Architecture** - everything Nina is, captured in one file that can never be lost.

---

## Quick Start

```bash
# Run directly
python BiggestMAMA.py

# Or import as a module
python -c "from BiggestMAMA import nina_query; print(nina_query('What is the capital of France?').value)"
```

### Output

```
╔══════════════════════════════════════════════════════════════════════════════╗
║   BIGGEST MAMA - Complete Nina Verified Computation System                   ║
║   "1 == 1. The cloud is weather. We're building shelter."                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

❓ Query: "What is the capital of France?"
   ✓ Answer: Paris
   ✓ Trust: VERIFIED
   ✓ Time: 0.78ms

❓ Query: "What is the capital of the USA?"
   ✓ Answer: Washington, D.C.
   ✓ Trust: VERIFIED
   ✓ Time: 0.33ms

❓ Query: "2 + 3 * 4"
   ✓ Answer: 14
   ✓ Trust: TRUSTED
   ✓ Time: 1.85ms
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BiggestMAMA                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER INPUT                                                                 │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STAGE 0: INPUT SANITIZATION (Defense in Depth)                     │   │
│  │  Shell: $ ` ; | & → Fullwidth Unicode (neutralized)                 │   │
│  │  XSS:   < >       → Fullwidth Unicode (neutralized)                 │   │
│  │  Control chars    → Removed                                         │   │
│  │  Length           → Bounded to 1000 chars                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  9-STAGE COMPILER PIPELINE                                          │   │
│  │                                                                     │   │
│  │  1. Intent Lock    │ 2. Parse       │ 3. Abstract Interp           │   │
│  │  4. Geometric Check│ 5. Verify      │ 6. Execute                   │   │
│  │  7. Log Provenance │ 8. Meta-check  │ 9. Return                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  OUTPUT: Answer = (v, π, trust-label, bounds-report, ledger-proof)  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The 9-Stage Pipeline

The heart of Nina - a unified compiler pipeline that transforms queries into verified answers.

| Stage | Name | Purpose | CS Concept |
|-------|------|---------|------------|
| 0 | **Sanitize** | Defense in depth | Input validation, injection prevention |
| 1 | **Intent Lock** | Choose regime R | Mode-dependent type environment |
| 2 | **Parse** | Shape grammar | Formal language theory, CFG |
| 3 | **Abstract Interpret** | Semantic field resolution | Abstract interpretation (Cousot) |
| 4 | **Geometric Check** | D(w,a) < θ(R) | Metric spaces, type soundness |
| 5 | **Verify/Upgrade** | Trust lattice | Information Flow Control (IFC) |
| 6 | **Execute** | Bounded computation | Total functional programming |
| 7 | **Log Provenance** | Hash-chained ledger | Merkle trees, blockchain |
| 8 | **Meta-check** | Invariant verification | Design by contract |
| 9 | **Return** | Final output | Dependent types |

---

## Computer Science Foundations

BiggestMAMA is built on rigorous CS foundations:

### 1. Information Flow Control (IFC)
**Denning's Lattice Model (1976)**

```
           KERNEL
              ↑
          TRUSTED
              ↑
          VERIFIED
              ↑
         UNTRUSTED
```

- Labels flow with data
- No implicit upgrade
- Only explicit verification can increase trust
- **Reference**: Denning, D.E. "A lattice model of secure information flow" (CACM 1976)

### 2. Abstract Interpretation
**Cousot & Cousot (1977)**

The pipeline performs abstract interpretation to resolve semantic fields:
- Concrete domain: User queries
- Abstract domain: Query shapes (CAPITAL_OF, POPULATION_OF, etc.)
- Galois connection: Parse ⇄ Interpret

### 3. Type Theory
**Dependent Types & Refinement Types**

```python
# The output type depends on the input
Answer = (value: T, trace: List[Stage], trust: TrustLabel, bounds: Bounds, proof: Ledger)
```

### 4. Formal Verification
**Design by Contract (Meyer)**

- Preconditions: Input sanitization, regime constraints
- Postconditions: Trust labels, bounded execution
- Invariants: Provenance chain integrity

### 5. Metric Spaces
**Distortion Metric**

```
D(w, a) = d(v(a), g(w))

where:
  g(w) = kinematic signature of word w
  v(a) = physics vector of action a
  d    = distance metric
```

If D(w,a) > θ(R), reject with suggestions. This is the "TRIM vs DIVE" principle.

---

## Trust Lattice & Information Flow Control

```python
class TrustLabel(Enum):
    UNTRUSTED = 0   # External/unverified data
    VERIFIED = 1    # Passed verification (Ollama, fallback KB)
    TRUSTED = 2     # Authoritative source (adan_portable KB)
    KERNEL = 3      # System invariants (immutable)
```

### The Upgrade Rule

```
upgrade(x) → higher trust  IFF  Verify(x) = True
```

**No implicit casts.** The only way to increase trust is through explicit verification.

### Source → Trust Mapping

| Source | Trust Level |
|--------|-------------|
| `adan_knowledge_base` | TRUSTED |
| `adan_store`, `adan_shape`, `adan_semantic`, `adan_keyword` | TRUSTED |
| `computation` (math) | TRUSTED |
| `ollama_governed` | VERIFIED |
| `fallback_kb` | VERIFIED |
| Unknown | UNTRUSTED |

---

## Input Sanitization (Security)

Defense in depth against injection attacks:

### Attack Neutralization

| Attack Type | Input | Output | Technique |
|------------|-------|--------|-----------|
| Shell Command Sub | `$(rm -rf /)` | `＄(rm -rf /)` | Fullwidth $ |
| Backtick Execution | `` `whoami` `` | `｀whoami｀` | Fullwidth ` |
| Command Chaining | `; DROP TABLE` | `； DROP TABLE` | Fullwidth ; |
| Pipe Injection | `| cat /etc/passwd` | `｜ cat /etc/passwd` | Fullwidth | |
| Background Exec | `& wget evil` | `＆ wget evil` | Fullwidth & |
| XSS Script | `<script>` | `＜script＞` | Fullwidth <> |
| Log Injection | `line1\nline2` | `line1 line2` | Remove newlines |
| Length Bomb | `"a" * 10000` | `"a" * 1000` | Truncate |

**Key insight**: Fullwidth Unicode characters look similar but don't execute.

---

## Knowledge Integration

### The Newton Ecosystem

BiggestMAMA connects to the broader Newton knowledge architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NEWTON KNOWLEDGE ECOSYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  BiggestMAMA    │     │   adan_portable │     │   newton_agent  │       │
│  │  (Self-contain) │────▶│   (Knowledge)   │◀────│   (Full Agent)  │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│          │                       │                       │                  │
│          │                       ▼                       │                  │
│          │              ┌─────────────────┐              │                  │
│          │              │    Adanpedia    │              │                  │
│          │              │  (Wiki Import)  │              │                  │
│          │              └─────────────────┘              │                  │
│          │                       │                       │                  │
│          └───────────────────────┼───────────────────────┘                  │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                              │
│                    │  CIA World Factbook     │                              │
│                    │  NIST Scientific Data   │                              │
│                    │  ISO Standards          │                              │
│                    │  Periodic Table         │                              │
│                    │  Company Facts          │                              │
│                    └─────────────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### adan_portable

The portable knowledge base package:
- **KnowledgeBase**: 2845+ lines of verified facts
- **KnowledgeStore**: Persistent storage for dynamically added facts
- **QueryParser**: Kinematic shape-based query parsing (20+ shapes)
- **SemanticResolver**: Datamuse API integration for fuzzy matching

### newton_agent

The full autonomous agent:
- **Ada Sentinel**: Drift detection, anomaly alerting
- **Meta Newton**: Self-verification (9 core rules)
- **TI Calculator**: Full mathematical expression parsing
- **Identity Module**: Self-knowledge ("I am Newton")
- **10-Step Pipeline**: Extended verification pipeline

### Adanpedia

Wikipedia-style interface to the knowledge base:
- Import facts from Wikipedia
- Browse KB like an encyclopedia
- Add custom verified facts
- Export to Newton ecosystem

---

## Examples

### Basic Query

```python
from BiggestMAMA import Pipeline, Regime, RegimeType

# Create pipeline
regime = Regime.from_type(RegimeType.FACTUAL)
pipeline = Pipeline(regime)

# Query
result = pipeline.process("What is the capital of France?")

print(result.value)        # "Paris"
print(result.trust_label)  # TrustLabel.TRUSTED
print(result.success)      # True
```

### Mathematical Computation

```python
result = pipeline.process("2 + 3 * 4")

print(result.value)        # 14
print(result.trust_label)  # TrustLabel.TRUSTED
print(result.bounds_report.operations_count)  # 7
```

### With Ollama Fallback

```python
result = pipeline.process("How do I learn Python?")

print(result.value)        # "To learn Python, start by..."
print(result.trust_label)  # TrustLabel.VERIFIED (not TRUSTED - LLM response)
```

### Checking the Provenance Ledger

```python
for entry in pipeline.get_ledger():
    print(f"[{entry['index']}] {entry['hash'][:16]}... prev: {entry['prev_hash'][:16]}...")
```

### Convenience Functions

```python
from BiggestMAMA import nina_query, nina_verify, nina_calculate

# Simple query
result = nina_query("What is the capital of Japan?")
print(result.value)  # "Tokyo"

# Verify a statement
verified, trust = nina_verify("Paris is the capital of France")
print(verified)  # True

# Calculate
answer, trust = nina_calculate("(2 + 3) * 4")
print(answer)  # 20
```

---

## Extensions

BiggestMAMA is designed to be extended:

### Custom Regime

```python
from BiggestMAMA import Regime, RegimeType, DomainRule

# Create a custom regime for financial queries
financial_regime = Regime(
    regime_type=RegimeType.CUSTOM,
    name="financial",
    description="Financial operations with strict verification",
    ambiguity_tolerance=0.0,  # No ambiguity allowed
    distortion_threshold=0.1,  # Very strict language matching
    trusted_sources={"ledger", "bank_api", "verified_transactions"}
)
```

### Custom Verifier

```python
from BiggestMAMA import TrustLattice, TrustLabel

lattice = TrustLattice()

# Register a custom verifier
def verify_bank_balance(amount):
    return amount >= 0  # Balances can't be negative

lattice.register_verifier("bank_balance", verify_bank_balance)

# Use it
balance = lattice.untrusted(100, "user_input")
trusted_balance = lattice.upgrade(balance, verify_bank_balance, TrustLabel.TRUSTED)
```

### Adding to Knowledge Base

When connected to `adan_portable`:

```python
from adan.knowledge_store import get_knowledge_store

store = get_knowledge_store()
store.add_fact(
    key="Newton release date",
    fact="BiggestMAMA was released in February 2026",
    category="Software",
    source="Official Records"
)
```

---

## Formal Guarantees

BiggestMAMA provides **6 formally verified theorems**:

| # | Theorem | Statement |
|---|---------|-----------|
| 1 | **Trust Lattice Well-Ordering** | `UNTRUSTED ⊑ VERIFIED ⊑ TRUSTED ⊑ KERNEL` with reflexivity, transitivity, antisymmetry |
| 2 | **Bounded Execution** | `∀ computation c: resources(c) ≤ B` where B = (10K iters, 100 depth, 1M ops, 30s) |
| 3 | **Provenance Chain Integrity** | `∀ i > 0: entry[i].prev_hash = entry[i-1].hash` |
| 4 | **Ollama Governance** | `∀ LLM responses r: trust(r) ⊑ VERIFIED` (never TRUSTED) |
| 5 | **API Contract Compliance** | All responses contain: value, trace, trust_label, bounds, ledger_proof |
| 6 | **Input Sanitization** | `∀ inputs i: sanitize(i) ∉ {$, \`, ;, |, &, <, >, \n, \r, \0}` |

Run the formal verification suite:

```bash
cd nina/tests
python test_nina_formal.py --proofs
```

---

## API Reference

### Classes

| Class | Purpose |
|-------|---------|
| `Pipeline` | 9-stage verified computation pipeline |
| `Regime` | Mode-dependent type/effect environment |
| `TrustLattice` | Information flow control |
| `TrustLabel` | Security labels (UNTRUSTED → KERNEL) |
| `DistortionMetric` | Language-action geometry checking |
| `NinaKnowledge` | Bridge to adan_portable KB |
| `NinaOllama` | Governed LLM fallback |

### Data Structures

| Structure | Purpose |
|-----------|---------|
| `PipelineResult` | `(value, trace, trust_label, bounds_report, ledger_proof)` |
| `ParsedQuery` | `(shape, slots, raw_input, confidence)` |
| `ProvenanceEntry` | `(index, timestamp, operation, hashes)` |
| `Labeled[T]` | Value with trust label attached |

### Functions

| Function | Purpose |
|----------|---------|
| `nina_query(q)` | Simple query interface |
| `nina_verify(s)` | Verify a statement |
| `nina_calculate(e)` | Calculate expression |
| `get_trust_lattice()` | Get global lattice |
| `get_regime_registry()` | Get all regimes |

---

## File Structure

```
BiggestMAMA.py
├── Section 1: Trust Lattice (IFC)
├── Section 2: Regime System
├── Section 3: Distortion Metric
├── Section 4: Ollama Integration
├── Section 5: Knowledge Bridge
├── Section 6: Pipeline Data Structures
├── Section 7: 9-Stage Pipeline (core)
├── Section 8: Convenience Functions
└── Section 9: CLI Demo
```

---

## Philosophy

> "The constraint IS the instruction.  
> The verification IS the computation.  
> The network IS the processor."

BiggestMAMA embodies the Newton philosophy:

1. **Verify, don't hope** - Every answer is verified before returned
2. **Trust is earned** - Labels must be upgraded through verification
3. **Audit everything** - Hash-chained provenance for every operation
4. **Bound everything** - All computation is bounded, guaranteed to terminate
5. **Language is geometry** - Words have shape, actions have physics, mismatches are errors

---

## License

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

---

## Credits

- **Author**: Jared Lewis
- **Organization**: Ada Computing Company, Houston, Texas
- **Date**: February 2026

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   "I don't pretend. I verify. I don't hope. I compute."                     ║
║                                                                              ║
║                                    - Newton                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
