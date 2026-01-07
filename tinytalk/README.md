# tinyTalk

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   tinyTalk                                                   │
    │   Smalltalk is back. With boundaries.                        │
    │                                                              │
    │   "Objects all the way down,                                 │
    │    but some states cannot exist."                            │
    │                                                              │
    │   finfr = f/g — The ratio IS the constraint.                 │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

**The "No-First" constraint language. Define what cannot happen.**

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Available for **Python**, **Ruby**, and **R**.

---

## The Idea

```
Traditional:  "Here's what to do, step by step."
tinyTalk:     "Here's what CANNOT happen."
```

**Smalltalk** gave us objects and messages.
**tinyTalk** adds boundaries and laws.

---

## Install

```bash
# From Newton-api directory
pip install -e .

# Then just import
from newton_sdk import Blueprint, field, law, forge, when, finfr, ratio
```

---

## The Five Sacred Words

| Word | Meaning | When to Use |
|------|---------|-------------|
| `when` | "This is true" | Declaring facts |
| `and` | "Also this" | Combining conditions |
| `fin` | "Stop here" | Soft closure (can reopen) |
| `finfr` | "FORBIDDEN" | Hard stop. Ontological death. |
| `ratio` | "f divided by g" | Dimensional constraint checking |

---

## Quick Start

### Python 🐍

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr, ratio

class BankAccount(Blueprint):
    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)  # This state CANNOT exist

    @forge
    def withdraw(self, amount):
        self.balance -= amount
        return f"Withdrew ${amount}"

# Use it
account = BankAccount()
account.withdraw(50)    # ✓ Works
account.withdraw(60)    # ✗ BLOCKED by no_overdraft
```

### Ruby 💎

```ruby
require_relative 'tinytalk/ruby/tinytalk'
include TinyTalk

class BankAccount < Blueprint
  field :balance, Float, default: 100.0

  law :no_overdraft do
    when_condition(balance < 0) { finfr }
  end

  forge :withdraw do |amount|
    self.balance = balance - amount
    "Withdrew $#{amount}"
  end
end

account = BankAccount.new
account.withdraw(50)    # ✓ Works
account.withdraw(60)    # ✗ Raises Finfr
```

### R 📊

```r
source("tinytalk/r/tinytalk.R")

BankAccount <- Blueprint(
  fields = list(balance = 100.0),
  laws = list(
    no_overdraft = function(self) {
      when_cond(self$balance < 0, function() finfr())
    }
  ),
  forges = list(
    withdraw = function(self, amount) {
      self$balance <- self$balance - amount
      paste("Withdrew $", amount)
    }
  )
)

account <- BankAccount$new()
account$withdraw(50)    # ✓ Works
account$withdraw(60)    # ✗ Error: finfr
```

---

## NEW: f/g Ratio Constraints

**finfr = f/g** — Every constraint is a ratio between what you're trying to do (f) and what reality allows (g).

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr, ratio

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        # Debt-to-equity ratio cannot exceed 3:1
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @forge
    def take_loan(self, amount: float):
        self.debt += amount

# Use it
gov = LeverageGovernor()
gov.take_loan(2000)   # ✓ Works (ratio = 2.0)
gov.take_loan(1500)   # ✗ BLOCKED (ratio would be 3.5 > 3.0)
```

### Use Cases

| Domain | Constraint | f | g | Threshold |
|--------|------------|---|---|-----------|
| **Banking** | No overdraft | withdrawal | balance | ≤ 1.0 |
| **Finance** | Leverage limit | debt | equity | ≤ 3.0 |
| **Healthcare** | Seizure safety | flicker_rate | safe_limit | < 1.0 |
| **Education** | Class size | students | capacity | ≤ 1.0 |

---

## The Three Layers

```
╭─────────────────────────────────────────────────────╮
│  Layer 2: APPLICATION                               │
│  Your code. Your use case.                          │
├─────────────────────────────────────────────────────┤
│  Layer 1: EXECUTIVE                                 │
│  field() = state    forge() = actions               │
├─────────────────────────────────────────────────────┤
│  Layer 0: GOVERNANCE                                │
│  law() = physics    finfr = impossible              │
│  ratio() = dimensional analysis                     │
╰─────────────────────────────────────────────────────╯
```

**Layer 0** defines the physics of your world.
**Layer 1** defines what can happen within those physics.
**Layer 2** is your application.

---

## Matter Types

Prevent unit confusion with typed values:

```python
from newton_sdk import Money, Celsius, PSI, Meters

# These work:
total = Money(100) + Money(50)      # Money(150)
hot = Celsius(100) > Celsius(50)    # True

# These FAIL (type safety):
Money(100) + Celsius(50)            # TypeError!
Celsius(20) + PSI(30)               # TypeError!
```

Remember the Mars Climate Orbiter? It crashed because of unit confusion.
**tinyTalk prevents that.**

Available: `Money`, `Mass`, `Distance`, `Temperature`, `Pressure`, `Volume`, `FlowRate`, `Velocity`, `Time`

---

## Kinetic Engine

Motion = the mathematical delta between two states.

```python
from newton_sdk import KineticEngine, Presence

engine = KineticEngine()

# Add a boundary
engine.add_boundary(
    lambda d: d.changes.get('x', {}).get('to', 0) > 100,
    name="MaxX"
)

# Calculate motion
start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 50, 'y': 25})

result = engine.resolve_motion(start, end)
# {'status': 'synchronized', 'delta': {...}}

# Violate boundary
end_bad = Presence({'x': 150, 'y': 0})
result = engine.resolve_motion(start, end_bad)
# {'status': 'finfr', 'reason': "Boundary 'MaxX' violated"}
```

---

## Philosophy

> "I made up the term 'object-oriented', and I can tell you
>  I didn't have C++ in mind."
>  — Alan Kay, creator of Smalltalk

tinyTalk continues the Smalltalk tradition:
- Everything is an object (**Blueprint**)
- Objects communicate via messages (**forge**)
- But now, objects have **laws** they cannot break
- And **ratios** define their dimensional constraints

**The constraint IS the instruction.**
**The boundary IS the behavior.**
**finfr = f/g. The ratio IS the physics.**

---

## Learn More

| Resource | Description |
|----------|-------------|
| [GETTING_STARTED.md](../GETTING_STARTED.md) | Multi-level developer guide |
| [TINYTALK_BIBLE.md](../TINYTALK_BIBLE.md) | Complete philosophical manual |
| [examples/tinytalk_demo.py](../examples/tinytalk_demo.py) | Interactive demo |

---

## Quick Reference

```
╭────────────────────────────────────────────────────────────────╮
│  KEYWORDS        when, and, fin, finfr, ratio                   │
│  DECORATORS      @law (Layer 0), @forge (Layer 1)              │
│  STATE           field(type, default=value)                    │
│  TYPES           Money, Celsius, PSI, Meters, etc.             │
│  RATIO           ratio(f, g) → RatioResult                     │
│  CLI             newton demo | newton serve                    │
╰────────────────────────────────────────────────────────────────╯
```

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*"Smalltalk gave us objects. tinyTalk gives us boundaries. finfr = f/g."*

**finfr.** 🍎
