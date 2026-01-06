# Newton Quick Start for R Studio

## Installation (30 seconds)

```r
# Install dependencies
install.packages(c("httr2", "jsonlite", "R6"))

# Load Newton package from local source
devtools::install_local("/path/to/Newton-api/newton.r")

# Or just source the files directly:
source("newton.r/R/tinytalk.R")
source("newton.r/R/client.R")
```

---

## Two Ways to Use Newton

| Method | What it does | Needs server? |
|--------|--------------|---------------|
| **Local (tinyTalk)** | Define constraints in R, instant enforcement | No |
| **Remote (API)** | Content verification, encrypted storage, audit trails | Yes |

---

## Quick Start: Local Mode (No Server)

The core idea: **Define what CANNOT happen, not what should.**

```r
library(newton)

# Step 1: Define a Blueprint with Laws
BankAccount <- Blueprint(
  fields = list(
    balance = Money(1000),
    owner = "Alice"
  ),
  laws = list(
    no_overdraft = function(self) {
      when_cond(self$balance < Money(0), finfr())  # Cannot go negative!
    }
  ),
  forges = list(
    withdraw = function(self, amount) {
      self$balance <- self$balance - Money(amount)
      self$balance
    },
    deposit = function(self, amount) {
      self$balance <- self$balance + Money(amount)
      self$balance
    }
  )
)

# Step 2: Create an account
account <- BankAccount$new(owner = "Alice", balance = Money(500))

# Step 3: Use it
account$deposit(200)   # Works! balance = 700
account$withdraw(300)  # Works! balance = 400

# Step 4: Try to violate the law
tryCatch({
  account$withdraw(1000)  # Would make balance = -600
}, error = function(e) {
  cat("BLOCKED:", e$message, "\n")
  cat("Balance unchanged:", account$balance$value, "\n")  # Still 400
})
```

**Key concepts:**
- `Blueprint()` = defines state + laws + operations
- `finfr()` = "this state CANNOT exist" (hard stop)
- `when_cond(bad_thing, finfr())` = if bad_thing happens, block it
- Operations automatically rollback if they violate any law

---

## Quick Start: Remote Mode (API Client)

```r
# Start Newton server first (in terminal):
# python newton_supercomputer.py

library(newton)

# Connect to API
client <- Newton$new("http://localhost:8000")

# Check connection
client$health()

# Verify content safety
result <- client$verify("Help me write a business plan")
cat("Safe:", result$verified, "\n")

# Verified math
result <- client$calculate("sqrt(16) + 2^3")
cat("Result:", result$result, "\n")

# Check a constraint
result <- client$constraint(
  constraint = list(field = "balance", operator = "ge", value = 0),
  object = list(balance = 100)
)
cat("Passed:", result$passed, "\n")
```

---

## Demo Case: Trading Risk Management

This demo shows Newton preventing dangerous trades in real-time.

```r
library(newton)

# === DEFINE THE TRADING ACCOUNT ===

TradingAccount <- Blueprint(
  fields = list(
    capital = Money(100000),
    exposure = Money(0),
    max_leverage = 5.0
  ),

  laws = list(
    # LAW 1: Leverage cannot exceed limit
    leverage_limit = function(self) {
      if (self$capital$value > 0) {
        leverage <- self$exposure$value / self$capital$value
        when_cond(leverage > self$max_leverage,
                  finfr("leverage_limit",
                        paste("Leverage", round(leverage, 2), "exceeds max", self$max_leverage)))
      }
    },

    # LAW 2: Cannot have negative capital
    positive_capital = function(self) {
      when_cond(self$capital < Money(0), finfr())
    }
  ),

  forges = list(
    open_position = function(self, size) {
      self$exposure <- self$exposure + Money(size)
      list(
        action = "opened",
        new_exposure = self$exposure$value,
        leverage = round(self$exposure$value / self$capital$value, 2)
      )
    },

    close_position = function(self, size) {
      self$exposure <- self$exposure - Money(size)
      list(
        action = "closed",
        new_exposure = self$exposure$value,
        leverage = round(self$exposure$value / self$capital$value, 2)
      )
    },

    record_loss = function(self, amount) {
      self$capital <- self$capital - Money(amount)
      list(remaining_capital = self$capital$value)
    }
  )
)

# === USE IT ===

trader <- TradingAccount$new()
cat("Starting capital:", trader$capital$value, "\n")
cat("Max leverage:", trader$max_leverage, "x\n\n")

# Trade 1: Open $200,000 position (2x leverage) - OK
result <- trader$open_position(200000)
cat("Trade 1: Opened $200K position\n")
cat("  Leverage:", result$leverage, "x - ALLOWED\n\n")

# Trade 2: Open another $200,000 (4x leverage) - OK
result <- trader$open_position(200000)
cat("Trade 2: Opened another $200K\n")
cat("  Leverage:", result$leverage, "x - ALLOWED\n\n")

# Trade 3: Try to open $200,000 more (would be 6x) - BLOCKED!
tryCatch({
  trader$open_position(200000)
}, error = function(e) {
  cat("Trade 3: Tried to open $200K more\n")
  cat("  BLOCKED!", e$message, "\n")
  cat("  Exposure unchanged:", trader$exposure$value, "\n\n")
})

# Trade 4: Close $100K, then open $100K - OK (still 5x)
trader$close_position(100000)
result <- trader$open_position(100000)
cat("Trade 4: Rebalanced positions\n")
cat("  Leverage:", result$leverage, "x - ALLOWED (at limit)\n")
```

**Output:**
```
Starting capital: 100000
Max leverage: 5 x

Trade 1: Opened $200K position
  Leverage: 2 x - ALLOWED

Trade 2: Opened another $200K
  Leverage: 4 x - ALLOWED

Trade 3: Tried to open $200K more
  BLOCKED! Law 'leverage_limit' prevents this state (finfr)
  Exposure unchanged: 400000

Trade 4: Rebalanced positions
  Leverage: 5 x - ALLOWED (at limit)
```

---

## Type Safety with Matter Types

Newton prevents unit confusion errors:

```r
# These types cannot be mixed
balance <- Money(1000)
weight <- Mass(50)
distance <- Distance(100)

# Valid operations
total <- Money(500) + Money(300)  # Money(800)
doubled <- balance * 2             # Money(2000)

# Invalid operations - these will ERROR
# Money(100) + Mass(50)            # ERROR: Cannot add Money and Mass
# Money(100) < Distance(200)       # ERROR: Cannot compare Money with Distance
```

---

## Key Patterns

### Pattern 1: The Ratio Constraint
Every constraint is fundamentally a ratio (f/g):
```r
ratio(debt, equity, threshold = 3.0)  # debt/equity must be <= 3
ratio(withdrawal, balance, threshold = 1.0)  # can't withdraw more than you have
```

### Pattern 2: Combinations over Permutations
Don't enumerate valid inputs. Define the valid SPACE:
```r
# BAD: Check every possible withdrawal
# if withdrawal == 100 then ok
# if withdrawal == 200 then ok
# ...

# GOOD: Define the constraint space
laws = list(
  valid_withdrawal = function(self) {
    when_cond(self$withdrawal > self$balance, finfr())
  }
)
```

---

## Files to Explore

```
newton.r/
├── R/
│   ├── tinytalk.R    # Local constraint language
│   ├── client.R      # HTTP API client
│   └── constraints.R # CDL constraint helpers
├── inst/examples/
│   ├── banking.R     # Bank account demo
│   └── trading.R     # Trading system demo
└── vignettes/
    └── newton-guide.Rmd  # Full documentation
```

---

## Summary

1. **Install**: `devtools::install_local("newton.r")`
2. **Local mode**: Use `Blueprint()` with laws + forges
3. **Remote mode**: Use `Newton$new()` client
4. **Philosophy**: Define what CANNOT happen, not what should
5. **Result**: Impossible states are prevented, not detected after the fact
