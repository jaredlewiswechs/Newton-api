# Newton Logic Engine

**Verified Turing Completeness**

The Logic Engine gives Newton the ability to calculate anything a traditional computer can calculate. The difference: every computation is verified and bounded.

---

## Overview

```
Newton can calculate anything El Capitan can.
Just verified.
```

The Logic Engine provides:
- Full arithmetic and mathematical operations
- Boolean logic with all standard gates
- Conditional branching (if/else, multi-branch)
- Bounded loops (for, while, map, filter, reduce)
- First-class functions (def, call, lambda)
- Variables and assignment
- List operations

All execution is bounded to guarantee termination.

---

## Quick Start

```bash
# Simple arithmetic
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'

# Response
{
  "result": "5",
  "type": "number",
  "verified": true,
  "operations": 3,
  "elapsed_us": 42
}
```

---

## Operators

### Arithmetic

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `+` | Addition | `{"op": "+", "args": [2, 3]}` | `5` |
| `-` | Subtraction | `{"op": "-", "args": [10, 4]}` | `6` |
| `*` | Multiplication | `{"op": "*", "args": [3, 4]}` | `12` |
| `/` | Division | `{"op": "/", "args": [15, 3]}` | `5` |
| `%` | Modulo | `{"op": "%", "args": [17, 5]}` | `2` |
| `**` | Power | `{"op": "**", "args": [2, 8]}` | `256` |
| `neg` | Negate | `{"op": "neg", "args": [5]}` | `-5` |
| `abs` | Absolute | `{"op": "abs", "args": [-7]}` | `7` |

### Boolean

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `and` | Logical AND | `{"op": "and", "args": [true, false]}` | `false` |
| `or` | Logical OR | `{"op": "or", "args": [true, false]}` | `true` |
| `not` | Logical NOT | `{"op": "not", "args": [true]}` | `false` |
| `xor` | Exclusive OR | `{"op": "xor", "args": [true, true]}` | `false` |
| `nand` | NOT AND | `{"op": "nand", "args": [true, true]}` | `false` |
| `nor` | NOT OR | `{"op": "nor", "args": [false, false]}` | `true` |

### Comparison

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `==` | Equal | `{"op": "==", "args": [5, 5]}` | `true` |
| `!=` | Not equal | `{"op": "!=", "args": [5, 3]}` | `true` |
| `<` | Less than | `{"op": "<", "args": [3, 5]}` | `true` |
| `>` | Greater than | `{"op": ">", "args": [5, 3]}` | `true` |
| `<=` | Less or equal | `{"op": "<=", "args": [5, 5]}` | `true` |
| `>=` | Greater or equal | `{"op": ">=", "args": [5, 5]}` | `true` |

### Math Functions

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `sqrt` | Square root | `{"op": "sqrt", "args": [16]}` | `4` |
| `log` | Natural log | `{"op": "log", "args": [2.718]}` | `~1` |
| `sin` | Sine | `{"op": "sin", "args": [0]}` | `0` |
| `cos` | Cosine | `{"op": "cos", "args": [0]}` | `1` |
| `tan` | Tangent | `{"op": "tan", "args": [0]}` | `0` |
| `floor` | Floor | `{"op": "floor", "args": [3.7]}` | `3` |
| `ceil` | Ceiling | `{"op": "ceil", "args": [3.2]}` | `4` |
| `round` | Round | `{"op": "round", "args": [3.5]}` | `4` |
| `min` | Minimum | `{"op": "min", "args": [3, 7, 2]}` | `2` |
| `max` | Maximum | `{"op": "max", "args": [3, 7, 2]}` | `7` |
| `sum` | Sum list | `{"op": "sum", "args": [[1, 2, 3]]}` | `6` |

---

## Control Flow

### if - Conditional

```json
{
  "op": "if",
  "args": [
    {"op": ">", "args": [10, 5]},  // condition
    "yes",                          // if true
    "no"                            // if false
  ]
}
// → "yes"
```

### cond - Multi-branch

```json
{
  "op": "cond",
  "args": [
    [{"op": "<", "args": [{"op": "var", "args": ["x"]}, 0]}, "negative"],
    [{"op": "==", "args": [{"op": "var", "args": ["x"]}, 0]}, "zero"],
    [true, "positive"]  // default case
  ]
}
```

---

## Loops

All loops are bounded by `max_iterations` to guarantee termination.

### for - Bounded Iteration

```json
{
  "op": "for",
  "args": [
    "i",                                    // variable name
    0,                                      // start
    5,                                      // end (exclusive)
    {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}  // body
  ]
}
// → [0, 2, 4, 6, 8]
```

### while - Conditional Loop

```json
{
  "op": "block",
  "args": [
    {"op": "let", "args": ["x", 1]},
    {"op": "while", "args": [
      {"op": "<", "args": [{"op": "var", "args": ["x"]}, 10]},
      {"op": "set", "args": ["x", {"op": "*", "args": [{"op": "var", "args": ["x"]}, 2]}]}
    ]},
    {"op": "var", "args": ["x"]}
  ]
}
// → 16 (1 → 2 → 4 → 8 → 16)
```

### map - Transform List

```json
{
  "op": "map",
  "args": [
    {"op": "lambda", "args": [["x"], {"op": "*", "args": [{"op": "var", "args": ["x"]}, 2]}]},
    {"op": "list", "args": [1, 2, 3, 4, 5]}
  ]
}
// → [2, 4, 6, 8, 10]
```

### filter - Select Elements

```json
{
  "op": "filter",
  "args": [
    {"op": "lambda", "args": [["x"], {"op": ">", "args": [{"op": "var", "args": ["x"]}, 2]}]},
    {"op": "list", "args": [1, 2, 3, 4, 5]}
  ]
}
// → [3, 4, 5]
```

### reduce - Aggregate

```json
{
  "op": "reduce",
  "args": [
    {"op": "lambda", "args": [
      ["acc", "x"],
      {"op": "+", "args": [{"op": "var", "args": ["acc"]}, {"op": "var", "args": ["x"]}]}
    ]},
    0,                                      // initial value
    {"op": "list", "args": [1, 2, 3, 4, 5]} // list
  ]
}
// → 15
```

---

## Functions

### def - Define Function

```json
{
  "op": "block",
  "args": [
    {"op": "def", "args": ["square", ["x"],
      {"op": "*", "args": [{"op": "var", "args": ["x"]}, {"op": "var", "args": ["x"]}]}
    ]},
    {"op": "call", "args": ["square", 5]}
  ]
}
// → 25
```

### lambda - Anonymous Function

```json
{
  "op": "lambda",
  "args": [
    ["x", "y"],                              // parameters
    {"op": "+", "args": [{"op": "var", "args": ["x"]}, {"op": "var", "args": ["y"]}]}
  ]
}
```

### call - Invoke Function

```json
{
  "op": "call",
  "args": ["functionName", arg1, arg2, ...]
}
```

---

## Variables

### let - Declare Variable

```json
{"op": "let", "args": ["x", 10]}
```

### set - Update Variable

```json
{"op": "set", "args": ["x", 20]}
```

### var - Read Variable

```json
{"op": "var", "args": ["x"]}
```

---

## Sequences

### block - Sequential Execution

```json
{
  "op": "block",
  "args": [
    {"op": "let", "args": ["x", 5]},
    {"op": "let", "args": ["y", 10]},
    {"op": "+", "args": [{"op": "var", "args": ["x"]}, {"op": "var", "args": ["y"]}]}
  ]
}
// → 15 (returns last expression)
```

### list - Create List

```json
{"op": "list", "args": [1, 2, 3, 4, 5]}
// → [1, 2, 3, 4, 5]
```

### index - Access Element

```json
{
  "op": "index",
  "args": [
    {"op": "list", "args": [10, 20, 30]},
    1
  ]
}
// → 20
```

### len - List Length

```json
{
  "op": "len",
  "args": [{"op": "list", "args": [1, 2, 3, 4, 5]}]
}
// → 5
```

---

## Bounded Execution

Every computation has limits. This is what makes Newton verified.

```python
ExecutionBounds(
    max_iterations=10000,       # No infinite loops
    max_recursion_depth=100,    # No stack overflow
    max_operations=1000000,     # No runaway compute
    timeout_seconds=30.0        # No endless waits
)
```

### Configuring Bounds

```json
{
  "expression": {"op": "for", "args": ["i", 0, 100000, {"op": "var", "args": ["i"]}]},
  "max_iterations": 100000,
  "max_operations": 10000000,
  "timeout_seconds": 60.0
}
```

### Bound Limits

| Bound | Default | Maximum |
|-------|---------|---------|
| `max_iterations` | 10,000 | 100,000 |
| `max_operations` | 1,000,000 | 10,000,000 |
| `timeout_seconds` | 30.0 | 60.0 |
| `max_recursion_depth` | 100 | 1,000 |

---

## Examples

### Factorial

```json
{
  "op": "block",
  "args": [
    {"op": "def", "args": ["factorial", ["n"],
      {"op": "if", "args": [
        {"op": "<=", "args": [{"op": "var", "args": ["n"]}, 1]},
        1,
        {"op": "*", "args": [
          {"op": "var", "args": ["n"]},
          {"op": "call", "args": ["factorial", {"op": "-", "args": [{"op": "var", "args": ["n"]}, 1]}]}
        ]}
      ]}
    ]},
    {"op": "call", "args": ["factorial", 10]}
  ]
}
// → 3628800
```

### Fibonacci

```json
{
  "op": "block",
  "args": [
    {"op": "def", "args": ["fib", ["n"],
      {"op": "if", "args": [
        {"op": "<=", "args": [{"op": "var", "args": ["n"]}, 1]},
        {"op": "var", "args": ["n"]},
        {"op": "+", "args": [
          {"op": "call", "args": ["fib", {"op": "-", "args": [{"op": "var", "args": ["n"]}, 1]}]},
          {"op": "call", "args": ["fib", {"op": "-", "args": [{"op": "var", "args": ["n"]}, 2]}]}
        ]}
      ]}
    ]},
    {"op": "call", "args": ["fib", 10]}
  ]
}
// → 55
```

### Prime Check

```json
{
  "op": "block",
  "args": [
    {"op": "let", "args": ["n", 17]},
    {"op": "let", "args": ["is_prime", true]},
    {"op": "for", "args": ["i", 2, {"op": "var", "args": ["n"]},
      {"op": "if", "args": [
        {"op": "==", "args": [{"op": "%", "args": [{"op": "var", "args": ["n"]}, {"op": "var", "args": ["i"]}]}, 0]},
        {"op": "set", "args": ["is_prime", false]},
        null
      ]}
    ]},
    {"op": "var", "args": ["is_prime"]}
  ]
}
// → true
```

### Sum of Squares

```json
{
  "op": "reduce",
  "args": [
    {"op": "lambda", "args": [["acc", "x"],
      {"op": "+", "args": [
        {"op": "var", "args": ["acc"]},
        {"op": "*", "args": [{"op": "var", "args": ["x"]}, {"op": "var", "args": ["x"]}]}
      ]}
    ]},
    0,
    {"op": "for", "args": ["i", 1, 11, {"op": "var", "args": ["i"]}]}
  ]
}
// → 385 (1² + 2² + ... + 10²)
```

---

## Value Types

The Logic Engine supports these value types:

| Type | Examples |
|------|----------|
| `number` | `42`, `3.14`, `-17` |
| `boolean` | `true`, `false` |
| `string` | `"hello"`, `"world"` |
| `null` | `null` |
| `list` | `[1, 2, 3]` |
| `function` | Lambda or defined function |

---

## Error Handling

### Iteration Exceeded

```json
{
  "error": "Exceeded maximum iterations (10000)",
  "code": 429
}
```

### Operation Limit

```json
{
  "error": "Exceeded maximum operations (1000000)",
  "code": 429
}
```

### Timeout

```json
{
  "error": "Execution exceeded timeout of 30.0 seconds",
  "code": 408
}
```

### Recursion Depth

```json
{
  "error": "Maximum recursion depth exceeded (100)",
  "code": 429
}
```

### Division by Zero

```json
{
  "error": "Division by zero",
  "code": 400
}
```

---

## Why Bounded?

Traditional computers can run forever. Newton cannot.

This is a feature, not a limitation.

**Unbounded execution:**
- No guarantee of termination
- Resource exhaustion attacks possible
- Cannot audit what hasn't finished
- "Halting problem" unsolvable

**Bounded execution:**
- Guaranteed termination
- Fixed resource consumption
- Complete audit trail
- Every computation finishes

Newton proves that every computation will terminate before it starts. This is what makes Newton a verified supercomputer.

---

## The Closure Condition

Every Newton computation reduces to:

```python
def newton(current, goal):
    return current == goal

# 1 == 1 → execute
# 1 != 1 → halt
```

The Logic Engine evaluates expressions. The closure condition determines if the result is valid. Together, they form verified computation.

---

© 2025-2026 Ada Computing Company · Houston, Texas

*"Newton can calculate anything. Just verified."*
