# Newton-API Master README

**February 2026**

A verification-first computation platform combining Ada Lovelace's computational philosophy with Newton's verification engine.

---

## Main Components

| Component | Description | Location |
|-----------|-------------|----------|
| **Nina** | Consumer PDA interface + Developer verification forge | `/nina` |
| **Adan** | Full-featured self-verifying autonomous agent | `/adan` |
| **Adan Portable** | Standalone distribution for deployment | `/adan_portable` |
| **newton_agent** | Core verified computation engine | `/newton_agent` |

---

## Nina

**Newton Intelligence and Natural Assistant**

A contemporary reimagining of the Apple Newton MessagePad (1993-1998), providing both a consumer-facing PDA interface and a developer-facing verification engine.

### Consumer UI (`nina-pda`)
- Notes
- Names (Contacts)
- Dates (Calendar)
- Calculator
- Verify

### Developer Forge
- **9-Stage Compiler Pipeline:** Intent Lock → Parse → Abstract Interpretation → Geometric Check → Verify/Upgrade → Execute → Log → Meta-check → Return
- **Regime System:** Mode-dependent verification rules
- **Distortion Metric:** `D(w,a) = d(v(a), g(w))` for input validation
- **Trust Lattice:** `UNTRUSTED ⊏ TRUSTED` promotion mechanism
- **Knowledge Bridge:** Connects to `adan_portable` knowledge base

### Core Modules
```
nina/developer/forge/
├── regime.py      # Domain rules
├── distortion.py  # Distortion metric
├── trust.py       # Trust lattice
├── pipeline.py    # 9-stage pipeline
├── knowledge.py   # KB bridge
└── ollama.py      # Ollama integration
```

---

## Adan

**Ada + Newton**

A self-verifying autonomous agent combining Ada Lovelace's computational philosophy with Newton's verification engine.

### 10-Step Pipeline
1. Ada Sense
2. Constraint Check
3. Identity Check
4. Knowledge Base
5. Knowledge Mesh
6. Math Engine
7. LLM
8. Ada Watch
9. Grounding
10. Meta Verify

### Key Features
- **Ada Sentinel:** Immune system detecting semantic drift and adversarial patterns
- **Meta Newton:** Self-verification with 9 core constraints
- **Kinematic Linguistics:** Language treated as physics
- **TI Calculator:** Full TI-84 style verified calculator
- **Knowledge Base:** 2,845 lines with 200+ countries, 118 elements, 50+ company facts
- **Identity Module:** Self-verification system
- **Trajectory Verifier:** Action sequence validation

### Core Components
```
adan/
├── agent.py                 # Main NewtonAgent orchestrator
├── ada.py                   # Sentinel system
├── meta_newton.py           # Self-verification
├── kinematic_linguistics.py # Language physics
├── ti_calculator.py         # Verified calculations
├── knowledge_base.py        # 126KB verified facts
├── trajectory_verifier.py   # Action validation
└── identity.py              # Self-knowledge
```

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message to agent |
| `/ground` | POST | Verify specific claims |
| `/history` | GET | Get conversation history |
| `/audit` | GET | Export full audit trail |

### Performance
- **Accuracy:** 100% on 50-query benchmark
- **Response Time:** 0.7ms average
- **Throughput:** 1,113 queries/sec

---

## Adan Portable

A portable, self-contained version of Adan designed for deployment without external dependencies. Acts as the knowledge and logic provider for other components.

### Run Modes
```bash
python run.py              # Start server + open UI
python run.py --no-browser # Start server only
python run.py --wiki       # Start Adanpedia on port 8085
python run.py --test       # Run integration tests
python run.py --acid       # Run ACID test
```

### Structure
```
adan_portable/
├── run.py          # Main entry point
├── core/
│   ├── logic.py    # Core verification logic
│   └── __init__.py
├── adan/           # Full Adan codebase (portable)
└── requirements.txt
```

---

## newton_agent

The core verified computation engine that serves as the foundation for all Newton-based applications.

### Fundamental Law
```python
def newton(current, goal):
    return current == goal
# When True → execute
# When False → halt
```

### Key Features
- **Verified Computation:** Proof of correctness, not just results
- **Ada Lovelace Principle:** Computation is more than calculation
- **Safety Constraints:** Harm, legal, medical, privacy, security checks
- **Deterministic Responses:** Same input → same output
- **Bounded Execution:** Memory, time, recursion limits enforced
- **Audit Trail:** Complete ledger with cryptographic proofs

### Core Modules
```
newton_agent/
├── agent.py              # Main orchestrator
├── ada.py                # Sentinel system
├── meta_newton.py        # Meta-level verification
├── kinematic_linguistics.py
├── ti_calculator.py      # Verified math
├── knowledge_base.py     # Pre-verified facts (CIA, NIST, ISO, IUPAC)
├── identity.py           # Self-knowledge
├── constraints.py        # Safety constraints
├── language_mechanics.py # Typo correction
├── llm_ollama.py         # Ollama backend
└── grounding_enhanced.py # External verification
```

### Response Structure
```python
AgentResponse:
  - content: str              # The answer
  - verified: bool            # Verification status
  - constraints_passed: bool  # Safety checks
  - source: str               # KB, LOGIC, LLM, IDENTITY
  - processing_time_ms: float # Latency
  - metadata: Dict            # Additional context
```

### Performance Benchmarks
- **50/50 queries** correct and verified
- **0.7ms** average response time
- **1,113** queries/sec throughput
- **638x** faster than Stripe
- **563x** faster than GPT-4

---

## Component Relationships

```
newton_agent (core engine)
    │
    ├── adan (full featured agent)
    │   ├── API endpoints
    │   ├── Web UI
    │   └── All core modules
    │
    ├── adan_portable (standalone)
    │   └── Embedded adan copy
    │
    └── nina (consumer interface)
        ├── PDA UI (HTML/CSS/JS)
        └── Developer forge
            └── Bridges to adan_portable KB
```

---

## Architectural Philosophy

All components are built on **verification-first architecture**:

- **Constraints are instructions** — Rules define what's possible
- **Verification is computation** — Proving correctness is the operation
- **Trust is earned, not assumed** — External input must be verified
- **Determinism matters** — Same input always produces same output
- **Bounds are guaranteed** — No unbounded operations

---

## License

Open Source (Non-Commercial) for personal/academic projects.
Commercial license required for revenue-generating applications.

---

**Created by:** Jared Lewis
