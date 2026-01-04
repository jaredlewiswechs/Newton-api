# Newton: Unified Architecture Guide

**How All Components Work Together**

**January 4, 2026** | **Jared Nashon Lewis** | **Ada Computing Company**

---

## System Overview

Newton is a verification substrate where nine core modules compose into a unified constraint-first computing platform.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NEWTON SUPERCOMPUTER v6.0                            │
│                    ~53,750 lines of verified code                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    REVERSIBLE SHELL (PHONON)                     │   │
│  │  try↔untry  split↔join  lock↔unlock  take↔give  peek            │   │
│  │  open↔close  remember↔forget  say↔unsay                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │   CDL   │  │  LOGIC  │  │  FORGE  │  │ ROBUST  │  │GROUNDING│      │
│  │  3.0    │  │ ENGINE  │  │  (CPU)  │  │ (STATS) │  │ (FACTS) │      │
│  │ (LANG)  │  │ (CALC)  │  │         │  │         │  │         │      │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘      │
│       └────────────┴────────────┴────────────┴────────────┘            │
│                              │                                          │
│  ┌─────────┐  ┌─────────────┴─────────────┐  ┌─────────┐              │
│  │  VAULT  │  │          LEDGER           │  │ BRIDGE  │              │
│  │  (RAM)  │  │          (DISK)           │  │  (BUS)  │              │
│  │  AES-256│  │  Hash-chain + Merkle      │  │  PBFT   │              │
│  └─────────┘  └───────────────────────────┘  └─────────┘              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      GLASS BOX LAYER                             │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────────────────┐  │   │
│  │  │Policy Engine │  │ Negotiator │  │    Merkle Anchor       │  │   │
│  │  │(policy-code) │  │   (HITL)   │  │   (proof export)       │  │   │
│  │  └──────────────┘  └────────────┘  └────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CARTRIDGE SYSTEM                            │   │
│  │  Visual │ Sound │ Sequence │ Data │ Rosetta │ Document Vision   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                          ASK NEWTON                                     │
│                            /ask                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Nine Core Modules

### 1. CDL 3.0 (Constraint Definition Language)

**File**: `core/cdl.py` (~1,060 lines)
**Purpose**: The instruction set of Newton

CDL defines the syntax and semantics for expressing constraints.

#### Operators by Category

| Category | Operators |
|----------|-----------|
| **Comparison** | `eq`, `ne`, `lt`, `gt`, `le`, `ge` |
| **String** | `contains`, `matches` (regex) |
| **Set** | `in`, `not_in` |
| **Existence** | `exists`, `empty` |
| **Temporal** | `within`, `after`, `before` |
| **Aggregation** | `sum_lt`, `count_lt`, `avg_lt` (with window) |
| **Ratio** | `ratio_lt`, `ratio_le`, `ratio_undefined` |
| **Logic** | `and`, `or`, `not` composites |
| **Conditional** | `if/then/else` branching |

#### Seven Constraint Domains

| Domain | Purpose | Example Use |
|--------|---------|-------------|
| `financial` | Money, leverage, ratios | `debt/equity ≤ 3.0` |
| `temporal` | Time windows, deadlines | `count in 24h < 10` |
| `health` | Safety bounds, dosages | `temperature < 38.5°C` |
| `epistemic` | Confidence, certainty | `ground(claim, 0.95)` |
| `identity` | Permissions, scopes | `role in ["admin"]` |
| `communication` | Content safety | `!contains("harmful")` |
| `custom` | User-defined | Extensible framework |

#### CDL Example

```python
from core.cdl import AtomicConstraint, CompositeConstraint, Operator

# Single constraint
no_overdraft = AtomicConstraint(
    field="balance",
    operator=Operator.GE,
    value=0,
    domain="financial"
)

# Composite constraint
safe_withdrawal = CompositeConstraint(
    operator=Operator.AND,
    constraints=[
        AtomicConstraint("balance", Operator.GE, 0),
        AtomicConstraint("withdrawal", Operator.LE, 1000),
        AtomicConstraint("daily_total", Operator.SUM_LT, 5000, window="24h")
    ]
)
```

---

### 2. Logic Engine (Verified Computation)

**File**: `core/logic.py` (~1,261 lines)
**Purpose**: Turing-complete computation within verifiable bounds

The Logic Engine can compute anything El Capitan can—just verified.

#### Operator Categories

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

#### Bounded Execution

```python
ExecutionBounds(
    max_iterations=10000,       # No infinite loops
    max_recursion_depth=100,    # No stack overflow
    max_operations=1000000,     # No runaway compute
    timeout_seconds=30.0        # No endless waits
)
```

**Guarantee**: Every computation terminates. HaltChecker validates before execution.

---

### 3. Forge (Verification CPU)

**File**: `core/forge.py` (~737 lines)
**Purpose**: The central processing unit of Newton

Forge orchestrates all verification:

| Capability | Implementation |
|------------|----------------|
| **Parallel evaluation** | ThreadPoolExecutor |
| **Content safety** | Pattern matching |
| **Signal verification** | Structured validation |
| **Sub-millisecond latency** | <1ms typical |
| **Result caching** | SHA-256 keyed, 5-min TTL |

#### The Forge Cycle

```python
# Traditional CPU: fetch → decode → execute → writeback
# Forge cycle: constraint → project → verify → commit/rollback → proof

def forge_verify(constraint, state):
    # 1. Project what state would be after operation
    projected_state = project(state, operation)

    # 2. Verify constraint against projected state
    result = cdl_evaluate(constraint, projected_state)

    # 3. If valid, commit; otherwise rollback
    if result.passed:
        commit(projected_state)
        return proof(constraint, state, result)
    else:
        rollback()
        raise ConstraintViolation(result)
```

#### Benchmarks

| Operation | Speed | Time |
|-----------|-------|------|
| CDL Constraint Evaluation | 249,697 ops/sec | 4.0 μs |
| Content Safety (Pattern) | 201,056 ops/sec | 5.0 μs |
| f/g Ratio Calculation | 2,131,593 ops/sec | 469 ns |
| Full Verification Pipeline | 99,768 ops/sec | 10.0 μs |

---

### 4. Vault (Encrypted Storage)

**File**: `core/vault.py` (~538 lines)
**Purpose**: Secure, identity-derived storage (RAM equivalent)

| Feature | Implementation |
|---------|----------------|
| **Encryption** | AES-256-GCM with authenticated data |
| **Key Derivation** | PBKDF2 (100,000 iterations) |
| **Identity Binding** | Keys derived from identity |
| **Type Preservation** | Maintains data types across encryption |

#### Usage

```python
from core.vault import Vault

vault = Vault(master_key="derived-from-identity")

# Store encrypted
vault.store("user:123:balance", 1000.00)

# Retrieve (decrypted automatically)
balance = vault.retrieve("user:123:balance")

# Data type preserved
assert isinstance(balance, float)
```

---

### 5. Ledger (Immutable History)

**File**: `core/ledger.py` (~576 lines)
**Purpose**: Append-only audit trail (disk equivalent)

| Feature | Implementation |
|---------|----------------|
| **Hash Chaining** | Each entry references previous |
| **Merkle Tree** | O(log n) membership proofs |
| **Verification Certificates** | Exportable proof documents |
| **Complete Audit Trail** | Every operation logged |

#### Entry Structure

```python
LedgerEntry(
    index=42,
    timestamp="2026-01-04T12:00:00Z",
    operation="verify_constraint",
    data={"constraint": "balance >= 0", "result": True},
    prev_hash="abc123...",
    hash="def456...",
    merkle_root="ghi789..."
)
```

#### Merkle Proofs

```python
# Generate proof for any entry
proof = ledger.generate_merkle_proof(entry_index=42)

# Verify independently (no trust required)
is_valid = verify_merkle_proof(
    entry_hash=proof.entry_hash,
    root=proof.merkle_root,
    path=proof.sibling_hashes
)
```

---

### 6. Bridge (Distributed Consensus)

**File**: `core/bridge.py` (~542 lines)
**Purpose**: PBFT-inspired consensus for distributed verification

| Feature | Implementation |
|---------|----------------|
| **Node Identity** | ECDSA key pairs |
| **Byzantine Tolerance** | f = (n-1)/3 faulty nodes |
| **Consensus Rounds** | prepare → commit → finalize |
| **View Changes** | Leader rotation on failure |

#### Consensus Protocol

```
Node 0: "Constraint X passes" (PREPARE)
Node 1: "Constraint X passes" (PREPARE)
Node 2: "Constraint X passes" (PREPARE)
  ↓
All agree → COMMIT phase
  ↓
2/3+ commits received → FINALIZE
  ↓
Result: Verified with Byzantine fault tolerance
```

#### Usage

```python
from core.bridge import Bridge, Node

# Create network
nodes = [Node(f"node-{i}") for i in range(3)]
bridge = Bridge(nodes)

# Reach consensus
result = await bridge.reach_consensus(
    operation="verify_constraint",
    data=constraint_data
)

if result.consensus_reached:
    # Verified by multiple independent nodes
    verified_result = result.value
```

---

### 7. Robust (Adversarial Statistics)

**File**: `core/robust.py` (~597 lines)
**Purpose**: Statistics designed to resist manipulation

| Feature | Purpose |
|---------|---------|
| **MAD over Mean** | Median Absolute Deviation resists outliers |
| **Locked Baselines** | Immutable reference points |
| **Source Tracking** | Provenance for all data |
| **Temporal Decay** | Recent data weighted appropriately |
| **Attack Detection** | Identifies manipulation attempts |

#### Why MAD?

```
Dataset: [10, 11, 12, 13, 14, 1000000]

Mean: 166,676.67  ← Destroyed by outlier
Median: 12.5      ← Robust to outlier
MAD: 1.5          ← Measures actual spread

Newton uses MAD for all statistical operations
```

#### Usage

```python
from core.robust import RobustStats

stats = RobustStats()
stats.add_baseline("normal_temp", values=[36.5, 36.8, 37.0, 36.7])

# Check if new value is anomalous
is_anomaly = stats.is_anomaly(
    value=42.0,
    baseline="normal_temp",
    threshold=3.0  # 3 MAD from median
)  # True - significantly anomalous
```

---

### 8. Grounding (Reality Anchoring)

**File**: `core/grounding.py` (~214 lines)
**Purpose**: Verify claims against external evidence

| Feature | Purpose |
|---------|---------|
| **Source Tiers** | Government, Academic, Industry, User |
| **Confidence Levels** | 0.0 to 1.0 certainty |
| **Claim Verification** | Check facts against authoritative sources |
| **Provenance Tracking** | Know where facts came from |

#### Usage

```python
from core.grounding import GroundingEngine

grounding = GroundingEngine()

# Verify a claim
result = grounding.verify_claim(
    claim="Water boils at 100°C at sea level",
    required_confidence=0.95,
    source_tier="Academic"
)

if result.verified:
    # Claim is grounded with sources
    print(f"Verified by: {result.sources}")
else:
    # Claim could not be verified
    print(f"Unverified: {result.reason}")
```

---

### 9. Glass Box (Transparency Layer)

**Files**: `core/policy_engine.py`, `core/negotiator.py`, `core/merkle_anchor.py`, `core/vault_client.py`
**Purpose**: Policy enforcement, human oversight, and proof export

#### 9.1 Policy Engine (Policy-as-Code)

```python
from core.policy_engine import Policy, PolicyType, PolicyAction

# Define policy
no_large_withdrawals = Policy(
    name="no_large_withdrawals",
    type=PolicyType.SIZE_LIMIT,
    action=PolicyAction.REQUIRE_APPROVAL,
    condition=lambda ctx: ctx.amount > 10000,
    message="Withdrawals over $10,000 require approval"
)

# Apply to operations
engine.add_policy(no_large_withdrawals)
```

#### 9.2 Negotiator (Human-in-the-Loop)

```python
from core.negotiator import Negotiator, ApprovalRequest

negotiator = Negotiator()

# Request human approval
request = ApprovalRequest(
    operation="large_withdrawal",
    amount=50000,
    priority="HIGH",
    ttl_hours=1
)

approval = await negotiator.request_approval(request)

if approval.granted:
    proceed_with_operation()
else:
    reject_operation(approval.reason)
```

#### 9.3 Merkle Anchor (Proof Export)

```python
from core.merkle_anchor import MerkleAnchorScheduler

scheduler = MerkleAnchorScheduler(interval_minutes=5)

# Create anchor manually
anchor = scheduler.create_anchor()

# Export proof for any entry
certificate = scheduler.export_certificate(entry_index=42)

# Certificate can be verified externally
# No trust in Newton required
```

---

## The Cartridge System

Cartridges are domain-specific media generators that output verified specifications.

| Cartridge | Purpose | Output |
|-----------|---------|--------|
| **Visual** | Graphics, charts | SVG/PNG specs |
| **Sound** | Audio generation | Audio specs |
| **Sequence** | Animation | Frame sequences |
| **Data** | Reports, tables | Structured data |
| **Rosetta** | Code generation | Source code |
| **Document Vision** | Receipt/expense processing | Structured extraction |

#### Cartridge Architecture

```
User Intent: "Make me a chart of sales data"
  ↓
Constraint Extraction:
  - "chart" → Visual cartridge
  - "sales data" → data_source = sales
  - Implicit: no misleading visualizations
  ↓
Cartridge Constraints Check:
  - width: 800 (max 4096)     ✓
  - height: 600 (max 4096)    ✓
  - elements: 50 (max 100)    ✓
  - no misleading data        ✓
  ↓
Specification Generation:
  {
    "type": "bar_chart",
    "data_source": "sales",
    "style": "minimal",
    "verified": true,
    "merkle_root": "a3f8..."
  }
  ↓
Output: Verified specification, not hallucination
```

---

## Data Flow Through the System

### Complete Request Flow

```
1. INPUT: Natural language or API call
   │
   ↓
2. CONSTRAINT EXTRACTION (Voice Interface / Constraint Extractor)
   │ Extract formal constraints from fuzzy intent
   ↓
3. CDL PARSING
   │ Parse constraints into CDL structures
   ↓
4. POLICY CHECK (Glass Box - Policy Engine)
   │ Pre-operation policy validation
   ↓
5. FORGE VERIFICATION
   │ ├── State projection
   │ ├── Constraint evaluation (parallel)
   │ └── f/g ratio check
   ↓
6. EXECUTION (if constraints satisfied)
   │ ├── Logic Engine computation
   │ ├── Vault read/write
   │ └── Bridge consensus (if distributed)
   ↓
7. LEDGER RECORDING
   │ ├── Hash-chain append
   │ └── Merkle tree update
   ↓
8. POST-VALIDATION (Glass Box - Policy Engine)
   │ Post-operation checks
   ↓
9. PROOF GENERATION
   │ Merkle proof for verification
   ↓
10. OUTPUT: Result + Cryptographic Proof
```

---

## Module Interdependencies

```
                    ┌──────────────┐
                    │   CDL 3.0    │
                    │  (language)  │
                    └──────┬───────┘
                           │ defines constraints
                           ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    LOGIC     │←──→│    FORGE     │←──→│   ROBUST     │
│   ENGINE     │    │    (CPU)     │    │   (stats)    │
│  (compute)   │    │              │    │              │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │ records
                           ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    VAULT     │←──→│   LEDGER     │←──→│   BRIDGE     │
│  (storage)   │    │  (history)   │    │ (consensus)  │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ↓
                    ┌──────────────┐
                    │  GLASS BOX   │
                    │(transparency)│
                    └──────┬───────┘
                           │
                           ↓
                    ┌──────────────┐
                    │  GROUNDING   │
                    │  (reality)   │
                    └──────────────┘
```

### Dependency Rules

| Module | Depends On | Depended By |
|--------|------------|-------------|
| CDL | None | Forge, Logic Engine |
| Logic Engine | CDL | Forge, Cartridges |
| Forge | CDL, Logic Engine, Robust | All verification operations |
| Vault | None | Ledger, Glass Box |
| Ledger | Vault | Forge, Glass Box, Bridge |
| Bridge | Ledger | Distributed verification |
| Robust | None | Forge, Grounding |
| Grounding | Robust | Glass Box, Cartridges |
| Glass Box | Ledger, Vault, Grounding | Top-level API |

---

## File Organization

```
Newton-api/
├── newton_supercomputer.py    # Main API server (3,021 lines)
├── core/
│   ├── cdl.py                 # Constraint Definition Language (1,060 lines)
│   ├── logic.py               # Verified computation engine (1,261 lines)
│   ├── forge.py               # Verification CPU (737 lines)
│   ├── vault.py               # Encrypted storage (538 lines)
│   ├── ledger.py              # Immutable history (576 lines)
│   ├── bridge.py              # Distributed consensus (542 lines)
│   ├── robust.py              # Adversarial statistics (597 lines)
│   ├── grounding.py           # Fact verification (214 lines)
│   ├── shell.py               # Reversible shell (941 lines)
│   ├── cartridges.py          # Media specifications (1,727 lines)
│   ├── voice_interface.py     # MOAD voice input (1,649 lines)
│   ├── policy_engine.py       # Policy-as-code (354 lines)
│   ├── negotiator.py          # Human-in-the-loop (361 lines)
│   ├── merkle_anchor.py       # Proof export (340 lines)
│   └── vault_client.py        # Provenance logging (132 lines)
├── tinytalk_py/
│   ├── core.py                # tinyTalk interpreter
│   ├── education.py           # Education cartridge (1,703 lines)
│   ├── teks_database.py       # Texas curriculum (1,334 lines)
│   ├── teachers_aide_db.py    # Teacher tools (1,115 lines)
│   └── interface_builder.py   # UI generation (996 lines)
├── swift/
│   └── Ada.swift              # iOS client (983 lines)
├── tests/
│   ├── test_tinytalk.py       # Language tests (1,615 lines)
│   ├── test_integration.py    # Integration tests (942 lines)
│   ├── test_newton_chess.py   # Chess verification tests (1,213 lines)
│   └── test_*.py              # Additional tests (~5,000 lines)
└── docs/
    └── foundation/            # Foundation documentation
```

---

## Summary: The Unified System

Newton is nine modules composed into a verification substrate:

1. **CDL** defines what constraints look like
2. **Logic Engine** computes anything, verified
3. **Forge** checks constraints before execution
4. **Vault** stores data encrypted
5. **Ledger** records everything immutably
6. **Bridge** verifies across multiple nodes
7. **Robust** resists statistical manipulation
8. **Grounding** anchors to reality
9. **Glass Box** ensures transparency

**The key insight**: These modules don't just exist side by side. They COMPOSE. Removing any one breaks the guarantees of the whole system.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   The constraint IS the instruction.                        │
│   The verification IS the computation.                      │
│                                                             │
│   1 == 1 → execute                                          │
│   1 != 1 → halt                                             │
│                                                             │
│   This isn't a feature. It's the architecture.              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

© 2025-2026 Jared Nashon Lewis · Ada Computing Company · Houston, Texas
