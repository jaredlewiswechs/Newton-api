# ============================================================================
#  tinyTalk for R - The Constraint Language
# ============================================================================
#
#  The "No-First" philosophy: Define what CANNOT happen, not what should.
#  Combinations over permutations: verify constraint SPACES efficiently.
#
#  Books:
#    I.   LEXICON   - Core constraint words (finfr, fin, when, ratio)
#    II.  MATTER    - Typed values preventing unit confusion
#    III. BLUEPRINT - State + Laws + Forges architecture
#
# ============================================================================

# ============================================================================
#  BOOK I: THE LEXICON
# ============================================================================

#' Finfr - Ontological Death
#'
#' @description
#' The state CANNOT exist. This is not an error to catch - it represents
#' a fundamental impossibility. When triggered, execution halts and state
#' rolls back to last valid configuration.
#'
#' @details
#' finfr represents the ratio f/g becoming undefined or exceeding bounds:
#' - Division by zero (g = 0): The constraint space collapses
#' - Ratio exceeds limit (f/g > threshold): Reality cannot accommodate
#'
#' @param law_name Name of the law that triggered finfr
#' @param message Optional descriptive message
#'
#' @examples
#' \dontrun{
#' # Bank account cannot go negative
#' BankAccount <- Blueprint(
#'   fields = list(balance = Money(1000)),
#'   laws = list(
#'     no_overdraft = function(self) {
#'       when_cond(self$balance < Money(0), finfr())
#'     }
#'   )
#' )
#' }
#'
#' @export
finfr <- function(law_name = "inline", message = NULL) {
  msg <- if (is.null(message)) {
    paste0("Law '", law_name, "' prevents this state (finfr)")
  } else {
    message
  }
  stop(structure(
    list(message = msg, law_name = law_name),
    class = c("finfr", "tinytalk_error", "error", "condition")
  ))
}

#' Fin - Soft Closure
#'
#' @description
#' A stopping point that CAN be reopened. Unlike finfr, fin represents
#' a temporary boundary, not an ontological impossibility.
#'
#' @param law_name Name of the law that triggered fin
#' @param message Optional descriptive message
#'
#' @examples
#' \dontrun{
#' # Trading halted during market hours
#' when_cond(market_closed, fin("trading"))
#' }
#'
#' @export
fin <- function(law_name = "inline", message = NULL) {
  msg <- if (is.null(message)) {
    paste0("Law '", law_name, "' closed this path (fin)")
  } else {
    message
  }
  stop(structure(
    list(message = msg, law_name = law_name),
    class = c("fin", "tinytalk_error", "error", "condition")
  ))
}

#' When Condition
#'
#' @description
#' Declares a constraint. If condition is TRUE, executes result.
#' Core primitive for the "No-First" philosophy.
#'
#' @details
#' The pattern `when_cond(bad_state, finfr())` reads as:
#' "When this bad state occurs, it cannot exist."
#'
#' This is the inverse of traditional programming which says
#' "if good_state then proceed". We define the boundaries,
#' not the paths.
#'
#' @param condition The condition to check
#' @param result What to execute if TRUE (typically finfr() or fin())
#' @return Invisibly returns the condition
#'
#' @examples
#' # Constraint: withdrawal cannot exceed balance
#' when_cond(withdrawal > balance, finfr())
#'
#' # Constraint: leverage cannot exceed 3x
#' when_cond(debt / equity > 3.0, finfr())
#'
#' @export
when_cond <- function(condition, result = NULL) {
  if (isTRUE(condition)) {
    if (is.function(result)) {
      result()
    } else if (!is.null(result)) {
      force(result)
    }
  }
  invisible(condition)
}

#' Ratio - The f/g Constraint
#'
#' @description
#' Every constraint in Newton is fundamentally a ratio:
#' f = what you're trying to do (forge/fact/function)
#' g = what reality allows (ground/goal/governance)
#'
#' @details
#' The ratio f/g encapsulates all constraint logic:
#' - f/g < 1: Safe operation within bounds
#' - f/g = 1: At the boundary
#' - f/g > 1: Exceeds bounds (finfr)
#' - g = 0: Undefined (finfr) - the constraint space collapses
#'
#' @param f Numerator - what you're attempting
#' @param g Denominator - what's allowed
#' @param threshold Maximum allowed ratio (default: 1.0)
#' @param epsilon Floating point tolerance (default: 1e-9)
#' @return The ratio value, or triggers finfr if violated
#'
#' @examples
#' # Bank: withdrawal / balance must be <= 1
#' ratio(withdrawal, balance, threshold = 1.0)
#'
#' # Finance: debt / equity must be <= 3
#' ratio(debt, equity, threshold = 3.0)
#'
#' @export
ratio <- function(f, g, threshold = 1.0, epsilon = 1e-9) {
  # Extract numeric values from Matter types
  f_val <- if (inherits(f, "Matter")) f$value else f
  g_val <- if (inherits(g, "Matter")) g$value else g

  # Check for undefined (g = 0)
  if (abs(g_val) < epsilon) {
    finfr("ratio", "Denominator is zero - constraint space undefined (finfr)")
  }

  r <- f_val / g_val

  # Check threshold
  if (r > threshold + epsilon) {
    finfr("ratio", sprintf("Ratio %.4f exceeds threshold %.4f (finfr)", r, threshold))
  }

  r
}

# ============================================================================
#  BOOK II: MATTER - Typed Values
# ============================================================================

#' Create a Matter Type
#'
#' @description
#' Matter types prevent unit confusion errors (like the Mars Orbiter).
#' You cannot add Money to Mass or compare Distance to Time.
#'
#' @details
#' Combinations over permutations: Rather than checking all possible
#' unit mismatches at runtime, Matter types make invalid combinations
#' impossible at the type level.
#'
#' @param value Numeric value
#' @param unit Unit string
#' @param type Matter type name
#' @return A Matter object
#'
#' @export
Matter <- function(value, unit, type) {
  structure(
    list(value = as.numeric(value), unit = unit),
    class = c(type, "Matter")
  )
}

#' Money Type
#' @param value Numeric value
#' @param unit Currency unit (default: "USD")
#' @return A Money object
#' @export
Money <- function(value, unit = "USD") {
  Matter(value, unit, "Money")
}

#' Mass Type
#' @param value Numeric value
#' @param unit Mass unit (default: "kg")
#' @return A Mass object
#' @export
Mass <- function(value, unit = "kg") {
  Matter(value, unit, "Mass")
}

#' Distance Type
#' @param value Numeric value
#' @param unit Distance unit (default: "m")
#' @return A Distance object
#' @export
Distance <- function(value, unit = "m") {
  Matter(value, unit, "Distance")
}

#' Temperature Type
#' @param value Numeric value
#' @param unit Temperature unit (default: "C")
#' @return A Temperature object
#' @export
Temperature <- function(value, unit = "C") {
  Matter(value, unit, "Temperature")
}

#' Pressure Type
#' @param value Numeric value
#' @param unit Pressure unit (default: "PSI")
#' @return A Pressure object
#' @export
Pressure <- function(value, unit = "PSI") {
  Matter(value, unit, "Pressure")
}

#' Volume Type
#' @param value Numeric value
#' @param unit Volume unit (default: "L")
#' @return A Volume object
#' @export
Volume <- function(value, unit = "L") {
  Matter(value, unit, "Volume")
}

#' Time Type
#' @param value Numeric value
#' @param unit Time unit (default: "s")
#' @return A Time object
#' @export
Time <- function(value, unit = "s") {
  Matter(value, unit, "Time")
}

#' Ratio Type (dimensionless)
#' @param value Numeric value
#' @return A Ratio object
#' @export
Ratio <- function(value) {
  Matter(value, "", "Ratio")
}

# Convenience constructors
#' @export
Celsius <- function(value) Temperature(value, "C")

#' @export
Fahrenheit <- function(value) Temperature(value, "F")

#' @export
PSI <- function(value) Pressure(value, "PSI")

#' @export
Liters <- function(value) Volume(value, "L")

#' @export
Meters <- function(value) Distance(value, "m")

#' @export
Kilograms <- function(value) Mass(value, "kg")

#' @export
Seconds <- function(value) Time(value, "s")

# ----------------------------------------------------------------------------
#  Matter Operations
# ----------------------------------------------------------------------------

#' @export
`+.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot add", class(a)[1], "and", class(b)[1]))
  }
  Matter(a$value + b$value, a$unit, class(a)[1])
}

#' @export
`-.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot subtract", class(b)[1], "from", class(a)[1]))
  }
  Matter(a$value - b$value, a$unit, class(a)[1])
}

#' @export
`*.Matter` <- function(a, b) {
  if (is.numeric(b)) {
    Matter(a$value * b, a$unit, class(a)[1])
  } else if (is.numeric(a)) {
    Matter(a * b$value, b$unit, class(b)[1])
  } else {
    stop(paste("Cannot multiply", class(a)[1], "by", class(b)[1]))
  }
}

#' @export
`/.Matter` <- function(a, b) {
  if (is.numeric(b)) {
    Matter(a$value / b, a$unit, class(a)[1])
  } else if (inherits(b, class(a)[1])) {
    # Same type division yields dimensionless ratio
    a$value / b$value
  } else {
    stop(paste("Cannot divide", class(a)[1], "by", class(b)[1]))
  }
}

#' @export
`<.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value < b$value
}

#' @export
`>.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value > b$value
}

#' @export
`<=.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value <= b$value
}

#' @export
`>=.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value >= b$value
}

#' @export
`==.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    return(FALSE)
  }
  a$value == b$value
}

#' @export
print.Matter <- function(x, ...) {
  if (x$unit == "") {
    cat(paste0(class(x)[1], "(", x$value, ")\n"))
  } else {
    cat(paste0(class(x)[1], "(", x$value, " ", x$unit, ")\n"))
  }
  invisible(x)
}

# ============================================================================
#  BOOK III: THE BLUEPRINT
# ============================================================================

#' Create a Blueprint Class
#'
#' @description
#' Blueprint is the core pattern for constraint-verified state management.
#' It combines:
#' - Fields: The state space
#' - Laws: Constraints that must never be violated (combinations)
#' - Forges: Operations that transform state under law protection
#'
#' @details
#' The Blueprint pattern inverts traditional OOP:
#' - Traditional: Methods do things, validation is optional
#' - Blueprint: Laws define what cannot happen, forges operate within bounds
#'
#' Every forge execution:
#' 1. Saves current state
#' 2. Executes the operation
#' 3. Checks ALL laws
#' 4. If any law triggers finfr: rollback to saved state
#' 5. If all laws pass: commit new state
#'
#' This is verification AS computation, not verification OF computation.
#'
#' @param fields Named list of default field values
#' @param laws Named list of law functions (take self, may call finfr/fin)
#' @param forges Named list of forge functions (take self + args)
#' @return A Blueprint factory with $new() method
#'
#' @examples
#' # Bank account that cannot overdraft
#' BankAccount <- Blueprint(
#'   fields = list(
#'     balance = Money(0),
#'     owner = ""
#'   ),
#'   laws = list(
#'     no_overdraft = function(self) {
#'       when_cond(self$balance < Money(0), finfr())
#'     }
#'   ),
#'   forges = list(
#'     deposit = function(self, amount) {
#'       self$balance <- self$balance + amount
#'       self$balance
#'     },
#'     withdraw = function(self, amount) {
#'       self$balance <- self$balance - amount
#'       self$balance
#'     }
#'   )
#' )
#'
#' account <- BankAccount$new(balance = Money(100), owner = "Alice")
#' account$deposit(Money(50))   # Works: balance = 150
#' account$withdraw(Money(200)) # Blocked by finfr! balance stays 150
#'
#' @export
Blueprint <- function(fields = list(), laws = list(), forges = list()) {

  # Store the blueprint definition
  blueprint_def <- list(
    fields = fields,
    laws = laws,
    forges = forges
  )

  # The constructor returns an object with $new() method
  result <- list(
    new = function(...) {
      # Create instance environment
      instance <- new.env(parent = emptyenv())

      # Initialize fields from defaults and overrides
      init_args <- list(...)
      for (name in names(blueprint_def$fields)) {
        if (name %in% names(init_args)) {
          instance[[name]] <- init_args[[name]]
        } else {
          instance[[name]] <- blueprint_def$fields[[name]]
        }
      }

      # State management functions
      instance$save_state <- function() {
        state <- list()
        for (name in names(blueprint_def$fields)) {
          state[[name]] <- instance[[name]]
        }
        state
      }

      instance$restore_state <- function(state) {
        for (name in names(state)) {
          instance[[name]] <- state[[name]]
        }
      }

      instance$get_state <- function() {
        state <- list()
        for (name in names(blueprint_def$fields)) {
          state[[name]] <- instance[[name]]
        }
        state
      }

      # Law checking function
      instance$check_laws <- function() {
        for (law_name in names(blueprint_def$laws)) {
          law_fn <- blueprint_def$laws[[law_name]]
          tryCatch(
            law_fn(instance),
            finfr = function(e) {
              return(list(triggered = TRUE, law = law_name, type = "finfr"))
            },
            fin = function(e) {
              return(list(triggered = TRUE, law = law_name, type = "fin"))
            }
          )
        }
        list(triggered = FALSE)
      }

      # Create forge wrappers with automatic law checking
      for (forge_name in names(blueprint_def$forges)) {
        local({
          fn <- blueprint_def$forges[[forge_name]]
          fname <- forge_name

          instance[[fname]] <- function(...) {
            # Save state for potential rollback
            saved <- instance$save_state()

            tryCatch({
              # Execute the forge
              result <- fn(instance, ...)

              # Check all laws after execution
              for (law_name in names(blueprint_def$laws)) {
                law_fn <- blueprint_def$laws[[law_name]]
                tryCatch(
                  law_fn(instance),
                  finfr = function(e) {
                    # Rollback and re-raise
                    instance$restore_state(saved)
                    finfr(law_name)
                  },
                  fin = function(e) {
                    instance$restore_state(saved)
                    fin(law_name)
                  }
                )
              }

              result
            }, error = function(e) {
              if (inherits(e, "tinytalk_error")) {
                instance$restore_state(saved)
              }
              stop(e)
            })
          }
        })
      }

      class(instance) <- c("BlueprintInstance", "environment")
      instance
    }
  )

  class(result) <- c("Blueprint", "list")
  result
}

#' @export
print.BlueprintInstance <- function(x, ...) {
  state <- x$get_state()
  fields_str <- paste(
    sapply(names(state), function(n) {
      val <- state[[n]]
      if (inherits(val, "Matter")) {
        paste0(n, "=", val$value, " ", val$unit)
      } else {
        paste0(n, "=", format(val))
      }
    }),
    collapse = ", "
  )
  cat(paste0("Blueprint(", fields_str, ")\n"))
  invisible(x)
}

#' @export
print.Blueprint <- function(x, ...) {
  cat("Blueprint()\n")
  cat("  Use $new() to create instances\n")
  invisible(x)
}
