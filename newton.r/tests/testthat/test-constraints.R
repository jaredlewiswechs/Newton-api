# Tests for CDL constraint builders

test_that("constraint creates valid structure", {
  c <- constraint("balance", "ge", 0)

  expect_s3_class(c, "cdl_constraint")
  expect_equal(c$field, "balance")
  expect_equal(c$operator, "ge")
  expect_equal(c$value, 0)
})

test_that("constraint generates ID automatically", {
  c <- constraint("balance", "ge", 0)
  expect_match(c$id, "constraint_balance_ge")
})

test_that("constraint accepts custom ID", {
  c <- constraint("balance", "ge", 0, id = "my_custom_id")
  expect_equal(c$id, "my_custom_id")
})

test_that("constraint accepts domain", {
  c <- constraint("balance", "ge", 0, domain = "FINANCIAL")
  expect_equal(c$domain, "FINANCIAL")
})

test_that("ratio_constraint creates valid structure", {
  c <- ratio_constraint("debt", "equity", "le", 3.0)

  expect_s3_class(c, "cdl_ratio_constraint")
  expect_equal(c$f_field, "debt")
  expect_equal(c$g_field, "equity")
  expect_equal(c$operator, "ratio_le")
  expect_equal(c$threshold, 3.0)
})

test_that("temporal_constraint creates valid structure", {
  c <- temporal_constraint("created_at", "within", "24h")

  expect_s3_class(c, "cdl_temporal_constraint")
  expect_equal(c$field, "created_at")
  expect_equal(c$operator, "within")
  expect_equal(c$reference, "24h")
})

test_that("composite_constraint with AND", {
  c <- composite_constraint("AND", list(
    constraint("a", "ge", 0),
    constraint("b", "le", 100)
  ))

  expect_s3_class(c, "cdl_composite_constraint")
  expect_equal(c$operator, "AND")
  expect_equal(length(c$constraints), 2)
})

test_that("all_of creates AND composite", {
  c <- all_of(
    constraint("a", "ge", 0),
    constraint("b", "le", 100)
  )

  expect_equal(c$operator, "AND")
  expect_equal(length(c$constraints), 2)
})

test_that("any_of creates OR composite", {
  c <- any_of(
    constraint("role", "eq", "admin"),
    constraint("role", "eq", "moderator")
  )

  expect_equal(c$operator, "OR")
  expect_equal(length(c$constraints), 2)
})

test_that("none_of creates NOT composite", {
  c <- none_of(constraint("status", "eq", "blocked"))

  expect_equal(c$operator, "NOT")
  expect_equal(length(c$constraints), 1)
})

test_that("financial helpers work", {
  no_od <- financial$no_overdraft("balance")
  expect_equal(no_od$field, "balance")
  expect_equal(no_od$operator, "ge")
  expect_equal(no_od$value, 0)

  lev <- financial$leverage_limit("debt", "equity", 3.0)
  expect_equal(lev$f_field, "debt")
  expect_equal(lev$g_field, "equity")
  expect_equal(lev$threshold, 3.0)
})

test_that("cdl_domain constants are defined", {
  expect_equal(cdl_domain$FINANCIAL, "FINANCIAL")
  expect_equal(cdl_domain$HEALTH, "HEALTH")
  expect_equal(cdl_domain$EPISTEMIC, "EPISTEMIC")
})
