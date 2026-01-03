# TinyTalk API Reference

Complete reference for the TinyTalk constraint language.

## Core Primitives

### Blueprint

Base class for all TinyTalk objects.

```python
from newton import Blueprint

class MyClass(Blueprint):
    # Define fields, laws, and forges here
    pass
```

**Methods:**
- `_get_state() -> Dict[str, Any]` - Get current field values
- `_check_laws() -> Tuple[bool, Optional[Law]]` - Check all laws

### field(type_, default=None)

Declare a typed field.

```python
from newton import Blueprint, field

class Person(Blueprint):
    name = field(str, default="")
    age = field(int, default=0)
    balance = field(float, default=0.0)
```

**Parameters:**
- `type_` - The Python type (int, float, str, etc.)
- `default` - Default value when not provided

### @law

Decorator to mark a method as a governance law.

```python
from newton import Blueprint, field, law, when, finfr

class Account(Blueprint):
    balance = field(float, default=0.0)

    @law
    def no_overdraft(self):
        """Balance must never be negative."""
        when(self.balance < 0, finfr)
```

Laws are evaluated **after** each forge completes. If a law triggers `finfr`, the forge is rolled back.

### @forge

Decorator to mark a method as an executive mutation.

```python
from newton import Blueprint, field, forge

class Counter(Blueprint):
    count = field(int, default=0)

    @forge
    def increment(self, amount: int = 1):
        self.count += amount
        return self.count
```

Forges:
1. Save current state
2. Execute the mutation
3. Check all laws
4. If any law triggers `finfr`, rollback and raise `LawViolation`

### when(condition, result=None)

Declare a fact. Used inside laws.

```python
from newton import when, finfr

# Trigger finfr if condition is true
when(self.balance < 0, finfr)

# Just check a condition (returns bool)
is_positive = when(self.balance > 0)
```

**Parameters:**
- `condition` - Boolean expression
- `result` - `finfr` or `fin` (optional)

### finfr

Finality. Ontological death. The state **cannot** exist.

```python
from newton import when, finfr

when(self.value < 0, finfr)  # Negative values cannot exist
```

### fin

Closure. A stopping point that can be reopened. Less severe than `finfr`.

```python
from newton import when, fin

when(self.is_complete, fin)  # Closed but can reopen
```

### LawViolation

Exception raised when a law's `finfr` condition is triggered.

```python
from newton import LawViolation

try:
    account.withdraw(1000)
except LawViolation as e:
    print(f"Blocked by law: {e.law_name}")
    print(f"Message: {e.message}")
```

### FinClosure

Exception raised when a law's `fin` condition is triggered.

```python
from newton import FinClosure

try:
    task.complete()
except FinClosure as e:
    print(f"Task closed: {e.law_name}")
```

## Ratio System (f/g)

### ratio(f, g, epsilon=1e-9)

Calculate the f/g ratio for dimensional analysis.

```python
from newton import ratio, when, finfr

# Check if ratio exceeds threshold
when(ratio(self.debt, self.equity) > 3.0, finfr)

# Check if ratio is below threshold
when(ratio(self.withdrawal, self.balance) > 1.0, finfr)
```

**Parameters:**
- `f` - Numerator (forge/fact/function)
- `g` - Denominator (ground/goal/governance)
- `epsilon` - Tolerance for zero comparison

**Returns:** `RatioResult` that supports comparison operators

### RatioResult

Result of a ratio calculation.

```python
r = ratio(100, 50)
print(r.value)      # 2.0
print(r.undefined)  # False
print(r > 1.5)      # True
```

**Properties:**
- `value: float` - The calculated ratio
- `undefined: bool` - True if denominator ≈ 0
- `f: float` - Original numerator
- `g: float` - Original denominator

### finfr_if_undefined(f, g, epsilon=1e-9)

Trigger finfr if the ratio is undefined (g ≈ 0).

```python
from newton import finfr_if_undefined

@law
def valid_divisor(self):
    finfr_if_undefined(self.numerator, self.denominator)
```

## Matter Types (Type-Safe Units)

### Matter (Base Class)

Abstract base for all typed values.

```python
from newton import Matter

# All Matter types support:
# - Addition/subtraction (same type only)
# - Multiplication/division by scalars
# - Comparison (same type only)
```

### Money

Monetary value.

```python
from newton import Money

budget = Money(1000)
expense = Money(150, "EUR")  # With currency

remaining = budget - expense  # OK if same currency
scaled = budget * 2           # Money(2000)
```

### Mass

Weight/mass value. Default unit: kg.

```python
from newton import Mass, Kilograms

weight = Mass(50)
also_weight = Kilograms(50)
```

### Distance

Length value. Default unit: m.

```python
from newton import Distance, Meters

length = Distance(100)
also_length = Meters(100)
```

### Temperature

Temperature with unit conversion.

```python
from newton import Temperature, Celsius, Fahrenheit

temp_c = Celsius(20)
temp_f = Fahrenheit(68)

# Convert
in_celsius = temp_f.to_celsius()
in_fahrenheit = temp_c.to_fahrenheit()
in_kelvin = temp_c.to_kelvin()
```

### Pressure

Force per area. Default unit: PSI.

```python
from newton import Pressure, PSI

p = Pressure(30)
also_p = PSI(30)
```

### Volume

Capacity. Default unit: L.

```python
from newton import Volume, Liters

v = Volume(5)
also_v = Liters(5)
```

### Time

Duration. Default unit: s.

```python
from newton import Time

duration = Time(60)  # 60 seconds
```

### Velocity

Speed. Default unit: m/s.

```python
from newton import Velocity

speed = Velocity(10)  # 10 m/s
```

### FlowRate

Flow rate. Default unit: L/min.

```python
from newton import FlowRate

flow = FlowRate(5)  # 5 L/min
```

## Kinetic Engine

### Presence

A snapshot of state.

```python
from newton import Presence

start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 100, 'y': 50})

# Calculate delta
delta = end - start
```

**Properties:**
- `state: Dict[str, Any]` - The state values
- `timestamp: Optional[float]` - When this state occurred
- `label: str` - Optional label

### Delta

The difference between two presences.

```python
from newton import Presence

start = Presence({'x': 0})
end = Presence({'x': 100})

delta = end - start
print(delta.changes)
# {'x': {'from': 0, 'to': 100, 'delta': 100}}
```

**Properties:**
- `changes: Dict[str, Any]` - The changes
- `source: Optional[Presence]` - Starting state
- `target: Optional[Presence]` - Ending state

### KineticEngine

Master motion engine for bounded state transitions.

```python
from newton import KineticEngine, Presence

engine = KineticEngine()

# Add boundary
engine.add_boundary(
    lambda d: d.changes.get('x', {}).get('to', 0) > 100,
    name="MaxX"
)

# Resolve motion
result = engine.resolve_motion(
    Presence({'x': 0}),
    Presence({'x': 50})
)

print(result['status'])  # 'synchronized' or 'finfr'
```

**Methods:**
- `add_boundary(check, name="")` - Add a boundary check
- `resolve_motion(start, end, signal=None)` - Resolve motion
- `interpolate(start, end, steps=10)` - Generate intermediate states

### motion(start, end)

Quick helper to calculate motion.

```python
from newton import motion

delta = motion({'x': 0}, {'x': 100})
print(delta.changes)
```

## Client API

### Newton

Client for Newton Supercomputer server.

```python
from newton import Newton

newton = Newton("http://localhost:8000")
newton = Newton("https://newton-api.onrender.com", api_key="...")
```

**Methods:**

```python
# Health check
health = newton.health()

# Verified calculation
result = newton.calculate({"op": "+", "args": [2, 3]})
print(result.result)  # 5

# Content verification
result = newton.verify("Is this safe?")
print(result.verified)  # True/False

# Constraint evaluation
result = newton.constraint(
    {"field": "balance", "operator": "ge", "value": 0},
    {"balance": 100}
)

# Grounding (fact-checking)
result = newton.ground("The Earth is round", confidence=0.8)

# Robust statistics
result = newton.statistics([1, 2, 3, 4, 100])  # MAD over mean

# Convenience methods
newton.add(2, 3)       # 5.0
newton.subtract(5, 3)  # 2.0
newton.multiply(4, 5)  # 20.0
newton.divide(10, 2)   # 5.0
newton.is_safe("text") # True/False
```

### NewtonError

Exception from Newton server.

```python
from newton import Newton, NewtonError

try:
    result = newton.calculate({"op": "invalid"})
except NewtonError as e:
    print(e.message)
    print(e.code)
    print(e.details)
```

## Server

### serve(host, port, reload)

Start the Newton server.

```python
from newton import serve

serve(host="0.0.0.0", port=8000, reload=False)
```

Or from CLI:
```bash
newton serve --port 8000
```
