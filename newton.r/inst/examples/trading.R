# ============================================================================
#  Example: Risk-Governed Trading System
# ============================================================================
#
#  Demonstrates Newton for financial trading with:
#  - Leverage limits
#  - Position limits
#  - Risk boundaries
#
#  Key insight: Combinations over permutations.
#  We define the valid state SPACE, not enumerate invalid inputs.
#
# ============================================================================

library(newton)

cat("
============================================
Risk-Governed Trading System
============================================
Constraints define what CANNOT happen:
- Leverage > 10x: finfr
- Single position > 20% of capital: finfr
- Total exposure > capital * 10: finfr

The constraint space is the COMBINATION of
all valid states. We don't check permutations.
============================================
")

# ----------------------------------------------------------------------------
#  Define the Trading System Blueprint
# ----------------------------------------------------------------------------

TradingSystem <- Blueprint(
  fields = list(
    capital = Money(1000000),       # Starting capital
    positions = list(),              # Open positions
    total_exposure = Money(0),       # Sum of position sizes
    realized_pnl = Money(0),         # Closed position P&L
    trades_today = 0,
    max_trades_per_day = 100
  ),

  laws = list(
    # Law 1: Maximum leverage of 10x
    max_leverage = function(self) {
      if (self$capital > Money(0)) {
        leverage <- self$total_exposure$value / self$capital$value
        when_cond(leverage > 10, finfr())
      }
    },

    # Law 2: No single position > 20% of capital
    concentration_limit = function(self) {
      max_position_size <- self$capital$value * 0.20
      for (pos in self$positions) {
        when_cond(pos$size$value > max_position_size, finfr())
      }
    },

    # Law 3: Daily trade limit
    trade_limit = function(self) {
      when_cond(self$trades_today > self$max_trades_per_day, finfr())
    },

    # Law 4: Exposure cannot be negative
    positive_exposure = function(self) {
      when_cond(self$total_exposure < Money(0), finfr())
    }
  ),

  forges = list(
    # Open a new position
    open_position = function(self, symbol, size) {
      if (!inherits(size, "Money")) {
        size <- Money(size)
      }

      position <- list(
        symbol = symbol,
        size = size,
        opened_at = Sys.time()
      )

      self$positions[[length(self$positions) + 1]] <- position
      self$total_exposure <- self$total_exposure + size
      self$trades_today <- self$trades_today + 1

      leverage <- self$total_exposure$value / self$capital$value

      list(
        action = "open",
        symbol = symbol,
        size = size$value,
        total_exposure = self$total_exposure$value,
        leverage = sprintf("%.2fx", leverage),
        trades_today = self$trades_today
      )
    },

    # Close a position
    close_position = function(self, symbol, pnl) {
      if (!inherits(pnl, "Money")) {
        pnl <- Money(pnl)
      }

      # Find and remove position
      pos_idx <- NULL
      pos_size <- Money(0)
      for (i in seq_along(self$positions)) {
        if (self$positions[[i]]$symbol == symbol) {
          pos_idx <- i
          pos_size <- self$positions[[i]]$size
          break
        }
      }

      if (is.null(pos_idx)) {
        stop(paste("Position not found:", symbol))
      }

      # Remove position
      self$positions <- self$positions[-pos_idx]
      self$total_exposure <- self$total_exposure - pos_size
      self$realized_pnl <- self$realized_pnl + pnl
      self$trades_today <- self$trades_today + 1

      list(
        action = "close",
        symbol = symbol,
        size_closed = pos_size$value,
        pnl = pnl$value,
        total_exposure = self$total_exposure$value,
        realized_pnl = self$realized_pnl$value
      )
    },

    # Add capital
    add_capital = function(self, amount) {
      if (!inherits(amount, "Money")) {
        amount <- Money(amount)
      }
      self$capital <- self$capital + amount
      list(
        action = "add_capital",
        amount = amount$value,
        new_capital = self$capital$value
      )
    }
  )
)

# ----------------------------------------------------------------------------
#  Create System and Trade
# ----------------------------------------------------------------------------

cat("\n--- Initializing Trading System ---\n")

system <- TradingSystem$new()
cat(sprintf("Capital: $%s\n", format(system$capital$value, big.mark = ",")))
cat(sprintf("Max leverage: 10x ($%s exposure)\n",
            format(system$capital$value * 10, big.mark = ",")))

# ----------------------------------------------------------------------------
#  Build Up Positions (Valid Operations)
# ----------------------------------------------------------------------------

cat("\n--- Building Positions ---\n")

# Open several positions
positions_to_open <- list(
  list(symbol = "AAPL", size = 500000),
  list(symbol = "GOOGL", size = 400000),
  list(symbol = "MSFT", size = 300000),
  list(symbol = "AMZN", size = 200000)
)

for (pos in positions_to_open) {
  result <- system$open_position(pos$symbol, Money(pos$size))
  cat(sprintf("Opened %s: $%s | Total exposure: $%s | Leverage: %s\n",
              result$symbol,
              format(result$size, big.mark = ","),
              format(result$total_exposure, big.mark = ","),
              result$leverage))
}

# ----------------------------------------------------------------------------
#  Test Leverage Limit (finfr)
# ----------------------------------------------------------------------------

cat("\n--- Testing Leverage Limit ---\n")

current_exposure <- system$total_exposure$value
remaining_capacity <- (system$capital$value * 10) - current_exposure
cat(sprintf("Current exposure: $%s\n", format(current_exposure, big.mark = ",")))
cat(sprintf("Remaining capacity: $%s\n", format(remaining_capacity, big.mark = ",")))

# This should work (stays under 10x)
cat("\nOpening NVDA for $8M (stays under 10x)...\n")
result <- system$open_position("NVDA", Money(8000000))
cat(sprintf("Success! Leverage now: %s\n", result$leverage))

# This would exceed 10x - should trigger finfr
cat("\nTrying to open TSLA for $2M (would exceed 10x)...\n")
tryCatch({
  system$open_position("TSLA", Money(2000000))
  cat("ERROR: This should have been blocked!\n")
}, finfr = function(e) {
  cat("BLOCKED by finfr: Leverage limit would be exceeded\n")
  cat(sprintf("Exposure unchanged: $%s\n",
              format(system$total_exposure$value, big.mark = ",")))
})

# ----------------------------------------------------------------------------
#  Test Concentration Limit (finfr)
# ----------------------------------------------------------------------------

cat("\n--- Testing Concentration Limit ---\n")

max_single_position <- system$capital$value * 0.20
cat(sprintf("Max single position: $%s (20%% of capital)\n",
            format(max_single_position, big.mark = ",")))

# Close some positions to make room
cat("\nClosing NVDA to free up capacity...\n")
result <- system$close_position("NVDA", Money(50000))  # $50k profit
cat(sprintf("Closed NVDA, realized P&L: $%s\n", format(result$pnl, big.mark = ",")))

# Try to open a position that's too large
cat("\nTrying to open META for $300k (> 20% of capital)...\n")
tryCatch({
  system$open_position("META", Money(300000))
  cat("ERROR: This should have been blocked!\n")
}, finfr = function(e) {
  cat("BLOCKED by finfr: Position too concentrated\n")
})

# This size is OK
cat("\nOpening META for $150k (within 20% limit)...\n")
result <- system$open_position("META", Money(150000))
cat(sprintf("Success! Position opened at $%s\n", format(result$size, big.mark = ",")))

# ----------------------------------------------------------------------------
#  Show Final State
# ----------------------------------------------------------------------------

cat("\n--- Final System State ---\n")

cat(sprintf("Capital: $%s\n", format(system$capital$value, big.mark = ",")))
cat(sprintf("Total Exposure: $%s\n", format(system$total_exposure$value, big.mark = ",")))
cat(sprintf("Leverage: %.2fx\n", system$total_exposure$value / system$capital$value))
cat(sprintf("Realized P&L: $%s\n", format(system$realized_pnl$value, big.mark = ",")))
cat(sprintf("Trades today: %d\n", system$trades_today))
cat(sprintf("Open positions: %d\n", length(system$positions)))

cat("\nPositions:\n")
for (pos in system$positions) {
  cat(sprintf("  %s: $%s\n", pos$symbol, format(pos$size$value, big.mark = ",")))
}

# ----------------------------------------------------------------------------
#  Demonstrate KineticEngine for Motion Analysis
# ----------------------------------------------------------------------------

cat("\n--- Motion Analysis with KineticEngine ---\n")

engine <- KineticEngine()

# Add leverage boundary
engine$add_boundary(
  function(delta) {
    if ("leverage" %in% names(delta$changes)) {
      delta$changes$leverage$to > 10
    } else {
      FALSE
    }
  },
  name = "max_leverage_10x"
)

# Test motion
p1 <- Presence(list(exposure = 5000000, capital = 1000000, leverage = 5.0))
p2 <- Presence(list(exposure = 12000000, capital = 1000000, leverage = 12.0))

result <- engine$resolve_motion(p1, p2)
cat(sprintf("Motion status: %s\n", result$status))
if (result$status == "finfr") {
  cat(sprintf("Reason: %s\n", result$reason))
}

cat("\n--- End of Trading Demo ---\n")
