# ============================================================================
#  Example: Banking System with Constraint Verification
# ============================================================================
#
#  Demonstrates the Newton R package for bank account management.
#  Key concept: Combinations over permutations.
#
# ============================================================================

library(newton)

cat("
========================================
Banking System: Constraint Verification
========================================
Philosophy: Define what CANNOT happen.

We don't check every possible invalid input.
We define the constraint space and let violations
trigger finfr (ontological death).
========================================
")

# ----------------------------------------------------------------------------
#  Define the Bank Account Blueprint
# ----------------------------------------------------------------------------

BankAccount <- Blueprint(
  fields = list(
    account_id = "",
    owner = "",
    balance = Money(0),
    overdraft_limit = Money(0),  # Some accounts allow overdraft
    daily_withdrawal = Money(0),
    max_daily_withdrawal = Money(10000)
  ),

  laws = list(
    # Law 1: Balance cannot go below overdraft limit
    no_excessive_overdraft = function(self) {
      effective_limit <- Money(-self$overdraft_limit$value)
      when_cond(self$balance < effective_limit, finfr())
    },

    # Law 2: Cannot exceed daily withdrawal limit
    daily_limit = function(self) {
      when_cond(self$daily_withdrawal > self$max_daily_withdrawal, finfr())
    }
  ),

  forges = list(
    deposit = function(self, amount) {
      if (!inherits(amount, "Money")) {
        amount <- Money(amount)
      }
      when_cond(amount < Money(0), finfr("deposit", "Cannot deposit negative amount"))
      self$balance <- self$balance + amount
      list(
        action = "deposit",
        amount = amount$value,
        new_balance = self$balance$value
      )
    },

    withdraw = function(self, amount) {
      if (!inherits(amount, "Money")) {
        amount <- Money(amount)
      }
      when_cond(amount < Money(0), finfr("withdraw", "Cannot withdraw negative amount"))
      self$balance <- self$balance - amount
      self$daily_withdrawal <- self$daily_withdrawal + amount
      list(
        action = "withdraw",
        amount = amount$value,
        new_balance = self$balance$value,
        daily_total = self$daily_withdrawal$value
      )
    },

    transfer_to = function(self, other, amount) {
      if (!inherits(amount, "Money")) {
        amount <- Money(amount)
      }
      # Withdraw from self
      self$balance <- self$balance - amount
      self$daily_withdrawal <- self$daily_withdrawal + amount
      # Deposit to other (this is a reference, so it works)
      other$balance <- other$balance + amount
      list(
        action = "transfer",
        amount = amount$value,
        from_balance = self$balance$value,
        to_balance = other$balance$value
      )
    }
  )
)

# ----------------------------------------------------------------------------
#  Create Accounts and Demonstrate
# ----------------------------------------------------------------------------

cat("\n--- Creating Accounts ---\n")

# Alice: Standard account, no overdraft
alice <- BankAccount$new(
  account_id = "A001",
  owner = "Alice",
  balance = Money(1000)
)
cat("Alice's account:", alice$balance$value, "USD\n")

# Bob: Premium account with $500 overdraft protection
bob <- BankAccount$new(
  account_id = "B001",
  owner = "Bob",
  balance = Money(500),
  overdraft_limit = Money(500)
)
cat("Bob's account:", bob$balance$value, "USD (overdraft limit: 500)\n")

# ----------------------------------------------------------------------------
#  Test Valid Operations
# ----------------------------------------------------------------------------

cat("\n--- Valid Operations ---\n")

# Alice deposits $500
result <- alice$deposit(Money(500))
cat("Alice deposits $500:", result$new_balance, "USD\n")

# Alice withdraws $300
result <- alice$withdraw(Money(300))
cat("Alice withdraws $300:", result$new_balance, "USD\n")

# Bob uses overdraft
result <- bob$withdraw(Money(700))
cat("Bob withdraws $700 (using overdraft):", result$new_balance, "USD\n")

# ----------------------------------------------------------------------------
#  Test Law Violations (finfr)
# ----------------------------------------------------------------------------

cat("\n--- Testing Law Violations (finfr) ---\n")

# Alice tries to overdraft (no overdraft protection)
cat("Alice tries to withdraw $2000 (would overdraft)...\n")
tryCatch({
  alice$withdraw(Money(2000))
  cat("ERROR: This should not happen!\n")
}, finfr = function(e) {
  cat("BLOCKED by finfr:", e$message, "\n")
  cat("Alice's balance unchanged:", alice$balance$value, "USD\n")
})

# Bob exceeds overdraft limit
cat("\nBob tries to withdraw $500 more (would exceed limit)...\n")
tryCatch({
  bob$withdraw(Money(500))
  cat("ERROR: This should not happen!\n")
}, finfr = function(e) {
  cat("BLOCKED by finfr:", e$message, "\n")
  cat("Bob's balance unchanged:", bob$balance$value, "USD\n")
})

# ----------------------------------------------------------------------------
#  Test Daily Limit
# ----------------------------------------------------------------------------

cat("\n--- Testing Daily Withdrawal Limit ---\n")

# Create account with specific limit for testing
charlie <- BankAccount$new(
  account_id = "C001",
  owner = "Charlie",
  balance = Money(50000),
  max_daily_withdrawal = Money(1000)
)

# Series of withdrawals
charlie$withdraw(Money(400))
cat("Charlie withdraws $400, daily total:", charlie$daily_withdrawal$value, "\n")

charlie$withdraw(Money(500))
cat("Charlie withdraws $500, daily total:", charlie$daily_withdrawal$value, "\n")

# This would exceed daily limit
cat("Charlie tries to withdraw $200 more (exceeds daily limit)...\n")
tryCatch({
  charlie$withdraw(Money(200))
}, finfr = function(e) {
  cat("BLOCKED by finfr:", e$message, "\n")
  cat("Daily withdrawal still:", charlie$daily_withdrawal$value, "\n")
})

# ----------------------------------------------------------------------------
#  Demonstrate the f/g Ratio
# ----------------------------------------------------------------------------

cat("\n--- The f/g Ratio ---\n")

cat("
Every constraint is fundamentally a ratio:
  f = what you're trying to do
  g = what reality allows

For withdrawals:
  f = withdrawal amount
  g = available balance + overdraft
  threshold = 1.0 (can't exceed 100%)

When f/g > threshold: finfr
When g = 0: finfr (undefined)
")

# Show ratio calculation
current_balance <- 1000
overdraft <- 0
available <- current_balance + overdraft
withdrawal <- 500

cat(sprintf("\nf = %d (withdrawal)\n", withdrawal))
cat(sprintf("g = %d (available)\n", available))
cat(sprintf("f/g = %.2f (ratio)\n", withdrawal / available))
cat(sprintf("threshold = 1.0\n"))
cat(sprintf("Result: %s\n", if (withdrawal / available <= 1.0) "PASS" else "finfr"))

cat("\n--- End of Demo ---\n")
