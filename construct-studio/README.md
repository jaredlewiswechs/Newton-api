# Construct Studio v0.1

**A Constraint-First Execution Environment**

Programs don't "fail" — they never exist if they violate invariants.
This is not a rule engine. It's geometric validation of intent.

```
In CAD, intersecting geometry shows a collision.
In Construct, violating a constraint shows Ontological Death.
```

---

## What Is This?

Construct Studio is a **design-time simulator for business physics**.

It provides:
- **Pre-approval by physics, not by process** — illegal states cannot execute
- **Geometric validation** — constraints are collision detection
- **Immutable audit trails** — every force application is recorded
- **Domain cartridges** — plug-in constraint systems for Finance, Infrastructure, Risk

This is not:
- an IDE
- a linter
- a test runner
- a workflow engine

It's a **Logic CAD Tool** where the constraint IS the instruction.

---

## Quick Start

### Python REPL

```bash
cd construct-studio
python -m construct_studio
```

```
construct> floor card
  Created CorporateCard floor (budget: 5000 USD)

construct> force 1500 USD >> CorporateCard
  Applying force: 1500 USD >> CorporateCard.budget
  ─────────────────────────────────────────
  ✓ FORCE ABSORBED
    Ratio: 30.0%
    Remaining: 3500 USD
    Utilization: 30.0%

construct> force 4000 USD >> CorporateCard
  Applying force: 4000 USD >> CorporateCard.budget
  ─────────────────────────────────────────
  ✗ ONTOLOGICAL DEATH
    Overflow: 500 USD
    Available: 3500 USD
    Requested: 4000 USD
```

### Python API

```python
from construct_studio import Matter, Floor, Construct, attempt

# Define a Floor (constraint container)
class CorporateCard(Floor):
    budget = Matter(5000, "USD")

# Create matter and apply force
expense = Matter(1500, "USD")
expense >> CorporateCard.budget  # OK

# This would cause Ontological Death:
big_expense = Matter(6000, "USD")
big_expense >> CorporateCard.budget  # Dies
```

### Soft Mode (Simulation)

```python
from construct_studio import attempt

with attempt():
    result = Matter(6000, "USD") >> CorporateCard.budget
    if not result:
        print(f"Would overflow by {result.ratio.overflow} USD")
```

### Web UI

Open `ui/index.html` in your browser for a visual CAD-like interface.

---

## Core Concepts

### Matter

A typed value with units. The "solid" in your design space.

```python
cost = Matter(1500, "USD")
cpu = Matter(32, "vCPU")
risk = Matter(0.15, "probability")
```

### Floor

A constraint container. The boundary of valid design space.

```python
class DeploymentQuota(Floor):
    cpu = Matter(64, "vCPU")
    memory = Matter(256, "GB")
```

### Force (>>)

The physics operator. Applies Matter to a Floor.

```python
cpu_request = Matter(32, "vCPU")
cpu_request >> DeploymentQuota  # Force application
```

Force either:
- **Succeeds**: Matter is absorbed, capacity reduced
- **Fails**: Ontological Death — this timeline doesn't exist

### Ratio

The collision test result.

```python
ratio.fits      # True if force succeeded
ratio.value     # Numerator/denominator
ratio.overflow  # How much didn't fit
```

### Ledger

The immutable audit trail.

```python
from construct_studio import global_ledger

global_ledger.print_summary()
# ╔══════════════════════════════════════════╗
# ║  LEDGER: global                          ║
# ╠══════════════════════════════════════════╣
# ║  Total Entries:                       15 ║
# ║  Successes:                           12 ║
# ║  Deaths:                               3 ║
# ║  Death Rate:                        20.0% ║
# ╚══════════════════════════════════════════╝
```

### Ontological Death

Not an exception to catch — it's reality pruning.

```python
class OntologicalDeath(Exception):
    """
    The illegal state never existed.
    In CAD terms: the geometry intersected.
    There is no "fix" — there is only "redesign".
    """
```

---

## Domain Cartridges

### Finance

```python
from construct_studio.cartridges.finance import (
    CorporateCard, spend, simulate_spending
)

# Direct use
card = CorporateCard()
expense = Matter(1500, "USD")
expense >> card

# High-level API
result = spend(1500, "Office supplies")

# Simulation
results = simulate_spending([
    (1500, "Office supplies"),
    (800, "Team lunch"),
    (2000, "Software license"),
    (1200, "Conference"),  # Dies
])
```

### Infrastructure

```python
from construct_studio.cartridges.infrastructure import (
    DeploymentQuota, DeploymentSpec, simulate_deployments
)

# Define deployment
spec = DeploymentSpec(
    name="api-server",
    cpu=4,
    memory=8,
    replicas=3
)

# Simulate fleet deployment
results = simulate_deployments([
    DeploymentSpec("api", cpu=4, memory=8, replicas=3),
    DeploymentSpec("worker", cpu=8, memory=16, replicas=5),
    DeploymentSpec("ml-model", cpu=32, memory=128, replicas=2),  # Dies
])
```

### Risk

```python
from construct_studio.cartridges.risk import (
    RiskBudget, RiskPosition, simulate_portfolio, accept_risk
)

# Accept a risk
result = accept_risk(0.05, "Market exposure")

# Simulate portfolio
positions = [
    RiskPosition("Stocks", 50000, probability_of_loss=0.05),
    RiskPosition("Crypto", 10000, probability_of_loss=0.15),
    RiskPosition("Venture", 20000, probability_of_loss=0.30),  # Dies
]
results = simulate_portfolio(positions)
```

---

## Engine API

For complex simulations:

```python
from construct_studio import ConstructEngine, SimulationMode

# Create engine
engine = ConstructEngine("my_simulation", SimulationMode.SOFT)

# Register floors
engine.register_floor(CorporateCard)
engine.register_floor(DeploymentQuota)

# Take snapshot
engine.snapshot("before_operations")

# Run simulation
result = engine.simulate([
    ("force", {"value": 1000, "unit": "USD", "floor": "CorporateCard"}),
    ("force", {"value": 2000, "unit": "USD", "floor": "CorporateCard"}),
    ("force", {"value": 3000, "unit": "USD", "floor": "CorporateCard"}),  # Dies
])

print(result)
# SimulationResult(FAILED, 2/3 ops, 1 deaths)

# Analyze
analysis = engine.analyze()

# Restore snapshot
engine.restore("before_operations")
```

---

## Architecture

```
construct-studio/
├── __init__.py          # Public API
├── core.py              # Matter, Floor, Force, Ratio, ConstructError
├── ledger.py            # Immutable audit trail
├── engine.py            # Simulation engine
├── cli.py               # Interactive REPL
├── cartridges/          # Domain modules
│   ├── finance.py       # Corporate cards, budgets
│   ├── infrastructure.py # Deployment quotas
│   └── risk.py          # Probability budgets
├── ui/
│   └── index.html       # Visual CAD interface
└── tests/
    └── test_core.py     # Unit tests
```

### Design Principles

1. **O(1) Ratio** — Constraint checking is constant time
2. **Append-only Ledger** — No history modification
3. **No shared mutable state** — Except the log
4. **UI is projection** — Pure function of Ledger state
5. **Fail fast, fail permanent** — Ontological Death, not retry

---

## The Mental Model

Think of it like CAD software:

| CAD Concept | Construct Concept |
|-------------|-------------------|
| Solid geometry | Matter |
| Bounding box | Floor |
| Motion vector | Force (>>) |
| Collision detection | Ratio |
| Version history | Ledger |
| Invalid geometry | Ontological Death |

---

## Why This Matters

Traditional governance:
```
1. Write policy document
2. Build approval workflow
3. Hope people follow it
4. Audit after violations
5. Fix retroactively
```

Construct governance:
```
1. Define physics (Floor)
2. Apply force (>>)
3. Invalid states cannot exist
4. Ledger proves everything
5. Nothing to fix
```

**Pre-approval by physics, not by process.**

---

## Roadmap

### v0.2 (Next)
- [ ] Explicit Floor base class improvements
- [ ] AST-based analysis (remove monkey-patching)
- [ ] Live edit → re-simulate loop
- [ ] Persist Ledger to disk

### v0.3
- [ ] Multiple Floors per project
- [ ] Named constraints
- [ ] Export Ledger as compliance artifact
- [ ] Headless mode (CI/CD)

### v1.0
- [ ] Web UI with real-time collaboration
- [ ] Plugin marketplace (cartridges)
- [ ] GitHub integration
- [ ] "Explain this death" LLM integration

---

## Philosophy

> "The constraint IS the instruction."

You didn't write a budget policy.
You defined the physics of spending.

You didn't create an approval workflow.
You made illegal states impossible.

The Ledger doesn't prove compliance.
It proves existence.

---

## License

MIT

---

## Contributing

This is v0.1 — early, working, coherent.

If you see this and think "I need this for X domain" — you're probably right.

Create a cartridge. Make the physics real.
