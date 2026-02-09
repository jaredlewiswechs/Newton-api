# Newton SDK

**Verified computation for everyone.**

```python
import newton

# Verify a claim
result = newton.verify("2 + 2 equals 4")
print(result)  # VerificationResult(✓, confidence=1.00)

# Check constraints
newton.check(25, newton.gt(18))  # True

# Calculate with verification
newton.calc("sqrt(16) + 2")  # 6.0

# Ground claims in evidence
newton.ground("Python was created by Guido van Rossum")
```

## Installation

```bash
pip install newton-sdk
```

Or from source:
```bash
git clone https://github.com/newton/newton-sdk
cd newton-sdk
pip install -e .
```

## Quick Start

### Verification

```python
import newton

# Mathematical verification
result = newton.verify("5 + 3 equals 8")
print(result.verified)    # True
print(result.confidence)  # 1.0

# With context
result = newton.verify(
    "The user is an adult",
    context={"user_age": 25}
)
```

### Constraints

```python
from newton import check, gt, lt, ge, le, eq, ne
from newton import contains, matches, between
from newton import all_of, any_of, is_in

# Simple constraints
check(25, gt(18))           # True - greater than 18
check(10, between(1, 100))  # True - between 1 and 100
check("hello", contains("ell"))  # True

# Compound constraints
check(25, all_of(gt(18), lt(65)))  # True - adult working age
check("admin", is_in(["admin", "user", "guest"]))  # True

# Object constraints
user = {"name": "Alice", "age": 25, "role": "admin"}
check(user, {
    "age": gt(18),
    "role": is_in(["admin", "user"])
})  # True
```

### Calculations

```python
from newton import calc

# Basic math
calc("2 + 2")           # 4
calc("10 / 3")          # 3.333...
calc("2 ** 10")         # 1024

# Functions
calc("sqrt(16)")        # 4.0
calc("max(1, 5, 3)")    # 5
calc("sin(pi / 2)")     # 1.0
calc("log(e)")          # 1.0

# Complex expressions
calc("sqrt(16) + 2 * 3")  # 10.0
```

### Grounding

```python
from newton import ground

# Ground claims in evidence
result = ground("Python was created by Guido van Rossum")
print(result.grounded)    # True
print(result.sources)     # ['https://...', ...]
print(result.confidence)  # 0.7
```

### Decorators

```python
from newton import verified, bounded, constrained
from newton import gt, is_not_none

# Verified functions log all calls
@verified
def process(data):
    return data * 2

# Bounded functions are guaranteed to terminate
@bounded(max_iterations=1000, timeout_seconds=5.0)
def process_items(items):
    for item in items:
        yield item * 2

# Constrained functions enforce input/output rules
@constrained(input=gt(0), output=gt(0))
def double_positive(x):
    return x * 2

double_positive(5)   # 10
double_positive(-1)  # Raises ValueError
```

## The Newton Class

For more control, use the `Newton` class:

```python
from newton import Newton
from newton.types import Bounds

# Create with custom bounds
n = Newton(bounds=Bounds(
    max_iterations=10_000,
    max_operations=1_000_000,
    timeout_seconds=30.0
))

# All operations
n.verify("claim")
n.check(value, constraint)
n.calc("expression")
n.ground("claim")

# Access audit log
for entry in n.audit_log:
    print(entry.timestamp, entry.action, entry.verified)
```

## Constraint Reference

### Comparison
- `eq(value)` - Equal to
- `ne(value)` - Not equal to
- `lt(value)` - Less than
- `gt(value)` - Greater than
- `le(value)` - Less than or equal
- `ge(value)` - Greater than or equal
- `between(low, high)` - Between (inclusive)

### String
- `contains(substring)` - Contains substring
- `starts_with(prefix)` - Starts with
- `ends_with(suffix)` - Ends with
- `matches(pattern)` - Matches regex
- `length(constraint)` - Check length

### Collection
- `is_in(collection)` - Value in collection
- `not_in(collection)` - Value not in collection
- `is_empty()` - Is empty
- `is_not_empty()` - Is not empty

### Type
- `is_type(type)` - Is instance of type
- `is_none()` - Is None
- `is_not_none()` - Is not None

### Temporal
- `within(seconds)` - Within N seconds of now
- `after(timestamp)` - After timestamp
- `before(timestamp)` - Before timestamp

### Composite
- `all_of(*constraints)` - All must pass (AND)
- `any_of(*constraints)` - Any must pass (OR)
- `none_of(*constraints)` - None must pass (NOR)

### Operators
```python
# Combine with operators
adult = gt(18)
senior = gt(65)

working_age = adult & ~senior  # AND + NOT
any_adult = adult | senior     # OR
```

## The Fundamental Law

```python
from newton import newton

# newton(current, goal) returns current == goal
# When true → execute
# When false → halt

newton(1, 1)  # True
newton(1, 2)  # False
```

This isn't a feature. It's the architecture.

> "1 == 1. The cloud is weather. We're building shelter."

## License

MIT License - see LICENSE file.
