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

### Education (Lesson Planning)

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/education/lesson`](#education-lesson) | POST | Generate NES-compliant lesson plan |
| [`/education/slides`](#education-slides) | POST | Generate slide deck |
| [`/education/assess`](#education-assess) | POST | Analyze student assessments (MAD) |
| [`/education/plc`](#education-plc) | POST | Generate PLC report |
| [`/education/teks`](#education-teks) | GET | Browse all TEKS standards |
| [`/education/teks/{code}`](#education-teks-code) | GET | Get specific TEKS standard |
| [`/education/teks/search`](#education-teks-search) | POST | Search TEKS standards |
| [`/education/info`](#education-info) | GET | Education API documentation |

### Teacher's Aide Database (Classroom Management)

| Endpoint | Method | Description |
|----------|--------|-------------|
| [`/teachers/db`](#teachers-db) | GET | Database summary |
| [`/teachers/students`](#teachers-students-post) | POST | Add a new student |
| [`/teachers/students/batch`](#teachers-students-batch) | POST | Add multiple students |
| [`/teachers/students`](#teachers-students-get) | GET | List/search students |
| [`/teachers/students/{id}`](#teachers-students-id) | GET | Get student details |
| [`/teachers/classrooms`](#teachers-classrooms-post) | POST | Create a classroom |
| [`/teachers/classrooms`](#teachers-classrooms-get) | GET | List all classrooms |
| [`/teachers/classrooms/{id}`](#teachers-classrooms-id) | GET | Get classroom with roster |
| [`/teachers/classrooms/{id}/students`](#teachers-classrooms-students) | POST | Add students to classroom |
| [`/teachers/classrooms/{id}/groups`](#teachers-classrooms-groups) | GET | **Get differentiated groups** |
| [`/teachers/classrooms/{id}/reteach`](#teachers-classrooms-reteach) | GET | Get reteach group |
| [`/teachers/assessments`](#teachers-assessments) | POST | Create an assessment |
| [`/teachers/assessments/{id}/scores`](#teachers-assessments-scores) | POST | Enter scores by student ID |
| [`/teachers/assessments/{id}/quick-scores`](#teachers-assessments-quick-scores) | POST | Enter scores by name |
| [`/teachers/interventions`](#teachers-interventions) | POST | Create intervention plan |
| [`/teachers/teks`](#teachers-teks) | GET | Browse 188 TEKS (K-8) |
| [`/teachers/teks/stats`](#teachers-teks-stats) | GET | TEKS statistics |
| [`/teachers/db/save`](#teachers-db-save) | POST | Save database to file |
| [`/teachers/db/load`](#teachers-db-load) | POST | Load database from file |
| [`/teachers/info`](#teachers-info) | GET | Teacher's Aide API docs |

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

## Education Endpoints

### /education/lesson

Generate an NES-compliant lesson plan with TEKS alignment.

**POST** `/education/lesson`

#### Request Body

```json
{
  "grade": 5,
  "subject": "math",
  "teks_codes": ["5.3A", "5.3B"],
  "topic": "Adding Fractions with Unlike Denominators",
  "accommodations": {
    "ell": true,
    "sped": false,
    "504": false,
    "gt": false
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `grade` | int | Yes | Grade level (K=0, 1-12) |
| `subject` | string | Yes | Subject: math, science, ela, social_studies |
| `teks_codes` | array | Yes | TEKS standard codes |
| `topic` | string | No | Specific lesson topic |
| `accommodations` | object | No | ELL, SPED, 504, GT flags |

#### Response

```json
{
  "lesson_plan": {
    "title": "Adding Fractions with Unlike Denominators",
    "grade": 5,
    "subject": "math",
    "teks_codes": ["5.3A", "5.3B"],
    "duration_minutes": 50,
    "phases": [
      {
        "name": "Opening",
        "duration": 5,
        "activities": ["Number talk with fraction comparison", "Review previous day's learning"]
      },
      {
        "name": "Instruction",
        "duration": 15,
        "activities": ["Model finding common denominators", "Demonstrate addition process"]
      },
      {
        "name": "Guided Practice",
        "duration": 15,
        "activities": ["Partner work with fraction tiles", "Collaborative problem solving"]
      },
      {
        "name": "Independent Practice",
        "duration": 10,
        "activities": ["Individual worksheet", "Self-assessment checklist"]
      },
      {
        "name": "Closing",
        "duration": 5,
        "activities": ["Exit ticket", "Preview next lesson"]
      }
    ],
    "accommodations_applied": ["ell"],
    "teks_aligned": true
  },
  "verified": true,
  "fingerprint": "EDU-A1B2C3D4"
}
```

---

### /education/slides

Generate a slide deck specification for a lesson.

**POST** `/education/slides`

#### Request Body

```json
{
  "grade": 5,
  "subject": "math",
  "teks_codes": ["5.3A"],
  "topic": "Adding Fractions",
  "slide_count": 10
}
```

---

### /education/assess

Analyze student assessment data using MAD statistics.

**POST** `/education/assess`

#### Request Body

```json
{
  "scores": [85, 72, 90, 65, 88, 45, 92, 78, 80, 95],
  "teks_codes": ["5.3A", "5.3B"],
  "class_size": 25
}
```

#### Response

```json
{
  "analysis": {
    "n": 10,
    "median": 81.5,
    "mad": 8.0,
    "passing_rate": 0.8,
    "at_risk_students": [5],
    "mastery_students": [2, 6, 9],
    "teks_performance": {
      "5.3A": {"median": 83, "mastery_rate": 0.7},
      "5.3B": {"median": 78, "mastery_rate": 0.6}
    }
  },
  "recommendations": [
    "Reteach 5.3B with additional scaffolding",
    "Provide intervention for student at index 5"
  ],
  "verified": true
}
```

---

### /education/plc

Generate a PLC (Professional Learning Community) report.

**POST** `/education/plc`

#### Request Body

```json
{
  "campus": "Example Elementary",
  "grade": 5,
  "subject": "math",
  "scores": [85, 72, 90, 65, 88, 45, 92, 78, 80, 95],
  "teks_codes": ["5.3A", "5.3B"],
  "period": "Week 12"
}
```

---

### /education/teks

Browse all available TEKS standards.

**GET** `/education/teks`

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `grade` | int | - | Filter by grade level |
| `subject` | string | - | Filter by subject |

---

### /education/teks/{code}

Get a specific TEKS standard by code.

**GET** `/education/teks/{code}`

#### Response

```json
{
  "code": "5.3A",
  "grade": 5,
  "subject": "math",
  "description": "Add and subtract fractions with unequal denominators",
  "cognitive_level": "apply",
  "prerequisites": ["4.3A", "4.3B"],
  "strand": "Number and Operations"
}
```

---

### /education/teks/search

Search TEKS standards by keyword, grade, or subject.

**POST** `/education/teks/search`

#### Request Body

```json
{
  "query": "fractions",
  "grade": 5,
  "subject": "math"
}
```

---

### /education/info

Get education API documentation and available subjects/grades.

**GET** `/education/info`

#### Response

```json
{
  "version": "1.0.0",
  "subjects": ["math", "science", "ela", "social_studies"],
  "grades": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
  "nes_phases": [
    {"name": "Opening", "duration": 5},
    {"name": "Instruction", "duration": 15},
    {"name": "Guided Practice", "duration": 15},
    {"name": "Independent Practice", "duration": 10},
    {"name": "Closing", "duration": 5}
  ],
  "total_duration": 50,
  "accommodations": ["ell", "sped", "504", "gt"]
}
```

---

## Teacher's Aide Database Endpoints

The Teacher's Aide Database provides classroom management with **automatic differentiation**. Students are automatically grouped into 4 tiers based on their assessment performance.

### Differentiation Tiers

| Tier | Level | Score Range | Instruction |
|------|-------|-------------|-------------|
| **Tier 3** | Needs Reteach | Below 70% | Small group with teacher, manipulatives |
| **Tier 2** | Approaching | 70-79% | Guided practice with scaffolds |
| **Tier 1** | Mastery | 80-89% | Standard instruction |
| **Enrichment** | Advanced | 90%+ | Extension activities, peer tutoring |

### /teachers/db

Get database summary and statistics.

**GET** `/teachers/db`

#### Response

```json
{
  "total_students": 125,
  "total_classrooms": 5,
  "total_assessments": 23,
  "total_interventions": 8
}
```

---

### /teachers/students (POST)

Add a new student to the database.

**POST** `/teachers/students`

#### Request Body

```json
{
  "first_name": "Maria",
  "last_name": "Garcia",
  "grade": 5,
  "accommodations": ["ell", "504"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | Student's first name |
| `last_name` | string | Yes | Student's last name |
| `grade` | int | Yes | Grade level (K=0, 1-12) |
| `accommodations` | array | No | List: ell, sped, 504, gt, dyslexia, rti |

#### Response

```json
{
  "id": "STU0001",
  "first_name": "Maria",
  "last_name": "Garcia",
  "grade": 5,
  "accommodations": ["ell", "504"],
  "mastery_levels": {},
  "created_at": "2026-01-02T10:00:00Z"
}
```

---

### /teachers/students/batch

Add multiple students at once.

**POST** `/teachers/students/batch`

#### Request Body

```json
{
  "students": [
    {"first_name": "John", "last_name": "Smith", "grade": 5},
    {"first_name": "Sarah", "last_name": "Johnson", "grade": 5, "accommodations": ["gt"]},
    {"first_name": "Carlos", "last_name": "Rodriguez", "grade": 5, "accommodations": ["ell"]}
  ]
}
```

#### Response

```json
{
  "added": 3,
  "students": [
    {"id": "STU0001", "name": "John Smith"},
    {"id": "STU0002", "name": "Sarah Johnson"},
    {"id": "STU0003", "name": "Carlos Rodriguez"}
  ]
}
```

---

### /teachers/students (GET)

List or search students.

**GET** `/teachers/students`

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search by name (partial match) |
| `grade` | int | Filter by grade level |

#### Response

```json
{
  "students": [
    {
      "id": "STU0001",
      "first_name": "Maria",
      "last_name": "Garcia",
      "grade": 5,
      "accommodations": ["ell", "504"]
    }
  ],
  "total": 1
}
```

---

### /teachers/students/{id}

Get detailed student information including mastery levels.

**GET** `/teachers/students/{id}`

#### Response

```json
{
  "id": "STU0001",
  "first_name": "Maria",
  "last_name": "Garcia",
  "grade": 5,
  "accommodations": ["ell", "504"],
  "mastery_levels": {
    "5.3A": "mastery",
    "5.3B": "approaching",
    "5.4A": "needs_reteach"
  },
  "assessment_history": [
    {"assessment_id": "ASSESS0001", "score": 85, "date": "2026-01-02"}
  ]
}
```

---

### /teachers/classrooms (POST)

Create a new classroom.

**POST** `/teachers/classrooms`

#### Request Body

```json
{
  "name": "5th Period Math",
  "grade": 5,
  "subject": "mathematics",
  "teacher_name": "Ms. Johnson",
  "current_teks": ["5.3A", "5.3B"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Classroom name |
| `grade` | int | Yes | Grade level |
| `subject` | string | Yes | Subject area |
| `teacher_name` | string | Yes | Teacher's name |
| `current_teks` | array | No | Current TEKS focus |

#### Response

```json
{
  "id": "CLASS001",
  "name": "5th Period Math",
  "grade": 5,
  "subject": "mathematics",
  "teacher_name": "Ms. Johnson",
  "current_teks": ["5.3A", "5.3B"],
  "student_ids": [],
  "created_at": "2026-01-02T10:00:00Z"
}
```

---

### /teachers/classrooms (GET)

List all classrooms.

**GET** `/teachers/classrooms`

---

### /teachers/classrooms/{id}

Get classroom details with full roster.

**GET** `/teachers/classrooms/{id}`

#### Response

```json
{
  "classroom": {
    "id": "CLASS001",
    "name": "5th Period Math",
    "grade": 5,
    "subject": "mathematics",
    "teacher_name": "Ms. Johnson"
  },
  "roster": [
    {"id": "STU0001", "name": "Garcia, Maria", "accommodations": ["ell", "504"]},
    {"id": "STU0002", "name": "Smith, John", "accommodations": []}
  ],
  "student_count": 2
}
```

---

### /teachers/classrooms/{id}/students

Add students to a classroom roster.

**POST** `/teachers/classrooms/{id}/students`

#### Request Body

```json
{
  "student_ids": ["STU0001", "STU0002", "STU0003"]
}
```

---

### /teachers/classrooms/{id}/groups

**THE KEY FEATURE** - Get students grouped by differentiation tier.

**GET** `/teachers/classrooms/{id}/groups`

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `teks_code` | string | Filter by specific TEKS (optional) |

#### Response

```json
{
  "classroom_id": "CLASS001",
  "classroom_name": "5th Period Math",
  "teks_filter": null,
  "groups": {
    "needs_reteach": {
      "students": [
        {"id": "STU0003", "name": "Carlos Rodriguez", "score": 65}
      ],
      "count": 1,
      "instruction": "Small group with teacher. Use manipulatives. Review prerequisite skills."
    },
    "approaching": {
      "students": [
        {"id": "STU0004", "name": "Emily Davis", "score": 75}
      ],
      "count": 1,
      "instruction": "Guided practice with scaffolds. Pair with mastery student."
    },
    "mastery": {
      "students": [
        {"id": "STU0001", "name": "Maria Garcia", "score": 85}
      ],
      "count": 1,
      "instruction": "Standard instruction. Independent practice."
    },
    "advanced": {
      "students": [
        {"id": "STU0002", "name": "Sarah Johnson", "score": 95}
      ],
      "count": 1,
      "instruction": "Extension activities. Peer tutoring. Leadership roles."
    },
    "not_assessed": {
      "students": [],
      "count": 0,
      "instruction": "Assess these students first."
    }
  },
  "summary": {
    "total": 4,
    "needs_reteach": 1,
    "approaching": 1,
    "mastery": 1,
    "advanced": 1
  }
}
```

---

### /teachers/classrooms/{id}/reteach

Get only the reteach group for quick intervention planning.

**GET** `/teachers/classrooms/{id}/reteach`

---

### /teachers/assessments

Create a new assessment.

**POST** `/teachers/assessments`

#### Request Body

```json
{
  "name": "Exit Ticket - Fractions",
  "classroom_id": "CLASS001",
  "teks_codes": ["5.3A", "5.3B"],
  "total_points": 10
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Assessment name |
| `classroom_id` | string | Yes | Associated classroom |
| `teks_codes` | array | Yes | TEKS being assessed |
| `total_points` | int | Yes | Maximum score |

---

### /teachers/assessments/{id}/scores

Enter scores by student ID.

**POST** `/teachers/assessments/{id}/scores`

#### Request Body

```json
{
  "scores": {
    "STU0001": 8,
    "STU0002": 10,
    "STU0003": 6
  }
}
```

#### Response

```json
{
  "assessment_id": "ASSESS0001",
  "scores_entered": 3,
  "class_average": 80.0,
  "mastery_rate": 0.67,
  "groups_updated": true
}
```

---

### /teachers/assessments/{id}/quick-scores

**Enter scores by student name** - No IDs needed!

**POST** `/teachers/assessments/{id}/quick-scores`

#### Request Body

```json
{
  "scores": [
    ["Maria Garcia", 8],
    ["John Smith", 10],
    ["Carlos Rodriguez", 6]
  ]
}
```

This matches students by name (case-insensitive, partial match supported) and automatically updates their mastery levels.

---

### /teachers/interventions

Create an intervention plan for a group of students.

**POST** `/teachers/interventions`

#### Request Body

```json
{
  "name": "Fraction Reteach Group",
  "classroom_id": "CLASS001",
  "teks_codes": ["5.3A"],
  "tier": "needs_reteach",
  "student_ids": ["STU0003", "STU0005"],
  "strategies": ["Small group instruction", "Manipulatives", "Visual models"],
  "notes": "Focus on finding common denominators"
}
```

---

### /teachers/teks

Browse the extended TEKS database (188 standards, K-8).

**GET** `/teachers/teks`

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `grade` | int | Filter by grade (0-8) |
| `subject` | string | Filter by subject |

#### Response

```json
{
  "teks": [
    {
      "code": "5.3A",
      "grade": 5,
      "subject": "mathematics",
      "description": "Add and subtract fractions with unequal denominators...",
      "strand": "Number and Operations",
      "cognitive_level": "apply"
    }
  ],
  "total": 188
}
```

---

### /teachers/teks/stats

Get TEKS database statistics.

**GET** `/teachers/teks/stats`

#### Response

```json
{
  "total_standards": 188,
  "by_subject": {
    "mathematics": 72,
    "reading": 48,
    "science": 40,
    "social_studies": 28
  },
  "by_grade": {
    "K": 16,
    "1": 20,
    "2": 22,
    "3": 24,
    "4": 26,
    "5": 26,
    "6": 18,
    "7": 18,
    "8": 18
  }
}
```

---

### /teachers/db/save

Save the entire database to a JSON file.

**POST** `/teachers/db/save`

#### Request Body

```json
{
  "filename": "my_classroom_backup.json"
}
```

---

### /teachers/db/load

Load a previously saved database from JSON.

**POST** `/teachers/db/load`

#### Request Body

```json
{
  "filename": "my_classroom_backup.json"
}
```

---

### /teachers/info

Get Teacher's Aide API documentation and feature summary.

**GET** `/teachers/info`

---

## Quick Start: Differentiation Workflow

```bash
# 1. Add students (batch)
curl -X POST http://localhost:8000/teachers/students/batch \
  -H "Content-Type: application/json" \
  -d '{"students": [
    {"first_name": "Maria", "last_name": "Garcia", "grade": 5, "accommodations": ["ell"]},
    {"first_name": "John", "last_name": "Smith", "grade": 5},
    {"first_name": "Sarah", "last_name": "Johnson", "grade": 5, "accommodations": ["gt"]}
  ]}'

# 2. Create classroom
curl -X POST http://localhost:8000/teachers/classrooms \
  -H "Content-Type: application/json" \
  -d '{"name": "5th Math", "grade": 5, "subject": "mathematics", "teacher_name": "Ms. Johnson"}'

# 3. Add students to classroom
curl -X POST http://localhost:8000/teachers/classrooms/CLASS001/students \
  -H "Content-Type: application/json" \
  -d '{"student_ids": ["STU0001", "STU0002", "STU0003"]}'

# 4. Create assessment
curl -X POST http://localhost:8000/teachers/assessments \
  -H "Content-Type: application/json" \
  -d '{"name": "Exit Ticket", "classroom_id": "CLASS001", "teks_codes": ["5.3A"], "total_points": 10}'

# 5. Enter scores by name (THE EASY WAY!)
curl -X POST http://localhost:8000/teachers/assessments/ASSESS0001/quick-scores \
  -H "Content-Type: application/json" \
  -d '{"scores": [["Maria Garcia", 8], ["John Smith", 6], ["Sarah Johnson", 10]]}'

# 6. GET DIFFERENTIATED GROUPS!
curl http://localhost:8000/teachers/classrooms/CLASS001/groups
```

---

© 2025-2026 Ada Computing Company · Houston, Texas
