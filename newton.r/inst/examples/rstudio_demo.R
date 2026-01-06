# ============================================================================
#  NEWTON QUICK START DEMO FOR R STUDIO
# ============================================================================
#
#  Run this file in RStudio to see Newton in action!
#  No server required - this uses local tinyTalk constraints.
#
# ============================================================================

# Load Newton (adjust path as needed)
source("../../R/tinytalk.R")

cat("\n")
cat("╔══════════════════════════════════════════════════════════════════╗\n")
cat("║          NEWTON QUICK START - R STUDIO DEMO                      ║\n")
cat("║                                                                  ║\n")
cat("║   Philosophy: Define what CANNOT happen, not what should.        ║\n")
cat("╚══════════════════════════════════════════════════════════════════╝\n\n")

# ============================================================================
#  DEMO 1: BANK ACCOUNT WITH OVERDRAFT PROTECTION
# ============================================================================

cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  DEMO 1: Bank Account with Overdraft Protection\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

# Define the blueprint
BankAccount <- Blueprint(
  fields = list(
    balance = Money(1000),
    owner = "Customer"
  ),
  laws = list(
    no_overdraft = function(self) {
      when_cond(self$balance < Money(0), finfr("no_overdraft"))
    }
  ),
  forges = list(
    withdraw = function(self, amount) {
      if (!inherits(amount, "Money")) amount <- Money(amount)
      self$balance <- self$balance - amount
      self$balance
    },
    deposit = function(self, amount) {
      if (!inherits(amount, "Money")) amount <- Money(amount)
      self$balance <- self$balance + amount
      self$balance
    }
  )
)

# Create account
account <- BankAccount$new(owner = "Alice", balance = Money(500))
cat("Created account for Alice with $500\n\n")

# Valid operations
cat("► Deposit $200... ")
account$deposit(200)
cat("SUCCESS! Balance: $", account$balance$value, "\n", sep = "")

cat("► Withdraw $300... ")
account$withdraw(300)
cat("SUCCESS! Balance: $", account$balance$value, "\n", sep = "")

# Try to overdraft
cat("► Withdraw $500 (would overdraft)... ")
tryCatch({
  account$withdraw(500)
  cat("SUCCESS!\n")  # Won't reach here
}, error = function(e) {
  cat("BLOCKED!\n")
  cat("  → Law 'no_overdraft' prevented invalid state\n")
  cat("  → Balance unchanged: $", account$balance$value, "\n", sep = "")
})

cat("\n")

# ============================================================================
#  DEMO 2: TRADING WITH LEVERAGE LIMITS
# ============================================================================

cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  DEMO 2: Trading Account with 5x Leverage Limit\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

TradingAccount <- Blueprint(
  fields = list(
    capital = Money(100000),
    exposure = Money(0),
    max_leverage = 5.0
  ),
  laws = list(
    leverage_limit = function(self) {
      if (self$capital$value > 0) {
        leverage <- self$exposure$value / self$capital$value
        when_cond(leverage > self$max_leverage, finfr("leverage_limit"))
      }
    }
  ),
  forges = list(
    open_position = function(self, size) {
      self$exposure <- self$exposure + Money(size)
      self$exposure$value / self$capital$value  # Return leverage
    }
  )
)

trader <- TradingAccount$new()
cat("Capital: $100,000 | Max leverage: 5x\n\n")

# Open positions until blocked
positions <- c(200000, 200000, 100000, 100000)
for (i in seq_along(positions)) {
  size <- positions[i]
  cat("► Open $", format(size, big.mark = ","), " position... ", sep = "")

  tryCatch({
    leverage <- trader$open_position(size)
    cat("SUCCESS! Leverage: ", round(leverage, 1), "x\n", sep = "")
  }, error = function(e) {
    would_be <- (trader$exposure$value + size) / trader$capital$value
    cat("BLOCKED! (Would be ", round(would_be, 1), "x > 5x limit)\n", sep = "")
  })
}

cat("\nFinal exposure: $", format(trader$exposure$value, big.mark = ","), "\n", sep = "")

cat("\n")

# ============================================================================
#  DEMO 3: TYPE SAFETY - PREVENTING UNIT CONFUSION
# ============================================================================

cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  DEMO 3: Type Safety (Prevents Mars Orbiter-style bugs)\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

# Create typed values
dollars <- Money(1000)
kilos <- Mass(50)
meters <- Distance(100)

cat("Created: $1000, 50kg, 100m\n\n")

# Valid: same types
cat("► Add Money($500) + Money($300)... ")
result <- Money(500) + Money(300)
cat("= Money($", result$value, ")\n", sep = "")

# Valid: multiply by scalar
cat("► Money($100) * 3... ")
result <- Money(100) * 3
cat("= Money($", result$value, ")\n", sep = "")

# Invalid: different types
cat("► Money($100) + Mass(50kg)... ")
tryCatch({
  result <- Money(100) + Mass(50)
  cat("= ", result, "\n")
}, error = function(e) {
  cat("ERROR! Cannot add Money and Mass\n")
})

cat("► Compare Money($100) < Distance(200m)... ")
tryCatch({
  result <- Money(100) < Distance(200)
  cat("= ", result, "\n")
}, error = function(e) {
  cat("ERROR! Cannot compare Money with Distance\n")
})

cat("\n")

# ============================================================================
#  DEMO 4: THE RATIO CONSTRAINT (f/g)
# ============================================================================

cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  DEMO 4: The Ratio Constraint (f/g)\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

cat("Every Newton constraint is fundamentally a ratio:\n")
cat("  f = what you're trying to do\n")
cat("  g = what reality allows\n")
cat("  threshold = maximum allowed ratio\n\n")

# Valid ratio
cat("► ratio(debt=2000, equity=1000, threshold=3.0)... ")
tryCatch({
  r <- ratio(2000, 1000, threshold = 3.0)
  cat("= ", r, " (OK, within limit)\n", sep = "")
}, error = function(e) {
  cat("BLOCKED!\n")
})

# Exceeds threshold
cat("► ratio(debt=4000, equity=1000, threshold=3.0)... ")
tryCatch({
  r <- ratio(4000, 1000, threshold = 3.0)
  cat("= ", r, "\n", sep = "")
}, error = function(e) {
  cat("BLOCKED! Ratio 4.0 exceeds threshold 3.0\n")
})

# Division by zero
cat("► ratio(debt=1000, equity=0, threshold=3.0)... ")
tryCatch({
  r <- ratio(1000, 0, threshold = 3.0)
  cat("= ", r, "\n", sep = "")
}, error = function(e) {
  cat("BLOCKED! Cannot divide by zero\n")
})

cat("\n")

# ============================================================================
#  SUMMARY
# ============================================================================

cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
cat("  SUMMARY\n")
cat("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

cat("Key Newton concepts:\n\n")

cat("  Blueprint()  - Define state + laws + operations\n")
cat("  finfr()      - 'This state CANNOT exist' (hard stop)\n")
cat("  when_cond()  - 'When X happens, block it'\n")
cat("  ratio(f,g,t) - 'f/g must be <= threshold'\n")
cat("  Matter types - Prevent unit confusion (Money, Mass, etc.)\n\n")

cat("Philosophy: Define what CANNOT happen, not what should.\n")
cat("Result: Invalid states are prevented, not detected after the fact.\n\n")

cat("Next steps:\n")
cat("  • Read: RSTUDIO_QUICKSTART.md\n")
cat("  • Examples: newton.r/inst/examples/\n")
cat("  • API client: newton.r/R/client.R\n")
cat("\n")
