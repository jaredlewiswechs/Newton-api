# ============================================================================
#  BOOK IV: THE ENGINE - Motion and State Transitions
# ============================================================================
#
#  The Engine resolves motion through the Delta Function.
#  Every state transition is captured as:
#    Delta = Presence(end) - Presence(start)
#
#  Boundary checks ensure transitions stay within valid constraint space.
#
# ============================================================================

#' Presence - A Snapshot of State
#'
#' @description
#' Presence captures the complete state at a moment in time.
#' It's the "photograph" of the constraint space.
#'
#' @param state Named list of state values
#' @param timestamp Optional timestamp
#' @param label Optional descriptive label
#' @return A Presence object
#'
#' @examples
#' # Capture current account state
#' p1 <- Presence(list(balance = 1000, transactions = 5), label = "before_withdrawal")
#'
#' @export
Presence <- function(state, timestamp = NULL, label = "") {
  if (is.null(timestamp)) {
    timestamp <- Sys.time()
  }
  structure(
    list(state = state, timestamp = timestamp, label = label),
    class = "Presence"
  )
}

#' @export
print.Presence <- function(x, ...) {
  state_str <- paste(
    sapply(names(x$state), function(n) {
      val <- x$state[[n]]
      if (inherits(val, "Matter")) {
        paste0(n, "=", val$value, " ", val$unit)
      } else {
        paste0(n, "=", format(val))
      }
    }),
    collapse = ", "
  )
  cat(paste0("Presence(", state_str, ")\n"))
  if (x$label != "") {
    cat(paste0("  label: '", x$label, "'\n"))
  }
  invisible(x)
}

#' Delta - The Resolution Between Two Presences
#'
#' @description
#' Delta captures what changed between two states.
#' This is the mathematical heart of motion in Newton.
#'
#' @details
#' The Delta function enables:
#' - Precise tracking of state changes
#' - Boundary violation detection
#' - Audit trail generation
#' - Rollback computation
#'
#' @param changes Named list of changes (from, to, delta)
#' @param source Source Presence
#' @param target Target Presence
#' @return A Delta object
#'
#' @export
Delta <- function(changes, source = NULL, target = NULL) {
  structure(
    list(changes = changes, source = source, target = target),
    class = "Delta"
  )
}

#' Calculate Delta Between Two Presences
#'
#' @description
#' Compute the mathematical difference between two state snapshots.
#'
#' @param start_p Starting Presence
#' @param end_p Ending Presence
#' @return A Delta object describing all changes
#'
#' @examples
#' p1 <- Presence(list(balance = 1000, count = 5))
#' p2 <- Presence(list(balance = 800, count = 6))
#' d <- calculate_delta(p1, p2)
#' # Shows: balance: 1000 -> 800 (delta: -200)
#' #        count: 5 -> 6 (delta: 1)
#'
#' @export
calculate_delta <- function(start_p, end_p) {
  changes <- list()

  all_keys <- unique(c(names(start_p$state), names(end_p$state)))

  for (key in all_keys) {
    start_val <- start_p$state[[key]]
    end_val <- end_p$state[[key]]

    if (!identical(start_val, end_val)) {
      # Handle Matter types
      if (inherits(start_val, "Matter") && inherits(end_val, "Matter")) {
        changes[[key]] <- list(
          from = start_val$value,
          to = end_val$value,
          delta = end_val$value - start_val$value,
          unit = start_val$unit
        )
      } else if (is.numeric(start_val) && is.numeric(end_val)) {
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

#' @export
print.Delta <- function(x, ...) {
  cat("Delta(\n")
  for (key in names(x$changes)) {
    change <- x$changes[[key]]
    if (!is.null(change$delta)) {
      unit_str <- if (!is.null(change$unit)) paste0(" ", change$unit) else ""
      cat(sprintf("  %s: %s -> %s (delta: %+g%s)\n",
                  key, change$from, change$to, change$delta, unit_str))
    } else {
      cat(sprintf("  %s: %s -> %s\n", key, change$from, change$to))
    }
  }
  cat(")\n")
  invisible(x)
}

#' KineticEngine - Resolves Motion Through Boundary Checks
#'
#' @description
#' The KineticEngine validates state transitions against boundary constraints.
#' It's the runtime enforcement of Newton's constraint philosophy.
#'
#' @details
#' The engine operates on the principle of combinations over permutations:
#' rather than checking all possible invalid transitions, it defines
#' boundary conditions that constrain the space of valid motions.
#'
#' @return A KineticEngine environment
#'
#' @examples
#' engine <- KineticEngine()
#'
#' # Add boundary: balance cannot go negative
#' engine$add_boundary(
#'   function(delta) {
#'     if ("balance" %in% names(delta$changes)) {
#'       delta$changes$balance$to < 0
#'     } else {
#'       FALSE
#'     }
#'   },
#'   name = "no_overdraft"
#' )
#'
#' # Test motion
#' p1 <- Presence(list(balance = 100))
#' p2 <- Presence(list(balance = -50))
#' result <- engine$resolve_motion(p1, p2)
#' # result$status == "finfr" (boundary violated)
#'
#' @export
KineticEngine <- function() {
  engine <- new.env(parent = emptyenv())

  engine$presence_start <- NULL
  engine$presence_end <- NULL
  engine$kinetic_delta <- NULL
  engine$boundary_checks <- list()

  #' Add a boundary check
  #' @param check Function that takes Delta, returns TRUE if violated
  #' @param name Name of the boundary
  engine$add_boundary <- function(check, name = "") {
    engine$boundary_checks[[length(engine$boundary_checks) + 1]] <- list(
      check = check,
      name = name
    )
    invisible(engine)
  }

  #' Resolve motion between two presences
  #' @param start_p Starting Presence
  #' @param end_p Ending Presence
  #' @return Resolution result with status and delta
  engine$resolve_motion <- function(start_p, end_p) {
    engine$presence_start <- start_p
    engine$presence_end <- end_p
    engine$kinetic_delta <- calculate_delta(start_p, end_p)

    # Check all boundaries
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

  #' Clear all boundaries
  engine$clear_boundaries <- function() {
    engine$boundary_checks <- list()
    invisible(engine)
  }

  #' Get boundary count
  engine$boundary_count <- function() {
    length(engine$boundary_checks)
  }

  class(engine) <- c("KineticEngine", "environment")
  engine
}

#' @export
print.KineticEngine <- function(x, ...) {
  cat("KineticEngine\n")
  cat("  Boundaries:", length(x$boundary_checks), "\n")
  for (i in seq_along(x$boundary_checks)) {
    boundary <- x$boundary_checks[[i]]
    cat(sprintf("    [%d] %s\n", i, boundary$name))
  }
  invisible(x)
}

#' Quick Motion Calculation
#'
#' @description
#' Convenience function to calculate delta between two state snapshots.
#'
#' @param start Named list representing start state
#' @param end Named list representing end state
#' @return A Delta object
#'
#' @examples
#' delta <- motion(
#'   list(x = 0, y = 0),
#'   list(x = 10, y = 5)
#' )
#'
#' @export
motion <- function(start, end) {
  calculate_delta(Presence(start), Presence(end))
}

# ============================================================================
#  Trajectory - Path Through State Space
# ============================================================================

#' Trajectory - A Sequence of Presences
#'
#' @description
#' Trajectory captures the complete path through state space,
#' enabling analysis of motion patterns and constraint compliance.
#'
#' @return A Trajectory environment
#'
#' @examples
#' traj <- Trajectory()
#' traj$record(list(balance = 1000))
#' traj$record(list(balance = 800))
#' traj$record(list(balance = 1200))
#' traj$summary()
#'
#' @export
Trajectory <- function() {
  traj <- new.env(parent = emptyenv())

  traj$presences <- list()
  traj$deltas <- list()

  #' Record a new presence
  #' @param state Current state
  #' @param label Optional label
  traj$record <- function(state, label = "") {
    p <- Presence(state, label = label)
    n <- length(traj$presences)

    traj$presences[[n + 1]] <- p

    # Calculate delta from previous if exists
    if (n > 0) {
      d <- calculate_delta(traj$presences[[n]], p)
      traj$deltas[[n]] <- d
    }

    invisible(p)
  }

  #' Get all presences
  traj$get_presences <- function() {
    traj$presences
  }

  #' Get all deltas
  traj$get_deltas <- function() {
    traj$deltas
  }

  #' Summarize trajectory
  traj$summary <- function() {
    n <- length(traj$presences)
    if (n == 0) {
      cat("Empty trajectory\n")
      return(invisible(NULL))
    }

    cat(sprintf("Trajectory: %d presences, %d deltas\n", n, length(traj$deltas)))

    # Show first and last
    cat("\nFirst state:\n")
    print(traj$presences[[1]])

    if (n > 1) {
      cat("\nLast state:\n")
      print(traj$presences[[n]])

      # Calculate total delta
      cat("\nTotal motion:\n")
      total <- calculate_delta(traj$presences[[1]], traj$presences[[n]])
      print(total)
    }

    invisible(NULL)
  }

  class(traj) <- c("Trajectory", "environment")
  traj
}

#' @export
print.Trajectory <- function(x, ...) {
  cat(sprintf("Trajectory(%d presences)\n", length(x$presences)))
  invisible(x)
}
