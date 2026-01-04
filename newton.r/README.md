# newton: R Package for Constraint Verification

> **Combinations over permutations.**
> Define what CANNOT happen, not what should.

Newton is a constraint verification supercomputer. This R package provides:

- **tinyTalk Language** - The "No-First" constraint programming language
- **Matter Types** - Type-safe values preventing unit confusion
- **Blueprints** - State + Laws + Forges architecture
- **KineticEngine** - Motion and boundary enforcement
- **Newton Client** - HTTP interface to Newton API

## Philosophy

Traditional programming: "If condition is true, do this."

Newton: **"This state CANNOT exist."**

```r
# Traditional (enumerating valid states)
if (balance >= amount && account_active && ...) {
  withdraw(amount)
}

# Newton (defining invalid states)
BankAccount <- Blueprint(
  laws = list(
    no_overdraft = function(self) {
      when_cond(self$balance < Money(0), finfr())
    }
  )
)
```

## Installation

```r
# Install dependencies
install.packages(c("httr2", "jsonlite", "R6"))

# Install from source
devtools::install_local("path/to/newton.r")

# Or install directly from GitHub
devtools::install_github("newton-ai/newton.r")
```

## Quick Start

### Local Verification with tinyTalk

```r
library(newton)

# Define a Blueprint with laws
Account <- Blueprint(
  fields = list(balance = Money(1000)),
  laws = list(
    no_overdraft = function(self) {
      when_cond(self$balance < Money(0), finfr())
    }
  ),
  forges = list(
    withdraw = function(self, amount) {
      self$balance <- self$balance - amount
    }
  )
)

# Use it
acct <- Account$new()
acct$withdraw(Money(500))  # OK
acct$withdraw(Money(600))  # finfr! State rolls back
```

### Remote Verification with Newton API

```r
client <- Newton$new("http://localhost:8000")

# Verify content
result <- client$verify("Hello world")

# Verified calculation
result <- client$calculate("sqrt(16) + 2^3")

# CDL constraint
result <- client$constraint(
  constraint = list(field = "balance", operator = "ge", value = 0),
  object = list(balance = 100)
)
```

## The Four Books

### Book I: Lexicon

```r
# finfr - Ontological death (state cannot exist)
when_cond(balance < 0, finfr())

# fin - Soft closure (can be reopened)
when_cond(market_closed, fin())

# ratio - The f/g constraint
ratio(withdrawal, balance, threshold = 1.0)
```

### Book II: Matter Types

```r
# Type-safe values
balance <- Money(1000, "USD")
weight <- Mass(75, "kg")

# Cannot mix types
Money(500) + Mass(10)  # ERROR

# Same-type division yields ratio
Money(500) / Money(1000)  # 0.5
```

### Book III: Blueprints

```r
TradingAccount <- Blueprint(
  fields = list(
    equity = Money(100000),
    debt = Money(0)
  ),
  laws = list(
    leverage_limit = function(self) {
      when_cond(self$debt$value / self$equity$value > 3, finfr())
    }
  ),
  forges = list(
    borrow = function(self, amount) {
      self$debt <- self$debt + amount
    }
  )
)
```

### Book IV: Engine

```r
engine <- KineticEngine()

engine$add_boundary(
  function(delta) delta$changes$balance$to < 0,
  name = "no_overdraft"
)

result <- engine$resolve_motion(
  Presence(list(balance = 100)),
  Presence(list(balance = -50))
)
# result$status == "finfr"
```

## The f/g Ratio

Every constraint is fundamentally:

```
f/g <= threshold

f = what you're trying to do (forge/fact/function)
g = what reality allows (ground/goal/governance)
```

- `f/g <= threshold` → Valid
- `f/g > threshold` → finfr (exceeds bounds)
- `g = 0` → finfr (undefined)

Examples:
- Bank: `withdrawal/balance <= 1.0`
- Finance: `debt/equity <= 3.0`
- Trading: `exposure/capital <= 10.0`

## CDL Constraints

Build constraints for Newton API:

```r
# Simple
constraint("balance", "ge", 0)

# Ratio
ratio_constraint("debt", "equity", "le", 3.0)

# Composite
all_of(
  constraint("age", "ge", 18),
  constraint("verified", "eq", TRUE)
)
```

## Examples

See `inst/examples/` for complete examples:

- `banking.R` - Bank account with overdraft protection
- `trading.R` - Risk-governed trading system
- `combinations.R` - Philosophy demonstration

## Structure

```
newton.r/
├── R/
│   ├── client.R      # Newton API client
│   ├── tinytalk.R    # Core language (Lexicon, Matter, Blueprint)
│   ├── constraints.R # CDL constraint builders
│   └── engine.R      # KineticEngine, Presence, Delta
├── inst/examples/    # Example scripts
├── vignettes/        # Comprehensive guide
├── DESCRIPTION
├── NAMESPACE
└── README.md
```

## Core Equation

```
newton(current, goal) = current == goal

finfr = f/g  (when undefined or exceeds threshold)
```

This is **verification AS computation**, not verification OF computation.

## License

MIT
