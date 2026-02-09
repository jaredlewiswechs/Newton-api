# Statsy Example: Functions and Control Flow
# Run with: python statsy/statsy.py statsy/examples/functions.st

print("===================================================")
print("  FUNCTIONS IN STATSY")
print("===================================================")

# Define a custom function
fn z_score(x, mu, sigma) {
    return (x - mu) / sigma
}

# Use it
data = [85, 90, 78, 92, 88, 76, 95, 89]
m = mean(data)
s = std(data)

print("")
print("Data mean:")
print(m)
print("Data std:")
print(s)

print("")
print("Z-scores:")
for val in data {
    z = z_score(val, m, s)
    print(z)
}

# Conditionals
print("")
print("=== Conditional Logic ===")
score = 85

if score >= 90 {
    print("Grade: A")
} else {
    if score >= 80 {
        print("Grade: B")
    } else {
        print("Grade: C or below")
    }
}

# Custom statistical function
fn coefficient_of_variation(x) {
    m = mean(x)
    s = std(x)
    return (s / m) * 100
}

print("")
print("=== Coefficient of Variation ===")
cv = coefficient_of_variation(data)
print(cv)

# Simulation
print("")
print("=== Monte Carlo: Mean of Random Samples ===")
sample_means = []
for i in seq(1, 5, 1) {
    sample = rnorm(100, 50, 10)
    sample_means = c(sample_means, mean(sample))
}
print("Sample means:")
print(sample_means)
print("Mean of means:")
print(mean(sample_means))
