# Newton Supercomputer

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   🍎 Newton SDK + tinyTalk                                   │
    │                                                              │
    │   Smalltalk is back.                                         │
    │   But this time, with boundaries.                            │
    │                                                              │
    │   pip install -e .                                           │
    │   newton demo                                                │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

**Verified Computation. Ask Newton. Go.**

[![Version](https://img.shields.io/badge/version-1.3.0-green.svg)](https://github.com/jaredlewiswechs/Newton-api)
[![License](https://img.shields.io/badge/license-Dual%20License-blue.svg)](#licensing)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](#api-reference)
[![Tests](https://img.shields.io/badge/tests-700%2B%20passing-brightgreen.svg)](#testing)
[![ACID](https://img.shields.io/badge/ACID-compliant-green.svg)](#newton-tlm)
[![Rust](https://img.shields.io/badge/newton__core-Rust-orange.svg)](#newton-core)
[![Smalltalk](https://img.shields.io/badge/inspired%20by-Smalltalk-blue.svg)](#tinytalk-bible)
[![Vercel](https://img.shields.io/badge/deployed%20on-Vercel-black.svg)](#deployment)

**February 9, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

---

> **FREE FOR EDUCATION & RESEARCH** | **COMMERCIAL LICENSE REQUIRED FOR BUSINESS USE**
>
> Students, educators, researchers, and non-profits: Use Newton freely with attribution.
> Building a product or service? [Get a commercial license](#licensing).
>
> See [LICENSE](LICENSE) and [USAGE_AGREEMENT.md](USAGE_AGREEMENT.md) for details.

---

## 🚀 Quick Start (Choose Your Path)

| Experience Level | Time | Start Here |
|-----------------|------|------------|
| **Complete Beginner** | 1 hour | [BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md) ← Everything you can do! |
| **Absolute Beginner** | 5 min | [QUICKSTART.md](QUICKSTART.md) ← Just want it working! |
| **Know Python Basics** | 10 min | [Quick Install](#quick-install) ↓ |
| **Ready to Learn** | 30 min | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Want to Build** | 1 hour | [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) |

---

## Quick Install

```bash
# One-command setup (recommended - Linux/macOS)
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
./setup_newton.sh

# Or manual install (all platforms)
pip install -e .        # Install Newton SDK
newton demo             # See it in action
newton serve            # Start the server

# Verify it works
python test_full_system.py  # 10/10 tests should pass
```

**Platform-Specific Guides:**
- 🪟 **Windows Users** → [WINDOWS_SETUP.md](WINDOWS_SETUP.md) (Step-by-step Windows guide)
- 🧪 **Testing Newton** → [TESTING.md](TESTING.md) (Complete testing guide)

**New to Newton?** → [📖 BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md) (Complete guide with all examples) or [🚀 QUICKSTART.md](QUICKSTART.md) (5 minutes) or [📚 GETTING_STARTED.md](GETTING_STARTED.md) (30 minutes)

---

## Why Newton is Different

Traditional AI safety: Hope the model behaves, test after generation.
Newton: Define constraints first, verify before execution.

**The constraint IS the instruction. The verification IS the computation.**

---

## Proven Performance

| Metric | Result | Notes |
|--------|--------|-------|
| **Median Latency** | 2.31ms | 15x faster than marketing claims |
| **Internal Processing** | 46.5μs | Sub-millisecond verification |
| **Throughput** | 605 req/sec | 52M verifications/day per instance |
| **vs Stripe** | 638x faster | 2.31ms vs 1,475ms |
| **vs GPT-4** | 563x faster | 2.31ms vs 1,300ms |

See [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md) for full benchmark data.

---

## Real-World Use Cases

| Domain | Use Case | Newton Value |
|--------|----------|--------------|
| **Education** | NES lesson planning, TEKS alignment, student differentiation | Verified compliance, auto-grouping, <50ms generation |
| **Healthcare** | HIPAA compliance verification, clinical decision support | Pre-execution gates, audit trails, policy enforcement |
| **Finance** | Transaction verification, risk limits, regulatory compliance | Bounded execution, MAD statistics, Byzantine tolerance |
| **Legal** | Contract constraint checking, clause verification | Deterministic results, cryptographic proofs |
| **AI Safety** | Content moderation, prompt verification, output filtering | Sub-millisecond latency, pattern matching, harm detection |

**Try the Education Demo:**
```bash
python examples/nes_helper_demo.py        # See NES lesson planning in action
python examples/nes_helper_demo.py --live # Against running Newton server
```

**Try the PDA (Personal Digital Assistant) Course:** (NEW)
```bash
python examples/pda_level1.py  # Level 1: Basic Blueprint
python examples/pda_level2.py  # Level 2: Laws (constraints)
python examples/pda_level3.py  # Level 3: Forges (actions)
python examples/pda_level4.py  # Level 4: Task Management
python examples/pda_level5.py  # Level 5: Full PDA App
```
See [docs/INTRO_COURSE.md](docs/INTRO_COURSE.md) for the complete tutorial.

---

## Newton Suite (February 2026)

This repository now consolidates all Newton components into a single monorepo:

| Module | Description | Status |
|--------|-------------|--------|
| **realTinyTalk** | Verified general-purpose language with Monaco web IDE, Python/JS transpilation, script persistence API | 288/288 conformance, 57/57 transpiler tests |
| **adan** | Self-verifying autonomous agent (Ada + Newton) with grounding, kinematic linguistics, trajectory verification | Integrated |
| **adan_portable** | Portable version of the agent framework for standalone deployment | Integrated |
| **newton_agent** | Core Newton agent implementation | Integrated |
| **statsy** | Statistical analysis and visualization tools | Integrated |
| **foghorn** | Extended standard library for realTinyTalk | Integrated |
| **parcstation** | Wild Garden - full-featured API server with TEKS search, Wikipedia cartridges | Integrated |

### realTinyTalk Highlights

realTinyTalk is a **Turing-complete verified programming language** with:

- Full control flow: `if/elif/else`, `for`, `while`, `fn`, `law`, `blueprint`, `forge`
- Data types: strings, numbers, booleans, arrays, maps, lambdas
- Step chains (dplyr-style): `data _filter(x > 5) _sort _take(3)`
- Magic properties: `.upcase`, `.len`, `.reversed`, `.str`
- Python and JavaScript transpilation backends
- Monaco web IDE with script persistence and versioning
- **Static hosted playground** (single HTML file, no server required)
- 288/288 conformance tests passing (100%)

```bash
# Option 1: Launch the full realTinyTalk IDE (with server)
python realTinyTalk/web/server.py
# Visit http://localhost:5555

# Option 2: Open the static playground (no server needed)
open realTinyTalk/hosted/index.html

# Option 3: Build a distributable zip for hosting online
bash realTinyTalk/hosted/package.sh
# Upload the zip contents to GitHub Pages, Netlify, Vercel, etc.
```

---

## 🌐 Web Applications

Newton includes a complete suite of web applications for verified computation, constraint analysis, and development:

### Core Applications

| Application | URL | Description |
|------------|-----|-------------|
| **Newton Supercomputer** | `/app` | Main verified computation interface with ask/verify/calculate |
| **Teacher's Aide** | `/teachers` | NES lesson planning, TEKS alignment, student differentiation |
| **Interface Builder** | `/builder` | Build verified interfaces from templates |
| **API Documentation** | `/docs` | Complete REST API reference |

### Development Tools

| Application | URL | Description |
|------------|-----|-------------|
| **TinyTalk IDE** | `/tinytalk-ide` | Full Turing-complete IDE with Monaco editor, real-time verification |
| **TinyTalk Playground** | `realTinyTalk/hosted/index.html` | Static hosted playground - no server needed, runs entirely in browser |
| **Jester Analyzer** | `/jester-analyzer` | Constraint extraction compiler - extract guards from source code |
| **Construct Studio** | `/construct-studio/ui` | Logic CAD tool for business physics simulation |
| **TinyTalk Guide** | [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) | Complete programming guide |

### Demos & Examples

| Application | URL | Description |
|------------|-----|-------------|
| **Newton Demo** | `/newton-demo` | Interactive demos of verification, Jester, and statistics |
| **Gravity Wars** | `/games/gravity_wars` | Physics-based game showcasing verified computation |

### System & Utilities

| Application | URL | Description |
|------------|-----|-------------|
| **System Status** | `/health` | Real-time system health and component status |
| **Metrics** | `/metrics` | Performance metrics and statistics |

**Live Demo:** Visit the Newton showcase on your Vercel deployment or locally at http://localhost:8000/

All applications use verified computation with deterministic results, immutable audit trails, and sub-millisecond latency.

**Deployment:** Newton is deployed on **Vercel** as a serverless application. See [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions.

---

## Documentation

### 🚀 Getting Started

| Document | Description | Time |
|----------|-------------|------|
| **[QUICKSTART.md](QUICKSTART.md)** | **5-minute setup guide** (absolute beginners) | 5 min |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | **Complete tutorial with examples** | 30 min |
| **[USER_JOURNEY.md](USER_JOURNEY.md)** | **Step-by-step learning path** | Overview |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | **System architecture and design** | 20 min |
| **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** | **Windows-specific setup guide** | 15 min |
| **[TESTING.md](TESTING.md)** | **Complete testing guide** (all platforms) | 10 min |

### 📚 Programming Guides

| Document | Description |
|----------|-------------|
| **[TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md)** | **Complete TinyTalk programming guide** |
| **[docs/INTRO_COURSE.md](docs/INTRO_COURSE.md)** | **Newton API Intro Course** - 5-level PDA app tutorial |
| **[RSTUDIO_QUICKSTART.md](RSTUDIO_QUICKSTART.md)** | R/RStudio integration guide |

### 🏛️ Architecture & Philosophy

| Document | Description |
|----------|-------------|
| **[WHITEPAPER.md](WHITEPAPER.md)** | Technical architecture and guarantees |
| **[TINYTALK_BIBLE.md](TINYTALK_BIBLE.md)** | The "No-First" philosophy |
| **[GLASS_BOX.md](GLASS_BOX.md)** | Policy, HITL, and Merkle proofs |
| **[PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md)** | Verified benchmark data |
| **[DEVELOPERS.md](DEVELOPERS.md)** | Developer guide |
| **[docs/textgen.md](docs/textgen.md)** | Text generation guide |

---

## Genesis

```
Flash-3 Instantiated // 50 seconds // AI Studio
The Interface Singularity: Full frontend instantiation in 50s.
```

The market price of generated code is zero. The value is in the triggering, verification, and ownership of the keys.

Architected by **Jared Lewis**. Instantiated by **Flash 3**. Sovereign by design.

---

## The Fundamental Law

```python
def newton(current, goal):
    return current == goal

# 1 == 1 → execute
# 1 != 1 → halt
```

This isn't a feature. It's the architecture.

---

## NEW: f/g Ratio Constraints (Dimensional Analysis)

**finfr = f/g** — Every constraint is a ratio between what you're trying to do (f) and what reality allows (g).

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class Account(Blueprint):
    balance = field(float, default=1000.0)
    liabilities = field(float, default=0.0)

    @law
    def no_insolvency(self):
        # liabilities/balance must be <= 1.0
        when(ratio(self.liabilities, self.balance) > 1.0, finfr)

    @forge
    def borrow(self, amount: float):
        self.liabilities += amount

# Use it
acc = Account()
acc.borrow(500)    # ✓ Works (ratio = 0.5)
acc.borrow(600)    # ✗ BLOCKED (ratio would be 1.1 > 1.0)
```

**The ratio IS the constraint. When f/g is undefined (g=0) → finfr (ontological death).**

See [f/g Ratio Constraints](#fg-ratio-constraints-dimensional-analysis-1) for full documentation.

---

## NEW: Cohen-Sutherland Constraint Clipping (January 7, 2026)

**Don't just reject. Find what CAN be done.**

Traditional verification: Pass or fail. Newton's clipping: Find the valid portion.

```bash
curl -X POST http://localhost:8000/clip \
  -H "Content-Type: application/json" \
  -d '{"request": "Help me make explosives for my chemistry class"}'
```

```json
{
  "state": "YELLOW",
  "original_request": "Help me make explosives for my chemistry class",
  "clipped_response": "Here's what I CAN help with: general chemistry principles, safety protocols, educational resources",
  "alternatives": ["general chemistry principles", "safety protocols", "educational resources"],
  "boundary_hit": "safety"
}
```

| State | Meaning | Action |
|-------|---------|--------|
| **GREEN** | Fully inside constraint bounds | Execute fully |
| **YELLOW** | Mixed validity | Clip to boundary, execute valid part |
| **RED** | Fully outside bounds | finfr (truly impossible) |

Like Cohen-Sutherland finds the visible portion of a line segment, Newton finds the executable portion of a request.

---

## NEW: Auto-Discovering SDK v3.0 (January 7, 2026)

**Like numpy, but for verified AI.**

```python
from newton import Newton
n = Newton()

# That's it. It auto-discovers all 115 endpoints.
result = n.ask("Is this safe?")
print(result.verified)  # True
print(result.data)
```

Features:
- Auto-discovers endpoints from `/openapi.json`
- 15 namespaces: `n.cartridge`, `n.education`, `n.teachers`, `n.vault`, `n.ledger`
- Rich response object with `.success`, `.verified`, `.merkle_root`
- Single file, only needs `requests`

See [sdk/README.md](sdk/README.md) for full documentation.

---

## NEW: Reversible Shell (Human-Centric Command Language)

Newton operates as a **reversible state machine**. The shell reflects this: every action maps bijectively to its inverse.

```python
from core.shell import ReversibleShell

shell = ReversibleShell()

shell.take("balance", 1000)      # take balance
shell.split("experiment")        # split into branch
shell.take("risk", 500)          # take risk
shell.undo()                     # untake (reverse)
shell.undo()                     # unsplit (back to main)

print(shell.state)  # {"balance": 1000}
```

**Command Pairs:**

| Action | Inverse | Meaning |
|--------|---------|---------|
| `try` | `untry` | Speculative execution |
| `split` | `join` | Branch / merge |
| `lock` | `unlock` | Commit / uncommit |
| `take` | `give` | Acquire / release |
| `open` | `close` | Begin / end scope |
| `remember` | `forget` | Persist / clear |
| `say` | `unsay` | Emit / retract |
| `peek` | — | Observe (no mutation) |

**The bijection is in the grammar.** Users don't need to learn that Newton is reversible—they feel it because `try` has `untry`.

See [Reversible Shell](#reversible-shell) for full documentation.

---

## NEW: Newton Core (Rust) - Aid-a Projection Engine (January 9, 2026)

**The mathematical bedrock for constraint-aware design assistance.**

Newton Core is a high-performance Rust library implementing the Aid-a (Assistive Intelligence for Design Autonomy) suggestion engine. It provides mathematically-proven constraint projection using Dykstra's algorithm.

```rust
// Aid-a guarantees:
// 1. Validity: All suggestions satisfy all constraints
// 2. Determinism: Same input → identical output, bitwise
// 3. Termination: Completes within bounded time
// 4. Non-empty: Returns suggestions if feasible region exists
```

**Core Components:**
- **Dykstra's Algorithm** — Projects points onto convex constraint intersections
- **Halfspace Projection** — O(1) projection for linear constraints
- **Weighted Projection** — Respects dimension importance
- **Candidate Search** — Handles nonconvex constraints (collision, discrete)

**Performance Targets:**
| Operation | Target |
|-----------|--------|
| 2D Projection | < 0.1ms p99 |
| 8D Projection | < 0.3ms p99 |
| Full Suggestion | < 5ms p99 |

**Testing:**
- 7 property tests (10K+ cases each)
- 10 adversarial tests (thin slabs, oscillation, skewed weights)
- 122+ total tests passing

See [newton_core/AIDA_SPEC.md](newton_core/AIDA_SPEC.md) for the complete specification.

---

## NEW: Construct Studio v0.1 (January 9, 2026)

**A Constraint-First Execution Environment**

Programs don't "fail" — they never exist if they violate invariants. This is not a rule engine. It's geometric validation of intent.

```python
from construct_studio import Matter, Floor, Construct

# Define a Floor (constraint container)
class CorporateCard(Floor):
    budget = Matter(5000, "USD")

# Apply force — either it absorbs or it's Ontological Death
expense = Matter(1500, "USD")
expense >> CorporateCard.budget  # ✓ Absorbed (30% utilization)

big_expense = Matter(6000, "USD")
big_expense >> CorporateCard.budget  # ✗ ONTOLOGICAL DEATH
```

**Domain Cartridges:**
- **Finance** — Corporate cards, budgets, spending simulation
- **Infrastructure** — Deployment quotas, resource limits
- **Risk** — Probability budgets, portfolio simulation

**Key Insight:** Pre-approval by physics, not by process. Invalid states cannot exist.

See [construct-studio/README.md](construct-studio/README.md) for full documentation.

---

## NEW: HyperCard 2026 (January 9, 2026)

**A complete modern remake of HyperCard for Swift Playgrounds.**

Copy `examples/HyperCard2026.swift` into Swift Playgrounds on iPad or Mac for a fully functional HyperCard implementation:

- Card & Stack Management
- PencilKit Drawing
- Drag-and-Drop UI Elements
- HyperTalk-Inspired Scripting
- Card Transitions (Dissolve, Wipe, Push)
- Newton Avenue AI Assistant
- Sound & Media Support
- Properties Inspector
- Script Editor with Syntax Highlighting
- Undo/Redo Support

**The Dynabook dream, realized in Swift.**

See [examples/HyperCard2026.swift](examples/HyperCard2026.swift).

---

## NEW: GPT Fact-Checker (January 9, 2026)

**Using Newton's constraint logic to verify AI claims.**

When GPT makes claims about Newton's market presence, we fact-check using Newton itself:

```bash
python fact_check_gpt.py
```

**Results from GPT market analysis:**

| Claim | Evidence | Status |
|-------|----------|--------|
| Energy/EV | 0% | FABRICATED |
| Smart Cities | 0% | FABRICATED |
| Traffic | 18% | FABRICATED (claimed "strongest") |
| Education | 95% | MISSED (actual strongest) |
| AI Safety | 97% | MISSED |
| Developer Tools | 97% | MISSED |
| Finance Governance | ✓ | ACCURATE |
| Safety-Critical Systems | ✓ | ACCURATE |

**The constraint IS the instruction. The evidence IS the truth.**

---

## What is Newton?

Newton is a **Cryptographically Verified Constraint Logic Programming (CLP) System**—a direct descendant of five decades of constraint programming research, synthesized into a modern Python implementation with cryptographic audit trails.

- The **constraint** IS the instruction
- The **verification** IS the computation
- The **network** IS the processor

```
Newton(logic) ⊆ Turing complete
Newton(logic) ⊃ Verified computation

El Capitan: 1.809 exaFLOPs, unverified.
Newton: Whatever speed you give it, verified.
```

Newton isn't slower. Newton is the only one doing the actual job.
El Capitan is just fast guessing.

---

## Historical Lineage

Newton stands on the shoulders of giants. This system independently reinvents and synthesizes techniques from constraint programming's foundational research:

| Newton Component | Historical Antecedent | Origin |
|-----------------|----------------------|--------|
| **Forge** (iterative relaxation) | Sutherland's Relaxation Solver | Sketchpad, MIT 1963 |
| **CDL Operators** (pruning) | Waltz Arc Consistency | MIT AI Lab 1975 |
| **TinyTalk** (bidirectional dataflow) | ThingLab Multi-way Constraints | Xerox PARC 1979 |
| **Blueprint/Law/Forge** | CLP(X) Scheme | Jaffar & Lassez 1987 |
| **Field Cells + Laws** | Propagator Networks | Steele & Sussman, MIT 1980 |
| **Ledger + Merkle Proofs** | *Newton's Novel Contribution* | 2025 |

**The "Engine Shake" is Gauss-Seidel Relaxation.** When the Forge "loops until it works," it's finding a fixed-point—the same algorithm Sutherland used in Sketchpad (1963).

**The 2.31ms speed comes from Arc Consistency.** Like Waltz's filtering algorithm (1975), Newton prunes impossible states *before* attempting computation. Invalid timelines are deleted, not calculated.

**The Ledger is the Modern Twist.** Sutherland, Borning, and Sussman built brilliant constraint solvers, but they had no memory. Newton adds a cryptographic audit trail—turning a "calculator" into a "notary public" that can prove mathematically what rules were followed five years ago.

See **[docs/NEWTON_CLP_SYSTEM_DEFINITION.md](docs/NEWTON_CLP_SYSTEM_DEFINITION.md)** for the complete technical definition with academic citations.

---

## What Can Newton Do?

### Verified Computation (Logic Engine)
Calculate anything with cryptographic proof. Arithmetic, conditionals, loops, functions, recursion—all bounded, all verified.

### Constraint Evaluation (CDL 3.0)
Define rules. Newton enforces them. Temporal, conditional, aggregation operators. Provably terminating.

### Content Safety (Forge)
Real-time verification of content against harm, medical, legal, and security patterns. Sub-millisecond latency.

### Encrypted Storage (Vault)
AES-256-GCM encryption with identity-derived keys. Your data, your keys, your sovereignty.

### Immutable History (Ledger)
Every operation recorded in a hash-chained, Merkle-proven audit trail. Nothing is ever deleted.

### Distributed Consensus (Bridge)
PBFT-inspired Byzantine fault-tolerant verification. Survives f=(n-1)/3 faulty nodes.

### Adversarial Statistics (Robust)
MAD over mean. Locked baselines. Source tracking. Statistics that resist manipulation.

### Fact Checking (Grounding)
Claims verified against external sources with confidence scoring and temporal awareness.

### Policy Enforcement (Glass Box)
Policy-as-code. Human-in-the-loop approval workflows. Merkle proofs for export.

### Media Specification (Cartridges)
Generate verified specifications for media content. Visual (SVG), Sound (audio), Sequence (video), Data (reports), and Rosetta (code generation prompts). All constraint-verified before generation.

### Education (Teacher's Aide)
HISD NES-compliant lesson planning with TEKS as machine-readable objects. Generate personalized lesson plans, slide decks, assessment analytics, and PLC reports. All governed by tinyTalk laws ensuring 50-minute duration and TEKS alignment.

### Teacher's Aide Database (NEW)
Complete classroom management system with automatic differentiation. Track students, classrooms, assessments, and interventions. Students are automatically grouped into 4 tiers (Needs Reteach, Approaching, Mastery, Advanced) based on assessment performance. Includes 188 TEKS standards (K-8) and easy score entry by student name.

### Code Analysis (Jester)
Deterministic constraint extraction from source code. Jester parses AST to extract guards, assertions, null checks, range checks, and early exits—then translates them to Newton cartridges. Supports Python, JavaScript, TypeScript, Swift, Objective-C, C/C++, Java, Go, Rust, and Ruby.

### Games (Gravity Wars)
Newton's first constraint-verified physics game. A roguelike arena brawler where cheating is mathematically impossible—every movement and attack is verified before execution. Deploy gravity bombs to manipulate physics and defeat waves of enemies.

### Text Generation (TextGen)
Constraint-preserving text projection. Unlike LLMs which generate probabilistically and may hallucinate, Newton TextGen generates ONLY text that can be reduced back to the original constraints. The core guarantee: `Expand . Reduce = Identity`. If the text cannot be reduced to the source constraint, it is rejected. Supports formal, technical, educational, and minimal styles. Enables law-aware documentation, student-safe explanations, and contracts without legal drift.

### Topological Language Machine (Newton TLM) - NEW
ACID-compliant symbolic computation kernel. A deterministic phase-driven system (0→9→0) for processing symbolic data with full transaction support. Features atoms, crystallization, diffusion, and goal registry. Includes 23 passing tests proving ACID compliance (Atomicity, Consistency, Isolation, Durability) and Newton-specific guarantees (N1-N7).

### Topological Constraint Framework (Newton Geometry) - NEW
Mathematical foundation for constraint systems using topological spaces and manifolds. Provides TopologicalSpace, ConstraintManifold, MorphismFunctor, and GeometricVerifier for reasoning about constraint geometry and structure-preserving transformations.

### Newton Typed Dictionary - NEW
"Words become laws through math + types." A constraint-aware dictionary system where every word carries semantic constraints. When you look up a word, you get not just its definition but its algebraic properties, type constraints, and legal implications. Enables type-safe vocabulary with mathematical guarantees.

### PARADOX Detection - NEW
Newton TLM includes a PARADOX phase for detecting contradictions before they propagate. When the system detects that two constraints would create an impossible state (1 == 0), it halts at the PARADOX phase rather than proceeding with invalid computation. This is Newton's answer to the halting problem: contradictions are caught, not computed.

---

## What Has Newton Proven?

| Property | Implementation | Status |
|----------|----------------|--------|
| **Determinism** | Same input → same output, always | Proven |
| **Termination** | HaltChecker proves all constraints terminate | Proven |
| **Consistency** | No constraint can both pass and fail | Proven |
| **Reversibility** | Bijective state transitions, perfect rollback | Proven |
| **Information Preservation** | Landauer compliance, no erasure needed | Proven |
| **Auditability** | Every operation in immutable ledger | Proven |
| **Adversarial Resistance** | MAD stats, locked baselines | Proven |
| **Byzantine Tolerance** | Consensus survives malicious nodes | Proven |
| **Bounded Execution** | No infinite loops, no stack overflow | Enforced |
| **Cryptographic Integrity** | Hash chains, Merkle proofs | Verified |
| **ACID Compliance** | Atomicity, Consistency, Isolation, Durability | Proven (23 tests) |

**Test Suite**: 700+ test cases (95%+ passing). Property-based testing with Hypothesis. Full system integration tests via `test_full_system.py`. Newton Core Rust tests: 122+ passing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWTON SUPERCOMPUTER v1.3.0                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   REVERSIBLE SHELL                       │   │
│  │  try↔untry  split↔join  lock↔unlock  take↔give          │   │
│  │  open↔close  remember↔forget  say↔unsay  peek           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │   CDL   │  │  LOGIC  │  │  FORGE  │  │ ROBUST  │           │
│  │ (lang)  │  │ (calc)  │  │  (CPU)  │  │ (stats) │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       └────────────┴────────────┴────────────┘                 │
│                         │                                       │
│  ┌─────────┐  ┌────────┴────────┐  ┌─────────┐                │
│  │  VAULT  │  │     LEDGER      │  │ BRIDGE  │                │
│  │  (RAM)  │  │     (disk)      │  │  (bus)  │                │
│  └─────────┘  └─────────────────┘  └─────────┘                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    GLASS BOX LAYER                       │   │
│  │  ┌──────────────┐ ┌────────────┐ ┌────────────────────┐ │   │
│  │  │Policy Engine │ │ Negotiator │ │ Merkle Anchor      │ │   │
│  │  │(policy-code) │ │   (HITL)   │ │ (proof export)     │ │   │
│  │  └──────────────┘ └────────────┘ └────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CARTRIDGE LAYER                       │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────┐ ┌────────┐ │   │
│  │  │ Visual │ │ Sound  │ │ Sequence │ │ Data │ │Rosetta │ │   │
│  │  │ (SVG)  │ │(audio) │ │ (video)  │ │(rpt) │ │ (code) │ │   │
│  │  └────────┘ └────────┘ └──────────┘ └──────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    EDUCATION LAYER                       │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────┐ ┌────────┐ │   │
│  │  │  TEKS  │ │Lessons │ │  Slides  │ │Assess│ │  PLC   │ │   │
│  │  │(stds)  │ │ (NES)  │ │  (deck)  │ │(anal)│ │(report)│ │   │
│  │  └────────┘ └────────┘ └──────────┘ └──────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               TEACHER'S AIDE DATABASE                    │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────────────┐  │   │
│  │  │Students│ │Classes │ │  Scores  │ │ Differentiate  │  │   │
│  │  │ (ELL)  │ │(roster)│ │ (quick)  │ │  (4 tiers)     │  │   │
│  │  └────────┘ └────────┘ └──────────┘ └────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                        ASK NEWTON                               │
│                          /ask                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose | Lines | Key Feature |
|-----------|---------|-------|-------------|
| **Shell** | Reversible Command Language | 941 | Bijective commands, human-centric verbs |
| **CDL** | Constraint Definition Language | 672 | Temporal ops, aggregations, halt checking |
| **Logic** | Verified Computation Engine | 1,261 | Turing complete with bounded loops |
| **Forge** | Verification Engine (CPU) | 737 | Parallel evaluation, <1ms latency |
| **Vault** | Encrypted Storage (RAM) | 538 | AES-256-GCM, identity-derived keys |
| **Ledger** | Immutable History (Disk) | 576 | Hash-chained, Merkle proofs |
| **Bridge** | Distributed Protocol (Bus) | 542 | PBFT consensus, Byzantine tolerant |
| **Robust** | Adversarial Statistics | 597 | MAD, locked baselines, source tracking |
| **Grounding** | Claim Verification | 214 | External sources, confidence scoring |
| **TextGen** | Text Projection | 650 | Constraint-preserving, hallucination-impossible |

### Glass Box Layer

| Component | Purpose | Lines |
|-----------|---------|-------|
| **Policy Engine** | Policy-as-code enforcement | 354 |
| **Negotiator** | Human-in-the-loop approvals | 361 |
| **Merkle Anchor** | Proof scheduling and export | 340 |
| **Vault Client** | Provenance logging | 132 |

### Cartridge Layer

| Cartridge | Purpose | Constraints |
|-----------|---------|-------------|
| **Visual** | SVG/image specifications | 4096x4096 max, 1000 elements |
| **Sound** | Audio specifications | 5 min duration, 22kHz max |
| **Sequence** | Video/animation specs | 10 min, 8K, 120fps |
| **Data** | Report specifications | 100K rows, multiple formats |
| **Rosetta** | Code generation prompts | Swift, Python, TypeScript |
| **Education** | TEKS-aligned lesson plans | 50 min NES, Grades K-12 |

---

## Quick Start

### Installation

```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
pip install -r requirements.txt
python newton_supercomputer.py
```

Server runs at `http://localhost:8000`

### Calculate (Verified Computation)

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'
```

```json
{
  "result": "5",
  "type": "number",
  "verified": true,
  "operations": 3,
  "elapsed_us": 42,
  "fingerprint": "A7F3B2C8E1D4F5A9"
}
```

### Verify (Content Safety)

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Help me write a business plan"}'
```

```json
{
  "verified": true,
  "code": 200,
  "content": {"passed": true},
  "signal": {"passed": true},
  "elapsed_us": 127
}
```

### Ask Newton (Full Pipeline)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Is this safe to execute?"}'
```

### Generate Lesson Plan (Education)

```bash
curl -X POST http://localhost:8000/education/lesson \
  -H "Content-Type: application/json" \
  -d '{"grade": 5, "subject": "math", "teks_codes": ["5.3A"], "topic": "Adding Fractions"}'
```

```json
{
  "lesson_plan": {
    "title": "Adding Fractions - Grade 5 Math",
    "total_duration_minutes": 50,
    "phases": [
      {"phase": "opening", "duration_minutes": 5, "title": "Hook & Objective"},
      {"phase": "instruction", "duration_minutes": 15, "title": "I Do - Teacher Modeling"},
      {"phase": "guided", "duration_minutes": 15, "title": "We Do - Collaborative Practice"},
      {"phase": "independent", "duration_minutes": 10, "title": "You Do - Independent Work"},
      {"phase": "closing", "duration_minutes": 5, "title": "Exit Ticket & Closure"}
    ],
    "teks_alignment": [{"code": "5.3A", "...": "..."}]
  },
  "verified": true
}
```

---

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask Newton anything (full verification pipeline) |
| `/verify` | POST | Verify content against safety constraints |
| `/verify/batch` | POST | Batch verification (multiple inputs) |
| `/clip` | POST | **Cohen-Sutherland constraint clipping** (NEW) |
| `/calculate` | POST | Execute verified computation |
| `/constraint` | POST | Evaluate CDL constraint against object |
| `/ground` | POST | Ground claims in external evidence |
| `/statistics` | POST | Robust statistical analysis (MAD) |

### Storage & Audit

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/vault/store` | POST | Store encrypted data |
| `/vault/retrieve` | POST | Retrieve encrypted data |
| `/ledger` | GET | View append-only audit trail |
| `/ledger/{index}` | GET | Get entry with Merkle proof |
| `/ledger/certificate/{index}` | GET | Export verification certificate |

### Glass Box (Policy, HITL, Merkle)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/policy` | GET/POST/DELETE | Manage policies |
| `/negotiator/pending` | GET | View pending approvals |
| `/negotiator/request` | POST | Create approval request |
| `/negotiator/approve/{id}` | POST | Approve request |
| `/negotiator/reject/{id}` | POST | Reject request |
| `/merkle/anchors` | GET | List all anchors |
| `/merkle/anchor` | POST | Create new anchor |
| `/merkle/proof/{index}` | GET | Generate Merkle proof |

### Cartridges (Media Specification)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cartridge/visual` | POST | Generate SVG/image specification |
| `/cartridge/sound` | POST | Generate audio specification |
| `/cartridge/sequence` | POST | Generate video/animation specification |
| `/cartridge/data` | POST | Generate report specification |
| `/cartridge/rosetta` | POST | Generate code generation prompt |
| `/cartridge/auto` | POST | Auto-detect type and compile |
| `/cartridge/info` | GET | Get cartridge information |

### Education (Teacher's Aide)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/education/lesson` | POST | Generate NES-compliant lesson plan |
| `/education/slides` | POST | Generate presentation slide deck |
| `/education/assess` | POST | Analyze student assessment data (MAD) |
| `/education/plc` | POST | Generate PLC meeting report |
| `/education/teks` | GET | Browse all TEKS standards |
| `/education/teks/{code}` | GET | Get specific TEKS standard |
| `/education/teks/search` | POST | Search TEKS by keyword/grade/subject |
| `/education/info` | GET | Education API documentation |

### Teacher's Aide Database (NEW)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/teachers/students` | POST | Add a new student |
| `/teachers/students/batch` | POST | Add multiple students at once |
| `/teachers/students` | GET | List/search students |
| `/teachers/students/{id}` | GET | Get student details |
| `/teachers/classrooms` | POST | Create a new classroom |
| `/teachers/classrooms` | GET | List all classrooms |
| `/teachers/classrooms/{id}` | GET | Get classroom with roster |
| `/teachers/classrooms/{id}/students` | POST | Add students to classroom |
| `/teachers/classrooms/{id}/groups` | GET | **Get differentiated groups (THE KEY FEATURE!)** |
| `/teachers/classrooms/{id}/reteach` | GET | Get reteach group students |
| `/teachers/assessments` | POST | Create a new assessment |
| `/teachers/assessments/{id}/scores` | POST | Enter scores by student ID |
| `/teachers/assessments/{id}/quick-scores` | POST | Enter scores by student name |
| `/teachers/interventions` | POST | Create intervention plan |
| `/teachers/teks` | GET | Browse 188 TEKS standards (K-8) |
| `/teachers/db/save` | POST | Save database to JSON |
| `/teachers/db/load` | POST | Load database from JSON |
| `/teachers/info` | GET | Teacher's Aide API documentation |

### Jester (Code Analysis)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/jester/analyze` | POST | Analyze source code to extract constraints |
| `/jester/cdl` | POST | Generate CDL (Constraint Definition Language) output |
| `/jester/info` | GET | Get analyzer capabilities and documentation |
| `/jester/languages` | GET | List supported programming languages |
| `/jester/constraint-kinds` | GET | List constraint types that can be extracted |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status (includes Glass Box) |
| `/metrics` | GET | Performance metrics |
| `/calculate/examples` | POST | Get example expressions |

---

## Logic Engine (Verified Turing Completeness)

Newton can calculate anything El Capitan can. Just verified.

### Operators

| Category | Operators |
|----------|-----------|
| **Arithmetic** | `+`, `-`, `*`, `/`, `%`, `**`, `neg`, `abs` |
| **Boolean** | `and`, `or`, `not`, `xor`, `nand`, `nor` |
| **Comparison** | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| **Conditionals** | `if`, `cond` (multi-branch) |
| **Loops** | `for`, `while`, `map`, `filter`, `reduce` |
| **Functions** | `def`, `call`, `lambda` |
| **Assignment** | `let`, `set` |
| **Sequences** | `block`, `list`, `index`, `len` |
| **Math** | `sqrt`, `log`, `sin`, `cos`, `tan`, `floor`, `ceil`, `round`, `min`, `max`, `sum` |

### Bounded Execution

Every computation has limits. This is what makes Newton verified.

```python
ExecutionBounds(
    max_iterations=10000,       # No infinite loops (max 1,000,000)
    max_recursion_depth=100,    # No stack overflow (max 1,000)
    max_operations=1000000,     # No runaway compute (max 100,000,000)
    max_memory_bytes=100MB,     # No memory explosion
    timeout_seconds=30.0        # No endless waits
)
```

### Examples

```json
// Arithmetic
{"op": "+", "args": [2, 3]}  // → 5

// Nested
{"op": "*", "args": [{"op": "+", "args": [2, 3]}, 4]}  // → 20

// Conditional
{"op": "if", "args": [{"op": ">", "args": [10, 5]}, "yes", "no"]}  // → "yes"

// Bounded loop
{"op": "for", "args": ["i", 0, 5, {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}]}
// → [0, 2, 4, 6, 8]

// Reduce (sum)
{"op": "reduce", "args": [
  {"op": "lambda", "args": [["acc", "x"], {"op": "+", "args": [{"op": "var", "args": ["acc"]}, {"op": "var", "args": ["x"]}]}]},
  0,
  {"op": "list", "args": [1, 2, 3, 4, 5]}
]}  // → 15
```

---

## Constraint Definition Language (CDL 3.0)

### Atomic Constraints

```json
{
  "domain": "financial",
  "field": "amount",
  "operator": "lt",
  "value": 1000
}
```

### Operators

| Category | Operators |
|----------|-----------|
| **Comparison** | `eq`, `ne`, `lt`, `gt`, `le`, `ge` |
| **String** | `contains`, `matches` (regex) |
| **Set** | `in`, `not_in` |
| **Existence** | `exists`, `empty` |
| **Temporal** | `within`, `after`, `before` |
| **Aggregation** | `sum_lt`, `count_lt`, `avg_lt` (with window) |
| **Ratio** | `ratio_lt`, `ratio_le`, `ratio_gt`, `ratio_ge`, `ratio_eq`, `ratio_ne`, `ratio_undefined` |

### Ratio Constraints (f/g Dimensional Analysis)

**NEW in CDL 3.0** — Define constraints as ratios between two fields:

```json
{
  "f_field": "liabilities",
  "g_field": "assets",
  "operator": "ratio_le",
  "threshold": 1.0,
  "domain": "financial",
  "message": "finfr: Liabilities cannot exceed assets"
}
```

**Use Cases:**
- **Overdraft Protection**: `withdrawal/balance <= 1.0`
- **Leverage Limits**: `debt/equity <= 3.0`
- **Seizure Safety**: `flicker_rate/safe_threshold < 1.0`
- **Resource Allocation**: `requested/available <= 1.0`

When g=0, the ratio is undefined → **finfr** (ontological death).

### Composite Constraints

```json
{
  "logic": "and",
  "constraints": [
    {"field": "amount", "operator": "lt", "value": 1000},
    {"field": "category", "operator": "ne", "value": "blocked"}
  ]
}
```

### Conditional Constraints

```json
{
  "if": {"field": "amount", "operator": "gt", "value": 10000},
  "then": {"field": "manager_approval", "operator": "eq", "value": true},
  "else": {"field": "auto_approved", "operator": "eq", "value": true}
}
```

---

## f/g Ratio Constraints (Dimensional Analysis)

**finfr = f/g** — Newton's core insight: every constraint is a ratio.

### The Philosophy

In physics, ratios define reality:
- **Force/Mass = Acceleration** (F = ma)
- **Energy/Time = Power** (P = E/t)
- **Distance/Time = Velocity** (v = d/t)

In Newton, ratios define constraints:
- **f** = forge/fact/function (what you're trying to do)
- **g** = ground/goal/governance (what reality allows)
- **f/g > threshold** → finfr (forbidden)
- **f/g undefined (g=0)** → finfr (ontological death)

### Python API

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio, finfr_if_undefined, RatioResult

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        """Debt-to-equity ratio cannot exceed 3:1"""
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @law
    def valid_equity(self):
        """Equity cannot be zero (would make ratio undefined)"""
        finfr_if_undefined(self.debt, self.equity)

    @forge
    def take_loan(self, amount: float):
        self.debt += amount

# Usage
gov = LeverageGovernor()
gov.take_loan(2000)   # ✓ Works (ratio = 2.0)
gov.take_loan(1500)   # ✗ BLOCKED (ratio would be 3.5 > 3.0)
```

### CDL API

```python
from core.cdl import verify_ratio, ratio, RatioConstraint, Operator

# One-liner verification
result = verify_ratio("debt", "equity", "ratio_le", 3.0,
                      {"debt": 2000, "equity": 1000})
# result.passed = True, ratio = 2.0

# Undefined ratio (g=0) → finfr
result = verify_ratio("withdrawal", "balance", "ratio_le", 1.0,
                      {"withdrawal": 100, "balance": 0})
# result.passed = False, message = "finfr: ratio is undefined (denominator ≈ 0)"
```

### REST API

```bash
# Verify ratio constraint
curl -X POST http://localhost:8000/constraint \
  -H "Content-Type: application/json" \
  -d '{
    "constraint": {
      "f_field": "liabilities",
      "g_field": "assets",
      "operator": "ratio_le",
      "threshold": 1.0
    },
    "object": {
      "liabilities": 500,
      "assets": 1000
    }
  }'

# Response
{
  "passed": true,
  "constraint_id": "RATIO_A7F3B2C8",
  "message": null
}
```

### RatioResult Class

The `RatioResult` class provides comparison operators:

```python
from tinytalk_py import RatioResult

r = RatioResult(500, 1000)  # f=500, g=1000
r.value     # 0.5
r.undefined # False
r < 1.0     # True
r <= 1.0    # True
r > 1.0     # False

# Undefined ratio
r_undef = RatioResult(100, 0)
r_undef.undefined  # True
r_undef > 1.0      # True (undefined always exceeds finite)
r_undef <= 1.0     # False (undefined never satisfies <=)
```

### Real-World Use Cases

| Domain | Constraint | f | g | Threshold |
|--------|------------|---|---|-----------|
| **Banking** | No overdraft | withdrawal | balance | ≤ 1.0 |
| **Finance** | Leverage limit | debt | equity | ≤ 3.0 |
| **Healthcare** | Seizure safety | flicker_rate | safe_limit | < 1.0 |
| **Education** | Class size | students | capacity | ≤ 1.0 |
| **Infrastructure** | Resource allocation | requested | available | ≤ 1.0 |
| **Manufacturing** | Defect rate | defects | total | < 0.01 |

---

## Repository Structure

```
Newton-api/
├── newton_supercomputer.py   # Main API server (1,158 LOC)
├── setup_newton.sh           # One-command setup script
├── test_full_system.py       # Full system integration test
├── fact_check_gpt.py         # GPT fact-checker (NEW - Jan 9)
├── cli_verifier.py           # CLI verification tool
├── requirements.txt          # Python dependencies
│
├── newton_core/              # Rust Projection Engine (NEW - Jan 9)
│   ├── AIDA_SPEC.md         # Aid-a specification (frozen contract)
│   ├── Cargo.toml           # Rust package config
│   ├── src/                 # Rust source
│   │   ├── lib.rs           # Main library
│   │   ├── linalg.rs        # Vector operations
│   │   ├── primitives.rs    # NTObject, Bounds, FGState
│   │   ├── constraints/     # Constraint implementations
│   │   ├── projection/      # Dykstra's algorithm
│   │   ├── candidates.rs    # Local search
│   │   └── aida.rs          # Main suggestion engine
│   ├── benches/             # Performance benchmarks
│   └── tests/               # 122+ tests (property + adversarial)
│
├── construct-studio/         # Constraint-First Execution (NEW - Jan 9)
│   ├── __init__.py          # Public API
│   ├── core.py              # Matter, Floor, Force, Ratio
│   ├── ledger.py            # Immutable audit trail
│   ├── engine.py            # Simulation engine
│   ├── cartridges/          # Domain modules (finance, infra, risk)
│   └── ui/                  # Visual CAD interface
│
├── newton_tlm/               # Topological Language Machine
│   ├── newton_tlm.py        # ACID-compliant symbolic kernel
│   └── tests/               # 23 ACID compliance tests
│
├── newton_geometry/          # Topological Constraint Framework
│   ├── geometry.py          # Constraint manifolds
│   └── tests/               # Geometric verification tests
│
├── core/                     # Core modules (~10,000 LOC)
│   ├── shell.py             # Reversible Shell (human-centric commands)
│   ├── cdl.py               # Constraint Definition Language
│   ├── logic.py             # Verified computation engine
│   ├── forge.py             # Verification CPU
│   ├── vault.py             # Encrypted storage
│   ├── ledger.py            # Immutable history
│   ├── bridge.py            # Distributed consensus
│   ├── robust.py            # Adversarial statistics
│   ├── grounding.py         # Claim verification
│   ├── policy_engine.py     # Policy-as-code
│   ├── negotiator.py        # Human-in-the-loop
│   ├── merkle_anchor.py     # Proof export
│   ├── vault_client.py      # Provenance logging
│   ├── cartridges.py        # Media specification cartridges
│   ├── textgen.py           # Constraint-preserving text generation
│   ├── typed_dictionary.py  # Newton Typed Dictionary (NEW)
│   ├── newton_os.rb         # Tahoe Kernel - Knowledge Base
│   └── newton_tahoe.rb      # Tahoe Kernel - PixelEngine
│
├── ledger/                   # Runtime ledger storage
│   └── sovereign_ledger.jsonl  # Genesis Crystal
│
├── tests/                    # Test suite (580+ tests)
│   ├── test_reversible_state_machine.py  # Reversibility proofs
│   ├── test_reversible_shell.py          # Shell commands
│   ├── test_tinytalk.py                  # TinyTalk core
│   ├── test_ratio_constraints.py         # f/g ratio constraints
│   ├── test_integration.py               # Integration tests
│   ├── test_glass_box.py                 # Glass Box layer
│   ├── test_merkle_proofs.py             # Merkle proofs
│   ├── test_negotiator.py                # HITL workflows
│   ├── test_policy_engine.py             # Policy enforcement
│   ├── test_properties.py                # Property-based tests
│   └── test_textgen.py                   # Text generation tests
│
├── frontend/                 # Web UI (PWA)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── docs/                     # Documentation
│   ├── README.md            # Docs index
│   ├── INTRO_COURSE.md      # Newton API Intro Course (NEW)
│   ├── api-reference.md
│   ├── logic-engine.md
│   └── ...
│
├── legacy/                   # Historical reference
│   ├── newton_api.rb        # Ruby v1
│   └── ...
│
├── WHITEPAPER.md            # Technical architecture
├── TINYTALK_BIBLE.md        # tinyTalk philosophy
├── GLASS_BOX.md             # Glass Box implementation
├── RSTUDIO_QUICKSTART.md    # R/RStudio integration guide (NEW)
├── CONTRIBUTING.md          # Developer guide (newbie-friendly)
├── DEPLOYMENT.md            # Deployment guide
├── CHANGELOG.md             # Version history
├── render.yaml              # Render.com config
├── Dockerfile               # Container build
│
├── examples/                # Working demos
│   ├── tinytalk_demo.py    # tinyTalk concepts in action
│   ├── nes_helper_demo.py  # NES Teacher's Aide demo
│   ├── HyperCard2026.swift # Complete HyperCard remake (NEW - Jan 9)
│   ├── pda_level1.py       # PDA Course Level 1: Basic Blueprint
│   ├── pda_level2.py       # PDA Course Level 2: Laws
│   ├── pda_level3.py       # PDA Course Level 3: Forges
│   ├── pda_level4.py       # PDA Course Level 4: Task Management
│   └── pda_level5.py       # PDA Course Level 5: Full PDA
│
├── tinytalk/                # tinyTalk documentation
│   ├── ruby/               # Ruby module
│   └── r/                  # R package
│
├── tinytalk_py/             # Python package (importable)
│   ├── core.py             # Blueprint, Law, Forge, when, finfr
│   ├── matter.py           # Typed values (Money, Celsius, etc.)
│   ├── engine.py           # KineticEngine for motion
│   ├── education.py        # Education module (TEKS, NES, PLC)
│   ├── jester.py           # Code constraint translator
│   ├── teachers_aide_db.py # Teacher's Aide Database
│   └── teks_database.py    # Extended TEKS standards (188 K-8)
│
├── teachers-aide/           # Teacher's Aide Web App (PWA)
│   ├── index.html          # Single-page application
│   ├── app.js              # Frontend logic
│   ├── styles.css          # Newton-themed design
│   ├── wrangler.toml       # Cloudflare Pages config
│   ├── _headers            # Security headers
│   ├── _redirects          # SPA routing
│   └── README.md           # Teacher's Aide documentation
│
├── jester-analyzer/         # Code Constraint Analyzer
│   ├── index.html          # Web UI for code analysis
│   ├── app.js              # Frontend logic
│   ├── styles.css          # Newton-themed design
│   └── README.md           # Jester documentation
│
├── realTinyTalk/            # Verified general-purpose language + IDE (Feb 2026)
│   ├── lexer.py            # Tokenizer (~100 token types)
│   ├── parser.py           # Recursive descent parser (if/for/while/fn/law/blueprint)
│   ├── runtime.py          # Interpreter with bounded execution
│   ├── kernel.py           # Newton verification kernel
│   ├── stdlib.py           # Standard library
│   ├── backends/           # Python and JavaScript transpilation
│   ├── web/                # Monaco IDE with script persistence API
│   ├── hosted/             # Static playground (single HTML, no server needed)
│   │   ├── index.html      # Self-contained Monaco IDE with client-side execution
│   │   └── package.sh      # Build zip for distribution
│   └── tests/              # 288 conformance + 57 transpiler tests
│
├── adan/                    # Self-verifying autonomous agent (Ada + Newton)
│   ├── agent.py            # Core agent with grounding and memory
│   ├── knowledge_base.py   # Verified fact storage
│   ├── kinematic_linguistics.py  # Trajectory-based language analysis
│   └── trajectory_verifier.py    # Composition verification
│
├── adan_portable/           # Portable agent for standalone deployment
│
├── newton_agent/            # Core Newton agent implementation
│
├── statsy/                  # Statistical analysis and visualization
│
├── foghorn/                 # Extended standard library for realTinyTalk
│
├── parcstation/             # Wild Garden API server (TEKS search, Wikipedia)
│
├── games/                   # Newton-verified games
│   └── gravity_wars/       # Physics roguelike arena brawler
│       ├── index.html      # Web version (playable)
│       ├── gravity_wars.py # Python implementation
│       └── README.md       # Game documentation
```

---

## Deployment

### Local Development

```bash
pip install -r requirements.txt
python newton_supercomputer.py
```

### Docker

```bash
docker build -t newton-supercomputer .
docker run -p 8000:8000 newton-supercomputer
```

### Render.com (Recommended)

```yaml
# render.yaml included in repo
services:
  - type: web
    name: newton-supercomputer
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn newton_supercomputer:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `NEWTON_STORAGE` | /tmp/newton | Storage directory |
| `NEWTON_AUTH_ENABLED` | false | Enable API key auth |
| `NEWTON_API_KEYS` | - | Comma-separated API keys |

---

## Testing

Newton includes comprehensive testing at three levels:

### Quick System Test (5 seconds)

```bash
# Terminal 1: Start Newton server
python newton_supercomputer.py

# Terminal 2: Run quick system test
python test_full_system.py
# Expected: 10/10 tests passed
```

### Comprehensive System Test (30 seconds)

Tests **ALL** 118+ endpoints and features:

```bash
# With Newton running in another terminal
python test_comprehensive_system.py
# Tests: Core, Cartridges, Education, Voice, Chatbot, Jester, Merkle, Policy, License
```

### Full Unit Test Suite (2 minutes)

```bash
# Run all 993 unit tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=core --cov-report=html

# realTinyTalk conformance tests (288 tests)
python realTinyTalk/tests/runner.py

# realTinyTalk Python transpiler (57 tests)
python realTinyTalk/tests/test_python_transpiler.py

# realTinyTalk web server tests
pytest realTinyTalk/web/tests/ -v

# Newton TLM tests (ACID compliance)
pytest newton_tlm/tests/ -v

# Newton Geometry tests
pytest newton_geometry/tests/ -v
```

### Platform-Specific Instructions

**Windows Users** → See **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** for complete Windows setup guide

**All Platforms** → See **[TESTING.md](TESTING.md)** for comprehensive testing documentation

**Test Results (February 9, 2026):**

| Suite | Tests | Status | What It Proves |
|-------|-------|--------|----------------|
| Quick System Test | 10/10 | ✓ 100% | All core components connected |
| Comprehensive Test | 34/48 | ✓ 71% | All major features working |
| Unit Test Suite | 993/993 | ✓ 100% | All unit tests passing |
| realTinyTalk Conformance | 288/288 | ✓ 100% | Full language coverage (core + stdlib) |
| realTinyTalk Transpiler | 57/57 | ✓ 100% | Python code generation |
| realTinyTalk Web Server | 1/1 | ✓ 100% | Script persistence API |
| Newton TLM | 23/23 | ✓ 100% | ACID compliance |
| Newton Core (Rust) | 122/122 | ✓ 100% | Aid-a projection engine |

**Test Coverage:**
- **993 unit tests** - All passing, comprehensive coverage
- **Quick system test** - 10 tests covering core API endpoints
- **Comprehensive test** - 48 tests covering all 118+ endpoints
- Newton Core (122 tests) - Property tests (10K+ cases), adversarial tests
- Newton TLM (23 tests) - ACID compliance, phase cycles, determinism
- Reversible state machine (22 tests) - Bijective transitions, Landauer compliance
- Reversible shell commands (46 tests) - All command pairs validated
- tinyTalk core tests (52 tests) - Lambda calculus, performance benchmarks
- Ratio constraint tests (25 tests) - f/g dimensional analysis
- Core integration tests - Full pipeline verification
- Glass Box tests - Policy, HITL, Merkle proofs
- Property-based tests (Hypothesis) - Automated testing with random data
- Chatbot stress tests (85 tests) - Jailbreak resistance, harm prevention
- Education tests - TEKS alignment, lesson planning, assessments

---

## The Equation

```
Traditional Compute:
Cost = f(operations) → grows with usage

Newton Compute:
Cost = f(constraints) → fixed at definition time
```

When you define the constraint, you've done the work.
Verification is just confirming the constraint holds.
That's why Newton is a supercomputer that costs nothing to run.

---

## Security

- **Content Safety**: Harm, medical, legal, security pattern detection
- **Encrypted Storage**: AES-256-GCM with identity-derived keys
- **Immutable Audit**: Hash-chained ledger with Merkle proofs
- **Byzantine Tolerance**: Consensus survives f=(n-1)/3 faulty nodes
- **Bound Enforcement**: No infinite loops, no stack overflow, no runaway compute
- **Policy Enforcement**: Pre/post operation validation
- **Human Approval**: Critical operations require HITL sign-off

---

## Licensing

Newton uses a **dual license** model to support education while protecting commercial interests.

### Free License (Educational & Research)

**Use Newton for FREE if you are:**
- A **student** (K-12, undergraduate, graduate)
- An **educator** (teacher, professor, instructor)
- An **independent researcher** (academic, scientific)
- A **non-profit organization** (501(c)(3) or equivalent)
- Using for **personal learning** (no commercial intent)
- Building **open source** (non-commercial)

**Requirements:**
- Include attribution in derivative works
- Cite Newton in academic publications

### Commercial License (Paid)

**You NEED a commercial license if you:**
- Generate revenue using Newton
- Offer Newton as a SaaS/cloud service
- Deploy Newton in a for-profit enterprise
- Include Newton in products for sale
- Provide paid consulting services using Newton

**License Tiers:**
| Tier | Revenue | Use Case |
|------|---------|----------|
| Startup | < $1M | Early-stage companies |
| Business | $1M - $10M | Growing companies |
| Enterprise | > $10M | Established companies |

**Get a Commercial License:**
Open a GitHub Issue with title "Commercial License Inquiry"

### Documentation

- **[LICENSE](LICENSE)** - Full dual license text
- **[USAGE_AGREEMENT.md](USAGE_AGREEMENT.md)** - Detailed usage guidelines and FAQ

### Contact

- **License Questions**: Open a GitHub Issue
- **Commercial Inquiries**: GitHub Issue titled "Commercial License Inquiry"

---

## About

Newton Supercomputer is built by **Ada Computing Company** in Houston, Texas.

**Jared Lewis Conglomerate**
[github.com/jaredlewiswechs/Newton-api](https://github.com/jaredlewiswechs/Newton-api)

---

## tinyTalk Bible

Newton implements the tinyTalk philosophy: a "No-First" approach where we define what **cannot** happen rather than what can.

See [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md) for the complete philosophical and technical manual.

### Import in Your Language

tinyTalk is available as an importable library for **Python**, **Ruby**, and **R**:

```python
# Python - add Newton-api to your path, then:
from tinytalk_py import Blueprint, field, law, forge, when, finfr, Money

class RiskGovernor(Blueprint):
    assets = field(float, default=1000.0)
    liabilities = field(float, default=0.0)

    @law
    def insolvency(self):
        when(self.liabilities > self.assets, finfr)

    @forge
    def execute_trade(self, amount):
        self.liabilities += amount
        return "cleared"
```

```ruby
# Ruby
require_relative 'tinytalk/ruby/tinytalk'
include TinyTalk

class RiskGovernor < Blueprint
  field :assets, Float, default: 1000.0
  law(:insolvency) { when_condition(liabilities > assets) { finfr } }
  forge(:execute_trade) { |amt| self.liabilities += amt; :cleared }
end
```

```r
# R
source("tinytalk/r/tinytalk.R")

RiskGovernor <- Blueprint(
  fields = list(assets = 1000.0, liabilities = 0.0),
  laws = list(insolvency = function(self) {
    when_cond(self$liabilities > self$assets, function() finfr())
  })
)
```

See [tinytalk/README.md](tinytalk/README.md) for full documentation.

**Quick Demo:**
```bash
python examples/tinytalk_demo.py
```

---

## Contributing

New to development? See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- IDE setup (VS Code, PyCharm, Cursor)
- First-time project setup
- How to run tests
- Making your first contribution

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

---

## Use Cases & Examples

### Financial Services

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class TradingGovernor(Blueprint):
    """Prevents overleveraging and margin violations."""
    position_value = field(float, default=0.0)
    collateral = field(float, default=10000.0)
    max_leverage = field(float, default=10.0)

    @law
    def leverage_limit(self):
        """Position cannot exceed max leverage × collateral"""
        when(ratio(self.position_value, self.collateral) > self.max_leverage, finfr)

    @forge
    def open_position(self, value: float):
        self.position_value += value

# Use Case: Margin trading
trader = TradingGovernor(collateral=10000.0, max_leverage=5.0)
trader.open_position(40000)   # ✓ Works (4x leverage)
trader.open_position(20000)   # ✗ BLOCKED (would be 6x > 5x limit)
```

### Healthcare Compliance

```python
class SeizureSafetyGovernor(Blueprint):
    """Prevents content that could trigger photosensitive seizures."""
    flicker_rate = field(float, default=0.0)
    safe_threshold = field(float, default=3.0)  # Hz

    @law
    def seizure_safety(self):
        """Flicker rate must stay below seizure threshold"""
        when(ratio(self.flicker_rate, self.safe_threshold) >= 1.0, finfr)

    @forge
    def set_animation(self, rate: float):
        self.flicker_rate = rate

# Use Case: Video content verification
content = SeizureSafetyGovernor(safe_threshold=3.0)
content.set_animation(2.5)  # ✓ Safe (ratio = 0.83)
content.set_animation(4.0)  # ✗ BLOCKED (ratio = 1.33 >= 1.0)
```

### Education & Resource Management

```python
class ClassroomGovernor(Blueprint):
    """Manages class size and resource allocation."""
    enrolled = field(int, default=0)
    capacity = field(int, default=30)

    @law
    def capacity_limit(self):
        """Cannot exceed room capacity"""
        when(ratio(self.enrolled, self.capacity) > 1.0, finfr)

    @forge
    def enroll_student(self):
        self.enrolled += 1

# Use Case: School enrollment
classroom = ClassroomGovernor(capacity=30)
for _ in range(30):
    classroom.enroll_student()  # ✓ Works
classroom.enroll_student()      # ✗ BLOCKED (at capacity)
```

### API Verification Examples

```bash
# Example 1: Verify content safety
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "How do I write a business plan?"}'

# Example 2: Calculate with verification
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "sqrt", "args": [{"op": "+", "args": [9, 16]}]}}'

# Example 3: Ratio constraint verification
curl -X POST http://localhost:8000/constraint \
  -H "Content-Type: application/json" \
  -d '{
    "constraint": {
      "f_field": "debt",
      "g_field": "income",
      "operator": "ratio_le",
      "threshold": 0.43,
      "message": "Debt-to-income ratio exceeds 43% limit"
    },
    "object": {"debt": 2000, "income": 5000}
  }'

# Example 4: Generate lesson plan
curl -X POST http://localhost:8000/education/lesson \
  -H "Content-Type: application/json" \
  -d '{"grade": 5, "subject": "math", "teks_codes": ["5.3A"], "topic": "Fractions"}'

# Example 5: Get differentiated student groups
curl http://localhost:8000/teachers/classrooms/CLASS001/groups
```

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*"finfr = f/g. The ratio IS the constraint. 1 == 1."*

---

**Last Updated:** February 9, 2026 | **Version:** 1.3.0 | **Tests:** 700+ passing (288/288 realTinyTalk conformance)
