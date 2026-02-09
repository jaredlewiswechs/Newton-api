# Jester

## Newton Code Constraint Compiler

Jester is the **constraint extraction front-end** for the Newton Supercomputer. It translates imperative source code into formal constraint specifications.

This is not an analyzer. This is a **compiler pass** that converts procedural guards into declarative laws.

---

## What Jester Does

```
Source Code → AST → Constraint Extraction → Newton Cartridge → CDL
```

| Stage | Input | Output |
|-------|-------|--------|
| **Parse** | Source code (any language) | Abstract Syntax Tree |
| **Extract** | AST nodes | Raw guard conditions |
| **Normalize** | Raw conditions | Standardized constraint form |
| **Translate** | Normalized form | Newton ratio constraints |
| **Analyze** | Control flow | Unreachable states |
| **Emit** | All of the above | Newton Cartridge (JSON) or CDL |

---

## Core Concept

Every `if` statement is a law waiting to be extracted.

```python
# This code:
if amount > balance:
    return None

# Contains this law:
# LAW: amount / balance <= 1.0

# Which forbids this state:
# FORBIDDEN: amount > balance
```

Jester makes the implicit explicit.

---

## Installation

Jester is built into Newton. No separate installation required.

```python
from tinytalk_py.jester import Jester, analyze_code
from core import import_code  # CDL integration
```

---

## API

### Direct Analysis

```python
from tinytalk_py.jester import Jester

code = """
def withdraw(amount, balance):
    if amount <= 0:
        raise ValueError("Invalid")
    if amount > balance:
        return None
    return balance - amount
"""

jester = Jester(code)
cartridge = jester.analyze().to_dict()

# cartridge contains:
# - constraints: [{kind: "guard", newton_constraint: "amount <= 0", ...}]
# - forbidden_states: ["NOT (amount <= 0)", "NOT (amount > balance)"]
# - unreachable_states: [...]  # CFG analysis results
# - required_invariants: [...]
```

### CDL Integration (@import_code)

```python
from core import import_code

# Import constraints from any source code
cartridge = import_code("""
    guard let user = user else { return nil }
    precondition(user.age >= 18)
""", language="swift")

# Use in CDL definitions
from core import CDLParser

parser = CDLParser()
result = parser.parse_with_imports({
    "@import_code": {"code": source_code, "language": "python"},
    "field": "amount",
    "operator": "lt",
    "value": 1000
})
```

### HTTP API

```bash
# Analyze code
curl -X POST http://localhost:8000/jester/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def f(x):\n  if x < 0: return\n  return x*2"}'

# Get CDL output
curl -X POST http://localhost:8000/jester/cdl \
  -H "Content-Type: application/json" \
  -d '{"code": "...", "language": "python"}'
```

---

## Constraint Kinds

| Kind | Pattern | Example |
|------|---------|---------|
| `guard` | `if condition:` | `if x < 0: return` |
| `assertion` | `assert condition` | `assert balance >= 0` |
| `early_exit` | `if cond: return` | `if not valid: return None` |
| `null_check` | `if x is None` | `guard let x = x else` |
| `precondition` | `precondition(...)` | `precondition(x > 0)` |
| `exception` | `raise/throw` | `raise ValueError(...)` |

---

## CFG Analysis (v1.1)

Jester performs control flow analysis to detect:

### Dead Code
```python
def f():
    return 1
    x = 2  # UNREACHABLE: follows return at line 2
```

### Tautological Conditions
```python
if True:      # UNREACHABLE: else branch can never execute
    do_thing()
else:
    never_runs()
```

### Contradictory Guards
```python
if x > 10:
    if x < 5:  # UNREACHABLE: contradicts x > 10
        impossible()
```

---

## Supported Languages

| Language | Detection | Extraction | CFG |
|----------|-----------|------------|-----|
| Python | Yes | Yes | Yes |
| JavaScript | Yes | Yes | Yes |
| TypeScript | Yes | Yes | Yes |
| Swift | Yes | Yes | Yes |
| Objective-C | Yes | Yes | Yes |
| C | Yes | Yes | Yes |
| C++ | Yes | Yes | Yes |
| Java | Yes | Yes | Yes |
| Go | Yes | Yes | Yes |
| Rust | Yes | Yes | Yes |
| Ruby | Yes | Yes | Yes |

---

## Output Formats

### Newton Cartridge (JSON)

```json
{
  "source_language": "python",
  "constraints": [
    {
      "kind": "guard",
      "raw_condition": "amount <= 0",
      "normalized_form": "amount <= 0",
      "newton_constraint": "amount <= 0",
      "line_number": 3,
      "context": "Conditional check"
    }
  ],
  "forbidden_states": ["NOT (amount <= 0)"],
  "unreachable_states": [],
  "required_invariants": [],
  "summary": {
    "total_constraints": 2,
    "unreachable_count": 0
  }
}
```

### CDL (Constraint Definition Language)

```
// Newton Cartridge - Generated from python
// Extracted 2 constraints

cartridge JesterAnalysis {
  // guard: amount <= 0
  constraint c0: amount <= 0;

  // guard: amount > balance
  constraint c1: amount / balance > 1.0;

  // Forbidden states
  forbidden: NOT (amount <= 0);
  forbidden: NOT (amount > balance);
}
```

---

## Architecture

```
+----------------------------------------------------------+
|                        JESTER                            |
+----------------------------------------------------------+
|                                                          |
|  +--------------+   +--------------+   +---------------+ |
|  |   Language   | > |    Regex     | > |  Constraint   | |
|  |   Detector   |   |   Extractor  |   |   Normalizer  | |
|  +--------------+   +--------------+   +---------------+ |
|         |                 |                   |          |
|         |           +-----+-----+             |          |
|         |           |Tree-Sitter|             |          |
|         |           | (optional)|             |          |
|         |           +-----------+             |          |
|         |                                     |          |
|         v                                     v          |
|  +--------------+                    +---------------+   |
|  |     CFG      |                    |    Newton     |   |
|  |   Analyzer   |                    |  Translator   |   |
|  +--------------+                    +---------------+   |
|         |                                     |          |
|         v                                     v          |
|  +--------------+                    +---------------+   |
|  | Unreachable  |                    |   Cartridge   |   |
|  |    States    |                    |   Generator   |   |
|  +--------------+                    +---------------+   |
|                                              |           |
+----------------------------------------------+-----------+
                                               v
                                    +------------------+
                                    | Newton Cartridge |
                                    |   (JSON / CDL)   |
                                    +------------------+
```

---

## The Compiler Perspective

Jester is the **lexer/parser** of constraint extraction:

| Traditional Compiler | Jester |
|---------------------|--------|
| Lexer -> Tokens | Language Detector -> Source Lang |
| Parser -> AST | Regex/Tree-Sitter -> Conditions |
| Semantic Analysis | Constraint Normalizer |
| Code Generation | CDL/Cartridge Emission |
| Optimization | CFG Unreachable Detection |

The output is not machine code. The output is **verified truth**.

---

## Why This Matters

### Before Jester

```
Developer writes code with guards
  -> Guards are implicit assumptions
  -> Assumptions are not verified
  -> Bugs happen at runtime
```

### After Jester

```
Developer writes code with guards
  -> Jester extracts guards as constraints
  -> Newton verifies constraints at compile time
  -> Invalid states cannot be constructed
```

---

## Integration Points

### Newton CDL
```python
from core import import_code
cartridge = import_code(source_code)
```

### Newton API
```
POST /jester/analyze
POST /jester/cdl
GET  /jester/info
```

### Web UI
```
/jester/  - Interactive code analyzer
```

---

## Version History

| Version | Features |
|---------|----------|
| 1.0.0 | Guard extraction, multi-language, CDL output |
| 1.1.0 | CFG analysis, unreachable state detection, @import_code |

---

## Credits

Jester implements concepts from:
- Waltz's constraint propagation (1975)
- Abstract interpretation (Cousot & Cousot, 1977)
- Design by Contract (Meyer, 1986)
- Dependent type theory

Built for the Newton Supercomputer.

---

*"The code is irrelevant - the state condition is the product."*
