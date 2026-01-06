# Newton Supercomputer Documentation

**Verified Computation. Ask Newton. Go.**

Welcome to the Newton Supercomputer documentation. Newton is a **Cryptographically Verified Constraint Logic Programming (CLP) System**—a direct descendant of five decades of constraint programming research (Sketchpad 1963, Waltz 1975, ThingLab 1979, CLP 1987, Propagators 1980), synthesized into a modern Python implementation with cryptographic audit trails.

The constraint IS the instruction. The verification IS the computation.

**finfr = f/g** — Every constraint is a ratio between what you're trying to do (f) and what reality allows (g).

**Version**: 1.2.0 | **Date**: January 6, 2026 | **Tests**: 580+ passing | **Jared Nashon Lewis** | **Jared Lewis Conglomerate** | **parcRI** | **Newton** | **tinyTalk** | **Ada Computing Company**

---

## Documentation Index

### Getting Started
- [Quick Start Guide](getting-started.md) - Get up and running in 5 minutes
- **[Newton API Intro Course](INTRO_COURSE.md)** - 5-level PDA tutorial with runnable examples (NEW)
- **[R/RStudio Quickstart](../RSTUDIO_QUICKSTART.md)** - Local and remote R integration (NEW)
- [Authentication](authentication.md) - API keys, rate limits, and security
- [Configuration](configuration.md) - Environment variables and settings

### Core Concepts
- **[CLP System Definition](NEWTON_CLP_SYSTEM_DEFINITION.md)** - Historical lineage and CS foundations (Sketchpad, Waltz, ThingLab, CLP)
- **[Geometric Constraint Semantics](foundation/GEOMETRIC_CONSTRAINT_SEMANTICS.md)** - Symbol geometry → constraint verification (NEW)
- [f/g Visual Language](product-architecture/FG_VISUAL_LANGUAGE.md) - The Newton ratio made visible
- [Whitepaper](../WHITEPAPER.md) - Architecture and philosophy
- [Glass Box](../GLASS_BOX.md) - Policy enforcement, HITL, Merkle proofs
- [Logic Engine](logic-engine.md) - Verified Turing complete computation
- [Technical Roadmap](ROADMAP.md) - Development phases and goals
- [Changelog](../CHANGELOG.md) - Version history

### API Reference
- [API Overview](api-reference.md) - Complete API reference
- [Core Endpoints](endpoints/core.md) - Verify, Calculate, Constraint, Ground
- [Audit & Security](endpoints/audit.md) - Ledger, Vault, Certificates
- [Metadata](endpoints/metadata.md) - Health, Metrics, Examples

### Components

#### Core Layer

| Component | Documentation | Purpose | Lines |
|-----------|---------------|---------|-------|
| **CDL** | [Constraints](api-reference.md#constraint) | Constraint Definition Language | 672 |
| **Logic** | [logic-engine.md](logic-engine.md) | Verified computation engine | 1,261 |
| **Forge** | [Verification](api-reference.md#verify) | Parallel verification CPU | 737 |
| **Vault** | [Storage](api-reference.md#vault-store) | Encrypted storage (AES-256-GCM) | 538 |
| **Ledger** | [Audit](api-reference.md#ledger) | Immutable hash-chained history | 576 |
| **Bridge** | [Distributed](api-reference.md) | PBFT Byzantine consensus | 542 |
| **Robust** | [Statistics](api-reference.md#statistics) | Adversarial-resistant stats | 597 |
| **Grounding** | [grounding.md](grounding.md) | Claim verification | 214 |

#### Glass Box Layer

| Component | Documentation | Purpose | Lines |
|-----------|---------------|---------|-------|
| **Policy Engine** | [Glass Box](../GLASS_BOX.md) | Policy-as-code enforcement | 354 |
| **Negotiator** | [Glass Box](../GLASS_BOX.md) | Human-in-the-loop approvals | 361 |
| **Merkle Anchor** | [Glass Box](../GLASS_BOX.md) | Proof scheduling and export | 340 |
| **Vault Client** | [Glass Box](../GLASS_BOX.md) | Provenance logging | 132 |

#### Tahoe Kernel

| Component | Purpose |
|-----------|---------|
| **newton_os.rb** | Knowledge Base with origin truth |
| **newton_tahoe.rb** | PixelEngine with genesis mark |

#### Advanced Modules (NEW in 1.2.0)

| Component | Documentation | Purpose | Tests |
|-----------|---------------|---------|-------|
| **Newton TLM** | [newton_tlm/README.md](../newton_tlm/README.md) | ACID-compliant symbolic kernel with PARADOX detection | 23/23 |
| **Newton Geometry** | [newton_geometry/README.md](../newton_geometry/README.md) | Topological constraint framework | ✓ |
| **TextGen** | [textgen.md](textgen.md) | Constraint-preserving text generation | ✓ |
| **Typed Dictionary** | [core/typed_dictionary.py](../core/typed_dictionary.py) | Words become laws through math + types (NEW) | ✓ |
| **Jester** | [jester-analyzer/README.md](../jester-analyzer/README.md) | Code constraint translator | ✓ |

### Advanced Features
- [Cartridges](cartridges.md) - Visual, Sound, Sequence, Data, Rosetta, Auto
- [Framework Verification](frameworks.md) - Apple, Web, ML framework constraints
- [Swift & SwiftUI Guide](frameworks/SWIFT_SWIFTUI_GUIDE.md) - Native iOS/iPadOS development with Swift 6.2
- [Claim Grounding](grounding.md) - Fact-checking against external sources
- [Newton PDA](newton-pda.md) - Personal Data Assistant (PWA)
- [Teacher's Aide](../teachers-aide/README.md) - HISD NES lesson planning, TEKS alignment, classroom management, and auto-differentiation

### Deployment
- [Deployment Guide](../DEPLOYMENT.md) - Render.com, Docker, Local
- [Self-Hosting Guide](self-hosting.md) - Deploy Newton on your infrastructure

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWTON SUPERCOMPUTER v1.2.0                  │
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
│  │               TEACHER'S AIDE DATABASE                    │   │
│  │  ┌──────────┐ ┌────────────┐ ┌─────────────────────────┐│   │
│  │  │ Students │ │ Classrooms │ │ Auto-Differentiation    ││   │
│  │  │   (188   │ │ Assessment │ │ Tier 3→2→1→Enrichment   ││   │
│  │  │   TEKS)  │ │  Tracking  │ │ (groups after scores)   ││   │
│  │  └──────────┘ └────────────┘ └─────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                        ASK NEWTON                               │
│                          /ask                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [Main README](../README.md) | Project overview |
| [API Reference](api-reference.md) | Full endpoint documentation |
| [Logic Engine](logic-engine.md) | Verified computation guide |
| [Glass Box](../GLASS_BOX.md) | Policy, HITL, Merkle proofs |
| [Whitepaper](../WHITEPAPER.md) | Technical architecture |
| [GitHub](https://github.com/jaredlewiswechs/Newton-api) | Source code |

---

## Base URL

| Environment | URL |
|-------------|-----|
| **Hosted API** | `https://newton-api.onrender.com` |
| **Self-hosted** | `http://localhost:8000` |

---

## API Endpoints Summary

### Core (7 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Full verification pipeline |
| `/verify` | POST | Content safety verification |
| `/verify/batch` | POST | Batch verification |
| `/calculate` | POST | Verified computation |
| `/constraint` | POST | CDL constraint evaluation |
| `/ground` | POST | Claim grounding |
| `/statistics` | POST | Robust statistical analysis |

### Storage & Audit (5 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/vault/store` | POST | Store encrypted data |
| `/vault/retrieve` | POST | Retrieve encrypted data |
| `/ledger` | GET | View audit trail |
| `/ledger/{index}` | GET | Entry with Merkle proof |
| `/ledger/certificate/{index}` | GET | Export certificate |

### Glass Box (10 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/policy` | GET/POST/DELETE | Policy management |
| `/negotiator/pending` | GET | Pending approvals |
| `/negotiator/request` | POST | Create approval request |
| `/negotiator/request/{id}` | GET | Get request |
| `/negotiator/approve/{id}` | POST | Approve request |
| `/negotiator/reject/{id}` | POST | Reject request |
| `/merkle/anchors` | GET | List anchors |
| `/merkle/anchor` | POST | Create anchor |
| `/merkle/proof/{index}` | GET | Generate proof |
| `/merkle/latest` | GET | Latest anchor |

### Cartridges (7 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cartridge/visual` | POST | SVG/image specification |
| `/cartridge/sound` | POST | Audio specification |
| `/cartridge/sequence` | POST | Video/animation specification |
| `/cartridge/data` | POST | Report specification |
| `/cartridge/rosetta` | POST | Code generation prompt |
| `/cartridge/auto` | POST | Auto-detect and compile |
| `/cartridge/info` | GET | Cartridge information |

### Education (8 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/education/lesson` | POST | Generate NES-compliant lesson plan |
| `/education/slides` | POST | Generate slide deck |
| `/education/assess` | POST | Analyze student assessments (MAD) |
| `/education/plc` | POST | Generate PLC report |
| `/education/teks` | GET | Browse TEKS standards |
| `/education/teks/{code}` | GET | Get specific standard |
| `/education/teks/search` | POST | Search standards |
| `/education/info` | GET | Education API documentation |

### Teacher's Aide Database (20 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/teachers/db` | GET | Database summary |
| `/teachers/students` | POST | Add student |
| `/teachers/students/batch` | POST | Add multiple students |
| `/teachers/students` | GET | List/search students |
| `/teachers/students/{id}` | GET | Get student details |
| `/teachers/classrooms` | POST | Create classroom |
| `/teachers/classrooms` | GET | List classrooms |
| `/teachers/classrooms/{id}` | GET | Get classroom with roster |
| `/teachers/classrooms/{id}/students` | POST | Add students to roster |
| `/teachers/classrooms/{id}/groups` | GET | **Get differentiated groups** |
| `/teachers/classrooms/{id}/reteach` | GET | Get reteach group |
| `/teachers/assessments` | POST | Create assessment |
| `/teachers/assessments/{id}/scores` | POST | Enter scores by ID |
| `/teachers/assessments/{id}/quick-scores` | POST | Enter scores by name |
| `/teachers/interventions` | POST | Create intervention plan |
| `/teachers/teks` | GET | Browse 188 TEKS (K-8) |
| `/teachers/teks/stats` | GET | TEKS statistics |
| `/teachers/db/save` | POST | Save database to file |
| `/teachers/db/load` | POST | Load database from file |
| `/teachers/info` | GET | Teacher's Aide API docs |

### System (3 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status |
| `/metrics` | GET | Performance metrics |
| `/calculate/examples` | POST | Example expressions |

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

## Proven Properties

| Property | Implementation | Status |
|----------|----------------|--------|
| **Determinism** | Same input → same output | Proven |
| **Termination** | HaltChecker proves termination | Proven |
| **Consistency** | No constraint can both pass and fail | Proven |
| **Auditability** | Every operation in ledger | Proven |
| **Adversarial Resistance** | MAD stats, locked baselines | Proven |
| **Byzantine Tolerance** | PBFT consensus | Proven |
| **Bounded Execution** | Hard limits enforced | Enforced |
| **Cryptographic Integrity** | Hash chains, Merkle proofs | Verified |

---

## Test Coverage (January 2026)

| Test Suite | Tests | Status | What It Proves |
|------------|-------|--------|----------------|
| **Full System** | 10/10 | ✓ 100% | All components connected |
| **Newton TLM** | 23/23 | ✓ 100% | ACID compliance |
| **Main Suite** | 558/586 | ✓ 95% | Core functionality |

### Detailed Breakdown

| Test Suite | Tests | Status |
|------------|-------|--------|
| Newton TLM (ACID) | 23 | Passing |
| Reversible State Machine | 22 | Passing |
| Reversible Shell | 46 | Passing |
| tinyTalk Core | 52 | Passing |
| Ratio Constraints (f/g) | 25 | Passing |
| Integration | 14 | Passing |
| Glass Box | 12 | Passing |
| Merkle Proofs | 13 | Passing |
| Negotiator | 12 | Passing |
| Policy Engine | 10 | Passing |
| Properties (Hypothesis) | Multiple | Passing |
| **Total** | **580+** | **95%+ Passing** |

---

---

## NEW: f/g Ratio Constraints

**finfr = f/g** — Newton's core insight: every constraint is a ratio.

### Quick Example

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @forge
    def take_loan(self, amount: float):
        self.debt += amount

gov = LeverageGovernor()
gov.take_loan(2000)   # ✓ Works (ratio = 2.0)
gov.take_loan(1500)   # ✗ BLOCKED (ratio = 3.5 > 3.0)
```

### REST API

```bash
curl -X POST http://localhost:8000/constraint \
  -H "Content-Type: application/json" \
  -d '{
    "constraint": {
      "f_field": "liabilities",
      "g_field": "assets",
      "operator": "ratio_le",
      "threshold": 1.0
    },
    "object": {"liabilities": 500, "assets": 1000}
  }'
```

### Use Cases

| Domain | Constraint | f | g | Threshold |
|--------|------------|---|---|-----------|
| **Banking** | No overdraft | withdrawal | balance | ≤ 1.0 |
| **Finance** | Leverage limit | debt | equity | ≤ 3.0 |
| **Healthcare** | Seizure safety | flicker_rate | safe_limit | < 1.0 |
| **Education** | Class size | students | capacity | ≤ 1.0 |

See [f/g Ratio Constraints](../README.md#fg-ratio-constraints-dimensional-analysis-1) for full documentation.

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*"finfr = f/g. The ratio IS the constraint. 1 == 1."*
