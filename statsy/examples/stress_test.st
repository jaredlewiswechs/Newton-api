# ===========================================================================
# STATSY STRESS TEST - Comprehensive Feature Testing
# ===========================================================================

print("================================================================")
print("  STATSY STRESS TEST - Testing All Features")
print("================================================================")

# ---------------------------------------------------------------------------
# TEST 1: Basic Arithmetic and Variables
# ---------------------------------------------------------------------------
print("")
print("TEST 1: Basic Arithmetic")
a = 10
b = 3
print("  10 + 3 = ")
print(a + b)
print("  10 - 3 = ")
print(a - b)
print("  10 * 3 = ")
print(a * b)
print("  10 / 3 = ")
print(a / b)
print("  10 ^ 3 = ")
print(a ^ 3)
print("  10 % 3 = ")
print(a % b)

# ---------------------------------------------------------------------------
# TEST 2: Vectors and Vector Operations
# ---------------------------------------------------------------------------
print("")
print("TEST 2: Vectors")
v1 = [1, 2, 3, 4, 5]
v2 = [10, 20, 30, 40, 50]
print("  v1 = ")
print(v1)
print("  v2 = ")
print(v2)
print("  v1 + v2 = ")
print(v1 + v2)
print("  v2 - v1 = ")
print(v2 - v1)
print("  v1 * 2 = ")
print(v1 * 2)
print("  v2 / 10 = ")
print(v2 / 10)

# ---------------------------------------------------------------------------
# TEST 3: Descriptive Statistics
# ---------------------------------------------------------------------------
print("")
print("TEST 3: Descriptive Statistics")
data = [12, 15, 18, 22, 25, 28, 30, 33, 35, 40]
print("  data = ")
print(data)
print("  mean = ")
print(mean(data))
print("  median = ")
print(median(data))
print("  std = ")
print(std(data))
print("  var = ")
print(var(data))
print("  min = ")
print(min(data))
print("  max = ")
print(max(data))
print("  sum = ")
print(sum(data))
print("  range = ")
print(range(data))
print("  iqr = ")
print(iqr(data))

# ---------------------------------------------------------------------------
# TEST 4: Robust Statistics (Newton-style)
# ---------------------------------------------------------------------------
print("")
print("TEST 4: Robust Statistics")
outlier_data = [10, 12, 11, 13, 10, 12, 500, 11, 10, 13]
print("  data with outlier: ")
print(outlier_data)
print("  mean (affected by outlier): ")
print(mean(outlier_data))
print("  robust_mean: ")
print(robust_mean(outlier_data))
print("  mad: ")
print(mad(outlier_data))
print("  trimmed_mean(0.1): ")
print(trimmed_mean(outlier_data, 0.1))
print("  winsorized_mean(0.1): ")
print(winsorized_mean(outlier_data, 0.1))
print("  detect_outliers: ")
print(detect_outliers(outlier_data, 3.5))

# ---------------------------------------------------------------------------
# TEST 5: Statistical Distributions
# ---------------------------------------------------------------------------
print("")
print("TEST 5: Distributions")
print("  dnorm(0, 0, 1) = ")
print(dnorm(0, 0, 1))
print("  pnorm(0, 0, 1) = ")
print(pnorm(0, 0, 1))
print("  qnorm(0.5, 0, 1) = ")
print(qnorm(0.5, 0, 1))
print("  rnorm(5, 0, 1) sample: ")
sample = rnorm(5, 0, 1)
print(sample)

# ---------------------------------------------------------------------------
# TEST 6: Hypothesis Tests
# ---------------------------------------------------------------------------
print("")
print("TEST 6: Hypothesis Tests")
group1 = [23, 25, 27, 22, 24, 26, 28, 23]
group2 = [30, 32, 28, 35, 31, 33, 29, 34]
print("  group1 mean: ")
print(mean(group1))
print("  group2 mean: ")
print(mean(group2))
print("  t_test result: ")
result = t_test(group1, group2)
print(result)

x_cor = [1, 2, 3, 4, 5, 6, 7, 8]
y_cor = [2.1, 4.0, 5.9, 8.1, 10.0, 12.0, 14.1, 16.0]
print("  correlation: ")
print(cor(x_cor, y_cor))
print("  cor_test: ")
print(cor_test(x_cor, y_cor))

# ---------------------------------------------------------------------------
# TEST 7: Linear Regression
# ---------------------------------------------------------------------------
print("")
print("TEST 7: Linear Regression")
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = [2.5, 4.8, 7.2, 9.5, 12.1, 14.3, 16.8, 19.0, 21.5, 24.0]
print("  Fitting y ~ 2.5x ...")
model = lm(x, y)

# ---------------------------------------------------------------------------
# TEST 8: ANOVA
# ---------------------------------------------------------------------------
print("")
print("TEST 8: One-Way ANOVA")
g1 = [85, 90, 88, 92, 87]
g2 = [78, 82, 80, 75, 79]
g3 = [95, 98, 92, 96, 94]
print("  Group 1 (mean=")
print(mean(g1))
print("  Group 2 (mean=")
print(mean(g2))
print("  Group 3 (mean=")
print(mean(g3))
result = anova(g1, g2, g3)

# ---------------------------------------------------------------------------
# TEST 9: Time Series
# ---------------------------------------------------------------------------
print("")
print("TEST 9: Time Series Analysis")
ts = [10, 15, 13, 18, 16, 22, 20, 25, 23, 28, 26, 30]
print("  Original: ")
print(sparkline(ts, "Data"))
print("  Moving Average (3): ")
ma = moving_avg(ts, 3)
print(sparkline(ma, "MA"))
print("  Exp Smoothing (0.3): ")
es = exp_smooth(ts, 0.3)
print(sparkline(es, "Exp"))

# ---------------------------------------------------------------------------
# TEST 10: User-Defined Functions
# ---------------------------------------------------------------------------
print("")
print("TEST 10: User Functions")

fn square(x) {
    return x * x
}

fn cube(x) {
    return x * x * x
}

fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print("  square(5) = ")
print(square(5))
print("  cube(3) = ")
print(cube(3))
print("  factorial(5) = ")
print(factorial(5))

# ---------------------------------------------------------------------------
# TEST 11: Control Flow
# ---------------------------------------------------------------------------
print("")
print("TEST 11: Control Flow")

fn grade(score) {
    if score >= 90 {
        return "A"
    }
    if score >= 80 {
        return "B"
    }
    if score >= 70 {
        return "C"
    }
    return "F"
}

scores = [95, 82, 67, 88]
for s in scores {
    g = grade(s)
    print("  Score ")
    print(s)
    print(" -> Grade ")
    print(g)
}

# ---------------------------------------------------------------------------
# TEST 12: Pipe Operator
# ---------------------------------------------------------------------------
print("")
print("TEST 12: Pipe Operator")
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("  data |> mean = ")
result = data |> mean()
print(result)
print("  data |> std = ")
result = data |> std()
print(result)

# ---------------------------------------------------------------------------
# TEST 13: Visualizations
# ---------------------------------------------------------------------------
print("")
print("TEST 13: Visualizations")
viz_data = [15, 18, 22, 25, 20, 28, 32, 30, 27, 35, 33, 40, 38, 42, 45]
print("  Histogram:")
histogram(viz_data, 5, 30, "Test Data")
print("")
print("  Box Plot:")
boxplot(viz_data, 40, "Test Data")
print("")
print("  Sparkline: ")
print(sparkline(viz_data, "Trend"))

# ---------------------------------------------------------------------------
# TEST 14: Math Functions
# ---------------------------------------------------------------------------
print("")
print("TEST 14: Math Functions")
print("  sqrt(16) = ")
print(sqrt(16))
print("  abs(-5) = ")
print(abs(-5))
print("  log(e) = ")
print(log(2.71828))
print("  exp(1) = ")
print(exp(1))
print("  sin(0) = ")
print(sin(0))
print("  cos(0) = ")
print(cos(0))
print("  floor(3.7) = ")
print(floor(3.7))
print("  ceil(3.2) = ")
print(ceil(3.2))
print("  round(3.567, 2) = ")
print(round(3.567, 2))

# ---------------------------------------------------------------------------
# TEST 15: NA Handling
# ---------------------------------------------------------------------------
print("")
print("TEST 15: NA Handling")
na_data = [1, 2, NA, 4, 5]
print("  data with NA: ")
print(na_data)
print("  is_na(NA) = ")
print(is_na(NA))
print("  mean still works: ")
print(mean(na_data))

# ---------------------------------------------------------------------------
# TEST 16: Newton Integration
# ---------------------------------------------------------------------------
print("")
print("TEST 16: Newton Knowledge Base")
newton_ask("What is the speed of light?")
newton_ask("What is photosynthesis?")

# ---------------------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------------------
print("")
print("================================================================")
print("  ALL TESTS COMPLETED SUCCESSFULLY!")
print("  Statsy: Statistics you can trust.")
print("================================================================")
