# Jester - Newton Code Constraint Translator

**Jester** is a deterministic code analyzer that extracts constraints, guard conditions, and invariants from source code and produces Newton cartridge representations.

## What Jester Does

Unlike AI-powered code analysis that "guesses" intent, Jester performs **rule-based extraction** using Abstract Syntax Tree (AST) parsing. It translates structural conditions into a formal constraint model.

### Extracts:
- **Guard Conditions** - `if` statements that protect against invalid states
- **Assertions** - Explicit requirements that must be true
- **Early Exits** - Return statements that prevent further execution
- **Null Checks** - Validation against null/nil/None values
- **Range Checks** - Bounds validation for numeric values
- **Exception Paths** - Conditions that lead to thrown errors

### Produces:
- **Newton Cartridge (JSON)** - Structured constraint representation
- **CDL Output** - Constraint Definition Language for verification
- **Forbidden States** - What states are not allowed
- **Required Invariants** - What must always be true

## Supported Languages

| Language | Extensions | Status |
|----------|------------|--------|
| Python | `.py` | Full |
| JavaScript | `.js`, `.mjs` | Full |
| TypeScript | `.ts`, `.tsx` | Full |
| Swift | `.swift` | Full |
| Objective-C | `.m`, `.mm` | Full |
| C | `.c`, `.h` | Full |
| C++ | `.cpp`, `.cc`, `.hpp` | Full |
| Java | `.java` | Full |
| Go | `.go` | Full |
| Rust | `.rs` | Full |
| Ruby | `.rb` | Full |

## API Endpoints

### `POST /jester/analyze`
Analyze source code to extract constraints.

```json
{
  "code": "def withdraw(amount, balance):\n    if amount <= 0:\n        raise ValueError('Invalid')\n    if amount > balance:\n        return None",
  "language": "python"
}
```

**Response:**
```json
{
  "source_language": "python",
  "constraints": [
    {
      "kind": "guard",
      "raw_condition": "amount <= 0",
      "normalized_form": "amount <= 0",
      "newton_constraint": "amount / 0 <= 1.0",
      "line_number": 2,
      "context": "Conditional check"
    }
  ],
  "forbidden_states": ["NOT (amount <= 0)"],
  "required_invariants": [],
  "summary": {"total_constraints": 2, "by_kind": {"guard": 2}}
}
```

### `POST /jester/cdl`
Generate CDL (Constraint Definition Language) output.

```json
{
  "code": "...",
  "language": "python"
}
```

**Response:**
```json
{
  "cdl": "// Newton Cartridge - Generated from python\n...",
  "constraint_count": 2
}
```

### `GET /jester/info`
Get analyzer capabilities and documentation.

### `GET /jester/languages`
List supported programming languages.

### `GET /jester/constraint-kinds`
List constraint types that can be extracted.

## Architecture

```
Code Input
    |
    v
Language Detector (auto-detect from patterns)
    |
    v
AST Parser (tree-sitter or regex fallback)
    |
    v
Constraint Extractor (guards, assertions, early exits)
    |
    v
Constraint Normalizer (standardize to Newton format)
    |
    v
Newton Cartridge Generator
    |
    v
JSON / CDL Output
```

## Why This Matters

Instead of saying "AI analyzed this code", Jester explicitly articulates:

- **What states are forbidden** (red)
- **What must always be true** (green)
- **What the function legally expects** (blue)

This is what Newton means by **correctness** - explicit, verifiable constraints.

No hallucination. No guessing. Just deterministic extraction of the rules your code already implies.

## Local Development

Access at: `http://localhost:8000/jester/`

## Deployment

Jester is deployed as part of the Newton Supercomputer API:
- Frontend: `/jester/`
- API: `/jester/analyze`, `/jester/cdl`, `/jester/info`

---

*"The code is irrelevant - the state condition is the product."*
