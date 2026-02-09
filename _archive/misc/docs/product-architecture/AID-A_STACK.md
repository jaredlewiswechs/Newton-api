# aid-a Product Stack Architecture
## "The Chip" and "The System"

---

## Steve's Framing

*"Newton is the chip. aid-a is the system-on-chip. Newton OS is the operating system. Each layer trusts the one below it absolutely."*

---

## The Vertical Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      NEWTON OS                                 ║  │
│  ║         Every syscall verified before execution               ║  │
│  ║         malloc, fopen, exec, socket → Newton first           ║  │
│  ╚═══════════════════════════════════════════════════════════════╝  │
│                                │                                    │
│                                ▼                                    │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      CONSUMER APPS                            ║  │
│  ╟───────────────┬───────────────┬───────────────┬───────────────╢  │
│  ║   Spotlight   │   Teacher's   │    parcRI     │   Canvas      ║  │
│  ║   Replacement │     Aide      │   Research    │  Diagramming  ║  │
│  ╚═══════════════╧═══════════════╧═══════════════╧═══════════════╝  │
│                                │                                    │
│                                ▼                                    │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      aid-a LAYER                              ║  │
│  ║          Upload → Claude → Newton → Master Object            ║  │
│  ╟───────────────────────────────────────────────────────────────╢  │
│  ║   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   ║  │
│  ║   │  Parse  │ →  │Structure│ →  │ Verify  │ →  │  Emit   │   ║  │
│  ║   │  Input  │    │ Claude  │    │ Newton  │    │ Object  │   ║  │
│  ║   └─────────┘    └─────────┘    └─────────┘    └─────────┘   ║  │
│  ╚═══════════════════════════════════════════════════════════════╝  │
│                                │                                    │
│                                ▼                                    │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      NEWTON API                               ║  │
│  ║          30+ endpoints, sub-millisecond verification         ║  │
│  ╟───────────────────────────────────────────────────────────────╢  │
│  ║  /verify  /constraint  /ground  /vault  /ledger  /glass-box  ║  │
│  ╚═══════════════════════════════════════════════════════════════╝  │
│                                │                                    │
│                                ▼                                    │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      NEWTON CORE                              ║  │
│  ║              The verification engine ("The Chip")            ║  │
│  ╟───────────┬───────────┬───────────┬───────────┬───────────────╢  │
│  ║   CDL     │  Logic    │  Forge    │  Vault    │  Ledger      ║  │
│  ║ Language  │  Engine   │  Verify   │  Encrypt  │  Record      ║  │
│  ╟───────────┼───────────┼───────────┼───────────┼───────────────╢  │
│  ║  Bridge   │  Robust   │ Grounding │  Policy   │ Negotiator   ║  │
│  ║ Distribute│  Stats    │  Facts    │  Rules    │  HITL        ║  │
│  ╚═══════════╧═══════════╧═══════════╧═══════════╧═══════════════╝  │
│                                │                                    │
│                                ▼                                    │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║                      tinyTalk / LAWS                          ║  │
│  ║            Purely declarative constraint language            ║  │
│  ║            "Vault walls where movement is impossible"        ║  │
│  ╚═══════════════════════════════════════════════════════════════╝  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Layer 0: tinyTalk / Laws
**Role**: Define what CANNOT happen
**Language**: Purely declarative
**Execution**: None (laws don't execute, they constrain)

```python
law no_overdraft:
    when withdrawal > balance:
        finfr  # "fin infinitive restriction" = forbidden state

law leverage_limit:
    when debt / equity > 3.0:
        finfr
```

Laws are the bedrock. Everything above exists to enforce them.

---

### Layer 1: Newton Core ("The Chip")
**Role**: Enforce laws, verify state, prove correctness
**Execution**: Sub-millisecond constraint checking
**Guarantees**: Deterministic, reversible, auditable

| Module | Metaphor | Function |
|--------|----------|----------|
| CDL | Vocabulary | Constraint Definition Language |
| Logic | Calculator | Verified computation |
| Forge | CPU | Verification execution |
| Vault | RAM | Encrypted working memory |
| Ledger | Disk | Immutable history |
| Bridge | Network bus | Distributed consensus |
| Robust | Immune system | Adversarial resistance |
| Grounding | Fact-checker | External verification |
| Policy | Rulebook | Governance policies |
| Negotiator | Human liaison | Approval workflows |

---

### Layer 2: Newton API
**Role**: Expose Newton capabilities over HTTP
**Execution**: RESTful endpoints
**Guarantees**: Every response includes verification proof

Key endpoints:
```
POST /verify          # Full verification pipeline
POST /constraint      # CDL evaluation
POST /ground          # Fact verification
GET  /glass-box/{id}  # Full transparency

POST /vault/store     # Encrypted storage
GET  /vault/retrieve  # Encrypted retrieval

GET  /ledger          # History
GET  /ledger/{index}  # Entry with proof

GET  /merkle/proof/{index}  # Cryptographic proof
```

---

### Layer 3: aid-a Layer
**Role**: Translate human intent to verified objects
**Execution**: The 5-minute workflow
**Guarantees**: Every output is a Master Object

```
┌─────────────────────────────────────────────────────────────┐
│                    aid-a PIPELINE                            │
│                                                              │
│  INPUT              CLAUDE              NEWTON               │
│  (messy)            (structure)         (verify)            │
│                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Voice    │      │ Parse &  │      │ Check    │          │
│  │ memo     │ ───▶ │ extract  │ ───▶ │ claims   │          │
│  │ 2:43     │      │ entities │      │ against  │          │
│  └──────────┘      └──────────┘      │ reality  │          │
│                                       └──────────┘          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Photo of │      │ OCR &    │      │ Verify   │          │
│  │ receipt  │ ───▶ │ extract  │ ───▶ │ amounts  │          │
│  │          │      │ amounts  │      │ balance  │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Text     │      │ Structure│      │ Validate │          │
│  │ notes    │ ───▶ │ into     │ ───▶ │ against  │          │
│  │ "..."    │      │ schema   │      │ CDL      │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│                                                              │
│                                       ┌──────────┐          │
│                                       │  MASTER  │          │
│                            OUTPUT ──▶ │  OBJECT  │          │
│                                       │  (1≡1)   │          │
│                                       └──────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Layer 4: Consumer Apps
**Role**: Domain-specific interfaces to aid-a
**Execution**: Native apps (iOS, macOS, web)
**Guarantees**: Inherit all Newton guarantees

| App | Domain | Key Feature |
|-----|--------|-------------|
| **Spotlight Replacement** | Local search | Verified answers, not just results |
| **Teacher's Aide** | Education | TEKS-aligned, differentiated instruction |
| **parcRI** | Research | Verified claims, grounded sources |
| **Canvas** | Diagramming | Visual constraint builder |

---

### Layer 5: Newton OS
**Role**: Operating system with verification at the kernel
**Execution**: Every syscall routed through Newton
**Guarantees**: Invalid states cannot exist at any level

```
Traditional OS:
  App → syscall → Kernel → Hardware
  (hope nothing crashes)

Newton OS:
  App → syscall → Newton → Kernel → Hardware
                    ↑
               Verify first,
               execute only if valid
```

---

## Cross-Cutting Concerns

### Glass Box (Transparency)

Spans all layers. At any point, you can see:
- What constraints apply
- History of verifications
- Cryptographic proofs
- Current f/g ratio

```
┌─────────────────────────────────────────────────────────────┐
│  GLASS BOX VIEW                                             │
│  ═══════════════                                            │
│                                                              │
│  Object: account_123                                         │
│  Created: 2024-01-03 10:42:15 UTC                           │
│                                                              │
│  CURRENT STATE                 f/g INDICATOR                │
│  ┌───────────────────────┐    ┌─────────────┐               │
│  │ balance:  $4,523.00   │    │             │               │
│  │ pending:  $  250.00   │    │    ●        │  0.27         │
│  │ liab:     $1,234.00   │    │             │               │
│  └───────────────────────┘    └─────────────┘               │
│                                                              │
│  ACTIVE CONSTRAINTS                                         │
│  ├─ no_overdraft (balance ≥ pending)         ✓ PASS        │
│  ├─ leverage_limit (liab/balance ≤ 3.0)      ✓ PASS        │
│  └─ positive_balance (balance > 0)           ✓ PASS        │
│                                                              │
│  VERIFICATION HISTORY                                       │
│  ├─ 10:42:15 Created            f/g=0.00    [proof]        │
│  ├─ 10:45:32 Deposit $5000      f/g=0.25    [proof]        │
│  ├─ 11:02:18 Withdrawal $500    f/g=0.27    [proof]        │
│  └─ 11:15:44 Loan $1200         f/g=0.27    [proof]        │
│                                                              │
│  EXPORT PROOF                                               │
│  [Download Merkle Certificate]  [Copy Hash]                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Reversibility (Bijection)

Every state transition at every layer is reversible:

```
Layer 0 (Laws):      Not applicable (laws don't change)
Layer 1 (Core):      Bijective operations (try/untry, take/give)
Layer 2 (API):       Every mutation returns inverse operation
Layer 3 (aid-a):     Every Master Object has rollback path
Layer 4 (Apps):      UI shows return path for every action
Layer 5 (Newton OS): System calls paired with inverses
```

---

### Trust Model

Each layer trusts the one below absolutely:

```
Newton OS
    ↓ trusts
Consumer Apps
    ↓ trusts
aid-a Layer
    ↓ trusts
Newton API
    ↓ trusts
Newton Core
    ↓ trusts
tinyTalk Laws
    ↓ trusts
Mathematics
```

No layer needs to verify what a lower layer has already verified. This is the source of Newton's efficiency: verification happens once, at the lowest level, and propagates upward as trust.

---

## The Master Object

The atomic unit of the aid-a layer:

```typescript
interface MasterObject {
    // Identity
    id: string;              // UUID
    type: string;            // Schema type
    version: number;         // Version for optimistic concurrency

    // Content
    content: Record<string, unknown>;

    // Verification
    verified: boolean;
    fg_ratio: number;
    constraints: Constraint[];
    last_verified: number;   // Timestamp

    // Proof
    merkle_root: string;
    merkle_proof: MerkleProof;
    ledger_index: number;

    // Lineage
    created_at: number;
    created_by: string;
    parent_id?: string;      // For versioning/branching
    history: HistoryEntry[];

    // Reversibility
    inverse_operations: Operation[];
}
```

Every Master Object:
1. Has been verified by Newton
2. Is recorded in the Ledger
3. Can be proven cryptographically
4. Can be reversed to any previous state

---

## Data Flow Example

User uploads a voice memo: "I spent $45 on lunch, $120 on groceries, and got a $500 paycheck."

```
LAYER 3: aid-a
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  INPUT                                                       │
│  [Voice: "I spent $45 on lunch, $120 on groceries..."]      │
│                                                              │
│  CLAUDE PROCESSING                                           │
│  {                                                           │
│    "transactions": [                                         │
│      {"type": "expense", "category": "food", "amount": 45}, │
│      {"type": "expense", "category": "groceries", "amt": 120},
│      {"type": "income", "category": "salary", "amt": 500}   │
│    ],                                                        │
│    "net_change": 335,                                        │
│    "proposed_constraints": [                                 │
│      "expenses ≤ balance",                                  │
│      "all amounts > 0"                                       │
│    ]                                                         │
│  }                                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 2: Newton API
┌──────────────────────────────────────────────────────────────┐
│  POST /verify                                                │
│  {                                                           │
│    "constraints": [...],                                     │
│    "current_state": {"balance": 1000},                       │
│    "proposed_state": {"balance": 1335}                       │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 1: Newton Core
┌──────────────────────────────────────────────────────────────┐
│  CDL: Parse constraints                                      │
│  Logic: Compute new balance (1000 + 500 - 45 - 120 = 1335)  │
│  Forge: Verify 1335 ≥ 0 (balance positive) ✓                │
│  Forge: Verify expenses ≤ previous_balance ✓                │
│  Vault: Encrypt new state                                    │
│  Ledger: Append entry #4527                                  │
│  Merkle: Generate proof                                      │
│                                                              │
│  RESULT: 1 == 1 (all constraints pass)                       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
LAYER 3: aid-a (emit)
┌──────────────────────────────────────────────────────────────┐
│  MASTER OBJECT                                               │
│  {                                                           │
│    id: "obj_7x9k2...",                                       │
│    type: "financial_update",                                 │
│    content: {                                                │
│      transactions: [...],                                    │
│      new_balance: 1335                                       │
│    },                                                        │
│    verified: true,                                           │
│    fg_ratio: 0.12,                                           │
│    merkle_proof: "...",                                      │
│    ledger_index: 4527                                        │
│  }                                                           │
│                                                              │
│  Badge: ● 1≡1 (green)                                        │
└──────────────────────────────────────────────────────────────┘
```

**Time elapsed: ~5 seconds**

---

## SDK Overview

### Python SDK

```python
from aida import upload, verify, forge, glass_box

# Upload raw content
obj = await upload(
    content="I spent $45 on lunch...",
    content_type="text",
    constraints=["expenses <= balance"]
)

# Check object state
status = await verify(obj.id)
print(f"f/g ratio: {status.fg_ratio}")  # 0.12
print(f"Verified: {status.verified}")    # True

# Mutate with verification
new_obj = await forge(
    obj.id,
    mutation={"expense": {"category": "dinner", "amount": 30}}
)

# Inspect everything
history = await glass_box(obj.id)
for entry in history.ledger:
    print(f"{entry.timestamp}: {entry.operation} (f/g={entry.fg_ratio})")
```

### Swift SDK

```swift
import AidA

// Upload
let obj = try await AidA.upload(
    content: voiceMemo,
    contentType: .audio,
    constraints: [.expensesLteBalance]
)

// Verify
let status = try await obj.verify()
print("f/g: \(status.fgRatio)")  // 0.12

// Forge
let newObj = try await obj.forge(
    mutation: .expense(category: "dinner", amount: 30)
)

// Glass Box
let history = try await obj.glassBox()
for entry in history {
    print("\(entry.date): \(entry.operation)")
}
```

### TypeScript SDK

```typescript
import { upload, verify, forge, glassBox } from '@newton/aida';

// Upload
const obj = await upload({
    content: "I spent $45 on lunch...",
    contentType: "text",
    constraints: ["expenses <= balance"]
});

// Verify
const status = await verify(obj.id);
console.log(`f/g: ${status.fgRatio}`);  // 0.12

// Forge
const newObj = await forge(obj.id, {
    mutation: { expense: { category: "dinner", amount: 30 } }
});

// Glass Box
const history = await glassBox(obj.id);
history.forEach(entry => {
    console.log(`${entry.timestamp}: ${entry.operation}`);
});
```

---

## Performance Characteristics

| Layer | Latency | Throughput | Notes |
|-------|---------|------------|-------|
| tinyTalk | N/A | N/A | Declarative only |
| Newton Core | 46.5μs | ∞ | Internal processing |
| Newton API | 2.31ms | 605 req/s | Full verification |
| aid-a | ~1-5s | 100 req/s | Depends on Claude latency |
| Consumer Apps | ~5s UX | N/A | "5 minutes to truth" |

The bottleneck is Claude, not Newton. Newton can verify faster than Claude can generate.

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                                  │
│                                                                     │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐      │
│  │   CDN         │    │   Load        │    │   aid-a       │      │
│  │   (Static)    │───▶│   Balancer    │───▶│   Workers     │      │
│  │               │    │               │    │   (3+)        │      │
│  └───────────────┘    └───────────────┘    └───────┬───────┘      │
│                                                     │               │
│                                            ┌────────┴────────┐     │
│                                            ▼                 ▼     │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐      │
│  │   Claude      │◀───│   Newton      │───▶│   Ledger      │      │
│  │   API         │    │   API         │    │   (Postgres)  │      │
│  │   (Anthropic) │    │   (3+)        │    │               │      │
│  └───────────────┘    └───────────────┘    └───────────────┘      │
│                              │                                      │
│                              ▼                                      │
│                       ┌───────────────┐                            │
│                       │   Vault       │                            │
│                       │   (Encrypted) │                            │
│                       │   (Redis)     │                            │
│                       └───────────────┘                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

The aid-a stack is a vertical integration from pure mathematics to consumer products:

1. **Laws** (tinyTalk): Define forbidden states
2. **Core** (Newton): Enforce laws with cryptographic proof
3. **API**: Expose enforcement over HTTP
4. **aid-a**: Translate human intent to verified objects
5. **Apps**: Domain-specific interfaces
6. **OS**: System-level verification

Each layer trusts the one below. Trust flows upward. Verification happens once at the bottom and propagates as certainty.

This is the architecture. This is aid-a. This is what we're building.

---

*"Newton is the chip. aid-a is the system. Truth is the product."*
