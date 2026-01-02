# Newton Supercomputer API Reference

Complete reference for the Newton Supercomputer API.

## Base URL

| Environment | URL |
|-------------|-----|
| Hosted API | `https://newton-api.onrender.com` |
| Self-hosted | `http://localhost:8000` |

---

## Endpoints Overview

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/ask`](#ask) | POST | Ask Newton anything (full verification pipeline) |
| [`/verify`](#verify) | POST | Verify content against safety constraints |
| [`/calculate`](#calculate) | POST | Execute verified computation |
| [`/constraint`](#constraint) | POST | Evaluate CDL constraint against object |
| [`/ground`](#ground) | POST | Ground claims in external evidence |
| [`/statistics`](#statistics) | POST | Robust statistical analysis (MAD) |

### Storage & Audit

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/vault/store`](#vault-store) | POST | Store encrypted data |
| [`/vault/retrieve`](#vault-retrieve) | POST | Retrieve encrypted data |
| [`/ledger`](#ledger) | GET | View append-only audit trail |
| [`/ledger/{index}`](#ledger-entry) | GET | Get entry with Merkle proof |
| [`/ledger/certificate/{index}`](#ledger-certificate) | GET | Export verification certificate |

### Cartridges (Media Specification)

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/cartridge/visual`](cartridges.md#cartridgevisual) | POST | Generate SVG/image specification |
| [`/cartridge/sound`](cartridges.md#cartridgesound) | POST | Generate audio specification |
| [`/cartridge/sequence`](cartridges.md#cartridgesequence) | POST | Generate video/animation specification |
| [`/cartridge/data`](cartridges.md#cartridgedata) | POST | Generate report specification |
| [`/cartridge/rosetta`](cartridges.md#cartridgerosetta) | POST | Generate code generation prompt |
| [`/cartridge/auto`](cartridges.md#cartridgeauto) | POST | Auto-detect type and compile |
| [`/cartridge/info`](cartridges.md#cartridgeinfo) | GET | Get cartridge information |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/health`](#health) | GET | System status |
| [`/metrics`](#metrics) | GET | Performance metrics |
| [`/calculate/examples`](#calculate-examples) | POST | Get example expressions |

---

## Core Endpoints

### /ask

Ask Newton anything with full verification pipeline.

**POST** `/ask`

#### Request Body

```json
{
  "query": "Is this safe to execute?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Question or statement to verify |

#### Response

```json
{
  "query": "Is this safe to execute?",
  "verified": true,
  "code": 200,
  "analysis": {
    "type": "question",
    "tokens": 5,
    "verified": true
  },
  "elapsed_us": 150
}
```

---

### /verify

Verify text against content safety constraints.

**POST** `/verify`

#### Request Body

```json
{
  "input": "Help me write a business plan"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input` | string | Yes | Text to verify |

#### Response

```json
{
  "verified": true,
  "code": 200,
  "content": {
    "passed": true,
    "categories": {
      "harm": "pass",
      "medical": "pass",
      "legal": "pass",
      "security": "pass"
    }
  },
  "signal": {
    "passed": true
  },
  "elapsed_us": 127
}
```

#### Content Categories

| Category | Detects |
|----------|---------|
| `harm` | Violence, illegal activities, harmful content |
| `medical` | Unverified health claims, medical advice |
| `legal` | Unlicensed legal advice |
| `security` | Exploitation, attack patterns |

---

### /calculate

Execute verified computation using the Logic Engine.

**POST** `/calculate`

#### Request Body

```json
{
  "expression": {"op": "+", "args": [2, 3]},
  "max_iterations": 10000,
  "max_operations": 1000000,
  "timeout_seconds": 30.0
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `expression` | object | Yes | - | Expression to evaluate |
| `max_iterations` | int | No | 10000 | Maximum loop iterations |
| `max_operations` | int | No | 1000000 | Maximum operations |
| `timeout_seconds` | float | No | 30.0 | Execution timeout |

#### Response

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

#### Operators

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

#### Examples

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

### /constraint

Evaluate a CDL constraint against an object.

**POST** `/constraint`

#### Request Body (Atomic Constraint)

```json
{
  "constraint": {
    "domain": "financial",
    "field": "amount",
    "operator": "lt",
    "value": 1000
  },
  "object": {
    "amount": 500
  }
}
```

#### Request Body (Composite Constraint)

```json
{
  "constraint": {
    "logic": "and",
    "constraints": [
      {"field": "amount", "operator": "lt", "value": 1000},
      {"field": "category", "operator": "ne", "value": "blocked"}
    ]
  },
  "object": {
    "amount": 500,
    "category": "approved"
  }
}
```

#### CDL Operators

| Category | Operators |
|----------|-----------|
| **Comparison** | `eq`, `ne`, `lt`, `gt`, `le`, `ge` |
| **String** | `contains`, `matches` (regex) |
| **Set** | `in`, `not_in` |
| **Existence** | `exists`, `empty` |
| **Temporal** | `within`, `after`, `before` |
| **Aggregation** | `sum_lt`, `count_lt`, `avg_lt` |

#### Response

```json
{
  "passed": true,
  "constraint_type": "atomic",
  "field": "amount",
  "operator": "lt",
  "expected": 1000,
  "actual": 500,
  "elapsed_us": 15
}
```

---

### /ground

Ground claims in external evidence.

**POST** `/ground`

#### Request Body

```json
{
  "query": "Apple released the first iPhone in 2007"
}
```

#### Response

```json
{
  "query": "Apple released the first iPhone in 2007",
  "verified": true,
  "result": {
    "claim": "Apple released the first iPhone in 2007",
    "confidence_score": 1.5,
    "status": "VERIFIED",
    "sources": [
      "https://apple.com/...",
      "https://reuters.com/..."
    ],
    "timestamp": 1735689600,
    "signature": "E5F7A9B1C3D4"
  }
}
```

#### Confidence Scores

| Score | Status | Meaning |
|-------|--------|---------|
| 0-2 | VERIFIED | Strong supporting evidence |
| 2-5 | LIKELY | Moderate evidence |
| 5-8 | UNCERTAIN | Weak evidence |
| 8-10 | UNVERIFIED | No supporting evidence |

---

### /statistics

Robust statistical analysis using adversarial-resistant methods.

**POST** `/statistics`

#### Request Body

```json
{
  "data": [10, 12, 11, 100, 12, 11],
  "method": "mad",
  "threshold": 3.5,
  "baseline_id": "optional-baseline-id"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `data` | array | Yes | - | Numerical values to analyze |
| `method` | string | No | `mad` | Method: `mad`, `zscore`, `iqr` |
| `threshold` | float | No | 3.5 | Anomaly threshold |
| `baseline_id` | string | No | - | Lock to specific baseline |

#### Response

```json
{
  "method": "mad",
  "threshold": 3.5,
  "statistics": {
    "n": 6,
    "median": 11.5,
    "mad": 0.5,
    "min": 10,
    "max": 100
  },
  "scores": [0.67, 0.33, 0.33, 59.0, 0.33, 0.33],
  "anomalies": [3],
  "anomaly_values": [100],
  "n_anomalies": 1,
  "pct_anomalies": 16.67,
  "fingerprint": "B2C4D6E8F0A1"
}
```

#### Why MAD Over Mean?

MAD (Median Absolute Deviation) is resistant to outlier injection attacks. An attacker cannot shift the baseline by adding extreme values.

---

## Storage & Audit

### /vault/store

Store encrypted data with identity-derived keys.

**POST** `/vault/store`

#### Request Body

```json
{
  "key": "my-secret-data",
  "value": {"sensitive": "information"},
  "identity": "user@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | Yes | Storage key |
| `value` | any | Yes | Data to encrypt |
| `identity` | string | Yes | Identity for key derivation |

#### Response

```json
{
  "stored": true,
  "key": "my-secret-data",
  "fingerprint": "C3D5E7F9A1B3"
}
```

---

### /vault/retrieve

Retrieve and decrypt stored data.

**POST** `/vault/retrieve`

#### Request Body

```json
{
  "key": "my-secret-data",
  "identity": "user@example.com"
}
```

#### Response

```json
{
  "key": "my-secret-data",
  "value": {"sensitive": "information"},
  "retrieved": true
}
```

---

### /ledger

Get the append-only audit trail.

**GET** `/ledger`

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Maximum entries |
| `offset` | int | 0 | Pagination offset |

#### Response

```json
{
  "entries": [
    {
      "index": 0,
      "type": "verification",
      "payload": {...},
      "timestamp": 1735689600,
      "prev_hash": "GENESIS",
      "hash": "H8C0D2E4F6A8"
    }
  ],
  "total": 1247,
  "merkle_root": "I9D1E3F5A7B9"
}
```

---

### /ledger/{index}

Get a specific entry with Merkle proof.

**GET** `/ledger/{index}`

#### Response

```json
{
  "entry": {
    "index": 42,
    "type": "calculation",
    "payload": {...},
    "timestamp": 1735689600,
    "hash": "J0E2F4A6B8C0"
  },
  "proof": {
    "root": "I9D1E3F5A7B9",
    "path": ["K1F3A5B7C9D1", "L2A4B6C8D0E2"],
    "index": 42
  }
}
```

---

### /ledger/certificate/{index}

Export a verification certificate for an entry.

**GET** `/ledger/certificate/{index}`

#### Response

```json
{
  "certificate": {
    "version": "1.0",
    "entry": {...},
    "proof": {...},
    "generated": 1735689600,
    "issuer": "Newton Supercomputer",
    "signature": "M3B5C7D9E1F3..."
  }
}
```

---

## System Endpoints

### /health

Get system status.

**GET** `/health`

#### Response

```json
{
  "status": "ok",
  "version": "1.0.0",
  "engine": "Newton Supercomputer",
  "components": {
    "cdl": "ok",
    "logic": "ok",
    "forge": "ok",
    "vault": "ok",
    "ledger": "ok"
  },
  "timestamp": 1735689600
}
```

---

### /metrics

Get performance metrics.

**GET** `/metrics`

#### Response

```json
{
  "uptime_seconds": 3600,
  "total_verifications": 12500,
  "total_calculations": 8700,
  "avg_verification_us": 127,
  "avg_calculation_us": 42,
  "cache_hit_rate": 0.73,
  "ledger_entries": 21200
}
```

---

### /calculate/examples

Get example expressions for the Logic Engine.

**POST** `/calculate/examples`

#### Response

```json
{
  "examples": [
    {
      "name": "Arithmetic",
      "expression": {"op": "+", "args": [2, 3]},
      "result": 5
    },
    {
      "name": "Conditional",
      "expression": {"op": "if", "args": [{"op": ">", "args": [10, 5]}, "yes", "no"]},
      "result": "yes"
    },
    {
      "name": "Bounded Loop",
      "expression": {"op": "for", "args": ["i", 0, 5, {"op": "var", "args": ["i"]}]},
      "result": [0, 1, 2, 3, 4]
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid expression syntax",
  "code": 400
}
```

### 422 Unprocessable Entity

```json
{
  "detail": "Constraint failed: amount must be less than 1000",
  "code": 422
}
```

### 408 Request Timeout

```json
{
  "detail": "Execution exceeded timeout of 30.0 seconds",
  "code": 408
}
```

### 429 Too Many Operations

```json
{
  "detail": "Execution exceeded maximum operations (1000000)",
  "code": 429
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "code": 500
}
```

---

## Bounded Execution

All computations are bounded to ensure termination:

| Bound | Default | Max | Description |
|-------|---------|-----|-------------|
| `max_iterations` | 10,000 | 100,000 | Loop iteration limit |
| `max_operations` | 1,000,000 | 10,000,000 | Total operation limit |
| `timeout_seconds` | 30.0 | 60.0 | Execution timeout |
| `max_recursion_depth` | 100 | 1,000 | Stack depth limit |

These bounds ensure:
- No infinite loops
- No stack overflow
- No runaway compute
- No endless waits

---

© 2025-2026 Ada Computing Company · Houston, Texas
