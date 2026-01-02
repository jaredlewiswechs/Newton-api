# tinyTalk Libraries

**The "No-First" constraint language. Define what cannot happen.**

tinyTalk is available for Python, Ruby, and R.

---

## Quick Start

### Python

```python
# Add Newton-api to your path
import sys
sys.path.insert(0, 'path/to/Newton-api')

from tinytalk_py import Blueprint, field, law, forge, when, finfr, Money

class RiskGovernor(Blueprint):
    assets = field(float, default=1000.0)
    liabilities = field(float, default=0.0)

    @law
    def insolvency(self):
        when(self.liabilities > self.assets, finfr)

    @forge
    def execute_trade(self, amount: float):
        self.liabilities += amount
        return "cleared"

# Use it
gov = RiskGovernor()
gov.execute_trade(500)   # Works: liabilities=500
gov.execute_trade(600)   # Raises LawViolation: liabilities would exceed assets
```

### Ruby

```ruby
require_relative 'path/to/Newton-api/tinytalk/ruby/tinytalk'
include TinyTalk

class RiskGovernor < Blueprint
  field :assets, Float, default: 1000.0
  field :liabilities, Float, default: 0.0

  law :insolvency do
    when_condition(liabilities > assets) { finfr }
  end

  forge :execute_trade do |amount|
    self.liabilities = liabilities + amount
    :cleared
  end
end

# Use it
gov = RiskGovernor.new
gov.execute_trade(500)   # Works
gov.execute_trade(600)   # Raises Finfr
```

### R

```r
source("path/to/Newton-api/tinytalk/r/tinytalk.R")

RiskGovernor <- Blueprint(
  fields = list(
    assets = 1000.0,
    liabilities = 0.0
  ),
  laws = list(
    insolvency = function(self) {
      when_cond(self$liabilities > self$assets, function() finfr())
    }
  ),
  forges = list(
    execute_trade = function(self, amount) {
      self$liabilities <- self$liabilities + amount
      "cleared"
    }
  )
)

# Use it
gov <- RiskGovernor$new()
gov$execute_trade(500)   # Works
gov$execute_trade(600)   # Error: finfr
```

---

## The Lexicon

| Keyword | Purpose | Description |
|---------|---------|-------------|
| `when` | Declare a fact | The present state. It acknowledges "is". |
| `and` | Combine facts | Join multiple facts into a complex shape. |
| `fin` | Closure | A stopping point (can be reopened). |
| `finfr` | Finality | Ontological death. The state is forbidden. |

---

## Matter Types

All languages include typed values that prevent unit confusion:

```python
# Python
from tinytalk import Money, Temperature, Celsius, PSI

balance = Money(100)
temp = Celsius(22.5)

# These work:
total = Money(100) + Money(50)   # Money(150)
hot = Celsius(100) > Celsius(50) # True

# These fail (type safety):
Money(100) + Celsius(50)         # TypeError!
```

Available types: `Money`, `Mass`, `Distance`, `Temperature`, `Pressure`, `Volume`, `FlowRate`, `Velocity`, `Time`

---

## The Three Layers

1. **Layer 0: Governance** - Laws define what cannot happen (`finfr`)
2. **Layer 1: Executive** - Forges define what happens (mutations)
3. **Layer 2: Application** - Your specific use case

---

## Kinetic Engine

Calculate motion as the mathematical delta between states:

```python
from tinytalk import KineticEngine, Presence

engine = KineticEngine()

# Add boundaries
engine.add_boundary(
    lambda d: d.changes.get('x', {}).get('to', 0) > 100,
    name="MaxX"
)

# Resolve motion
start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 50, 'y': 25})

result = engine.resolve_motion(start, end)
# {'status': 'synchronized', 'delta': {'x': {...}, 'y': {...}}, ...}

# Violates boundary:
end_bad = Presence({'x': 150, 'y': 0})
result = engine.resolve_motion(start, end_bad)
# {'status': 'finfr', 'reason': "Boundary 'MaxX' violated", ...}
```

---

## Learn More

- [TINYTALK_BIBLE.md](../TINYTALK_BIBLE.md) - The complete philosophical manual
- [examples/tinytalk_demo.py](../examples/tinytalk_demo.py) - Interactive demo
