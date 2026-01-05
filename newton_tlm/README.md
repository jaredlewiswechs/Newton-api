# Newton TLM - Topological Language Machine

```
    ═══════════════════════════════════════════════════════════════
    The constraint IS the instruction.
    The verification IS the computation.
    The network IS the processor.
    ═══════════════════════════════════════════════════════════════
```

A **Newton-compliant Topological Language Machine** - a deterministic symbolic language kernel for verified computation.

## Overview

Newton TLM implements a phase-driven symbolic computation system with guaranteed properties:

- **Deterministic**: Same input → same output, always
- **Bounded**: All operations terminate within defined limits
- **Reversible**: Perfect snapshot/restore/rollback capability
- **Auditable**: Append-only ledger with hash-chaining
- **Atomic**: Transactions are all-or-nothing
- **Verifiable**: 1==1 invariant checking at every step

## Architecture

### 4-Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Applications                                       │
│  • Pattern Recognition  • Goal Crystallization              │
│  • Semantic Networks    • Knowledge Graphs                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Newton TLM (This Module)                          │
│  • Phase Machine       • Transaction System                 │
│  • Ledger             • Snapshot/Restore                    │
│  • Invariant Checking • Goal Registry                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Graph Operations                                   │
│  • NetworkX DiGraph    • Atom Storage                       │
│  • Edge Management     • Pattern Counting                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Foundation                                         │
│  • Immutable Atoms     • Hash Functions                     │
│  • Data Structures     • Serialization                      │
└─────────────────────────────────────────────────────────────┘
```

## PARCRI Principles

Newton TLM follows the PARCRI methodology:

| Principle | Implementation |
|-----------|----------------|
| **P**attern = Diffs only | Ledger stores only deltas (atoms added, edges added, pattern changes) |
| **A**rchitecture = Intent first | Phase machine enforces intent before execution |
| **R**eading = Compress to learn | Patterns crystallize during CRYSTALLIZE phase |
| **C**onstraint = Boundary on recursion | Phase cycle is bounded (0→9→0), no infinite loops |
| **I**nvariant = Reversible state | Snapshot/restore enables perfect rollback |

## Quick Start

### Installation

```bash
# Install Newton TLM with dependencies
pip install networkx==3.1
```

### Basic Usage

```python
from newton_tlm import NewtonTLM

# Create a new TLM instance
tlm = NewtonTLM()

# Ingest data (full phase cycle: 0→9→0)
success = tlm.ingest("Hello, Newton!")

# Check state
state_hash = tlm.get_state_hash()
print(f"State hash: {state_hash}")

# Create snapshot
snapshot = tlm.snapshot()

# Make more changes
tlm.ingest("More data")

# Rollback to snapshot
tlm.rollback(snapshot.index)

# Export ledger for durability
ledger = tlm.export_ledger()
```

### Transaction Example

```python
from newton_tlm import NewtonTLM, Atom

tlm = NewtonTLM()

# Begin atomic transaction
tx = tlm.begin_transaction()

# Add atoms
atom1 = Atom.create("atom_1", "concept", "Newton")
atom2 = Atom.create("atom_2", "concept", "Computation")
tx.add_atom(atom1)
tx.add_atom(atom2)

# Add edge
tx.add_edge("atom_1", "atom_2", "relates_to")

# Update patterns
tx.update_pattern("concept_count", 2)

# Commit all changes atomically
tlm.commit_transaction()

# Or abort to discard all changes
# tlm.abort_transaction()
```

### Goal Registry Example

```python
from newton_tlm import NewtonTLM, GoalRegistry

tlm = NewtonTLM()

# Register goals
tlm.goal_registry.register_goal("process_10_items", 10)

# Process items
for i in range(10):
    tlm.ingest(f"item_{i}")

# Check goal achievement
item_count = len(tlm.graph.nodes())
achieved = tlm.goal_registry.check_goal("process_10_items", item_count)

print(f"Goal achieved: {achieved}")
```

## Phase Cycle

Every computation follows a strict phase cycle:

```
    0. IDLE       ──┐
         ↓          │
    1. INGEST      │
         ↓          │
    2. PARSE       │
         ↓          │
    3. CRYSTALLIZE │  Complete
         ↓          │  Cycle
    4. DIFFUSE     │
         ↓          │
    5. CONVERGE    │
         ↓          │
    6. VERIFY      │
         ↓          │
    7. COMMIT      │
         ↓          │
    8. REFLECT     │
         ↓          │
    0. IDLE ◄──────┘
```

### Phase Rules

1. **Every cycle starts at IDLE (0)**
2. **Every cycle returns to IDLE (0)**
3. **No phase can be skipped**
4. **No state mutation in IDLE**

### Phase Descriptions

| Phase | Purpose | Operations |
|-------|---------|------------|
| **IDLE** | Rest state | No mutations, ready for input |
| **INGEST** | Accept input | Begin transaction, receive data |
| **PARSE** | Structure data | Create atoms from input |
| **CRYSTALLIZE** | Form patterns | Update pattern counts |
| **DIFFUSE** | Spread activation | Propagate through graph |
| **CONVERGE** | Stabilize | Consolidate patterns |
| **VERIFY** | Check invariants | Validate constraints |
| **COMMIT** | Apply changes | Write to ledger |
| **REFLECT** | Learn | Analyze results |

## The 1==1 Invariant

At the heart of Newton is the fundamental law:

```python
newton(current, goal) → (current == goal)
```

When `current == goal` is **true** → execute  
When `current == goal` is **false** → halt

This isn't a feature. It's the architecture.

### Implementation

```python
from newton_tlm import one_equals_one, canonical_hash

# Check equivalence
current_state = {"value": 42, "status": "ready"}
goal_state = {"status": "ready", "value": 42}

# Order-independent comparison
assert one_equals_one(current_state, goal_state)

# Under the hood: deterministic hashing
hash1 = canonical_hash(current_state)
hash2 = canonical_hash(goal_state)
assert hash1 == hash2  # True despite different key order
```

## ACID + Newton Compliance

Newton TLM guarantees both traditional ACID properties and Newton-specific principles:

### ACID Properties

| Property | Guarantee | Test |
|----------|-----------|------|
| **Atomicity** | Empty/failed ingest = zero state change | Transaction abort doesn't affect state |
| **Consistency** | Same input → same hash | Deterministic state hashing |
| **Isolation** | Separate models don't interfere | Independent TLM instances |
| **Durability** | Export/replay preserves state | Ledger replay reconstructs exact state |

### Newton Principles

| Principle | Guarantee | Test |
|-----------|-----------|------|
| **N1: Determinism** | Same input → same output | Hash equality across runs |
| **N2: Boundary** | Bounded execution | Phase cycle enforcement |
| **N3: Diffability** | All changes tracked | Ledger completeness |
| **N4: Reversibility** | Snapshot/restore works | Rollback verification |
| **N5: Phase Loop** | 0→9→0 cycle enforced | Phase machine validation |
| **N6: 1==1 Invariant** | Goal equivalence | `one_equals_one()` checks |
| **N7: Ledger Integrity** | Hash chains consistent | Chain verification |

## File Structure

```
newton_tlm/
├── README.md                    # This file
├── __init__.py                  # Package exports
│
├── atom.py                      # Immutable atom dataclass (frozen)
├── transaction.py               # Atomic transaction buffer
├── ledger_entry.py              # Canonical diff format
├── phases.py                    # Phase machine (0→9→0 cycle)
├── invariant.py                 # 1==1 goal equivalence checks
├── reversibility.py             # Snapshot/restore/rollback
├── tlm.py                       # Main NewtonTLM class
│
└── tests/
    ├── __init__.py
    └── test_acid_newton.py      # ACID + Newton compliance tests
```

## API Reference

### Core Classes

#### NewtonTLM

Main class implementing the TLM.

```python
tlm = NewtonTLM()

# State operations
hash = tlm.get_state_hash()
tlm.ingest(data)

# Transaction management
tx = tlm.begin_transaction()
tlm.commit_transaction()
tlm.abort_transaction()

# Snapshot/restore
snapshot = tlm.snapshot()
tlm.restore(snapshot)
tlm.rollback(index)

# Ledger operations
ledger = tlm.export_ledger()
tlm.replay_ledger(ledger_data)
tlm.verify_integrity()
```

#### Atom

Immutable symbolic atom (frozen dataclass).

```python
atom = Atom.create(
    id="atom_1",
    kind="concept",
    value="Newton",
    layer=0
)

# Serialization
dict_data = atom.to_dict()
atom = Atom.from_dict(dict_data)
```

#### Transaction

Atomic mutation buffer.

```python
tx = Transaction()
tx.add_atom(atom)
tx.add_edge(from_id, to_id, edge_type)
tx.update_pattern(pattern, delta)
tx.commit()
tx.abort()
```

#### PhaseMachine

Phase cycle controller.

```python
pm = PhaseMachine()
pm.transition(Phase.INGEST)
pm.can_mutate_state()  # False in IDLE, True otherwise
pm.get_phase_name()
pm.reset()
```

#### GoalRegistry

Track goal achievements.

```python
registry = GoalRegistry()
registry.register_goal("goal_1", target_value)
achieved = registry.check_goal("goal_1", current_value)
progress = registry.progress()
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest newton_tlm/tests/test_acid_newton.py -v

# Run specific test class
pytest newton_tlm/tests/test_acid_newton.py::TestAcidCompliance -v

# Run specific test
pytest newton_tlm/tests/test_acid_newton.py::TestNewtonCompliance::test_n1_determinism -v
```

### Test Coverage

- **ACID Tests**: 12 tests covering atomicity, consistency, isolation, durability
- **Newton Tests**: 13 tests covering all 7 Newton principles
- **Integration Tests**: 3 tests combining multiple components

## Design Philosophy

### Why Phase-Driven?

Traditional systems: "Do this, then do that"  
Newton TLM: "Follow the cycle, verify at each phase"

Phases enforce **bounded execution** and **verified transitions**.

### Why Immutable Atoms?

Mutable state is the root of many computational evils:
- Race conditions
- Unpredictable behavior
- Difficult debugging

Immutable atoms (frozen dataclasses) guarantee:
- No accidental mutations
- Thread-safe operations
- Perfect reproducibility

### Why Append-Only Ledger?

Traditional logs can be modified, deleted, or corrupted.

Newton's ledger:
- **Append-only**: Never modified after writing
- **Hash-chained**: Each entry links to previous via hash
- **Verifiable**: Tampering breaks the chain
- **Replayable**: Perfect state reconstruction

### Why 1==1?

This isn't just equality checking. It's the **fundamental law of verified computation**:

```
If current state matches goal state → proceed
If current state differs from goal → halt
```

This principle:
- Prevents incorrect execution
- Enables goal-directed computation
- Provides verification at every step

## Advanced Usage

### Custom Phase Handling

```python
from newton_tlm import PhaseMachine, Phase

pm = PhaseMachine()

# Manual phase control
try:
    pm.transition(Phase.INGEST)
    pm.transition(Phase.PARSE)
    # ... process ...
    pm.transition(Phase.CRYSTALLIZE)
except RuntimeError as e:
    print(f"Phase violation: {e}")
    pm.reset()
```

### Ledger Analysis

```python
tlm = NewtonTLM()

# Make changes
for i in range(10):
    tlm.ingest(f"data_{i}")

# Analyze ledger
for entry in tlm.ledger:
    print(f"Entry {entry.index}:")
    print(f"  Phase: {entry.phase}")
    print(f"  Atoms added: {len(entry.atoms_added)}")
    print(f"  Hash before: {entry.hash_before[:8]}...")
    print(f"  Hash after: {entry.hash_after[:8]}...")
```

### Snapshot Management

```python
from newton_tlm import SnapshotManager

manager = SnapshotManager(max_snapshots=50)

# Save snapshots
for state in states:
    snapshot = create_snapshot(state)
    manager.save_snapshot(snapshot)

# Retrieve
latest = manager.get_latest()
specific = manager.get_by_index(5)

# Statistics
print(f"Snapshots stored: {manager.count()}")
```

## Performance Considerations

### Memory Usage

- **Atoms**: O(n) where n = number of atoms
- **Edges**: O(e) where e = number of edges  
- **Ledger**: O(t) where t = number of transactions
- **Snapshots**: O(s × (n + e)) where s = number of snapshots

### Time Complexity

- **Ingest**: O(1) for atom creation + O(k) for k patterns
- **State hash**: O(n + e) for full state serialization
- **Transaction commit**: O(a + e + p) for a atoms, e edges, p patterns
- **Rollback**: O(n + e) for state restoration
- **Ledger replay**: O(t × (a + e + p)) for t transactions

### Optimization Tips

1. **Batch operations** in transactions rather than individual commits
2. **Limit snapshot frequency** to avoid memory bloat
3. **Prune old ledger entries** if full history not needed (non-standard)
4. **Use pattern deltas** efficiently (increment/decrement vs. recount)

## Troubleshooting

### Phase Transition Errors

```python
# Problem: RuntimeError on phase transition
# Solution: Follow phase order strictly

pm = PhaseMachine()
# ✗ Wrong
pm.transition(Phase.COMMIT)  # Can't skip from IDLE to COMMIT

# ✓ Correct
pm.transition(Phase.INGEST)
pm.transition(Phase.PARSE)
# ... follow full cycle
```

### Transaction Already in Progress

```python
# Problem: RuntimeError when beginning new transaction
# Solution: Commit or abort existing transaction

tlm = NewtonTLM()
tx1 = tlm.begin_transaction()
# tx2 = tlm.begin_transaction()  # ✗ Error!

tlm.commit_transaction()  # or tlm.abort_transaction()
tx2 = tlm.begin_transaction()  # ✓ Now works
```

### Ledger Integrity Failure

```python
# Problem: verify_integrity() returns False
# Cause: Hash chain broken (corruption or tampering)
# Solution: Restore from clean backup

tlm = NewtonTLM()
ledger_backup = load_clean_ledger()
tlm.replay_ledger(ledger_backup)
```

## Contributing

Newton TLM follows the Newton project conventions:

- Python 3.9+ features
- Type hints for all function signatures
- Dataclasses with `@dataclass` decorator
- ASCII art headers with `═` characters
- PEP 8 style guidelines
- Comprehensive docstrings

## License

Same as Newton Supercomputer:
- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

## References

### Theoretical Foundations

- **Phase-driven computation**: Inspired by finite state machines and dataflow architectures
- **Immutable atoms**: Functional programming principles (Haskell, Clojure)
- **Append-only ledgers**: Blockchain and distributed systems
- **1==1 invariant**: Fixed-point theory and goal-directed computation
- **Graph topology**: Network science and topological data analysis

### Related Newton Components

- **CDL (Constraint Definition Language)**: `core/cdl.py`
- **Logic Engine**: `core/logic.py`
- **Ledger**: `core/ledger.py`
- **Forge**: `core/forge.py`

## Version History

- **1.0.0** (2026-01-05): Initial release
  - Core TLM implementation
  - Phase machine with 0→9→0 cycle
  - Transaction system
  - Ledger with hash-chaining
  - Snapshot/restore/rollback
  - 1==1 invariant checking
  - Comprehensive test suite

---

**"1 == 1. The cloud is weather. We're building shelter."**
