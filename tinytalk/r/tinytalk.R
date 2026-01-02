# ═══════════════════════════════════════════════════════════════════════════════
#  tinyTalk for R
# ═══════════════════════════════════════════════════════════════════════════════
#
# The "No-First" constraint language. Define what cannot happen.
#
# Usage:
#   source("tinytalk.R")
#
#   # Create a blueprint
#   RiskGovernor <- Blueprint(
#     fields = list(
#       assets = Money(1000),
#       liabilities = Money(0)
#     ),
#     laws = list(
#       insolvency = function(self) {
#         when_cond(self$liabilities > self$assets, finfr())
#       }
#     ),
#     forges = list(
#       execute_trade = function(self, amount) {
#         self$liabilities <- self$liabilities + amount
#         "cleared"
#       }
#     )
#   )
#
#   gov <- RiskGovernor$new()
#   gov$execute_trade(Money(500))   # Works
#   gov$execute_trade(Money(600))   # Blocked by finfr

# ═══════════════════════════════════════════════════════════════════════════════
# BOOK I: THE LEXICON
# ═══════════════════════════════════════════════════════════════════════════════

#' Finfr - Finality, Ontological Death
#' @description The state cannot exist. Raises an error.
#' @param law_name Name of the law that triggered finfr
#' @param message Optional message
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

#' Fin - Closure
#' @description A stopping point that can be reopened.
#' @param law_name Name of the law that triggered fin
#' @param message Optional message
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
#' @description Declares a fact. Executes result if condition is TRUE.
#' @param condition The condition to check
#' @param result What to do if TRUE (use finfr() or fin())
when_cond <- function(condition, result = NULL) {
  if (isTRUE(condition)) {
    if (is.function(result)) {
      result()
    } else if (!is.null(result)) {
      result
    }
  }
  invisible(condition)
}

# ═══════════════════════════════════════════════════════════════════════════════
# BOOK II: MATTER - Typed Values
# ═══════════════════════════════════════════════════════════════════════════════

#' Create a Matter type (base constructor)
#' @param value Numeric value
#' @param unit Unit string
#' @param type Matter type name
Matter <- function(value, unit, type) {
  structure(
    list(value = as.numeric(value), unit = unit),
    class = c(type, "Matter")
  )
}

#' Money type
#' @param value Numeric value
#' @param unit Currency unit (default: "USD")
Money <- function(value, unit = "USD") {
  Matter(value, unit, "Money")
}

#' Mass type
#' @param value Numeric value
#' @param unit Mass unit (default: "kg")
Mass <- function(value, unit = "kg") {
  Matter(value, unit, "Mass")
}

#' Distance type
#' @param value Numeric value
#' @param unit Distance unit (default: "m")
Distance <- function(value, unit = "m") {
  Matter(value, unit, "Distance")
}

#' Temperature type
#' @param value Numeric value
#' @param unit Temperature unit (default: "C")
Temperature <- function(value, unit = "C") {
  Matter(value, unit, "Temperature")
}

#' Convenience: Celsius
Celsius <- function(value) Temperature(value, "C")

#' Convenience: Fahrenheit
Fahrenheit <- function(value) Temperature(value, "F")

#' Pressure type
#' @param value Numeric value
#' @param unit Pressure unit (default: "PSI")
Pressure <- function(value, unit = "PSI") {
  Matter(value, unit, "Pressure")
}

#' Convenience: PSI
PSI <- function(value) Pressure(value, "PSI")

#' Volume type
#' @param value Numeric value
#' @param unit Volume unit (default: "L")
Volume <- function(value, unit = "L") {
  Matter(value, unit, "Volume")
}

#' Convenience: Liters
Liters <- function(value) Volume(value, "L")

#' Convenience: Meters
Meters <- function(value) Distance(value, "m")

#' Convenience: Kilograms
Kilograms <- function(value) Mass(value, "kg")

# Matter operations
`+.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot add", class(a)[1], "and", class(b)[1]))
  }
  Matter(a$value + b$value, a$unit, class(a)[1])
}

`-.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot subtract", class(b)[1], "from", class(a)[1]))
  }
  Matter(a$value - b$value, a$unit, class(a)[1])
}

`*.Matter` <- function(a, b) {
  if (is.numeric(b)) {
    Matter(a$value * b, a$unit, class(a)[1])
  } else {
    stop(paste("Cannot multiply", class(a)[1], "by", class(b)[1]))
  }
}

`/.Matter` <- function(a, b) {
  if (is.numeric(b)) {
    Matter(a$value / b, a$unit, class(a)[1])
  } else if (inherits(b, class(a)[1])) {
    a$value / b$value  # Returns scalar
  } else {
    stop(paste("Cannot divide", class(a)[1], "by", class(b)[1]))
  }
}

`<.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value < b$value
}

`>.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value > b$value
}

`<=.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value <= b$value
}

`>=.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    stop(paste("Cannot compare", class(a)[1], "with", class(b)[1]))
  }
  a$value >= b$value
}

`==.Matter` <- function(a, b) {
  if (!inherits(b, class(a)[1])) {
    return(FALSE)
  }
  a$value == b$value
}

print.Matter <- function(x, ...) {
  cat(paste0(class(x)[1], "(", x$value, " ", x$unit, ")\n"))
  invisible(x)
}

# ═══════════════════════════════════════════════════════════════════════════════
# BOOK III: THE BLUEPRINT
# ═══════════════════════════════════════════════════════════════════════════════

#' Create a Blueprint class
#' @param fields Named list of default field values
#' @param laws Named list of law functions
#' @param forges Named list of forge functions
Blueprint <- function(fields = list(), laws = list(), forges = list()) {

  # Create the blueprint environment
  blueprint_def <- list(
    fields = fields,
    laws = laws,
    forges = forges
  )

  # The constructor
  result <- list(
    new = function(...) {
      # Create instance environment
      instance <- new.env(parent = emptyenv())

      # Initialize fields
      init_args <- list(...)
      for (name in names(blueprint_def$fields)) {
        if (name %in% names(init_args)) {
          instance[[name]] <- init_args[[name]]
        } else {
          # Deep copy default value
          default <- blueprint_def$fields[[name]]
          if (is.list(default) || inherits(default, "Matter")) {
            instance[[name]] <- default
          } else {
            instance[[name]] <- default
          }
        }
      }

      # Add save/restore state functions
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

      # Add check_laws function
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

      # Create forge wrappers with law checking
      for (forge_name in names(blueprint_def$forges)) {
        local({
          fn <- blueprint_def$forges[[forge_name]]
          fname <- forge_name

          instance[[fname]] <- function(...) {
            # Save state for rollback
            saved <- instance$save_state()

            tryCatch({
              # Execute forge
              result <- fn(instance, ...)

              # Check all laws after execution
              for (law_name in names(blueprint_def$laws)) {
                law_fn <- blueprint_def$laws[[law_name]]
                tryCatch(
                  law_fn(instance),
                  finfr = function(e) {
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

print.BlueprintInstance <- function(x, ...) {
  state <- x$get_state()
  fields_str <- paste(
    sapply(names(state), function(n) paste0(n, "=", format(state[[n]]))),
    collapse = ", "
  )
  cat(paste0("Blueprint(", fields_str, ")\n"))
  invisible(x)
}

# ═══════════════════════════════════════════════════════════════════════════════
# BOOK IV: THE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

#' Presence - A snapshot of state
#' @param state Named list of state values
#' @param timestamp Optional timestamp
#' @param label Optional label
Presence <- function(state, timestamp = NULL, label = "") {
  structure(
    list(state = state, timestamp = timestamp, label = label),
    class = "Presence"
  )
}

print.Presence <- function(x, ...) {
  cat(paste0("Presence(", paste(names(x$state), x$state, sep = "=", collapse = ", "),
             ", label='", x$label, "')\n"))
  invisible(x)
}

#' Delta - The mathematical resolution between two Presences
#' @param changes Named list of changes
#' @param source Source Presence
#' @param target Target Presence
Delta <- function(changes, source = NULL, target = NULL) {
  structure(
    list(changes = changes, source = source, target = target),
    class = "Delta"
  )
}

#' Calculate delta between two presences
#' @param start_p Starting Presence
#' @param end_p Ending Presence
calculate_delta <- function(start_p, end_p) {
  changes <- list()

  all_keys <- unique(c(names(start_p$state), names(end_p$state)))

  for (key in all_keys) {
    start_val <- start_p$state[[key]]
    end_val <- end_p$state[[key]]

    if (!identical(start_val, end_val)) {
      if (is.numeric(start_val) && is.numeric(end_val)) {
        changes[[key]] <- list(
          from = start_val,
          to = end_val,
          delta = end_val - start_val
        )
      } else {
        changes[[key]] <- list(
          from = start_val,
          to = end_val,
          delta = NULL
        )
      }
    }
  }

  Delta(changes, source = start_p, target = end_p)
}

print.Delta <- function(x, ...) {
  cat("Delta(\n")
  for (key in names(x$changes)) {
    change <- x$changes[[key]]
    if (!is.null(change$delta)) {
      cat(paste0("  ", key, ": ", change$from, " -> ", change$to,
                 " (delta: ", change$delta, ")\n"))
    } else {
      cat(paste0("  ", key, ": ", change$from, " -> ", change$to, "\n"))
    }
  }
  cat(")\n")
  invisible(x)
}

#' KineticEngine - Resolves motion through the Delta Function
#' @description Creates a kinetic engine with optional boundary checks
KineticEngine <- function() {
  engine <- new.env(parent = emptyenv())

  engine$presence_start <- NULL
  engine$presence_end <- NULL
  engine$kinetic_delta <- NULL
  engine$boundary_checks <- list()

  #' Add a boundary check
  #' @param check Function that takes a Delta and returns TRUE if violated
  #' @param name Name of the boundary
engine$add_boundary <- function(check, name = "") {
    engine$boundary_checks[[length(engine$boundary_checks) + 1]] <- list(
      check = check,
      name = name
    )
  }

  #' Resolve motion between two presences
  #' @param start_p Starting Presence
  #' @param end_p Ending Presence
  engine$resolve_motion <- function(start_p, end_p) {
    engine$presence_start <- start_p
    engine$presence_end <- end_p
    engine$kinetic_delta <- calculate_delta(start_p, end_p)

    # Check boundaries
    for (boundary in engine$boundary_checks) {
      if (boundary$check(engine$kinetic_delta)) {
        return(list(
          status = "finfr",
          reason = paste0("Boundary '", boundary$name, "' violated"),
          message = "ONTO DEATH: This motion cannot exist.",
          delta = engine$kinetic_delta$changes
        ))
      }
    }

    list(
      status = "synchronized",
      delta = engine$kinetic_delta$changes,
      from = start_p$state,
      to = end_p$state
    )
  }

  class(engine) <- c("KineticEngine", "environment")
  engine
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

#' Quick motion calculation
#' @param start Named list representing start state
#' @param end Named list representing end state
motion <- function(start, end) {
  calculate_delta(Presence(start), Presence(end))
}

# Print package info on load
cat("
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk for R - v1.0.0
 The 'No-First' constraint language. Define what cannot happen.
═══════════════════════════════════════════════════════════════════════════════
")
