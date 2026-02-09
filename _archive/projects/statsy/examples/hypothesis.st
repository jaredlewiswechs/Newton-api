# Statsy Example: Hypothesis Testing
# Run with: python statsy/statsy.py statsy/examples/hypothesis.st

print("═══════════════════════════════════════════════")
print("  HYPOTHESIS TESTING IN STATSY")
print("═══════════════════════════════════════════════")

# Two groups of data
group_a = [23.5, 25.1, 22.8, 24.3, 26.0, 23.9, 25.5, 24.1]
group_b = [28.2, 30.1, 27.5, 29.8, 31.2, 28.9, 30.5, 29.0]

print("")
print("Group A:")
describe(group_a)

print("")
print("Group B:")
describe(group_b)

# Two-sample t-test
print("")
print("=== Two-Sample T-Test ===")
result = t_test(group_a, group_b)
print(result)

# Correlation test
print("")
print("=== Correlation Test ===")
x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2.1, 4.0, 5.9, 8.1, 10.0, 11.9, 14.1, 16.0]
cor_result = cor_test(x, y)
print(cor_result)

print("")
print("Correlation coefficient:")
print(cor(x, y))

# Verify statistical claim with Newton
print("")
print("=== Verify Statistical Concept ===")
newton_ask("What is a p-value in statistics?")
