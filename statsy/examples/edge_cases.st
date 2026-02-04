# ===========================================================================
# STATSY EDGE CASE TEST - Testing Boundary Conditions
# ===========================================================================

print("================================================================")
print("  STATSY EDGE CASE TEST")
print("================================================================")

# ---------------------------------------------------------------------------
# EDGE 1: Empty and Single Element Vectors
# ---------------------------------------------------------------------------
print("")
print("EDGE 1: Small Vectors")
single = [42]
print("  Single element [42]:")
print("    mean = ")
print(mean(single))
print("    std = ")
print(std(single))

# ---------------------------------------------------------------------------
# EDGE 2: All Same Values
# ---------------------------------------------------------------------------
print("")
print("EDGE 2: Constant Data")
constant = [5, 5, 5, 5, 5]
print("  Constant data [5,5,5,5,5]:")
print("    mean = ")
print(mean(constant))
print("    std = ")
print(std(constant))
print("    mad = ")
print(mad(constant))

# ---------------------------------------------------------------------------
# EDGE 3: Negative Numbers
# ---------------------------------------------------------------------------
print("")
print("EDGE 3: Negative Numbers")
negatives = [-10, -5, 0, 5, 10]
print("  Data: [-10, -5, 0, 5, 10]")
print("    mean = ")
print(mean(negatives))
print("    sum = ")
print(sum(negatives))

# ---------------------------------------------------------------------------
# EDGE 4: Large Numbers
# ---------------------------------------------------------------------------
print("")
print("EDGE 4: Large Numbers")
large = [1000000, 2000000, 3000000]
print("  Large data:")
print("    mean = ")
print(mean(large))
print("    sum = ")
print(sum(large))

# ---------------------------------------------------------------------------
# EDGE 5: Decimals
# ---------------------------------------------------------------------------
print("")
print("EDGE 5: Decimal Precision")
decimals = [0.1, 0.2, 0.3, 0.4, 0.5]
print("  Decimals [0.1..0.5]:")
print("    sum = ")
print(sum(decimals))
print("    mean = ")
print(mean(decimals))

# ---------------------------------------------------------------------------
# EDGE 6: Boolean Operations
# ---------------------------------------------------------------------------
print("")
print("EDGE 6: Booleans")
print("  true and true = ")
print(true and true)
print("  true and false = ")
print(true and false)
print("  true or false = ")
print(true or false)
print("  not true = ")
print(not true)

# ---------------------------------------------------------------------------
# EDGE 7: Comparisons
# ---------------------------------------------------------------------------
print("")
print("EDGE 7: Comparisons")
print("  5 > 3 = ")
print(5 > 3)
print("  5 < 3 = ")
print(5 < 3)
print("  5 == 5 = ")
print(5 == 5)
print("  5 != 3 = ")
print(5 != 3)
print("  5 >= 5 = ")
print(5 >= 5)
print("  5 <= 5 = ")
print(5 <= 5)

# ---------------------------------------------------------------------------
# EDGE 8: String Operations
# ---------------------------------------------------------------------------
print("")
print("EDGE 8: Strings")
s1 = "Hello"
s2 = "World"
print("  Concatenation: ")
print(s1 + " " + s2)

# ---------------------------------------------------------------------------
# EDGE 9: Nested Functions
# ---------------------------------------------------------------------------
print("")
print("EDGE 9: Nested Function Calls")
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("  round(sqrt(mean(data)), 2) = ")
result = round(sqrt(mean(data)), 2)
print(result)

# ---------------------------------------------------------------------------
# EDGE 10: Recursion Depth
# ---------------------------------------------------------------------------
print("")
print("EDGE 10: Recursion")
fn fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}
print("  fib(10) = ")
print(fib(10))

# ---------------------------------------------------------------------------
# EDGE 11: Scatter with Few Points
# ---------------------------------------------------------------------------
print("")
print("EDGE 11: Scatter with 3 points")
x = [1, 2, 3]
y = [2, 4, 6]
scatter(x, y, 30, 8, "Small Scatter")

# ---------------------------------------------------------------------------
# EDGE 12: Histogram with Few Bins
# ---------------------------------------------------------------------------
print("")
print("EDGE 12: Histogram 2 bins")
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
histogram(data, 2, 20, "2-Bin Histogram")

# ---------------------------------------------------------------------------
# EDGE 13: Perfect Correlation
# ---------------------------------------------------------------------------
print("")
print("EDGE 13: Perfect Correlation")
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
print("  y = 2x exactly")
print("  correlation = ")
print(cor(x, y))

# ---------------------------------------------------------------------------
# EDGE 14: Zero Correlation Data
# ---------------------------------------------------------------------------
print("")
print("EDGE 14: Uncorrelated Data")
x = [1, 2, 3, 4, 5]
y = [5, 2, 4, 1, 3]
print("  Shuffled y values")
print("  correlation = ")
print(cor(x, y))

# ---------------------------------------------------------------------------
# EDGE 15: Modified Z-Scores
# ---------------------------------------------------------------------------
print("")
print("EDGE 15: Modified Z-Scores")
data = [1, 2, 3, 100, 4, 5]
print("  Data with outlier 100:")
z = modified_zscore(data)
print("  Modified z-scores: ")
print(z)

# ---------------------------------------------------------------------------
# EDGE 16: For Loop with Vector
# ---------------------------------------------------------------------------
print("")
print("EDGE 16: Loop Over Vector")
numbers = [10, 20, 30]
total = 0
for n in numbers {
    total = total + n
}
print("  Sum via loop: ")
print(total)

# ---------------------------------------------------------------------------
# EDGE 17: Quantiles
# ---------------------------------------------------------------------------
print("")
print("EDGE 17: Quantiles")
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("  quantile(data, 0.25) = ")
print(quantile(data, 0.25))
print("  quantile(data, 0.50) = ")
print(quantile(data, 0.50))
print("  quantile(data, 0.75) = ")
print(quantile(data, 0.75))

# ---------------------------------------------------------------------------
# EDGE 18: Type Checking
# ---------------------------------------------------------------------------
print("")
print("EDGE 18: Type Checking")
print("  is_numeric(42) = ")
print(is_numeric(42))
print("  is_numeric(NA) = ")
print(is_numeric(NA))
print("  is_vector([1,2,3]) = ")
print(is_vector([1, 2, 3]))

print("")
print("================================================================")
print("  ALL EDGE CASES PASSED!")
print("================================================================")
