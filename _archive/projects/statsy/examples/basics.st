# Statsy Example: Basic Statistics
# Run with: python statsy/statsy.py statsy/examples/basics.st

# Vector creation
data = [23, 45, 67, 89, 12, 34, 56, 78, 90, 11]

# Descriptive statistics
print("=== Basic Statistics ===")
print(mean(data))
print(median(data))
print(std(data))
print(var(data))

# Pipe operator - fluent style
print("")
print("=== Piped Operations ===")
result = data |> mean()
print(result)

# Using describe for full summary
print("")
print("=== Full Description ===")
describe(data)

# Robust statistics (outlier-resistant)
print("")
print("=== With Outlier ===")
data_outlier = [1, 2, 3, 4, 5, 100]
print("Regular mean:")
print(mean(data_outlier))
print("Robust mean (trimmed):")
print(robust_mean(data_outlier))
print("MAD (robust dispersion):")
print(mad(data_outlier))

# Vector operations
print("")
print("=== Vector Math ===")
x = [1, 2, 3, 4, 5]
y = [5, 4, 3, 2, 1]
print(x + y)
print(x * 2)
print(x ^ 2)

# Correlation
print("")
print("=== Correlation ===")
print(cor(x, y))

# Query Newton knowledge base
print("")
print("=== Newton Integration ===")
newton_ask("What is the central limit theorem?")
