# Tests for Engine functionality (Presence, Delta, KineticEngine)

test_that("Presence captures state", {
  p <- Presence(list(x = 10, y = 20))

  expect_equal(p$state$x, 10)
  expect_equal(p$state$y, 20)
  expect_s3_class(p, "Presence")
})

test_that("Presence captures label", {
  p <- Presence(list(x = 10), label = "test_state")

  expect_equal(p$label, "test_state")
})

test_that("calculate_delta finds changes", {
  p1 <- Presence(list(x = 10, y = 20))
  p2 <- Presence(list(x = 15, y = 20))

  delta <- calculate_delta(p1, p2)

  expect_s3_class(delta, "Delta")
  expect_true("x" %in% names(delta$changes))
  expect_false("y" %in% names(delta$changes))  # y didn't change
  expect_equal(delta$changes$x$from, 10)
  expect_equal(delta$changes$x$to, 15)
  expect_equal(delta$changes$x$delta, 5)
})

test_that("calculate_delta works with Matter types", {
  p1 <- Presence(list(balance = Money(1000)))
  p2 <- Presence(list(balance = Money(800)))

  delta <- calculate_delta(p1, p2)

  expect_equal(delta$changes$balance$from, 1000)
  expect_equal(delta$changes$balance$to, 800)
  expect_equal(delta$changes$balance$delta, -200)
})

test_that("motion convenience function works", {
  delta <- motion(
    list(x = 0, y = 0),
    list(x = 10, y = 5)
  )

  expect_s3_class(delta, "Delta")
  expect_equal(delta$changes$x$delta, 10)
  expect_equal(delta$changes$y$delta, 5)
})

test_that("KineticEngine detects boundary violations", {
  engine <- KineticEngine()

  engine$add_boundary(
    function(delta) {
      if ("balance" %in% names(delta$changes)) {
        delta$changes$balance$to < 0
      } else {
        FALSE
      }
    },
    name = "no_negative_balance"
  )

  # Valid motion
  result <- engine$resolve_motion(
    Presence(list(balance = 100)),
    Presence(list(balance = 50))
  )
  expect_equal(result$status, "synchronized")

  # Invalid motion
  result <- engine$resolve_motion(
    Presence(list(balance = 100)),
    Presence(list(balance = -50))
  )
  expect_equal(result$status, "finfr")
  expect_match(result$reason, "no_negative_balance")
})

test_that("KineticEngine supports multiple boundaries", {
  engine <- KineticEngine()

  engine$add_boundary(
    function(delta) {
      if ("x" %in% names(delta$changes)) {
        delta$changes$x$to < 0
      } else {
        FALSE
      }
    },
    name = "x_positive"
  )

  engine$add_boundary(
    function(delta) {
      if ("y" %in% names(delta$changes)) {
        delta$changes$y$to < 0
      } else {
        FALSE
      }
    },
    name = "y_positive"
  )

  expect_equal(engine$boundary_count(), 2)

  # Violate first boundary
  result <- engine$resolve_motion(
    Presence(list(x = 10, y = 10)),
    Presence(list(x = -5, y = 10))
  )
  expect_equal(result$status, "finfr")

  # Violate second boundary
  result <- engine$resolve_motion(
    Presence(list(x = 10, y = 10)),
    Presence(list(x = 10, y = -5))
  )
  expect_equal(result$status, "finfr")

  # Valid motion
  result <- engine$resolve_motion(
    Presence(list(x = 10, y = 10)),
    Presence(list(x = 5, y = 5))
  )
  expect_equal(result$status, "synchronized")
})

test_that("Trajectory records presences", {
  traj <- Trajectory()

  traj$record(list(x = 0))
  traj$record(list(x = 10))
  traj$record(list(x = 20))

  presences <- traj$get_presences()
  expect_equal(length(presences), 3)

  deltas <- traj$get_deltas()
  expect_equal(length(deltas), 2)
})
