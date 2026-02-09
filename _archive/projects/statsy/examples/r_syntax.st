# R-like Syntax Tests for Statsy
# Demonstrating variadic arguments like R

# ═══════════════════════════════════════════════════════════════
# Test 1: Variadic mean - like R's mean(c(1,2,3)) but simpler
# ═══════════════════════════════════════════════════════════════
print("Test 1: Variadic mean")
print("mean(100, 1000, 200) =", mean(100, 1000, 200))
print("Expected: 433.333...")

print("")

# ═══════════════════════════════════════════════════════════════
# Test 2: Using c() to combine values (R-style)
# ═══════════════════════════════════════════════════════════════
print("Test 2: Vector with c()")
nums = c(100, 1000, 200)
print("nums =", nums)
print("mean(nums) =", mean(nums))

print("")

# ═══════════════════════════════════════════════════════════════
# Test 3: Other variadic functions
# ═══════════════════════════════════════════════════════════════
print("Test 3: Variadic other functions")
print("median(1, 5, 3, 7, 2) =", median(1, 5, 3, 7, 2))
print("sum(10, 20, 30) =", sum(10, 20, 30))
print("min(5, 2, 8, 1) =", min(5, 2, 8, 1))
print("max(5, 2, 8, 1) =", max(5, 2, 8, 1))
print("std(2, 4, 6, 8) =", std(2, 4, 6, 8))
print("var(2, 4, 6, 8) =", var(2, 4, 6, 8))

print("")

# ═══════════════════════════════════════════════════════════════
# Test 4: R-like I/O functions
# ═══════════════════════════════════════════════════════════════
print("Test 4: R-like I/O")
result = mean(100, 1000, 200)
cat("The mean is:", result)
print("paste result:", paste("Value =", result))
print("paste0 result:", paste0("x", 1, 2, 3))

print("")

# ═══════════════════════════════════════════════════════════════
# Test 5: sprintf for formatted output
# ═══════════════════════════════════════════════════════════════
print("Test 5: sprintf")
m = mean(1, 2, 3, 4, 5)
med = median(1, 2, 3, 4, 5)
print(sprintf("Mean = %.2f, Median = %.1f", m, med))

print("")

# ═══════════════════════════════════════════════════════════════
# Test 6: Mixed usage - variables and literals
# ═══════════════════════════════════════════════════════════════
print("Test 6: Mixed usage")
x = c(10, 20, 30)
y = c(40, 50)
print("mean of x and y combined:", mean(x, y))
print("mean with extra values:", mean(x, 100, 200))

print("")
print("═══════════════════════════════════════════════════════════════")
print("ALL R-LIKE SYNTAX TESTS COMPLETE!")
print("═══════════════════════════════════════════════════════════════")
