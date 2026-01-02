# Newton Supercomputer

**Verified Computation. Ask Newton. Go.**

[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/jaredlewiswechs/Newton-api)
[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](#licensing)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](#api-reference)
[![Tests](https://img.shields.io/badge/tests-47%20passing-brightgreen.svg)](#testing)

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

## What is Newton?

Newton is a **supercomputer** where:
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

---

## What Has Newton Proven?

| Property | Implementation | Status |
|----------|----------------|--------|
| **Determinism** | Same input → same output, always | Proven |
| **Termination** | HaltChecker proves all constraints terminate | Proven |
| **Consistency** | No constraint can both pass and fail | Proven |
| **Auditability** | Every operation in immutable ledger | Proven |
| **Adversarial Resistance** | MAD stats, locked baselines | Proven |
| **Byzantine Tolerance** | Consensus survives malicious nodes | Proven |
| **Bounded Execution** | No infinite loops, no stack overflow | Enforced |
| **Cryptographic Integrity** | Hash chains, Merkle proofs | Verified |

**Test Suite**: 47 test cases, all passing. Property-based testing with Hypothesis.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWTON SUPERCOMPUTER v1.0.0                  │
├─────────────────────────────────────────────────────────────────┤
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
│                        ASK NEWTON                               │
│                          /ask                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose | Lines | Key Feature |
|-----------|---------|-------|-------------|
| **CDL** | Constraint Definition Language | 672 | Temporal ops, aggregations, halt checking |
| **Logic** | Verified Computation Engine | 1,261 | Turing complete with bounded loops |
| **Forge** | Verification Engine (CPU) | 737 | Parallel evaluation, <1ms latency |
| **Vault** | Encrypted Storage (RAM) | 538 | AES-256-GCM, identity-derived keys |
| **Ledger** | Immutable History (Disk) | 576 | Hash-chained, Merkle proofs |
| **Bridge** | Distributed Protocol (Bus) | 542 | PBFT consensus, Byzantine tolerant |
| **Robust** | Adversarial Statistics | 597 | MAD, locked baselines, source tracking |
| **Grounding** | Claim Verification | 214 | External sources, confidence scoring |

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

---

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask Newton anything (full verification pipeline) |
| `/verify` | POST | Verify content against safety constraints |
| `/verify/batch` | POST | Batch verification (multiple inputs) |
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

## Repository Structure

```
Newton-api/
├── newton_supercomputer.py   # Main API server (1,158 LOC)
├── cli_verifier.py           # CLI verification tool
├── requirements.txt          # Python dependencies
│
├── core/                     # Core modules (~9,000 LOC)
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
│   ├── newton_os.rb         # Tahoe Kernel - Knowledge Base
│   └── newton_tahoe.rb      # Tahoe Kernel - PixelEngine
│
├── ledger/                   # Runtime ledger storage
│   └── sovereign_ledger.jsonl  # Genesis Crystal
│
├── tests/                    # Test suite (47 tests)
│   ├── test_integration.py
│   ├── test_glass_box.py
│   ├── test_merkle_proofs.py
│   ├── test_negotiator.py
│   ├── test_policy_engine.py
│   └── test_properties.py
│
├── frontend/                 # Web UI (PWA)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── docs/                     # Documentation
│   ├── README.md            # Docs index
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
├── CONTRIBUTING.md          # Developer guide (newbie-friendly)
├── DEPLOYMENT.md            # Deployment guide
├── CHANGELOG.md             # Version history
├── render.yaml              # Render.com config
├── Dockerfile               # Container build
│
├── examples/                # Working demos
│   └── tinytalk_demo.py    # tinyTalk concepts in action
│
├── tinytalk/                # tinyTalk documentation
│   ├── ruby/               # Ruby module
│   └── r/                  # R package
│
├── tinytalk_py/             # Python package (importable)
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

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ --cov=core --cov-report=html
```

**Test Coverage:**
- Core integration tests (14 tests)
- Glass Box tests (12 tests)
- Merkle proof tests (13 tests)
- Negotiator tests (12 tests)
- Policy engine tests (10 tests)
- Property-based tests (Hypothesis)

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

**Open Source (Non-Commercial)**
Personal projects, academic research, non-profit organizations.

**Commercial License Required**
SaaS products, enterprise deployments, revenue-generating applications.

Contact: **jn.lewis1@outlook.com**

---

## About

Newton Supercomputer is built by **Ada Computing Company** in Houston, Texas.

**Jared Lewis**
[linkedin.com/in/jaredlewisuh](https://linkedin.com/in/jaredlewisuh) · [parcri.net](https://parcri.net)

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

© 2025-2026 Ada Computing Company · Houston, Texas

*"1 == 1. The cloud is weather. We're building shelter."*
