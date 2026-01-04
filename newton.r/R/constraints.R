# ============================================================================
#  CDL Constraint Builders
# ============================================================================
#
#  Helpers for building CDL (Constraint Definition Language) constraints.
#  These map to Newton's constraint verification API.
#
#  Philosophy: Combinations over Permutations
#  - Define the valid constraint SPACE
#  - Objects either fall within or without
#  - No enumeration of all possibilities needed
#
# ============================================================================

#' CDL Domain Constants
#'
#' @description
#' Predefined constraint domains from Newton's CDL specification.
#'
#' @examples
#' cdl_domain$FINANCIAL  # "FINANCIAL"
#' cdl_domain$HEALTH     # "HEALTH"
#'
#' @export
cdl_domain <- list(
  FINANCIAL = "FINANCIAL",
  COMMUNICATION = "COMMUNICATION",
  HEALTH = "HEALTH",
  EPISTEMIC = "EPISTEMIC",
  TEMPORAL = "TEMPORAL",
  IDENTITY = "IDENTITY",
  CUSTOM = "CUSTOM"
)

#' Build a CDL Constraint
#'
#' @description
#' Create a constraint specification for Newton's constraint API.
#' Constraints define valid state spaces - objects either satisfy
#' the constraint or they don't.
#'
#' @details
#' Supported operators:
#' - Comparison: eq, ne, lt, gt, le, ge
#' - String: contains, matches, in, not_in
#' - Logic: exists, empty
#' - Temporal: within, after, before
#' - Aggregation: sum_lt, count_gt, avg_le, etc.
#'
#' @param field Field name to check
#' @param operator Comparison operator
#' @param value Value to compare against
#' @param domain CDL domain (optional)
#' @param id Constraint ID (optional, auto-generated if missing)
#' @return A constraint list suitable for Newton API
#'
#' @examples
#' # Balance must be >= 0
#' constraint("balance", "ge", 0)
#'
#' # Age must be in valid range
#' constraint("age", "ge", 0, domain = "HEALTH")
#'
#' # Status must be one of allowed values
#' constraint("status", "in", c("active", "pending", "closed"))
#'
#' @export
constraint <- function(field, operator, value, domain = NULL, id = NULL) {
  c <- list(
    field = field,
    operator = operator,
    value = value
  )

  if (!is.null(domain)) {
    c$domain <- domain
  }

  if (!is.null(id)) {
    c$id <- id
  } else {
    c$id <- paste0("constraint_", field, "_", operator)
  }

  class(c) <- c("cdl_constraint", "list")
  c
}

#' Build a Ratio Constraint
#'
#' @description
#' Create a ratio constraint (f/g analysis) - the core of Newton's
#' verification philosophy.
#'
#' @details
#' Every constraint is fundamentally a ratio:
#' - f = numerator (what you're trying to do)
#' - g = denominator (what's allowed)
#'
#' When g approaches 0, the constraint space becomes undefined (finfr).
#' When f/g exceeds threshold, the state cannot exist (finfr).
#'
#' @param f_field Field name for numerator
#' @param g_field Field name for denominator
#' @param operator Ratio operator: lt, le, gt, ge, eq, undefined
#' @param threshold Threshold value
#' @param id Constraint ID (optional)
#' @return A ratio constraint list
#'
#' @examples
#' # Withdrawal cannot exceed balance (withdrawal/balance <= 1)
#' ratio_constraint("withdrawal", "balance", "le", 1.0)
#'
#' # Leverage limit (debt/equity <= 3)
#' ratio_constraint("debt", "equity", "le", 3.0)
#'
#' # Inventory ratio (used/available < 0.9)
#' ratio_constraint("used", "available", "lt", 0.9)
#'
#' @export
ratio_constraint <- function(f_field, g_field, operator, threshold, id = NULL) {
  c <- list(
    type = "ratio",
    f_field = f_field,
    g_field = g_field,
    operator = paste0("ratio_", operator),
    threshold = threshold
  )

  if (!is.null(id)) {
    c$id <- id
  } else {
    c$id <- paste0("ratio_", f_field, "_", g_field, "_", operator)
  }

  class(c) <- c("cdl_ratio_constraint", "cdl_constraint", "list")
  c
}

#' Build a Temporal Constraint
#'
#' @description
#' Create a temporal constraint for time-based verification.
#'
#' @param field Field name containing timestamp
#' @param operator Temporal operator: within, after, before
#' @param reference Reference time or duration
#' @param id Constraint ID (optional)
#' @return A temporal constraint list
#'
#' @examples
#' # Must be within last 24 hours
#' temporal_constraint("created_at", "within", "24h")
#'
#' # Must be after start date
#' temporal_constraint("event_time", "after", "2024-01-01")
#'
#' @export
temporal_constraint <- function(field, operator, reference, id = NULL) {
  c <- list(
    type = "temporal",
    field = field,
    operator = operator,
    reference = reference
  )

  if (!is.null(id)) {
    c$id <- id
  } else {
    c$id <- paste0("temporal_", field, "_", operator)
  }

  class(c) <- c("cdl_temporal_constraint", "cdl_constraint", "list")
  c
}

#' Build a Composite Constraint
#'
#' @description
#' Combine multiple constraints with logical operators.
#'
#' @details
#' Composite constraints enable complex verification logic:
#' - AND: All constraints must pass
#' - OR: At least one constraint must pass
#' - NOT: Constraint must fail
#'
#' This is where "combinations over permutations" becomes powerful:
#' rather than checking every possible input, we define the
#' geometric intersection of constraint spaces.
#'
#' @param operator Logical operator: AND, OR, NOT
#' @param constraints List of constraint specifications
#' @param id Constraint ID (optional)
#' @return A composite constraint list
#'
#' @examples
#' # Both conditions must hold
#' composite_constraint("AND", list(
#'   constraint("balance", "ge", 0),
#'   constraint("credit_score", "ge", 600)
#' ))
#'
#' # Either condition suffices
#' composite_constraint("OR", list(
#'   constraint("role", "eq", "admin"),
#'   constraint("approved", "eq", TRUE)
#' ))
#'
#' @export
composite_constraint <- function(operator, constraints, id = NULL) {
  c <- list(
    type = "composite",
    operator = operator,
    constraints = constraints
  )

  if (!is.null(id)) {
    c$id <- id
  } else {
    c$id <- paste0("composite_", operator, "_", length(constraints))
  }

  class(c) <- c("cdl_composite_constraint", "cdl_constraint", "list")
  c
}

# ----------------------------------------------------------------------------
#  Constraint Combinators (Functional Style)
# ----------------------------------------------------------------------------

#' Combine Constraints with AND
#'
#' @description Combine multiple constraints - all must pass.
#' @param ... Constraints to combine
#' @return A composite AND constraint
#'
#' @examples
#' all_of(
#'   constraint("age", "ge", 18),
#'   constraint("verified", "eq", TRUE)
#' )
#'
#' @export
all_of <- function(...) {
  constraints <- list(...)
  composite_constraint("AND", constraints)
}

#' Combine Constraints with OR
#'
#' @description Combine multiple constraints - at least one must pass.
#' @param ... Constraints to combine
#' @return A composite OR constraint
#'
#' @examples
#' any_of(
#'   constraint("role", "eq", "admin"),
#'   constraint("role", "eq", "moderator")
#' )
#'
#' @export
any_of <- function(...) {
  constraints <- list(...)
  composite_constraint("OR", constraints)
}

#' Negate a Constraint
#'
#' @description The constraint must NOT pass.
#' @param constraint The constraint to negate
#' @return A composite NOT constraint
#'
#' @examples
#' # Not blocked
#' none_of(constraint("status", "eq", "blocked"))
#'
#' @export
none_of <- function(constraint) {
  composite_constraint("NOT", list(constraint))
}

# ----------------------------------------------------------------------------
#  Domain-Specific Constraint Builders
# ----------------------------------------------------------------------------

#' Financial Domain Constraints
#'
#' @description
#' Pre-built constraints for financial applications.
#'
#' @examples
#' # No negative balance
#' financial$no_overdraft("balance")
#'
#' # Leverage limit
#' financial$leverage_limit("debt", "equity", 3.0)
#'
#' @export
financial <- list(
  #' No overdraft constraint
  no_overdraft = function(balance_field) {
    constraint(balance_field, "ge", 0, domain = "FINANCIAL",
               id = paste0("no_overdraft_", balance_field))
  },

  #' Leverage limit constraint
  leverage_limit = function(debt_field, equity_field, max_ratio = 3.0) {
    ratio_constraint(debt_field, equity_field, "le", max_ratio,
                     id = paste0("leverage_", max_ratio, "x"))
  },

  #' Transaction limit constraint
  transaction_limit = function(amount_field, max_amount) {
    constraint(amount_field, "le", max_amount, domain = "FINANCIAL",
               id = paste0("tx_limit_", max_amount))
  },

  #' Positive amount constraint
  positive_amount = function(amount_field) {
    constraint(amount_field, "gt", 0, domain = "FINANCIAL",
               id = paste0("positive_", amount_field))
  }
)

#' Health Domain Constraints
#'
#' @description
#' Pre-built constraints for health applications.
#'
#' @export
health <- list(
  #' Valid age constraint
  valid_age = function(age_field, min = 0, max = 150) {
    all_of(
      constraint(age_field, "ge", min, domain = "HEALTH"),
      constraint(age_field, "le", max, domain = "HEALTH")
    )
  },

  #' Valid heart rate constraint
  valid_heart_rate = function(hr_field, min = 30, max = 250) {
    all_of(
      constraint(hr_field, "ge", min, domain = "HEALTH"),
      constraint(hr_field, "le", max, domain = "HEALTH")
    )
  },

  #' Valid blood pressure constraint
  valid_bp = function(systolic_field, diastolic_field) {
    all_of(
      constraint(systolic_field, "ge", 60, domain = "HEALTH"),
      constraint(systolic_field, "le", 300, domain = "HEALTH"),
      constraint(diastolic_field, "ge", 40, domain = "HEALTH"),
      constraint(diastolic_field, "le", 200, domain = "HEALTH")
    )
  }
)

# ----------------------------------------------------------------------------
#  Print Methods
# ----------------------------------------------------------------------------

#' @export
print.cdl_constraint <- function(x, ...) {
  cat("Constraint:\n")
  cat("  ID:", x$id, "\n")
  cat("  Field:", x$field, "\n")
  cat("  Operator:", x$operator, "\n")
  cat("  Value:", format(x$value), "\n")
  if (!is.null(x$domain)) {
    cat("  Domain:", x$domain, "\n")
  }
  invisible(x)
}

#' @export
print.cdl_ratio_constraint <- function(x, ...) {
  cat("Ratio Constraint:\n")
  cat("  ID:", x$id, "\n")
  cat("  f (numerator):", x$f_field, "\n")
  cat("  g (denominator):", x$g_field, "\n")
  cat("  Operator:", x$operator, "\n")
  cat("  Threshold:", x$threshold, "\n")
  invisible(x)
}

#' @export
print.cdl_composite_constraint <- function(x, ...) {
  cat("Composite Constraint:\n")
  cat("  ID:", x$id, "\n")
  cat("  Operator:", x$operator, "\n")
  cat("  Constraints:", length(x$constraints), "\n")
  invisible(x)
}
