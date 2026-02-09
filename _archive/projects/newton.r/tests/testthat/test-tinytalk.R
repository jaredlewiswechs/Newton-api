# Tests for tinyTalk core functionality

test_that("finfr raises correct error class", {
  expect_error(finfr("test_law"), class = "finfr")
})

test_that("fin raises correct error class", {
  expect_error(fin("test_law"), class = "fin")
})

test_that("when_cond triggers on TRUE condition", {
  expect_error(
    when_cond(TRUE, finfr()),
    class = "finfr"
  )
})

test_that("when_cond does not trigger on FALSE condition", {
  result <- when_cond(FALSE, finfr())
  expect_false(result)
})

test_that("ratio returns value when within threshold", {
  r <- ratio(500, 1000, threshold = 1.0)
  expect_equal(r, 0.5)
})

test_that("ratio triggers finfr when exceeding threshold", {
  expect_error(
    ratio(1500, 1000, threshold = 1.0),
    class = "finfr"
  )
})

test_that("ratio triggers finfr when denominator is zero", {
  expect_error(
    ratio(100, 0, threshold = 1.0),
    class = "finfr"
  )
})

test_that("Money type arithmetic works", {
  m1 <- Money(100)
  m2 <- Money(50)

  expect_equal((m1 + m2)$value, 150)
  expect_equal((m1 - m2)$value, 50)
  expect_equal((m1 * 2)$value, 200)
  expect_equal((m1 / 2)$value, 50)
  expect_equal(m1 / m2, 2)  # Dimensionless
})

test_that("Money type comparison works", {
  m1 <- Money(100)
  m2 <- Money(50)

  expect_true(m1 > m2)
  expect_true(m2 < m1)
  expect_true(m1 >= Money(100))
  expect_true(m2 <= Money(50))
  expect_true(m1 == Money(100))
})

test_that("Money type cannot mix with other types", {
  m <- Money(100)
  kg <- Mass(50)

  expect_error(m + kg)
  expect_error(m - kg)
  expect_error(m < kg)
})

test_that("Blueprint creates instances with default fields", {
  TestBlueprint <- Blueprint(
    fields = list(value = 10)
  )

  instance <- TestBlueprint$new()
  expect_equal(instance$value, 10)
})

test_that("Blueprint creates instances with override fields", {
  TestBlueprint <- Blueprint(
    fields = list(value = 10)
  )

  instance <- TestBlueprint$new(value = 20)
  expect_equal(instance$value, 20)
})

test_that("Blueprint laws trigger finfr on violation", {
  Account <- Blueprint(
    fields = list(balance = Money(100)),
    laws = list(
      no_overdraft = function(self) {
        when_cond(self$balance < Money(0), finfr())
      }
    ),
    forges = list(
      withdraw = function(self, amount) {
        self$balance <- self$balance - amount
      }
    )
  )

  acct <- Account$new()

  # Valid withdrawal
  acct$withdraw(Money(50))
  expect_equal(acct$balance$value, 50)

  # Invalid withdrawal - should trigger finfr and rollback
  expect_error(
    acct$withdraw(Money(100)),
    class = "finfr"
  )

  # Balance should be unchanged
 expect_equal(acct$balance$value, 50)
})

test_that("Blueprint state rolls back on law violation", {
  Counter <- Blueprint(
    fields = list(count = 0, max = 5),
    laws = list(
      max_limit = function(self) {
        when_cond(self$count > self$max, finfr())
      }
    ),
    forges = list(
      increment = function(self, n = 1) {
        self$count <- self$count + n
      }
    )
  )

  c <- Counter$new()
  c$increment(3)
  expect_equal(c$count, 3)

  c$increment(2)
  expect_equal(c$count, 5)

  # This would exceed max
  expect_error(c$increment(1), class = "finfr")
  expect_equal(c$count, 5)  # Rolled back
})
