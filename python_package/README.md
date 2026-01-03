# Newton Computer

**Verified computation with the TinyTalk constraint language.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Commercial-green.svg)](LICENSE)

Newton is a supercomputer built on the **"No-First" philosophy**: define what *cannot* happen, then execute safely. Instead of trying everything and catching errors, Newton prevents forbidden states from ever existing.

## Installation

```bash
# Client only (minimal dependencies)
pip install newton-computer

# With local server support
pip install newton-computer[server]

# Everything
pip install newton-computer[all]
```

## Quick Start (30 seconds)

```python
from newton import Blueprint, field, law, forge, when, finfr

class BankAccount(Blueprint):
    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        """Balance cannot go negative - ever."""
        when(self.balance < 0, finfr)

    @forge
    def withdraw(self, amount):
        self.balance -= amount
        return f"Withdrew ${amount}"

# Use it
account = BankAccount()
account.withdraw(50)   # Works: balance = 50
account.withdraw(60)   # BLOCKED! Would violate no_overdraft law
```

**That's it.** The `no_overdraft` law prevents the forbidden state (negative balance) from ever existing. No try/catch needed.

## The Philosophy

| Traditional Approach | Newton Approach |
|---------------------|-----------------|
| Try everything, catch errors | Define what cannot happen |
| Validate after the fact | Prevent before it happens |
| "Oops, let me fix that" | "That state cannot exist" |

## Core Concepts

### Blueprint
The base class for all Newton objects. Like a class, but with built-in constraint enforcement.

### field()
Declare typed state. Fields hold your data.

```python
balance = field(float, default=0.0)
name = field(str, default="")
```

### @law
Layer 0: Governance. Define forbidden states. If a law's condition becomes true, `finfr` is triggered.

```python
@law
def insolvency(self):
    when(self.liabilities > self.assets, finfr)
```

### @forge
Layer 1: Executive. Mutations that respect laws. Before a forge runs, all laws are checked.

```python
@forge
def execute_trade(self, amount):
    self.liabilities += amount
    return "cleared"
```

### finfr (Finality)
Ontological death. The state *cannot* exist. Not "shouldn't" - *cannot*.

### fin (Closure)
A stopping point that can be reopened. Less severe than finfr.

## Type-Safe Units (Matter)

Prevent unit confusion like the Mars Climate Orbiter disaster:

```python
from newton import Money, Mass, Distance

budget = Money(1000)
expense = Money(150)
remaining = budget - expense  # OK: Money - Money = Money

weight = Mass(50)
# budget + weight  # TypeError! Cannot add Money and Mass
```

Available Matter types:
- `Money` - Currency
- `Mass` - Weight (kg)
- `Distance` - Length (m)
- `Temperature` - Heat (C/F/K)
- `Pressure` - Force/area (PSI)
- `Volume` - Capacity (L)
- `Time` - Duration (s)
- `Velocity` - Speed (m/s)

## Kinetic Engine (State Transitions)

For game physics, animation, or any bounded state transitions:

```python
from newton import KineticEngine, Presence

engine = KineticEngine()

# Define boundaries
engine.add_boundary(
    lambda d: d.changes.get('x', {}).get('to', 0) > 100,
    name="MaxX"
)

start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 50, 'y': 25})

result = engine.resolve_motion(start, end)  # Allowed
```

## Remote Server (API)

Connect to a Newton server for verified computation:

```python
from newton import Newton

# Connect
newton = Newton("https://your-newton-server.com")

# Calculate with verification
result = newton.calculate({"op": "+", "args": [2, 3]})
print(result.result)  # 5

# Verify content
safe = newton.verify("Is this content safe?")
print(safe.verified)  # True/False

# Check constraints
check = newton.constraint(
    {"field": "balance", "operator": "ge", "value": 0},
    {"balance": 100}
)
```

## CLI

```bash
# Start local server
newton serve --port 8000

# Run demo
newton demo

# Calculate
newton calc "2 + 3"

# Verify content
newton verify "hello world"

# Create new project
newton init my_project
```

## Examples

### Trading System with Risk Limits

```python
from newton import Blueprint, field, law, forge, when, finfr, Money

class TradingDesk(Blueprint):
    position = field(Money, default=Money(0))
    max_position = field(Money, default=Money(1000000))

    @law
    def position_limit(self):
        when(abs(self.position.value) > self.max_position.value, finfr)

    @forge
    def trade(self, amount: Money):
        self.position = Money(self.position.value + amount.value)
        return f"Position: {self.position}"
```

### Thermostat with Safe Bounds

```python
from newton import Blueprint, field, law, forge, when, finfr

class Thermostat(Blueprint):
    temperature = field(float, default=20.0)

    @law
    def no_freezing(self):
        when(self.temperature < 0, finfr)

    @law
    def no_boiling(self):
        when(self.temperature > 100, finfr)

    @forge
    def set_temp(self, t):
        self.temperature = t
```

### Inventory That Can't Go Negative

```python
from newton import Blueprint, field, law, forge, when, finfr

class Inventory(Blueprint):
    stock = field(int, default=100)

    @law
    def no_negative_stock(self):
        when(self.stock < 0, finfr)

    @forge
    def sell(self, quantity):
        self.stock -= quantity
        return f"Sold {quantity}, remaining: {self.stock}"
```

## Advanced: Ratio Constraints (f/g)

For dimensional analysis and proportional limits:

```python
from newton import Blueprint, field, law, forge, when, finfr, ratio

class LeveragedFund(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=100.0)

    @law
    def leverage_limit(self):
        # debt/equity must be <= 3.0
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @forge
    def borrow(self, amount):
        self.debt += amount
```

## Documentation

- [TinyTalk Programming Guide](https://github.com/jaredlewiswechs/Newton-api/blob/main/TINYTALK_PROGRAMMING_GUIDE.md)
- [API Reference](https://github.com/jaredlewiswechs/Newton-api)
- [Examples](https://github.com/jaredlewiswechs/Newton-api/tree/main/examples)

## License

Commercial License. See [LICENSE](LICENSE) for details.

## Author

Created by Jared Lewis (jn.lewis1@outlook.com)
