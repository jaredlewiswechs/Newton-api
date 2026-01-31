# Newton Architecture Guide

**Visual guide to understanding Newton's structure and components.**

```
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🍎 Newton Architecture                                     │
│                                                              │
│   Understanding the verified computation system              │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│  "Withdraw $50 from account with $100 balance"              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    NEWTON API (FastAPI)                      │
│                  newton_supercomputer.py                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │   CDL   │    │  Forge  │    │  Vault  │
    │Constraint│   │Verify   │    │Encrypt  │
    │Language │    │Engine   │    │Storage  │
    └─────────┘    └─────────┘    └─────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                    ┌─────────┐
                    │ Ledger  │
                    │Immutable│
                    │ Audit   │
                    └─────────┘
                          │
                          ▼
                    ┌─────────┐
                    │ Result  │
                    │Verified │
                    │  True   │
                    └─────────┘
```

---

## Component Overview

### 1. Newton API Server (`newton_supercomputer.py`)

The main FastAPI server that exposes REST endpoints.

**Key Endpoints:**
- `/verify` - Verify content against constraints
- `/calculate` - Perform verified computation
- `/ask` - Full verification pipeline
- `/constraint` - Evaluate CDL constraints
- `/vault/*` - Encrypted storage operations
- `/ledger/*` - Audit trail access

**Technology:** Python 3.9+, FastAPI, Uvicorn

### 2. Core Engines (`core/`)

The verification and computation engines.

```
core/
├── cdl.py          # Constraint Definition Language
├── logic.py        # Verified computation engine
├── forge.py        # Verification engine
├── vault.py        # Encrypted storage (AES-256-GCM)
├── ledger.py       # Immutable audit trail
├── bridge.py       # Distributed consensus (PBFT)
├── robust.py       # Adversarial statistics (MAD)
└── grounding.py    # Evidence grounding
```

#### CDL (Constraint Definition Language)

Evaluates constraints expressed as JSON operators.

**Example:**
```json
{
  "op": "above",
  "args": ["balance", 0]
}
```

Returns `true` or `false`.

#### Logic Engine

Executes verified computation with guaranteed termination.

**Bounds:**
- Max iterations: 10,000
- Max recursion: 100
- Max operations: 1,000,000
- Timeout: 30 seconds

**Example:**
```json
{
  "op": "+",
  "args": [2, 3]
}
```

Returns `5` with proof of correctness.

#### Forge

The verification engine. Evaluates constraints in <1ms.

**Process:**
1. Parse constraint
2. Check bounds
3. Verify determinism
4. Return verified result

#### Vault

Encrypted storage with identity-derived keys.

**Features:**
- AES-256-GCM encryption
- Identity-based key derivation
- Secure key management
- Automatic encryption/decryption

#### Ledger

Immutable audit trail with Merkle proofs.

**Features:**
- Hash-chained entries
- Merkle tree for proofs
- Export verification certificates
- Cryptographic guarantees

#### Bridge

Distributed consensus using PBFT (Practical Byzantine Fault Tolerance).

**Features:**
- Byzantine fault tolerant
- 3f+1 node requirement
- Leader election
- State synchronization

#### Robust

Adversarial statistics using MAD (Median Absolute Deviation) instead of mean.

**Why MAD?**
- Resistant to outliers
- Deterministic
- No assumptions about distribution

### 3. TinyTalk Language

The constraint-first programming language.

```
tinytalk_py/
├── __init__.py     # Main SDK
├── blueprint.py    # Blueprint class system
├── matter.py       # Physical types (Money, Celsius, etc.)
└── decorators.py   # @law, @forge decorators
```

**Philosophy:**
- Define what CANNOT happen (laws)
- Define what CAN happen (forges)
- Everything else is forbidden

**Example:**
```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Account(Blueprint):
    balance = field(float, default=1000.0)
    
    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)  # Cannot exist
    
    @forge
    def withdraw(self, amount):
        self.balance -= amount
        return f"Withdrew ${amount}"
```

### 4. Newton Core (Rust)

High-performance constraint projection engine.

**Location:** `newton_core/` (Rust crate)

**Features:**
- Dykstra's projection algorithm
- Sub-millisecond performance
- Convex constraint handling
- Deterministic output

**Use Case:** Aid-a (AI-assisted design with constraints)

### 5. Newton TLM (Transaction Lifecycle Manager)

ACID-compliant transaction system.

**Location:** `newton_tlm/`

**Features:**
- Atomicity: All or nothing
- Consistency: Laws enforced
- Isolation: Snapshots for rollback
- Durability: Ledger persistence

**Example:**
```python
# Begin transaction
tlm.begin(instance)

# Make changes
instance.balance -= 100

# Constraint violation? → Rollback
# Everything OK? → Commit
tlm.commit(instance)
```

---

## Data Flow Example

Let's trace a complete request through Newton.

### Request: Withdraw $50 from account

```
1. User sends POST to /verify
   {
     "blueprint": "Account",
     "action": "withdraw",
     "args": [50]
   }

2. Newton API receives request
   → Parse JSON
   → Validate structure

3. Load Blueprint definition
   Account:
     - balance = 1000
     - law: no_overdraft (balance >= 0)

4. CDL evaluates constraints
   Current: balance = 1000
   After:   balance = 1000 - 50 = 950
   
   Check: 950 >= 0? YES ✓

5. Forge executes action
   → Begin transaction (TLM)
   → Update balance: 1000 → 950
   → Check laws: PASS ✓
   → Commit transaction

6. Ledger records event
   {
     "action": "withdraw",
     "amount": 50,
     "old_balance": 1000,
     "new_balance": 950,
     "timestamp": "2026-01-31T18:00:00Z",
     "verified": true
   }

7. Response sent to user
   {
     "success": true,
     "verified": true,
     "result": "Withdrew $50",
     "merkle_root": "abc123...",
     "elapsed_us": 1234
   }
```

---

## The Three Layers

Newton operates on a three-layer architecture:

```
╭─────────────────────────────────────────────────────────────╮
│  LAYER 2: APPLICATION                                       │
│  Your specific use case                                     │
│  (BankAccount, Thermostat, Game, etc.)                      │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: EXECUTIVE                                         │
│  State (fields) + Actions (forges)                          │
│  What CAN happen                                            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: GOVERNANCE                                        │
│  Constraints (laws)                                         │
│  What CANNOT happen                                         │
│  The physics of your world                                  │
╰─────────────────────────────────────────────────────────────╯
```

**Example:**

```python
# LAYER 0: GOVERNANCE (Laws)
@law
def no_overdraft(self):
    when(self.balance < 0, finfr)  # Forbidden state

# LAYER 1: EXECUTIVE (State + Actions)
balance = field(float, default=1000.0)

@forge
def withdraw(self, amount):
    self.balance -= amount  # Action

# LAYER 2: APPLICATION (Usage)
account = Account()
account.withdraw(50)  # Your specific use
```

**Why this matters:**
- Layer 0 is **immutable** (laws don't change)
- Layer 1 is **mutable** (state changes)
- Layer 2 is **your code** (application logic)

---

## Key Guarantees

Newton provides mathematical guarantees:

### 1. Determinism

Same input → same output. Always. Bitwise identical.

**Implementation:**
- No randomness in computation
- No system clock in verification
- No network calls during computation
- All operations are pure functions

### 2. Termination

All computations halt within bounded time.

**Implementation:**
- Max iteration count
- Max recursion depth
- Max operation count
- Timeout enforcement

### 3. Auditability

Every operation is logged in immutable ledger.

**Implementation:**
- Hash-chained entries
- Merkle tree for proofs
- Cryptographic signatures
- Export certificates

### 4. Verification Before Execution

Constraints checked before state changes.

**Implementation:**
- Transaction snapshots (TLM)
- Law evaluation before commit
- Automatic rollback on violation
- No invalid states ever exist

---

## Performance Characteristics

### API Latency

- **Median:** 2.31ms
- **Internal processing:** 46.5μs
- **Throughput:** 605 req/sec
- **vs GPT-4:** 563x faster
- **vs Stripe:** 638x faster

### Constraint Evaluation

- **CDL parsing:** <100μs
- **Forge verification:** <1ms
- **Ledger append:** <50μs
- **Total overhead:** <2ms

### Memory Usage

- **Per request:** ~1-10 KB
- **Ledger entry:** ~200 bytes
- **TLM snapshot:** Size of state
- **Total per instance:** <1 MB

---

## Deployment Options

### 1. Local Development

```bash
python newton_supercomputer.py
# Runs on http://localhost:8000
```

**Use for:**
- Development
- Testing
- Learning
- Prototyping

### 2. Docker Container

```bash
docker build -t newton .
docker run -p 8000:8000 newton
```

**Use for:**
- Production deployments
- Cloud services
- Kubernetes
- Microservices

### 3. Render.com (Managed)

```bash
# Uses render.yaml configuration
# Auto-deploys from GitHub
# Includes health checks
```

**Use for:**
- Quick deployment
- No DevOps needed
- Auto-scaling
- Managed infrastructure

### 4. Distributed Cluster (Bridge)

```bash
# 3f+1 nodes for Byzantine tolerance
# PBFT consensus
# Shared ledger
```

**Use for:**
- Mission-critical systems
- High availability
- Byzantine fault tolerance
- Regulatory compliance

---

## Security Architecture

### Encryption (Vault)

- **Algorithm:** AES-256-GCM
- **Key derivation:** Identity-based
- **Authenticated:** Yes (GCM mode)
- **Key rotation:** Supported

### Authentication

- **API keys:** Bearer tokens
- **Rate limiting:** Per-key limits
- **Request validation:** Pydantic schemas
- **CORS:** Configurable

### Audit Trail (Ledger)

- **Hash algorithm:** SHA-256
- **Chain integrity:** Merkle tree
- **Tamper detection:** Automatic
- **Export format:** JSON certificates

### Input Validation

- **Schema validation:** Pydantic
- **Constraint checking:** CDL
- **Harm detection:** Pattern matching
- **Grounding:** External evidence

---

## Extending Newton

### Add a New Endpoint

```python
# In newton_supercomputer.py

@app.post("/my_endpoint")
def my_endpoint(request: MyRequest):
    # Your logic here
    return {
        "success": True,
        "data": result,
        "verified": True
    }
```

### Add a New Constraint Operator

```python
# In core/cdl.py

class Operator(str, Enum):
    # ... existing operators ...
    MY_OP = "my_op"

# In CDLEvaluator._evaluate_atomic()
elif op == Operator.MY_OP:
    # Your logic here
    return left_val [your_operation] right_val
```

### Add a New Blueprint

```python
# In tinytalk_py/__init__.py or your own file

class MyBlueprint(Blueprint):
    field1 = field(str)
    field2 = field(int, default=0)
    
    @law
    def my_law(self):
        when(self.field2 < 0, finfr)
    
    @forge
    def my_action(self):
        self.field2 += 1
```

---

## Monitoring and Observability

### Health Check

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "ok",
  "version": "1.3.0",
  "uptime_seconds": 123.45,
  "constraints_verified": 1000,
  "ledger_size": 500
}
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

Returns:
- Request count
- Average latency
- Verification rate
- Error rate
- Ledger size

### Logs

```bash
# Watch logs
tail -f logs/newton.log

# Search logs
grep "ERROR" logs/newton.log
```

---

## Best Practices

### 1. Design Laws First

Before writing any actions, define your constraints.

**Bad:**
```python
class Account(Blueprint):
    balance = field(float)
    
    @forge
    def withdraw(self, amount):
        if self.balance - amount < 0:  # Check in action
            raise ValueError("Overdraft")
        self.balance -= amount
```

**Good:**
```python
class Account(Blueprint):
    balance = field(float)
    
    @law  # Constraint first
    def no_overdraft(self):
        when(self.balance < 0, finfr)
    
    @forge  # Action is simple
    def withdraw(self, amount):
        self.balance -= amount
```

### 2. Use Matter Types

Don't use raw numbers. Use typed values.

**Bad:**
```python
temperature = field(float)  # Celsius? Fahrenheit?
```

**Good:**
```python
from tinytalk_py import Celsius
temperature = field(Celsius)  # Clear units
```

### 3. Test Constraints

Write tests that verify laws are enforced.

```python
def test_overdraft_prevented():
    account = Account(balance=100)
    
    with pytest.raises(LawViolation):
        account.withdraw(150)  # Should be blocked
    
    assert account.balance == 100  # Unchanged
```

### 4. Keep Forges Simple

Actions should be simple state updates. Let laws handle validation.

### 5. Use TLM for Complex Operations

For multi-step operations, use TLM for atomicity.

```python
tlm = NewtonTLM()

tlm.begin(account1)
tlm.begin(account2)

try:
    # Transfer money
    account1.balance -= 100
    account2.balance += 100
    
    # Both succeed or both rollback
    tlm.commit(account1)
    tlm.commit(account2)
except LawViolation:
    tlm.rollback(account1)
    tlm.rollback(account2)
```

---

## Common Patterns

### Pattern 1: State Machine

```python
class Order(Blueprint):
    status = field(str, default="pending")
    
    @law
    def valid_transitions(self):
        # pending → confirmed → shipped → delivered
        valid = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": []
        }
        # Enforce state machine
```

### Pattern 2: Rate Limiting

```python
class APIKey(Blueprint):
    requests_today = field(int, default=0)
    last_reset = field(datetime)
    
    @law
    def rate_limit(self):
        when(self.requests_today > 1000, finfr)
    
    @forge
    def use(self):
        self.requests_today += 1
```

### Pattern 3: Resource Pool

```python
class ConnectionPool(Blueprint):
    active = field(int, default=0)
    max_connections = field(int, default=100)
    
    @law
    def no_overflow(self):
        when(self.active > self.max_connections, finfr)
    
    @forge
    def acquire(self):
        self.active += 1
    
    @forge
    def release(self):
        self.active -= 1
```

---

## Learn More

| Resource | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Complete tutorial |
| [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) | Full language reference |
| [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md) | Philosophy and design |
| [WHITEPAPER.md](WHITEPAPER.md) | Technical architecture |

---

**The constraint IS the instruction. The verification IS the computation.**

© 2025-2026 Jared Nashon Lewis · Newton · tinyTalk · Ada Computing Company
