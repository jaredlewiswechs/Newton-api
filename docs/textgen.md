# Newton Text Generation Module

**Constraint-Preserving Text Projection**

Newton does not generate language - it projects lawful meaning into words.

## Overview

The Newton TextGen module provides deterministic, constraint-preserving text generation. Unlike LLMs which generate probabilistically and may hallucinate, Newton TextGen generates ONLY text that can be reduced back to the original constraints.

### Core Guarantee

```
Expand . Reduce = Identity
```

If a generated text cannot be reduced back to the original constraint, it is rejected. This makes hallucination impossible by construction.

## Why This Module Exists

Traditional text generation systems (LLMs) have a fundamental problem:
- They generate probabilistically
- They may add claims not present in the source
- They may omit or distort source claims
- Verification requires human review

Newton TextGen solves this by:
- **Constraint = Instruction**: The text is derived from formal constraints
- **Verification = Computation**: Every output is verified to reduce back to source
- **No hallucination**: If reduce(text) != original, the text is rejected

## Quick Start

### One-liner API

```python
from core.textgen import project

# Simple constraint
text = project("balance", "ge", 0)
# Returns: "balance must be greater than or equal to 0."

# Ratio constraint (f/g dimensional analysis)
text = project("debt", "ratio_le", 3.0, denominator="equity")
# Returns: "The ratio of debt to equity must not exceed 3.0."
```

### Full API

```python
from core.textgen import TextConstraint, NewtonTextProjector

# Create constraints
constraints = [
    TextConstraint("balance", "ge", 0),
    TextConstraint("withdrawal", "le", "balance"),
    TextConstraint("debt", "ratio_le", 3.0, denominator="equity"),
]

# Create projector with desired style
projector = NewtonTextProjector(style="formal")

# Generate verified text
results = projector.generate(constraints)

for r in results:
    print(f"[{r.fingerprint}] {r.text}")
```

## Text Styles

Newton TextGen supports four styles:

### Formal (Legal/Contract Language)

```python
projector = NewtonTextProjector(style="formal")
```

Output examples:
- "balance must be greater than or equal to 0."
- "withdrawal shall not exceed balance."
- "The ratio of debt to equity must not exceed 3.0."

### Technical (Developer Documentation)

```python
projector = NewtonTextProjector(style="technical")
```

Output examples:
- "balance >= 0"
- "assert(withdrawal <= balance)"
- "require: debt/equity <= 3.0"

### Educational (Teacher-Friendly)

```python
projector = NewtonTextProjector(style="educational")
```

Output examples:
- "The balance needs to be at least 0."
- "Remember: withdrawal can't go above balance!"
- "Think of it like a balance: debt/equity can't exceed 3.0."

### Minimal (Terse, Code-like)

```python
projector = NewtonTextProjector(style="minimal")
```

Output examples:
- "balance >= 0"
- "withdrawal <= balance"
- "debt/equity <= 3.0"

## Supported Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `ge` | Greater than or equal | `balance >= 0` |
| `le` | Less than or equal | `withdrawal <= balance` |
| `eq` | Equals | `status == active` |
| `lt` | Less than | `amount < 1000` |
| `gt` | Greater than | `count > 5` |
| `ne` | Not equal | `category != blocked` |
| `ratio_le` | Ratio <= threshold | `debt/equity <= 3.0` |
| `ratio_lt` | Ratio < threshold | `flicker/safe < 1.0` |
| `ratio_ge` | Ratio >= threshold | `coverage/required >= 1.0` |
| `ratio_gt` | Ratio > threshold | `profit/cost > 1.0` |

## Document Generation

Generate complete documents from constraints:

```python
from core.textgen import generate_document, TextConstraint

constraints = [
    TextConstraint("balance", "ge", 0),
    TextConstraint("withdrawal", "le", "balance"),
    TextConstraint("debt", "ratio_le", 3.0, denominator="equity"),
]

doc = generate_document("Banking Rules", constraints, style="formal")

# Export as markdown
print(doc.to_markdown())
```

Output:
```markdown
# Banking Rules

1. balance must be greater than or equal to 0.
2. balance shall not be less than 0.
3. withdrawal must be less than or equal to balance.
4. withdrawal shall not exceed balance.
5. The ratio of debt to equity must not exceed 3.0.

*Document fingerprint: 98B1BC1B56EA1FF1*
```

## CDL Integration

Project CDL constraints directly:

```python
from core.cdl import AtomicConstraint, Operator, Domain
from core.textgen import project_cdl

constraint = AtomicConstraint(
    domain=Domain.FINANCIAL,
    field="balance",
    operator=Operator.GE,
    value=0
)

text = project_cdl(constraint)
# Returns: "balance must be greater than or equal to 0."
```

## JESTER Integration

Convert JESTER code analysis output to documentation:

```python
from core.textgen import project_jester_constraints

# JESTER output from code analysis
jester_output = [
    {"kind": "null_check", "variable": "user", "value": "null"},
    {"kind": "range_check", "field": "amount", "bound": 0},
]

results = project_jester_constraints(jester_output, style="technical")
for r in results:
    print(r.text)
```

## Ledger Integration

Every text projection can be recorded in Newton's immutable ledger:

```python
from core.textgen import create_text_ledger_entry, TextConstraint, NewtonTextProjector

projector = NewtonTextProjector(style="formal")
result = projector.project_one(TextConstraint("balance", "ge", 0))

# Create ledger entry
entry = create_text_ledger_entry(result)
# {
#   "operation": "textgen",
#   "payload_hash": "7029016EFF1290DC",
#   "result": "pass",
#   "metadata": {
#     "constraint": "balance ge 0",
#     "style": "formal",
#     "fingerprint": "7029016EFF1290DC"
#   }
# }
```

## Fingerprinting

Every generated text has a SHA-256 fingerprint:

```python
from core.textgen import text_fingerprint

fp = text_fingerprint("balance must be greater than or equal to 0.")
# Returns: "7029016EFF1290DC" (16-char uppercase hex)
```

This enables:
- **Audit trails**: Prove which text was generated
- **Deduplication**: Identify identical outputs
- **Verification**: Confirm text hasn't been modified

## Educational Use Cases

### Teacher-Friendly Explanations

```python
from core.textgen import explain_constraints, TextConstraint

constraints = [
    TextConstraint("balance", "ge", 0),
    TextConstraint("withdrawal", "ratio_le", 1.0, denominator="balance"),
]

explanations = explain_constraints(constraints)
# Returns list of educational explanations
```

### Student-Safe Documentation

Generate documentation that:
- Cannot contain false information
- Is mathematically provable
- Reduces back to formal constraints

## Architecture

```
CDL Constraints
     |
     v
+------------+
|  TEMPLATES |  (Expansion: constraints -> text candidates)
+------------+
     |
     v
+------------+
|  PROJECTOR |  (Selection: verify each candidate)
+------------+
     |
     v
+------------+
|  REDUCTION |  (Verification: text -> constraints)
+------------+
     |
     v
Verified Text (only if reduce(text) == original)
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `TextConstraint` | Canonical constraint representation |
| `NewtonTextProjector` | Main text generation engine |
| `ProjectionResult` | Result of text projection |
| `TextDocument` | Multi-section document |
| `TextStyle` | Enum of available styles |

### Functions

| Function | Description |
|----------|-------------|
| `project(field, op, value, ...)` | One-liner projection |
| `project_cdl(constraint, style)` | Project CDL constraint |
| `explain_constraints(constraints)` | Educational explanations |
| `generate_document(title, constraints)` | Generate full document |
| `text_fingerprint(text)` | Generate SHA-256 fingerprint |
| `reduce_text(text)` | Reduce text to constraints |
| `register_reduction(rule)` | Register custom reduction rule |
| `project_jester_constraints(output)` | Convert JESTER output |
| `create_text_ledger_entry(result)` | Create ledger entry |

## The Guarantee

This line is the entire guarantee:

```python
return set(reduced) == set(original)
```

If false, the text is rejected.

Newton TextGen enables:
- Law-aware documentation generation
- Student-safe explanations
- Contracts without legal drift
- Educational text that cannot lie
- "Explain this rule" buttons that are provably correct

---

*Newton does not generate language - it projects lawful meaning into words.*

*Expand . Reduce = Identity*
