# ============================================================================
#  Example: Combinations Over Permutations
# ============================================================================
#
#  This example demonstrates the core philosophy of Newton:
#  COMBINATIONS over PERMUTATIONS.
#
#  Traditional approach: Check every possible invalid input (permutations)
#  Newton approach: Define the valid state space (combinations)
#
# ============================================================================

library(newton)

cat("
==============================================
COMBINATIONS OVER PERMUTATIONS
==============================================

Traditional programming enumerates what's VALID.
Newton defines what's INVALID.

This is more powerful because:
1. Invalid states are often simpler to define
2. We verify SPACES, not individual points
3. New valid inputs automatically work

The constraint SPACE is the combination of all
states that satisfy all laws simultaneously.
==============================================
")

# ----------------------------------------------------------------------------
#  Example 1: Simple Loan Eligibility
# ----------------------------------------------------------------------------

cat("\n--- Example 1: Loan Eligibility ---\n")

cat("
PERMUTATION approach (traditional):
  if (credit_score >= 600 &&
      debt_to_income <= 0.43 &&
      employment_years >= 2 &&
      income >= 30000 &&
      age >= 18 &&
      not_bankrupt &&
      ...) {
    approve()
  }

COMBINATION approach (Newton):
  Laws define the boundaries of the eligible space.
  Any application inside the space is approved.
")

LoanApplication <- Blueprint(
  fields = list(
    credit_score = 0,
    annual_income = Money(0),
    existing_debt = Money(0),
    employment_years = 0,
    loan_amount = Money(0)
  ),

  laws = list(
    # Credit score floor
    min_credit = function(self) {
      when_cond(self$credit_score < 600, finfr())
    },

    # Debt-to-income ratio (including new loan)
    dti_limit = function(self) {
      if (self$annual_income > Money(0)) {
        monthly_income <- self$annual_income$value / 12
        monthly_debt <- self$existing_debt$value / 12
        new_payment <- self$loan_amount$value / 360  # 30-year loan approx
        total_monthly_debt <- monthly_debt + new_payment
        dti <- total_monthly_debt / monthly_income
        when_cond(dti > 0.43, finfr())
      }
    },

    # Employment history
    min_employment = function(self) {
      when_cond(self$employment_years < 2, finfr())
    },

    # Loan amount vs income (max 4x annual income)
    loan_to_income = function(self) {
      if (self$annual_income > Money(0)) {
        ratio_val <- self$loan_amount$value / self$annual_income$value
        when_cond(ratio_val > 4, finfr())
      }
    }
  ),

  forges = list(
    submit = function(self) {
      # If we get here, all laws passed
      list(
        status = "APPROVED",
        credit_score = self$credit_score,
        dti = (self$existing_debt$value + self$loan_amount$value) /
              self$annual_income$value,
        loan_amount = self$loan_amount$value
      )
    }
  )
)

# Test cases
cat("\nCase 1: Good applicant\n")
app1 <- LoanApplication$new(
  credit_score = 720,
  annual_income = Money(80000),
  existing_debt = Money(15000),
  employment_years = 5,
  loan_amount = Money(200000)
)
result <- app1$submit()
cat(sprintf("Result: %s (credit=%d, loan=$%s)\n",
            result$status, result$credit_score,
            format(result$loan_amount, big.mark = ",")))

cat("\nCase 2: Low credit score\n")
tryCatch({
  app2 <- LoanApplication$new(
    credit_score = 580,  # Below 600
    annual_income = Money(80000),
    existing_debt = Money(15000),
    employment_years = 5,
    loan_amount = Money(200000)
  )
  app2$submit()
}, finfr = function(e) {
  cat("DENIED: Credit score below minimum\n")
})

cat("\nCase 3: DTI too high\n")
tryCatch({
  app3 <- LoanApplication$new(
    credit_score = 700,
    annual_income = Money(50000),
    existing_debt = Money(30000),  # High existing debt
    employment_years = 3,
    loan_amount = Money(250000)
  )
  app3$submit()
}, finfr = function(e) {
  cat("DENIED: Debt-to-income ratio exceeded\n")
})

# ----------------------------------------------------------------------------
#  Example 2: Visualizing the Constraint Space
# ----------------------------------------------------------------------------

cat("\n--- Example 2: Constraint Space Geometry ---\n")

cat("
The constraint space is a GEOMETRIC region.
Each law defines a boundary (hyperplane).
The valid region is the INTERSECTION.

For 2D (credit_score, income):
  - credit >= 600: vertical line
  - income >= 30000: horizontal line
  - Valid region: upper-right quadrant

For our loan example with 4 constraints:
  - 4-dimensional space
  - Each constraint is a half-space
  - Valid applications are in the INTERSECTION

This is why COMBINATIONS > PERMUTATIONS:
  - We don't enumerate all (infinite) invalid points
  - We define the boundary, everything inside works
")

# Simple 2D demonstration
cat("\nSimple 2D constraint space:\n")
cat("  Constraint 1: x >= 10\n")
cat("  Constraint 2: y >= 5\n")
cat("  Constraint 3: x + y <= 30\n")
cat("\nValid region is the TRIANGLE formed by:\n")
cat("  (10, 5), (10, 20), (25, 5)\n")

# Test points
test_points <- list(
  list(x = 15, y = 10),  # Inside
  list(x = 5, y = 10),   # Violates x >= 10
  list(x = 20, y = 15),  # Violates x + y <= 30
  list(x = 10, y = 5)    # On boundary (valid)
)

SimpleSpace <- Blueprint(
  fields = list(x = 0, y = 0),
  laws = list(
    x_min = function(self) { when_cond(self$x < 10, finfr()) },
    y_min = function(self) { when_cond(self$y < 5, finfr()) },
    sum_max = function(self) { when_cond(self$x + self$y > 30, finfr()) }
  ),
  forges = list(
    check = function(self) { list(valid = TRUE, x = self$x, y = self$y) }
  )
)

cat("\nTesting points:\n")
for (pt in test_points) {
  tryCatch({
    s <- SimpleSpace$new(x = pt$x, y = pt$y)
    result <- s$check()
    cat(sprintf("  (%d, %d): VALID (inside space)\n", pt$x, pt$y))
  }, finfr = function(e) {
    cat(sprintf("  (%d, %d): INVALID (outside space)\n", pt$x, pt$y))
  })
}

# ----------------------------------------------------------------------------
#  Example 3: Ratio Constraints (f/g)
# ----------------------------------------------------------------------------

cat("\n--- Example 3: The f/g Ratio ---\n")

cat("
Every Newton constraint is fundamentally a RATIO:
  f/g <= threshold

Where:
  f = what you're trying to DO (force, forge, function)
  g = what reality ALLOWS (ground, goal, governance)

This unifies all constraints:
  - Overdraft: withdrawal/balance <= 1
  - Leverage: debt/equity <= 3
  - Bandwidth: usage/capacity <= 1
  - DTI: debt/income <= 0.43

Special cases:
  - g = 0: UNDEFINED (finfr) - can't divide by zero
  - f/g > threshold: EXCEEDED (finfr)
  - f/g <= threshold: VALID
")

# Demonstrate ratio function
cat("\nRatio examples:\n")

# Valid ratio
cat("  ratio(500, 1000, 1.0) = ")
r1 <- ratio(500, 1000, threshold = 1.0)
cat(sprintf("%.2f (VALID)\n", r1))

# At boundary
cat("  ratio(1000, 1000, 1.0) = ")
r2 <- ratio(1000, 1000, threshold = 1.0)
cat(sprintf("%.2f (VALID, at boundary)\n", r2))

# Exceeds threshold
cat("  ratio(1500, 1000, 1.0) = ")
tryCatch({
  ratio(1500, 1000, threshold = 1.0)
}, finfr = function(e) {
  cat("finfr (exceeds threshold)\n")
})

# Division by zero
cat("  ratio(100, 0, 1.0) = ")
tryCatch({
  ratio(100, 0, threshold = 1.0)
}, finfr = function(e) {
  cat("finfr (undefined, g=0)\n")
})

# ----------------------------------------------------------------------------
#  Key Takeaways
# ----------------------------------------------------------------------------

cat("\n--- Key Takeaways ---\n")

cat("
1. COMBINATIONS define the valid STATE SPACE
   - Geometric region in n-dimensional space
   - Intersection of all constraint half-spaces

2. PERMUTATIONS would enumerate all inputs
   - Exponential or infinite
   - Fragile: new cases break validation

3. Newton's approach:
   - Define laws (boundaries)
   - Any state satisfying all laws is valid
   - New valid states automatically work

4. The f/g ratio unifies all constraints:
   - Every law is ultimately f/g <= threshold
   - Special case: g=0 is ontological death

5. finfr is not an error:
   - It's a statement about reality
   - 'This state CANNOT exist'
   - State automatically rolls back
")

cat("\n--- End of Combinations Example ---\n")
